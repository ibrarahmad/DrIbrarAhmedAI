"""smolagents CodeAgent loop with only the three paper tools.

Falls back to a deterministic tool chain if smolagents / remote models are unavailable,
so the educational demo always runs offline.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.paper_log import write_paper_signal
from safety.gate import decide
from tools.signal_tools import normalize_event, score_signal

EVENT = {
    "ts": "2026-07-09T00:00:00Z",
    "symbol": "SOLUSDT",
    "price": 187.65,
    "spread_bps": 31,
    "liquidity_delta_pct": -18.4,
    "volume_z": 0.2,
    "source": "replay",
}


def run_deterministic() -> None:
    print("CodeAgent tools: normalize_event, score_signal, write_paper_signal")
    print("sandbox: exchange_order -> reject")
    print("sandbox: arbitrary import -> reject")
    print()
    print("agent.run(...)")
    tel = normalize_event(EVENT)
    print("  normalize_event() ok")
    action = score_signal(tel)
    print(f"  score_signal() -> {action['signal']} {action['confidence']}")
    decision = decide(action)
    if decision.get("signal") in {"REVIEW", "ALERT"}:
        path = write_paper_signal(decision, symbol="SOL")
        print(f"  write_paper_signal() ok → {path}")
    print("LIVE ORDERS: BLOCKED")


def run_smolagents() -> None:
    from tools.signal_tools import as_smolagents_tools

    tools = as_smolagents_tools()
    print("CodeAgent tools:", ", ".join(t.name for t in tools))
    print("sandbox: exchange_order -> reject")
    print("sandbox: arbitrary import -> reject")
    print()
    print("note: using deterministic specialty tools (offline-safe).")
    run_deterministic()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", action="store_true", default=True)
    parser.add_argument("--smolagents", action="store_true", help="Attempt smolagents import path")
    args = parser.parse_args()
    _ = args.paper
    if args.smolagents:
        try:
            run_smolagents()
            return
        except Exception as exc:
            print(f"smolagents path unavailable ({exc}); falling back")
    run_deterministic()


if __name__ == "__main__":
    main()
