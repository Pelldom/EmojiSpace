"""
Aevum-complete engine telemetry for playtest debugging.
JSON Lines format: one JSON object per line. Logging does not affect game logic.

Stage 1: log_debug_event + telemetry file (logs/).
Stage 2: log_event + debug file (tests/output/) with full payload and context.
"""
from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from typing import Any

_telemetry_file = None
_debug_file = None
_current_turn: int | None = None
_current_system_id: str | None = None


def start_telemetry(file_path: str) -> None:
    """Open the telemetry log file for appending. Idempotent; re-calling closes and reopens."""
    global _telemetry_file
    stop_telemetry()
    _telemetry_file = open(file_path, "a", encoding="utf-8")


def stop_telemetry() -> None:
    """Close the telemetry log file if open."""
    global _telemetry_file
    if _telemetry_file is not None:
        try:
            _telemetry_file.close()
        except Exception:
            pass
        _telemetry_file = None


def log_debug_event(event_type: str, data: dict[str, Any]) -> None:
    """Write one telemetry event as a single JSON object line. No-op if telemetry not started."""
    if _telemetry_file is None:
        return
    try:
        payload = {"event": event_type, **data}
        line = json.dumps(payload, default=str, ensure_ascii=False) + "\n"
        _telemetry_file.write(line)
        _telemetry_file.flush()
    except Exception:
        pass  # Logging must not affect game logic


# ---- Stage 2: engine-wide debug telemetry ----


def start_debug_telemetry(file_path: str) -> None:
    """Open the debug telemetry file for appending. Idempotent; re-calling closes and reopens."""
    global _debug_file
    stop_debug_telemetry()
    _debug_file = open(file_path, "a", encoding="utf-8")


def stop_debug_telemetry() -> None:
    """Close the debug telemetry file if open."""
    global _debug_file
    if _debug_file is not None:
        try:
            _debug_file.close()
        except Exception:
            pass
        _debug_file = None


def set_telemetry_context(turn: int | None = None, system_id: str | None = None) -> None:
    """Set current turn and system_id for log_event context. Safe to call from engine."""
    global _current_turn, _current_system_id
    if turn is not None:
        _current_turn = int(turn)
    if system_id is not None:
        _current_system_id = str(system_id)


def log_event(event_type: str, payload: dict[str, Any], component: str) -> None:
    """
    Write a full-payload telemetry event to the debug file.
    Adds timestamp, turn, system_id, component, event_type; payload is deep-copied.
    No-op if debug telemetry not started. Does not affect game logic.
    """
    if _debug_file is None:
        return
    try:
        payload_copy = copy.deepcopy(payload)
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        event = {
            "event_type": event_type,
            "timestamp": timestamp,
            "turn": _current_turn,
            "system_id": _current_system_id if _current_system_id is not None else "",
            "component": component,
            "payload": payload_copy,
        }
        line = json.dumps(event, default=str, ensure_ascii=False) + "\n"
        _debug_file.write(line)
        _debug_file.flush()
    except Exception:
        pass  # Logging must not affect game logic
