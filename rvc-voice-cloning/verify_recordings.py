#!/usr/bin/env python3
"""Verify raw recordings have enough clean speech before prepare/train."""
from __future__ import annotations

import argparse
import audioop
import struct
import subprocess
import sys
import wave
from pathlib import Path

from _lib import ROOT, load_config, which


AUDIO_EXTS = {".wav", ".mp3", ".flac", ".m4a"}


def _pcm_duration_and_clip(path: Path, ffmpeg: str | None) -> tuple[float, float]:
    """Return (duration_sec, clip_ratio). Prefer ffmpeg decode for non-WAV."""
    if path.suffix.lower() == ".wav":
        try:
            with wave.open(str(path), "rb") as wf:
                sr = wf.getframerate() or 1
                nch = wf.getnchannels()
                sw = wf.getsampwidth()
                nframes = wf.getnframes()
                raw = wf.readframes(nframes)
            dur = nframes / float(sr)
            if sw != 2:
                raw = audioop.lin2lin(raw, sw, 2)
            if nch > 1:
                raw = audioop.tomono(raw, 2, 0.5, 0.5)
            n = len(raw) // 2
            samples = struct.unpack("<" + "h" * n, raw) if n else ()
            clipped = sum(1 for s in samples if abs(s) >= 32000)
            return dur, (clipped / n if n else 0.0)
        except wave.Error:
            pass

    if not ffmpeg:
        # Last resort: file size guess is worse than failing clearly.
        raise SystemExit(f"Cannot decode {path.name}. Install ffmpeg.")

    # Duration via ffprobe-like ffmpeg
    probe = subprocess.run(
        [
            ffmpeg,
            "-i",
            str(path),
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    # ffmpeg prints Duration: HH:MM:SS.xx to stderr
    dur = 0.0
    for line in (probe.stderr or "").splitlines():
        if "Duration:" in line:
            part = line.split("Duration:")[1].split(",")[0].strip()
            hh, mm, ss = part.split(":")
            dur = int(hh) * 3600 + int(mm) * 60 + float(ss)
            break

    pcm = subprocess.run(
        [
            ffmpeg,
            "-v",
            "error",
            "-i",
            str(path),
            "-ac",
            "1",
            "-f",
            "s16le",
            "-acodec",
            "pcm_s16le",
            "pipe:1",
        ],
        check=True,
        capture_output=True,
    ).stdout
    n = len(pcm) // 2
    samples = struct.unpack("<" + "h" * n, pcm) if n else ()
    clipped = sum(1 for s in samples if abs(s) >= 32000)
    if dur <= 0 and n:
        # Assume 48k if duration parse failed (common device rate).
        dur = n / 48000.0
    return dur, (clipped / n if n else 0.0)


def verify(root: Path, input_dir: Path, min_minutes: float) -> int:
    ffmpeg = which("ffmpeg")
    files = sorted(
        p for p in input_dir.rglob("*") if p.is_file() and p.suffix.lower() in AUDIO_EXTS
    )
    if not files:
        print(f"Files: 0")
        print(f"Total speech: 0.0 minutes")
        print("Clipped files: 0")
        print("STATUS: NO RECORDINGS")
        print(f"Put WAV files in {input_dir} (browser Save WAV → Downloads → move here).")
        return 1

    total = 0.0
    clipped_files = 0
    for path in files:
        dur, clip_ratio = _pcm_duration_and_clip(path, ffmpeg)
        total += dur
        flag = ""
        if clip_ratio >= 0.01:
            clipped_files += 1
            flag = "  CLIPPED"
        print(f"  {path.name}: {dur/60:.2f} min{flag}")

    print("")
    print(f"Files: {len(files)}")
    print(f"Total speech: {total/60:.1f} minutes")
    print(f"Clipped files: {clipped_files}")
    ready = total >= min_minutes * 60 and clipped_files == 0
    if total >= min_minutes * 60 and clipped_files > 0:
        print("STATUS: RECORDING NEEDS CLEANER TAKES")
        return 1
    if ready:
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
