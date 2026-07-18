#!/usr/bin/env python3
"""Summarize segment metadata - clean vs noisy/reverb."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _lib import ROOT, load_config, read_metadata


def analyze(root: Path, speaker: str | None = None) -> int:
    cfg = load_config(root)
    speaker = speaker or cfg.get("speaker_name") or "demo"
    meta_path = root / "data" / "segments" / speaker / "metadata.csv"
    rows = read_metadata(meta_path)
    if not rows:
        print(f"NO DATA · {meta_path.relative_to(root)}")
        return 1

    clean = [r for r in rows if (r.get("label") or "").lower() == "clean"]
    noisy = [r for r in rows if (r.get("label") or "").lower() == "noisy"]
    reverb = [r for r in rows if (r.get("label") or "").lower() == "reverb"]
    total_sec = sum(float(r.get("duration_sec") or 0) for r in clean)

    print(f"speaker={speaker}")
    print(f"rows={len(rows)}  clean={len(clean)}  noisy={len(noisy)}  reverb={len(reverb)}")
    print(f"clean_minutes={total_sec/60:.2f}")
    print("")
    print("NORMAL (train these):")
    for r in clean[:5]:
        print(f"  {r.get('path')}  {r.get('duration_sec')}s  rms={r.get('rms_dbfs')} → KEEP")
    if noisy or reverb:
        print("")
        print("ANOMALY (drop before train):")
        for r in noisy + reverb:
            print(f"  {r.get('path')}  label={r.get('label')} → DROP")
    status = "PASS" if not noisy and not reverb and total_sec >= 60 else "REVIEW"
    print("")
    print(f"DATASET CHECK: {status}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--speaker", type=str, default=None)
    args = parser.parse_args()
    return analyze(args.root, args.speaker)


if __name__ == "__main__":
    sys.exit(main())
