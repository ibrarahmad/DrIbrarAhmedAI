#!/usr/bin/env python3
"""
Smoke test: prove the companion path works on this machine.

Does NOT flip consent.yaml. Does NOT claim a trained RVC clone without *.pth.

Steps:
  1) ffmpeg / python deps
  2) configure_rvc.py --prefer-library
  3) prepare raw WAV → segments
  4) play raw WAV (1s)
  5) infer clone_prove.txt (Edge TTS or macOS say)
  6) play output (1s)
  7) golden_replay + analyze + train_prep
  8) report RVC ready / not ready
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from _lib import ROOT, find_rvc_weights, load_config, which, write_json


def _run(argv: list[str], *, cwd: Path) -> None:
    print("+", " ".join(argv))
    proc = subprocess.run(argv, cwd=str(cwd))
    if proc.returncode != 0:
        raise SystemExit(f"FAIL: {' '.join(argv)} (code {proc.returncode})")


def main() -> int:
    root = ROOT
    py = sys.executable
    print("SMOKE TEST · rvc-voice-cloning")
    print(f"root={root}")
    print("")

    if not which("ffmpeg"):
        raise SystemExit("FAIL: ffmpeg missing (brew install ffmpeg)")
    print("[ok] ffmpeg")

    raw = root / "data" / "raw" / "my_voice_01.wav"
    if not raw.is_file():
        # copy demo audio into data/raw so record→play always has a file
        demo = root / "demo_audio" / "user_raw.mp3"
        if not demo.is_file():
            raise SystemExit("FAIL: no data/raw/*.wav and no demo_audio/user_raw.mp3")
        raw.parent.mkdir(parents=True, exist_ok=True)
        _run(
            ["ffmpeg", "-y", "-i", str(demo), "-ac", "1", "-ar", "40000", str(raw)],
            cwd=root,
        )
    print(f"[ok] raw wav: {raw.relative_to(root)}")

    _run([py, "configure_rvc.py", "--prefer-library"], cwd=root)
    _run([py, "prepare.py", "--input", "data/raw", "--speaker", "demo"], cwd=root)
    _run([py, "analyze.py"], cwd=root)
    _run([py, "train_prep.py"], cwd=root)

    _run(
        [py, "play_clone.py", "--wav", str(raw), "--label", "PLAY RAW", "--seconds", "1"],
        cwd=root,
    )

    prove_out = root / "output" / "smoke_baseline.wav"
    _run(
        [
            py,
            "infer.py",
            "--text-file",
            "scripts/clone_prove.txt",
            "--out",
            str(prove_out),
            "--baseline-only",
        ],
        cwd=root,
    )
    if not prove_out.is_file():
        raise SystemExit("FAIL: infer did not write output/smoke_baseline.wav")
    print(f"[ok] baseline smoke wrote {prove_out.relative_to(root)} (NOT a real clone)")

    _run(
        [
            py,
            "play_clone.py",
            "--wav",
            str(prove_out),
            "--label",
            "PLAY PROVE SCRIPT",
            "--seconds",
            "1",
        ],
        cwd=root,
    )

    _run([py, "golden_replay.py"], cwd=root)
    _run([py, "pipeline.py", "--skip-gate", "--baseline-only", "--text-file", "scripts/sample_line.txt"], cwd=root)

    cfg = load_config(root)
    model_dir = root / str(cfg.get("rvc_model_dir") or "models/rvc")
    pth, index = find_rvc_weights(model_dir)
    convert = str(cfg.get("rvc_convert_command") or "").strip()
    lib = which("rvc") is not None
    try:
        import rvc  # noqa: F401

        lib = True
    except Exception:
        pass

    payload = {
        "smoke": "PASS",
        "ffmpeg": True,
        "raw": str(raw.relative_to(root)),
        "prove": str(prove_out.relative_to(root)),
        "rvc_convert_command": bool(convert),
        "rvc_library": lib,
        "speaker_pth": pth.name if pth else None,
        "speaker_index": index.name if index else None,
        "rvc_convert_ready": bool(pth and convert and lib),
        "next_for_real_clone": [
            "bash setup_rvc.sh",
            "set attested: true in consent.yaml (own voice only)",
            "train in WebUI, copy speaker.pth + .index → models/rvc/",
            "python infer.py --text-file scripts/clone_prove.txt --out output/clone_prove.wav",
            "python play_clone.py --wav output/clone_prove.wav --label 'PLAY CLONE'",
            "python next_step.py  # must say fresh + RVC",
        ],
    }
    write_json(root / "output" / "smoke_test.json", payload)

    print("")
    print("SMOKE: PASS")
    print(f"  convert command wired: {bool(convert)}")
    print(f"  rvc library installed: {lib}")
    print(f"  speaker.pth present:   {bool(pth)}")
    if payload["rvc_convert_ready"]:
        print("  RVC CONVERT: READY")
    else:
        print("  RVC CONVERT: NOT READY yet (install + train + copy .pth)")
        for step in payload["next_for_real_clone"]:
            print(f"    - {step}")
    print("wrote output/smoke_test.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
