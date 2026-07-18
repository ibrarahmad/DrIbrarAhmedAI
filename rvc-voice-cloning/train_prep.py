#!/usr/bin/env python3
"""Validate dataset and print external RVC training steps (no fake training)."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from _lib import ROOT, find_rvc_weights, load_config, read_metadata, write_json


RVC_STEPS = """
# External RVC train (WebUI or library) — run outside this folder
# Upstream: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion
# WebUI:    https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI

1. preprocess  — resample/slice clips → 40k mono
2. extract F0  — rmvpe (recommended)
3. extract HuBERT features → 3_feature768 (v2)
4. train       — G/D from pretrained_v2 (~100–200 epochs)
5. build index — FAISS .index from training features
6. export      — copy best G_*.pth + .index → models/rvc/
"""


def train_prep(root: Path) -> Path:
    cfg = load_config(root)
    speaker = cfg.get("speaker_name") or "demo"
    seg_dir = root / "data" / "segments" / speaker
    meta = read_metadata(seg_dir / "metadata.csv")
    clean = [r for r in meta if (r.get("label") or "").lower() == "clean"]
    if not clean:
        raise SystemExit("No clean segments — run prepare.py / clean your data first.")

    total_sec = sum(float(r.get("duration_sec") or 0) for r in clean)
    manifest = {
        "speaker": speaker,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "sample_rate": cfg.get("sample_rate"),
        "segment_dir": str(seg_dir.relative_to(root)),
        "clean_clips": len(clean),
        "clean_seconds": round(total_sec, 2),
        "rvc_steps": [
            "preprocess",
            "extract_f0_rmvpe",
            "extract_hubert",
            "train",
            "build_index",
            "export_to_models_rvc",
        ],
        "upstream": "https://github.com/RVC-Project/Retrieval-based-Voice-Conversion",
    }
    out = root / "models" / "training_manifest.json"
    write_json(out, manifest)
    print(f"wrote {out.relative_to(root)}")
    print(f"clean_clips={len(clean)} clean_seconds={total_sec:.1f}")
    print(RVC_STEPS.strip())
    pth, index = find_rvc_weights(root / "models" / "rvc")
    if pth:
        print(f"weights present: {pth.name}" + (f" + {index.name}" if index else ""))
    else:
        print("weights: MISSING — place speaker.pth (+ .index) in models/rvc/ after train")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    train_prep(args.root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
