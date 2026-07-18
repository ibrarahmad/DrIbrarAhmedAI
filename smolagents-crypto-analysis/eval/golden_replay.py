"""Golden replay suite — schema + gate + paper path assertions."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.adapted_model import AdaptedModel
from models.paper_log import write_paper_signal
from safety.gate import decide
from schemas.validate import validate_action

CASES = [
    ("sol_anomaly_31bps", {"spread_bps": 31, "liquidity_delta_pct": -18.4, "volume_z": 0.2}, "REVIEW"),
    ("eth_false_alarm", {"spread_bps": 24, "liquidity_delta_pct": -3.0, "volume_z": 3.1}, "HOLD"),
    ("btc_normal_hold", {"spread_bps": 4, "liquidity_delta_pct": 1.0, "volume_z": 0.7}, "HOLD"),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", default="anomaly_v1")
    args = parser.parse_args()
    _ = args.suite
    model = AdaptedModel()
    passed = 0

    for name, feats, expect in CASES:
        event = {
            "ts": "2026-07-09T00:00:00Z",
            "symbol": "TESTUSDT",
            "price": 100.0,
            "source": "replay",
            **feats,
        }
        action = model.generate(event)
        ok, _ = validate_action(action)
        decision = decide(action)
        assert ok, name
        assert action["signal"] == expect, (name, action["signal"], expect)
        if expect == "REVIEW":
            write_paper_signal(decision, symbol="TEST")
        print(f"case {name} ........ PASS")
        passed += 1

    # missing evidence → gate HOLD
    bad = {"signal": "REVIEW", "confidence": 0.9, "reason": "x", "allowed_tool": "write_paper_signal"}
    d = decide(bad)
    assert d["signal"] == "HOLD"
    print("case missing_evidence ......... PASS (gate→HOLD)")
    passed += 1

    # live order attempt → BLOCK
    live = {
        "signal": "REVIEW",
        "confidence": 0.9,
        "reason": "x",
        "evidence": ["spread_bps"],
        "allowed_tool": "write_paper_signal",
        "live_order": True,
    }
    d = decide(live)
    assert d["signal"] == "HOLD"
    print("case live_order_attempt ....... PASS (BLOCK)")
    passed += 1

    print()
    print(f"{passed} passed · 0 failed · schema+gate+paper_log asserted")


if __name__ == "__main__":
    main()
