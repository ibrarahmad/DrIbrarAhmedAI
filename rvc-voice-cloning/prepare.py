#!/usr/bin/env python3
"""Prepare own-voice recordings: raw → clean stubs → segments metadata."""
from __future__ import annotations

import argparse
import csv
import shutil
import sys
from pathlib import Path

from _lib import ROOT, load_config, which


AUDIO_EXTS = {".wav", ".mp3", ".flac", ".m4a"}


def prepare(root: Path, input_dir: Path, speaker: str) -> Path:
    cfg = load_config(root)
    sample_rate = int(cfg.get("sample_rate") or 40000)
    raw_files = sorted(
        p for p in input_dir.rglob("*") if p.suffix.lower() in AUDIO_EXTS and p.is_file()
    )
    clean_dir = root / "data" / "clean" / speaker
    seg_dir = root / "data" / "segments" / speaker
    clean_dir.mkdir(parents=True, exist_ok=True)
    seg_dir.mkdir(parents=True, exist_ok=True)

    ffmpeg = which("ffmpeg")
    rows: list[dict[str, str]] = []

    if not raw_files:
        # Educational stub so the pipeline is inspectable without recordings.
        meta = seg_dir / "metadata.csv"
        if not meta.is_file():
            demo = ROOT / "data" / "segments" / "demo" / "metadata.csv"
            if demo.is_file():
                shutil.copy(demo, meta)
                print(f"no raw audio -  copied demo metadata → {meta.relative_to(root)}")
            else:
                raise SystemExit(f"No audio in {input_dir} and no demo metadata.")
        return meta

    for i, src in enumerate(raw_files, start=1):
        dest = clean_dir / f"{speaker}_{i:03d}.wav"
        if ffmpeg:
            import subprocess

            subprocess.run(
                [
                    ffmpeg,
                    "-y",
                    "-i",
                    str(src),
                    "-ac",
                    "1",
                    "-ar",
                    str(sample_rate),
                    str(dest),
                ],
                check=True,
                capture_output=True,
            )
        else:
            shutil.copy(src, dest)
        seg_name = f"seg_{i:03d}.wav"
        seg_path = seg_dir / seg_name
        shutil.copy(dest, seg_path)
        rows.append(
            {
                "path": seg_name,
                "duration_sec": "4.0",
                "rms_dbfs": "-18.0",
                "label": "clean",
            }
        )
        print(f"prepared {src.name} → {seg_path.relative_to(root)}")

    meta_path = seg_dir / "metadata.csv"
    with meta_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["path", "duration_sec", "rms_dbfs", "label"]
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {meta_path.relative_to(root)} ({len(rows)} clips)")
    return meta_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--input", type=Path, default=None, help="Raw recordings dir")
    parser.add_argument("--speaker", type=str, default=None)
    args = parser.parse_args()
    cfg = load_config(args.root)
    speaker = args.speaker or cfg.get("speaker_name") or "demo"
    input_dir = args.input or (args.root / "data" / "raw")
    meta = prepare(args.root, input_dir, speaker)
    print(f"READY · metadata={meta.relative_to(args.root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
