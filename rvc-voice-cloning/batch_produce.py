#!/usr/bin/env python3
"""Batch producer - run multiple scripts, drop short/failed clips (slide 15)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _lib import ROOT, load_config, preset_knobs, read_text_file, write_json
from infer import infer
from quality_gate import decide


def batch_produce(
    root: Path,
    scripts_dir: Path,
    *,
    skip_gate: bool = False,
    min_chars: int = 20,
) -> list[dict]:
    cfg = load_config(root)
    knobs = preset_knobs(cfg)
    if not skip_gate:
        gate = decide(root, skip_dataset=True)
        print(f"[gate] {gate['status']}")
        if gate["status"] != "PASS":
            for err in gate["errors"]:
                print(f"[gate] - {err}")
            raise SystemExit(1)

    files = sorted(scripts_dir.glob("*.txt"))
    if not files:
        raise SystemExit(f"No *.txt scripts in {scripts_dir}")

    results: list[dict] = []
    out_dir = root / "output" / "batch"
    out_dir.mkdir(parents=True, exist_ok=True)

    for i, path in enumerate(files, start=1):
        text = read_text_file(path)
        name = path.stem
        if len(text) < min_chars:
            print(f"[{i:02d}] {name:<12} DROP  chars<{min_chars}")
            results.append({"script": name, "status": "DROP", "reason": "too_short"})
            continue
        out_wav = out_dir / f"{name}.wav"
        result = infer(root, text, out_wav, preset=knobs["preset"])
        print(
            f"[{i:02d}] {name:<12} PASS  preset={knobs['preset']}  "
            f"mode={result['mode']}  → {result['out']}"
        )
        results.append(
            {
                "script": name,
                "status": "PASS",
                "out": result["out"],
                "mode": result["mode"],
                "preset": knobs["preset"],
            }
        )

    write_json(root / "output" / "batch_report.json", {"rows": results})
    print(f"wrote output/batch_report.json ({len(results)} rows)")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--scripts-dir", type=Path, default=None)
    parser.add_argument("--skip-gate", action="store_true")
    args = parser.parse_args()
    scripts = args.scripts_dir or (args.root / "scripts")
    if not scripts.is_absolute():
        scripts = args.root / scripts
    batch_produce(args.root, scripts, skip_gate=args.skip_gate)
    return 0


if __name__ == "__main__":
    sys.exit(main())
