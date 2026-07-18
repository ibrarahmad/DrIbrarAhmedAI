#!/usr/bin/env python3
"""Loudness-normalize WAV (+ optional MP3) for YouTube."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from _lib import ROOT, load_config, which


def export_audio(root: Path, in_wav: Path, out_dir: Path, basename: str) -> tuple[Path, Path | None]:
    cfg = load_config(root)
    ffmpeg = which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg required - brew install ffmpeg")
    if not in_wav.is_file():
        raise SystemExit(f"Missing input: {in_wav}")

    out_dir.mkdir(parents=True, exist_ok=True)
    lufs = float(cfg.get("export_integrated_lufs") or -16)
    tp = float(cfg.get("export_true_peak_db_tp") or -1.5)
    bitrate = int(cfg.get("export_mp3_bitrate_k") or 192)

    out_wav = out_dir / f"{basename}.wav"
    out_mp3 = out_dir / f"{basename}.mp3"
    filt = f"loudnorm=I={lufs}:TP={tp}:LRA=11"
    # ffmpeg cannot loudnorm in-place; write temp then replace
    tmp_wav = out_dir / f".{basename}.loudnorm.tmp.wav"
    subprocess.run(
        [ffmpeg, "-y", "-i", str(in_wav), "-af", filt, str(tmp_wav)],
        check=True,
        capture_output=True,
    )
    tmp_wav.replace(out_wav)
    print(f"wrote {out_wav.relative_to(root)}")
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(out_wav),
            "-codec:a",
            "libmp3lame",
            "-b:a",
            f"{bitrate}k",
            str(out_mp3),
        ],
        check=True,
        capture_output=True,
    )
    print(f"wrote {out_mp3.relative_to(root)}")
    print(f"EXPORT CHECK: PASS  loudnorm I={lufs} TP={tp}")
    return out_wav, out_mp3


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--in-wav", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--basename", type=str, default="narration")
    args = parser.parse_args()
    in_wav = args.in_wav or (args.root / "output" / "narration.wav")
    if not in_wav.is_absolute():
        in_wav = args.root / in_wav
    out_dir = args.out_dir or (args.root / "output")
    if not out_dir.is_absolute():
        out_dir = args.root / out_dir
    export_audio(args.root, in_wav, out_dir, args.basename)
    return 0


if __name__ == "__main__":
    sys.exit(main())
