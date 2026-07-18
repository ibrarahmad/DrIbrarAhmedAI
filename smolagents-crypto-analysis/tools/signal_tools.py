"""Three allowed tools — paper path only."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.adapted_model import AdaptedModel
from models.paper_log import append_review_queue, write_paper_signal as _write_paper
from schemas.validate import validate_action, validate_telemetry

_adapted = AdaptedModel()


def normalize_event(raw: dict) -> dict:
    """Map raw feed into the telemetry_event schema.

    Args:
        raw: Raw market/subgraph event dictionary.
    """
    return validate_telemetry(raw)


def score_signal(event: dict) -> dict:
    """Ask the adapted model for a strict action_object.

    Args:
        event: Validated telemetry_event dictionary.
    """
    action = _adapted.generate(event)
    ok, errors = validate_action(action)
    if not ok:
        raise ValueError("adapted model produced invalid action: " + "; ".join(errors))
    return action


def write_paper_signal(action: dict) -> str:
    """Append a paper signal JSONL row. Never places orders.

    Args:
        action: Action object from the adapted model / gate.
    """
    symbol = None
    if isinstance(action, dict):
        symbol = action.get("symbol")
    path = _write_paper(action, symbol=symbol)
    if action.get("signal") in {"REVIEW", "ALERT"}:
        append_review_queue(action, symbol=symbol)
    return path


def exchange_order(*_args: Any, **_kwargs: Any) -> None:
    """Intentionally missing from the allowlist."""
    raise AttributeError("exchange_order tool missing on purpose — LIVE ORDERS: BLOCKED")


def as_smolagents_tools():
    """Wrap the three paper tools for CodeAgent (optional)."""
    from smolagents import tool

    return [
        tool(normalize_event),
        tool(score_signal),
        tool(write_paper_signal),
    ]
