#!/usr/bin/env python3
"""Play a WAV/MP3 with afplay / ffplay / aplay."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from _lib import ROOT


def play(path: Path, *, label: str | None = None) -> int:
    if not path.is_file():
        print(f"MISSING: {path}")
        print("Generate first: python infer.py --text-file scripts/sample_line.txt")
        return 1
    tag = label or ("PLAY RAW" if "data/raw" in path.as_posix() else "PLAY AUDIO")
    print(f"{tag} → {path}")
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
    print("No afplay/ffplay/aplay found - open the file manually:")
    print(f"  {path.resolve()}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--wav", type=Path, default=None)
    parser.add_argument("--label", type=str, default=None)
    parser.add_argument(
        "--seconds",
        type=float,
        default=None,
        help="macOS afplay only: stop after N seconds (smoke tests)",
    )
    args = parser.parse_args()
    wav = args.wav or (args.root / "output" / "narration.wav")
    if not wav.is_absolute():
        wav = args.root / wav
    if args.seconds is not None and shutil.which("afplay"):
        if not wav.is_file():
            print(f"MISSING: {wav}")
            return 1
        tag = args.label or "PLAY AUDIO"
        print(f"{tag} → {wav} ({args.seconds}s)")
        print("using afplay")
        return subprocess.call(["afplay", "-t", str(args.seconds), str(wav)])
    return play(wav, label=args.label)


if __name__ == "__main__":
    sys.exit(main())
