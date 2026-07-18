"""Validate telemetry + action objects against the JSON contracts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TELEMETRY_SCHEMA = json.loads((ROOT / "schemas" / "telemetry_event.json").read_text())
ACTION_SCHEMA = json.loads((ROOT / "schemas" / "action_object.json").read_text())

TELEMETRY_REQUIRED = set(TELEMETRY_SCHEMA["required"])
ACTION_REQUIRED = set(ACTION_SCHEMA["required"])
SIGNAL_ENUM = set(ACTION_SCHEMA["properties"]["signal"]["enum"])
TOOL_ENUM = set(ACTION_SCHEMA["properties"]["allowed_tool"]["enum"])


def validate_telemetry(raw: dict[str, Any]) -> dict[str, Any]:
    missing = TELEMETRY_REQUIRED - set(raw)
    if missing:
        raise ValueError(f"telemetry missing fields: {sorted(missing)}")
    out = {k: raw[k] for k in TELEMETRY_REQUIRED}
    out["symbol"] = str(out["symbol"]).upper().replace("/", "")
    if not out["symbol"].endswith("T") and len(out["symbol"]) <= 6:
        # keep as-is for SOLUSDT-style symbols
        pass
    return out


def validate_action(raw: dict[str, Any]) -> tuple[bool, list[str]]:
    missing = sorted(ACTION_REQUIRED - set(raw))
    errors: list[str] = []
    if missing:
        errors.append("missing: " + ", ".join(missing))
    signal = raw.get("signal")
    if signal is not None and signal not in SIGNAL_ENUM:
        errors.append(f"bad signal: {signal}")
    conf = raw.get("confidence")
    if conf is not None and not isinstance(conf, (int, float)):
        errors.append("confidence must be number")
    elif isinstance(conf, (int, float)) and not (0.0 <= float(conf) <= 1.0):
        errors.append("confidence out of range")
    evidence = raw.get("evidence")
    if evidence is not None and not isinstance(evidence, list):
        errors.append("evidence must be array")
    tool = raw.get("allowed_tool")
    if tool is not None and tool not in TOOL_ENUM:
        errors.append(f"bad allowed_tool: {tool}")
    return (len(errors) == 0, errors)


def schema_check_report(raw: Any) -> str:
    if not isinstance(raw, dict):
        return "SCHEMA CHECK: FAIL\nmissing: signal, evidence, allowed_tool"
    ok, errors = validate_action(raw)
    if ok:
        return "SCHEMA CHECK: PASS"
    return "SCHEMA CHECK: FAIL\n" + "\n".join(errors)
