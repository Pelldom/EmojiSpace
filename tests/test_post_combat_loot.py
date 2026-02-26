"""
Test post-combat loot handling.
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from game_engine import GameEngine, EngineContext
from encounter_generator import generate_encounter
from time_engine import get_current_turn
from combat_resolver import CombatResult


def test_post_combat_loot_creates_pending_state():
    """Test that combat win with rewards creates pending loot state."""
    engine = GameEngine(world_seed=12345, config={"system_count": 5})
    
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    if current_system is None:
        pytest.skip("No current system available")
    
    # Generate an encounter with reward profile
    spec = generate_encounter(
        encounter_id="LOOT-TEST-001",
        world_seed="12345",
        system_government_id=current_system.government_id,
        active_situations=[],
    )
    
    # Ensure encounter has reward profile (mock if needed)
    if not hasattr(spec, "reward_profile_id") or not spec.reward_profile_id:
        # Skip if no reward profile
        pytest.skip("Encounter has no reward profile")
    
    # Initialize combat
    from game_engine import EngineContext
    context = EngineContext(
        command={"type": "test"},
        command_type="test",
        turn_before=int(get_current_turn()),
        turn_after=int(get_current_turn()),
    )
    
    # Resolve encounter with attack (triggers combat)
    engine._resolve_encounter(
        context=context,
        spec=spec,
        player_action="attack",
        player_kwargs={},
    )
    
    # Check if combat was initiated
    if not engine.has_pending_combat():
        pytest.skip("Combat was not initiated")
    
    # Simulate combat win by manually calling post-combat handler
    # (In real flow, this happens after combat ends)
    from combat_resolver import CombatResult
    combat_result = CombatResult(
        outcome="destroyed",
        rounds=1,
        winner="player",
        final_state_player={},
        final_state_enemy={},
        log=[],
        tr_player=10,
        tr_enemy=5,
        rcp_player=10,
        rcp_enemy=5,
        salvage_modules=[],
        combat_rng_seed=12345,
    )
    
    # Call post-combat handler
    engine._apply_post_combat_rewards_and_salvage(
        context=context,
        combat_result=combat_result,
        encounter_id=str(spec.encounter_id),
    )
    
    # Verify pending loot was created
    pending_loot = engine.get_pending_loot()
    assert pending_loot is not None, "Pending loot should be created after combat win"
    assert pending_loot.get("encounter_id") == str(spec.encounter_id)
    
    # Verify hard_stop was set
    assert context.hard_stop is True
    assert context.hard_stop_reason == "pending_loot_decision"


def test_resolve_pending_loot_take_all():
    """Test that resolve_pending_loot(True) applies credits."""
    engine = GameEngine(world_seed=12345, config={"system_count": 5})
    
    # Set up pending loot manually
    initial_credits = engine.player_state.credits
    engine._pending_loot = {
        "encounter_id": "TEST-001",
        "reward_payload": None,
        "salvage_modules": [],
        "credits": 100,
        "cargo_sku": None,
        "cargo_quantity": 0,
        "stolen_applied": False,
    }
    
    # Resolve with take_all=True
    result = engine.resolve_pending_loot(take_all=True)
    
    assert result.get("ok") is True
    assert engine.player_state.credits == initial_credits + 100
    assert engine.get_pending_loot() is None  # Should be cleared


def test_resolve_pending_loot_leave_all():
    """Test that resolve_pending_loot(False) does not apply credits."""
    engine = GameEngine(world_seed=12345, config={"system_count": 5})
    
    # Set up pending loot manually
    initial_credits = engine.player_state.credits
    engine._pending_loot = {
        "encounter_id": "TEST-001",
        "reward_payload": None,
        "salvage_modules": [],
        "credits": 100,
        "cargo_sku": None,
        "cargo_quantity": 0,
        "stolen_applied": False,
    }
    
    # Resolve with take_all=False
    result = engine.resolve_pending_loot(take_all=False)
    
    assert result.get("ok") is True
    assert engine.player_state.credits == initial_credits  # Credits unchanged
    assert engine.get_pending_loot() is None  # Should be cleared


def test_resolve_pending_loot_no_pending():
    """Test that resolve_pending_loot returns error when no pending loot."""
    engine = GameEngine(world_seed=12345, config={"system_count": 5})
    
    # Ensure no pending loot
    engine._pending_loot = None
    
    # Try to resolve
    result = engine.resolve_pending_loot(take_all=True)
    
    assert result.get("ok") is False
    assert result.get("error") == "no_pending_loot"


def test_resolve_pending_loot_resumes_encounters():
    """Test that resolve_pending_loot resumes encounter queue if encounters remain."""
    engine = GameEngine(world_seed=12345, config={"system_count": 5})
    
    # Create a mock encounter for remaining_encounters
    from encounter_generator import generate_encounter
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    if current_system is None:
        pytest.skip("No current system available")
    
    encounter1 = generate_encounter(
        encounter_id="TEST-ENC-001",
        world_seed="12345",
        system_government_id=current_system.government_id,
        active_situations=[],
    )
    encounter2 = generate_encounter(
        encounter_id="TEST-ENC-002",
        world_seed="12345",
        system_government_id=current_system.government_id,
        active_situations=[],
    )
    
    # Set up pending_travel with remaining encounters
    engine._pending_travel = {
        "travel_id": "TEST-TRAVEL",
        "payload": {},
        "remaining_encounters": [encounter2],
        "current_encounter": None,  # No current encounter (loot was just resolved)
        "encounter_context": {},
        "events_so_far": [],
    }
    
    # Set up pending loot
    engine._pending_loot = {
        "encounter_id": "TEST-ENC-001",
        "reward_payload": None,
        "salvage_modules": [],
        "credits": 100,
        "cargo_sku": None,
        "cargo_quantity": 0,
        "stolen_applied": False,
    }
    
    # Resolve loot
    result = engine.resolve_pending_loot(take_all=True)
    
    assert result.get("ok") is True
    assert result.get("resume_encounters") is True
    
    # Verify next encounter is set up
    assert engine.has_pending_encounter() is True
    assert engine._pending_travel.get("current_encounter") is not None
    assert str(engine._pending_travel.get("current_encounter").encounter_id) == "TEST-ENC-002"
    assert len(engine._pending_travel.get("remaining_encounters", [])) == 0
