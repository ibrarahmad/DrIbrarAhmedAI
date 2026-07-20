#!/usr/bin/env python3
"""Inspect prepared segments — live waveform QC — and KEEP/DROP guidance."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _lib import DEFAULT_SPEAKER, ROOT, load_config, read_metadata
from audio_qc import measure_wav


def analyze(root: Path, speaker: str | None = None) -> int:
    cfg = load_config(root)
    speaker = speaker or cfg.get("speaker_name") or DEFAULT_SPEAKER
    seg_dir = root / "data" / "segments" / speaker
    meta_path = seg_dir / "metadata.csv"
    rows = read_metadata(meta_path)

    # Prefer live WAV scan of the training folder (what WebUI will actually see).
    train_wavs = sorted(p for p in seg_dir.glob("seg_*.wav") if p.is_file())
    if not train_wavs and not rows:
        print(f"NO DATA · {meta_path.relative_to(root)}")
        return 1

    keep: list[tuple[str, dict]] = []
    drop: list[tuple[str, dict]] = []

    for path in train_wavs:
        m = measure_wav(path)
        if m["label"] == "clean":
            keep.append((path.name, m))
        else:
            drop.append((path.name, m))

    # Also report rejected/ folder if present.
    reject_dir = seg_dir / "rejected"
    if reject_dir.is_dir():
        for path in sorted(reject_dir.glob("*.wav")):
            m = measure_wav(path)
            drop.append((f"rejected/{path.name}", m))

    # Orphan metadata rows pointing at missing files.
    for r in rows:
        name = r.get("path") or ""
        if not name or name.startswith("rejected/"):
            continue
        if not (seg_dir / name).is_file():
            drop.append(
                (name, {"label": "missing", "duration_sec": 0.0, "rms_dbfs": -96.0})
            )

    clean_sec = sum(float(m["duration_sec"]) for _, m in keep)
    min_minutes = float(cfg.get("min_dataset_minutes") or 10.0)

    print(f"speaker={speaker}")
    print(f"train_wavs={len(train_wavs)}  KEEP={len(keep)}  DROP={len(drop)}")
    print(f"clean_minutes={clean_sec / 60:.2f}  (target ≥ {min_minutes:.1f})")
    print("")
    print("KEEP (in training folder — WebUI uses these):")
    for name, m in keep[:8]:
        print(
            f"  {name}  {float(m['duration_sec']):.2f}s  "
            f"rms={float(m['rms_dbfs']):.1f}  "
            f"clip={float(m.get('clip_ratio') or 0):.3%} → KEEP"
        )
    if len(keep) > 8:
        print(f"  … +{len(keep) - 8} more")
    if drop:
        print("")
        print("DROP (rejected / bad / missing):")
        for name, m in drop[:12]:
            print(
                f"  {name}  label={m['label']}  "
                f"{float(m['duration_sec']):.2f}s → DROP"
            )
        if len(drop) > 12:
            print(f"  … +{len(drop) - 12} more")

    if not keep:
        status = "FAIL"
    elif clean_sec >= min_minutes * 60:
        status = "PASS"
    else:
        status = "REVIEW"

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
