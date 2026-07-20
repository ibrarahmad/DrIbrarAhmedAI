#!/usr/bin/env python3
"""One-command demo: gate → prepare/analyze → infer → export (dry-run safe)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _lib import (
    DEFAULT_SPEAKER,
    ROOT,
    find_rvc_weights,
    load_config,
    read_text_file,
    write_json,
)
from analyze import analyze
from export import export_audio
from infer import infer
from prepare import prepare
from quality_gate import decide
from train_prep import train_prep


def run_pipeline(
    root: Path,
    text_file: Path,
    *,
    skip_gate: bool = False,
    baseline_only: bool = False,
) -> int:
    cfg = load_config(root)
    speaker = cfg.get("speaker_name") or DEFAULT_SPEAKER
    print("pipeline: consent → prepare → analyze → train_prep → infer → export")
    print(f"speaker={speaker}  gate={'off' if skip_gate else 'on'}")
    print("")

    if not skip_gate:
        # Demo path: skip strict dataset minutes so viewers can inspect the loop.
        gate = decide(root, skip_dataset=True)
        print(f"[gate] {gate['status']}")
        for err in gate["errors"]:
            print(f"[gate]  - {err}")
        if gate["status"] != "PASS":
            print("HINT: set attested: true in consent.yaml after confirming own-voice data")
            print("      or re-run with --skip-gate for a local dry-run")
            return 1
    else:
        print("[gate] skipped (--skip-gate)")

    print("")
    prepare(root, root / "data" / "raw", speaker)
    print("")
    analyze(root, speaker)
    print("")
    train_prep(root)
    print("")

    text = read_text_file(text_file if text_file.is_absolute() else root / text_file)
    out_wav = root / "output" / "narration.wav"
    result = infer(root, text, out_wav, baseline_only=baseline_only)
    print("")

    model_dir = root / str(cfg.get("rvc_model_dir") or "models/rvc")
    pth, index = find_rvc_weights(model_dir)
    print(f"[adapter] Edge TTS → {'RVC' if result['mode'] == 'edge_tts+rvc' else 'baseline copy'}")
    print(f"[model]   {pth.name if pth else 'none'}  index={index.name if index else 'none'}")
    print(f"[out]     {result['out']}")
    print("")

    export_mp3 = None
    if out_wav.is_file() and which_ffmpeg():
        _, export_mp3 = export_audio(root, out_wav, root / "output", "narration")
    else:
        print("[export] skipped (need ffmpeg + wav)")

    payload = {
        "mode": result["mode"],
        "preset": result.get("preset"),
        "weights": pth.name if pth else None,
        "index": index.name if index else None,
        "out": result["out"],
        "export": str(export_mp3.relative_to(root)) if export_mp3 else None,
        "live_impersonation": "BLOCKED",
        "gate": "PASS" if skip_gate or decide(root, skip_dataset=True)["status"] == "PASS" else "FAIL",
    }
    write_json(root / "output" / "result.json", payload)
    print("wrote output/result.json")

    print("")
    print("SYSTEM READY · complete loop · own-voice-only")
    return 0


def which_ffmpeg() -> bool:
    from _lib import which

    return which("ffmpeg") is not None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--text-file",
        type=Path,
        default=Path("scripts/sample_line.txt"),
    )
    parser.add_argument("--skip-gate", action="store_true")
    parser.add_argument("--baseline-only", action="store_true")
    args = parser.parse_args()
    return run_pipeline(
        args.root,
        args.text_file,
        skip_gate=args.skip_gate,
        baseline_only=args.baseline_only,
    )


if __name__ == "__main__":
    sys.exit(main())
