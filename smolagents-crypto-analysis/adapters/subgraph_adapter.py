"""Normalize subgraph-style events into the telemetry contract."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schemas.validate import validate_telemetry


def normalize_subgraph(event: dict[str, Any]) -> dict[str, Any]:
    pair = str(event.get("pair") or event.get("symbol") or "SOL/USDC")
    if "/" in pair:
        base, quote = pair.split("/", 1)
        quote = quote.upper()
        if quote in {"USDC", "USD"}:
            symbol = f"{base.upper()}USDT"
        else:
            symbol = f"{base.upper()}{quote}"
    else:
        symbol = pair.upper()
    raw = {
        "ts": event.get("ts") or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "symbol": symbol,
        "price": float(event["price"]),
        "spread_bps": float(event.get("spread_bps", 0)),
        "liquidity_delta_pct": float(event.get("liquidity_delta", event.get("liquidity_delta_pct", 0))),
        "volume_z": float(event.get("volume_z", 0)),
        "source": "subgraph",
    }
    return validate_telemetry(raw)


DEMO_EVENT = {
    "pair": "SOL/USDC",
    "block": 22811402,
    "price": 187.65,
    "spread_bps": 31,
    "liquidity_delta": -18.4,
    "volume_z": 0.2,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--event", type=Path, default=None)
    args = parser.parse_args()
    event = json.loads(args.event.read_text()) if args.event else DEMO_EVENT
    print("subgraph event:")
    print(f"  pool={event.get('pair')} block={event.get('block')}")
    print(
        f"  price={event.get('price')} liquidity_delta={event.get('liquidity_delta', event.get('liquidity_delta_pct'))} "
        f"volume_z={event.get('volume_z')}"
    )
    print()
    tel = normalize_subgraph(event)
    print("telemetry event:")
    print(f"  symbol={tel['symbol']} price={tel['price']} spread_bps={tel['spread_bps']}")
    print(
        f"  liquidity_delta_pct={tel['liquidity_delta_pct']} volume_z={tel['volume_z']} source={tel['source']}"
    )
    print()
    print("schema: same as telemetry_event.json")


if __name__ == "__main__":
    main()
