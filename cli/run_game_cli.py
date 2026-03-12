#!/usr/bin/env python3
"""
Player-facing CLI for EmojiSpace.
Usage: python cli/run_game_cli.py [--seed N] [--admin]
Logs go to logs/gameplay_seed_XXXXX.log; logs are not printed to screen.
For emoji display on Windows, set PYTHONIOENCODING=utf-8 or use a UTF-8 console.
"""

from __future__ import annotations

import argparse
import contextlib
import sys
from pathlib import Path

# Ensure src is on path before any engine/emoji imports
_root = Path(__file__).resolve().parent.parent
_src = _root / "src"
if _src.exists() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

# CLI package: add cli dir so imports like "from cli_renderer import ..." work when running as script
_cli_dir = Path(__file__).resolve().parent
if str(_cli_dir) not in sys.path:
    sys.path.insert(0, str(_cli_dir))

from game_engine import GameEngine
from logger import Logger, LogEntry

_suppress_console = False


@contextlib.contextmanager
def _suppress_logger_console():
    """Do not print log lines to screen; preserve file logging."""
    global _suppress_console
    old = _suppress_console
    _suppress_console = True
    try:
        _original_log = Logger.log
        def _patched_log(self, turn: int, action: str, state_change: str) -> None:
            entry = LogEntry(turn=turn, version=self._version, action=action, state_change=state_change)
            line = entry.format_line()
            if not _suppress_console:
                print(line)
            path = getattr(self, "_file_path", None)
            if getattr(self, "_file_enabled", False) and isinstance(path, str):
                try:
                    with open(path, "a", encoding="ascii", errors="replace") as f:
                        f.write(line + "\n")
                except Exception:
                    pass
        Logger.log = _patched_log
        yield
    finally:
        Logger.log = _original_log
        _suppress_console = old


def _prompt_seed() -> int:
    while True:
        raw = input("World seed (integer): ").strip()
        try:
            return int(raw)
        except ValueError:
            print("Please enter a valid integer.")


def main() -> None:
    parser = argparse.ArgumentParser(description="EmojiSpace player CLI")
    parser.add_argument("--seed", type=int, default=None, help="World seed (default: prompt)")
    parser.add_argument("--admin", action="store_true", help="Launch admin menu instead of player menu")
    args = parser.parse_args()

    seed = args.seed if args.seed is not None else _prompt_seed()

    # Preserve existing engine logging: file only, no console (patch before creating engine)
    log_path = str(_root / "logs" / f"gameplay_seed_{seed}.log")
    log_dir = _root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    with _suppress_logger_console():
        engine = GameEngine(world_seed=seed, config={"system_count": 5})
        engine.execute({"type": "set_logging", "enabled": True, "log_path": log_path, "truncate": True})
        if args.admin:
            from cli_admin import run_admin_loop
            print("EmojiSpace Admin")
            run_admin_loop(engine)
            return
        from cli_menus import run_main_loop
        print()
        print("EmojiSpace")
        run_main_loop(engine)


if __name__ == "__main__":
    # Emoji display: use UTF-8 stdout when possible (e.g. Windows console)
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    main()
