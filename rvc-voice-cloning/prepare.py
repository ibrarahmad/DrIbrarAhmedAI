#!/usr/bin/env python3
"""Prepare own-voice recordings: raw → mono 40 kHz → silence-split segments + metadata.

Only KEEP (clean) clips are written into data/segments/<speaker>/ for WebUI training.
Rejected clips go to data/segments/<speaker>/rejected/ with reasons in metadata.
"""
from __future__ import annotations

import argparse
import csv
import shutil
import sys
from pathlib import Path

from _lib import DEFAULT_SPEAKER, ROOT, load_config, which
from audio_qc import (
    clip_ratio,
    label_metrics,
    list_audio_files,
    load_mono_pcm16,
    rms_dbfs,
    split_on_silence,
    write_wav,
)


def _clear_dir_wavs(directory: Path) -> None:
    if not directory.is_dir():
        return
    for old in directory.glob("*.wav"):
        old.unlink()


def prepare(root: Path, input_dir: Path, speaker: str) -> Path:
    cfg = load_config(root)
    sample_rate = int(cfg.get("sample_rate") or 40000)
    min_clip = float(cfg.get("min_clip_length_sec") or 2.0)
    max_clip = float(cfg.get("max_clip_length_sec") or 12.0)

    raw_files = list_audio_files(input_dir)
    clean_dir = root / "data" / "clean" / speaker
    seg_dir = root / "data" / "segments" / speaker
    reject_dir = seg_dir / "rejected"
    clean_dir.mkdir(parents=True, exist_ok=True)
    seg_dir.mkdir(parents=True, exist_ok=True)
    reject_dir.mkdir(parents=True, exist_ok=True)

    # Honest rebuild each run (WebUI trains every WAV in the folder).
    _clear_dir_wavs(clean_dir)
    _clear_dir_wavs(seg_dir)
    _clear_dir_wavs(reject_dir)

    if not raw_files:
        raise SystemExit(
            f"No audio in {input_dir}.\n"
            "Record with: python open_recorder.py\n"
            "Then: mkdir -p data/raw && mv ~/Downloads/my_voice_*.wav data/raw/\n"
            "Check: python verify_recordings.py --input data/raw --min-minutes 10"
        )

    ffmpeg = which("ffmpeg")
    keep_rows: list[dict[str, str]] = []
    drop_rows: list[dict[str, str]] = []
    keep_i = 0
    drop_i = 0

    for src_i, src in enumerate(raw_files, start=1):
        try:
            pcm, sr = load_mono_pcm16(src, sample_rate, ffmpeg)
        except Exception as exc:  # noqa: BLE001 - beginner-facing path
            raise SystemExit(f"Failed to decode {src.name}: {exc}") from exc

        dest = clean_dir / f"{speaker}_{src_i:03d}.wav"
        write_wav(dest, pcm, sr)
        print(
            f"cleaned {src.name} → {dest.relative_to(root)} "
            f"({len(pcm) / 2 / sr:.1f}s · {rms_dbfs(pcm):.1f} dBFS)"
        )

        for clip in split_on_silence(
            pcm, sr, min_clip_sec=min_clip, max_clip_sec=max_clip
        ):
            dur = len(clip) / 2 / sr
            rms = rms_dbfs(clip)
            ratio = clip_ratio(clip)
            label = label_metrics(rms, ratio)
            row = {
                "duration_sec": f"{dur:.3f}",
                "rms_dbfs": f"{rms:.2f}",
                "clip_ratio": f"{ratio:.4f}",
                "label": label,
                "source": src.name,
            }
            if label == "clean":
                keep_i += 1
                name = f"seg_{keep_i:03d}.wav"
                write_wav(seg_dir / name, clip, sr)
                row["path"] = name
                keep_rows.append(row)
                print(
                    f"  KEEP  {name}  {dur:.2f}s  rms={rms:.1f}  "
                    f"clip={ratio:.3%}  ← {src.name}"
                )
            else:
                drop_i += 1
                name = f"drop_{drop_i:03d}.wav"
                write_wav(reject_dir / name, clip, sr)
                row["path"] = f"rejected/{name}"
                drop_rows.append(row)
                print(
                    f"  DROP  {name}  {dur:.2f}s  rms={rms:.1f}  "
                    f"clip={ratio:.3%}  → {label.upper()}"
                )

    meta_path = seg_dir / "metadata.csv"
    fieldnames = ["path", "duration_sec", "rms_dbfs", "clip_ratio", "label", "source"]
    with meta_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(keep_rows)
        writer.writerows(drop_rows)

    clean_sec = sum(float(r["duration_sec"]) for r in keep_rows)
    print(
        f"wrote {meta_path.relative_to(root)} "
        f"(KEEP={len(keep_rows)} · DROP={len(drop_rows)} · "
        f"{clean_sec / 60:.2f} clean minutes)"
    )
    if not keep_rows:
        raise SystemExit(
            "No clean segments produced. Re-record in a quieter room, "
            "then run prepare.py again."
        )
    return meta_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--input", type=Path, default=None, help="Raw recordings dir")
    parser.add_argument("--speaker", type=str, default=None)
    args = parser.parse_args()
    cfg = load_config(args.root)
    speaker = args.speaker or cfg.get("speaker_name") or DEFAULT_SPEAKER
    input_dir = args.input or (args.root / "data" / "raw")
    if not input_dir.is_absolute():
        input_dir = args.root / input_dir
    meta = prepare(args.root, input_dir, speaker)
    print(f"READY · metadata={meta.relative_to(args.root)}")
    print(f"WebUI dataset folder: {args.root / 'data' / 'segments' / speaker}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
