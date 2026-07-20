#!/usr/bin/env python3
"""Record helper - remind viewers how to capture own-voice WAVs into data/raw."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from _lib import ROOT


GUIDE = """
# How to record YOUR voice (complete demo)

## Option A - browser recorder (easiest)
  python open_recorder.py
  → Record → Stop → Save WAV
  → Move the downloaded .wav into data/raw/

## Option B - any app (Voice Memos / Audacity)
  Export WAV/MP3 into:  data/raw/
  Examples:
     data/raw/take_01.wav
     data/raw/my_voice_01.wav

## Tips
  Quiet room. Same mic for all clips. Speak naturally.
  Aim for 10+ minutes total (many short takes is fine).

## Next
  python record_voice.py --check
  python prepare.py --input data/raw --speaker myvoice
  python analyze.py
  python train_prep.py
  # train in RVC/WebUI → models/rvc/speaker.pth + .index
  python infer.py --text-file scripts/sample_line.txt
  python play_clone.py --wav output/narration.wav

OWN VOICE ONLY. Set consent.yaml attested: true after you confirm.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true", help="List files in data/raw")
    args = parser.parse_args()
    raw = args.root / "data" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    print(GUIDE.strip())
    print("")
    files = sorted(
        p for p in raw.iterdir() if p.is_file() and p.suffix.lower() in {".wav", ".mp3", ".flac", ".m4a"}
    )
    if args.check or files:
        print(f"data/raw → {len(files)} audio file(s)")
        for p in files[:12]:
            print(f"  {p.name}")
        if not files:
            print("  (empty - drop your recordings here)")
    else:
        print("data/raw is ready. Drop your voice recordings here, then --check.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
