#!/usr/bin/env python3
"""Own-voice consent + duration / dataset quality gate."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _lib import DEFAULT_SPEAKER, ROOT, load_config, load_consent, read_metadata


def check_consent(root: Path, *, require_attested: bool = True) -> list[str]:
    consent = load_consent(root)
    errors: list[str] = []
    if consent.get("policy") != "own_voice_only":
        errors.append("policy must be own_voice_only")
    blocked = set(consent.get("blocked") or [])
    for item in ("clone_without_consent", "impersonate_third_party"):
        if item not in blocked:
            errors.append(f"blocked list missing: {item}")
    if require_attested and not consent.get("attested"):
        errors.append("consent.yaml attested=false - set attested: true after you confirm own-voice recordings")
    return errors


def check_dataset(root: Path) -> list[str]:
    cfg = load_config(root)
    speaker = cfg.get("speaker_name") or DEFAULT_SPEAKER
    seg_dir = root / "data" / "segments" / speaker
    meta_path = root / "data" / "reports" / f"{speaker}.csv"
    if not meta_path.is_file():
        meta_path = seg_dir / "metadata.csv"
    rows = read_metadata(meta_path)
    errors: list[str] = []
    train_wavs = list(seg_dir.glob("seg_*.wav"))
    if not train_wavs:
        errors.append(f"no training WAVs in {seg_dir.relative_to(root)}")
        return errors
    if not rows:
        errors.append(f"no report at {meta_path.relative_to(root)}")
        return errors
    clean = [
        r
        for r in rows
        if (r.get("label") or "").lower() == "clean"
        and "rejected" not in str(r.get("path") or "")
    ]
    total_sec = sum(float(r.get("duration_sec") or 0) for r in clean)
    min_minutes = float(cfg.get("min_dataset_minutes") or 10)
    if total_sec / 60.0 < min_minutes:
        errors.append(
            f"clean speech {total_sec/60:.1f} min < min_dataset_minutes={min_minutes}"
        )
    bad = [
        r
        for r in rows
        if (r.get("label") or "").lower()
        in {"too-hot", "clipped", "silent", "noisy", "reverb", "silence"}
    ]
    if bad:
        errors.append(
            f"{len(bad)} dropped rows (clipped/too-hot/silent) — re-prepare before train"
        )
    return errors


def decide(root: Path, *, skip_dataset: bool = False) -> dict:
    errors = check_consent(root)
    if not skip_dataset:
        errors.extend(check_dataset(root))
    ok = not errors
    return {
        "status": "PASS" if ok else "FAIL",
        "errors": errors,
        "gate": "quality_gate",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--skip-dataset", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = decide(args.root, skip_dataset=args.skip_dataset)
    if args.json:
        import json

        print(json.dumps(result, indent=2))
    else:
        print(f"QUALITY GATE: {result['status']}")
        for err in result["errors"]:
            print(f" - {err}")
        if result["status"] == "PASS":
            print("consent ok · dataset ok · proceed")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
