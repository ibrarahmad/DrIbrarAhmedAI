"""Build readable train.jsonl pairs from normal + anomaly seeds."""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def seed_rows() -> list[dict]:
    normal = [
        {"spread_bps": 4, "liquidity_delta_pct": 1.0, "volume_z": 0.7, "label": "HOLD"},
        {"spread_bps": 6, "liquidity_delta_pct": -2.0, "volume_z": 0.9, "label": "HOLD"},
        {"spread_bps": 5, "liquidity_delta_pct": 0.3, "volume_z": 1.1, "label": "HOLD"},
        {"spread_bps": 24, "liquidity_delta_pct": -3.0, "volume_z": 3.1, "label": "HOLD"},
    ]
    anomaly = [
        {"spread_bps": 31, "liquidity_delta_pct": -18.4, "volume_z": 0.2, "label": "REVIEW"},
        {"spread_bps": 42, "liquidity_delta_pct": -22.0, "volume_z": 0.4, "label": "REVIEW"},
        {"spread_bps": 28, "liquidity_delta_pct": -40.0, "volume_z": 0.1, "label": "REVIEW"},
    ]
    (ROOT / "training" / "normal_flow.jsonl").write_text(
        "\n".join(json.dumps(r) for r in normal) + "\n", encoding="utf-8"
    )
    (ROOT / "training" / "anomaly_rows.jsonl").write_text(
        "\n".join(json.dumps(r) for r in anomaly) + "\n", encoding="utf-8"
    )
    return normal + anomaly


def expand(rows: list[dict], n: int, rng: random.Random) -> list[dict]:
    out: list[dict] = []
    while len(out) < n:
        base = dict(rng.choice(rows))
        label = base.pop("label")
        jitter = {
            "spread_bps": round(base["spread_bps"] + rng.uniform(-1.5, 1.5), 2),
            "liquidity_delta_pct": round(base["liquidity_delta_pct"] + rng.uniform(-1.0, 1.0), 2),
            "volume_z": round(base["volume_z"] + rng.uniform(-0.1, 0.1), 2),
        }
        action = {
            "signal": label,
            "confidence": 0.81 if label == "REVIEW" else 0.88,
            "reason": (
                "spread widened without volume confirmation"
                if label == "REVIEW"
                else "spread/liquidity/volume agree — no anomaly"
            ),
            "evidence": (
                ["spread_bps", "liquidity_delta_pct", "volume_z"]
                if label == "REVIEW"
                else ["spread_bps", "volume_z"]
            ),
            "allowed_tool": "write_paper_signal" if label == "REVIEW" else "none",
        }
        out.append({"input": jitter, "output": action})
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    seeds = seed_rows()
    pairs = expand(seeds, args.rows, random.Random(args.seed))
    out = ROOT / "data" / "train.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in pairs:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {out} ({len(pairs)} pairs)")


if __name__ == "__main__":
    main()
