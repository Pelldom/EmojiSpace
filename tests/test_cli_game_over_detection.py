"""Tests for CLI game over detection helpers."""

import pytest

# Import the helper functions from the CLI module
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from run_game_engine_cli import _is_game_over_result


def test_is_game_over_result_with_error_game_over():
    """Test detection of game over with error='game_over'."""
    result = {"error": "game_over", "game_over_reason": "ship_destroyed"}
    assert _is_game_over_result(result) is True


def test_is_game_over_result_with_game_over_reason():
    """Test detection of game over with game_over_reason field."""
    result = {"ok": False, "game_over_reason": "ship_destroyed"}
    assert _is_game_over_result(result) is True


def test_is_game_over_result_with_detail_reason():
    """Test detection of game over with detail.reason."""
    result = {"ok": False, "detail": {"reason": "ship_destroyed"}}
    assert _is_game_over_result(result) is True


def test_is_game_over_result_with_detail_reason_tier2_arrest():
    """Test detection of game over with detail.reason='tier2_arrest'."""
    result = {"ok": False, "detail": {"reason": "tier2_arrest"}}
    assert _is_game_over_result(result) is True


def test_is_game_over_result_not_game_over():
    """Test that normal results are not detected as game over."""
    result = {"ok": True}
    assert _is_game_over_result(result) is False


def test_is_game_over_result_with_error_not_game_over():
    """Test that other errors are not detected as game over."""
    result = {"ok": False, "error": "invalid_command"}
    assert _is_game_over_result(result) is False


def test_is_game_over_result_invalid_input():
    """Test that non-dict inputs return False."""
    assert _is_game_over_result(None) is False
    assert _is_game_over_result("string") is False
    assert _is_game_over_result([]) is False
