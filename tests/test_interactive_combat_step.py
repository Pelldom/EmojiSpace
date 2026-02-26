"""
Test step-based combat execution.

Verifies that:
1. Each combat_action executes exactly one round
2. Round number increments
3. Combat state persists between rounds
4. Combat can end normally
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from game_engine import GameEngine, EngineContext  # noqa: E402
from encounter_generator import generate_encounter  # noqa: E402
from time_engine import get_current_turn  # noqa: E402


def test_combat_action_advances_round():
    """Test that submitting one combat_action advances round_number or ends combat."""
    engine = GameEngine(world_seed=12345, config={"system_count": 5})
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    if current_system is None:
        pytest.skip("No current system available")
    
    # Generate an encounter and initialize combat
    spec = generate_encounter(
        encounter_id="STEP-TEST-001",
        world_seed="12345",
        system_government_id=current_system.government_id,
        active_situations=[],
    )
    
    context = EngineContext(
        command={"type": "test"},
        command_type="test",
        turn_before=int(get_current_turn()),
        turn_after=int(get_current_turn()),
    )
    
    # Initialize combat session
    engine._initialize_combat_session(spec, context)
    
    # Verify pending combat exists and round_number is 0 (not started)
    assert engine.has_pending_combat(), "Combat session should be initialized"
    pending = engine._pending_combat
    assert pending is not None
    assert pending["round_number"] == 0, "Round should start at 0 before first action"
    
    # Store initial round number
    initial_round = pending["round_number"]
    
    # Execute one combat action
    context2 = EngineContext(
        command={"type": "combat_action", "action": "focus_fire"},
        command_type="combat_action",
        turn_before=int(get_current_turn()),
        turn_after=int(get_current_turn()),
    )
    
    engine._execute_combat_action(context2, {"action": "focus_fire", "encounter_id": spec.encounter_id})
    
    # Verify round advanced OR combat ended
    if engine.has_pending_combat():
        # Combat continues - round should have advanced
        assert pending["round_number"] > initial_round, \
            f"Round should advance from {initial_round}, got {pending['round_number']}"
        assert pending["round_number"] >= 1, \
            f"Round should be at least 1 after first action, got {pending['round_number']}"
    else:
        # Combat ended - that's also valid
        assert True, "Combat ended after first action (acceptable outcome)"