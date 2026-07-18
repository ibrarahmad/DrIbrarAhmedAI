#!/usr/bin/env python3
"""Play a generated clone WAV (afplay / ffplay / aplay)."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from _lib import ROOT


def play(path: Path) -> int:
    if not path.is_file():
        print(f"MISSING: {path}")
        print("Generate first: python infer.py --text-file scripts/sample_line.txt")
        return 1
    print(f"PLAY CLONE → {path}")
    for player, args in (
        ("afplay", [str(path)]),
        ("ffplay", ["-nodisp", "-autoexit", str(path)]),
        ("aplay", [str(path)]),
    ):
        bin_path = shutil.which(player)
        if not bin_path:
            continue
        print(f"using {player}")
        return subprocess.call([bin_path, *args])
    print("No afplay/ffplay/aplay found — open the WAV manually:")
    print(f"  {path.resolve()}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--wav", type=Path, default=None)
    args = parser.parse_args()
    wav = args.wav or (args.root / "output" / "narration.wav")
    if not wav.is_absolute():
        wav = args.root / wav
    return play(wav)


if __name__ == "__main__":
    sys.exit(main())
