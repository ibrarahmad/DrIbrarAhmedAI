"""Adapted win: structured action passes schema check."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.adapted_model import AdaptedModel
from schemas.validate import schema_check_report

ROWS = {
    "sol_anomaly_31bps": ROOT / "logs" / "fixtures" / "sol_anomaly.json",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--row", default="sol_anomaly_31bps")
    args = parser.parse_args()
    event = json.loads(ROWS[args.row].read_text(encoding="utf-8"))
    action = AdaptedModel().generate(event)
    print(json.dumps(action, indent=2))
    print()
    print(">>> ADAPTED WIN")
    print(schema_check_report(action))
    print(f"SIGNAL: {action['signal']}  conf={action['confidence']}")
    print("narrow task + stable schema + strict output")
    print("=> component behavior · tools can consume this")
    out = ROOT / "eval" / "adapted_model.out"
    out.write_text(json.dumps(action, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
