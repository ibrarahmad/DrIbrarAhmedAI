#!/usr/bin/env python3
"""Inspect prepared segments — live waveform QC — and KEEP/DROP guidance."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _lib import DEFAULT_SPEAKER, ROOT, load_config, read_metadata
from audio_qc import measure_wav


def _report_path(root: Path, speaker: str) -> Path:
    modern = root / "data" / "reports" / f"{speaker}.csv"
    if modern.is_file():
        return modern
    # Legacy location from earlier companion builds.
    return root / "data" / "segments" / speaker / "metadata.csv"


def analyze(root: Path, speaker: str | None = None) -> int:
    cfg = load_config(root)
    speaker = speaker or cfg.get("speaker_name") or DEFAULT_SPEAKER
    seg_dir = root / "data" / "segments" / speaker
    reject_dir = root / "data" / "rejected" / speaker
    meta_path = _report_path(root, speaker)
    rows = read_metadata(meta_path)

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

    if reject_dir.is_dir():
        for path in sorted(reject_dir.glob("*.wav")):
            m = measure_wav(path)
            drop.append((f"data/rejected/{speaker}/{path.name}", m))

    # Legacy in-folder rejects (should be empty after prepare).
    legacy_reject = seg_dir / "rejected"
    if legacy_reject.is_dir():
        for path in sorted(legacy_reject.glob("*.wav")):
            m = measure_wav(path)
            drop.append((f"segments/.../rejected/{path.name}", m))

    for r in rows:
        name = r.get("path") or ""
        if not name or "rejected" in name:
            continue
        # path may be relative like data/segments/myvoice/seg_001.wav
        candidate = root / name if name.startswith("data/") else seg_dir / Path(name).name
        if not candidate.is_file() and not (seg_dir / Path(name).name).is_file():
            drop.append(
                (name, {"label": "missing", "duration_sec": 0.0, "rms_dbfs": -96.0})
            )

    clean_sec = sum(float(m["duration_sec"]) for _, m in keep)
    min_minutes = float(cfg.get("min_dataset_minutes") or 10.0)

    print(f"speaker={speaker}")
    print(f"train_wavs={len(train_wavs)}  KEEP={len(keep)}  DROP={len(drop)}")
    print(f"clean_minutes={clean_sec / 60:.2f}  (target ≥ {min_minutes:.1f})")
    print(f"report={meta_path.relative_to(root)}")
    print("")
    print("KEEP (WebUI training folder — WAV only):")
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
        print("DROP (clipped / too-hot / silent / missing):")
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
