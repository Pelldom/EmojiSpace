"""
Aevum-complete engine telemetry for playtest debugging.
JSON Lines format: one JSON object per line. Logging does not affect game logic.
"""
from __future__ import annotations

import json
from typing import Any

_telemetry_file = None


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
