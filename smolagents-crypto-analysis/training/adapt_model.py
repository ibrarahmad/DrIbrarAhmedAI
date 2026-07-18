"""Fit narrow thresholds from train.jsonl and save the specialty adapter."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fit(train_path: Path) -> dict:
    review_spreads: list[float] = []
    review_liqs: list[float] = []
    for line in train_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        out = row["output"]
        inp = row["input"]
        if out.get("signal") == "REVIEW":
            review_spreads.append(float(inp["spread_bps"]))
            review_liqs.append(float(inp["liquidity_delta_pct"]))
    if not review_spreads:
        raise SystemExit("no REVIEW rows in training data")
    # Conservative: slightly below the median anomaly spread / above the median liq drop
    review_spreads.sort()
    review_liqs.sort()
    mid_s = review_spreads[len(review_spreads) // 2]
    mid_l = review_liqs[len(review_liqs) // 2]
    return {
        "name": "telemetry-action-adapter",
        "version": "1.0.0",
        "review_spread_bps": round(max(20.0, mid_s - 5.0), 2),
        "review_liquidity_delta_pct": round(min(-10.0, mid_l + 5.0), 2),
        "hold_volume_z": 2.0,
        "trained_on": str(train_path),
        "review_rows": len(review_spreads),
        "note": "Narrow specialty adapter — paper-only. Educational. Not financial advice.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, default=ROOT / "data" / "train.jsonl")
    parser.add_argument("--out", type=Path, default=ROOT / "models" / "telemetry-action-adapter")
    args = parser.parse_args()
    if not args.train.exists():
        raise SystemExit(f"missing {args.train} — run training/build_dataset.py first")
    cfg = fit(args.train)
    args.out.mkdir(parents=True, exist_ok=True)
    out_file = args.out / "adapter.json"
    out_file.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    print(f"saved: {args.out}")


if __name__ == "__main__":
    main()
