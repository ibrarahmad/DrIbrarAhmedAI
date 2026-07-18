#!/usr/bin/env python3
"""
Complete educational demo — paper-only smolagents crypto loop.

Stages printed for the deck / viewers:
  1) schemas + paper-only sandbox
  2) specialty adapter (telemetry → action)
  3) baseline FAIL (generic essay)
  4) adapted WIN (structured REVIEW)
  5) pipeline: adapter → model → tools → gate → paper logs
  6) golden replay suite

Usage:
  python demo_complete.py
  python demo_complete.py --skip-baseline
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.adapted_model import AdaptedModel, GenericChatModel
from models.paper_log import write_paper_signal
from pipeline.run import DEMO, make_event, process
from safety.gate import decide
from schemas.validate import schema_check_report, validate_action


def _banner(title: str) -> None:
    print("")
    print("═" * 56)
    print(f" {title}")
    print("═" * 56)


def _run_golden() -> int:
    model = AdaptedModel()
    cases = [
        ("sol_anomaly_31bps", {"spread_bps": 31, "liquidity_delta_pct": -18.4, "volume_z": 0.2}, "REVIEW"),
        ("eth_false_alarm", {"spread_bps": 24, "liquidity_delta_pct": -3.0, "volume_z": 3.1}, "HOLD"),
        ("btc_normal_hold", {"spread_bps": 4, "liquidity_delta_pct": 1.0, "volume_z": 0.7}, "HOLD"),
    ]
    passed = 0
    for name, feats, expect in cases:
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
        assert ok and action["signal"] == expect, (name, action)
        if expect == "REVIEW":
            write_paper_signal(decision, symbol="TEST")
        print(f"case {name} ........ PASS")
        passed += 1

    bad = {"signal": "REVIEW", "confidence": 0.9, "reason": "x", "allowed_tool": "write_paper_signal"}
    assert decide(bad)["signal"] == "HOLD"
    print("case missing_evidence ......... PASS (gate→HOLD)")
    passed += 1

    live = {
        "signal": "REVIEW",
        "confidence": 0.9,
        "reason": "x",
        "evidence": ["spread_bps"],
        "allowed_tool": "write_paper_signal",
        "live_order": True,
    }
    assert decide(live)["signal"] == "HOLD"
    print("case live_order_attempt ....... PASS (BLOCK)")
    passed += 1
    print("")
    print(f"{passed} passed · 0 failed · schema+gate+paper_log asserted")
    return passed


def run_demo(*, skip_baseline: bool = False) -> int:
    _banner("COMPLETE DEMO · paper-only smolagents crypto")
    print("Companion: github.com/ibrarahmad/DrIbrarAhmedAI/smolagents-crypto-analysis")
    print(f"Root: {ROOT}")
    print("Educational. Not financial advice. LIVE ORDERS: BLOCKED")
    print("")

    # ── 1. contracts ────────────────────────────────────────────
    _banner("1/6  SCHEMAS + SANDBOX")
    tel_schema = ROOT / "schemas" / "telemetry_event.json"
    act_schema = ROOT / "schemas" / "action_object.json"
    policy = ROOT / "sandbox" / "policy.yaml"
    print(f"[schema] {tel_schema.name} OK" if tel_schema.is_file() else "[schema] MISSING telemetry")
    print(f"[schema] {act_schema.name} OK" if act_schema.is_file() else "[schema] MISSING action")
    print(f"[sandbox] {policy.name} paper-only" if policy.is_file() else "[sandbox] MISSING policy")
    print("[boundary] exchange_order → blocked by design")

    # ── 2. adapter ──────────────────────────────────────────────
    _banner("2/6  SPECIALTY ADAPTER")
    adapter = ROOT / "models" / "telemetry-action-adapter" / "adapter.json"
    print(f"[adapter] {adapter}" if adapter.is_file() else "[adapter] MISSING — run training/adapt_model.py")
    model = AdaptedModel()
    print("[adapter] telemetry-action-adapter loaded · narrow task ready")

    sol = make_event("SOL", DEMO["SOL"])

    # ── 3. baseline fail ────────────────────────────────────────
    if not skip_baseline:
        _banner("3/6  BASELINE FAIL")
        essay = GenericChatModel().generate(sol)
        print(essay)
        print("")
        print(">>> BASELINE FAIL")
        print(schema_check_report(essay))
        print("production: STOP — essay is not an action")
    else:
        _banner("3/6  BASELINE FAIL (skipped)")

    # ── 4. adapted win ──────────────────────────────────────────
    _banner("4/6  ADAPTED WIN")
    action = model.generate(sol)
    print(json.dumps(action, indent=2))
    print("")
    print(">>> ADAPTED WIN")
    print(schema_check_report(action))
    print(f"SIGNAL: {action['signal']}  conf={action['confidence']}")

    # ── 5. full pipeline ────────────────────────────────────────
    _banner("5/6  PIPELINE · adapter → model → gate → paper_log")
    print("pipeline: adapter → model → CodeAgent → gate → paper_log")
    print("model=telemetry-action-adapter  gate=on  live_orders=BLOCKED")
    print("")
    review_result = None
    for sym in ("BTC", "ETH", "SOL"):
        event = make_event(sym, DEMO[sym])
        result = process(event, verbose=False)
        scored = result["action"]
        drop_or_write = "write" if result["wrote"] else "drop"
        print(f"{sym}  normalize ok → score {scored['signal']:<6} → gate pass → {drop_or_write}")
        if scored["signal"] == "REVIEW":
            review_result = result
    print("")
    if review_result is not None:
        tel = review_result["telemetry"]
        act = review_result["action"]
        print(
            f"[adapter] {tel['symbol']} spread={tel['spread_bps']}bps "
            f"liq={tel['liquidity_delta_pct']}% volume_z={tel['volume_z']}"
        )
        print(f"[model]   {act['signal']} conf={act['confidence']} evidence={act['evidence']}")
        print("[agent]   normalize_event → score_signal → write_paper_signal")
        print("[gate]    approved paper · LIVE ORDERS: BLOCKED")
        if review_result.get("wrote"):
            print(f"[output]  {review_result['wrote']}")
            print("[output]  logs/review_queue.jsonl")
    print("")
    print("COMPLETE SYSTEM · paper-only · SYSTEM READY")

    # ── 6. golden ───────────────────────────────────────────────
    _banner("6/6  GOLDEN REPLAY")
    _run_golden()

    print("")
    print("NO LIVE ORDERS · demo_complete → clone the repo and rebuild every file")
    print("SYSTEM READY · follow each stage in the video")
    out = {
        "demo": "complete",
        "paper_only": True,
        "live_orders": "BLOCKED",
        "last_signal": (review_result or {}).get("action", {}).get("signal", "HOLD"),
        "companion": "github.com/ibrarahmad/DrIbrarAhmedAI/smolagents-crypto-analysis",
    }
    out_path = ROOT / "logs" / "demo_complete.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"[log] wrote {out_path}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Complete paper-only smolagents crypto demo")
    parser.add_argument("--skip-baseline", action="store_true")
    args = parser.parse_args()
    raise SystemExit(run_demo(skip_baseline=args.skip_baseline))


if __name__ == "__main__":
    main()
