"""Baseline failure: generic chat essay fails schema check."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.adapted_model import GenericChatModel
from schemas.validate import schema_check_report

ROWS = {
    "sol_anomaly_31bps": ROOT / "logs" / "fixtures" / "sol_anomaly.json",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--row", default="sol_anomaly_31bps")
    args = parser.parse_args()
    path = ROWS[args.row]
    event = json.loads(path.read_text(encoding="utf-8"))
    print(
        f"SOL row: spread_bps={event['spread_bps']} "
        f"liquidity_delta_pct={event['liquidity_delta_pct']} volume_z={event['volume_z']}"
    )
    print()
    text = GenericChatModel().generate(event)
    for line in text.split(". "):
        line = line.strip()
        if not line:
            continue
        if not line.endswith("."):
            line += "."
        print(line)
    print()
    print(">>> BASELINE FAIL")
    print(schema_check_report(text))
    print("production: STOP — essay is not an action")


if __name__ == "__main__":
    main()
