#!/usr/bin/env python3
"""Open the browser voice recorder (Save WAV → move file into data/raw/)."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

from _lib import ROOT


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    html = args.root / "recorder.html"
    if not html.is_file():
        raise SystemExit(f"Missing {html}")
    uri = html.resolve().as_uri()
    print("OPEN VOICE RECORDER")
    print(f"  {html}")
    print("")
    print("1. Click Record — allow microphone")
    print("2. Speak naturally (quiet room, same mic)")
    print("3. Stop → click Save WAV")
    print("4. Browser saves to ~/Downloads/ (not into the repo)")
    print("5. Move the file into data/raw/:")
    print("     mkdir -p data/raw")
    print("     mv ~/Downloads/my_voice_*.wav data/raw/")
    print("6. python verify_recordings.py --input data/raw --min-minutes 10")
    print("7. python prepare.py --input data/raw --speaker myvoice")
    print("")
    opened = webbrowser.open(uri)
    if not opened:
        # macOS fallback
        open_bin = shutil.which("open")
        if open_bin:
            subprocess.run([open_bin, str(html)], check=False)
        else:
            print(f"Open manually: {uri}")
            return 1
    print("Recorder opened in your browser.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
