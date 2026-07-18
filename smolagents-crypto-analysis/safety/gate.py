"""Safety gate — model proposes, gate decides."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schemas.validate import validate_action

ALLOWLIST = {"write_paper_signal", "append_review_queue", "none"}


def missing_fields(proposal: dict[str, Any]) -> bool:
    ok, _ = validate_action(proposal)
    return not ok


def decide(proposal: dict[str, Any]) -> dict[str, Any]:
    if proposal.get("confidence", 0) < 0.70:
        return {"signal": "HOLD", "reason": "low confidence", "live_orders": "BLOCKED"}
    if missing_fields(proposal):
        return {"signal": "HOLD", "reason": "incomplete action", "live_orders": "BLOCKED"}
    if proposal.get("allowed_tool") not in ALLOWLIST:
        return {"signal": "HOLD", "reason": "blocked tool", "live_orders": "BLOCKED"}
    if proposal.get("live_order"):
        return {"signal": "HOLD", "reason": "LIVE ORDERS: BLOCKED", "live_orders": "BLOCKED"}
    out = dict(proposal)
    out["live_orders"] = "BLOCKED"
    out["human_review_default"] = True
    return out  # paper path only


def main() -> None:
    parser = argparse.ArgumentParser(description="Run safety gate on a proposal JSON")
    parser.add_argument("--proposal", required=True, help="Path to action JSON")
    args = parser.parse_args()
    proposal = json.loads(Path(args.proposal).read_text(encoding="utf-8"))
    print("model_output = proposal")
    print("gate_output  = decision")
    print("log_output   = evidence trail")
    print()
    decision = decide(proposal)
    conf = float(proposal.get("confidence", 0))
    print(f"confidence {conf:.2f} >= 0.70 -> {'continue' if conf >= 0.70 else 'HOLD'}")
    print("fields complete -> continue" if not missing_fields(proposal) else "fields incomplete -> HOLD")
    tool = proposal.get("allowed_tool")
    print(f"tool {tool} in allowlist -> {'continue' if tool in ALLOWLIST else 'BLOCK'}")
    if proposal.get("live_order"):
        print("live_order requested -> BLOCK")
    else:
        print("live_order requested -> BLOCK")  # always blocked by design in demo messaging
    print()
    print(f"decision: {decision.get('signal')} (paper) · human_review_default=true")
    print("LIVE ORDERS: BLOCKED")


if __name__ == "__main__":
    main()
