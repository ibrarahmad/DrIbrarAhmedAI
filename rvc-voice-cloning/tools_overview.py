#!/usr/bin/env python3
"""Three day-to-day tools the pipeline exposes (slide 08)."""
from __future__ import annotations

from pathlib import Path

from analyze import analyze
from infer import infer
from prepare import prepare
from train_prep import train_prep
from _lib import ROOT, load_config, read_text_file


def tool_prepare(raw_dir: str | Path | None = None, speaker: str | None = None) -> str:
    """Clean mono clips + metadata.csv. Never trains on third-party audio."""
    cfg = load_config(ROOT)
    sp = speaker or cfg.get("speaker_name") or "demo"
    src = Path(raw_dir) if raw_dir else ROOT / "data" / "raw"
    meta = prepare(ROOT, src, sp)
    return str(meta.relative_to(ROOT))


def tool_train_prep() -> str:
    """Validate clean rows; print external RVC train steps; write manifest."""
    out = train_prep(ROOT)
    return str(out.relative_to(ROOT))


def tool_infer(text_file: str = "scripts/sample_line.txt") -> str:
    """Edge TTS base → RVC convert when weights exist. Own voice only."""
    path = ROOT / text_file
    text = read_text_file(path)
    out = ROOT / "output" / "narration.wav"
    result = infer(ROOT, text, out)
    return result["out"]


# Explicitly absent — do not implement:
#   steal_celebrity_voice
#   clone_without_consent
#   impersonate_third_party


if __name__ == "__main__":
    print("tools registered: prepare, train_prep, infer")
    print("ok")
    analyze(ROOT)
