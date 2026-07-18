"""Local adapted model: telemetry in → action_object out.

This is an intentional narrow specialty piece (rules + thresholds), not a
frontier chat model. Training scripts write the thresholds JSON consumed here.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ADAPTER = ROOT / "models" / "telemetry-action-adapter" / "adapter.json"


class AdaptedModel:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or DEFAULT_ADAPTER
        self.cfg = json.loads(self.path.read_text(encoding="utf-8"))

    def generate(self, event: dict[str, Any]) -> dict[str, Any]:
        spread = float(event.get("spread_bps", 0))
        liq = float(event.get("liquidity_delta_pct", 0))
        vol = float(event.get("volume_z", 0))
        review_spread = float(self.cfg.get("review_spread_bps", 25))
        review_liq = float(self.cfg.get("review_liquidity_delta_pct", -12))
        hold_volume_confirm = float(self.cfg.get("hold_volume_z", 2.0))

        evidence: list[str] = []
        # Anomaly: wide spread + liquidity drop without volume confirmation
        if spread >= review_spread:
            evidence.append("spread_bps")
        if liq <= review_liq:
            evidence.append("liquidity_delta_pct")
        if vol < hold_volume_confirm and ("spread_bps" in evidence or "liquidity_delta_pct" in evidence):
            evidence.append("volume_z")

        if len(evidence) >= 2 and "volume_z" in evidence:
            return {
                "signal": "REVIEW",
                "confidence": round(min(0.95, 0.75 + (spread - review_spread) * 0.01), 2),
                "reason": "spread widened without volume confirmation",
                "evidence": evidence,
                "allowed_tool": "write_paper_signal",
            }
        return {
            "signal": "HOLD",
            "confidence": 0.88,
            "reason": "spread/liquidity/volume agree — no anomaly",
            "evidence": ["spread_bps", "volume_z"],
            "allowed_tool": "none",
        }


class GenericChatModel:
    """Baseline: sounds smart, fails the action schema."""

    def generate(self, event: dict[str, Any]) -> str:
        return (
            "This could indicate a potential arbitrage opportunity, "
            "but crypto markets are volatile. You may want to "
            "monitor the order book, compare venues, and consider "
            "risk management before making a trade decision."
        )
