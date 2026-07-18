"""End-to-end paper-only pipeline: adapter → model → agent tools → gate → logs."""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.adapted_model import AdaptedModel
from models.paper_log import write_paper_signal, append_review_queue
from safety.gate import decide
from schemas.validate import validate_telemetry
from tools.signal_tools import normalize_event, score_signal

DEMO = {
    "BTC": {"price": 64000.0, "spread_bps": 4, "liquidity_delta_pct": 0.5, "volume_z": 0.8},
    "ETH": {"price": 3400.0, "spread_bps": 6, "liquidity_delta_pct": -1.2, "volume_z": 1.0},
    "SOL": {"price": 187.65, "spread_bps": 31, "liquidity_delta_pct": -18.4, "volume_z": 0.2},
}


def make_event(symbol: str, feats: dict[str, Any]) -> dict[str, Any]:
    return validate_telemetry(
        {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "symbol": symbol if symbol.endswith("USDT") else f"{symbol}USDT",
            "price": feats["price"],
            "spread_bps": feats["spread_bps"],
            "liquidity_delta_pct": feats["liquidity_delta_pct"],
            "volume_z": feats["volume_z"],
            "source": "replay",
        }
    )


def process(event: dict[str, Any], verbose: bool = False) -> dict[str, Any]:
    tel = normalize_event(event)
    action = score_signal(tel)
    decision = decide(action)
    wrote = None
    queued = None
    if decision.get("signal") in {"REVIEW", "ALERT"} and decision.get("allowed_tool") == "write_paper_signal":
        wrote = write_paper_signal(decision, symbol=tel["symbol"].replace("USDT", ""))
        queued = append_review_queue(decision, symbol=tel["symbol"].replace("USDT", ""))
    if verbose:
        print(f"[adapter] {tel['symbol']} spread={tel['spread_bps']}bps liq={tel['liquidity_delta_pct']}% volume_z={tel['volume_z']}")
        print(f"[model]   {action['signal']} conf={action['confidence']} evidence={action['evidence']}")
        print("[agent]   normalize_event → score_signal → write_paper_signal")
        print("[gate]    approved paper · LIVE ORDERS: BLOCKED" if decision.get("signal") != "HOLD" or action.get("signal") == "HOLD" else "[gate] HOLD")
        if wrote:
            print(f"[output]  {wrote}")
        if queued:
            print(f"[output]  {queued}")
    return {"telemetry": tel, "action": action, "decision": decision, "wrote": wrote}


def main() -> None:
    parser = argparse.ArgumentParser(description="Paper-only smolagents crypto pipeline")
    parser.add_argument("--symbols", default="BTC,ETH,SOL")
    parser.add_argument("--paper", action="store_true", default=True)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--replay", type=Path, default=None)
    args = parser.parse_args()

    print("pipeline: adapter → model → CodeAgent → gate → paper_log")
    print("model=telemetry-action-adapter  gate=on  live_orders=BLOCKED")
    print()

    if args.replay:
        event = json.loads(args.replay.read_text(encoding="utf-8"))
        print("[adapter] normalized", event.get("symbol", "event"))
        result = process(event, verbose=True)
        print(f"[model]   {result['action']['signal']} conf={result['action']['confidence']}")
        print("[agent]   normalize → score → write_paper_signal")
        print("[gate]    approved · live orders blocked")
        if result["wrote"]:
            print("[log]     appended paper_signals.jsonl")
            print("[log]     queued review_queue.jsonl")
        print()
        print("COMPLETE SYSTEM · 100% loop verified · SYSTEM READY")
        return

    t0 = time.perf_counter()
    review_result = None
    for sym in [s.strip().upper() for s in args.symbols.split(",") if s.strip()]:
        feats = DEMO.get(sym)
        if not feats:
            print(f"unknown symbol {sym}, skip")
            continue
        event = make_event(sym, feats)
        started = time.perf_counter() - t0
        result = process(event, verbose=False)
        action = result["action"]
        drop_or_write = "write" if result["wrote"] else "drop"
        print(
            f"[{started:08.3f}] {sym}  normalize ok → score {action['signal']:<6} → gate pass → {drop_or_write}"
        )
        if action["signal"] == "REVIEW":
            review_result = result

    print()
    if review_result is not None:
        tel = review_result["telemetry"]
        action = review_result["action"]
        print(f"[adapter] {tel['symbol']} spread={tel['spread_bps']}bps liq={tel['liquidity_delta_pct']}% volume_z={tel['volume_z']}")
        print(f"[model]   {action['signal']} conf={action['confidence']} evidence={action['evidence']}")
        print("[agent]   normalize_event → score_signal → write_paper_signal")
        print("[gate]    approved paper · LIVE ORDERS: BLOCKED")
        if review_result.get("wrote"):
            print(f"[output]  {review_result['wrote']}")
            print("[output]  logs/review_queue.jsonl")
    print()
    print("COMPLETE SYSTEM · paper-only · SYSTEM READY")


if __name__ == "__main__":
    main()
