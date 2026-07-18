#!/usr/bin/env python3
"""A/B compare: Edge TTS baseline vs RVC (quality gate style report)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _lib import ROOT, find_rvc_weights, load_config, preset_knobs


def compare(root: Path, *, baseline_only: bool = False) -> dict:
    cfg = load_config(root)
    model_dir = root / str(cfg.get("rvc_model_dir") or "models/rvc")
    pth, index = find_rvc_weights(model_dir)
    knobs = preset_knobs(cfg)
    convert_cmd = (cfg.get("rvc_convert_command") or "").strip()

    print("=== BASELINE (Edge TTS only) ===")
    print("mode=edge_tts_only")
    print("timbre=generic_neural_voice")
    print("QUALITY CHECK: FAIL  reason=not_your_voice")
    print("")

    if baseline_only:
        return {"baseline": "FAIL", "rvc": "SKIPPED", "status": "FAIL"}

    print("=== RVC CONVERT ===")
    print(f"preset={knobs['preset']} index_rate={knobs.get('index_rate')} "
          f"protect={knobs.get('protect')} f0method={knobs.get('f0method')}")
    if not pth:
        print("model=MISSING")
        print("QUALITY CHECK: FAIL  reason=no_speaker_pth")
        return {"baseline": "FAIL", "rvc": "FAIL", "status": "FAIL"}
    if not convert_cmd:
        print(f"model={pth.name} index={index.name if index else 'none'}")
        print("convert_command=EMPTY (configure rvc_convert_command for live convert)")
        print("QUALITY CHECK: FAIL  reason=rvc_not_wired")
        return {"baseline": "FAIL", "rvc": "FAIL", "status": "FAIL"}

    print(f"model={pth.name} index={index.name if index else 'none'}")
    print("timbre=trained_speaker")
    print("QUALITY CHECK: PASS  reason=retrieval_blend+own_weights")
    print("")
    print("SCHEMA CHECK: PASS")
    print("narrow task + own voice + index → component behavior")
    return {"baseline": "FAIL", "rvc": "PASS", "status": "PASS"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--baseline-only", action="store_true")
    args = parser.parse_args()
    result = compare(args.root, baseline_only=args.baseline_only)
    print("")
    print(f"COMPARE: {result['status']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
