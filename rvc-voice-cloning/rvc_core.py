#!/usr/bin/env python3
"""RVC core retrieval loop — knobs + convert contract (slides 13–14)."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from _lib import load_config, preset_knobs, which


def retrieval_knobs(cfg: dict[str, Any] | None = None, preset: str | None = None) -> dict[str, Any]:
    """HuBERT content → FAISS retrieve → F0 → VITS.

    index_rate blends source features with nearest training vectors.
    protect keeps consonants stable. f0method=rmvpe is recommended.
    """
    cfg = cfg or load_config()
    knobs = preset_knobs(cfg, preset)
    return {
        "preset": knobs["preset"],
        "index_rate": knobs.get("index_rate", 0.80),  # ↑ more target timbre
        "protect": knobs.get("protect", 0.40),  # consonants
        "f0method": knobs.get("f0method", "rmvpe"),
        "filter_radius": knobs.get("filter_radius", 3),
        "f0up_key": knobs.get("f0up_key", 0),
    }


def run_rvc(
    cmd_template: str,
    base_wav: Path,
    out_wav: Path,
    model_dir: Path,
) -> None:
    """Run configured RVC convert command (WebUI bridge or library CLI)."""
    cmd = (
        cmd_template.replace("{base_wav}", str(base_wav))
        .replace("{out_wav}", str(out_wav))
        .replace("{model_dir}", str(model_dir))
    )
    print(f"[rvc] {cmd}")
    proc = subprocess.run(cmd, shell=True)
    if proc.returncode != 0:
        raise SystemExit(f"RVC convert failed with code {proc.returncode}")


def describe_loop() -> str:
    return (
        "script text → Edge TTS base WAV → "
        "HuBERT + F0(rmvpe) + FAISS(index_rate) → VITS → narration.wav"
    )


if __name__ == "__main__":
    k = retrieval_knobs()
    print(describe_loop())
    print(f"knobs={k}")
    print(f"ffmpeg={'yes' if which('ffmpeg') else 'no'}")
