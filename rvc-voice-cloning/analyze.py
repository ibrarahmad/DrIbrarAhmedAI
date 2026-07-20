#!/usr/bin/env python3
"""Inspect segment WAVs — duration, loudness, clipping — and KEEP/DROP guidance."""
from __future__ import annotations

import argparse
import audioop
import math
import struct
import sys
import wave
from pathlib import Path

from _lib import ROOT, load_config, read_metadata


def _measure(path: Path) -> dict[str, float | str]:
    with wave.open(str(path), "rb") as wf:
        nch = wf.getnchannels()
        sw = wf.getsampwidth()
        sr = wf.getframerate()
        nframes = wf.getnframes()
        raw = wf.readframes(nframes)
    if nch != 1 or sw != 2:
        # Still report duration; mark for review.
        dur = nframes / float(sr or 1)
        return {
            "duration_sec": dur,
            "rms_dbfs": -96.0,
            "clip_ratio": 0.0,
            "label": "noisy",
        }
    dur = nframes / float(sr or 1)
    rms = audioop.rms(raw, 2)
    rms_db = -96.0 if rms <= 0 else 20.0 * math.log10(rms / 32768.0)
    n = len(raw) // 2
    samples = struct.unpack("<" + "h" * n, raw) if n else ()
    clipped = sum(1 for s in samples if abs(s) >= 32000)
    clip_ratio = (clipped / n) if n else 0.0
    if rms_db <= -50:
        label = "silence"
    elif clip_ratio >= 0.01:
        label = "clipped"
    elif rms_db > -6.0:
        label = "noisy"
    elif clip_ratio >= 0.005 and rms_db > -14.0:
        label = "noisy"
    else:
        label = "clean"
    return {
        "duration_sec": dur,
        "rms_dbfs": rms_db,
        "clip_ratio": clip_ratio,
        "label": label,
    }


def analyze(root: Path, speaker: str | None = None) -> int:
    cfg = load_config(root)
    speaker = speaker or cfg.get("speaker_name") or "myvoice"
    seg_dir = root / "data" / "segments" / speaker
    meta_path = seg_dir / "metadata.csv"
    rows = read_metadata(meta_path)
    if not rows:
        # Fall back to scanning WAVs directly.
        wavs = sorted(seg_dir.glob("seg_*.wav"))
        if not wavs:
            print(f"NO DATA · {meta_path.relative_to(root)}")
            return 1
        rows = [{"path": p.name} for p in wavs]

    keep: list[tuple[str, dict]] = []
    drop: list[tuple[str, dict]] = []
    for r in rows:
        name = r.get("path") or ""
        path = seg_dir / name
        if not path.is_file():
            drop.append((name or "?", {"label": "missing", "duration_sec": 0.0, "rms_dbfs": -96.0}))
            continue
        m = _measure(path)
        # Prefer live measurement over stale CSV labels.
        bucket = keep if m["label"] == "clean" else drop
        bucket.append((name, m))

    clean_sec = sum(float(m["duration_sec"]) for _, m in keep)
    min_minutes = float(cfg.get("min_dataset_minutes") or 10.0)

    print(f"speaker={speaker}")
    print(f"segments={len(keep)+len(drop)}  KEEP={len(keep)}  DROP={len(drop)}")
    print(f"clean_minutes={clean_sec/60:.2f}  (target ≥ {min_minutes:.1f})")
    print("")
    print("KEEP (train these):")
    for name, m in keep[:8]:
        print(
            f"  {name}  {float(m['duration_sec']):.2f}s  "
            f"rms={float(m['rms_dbfs']):.1f}  clip={float(m.get('clip_ratio') or 0):.3%} → KEEP"
        )
    if len(keep) > 8:
        print(f"  … +{len(keep)-8} more")
    if drop:
        print("")
        print("DROP (noise / clip / silence / missing):")
        for name, m in drop[:12]:
            print(
                f"  {name}  label={m['label']}  "
                f"{float(m['duration_sec']):.2f}s → DROP"
            )
        if len(drop) > 12:
            print(f"  … +{len(drop)-12} more")

    status = "PASS" if keep and clean_sec >= min_minutes * 60 else "REVIEW"
    if not keep:
        status = "FAIL"
    print("")
    print(f"DATASET CHECK: {status}")
    if status != "PASS":
        print(
            f"Need ~{min_minutes:.0f}+ minutes of clean speech. "
            "Re-record, then prepare.py again."
        )
    return 0 if status != "FAIL" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--speaker", type=str, default=None)
    args = parser.parse_args()
    return analyze(args.root, args.speaker)


if __name__ == "__main__":
    sys.exit(main())
