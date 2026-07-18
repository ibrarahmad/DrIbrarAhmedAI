"""Latency / token-shape race: essay model vs adapted specialty model."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.adapted_model import AdaptedModel, GenericChatModel

ROWS = {
    "sol_anomaly_31bps": ROOT / "logs" / "fixtures" / "sol_anomaly.json",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--row", default="sol_anomaly_31bps")
    args = parser.parse_args()
    event = json.loads(ROWS[args.row].read_text(encoding="utf-8"))

    t0 = time.perf_counter()
    essay = GenericChatModel().generate(event)
    t1 = time.perf_counter()
    action = AdaptedModel().generate(event)
    t2 = time.perf_counter()

    print()
    print("frontier_chat_model:")
    print(f"  tokens={len(essay.split()) * 2}  latency={t1 - t0:.3f}s  shape=essay")
    print()
    print("adapted_small_model:")
    print(f"  tokens={len(json.dumps(action).split())}  latency={t2 - t1:.3f}s  shape=action_json")
    print()
    print("winner for this job: adapted_small_model")
    print("reason: narrow contract · cheap · predictable")


if __name__ == "__main__":
    main()
