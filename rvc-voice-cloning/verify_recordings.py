#!/usr/bin/env python3
"""Verify raw recordings have enough speech before prepare/train."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _lib import ROOT, load_config, which
from audio_qc import CLIP_HARD, duration_and_clip, list_audio_files


def verify(root: Path, input_dir: Path, min_minutes: float) -> int:
    if not input_dir.is_absolute():
        input_dir = root / input_dir

    ffmpeg = which("ffmpeg")
    files = list_audio_files(input_dir)
    if not files:
        print("Files: 0")
        print("Total audio: 0.0 minutes")
        print("Clipped files: 0")
        print("STATUS: NO RECORDINGS")
        print(
            f"Put WAV files in {input_dir} "
            "(browser Save WAV → ~/Downloads → move here)."
        )
        return 1

    total = 0.0
    clipped_files = 0
    for path in files:
        try:
            dur, ratio = duration_and_clip(path, ffmpeg)
        except Exception as exc:  # noqa: BLE001 - beginner-facing path
            print(f"  {path.name}: ERROR ({exc})")
            return 1
        total += dur
        flag = ""
        if ratio >= CLIP_HARD:
            clipped_files += 1
            flag = "  CLIPPED"
        print(f"  {path.name}: {dur / 60:.2f} min{flag}")

    print("")
    print(f"Files: {len(files)}")
    print(f"Total audio: {total / 60:.1f} minutes")
    print(f"Clipped files: {clipped_files}")

    if total >= min_minutes * 60 and clipped_files > 0:
        print("STATUS: RECORDING NEEDS CLEANER TAKES")
        return 1
    if total >= min_minutes * 60 and clipped_files == 0:
        print("STATUS: RECORDING READY")
        return 0
    print("STATUS: NEED MORE SPEECH")
    print(f"Record until you have ≥ {min_minutes:.0f} minutes total.")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--min-minutes", type=float, default=None)
    args = parser.parse_args()
    cfg = load_config(args.root)
    min_minutes = (
        args.min_minutes
        if args.min_minutes is not None
        else float(cfg.get("min_dataset_minutes") or 10.0)
    )
    input_dir = args.input or (args.root / "data" / "raw")
    return verify(args.root, input_dir, min_minutes)


if __name__ == "__main__":
    sys.exit(main())
