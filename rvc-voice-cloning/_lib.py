"""Shared helpers for the RVC voice-cloning companion."""
from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent

# Default speaker / experiment name used across prepare → WebUI → export.
DEFAULT_SPEAKER = "myvoice"


def setup_script_hint() -> str:
    """Platform setup command shown to beginners (matches video Slide 4)."""
    if sys.platform.startswith("win"):
        return ".\\setup_rvc.ps1"
    return "bash setup_rvc.sh"


def venv_activate_lines() -> list[str]:
    if sys.platform.startswith("win"):
        return [
            "  cd $HOME\\DrIbrarAhmedAI\\rvc-voice-cloning",
            "  .\\.venv\\Scripts\\Activate.ps1",
        ]
    return [
        "  cd ~/DrIbrarAhmedAI/rvc-voice-cloning",
        "  source .venv/bin/activate",
    ]


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as exc:
        raise SystemExit("Install PyYAML: pip install -r requirements.txt") from exc
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise SystemExit(f"Expected mapping in {path}")
    return data


def load_config(root: Path | None = None) -> dict[str, Any]:
    base = root or ROOT
    return load_yaml(base / "config.yaml")


def load_consent(root: Path | None = None) -> dict[str, Any]:
    base = root or ROOT
    return load_yaml(base / "consent.yaml")


def find_rvc_weights(model_dir: Path) -> tuple[Path | None, Path | None]:
    pth = next(iter(sorted(model_dir.glob("*.pth"))), None)
    index = next(iter(sorted(model_dir.glob("*.index"))), None)
    return pth, index


def read_text_file(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Missing text file: {path}")
    return path.read_text(encoding="utf-8").strip()


def which(cmd: str) -> str | None:
    return shutil.which(cmd)


def run_cmd(argv: list[str], *, cwd: Path | None = None) -> int:
    print("+", " ".join(argv))
    proc = subprocess.run(argv, cwd=cwd)
    return proc.returncode


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_metadata(csv_path: Path) -> list[dict[str, str]]:
    if not csv_path.is_file():
        return []
    with csv_path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def preset_knobs(cfg: dict[str, Any], name: str | None = None) -> dict[str, Any]:
    presets = cfg.get("inference_presets") or {}
    key = name or cfg.get("inference_default_preset") or "clear"
    knobs = dict(presets.get(key) or {})
    knobs["preset"] = key
    knobs["f0method"] = cfg.get("rvc_f0method") or "rmvpe"
    return knobs
