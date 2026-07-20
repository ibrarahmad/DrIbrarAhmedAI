#!/usr/bin/env python3
"""Validate dataset and print exact WebUI training steps for beginners."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from _lib import (
    DEFAULT_SPEAKER,
    ROOT,
    find_rvc_weights,
    load_config,
    read_metadata,
    write_json,
)


def _rvc_steps() -> str:
    if sys.platform.startswith("win"):
        return r"""
# TRAIN IN WEBUI (beginners — do every line)
# Full guide: docs/TRAIN_WEBUI.md

cd "$HOME\DrIbrarAhmedAI\Retrieval-based-Voice-Conversion-WebUI"
python infer-web.py
# Browser → http://localhost:7865 → Train tab

Exact fields:
  Experiment name:  myvoice
  Dataset folder:   $HOME\DrIbrarAhmedAI\rvc-voice-cloning\data\segments\myvoice
  Sample rate:      40k
  F0 method:        rmvpe
  Device:           NVIDIA → CUDA/auto · AMD/Intel → DirectML · else CPU fallback
  Epochs:           200
  Save every:       25
  Batch size:       4            # use 2 if CUDA OOM / RAM low
  Version:          v2
  Pretrained G:     assets/pretrained_v2/f0G40k.pth
  Pretrained D:     assets/pretrained_v2/f0D40k.pth

Click IN ORDER:
  1) Preprocess / process dataset
  2) Extract pitch + features
  3) Train model
  4) Build / train feature index

Copy weights into companion:
  Copy-Item "assets\weights\myvoice.pth" `
    "..\rvc-voice-cloning\models\rvc\speaker.pth"
  Copy-Item "logs\myvoice\*.index" `
    "..\rvc-voice-cloning\models\rvc\myvoice.index"

cd "$HOME\DrIbrarAhmedAI\rvc-voice-cloning"
python configure_rvc.py --check
# REQUIRED: regenerate with YOUR weights (do not reuse demo WAV)
python infer.py --text-file scripts\clone_prove.txt --out output\clone_prove.wav
python play_clone.py --wav output\clone_prove.wav
python next_step.py
"""
    return """
# TRAIN IN WEBUI (beginners — do every line)
# Full guide: docs/TRAIN_WEBUI.md

cd ~/DrIbrarAhmedAI/Retrieval-based-Voice-Conversion-WebUI
python infer-web.py
# Browser → http://localhost:7865 → Train tab

Exact fields:
  Experiment name:  myvoice
  Dataset folder:   ~/DrIbrarAhmedAI/rvc-voice-cloning/data/segments/myvoice
  Sample rate:      40k
  F0 method:        rmvpe
  Device:           cpu          # Mac
  Epochs:           200
  Save every:       25
  Batch size:       4            # use 2 if RAM low
  Version:          v2
  Pretrained G:     assets/pretrained_v2/f0G40k.pth
  Pretrained D:     assets/pretrained_v2/f0D40k.pth

Click IN ORDER:
  1) Preprocess / process dataset
  2) Extract pitch + features
  3) Train model
  4) Build / train feature index

Copy weights into companion:
  cp assets/weights/myvoice.pth  ~/DrIbrarAhmedAI/rvc-voice-cloning/models/rvc/speaker.pth
  cp logs/myvoice/*.index        ~/DrIbrarAhmedAI/rvc-voice-cloning/models/rvc/myvoice.index

cd ~/DrIbrarAhmedAI/rvc-voice-cloning
python configure_rvc.py --check
# REQUIRED: regenerate with YOUR weights (do not reuse demo WAV)
python infer.py --text-file scripts/clone_prove.txt --out output/clone_prove.wav
python play_clone.py --wav output/clone_prove.wav
python next_step.py
"""


def train_prep(root: Path) -> Path:
    cfg = load_config(root)
    speaker = cfg.get("speaker_name") or DEFAULT_SPEAKER
    seg_dir = root / "data" / "segments" / speaker
    meta_path = seg_dir / "metadata.csv"
    if not meta_path.is_file():
        raise SystemExit(
            "No metadata yet. Run:\n"
            f"  python prepare.py --input data/raw --speaker {speaker}\n"
            "Need 10+ minutes clean speech in data/raw/ first."
        )
    meta = read_metadata(meta_path)
    clean = [
        r
        for r in meta
        if (r.get("label") or "").lower() == "clean"
        and not str(r.get("path") or "").startswith("rejected/")
        and (seg_dir / str(r.get("path") or "")).is_file()
    ]
    if not clean:
        raise SystemExit("No clean segments - run prepare.py / clean your data first.")

    total_sec = sum(float(r.get("duration_sec") or 0) for r in clean)
    if total_sec < 60:
        print(
            f"WARNING: only ~{total_sec:.0f}s labeled clean. "
            "Aim for 10+ minutes (600s+) of clean speech for a usable clone."
        )

    manifest = {
        "speaker": speaker,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "sample_rate": cfg.get("sample_rate"),
        "segment_dir": str(seg_dir.relative_to(root)),
        "clean_clips": len(clean),
        "clean_seconds": round(total_sec, 2),
        "rvc_steps": [
            "launch_webui_infer_web_py",
            "fill_train_fields",
            "preprocess",
            "extract_f0_rmvpe",
            "train",
            "build_index",
            "copy_to_models_rvc",
        ],
        "guide": "docs/TRAIN_WEBUI.md",
        "upstream": "https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI",
    }
    out = root / "models" / "training_manifest.json"
    write_json(out, manifest)
    print(f"wrote {out.relative_to(root)}")
    print(f"clean_clips={len(clean)} clean_seconds={total_sec:.1f}")
    print(f"dataset_folder_for_webui={seg_dir}")
    print(_rvc_steps().strip())
    pth, index = find_rvc_weights(root / "models" / "rvc")
    if pth:
        print(f"weights present: {pth.name}" + (f" + {index.name}" if index else ""))
        print("NEXT: python infer.py --text-file scripts/clone_prove.txt --out output/clone_prove.wav")
    else:
        print("weights: MISSING - finish WebUI train, then copy into models/rvc/")
        print("NEXT: follow the WebUI block above, then python next_step.py")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    train_prep(args.root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
