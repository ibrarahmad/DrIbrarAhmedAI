#!/usr/bin/env python3
"""
Complete educational demo using the official RVC library:
  https://github.com/RVC-Project/Retrieval-based-Voice-Conversion

Stages printed for the deck / viewers:
  1) check RVC library (pip / rvc CLI)
  2) configure companion
  3) record reminder (browser mic → data/raw/)
  4) prepare + train_prep
  5) Edge TTS → RVC convert (library API / CLI / WebUI)
  6) play clone

Usage:
  python demo_complete.py                 # full path (needs .pth for real clone)
  python demo_complete.py --baseline-only # Edge TTS only (no weights yet)
  python demo_complete.py --skip-record-check
"""
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

from _lib import ROOT, find_rvc_weights, load_config, read_text_file, which, write_json
from infer import infer
from play_clone import play
from prepare import prepare
from train_prep import train_prep


def _banner(title: str) -> None:
    print("")
    print("═" * 56)
    print(f" {title}")
    print("═" * 56)


def _rvc_library_ok() -> tuple[bool, str]:
    if importlib.util.find_spec("rvc") is not None:
        return True, "import rvc OK"
    if which("rvc"):
        return True, f"rvc CLI at {which('rvc')}"
    from _lib import setup_script_hint

    return False, f"MISSING - run: {setup_script_hint()}"


def _raw_wav_count(root: Path) -> int:
    raw = root / "data" / "raw"
    if not raw.is_dir():
        return 0
    n = 0
    for p in raw.iterdir():
        if p.suffix.lower() in {".wav", ".mp3", ".flac", ".m4a", ".ogg"}:
            n += 1
    return n


def run_demo(
    root: Path,
    *,
    baseline_only: bool = False,
    skip_record_check: bool = False,
    play_audio: bool = True,
) -> int:
    cfg = load_config(root)
    speaker = str(cfg.get("speaker_name") or "demo")
    model_dir = root / str(cfg.get("rvc_model_dir") or "models/rvc")

    _banner("COMPLETE DEMO · official RVC library")
    print("Upstream: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion")
    print(f"Companion: {root}")
    print("")

    # ── 1. library ──────────────────────────────────────────────
    _banner("1/6  RVC LIBRARY")
    ok, msg = _rvc_library_ok()
    print(f"[lib] {msg}")
    if not ok:
        from _lib import setup_script_hint

        print(f"HINT: {setup_script_hint()}")
        print(
            "      pip install "
            "git+https://github.com/RVC-Project/Retrieval-based-Voice-Conversion.git"
            "@7b284a634667c34103eaaeed972b48ccdb4b893e"
        )
        if not baseline_only:
            return 1

    # ── 2. configure ────────────────────────────────────────────
    _banner("2/6  CONFIGURE")
    cfg_check = subprocess.run(
        [sys.executable, str(root / "configure_rvc.py"), "--prefer-library", "--check"],
        cwd=str(root),
    )
    if cfg_check.returncode != 0 and not baseline_only:
        print("HINT: python configure_rvc.py --prefer-library")
        # continue - convert may still work via bridge after wiring

    # ── 3. record + PLAY the raw WAV ────────────────────────────
    _banner("3/6  RECORD YOUR VOICE · PLAY RAW WAV")
    n_raw = _raw_wav_count(root)
    print(f"[record] data/raw → {n_raw} audio file(s)")
    raw_dir = root / "data" / "raw"
    raw_wav = None
    if raw_dir.is_dir():
        for p in sorted(raw_dir.iterdir()):
            if p.suffix.lower() in {".wav", ".mp3", ".flac", ".m4a"}:
                raw_wav = p
                break
    if n_raw == 0 and not skip_record_check:
        print("HINT: python open_recorder.py  → Save WAV → move into data/raw/")
        print("      (re-run with --skip-record-check to continue without raw takes)")
        if not baseline_only:
            return 1
    elif n_raw == 0:
        print("[record] skipped check - using existing segments if any")
    if play_audio and raw_wav is not None:
        print(f"[play] RAW recording first → {raw_wav.relative_to(root)}")
        play(raw_wav)
    elif raw_wav is not None:
        print(f"[play] skipped - would play {raw_wav.relative_to(root)}")

    # ── 4. prepare + train reminder ─────────────────────────────
    _banner("4/6  PREPARE + TRAIN")
    if n_raw > 0:
        prepare(root, root / "data" / "raw", speaker)
    else:
        print("[prepare] no new raw files - keeping existing segments")
    train_prep(root)
    pth, index = find_rvc_weights(model_dir)
    print(f"[weights] {pth.name if pth else 'MISSING'}  index={index.name if index else 'none'}")
    if pth is None and not baseline_only:
        print("HINT: train in WebUI, copy speaker.pth (+ .index) → models/rvc/")
        print("      Or re-run: python demo_complete.py --baseline-only")
        return 1

    # ── 5. infer DIFFERENT text (prove clone) ───────────────────
    _banner("5/6  INFER · NEW SCRIPT (not training lines)")
    convert = str(cfg.get("rvc_convert_command") or "").strip()
    if not convert and not baseline_only:
        print("[config] wiring rvc_infer_bridge via configure_rvc.py …")
        subprocess.run(
            [sys.executable, str(root / "configure_rvc.py"), "--prefer-library"],
            cwd=str(root),
            check=False,
        )
    # Prefer prove script so the clone speaks words it was not just “shown”
    prove = root / "scripts" / "clone_prove.txt"
    text_file = prove if prove.is_file() else root / "scripts" / "sample_line.txt"
    out_wav = root / "output" / "clone_prove.wav"
    text = read_text_file(text_file)
    print(f"[text] {text_file.relative_to(root)}")
    print(f"[text] {text[:120]}{'…' if len(text) > 120 else ''}")
    result = infer(root, text, out_wav, baseline_only=baseline_only)
    print(f"[mode] {result['mode']}")

    # ── 6. play CLONE on that new text ──────────────────────────
    _banner("6/6  PLAY CLONE · DIFFERENT TEXT")
    if play_audio and out_wav.is_file():
        print(f"[play] CLONE → {out_wav.relative_to(root)}")
        play(out_wav)
    else:
        print(f"[play] file ready: {out_wav}")

    payload = {
        "demo": "complete",
        "upstream": "https://github.com/RVC-Project/Retrieval-based-Voice-Conversion",
        "mode": result["mode"],
        "weights": pth.name if pth else None,
        "index": index.name if index else None,
        "raw_played": str(raw_wav.relative_to(root)) if raw_wav else None,
        "prove_text": str(text_file.relative_to(root)),
        "out": result["out"],
        "library": msg,
    }
    write_json(root / "output" / "demo_complete.json", payload)
    print("")
    print("COMPLETE DEMO READY · heard raw WAV · heard clone on new text")
    print("wrote output/demo_complete.json")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--baseline-only", action="store_true")
    parser.add_argument("--skip-record-check", action="store_true")
    parser.add_argument("--no-play", action="store_true")
    args = parser.parse_args()
    return run_demo(
        args.root,
        baseline_only=args.baseline_only,
        skip_record_check=args.skip_record_check,
        play_audio=not args.no_play,
    )


if __name__ == "__main__":
    raise SystemExit(main())
