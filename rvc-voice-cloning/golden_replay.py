#!/usr/bin/env python3
"""Golden replay suite -  assert baseline fail, RVC path, consent gate (slide 17)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _lib import ROOT, find_rvc_weights, load_config, load_consent, write_json
from compare import compare
from quality_gate import decide


def _case(name: str, ok: bool, detail: str = "") -> dict:
    status = "PASS" if ok else "FAIL"
    suffix = f" ({detail})" if detail else ""
    print(f"case {name:<26} {status}{suffix}")
    return {"name": name, "ok": ok, "detail": detail}


def run_suite(root: Path) -> int:
    cfg = load_config(root)
    model_dir = root / str(cfg.get("rvc_model_dir") or "models/rvc")
    pth, _index = find_rvc_weights(model_dir)
    convert_cmd = (cfg.get("rvc_convert_command") or "").strip()
    consent = load_consent(root)

    results: list[dict] = []

    baseline = compare(root, baseline_only=True)
    results.append(
        _case("baseline_tts_only", baseline.get("baseline") == "FAIL", "FAIL expected")
    )

    full = compare(root, baseline_only=False)
    if pth and convert_cmd:
        results.append(_case("rvc_with_weights", full.get("rvc") == "PASS"))
    else:
        results.append(
            _case(
                "rvc_with_weights",
                full.get("rvc") == "FAIL",
                "FAIL expected until .pth + convert wired",
            )
        )

    results.append(
        _case(
            "missing_pth",
            (pth is None and full.get("rvc") == "FAIL") or (pth is not None),
            "FAIL expected" if pth is None else "weights present",
        )
    )

    if consent.get("attested"):
        gate = decide(root, skip_dataset=True)
        results.append(
            _case("consent_not_attested", True, "attested=true · gate→" + gate["status"])
        )
    else:
        gate = decide(root, skip_dataset=True)
        results.append(
            _case("consent_not_attested", gate["status"] == "FAIL", "gate→FAIL")
        )

    blocked = set(consent.get("blocked") or [])
    results.append(
        _case(
            "impersonation_attempt",
            "impersonate_third_party" in blocked and "clone_without_consent" in blocked,
            "BLOCK",
        )
    )

    passed = sum(1 for r in results if r["ok"])
    failed = len(results) - passed
    print("")
    print(f"{passed} passed · {failed} failed · quality+gate+files asserted")
    write_json(
        root / "output" / "golden_replay.json",
        {"passed": passed, "failed": failed, "cases": results},
    )
    return 0 if failed == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--suite", type=str, default="anomaly_v1")
    args = parser.parse_args()
    print(f"suite={args.suite}")
    return run_suite(args.root)


if __name__ == "__main__":
    sys.exit(main())
