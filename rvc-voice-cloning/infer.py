#!/usr/bin/env python3
"""Text → base WAV (Edge TTS, or macOS say fallback) → optional RVC convert."""
from __future__ import annotations

import argparse
import asyncio
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from _lib import (
    ROOT,
    find_rvc_weights,
    load_config,
    read_text_file,
    which,
)
from rvc_core import run_rvc, retrieval_knobs


def _ffmpeg_to_wav(src: Path, dest: Path, sample_rate: int = 40000) -> None:
    ffmpeg = which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg required to write WAV. brew install ffmpeg")
    subprocess.run(
        [ffmpeg, "-y", "-i", str(src), "-ac", "1", "-ar", str(sample_rate), str(dest)],
        check=True,
        capture_output=True,
    )


def _say_to_wav(text: str, dest: Path, sample_rate: int = 40000) -> None:
    """Offline Mac TTS so infer still works without Edge network."""
    say = which("say")
    if not say:
        raise SystemExit(
            "Edge TTS failed and macOS 'say' is missing. "
            "Fix network for edge-tts, or install ffmpeg + use a Mac."
        )
    aiff = dest.with_suffix(".aiff")
    subprocess.run([say, "-o", str(aiff), text], check=True, capture_output=True)
    _ffmpeg_to_wav(aiff, dest, sample_rate=sample_rate)
    aiff.unlink(missing_ok=True)
    print("[tts] backend=say (offline macOS)")


async def _edge_tts_to_wav(text: str, voice: str, rate: str, pitch: str, dest: Path) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch)
    tmp_mp3 = dest.with_suffix(".mp3")
    await communicate.save(str(tmp_mp3))
    _ffmpeg_to_wav(tmp_mp3, dest, sample_rate=40000)
    tmp_mp3.unlink(missing_ok=True)
    print("[tts] backend=edge-tts")


def text_to_wav(text: str, dest: Path, cfg: dict) -> str:
    """Return backend name used."""
    try:
        import edge_tts  # noqa: F401
    except ImportError:
        _say_to_wav(text, dest)
        return "say"

    try:
        asyncio.run(
            _edge_tts_to_wav(
                text,
                str(cfg.get("edge_tts_voice") or "en-US-GuyNeural"),
                str(cfg.get("edge_tts_rate") or "-5%"),
                str(cfg.get("edge_tts_pitch") or "+0Hz"),
                dest,
            )
        )
        return "edge-tts"
    except Exception as exc:
        print(f"[tts] edge-tts failed ({exc.__class__.__name__}); trying macOS say")
        _say_to_wav(text, dest)
        return "say"


def infer(
    root: Path,
    text: str,
    out_wav: Path,
    *,
    baseline_only: bool = False,
    preset: str | None = None,
) -> dict:
    cfg = load_config(root)
    knobs = retrieval_knobs(cfg, preset)
    model_dir = root / str(cfg.get("rvc_model_dir") or "models/rvc")
    pth, index = find_rvc_weights(model_dir)
    convert_cmd = (cfg.get("rvc_convert_command") or "").strip()

    out_wav.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="rvc_infer_") as tmp:
        base = Path(tmp) / "base.wav"
        print(f"[tts] chars={len(text)}")
        backend = text_to_wav(text, base, cfg)

        use_rvc = not baseline_only and pth is not None
        if use_rvc:
            print(f"[rvc] model={pth.name} index={index.name if index else 'none'}")
            print(
                f"[rvc] preset={knobs['preset']} index_rate={knobs.get('index_rate')} "
                f"protect={knobs.get('protect')} f0method={knobs.get('f0method')}"
            )
            if convert_cmd:
                run_rvc(convert_cmd, base, out_wav, model_dir)
            else:
                from rvc_infer_bridge import convert as rvc_convert

                rvc_convert(base, out_wav, model_dir)
            mode = f"{backend}+rvc"
        else:
            shutil.copy(base, out_wav)
            mode = f"{backend}_only"
            if baseline_only:
                print("[rvc] skipped - baseline-only")
            elif pth is None:
                print("[rvc] skipped - no *.pth in models/rvc/")
                print("[rvc] train in WebUI, copy speaker.pth here, then re-run infer")

    print(f"[out] {out_wav.relative_to(root)}  mode={mode}")
    return {
        "out": str(out_wav.relative_to(root)),
        "mode": mode,
        "preset": knobs["preset"],
        "has_weights": pth is not None,
        "has_index": index is not None,
        "tts_backend": backend,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--text", type=str, default=None)
    parser.add_argument("--text-file", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--baseline-only", action="store_true")
    parser.add_argument("--preset", type=str, default=None)
    args = parser.parse_args()

    if args.text_file:
        text = read_text_file(
            args.root / args.text_file if not args.text_file.is_absolute() else args.text_file
        )
    elif args.text:
        text = args.text.strip()
    else:
        text = read_text_file(args.root / "scripts" / "sample_line.txt")

    out = args.out or (args.root / "output" / "narration.wav")
    if not out.is_absolute():
        out = args.root / out
    infer(args.root, text, out, baseline_only=args.baseline_only, preset=args.preset)
    return 0


if __name__ == "__main__":
    sys.exit(main())
