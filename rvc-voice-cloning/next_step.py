#!/usr/bin/env python3
"""Tell a beginner the ONE next command to finish cloning their voice.

Run anytime:
  python next_step.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _lib import ROOT, find_rvc_weights, load_config, which


AUDIO_EXTS = {".wav", ".mp3", ".flac", ".m4a"}


def _count_raw(root: Path) -> int:
    raw = root / "data" / "raw"
    if not raw.is_dir():
        return 0
    return sum(1 for p in raw.rglob("*") if p.is_file() and p.suffix.lower() in AUDIO_EXTS)


def _has_segments(root: Path) -> bool:
    cfg = load_config(root)
    speaker = str(cfg.get("speaker_name") or "demo")
    meta = root / "data" / "segments" / speaker / "metadata.csv"
    return meta.is_file() and meta.stat().st_size > 20


def _library_ok() -> bool:
    try:
        import rvc  # noqa: F401

        return True
    except Exception:
        return False


def diagnose(root: Path) -> tuple[str, list[str]]:
    """Return (status_code, lines to print)."""
    lines: list[str] = []
    lines.append("════════════════════════════════════════")
    lines.append(" BEGINNER · NEXT STEP (clone YOUR voice)")
    lines.append("════════════════════════════════════════")
    lines.append("")

    # 1 ffmpeg
    if not which("ffmpeg"):
        lines += [
            "BLOCKED: FFmpeg missing",
            "",
            "NEXT (copy-paste):",
            "  brew install ffmpeg",
            "  ffmpeg -version",
            "",
            "Then run: python next_step.py",
        ]
        return "need_ffmpeg", lines

    # 2 venv hint
    if sys.prefix == getattr(sys, "base_prefix", sys.prefix):
        lines += [
            "TIP: activate the project venv first:",
            "  cd ~/DrIbrarAhmedAI/rvc-voice-cloning",
            "  source .venv/bin/activate",
            "",
        ]

    # 3 RVC library
    if not _library_ok():
        lines += [
            "BLOCKED: official RVC library not installed",
            "",
            "NEXT (copy-paste):",
            "  bash setup_rvc.sh",
            "  python configure_rvc.py --prefer-library",
            "  python next_step.py",
            "",
            "Guide: docs/RVC_SETUP.md",
        ]
        return "need_setup", lines

    # 4 configure convert command
    cfg = load_config(root)
    if not str(cfg.get("rvc_convert_command") or "").strip():
        lines += [
            "BLOCKED: companion not wired to RVC",
            "",
            "NEXT:",
            "  python configure_rvc.py --prefer-library",
            "  python configure_rvc.py --check",
            "  python next_step.py",
        ]
        return "need_configure", lines

    # 5 recordings
    n_raw = _count_raw(root)
    if n_raw < 1:
        lines += [
            "BLOCKED: no recordings in data/raw/",
            "",
            "NEED: 10+ minutes of YOUR clean speech (same mic, quiet room).",
            "A single 20-second take is not enough for a good clone.",
            "",
            "NEXT:",
            "  python open_recorder.py",
            "  # Record → Stop → Save WAV → put file in data/raw/",
            "  # Or use QuickTime Audio Recording → save into data/raw/",
            "  python play_clone.py --wav data/raw/YOUR_FILE.wav",
            "  python next_step.py",
        ]
        return "need_record", lines

    if n_raw < 3:
        lines.append(f"NOTE: only {n_raw} file(s) in data/raw/. Aim for many takes (10+ min total).")
        lines.append("")

    # 6 prepare
    if not _has_segments(root):
        lines += [
            "BLOCKED: dataset not prepared yet",
            "",
            "NEXT:",
            "  python prepare.py --input data/raw --speaker demo",
            "  python analyze.py",
            "  # KEEP clean clips · DROP noisy/reverb",
            "  python next_step.py",
        ]
        return "need_prepare", lines

    # 7 weights
    model_dir = root / str(cfg.get("rvc_model_dir") or "models/rvc")
    pth, index = find_rvc_weights(model_dir)
    if not pth:
        webui = Path(str(cfg.get("rvc_webui_root") or "")).expanduser()
        if not webui.is_dir():
            parent = root.parent
            guess = parent / "Retrieval-based-Voice-Conversion-WebUI"
            home_guess = Path.home() / "DrIbrarAhmedAI" / "Retrieval-based-Voice-Conversion-WebUI"
            if guess.is_dir():
                webui = guess
            elif home_guess.is_dir():
                webui = home_guess
            else:
                webui = home_guess
        lines += [
            "BLOCKED: no trained voice yet (models/rvc/*.pth missing)",
            "",
            "This is the step most beginners skip. Do it fully:",
            "",
            "NEXT:",
            f"  cd {webui}",
            "  python infer-web.py",
            "  # Browser → http://localhost:7865 → Train tab",
            "",
            "Exact fields + click order:",
            "  open docs/TRAIN_WEBUI.md",
            "  # or: python train_prep.py",
            "",
            "After train, copy weights:",
            f"  cp {webui}/assets/weights/myvoice.pth  {root}/models/rvc/speaker.pth",
            f"  cp {webui}/logs/myvoice/*.index       {root}/models/rvc/",
            "",
            "Then regenerate with YOUR weights (required):",
            f"  cd {root}",
            "  python configure_rvc.py --check",
            "  python infer.py --text-file scripts/clone_prove.txt --out output/clone_prove.wav",
            "  python next_step.py",
        ]
        return "need_train", lines

    # 8 success path — generate + play (fresh file with viewer weights)
    prove = root / "output" / "clone_prove.wav"
    prove_meta = root / "output" / "clone_prove.json"
    if not prove.is_file():
        lines += [
            "READY: weights found → " + pth.name + (f" + {index.name}" if index else ""),
            "",
            "NEXT (regenerate clone with YOUR weights — required):",
            "  python infer.py --text-file scripts/clone_prove.txt --out output/clone_prove.wav",
            "  python play_clone.py --wav output/clone_prove.wav",
            "",
            "Do not reuse an old demo WAV from before training.",
        ]
        return "need_infer", lines

    # Prove must be newer than weights (blocks stale TTS / demo WAV)
    try:
        if prove.stat().st_mtime + 1 < pth.stat().st_mtime:
            lines += [
                "BLOCKED: output/clone_prove.wav is OLDER than your .pth",
                f"  weights: {pth.name}",
                "",
                "NEXT (fresh infer with YOUR weights — required):",
                "  python infer.py --text-file scripts/clone_prove.txt --out output/clone_prove.wav",
                "  python play_clone.py --wav output/clone_prove.wav",
            ]
            return "need_infer", lines
    except OSError:
        pass

    # Prefer sidecar mode=+rvc when present
    if prove_meta.is_file():
        try:
            import json

            meta = json.loads(prove_meta.read_text(encoding="utf-8"))
            mode = str(meta.get("mode") or "")
            if "+rvc" not in mode:
                lines += [
                    "BLOCKED: output/clone_prove.wav is not an RVC convert",
                    f"  mode={mode or 'unknown'} (need *+rvc)",
                    "",
                    "NEXT:",
                    "  python infer.py --text-file scripts/clone_prove.txt --out output/clone_prove.wav",
                    "  # do not pass --baseline-only for a real clone",
                ]
                return "need_infer", lines
        except Exception:
            pass

    lines += [
        "READY: weights found → " + pth.name + (f" + {index.name}" if index else ""),
        "READY: output/clone_prove.wav is fresh + RVC",
        "",
        "NEXT (hear YOUR clone):",
        "  python play_clone.py --wav output/clone_prove.wav",
        "",
        "Regenerate anytime:",
        "  python infer.py --text-file scripts/clone_prove.txt --out output/clone_prove.wav",
        "",
        "Or full demo:",
        "  python demo_complete.py",
        "",
        "Stuck later? docs/TROUBLESHOOT.md",
        "Done? Comment FREECLONE on the video.",
    ]
    return "ready", lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    code, lines = diagnose(args.root)
    print("\n".join(lines))
    return 0 if code == "ready" else 1


if __name__ == "__main__":
    sys.exit(main())
