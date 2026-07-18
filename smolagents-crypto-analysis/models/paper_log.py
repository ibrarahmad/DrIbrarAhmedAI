"""Paper ledger helpers — never touches an exchange."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "logs" / "paper_signals.jsonl"
QUEUE = ROOT / "logs" / "review_queue.jsonl"


def append_jsonl(path: Path, row: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return str(path)


def write_paper_signal(action: dict[str, Any], symbol: str | None = None) -> str:
    row = dict(action)
    if symbol:
        row["symbol"] = symbol
    row["live_orders"] = "BLOCKED"
    return append_jsonl(PAPER, row)


def append_review_queue(action: dict[str, Any], symbol: str | None = None) -> str:
    row = dict(action)
    if symbol:
        row["symbol"] = symbol
    row["status"] = "queued_for_human"
    return append_jsonl(QUEUE, row)
