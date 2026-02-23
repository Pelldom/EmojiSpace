"""Tests for destination context block functionality."""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from game_engine import GameEngine  # noqa: E402


def test_destination_context_visited_system() -> None:
    """Test that destination context includes government and economy for visited systems."""
    engine = GameEngine(world_seed=12345)
    
    # Ensure system is visited (should be by default at start)
    current_system_id = engine.player_state.current_system_id
    assert current_system_id in engine.player_state.visited_system_ids
    
    context = engine.get_current_destination_context()
    
    # Always present fields
    assert "destination_name" in context
    assert "destination_type" in context
    assert "system_name" in context
    assert "system_id" in context
    assert isinstance(context["destination_name"], str)
    assert isinstance(context["destination_type"], str)
    assert isinstance(context["system_name"], str)
    
    # Should have government and economy for visited system
    assert "system_government" in context
    assert context["system_government"] != "", "Government should be present for visited system"
    
    assert "primary_economy" in context
    # primary_economy may be None if destination has no economy, but field should exist
    assert context["primary_economy"] is None or isinstance(context["primary_economy"], str)
    
    assert "secondary_economies" in context
    assert isinstance(context["secondary_economies"], list)
    
    assert "active_situations" in context
    assert isinstance(context["active_situations"], list)


def test_destination_context_unvisited_system() -> None:
    """Test that destination context excludes economy and situations for unvisited systems."""
    engine = GameEngine(world_seed=12345)
    
    # Clear visited systems to simulate unvisited state
    engine.player_state.visited_system_ids.clear()
    engine.player_state.visited_destination_ids.clear()
    
    context = engine.get_current_destination_context()
    
    # Always present fields
    assert "destination_name" in context
    assert "destination_type" in context
    assert "system_name" in context
    assert "system_id" in context
    
    # Should NOT have sensitive data for unvisited system
    assert "system_government" in context
    assert context["system_government"] == "", "Government should be empty for unvisited system"
    
    assert "primary_economy" in context
    assert context["primary_economy"] is None, "Primary economy should be None for unvisited system"
    
    assert "secondary_economies" in context
    assert context["secondary_economies"] == [], "Secondary economies should be empty for unvisited system"
    
    assert "active_situations" in context
    assert context["active_situations"] == [], "Active situations should be empty for unvisited system"


def test_destination_context_deterministic() -> None:
    """Test that destination context is deterministic for same seed and state."""
    engine1 = GameEngine(world_seed=12345)
    context1 = engine1.get_current_destination_context()
    
    engine2 = GameEngine(world_seed=12345)
    context2 = engine2.get_current_destination_context()
    
    # Should match for same seed
    assert context1["destination_name"] == context2["destination_name"]
    assert context1["destination_type"] == context2["destination_type"]
    assert context1["system_name"] == context2["system_name"]
    assert context1["system_id"] == context2["system_id"]
    
    # If both visited, should match sensitive data
    if (context1["system_government"] and context2["system_government"]):
        assert context1["system_government"] == context2["system_government"]
        assert context1["primary_economy"] == context2["primary_economy"]
        assert context1["secondary_economies"] == context2["secondary_economies"]


def test_destination_context_no_destination() -> None:
    """Test that destination context handles missing destination gracefully."""
    engine = GameEngine(world_seed=12345)
    
    # Clear destination
    engine.player_state.current_destination_id = None
    
    context = engine.get_current_destination_context()
    
    # Should return valid structure even without destination
    assert "destination_name" in context
    assert "destination_type" in context
    assert context["destination_name"] == "Unknown" or isinstance(context["destination_name"], str)
    assert context["destination_type"] == "unknown" or isinstance(context["destination_type"], str)
