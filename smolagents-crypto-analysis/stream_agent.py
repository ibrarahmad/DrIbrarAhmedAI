#!/usr/bin/env python3
"""Producer loop against a tiny demo stream."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters.subgraph_adapter import normalize_subgraph
from pipeline.run import DEMO, make_event, process


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter", default="subgraph")
    parser.add_argument("--paper", action="store_true", default=True)
    args = parser.parse_args()
    _ = args.paper

    rows = [
        ("BTC", DEMO["BTC"]),
        ("ETH", DEMO["ETH"]),
        ("SOL", DEMO["SOL"]),
    ]
    for i, (sym, feats) in enumerate(rows, start=1):
        if args.adapter == "subgraph" and sym == "SOL":
            event = normalize_subgraph(
                {
                    "pair": "SOL/USDC",
                    "price": feats["price"],
                    "spread_bps": feats["spread_bps"],
                    "liquidity_delta": feats["liquidity_delta_pct"],
                    "volume_z": feats["volume_z"],
                }
            )
        else:
            event = make_event(sym, feats)
        result = process(event)
        action = result["action"]
        if action["signal"] == "HOLD":
            note = "normal spread" if sym == "BTC" else "volume confirms move"
            print(f"[{i:02d}] {sym} HOLD   {note}")
        else:
            print(f"[{i:02d}] {sym} REVIEW spread={event['spread_bps']}bps liquidity={event['liquidity_delta_pct']}%")
            print(f'     evidence={json_dumps(action["evidence"])}')
            print("     wrote logs/paper_signals.jsonl")
            print("     queued logs/review_queue.jsonl")


def json_dumps(obj) -> str:
    import json

    return json.dumps(obj)


if __name__ == "__main__":
    main()
