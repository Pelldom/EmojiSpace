"""
Test interactive combat functionality.

Verifies that:
1. Choosing "attack" enters combat and calls the player action callback
2. Combat progresses round-by-round deterministically
3. No "combat_stub" remains in the dispatch path for attack
4. Combat initialization uses valid hulls with hull_max > 0
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from game_engine import GameEngine, EngineContext  # noqa: E402
from interaction_layer import HANDLER_COMBAT, dispatch_player_action  # noqa: E402
from encounter_generator import generate_encounter  # noqa: E402
from time_engine import get_current_turn  # noqa: E402


def test_attack_dispatches_to_combat_handler():
    """Test that attack action dispatches to 'combat' handler, not 'combat_stub'."""
    engine = GameEngine(world_seed=12345, config={"system_count": 5})
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    if current_system is None:
        pytest.skip("No current system available")
    
    spec = generate_encounter(
        encounter_id="TEST-001",
        world_seed="12345",
        system_government_id=current_system.government_id,
        active_situations=[],
    )
    result = dispatch_player_action(
        spec=spec,
        player_action="attack",
        world_seed="12345",
        ignore_count=0,
        reputation_band=0,
        notoriety_band=0,
    )
    assert result.next_handler == HANDLER_COMBAT, f"Expected {HANDLER_COMBAT}, got {result.next_handler}"


def test_combat_calls_player_action_callback():
    """Test that combat calls the player action callback at least once."""
    engine = GameEngine(world_seed=12345, config={"system_count": 5})
    
    # Track callback invocations
    callback_calls = []
    
    def mock_player_action_callback(round_number, player_hull_pct, enemy_hull_pct, allowed_actions):
        callback_calls.append({
            "round": round_number,
            "player_hull": player_hull_pct,
            "enemy_hull": enemy_hull_pct,
            "allowed_actions": allowed_actions,
        })
        # Return first available action
        return allowed_actions[0] if allowed_actions else "Focus Fire"
    
    # Generate an encounter and resolve it with attack
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    if current_system is None:
        pytest.skip("No current system available")
    
    spec = generate_encounter(
        encounter_id="COMBAT-TEST-001",
        world_seed="12345",
        system_government_id=current_system.government_id,
        active_situations=[],
    )
    
    # Resolve encounter with attack action and callback
    context = EngineContext(
        command={"type": "test"},
        command_type="test",
        turn_before=int(get_current_turn()),
        turn_after=int(get_current_turn()),
    )
    engine._resolve_encounter(
        context=context,
        spec=spec,
        player_action="attack",
        player_kwargs={"get_player_action": mock_player_action_callback},
    )
    
    # Verify callback was called at least once
    assert len(callback_calls) > 0, "Player action callback should be called at least once during combat"
    assert callback_calls[0]["round"] == 1, "First callback should be for round 1"
    assert "Focus Fire" in callback_calls[0]["allowed_actions"], "Focus Fire should be in allowed actions"


def test_combat_deterministic_with_same_choices():
    """Test that combat progresses deterministically with same seed and same player choices."""
    seed = 12345
    
    # First run
    engine1 = GameEngine(world_seed=seed, config={"system_count": 5})
    choices1 = []
    
    def callback1(round_number, player_hull_pct, enemy_hull_pct, allowed_actions):
        choice = "Focus Fire"  # Always choose Focus Fire
        choices1.append(choice)
        return choice
    
    current_system1 = engine1.sector.get_system(engine1.player_state.current_system_id)
    if current_system1 is None:
        pytest.skip("No current system available")
    
    spec1 = generate_encounter(
        encounter_id="DET-TEST-001",
        world_seed=str(seed),
        system_government_id=current_system1.government_id,
        active_situations=[],
    )
    
    context1 = EngineContext(
        command={"type": "test"},
        command_type="test",
        turn_before=int(get_current_turn()),
        turn_after=int(get_current_turn()),
    )
    engine1._resolve_encounter(
        context=context1,
        spec=spec1,
        player_action="attack",
        player_kwargs={"get_player_action": callback1},
    )
    
    # Second run with same seed and same choices
    engine2 = GameEngine(world_seed=seed, config={"system_count": 5})
    choices2 = []
    
    def callback2(round_number, player_hull_pct, enemy_hull_pct, allowed_actions):
        choice = "Focus Fire"  # Always choose Focus Fire (same as first run)
        choices2.append(choice)
        return choice
    
    current_system2 = engine2.sector.get_system(engine2.player_state.current_system_id)
    if current_system2 is None:
        pytest.skip("No current system available")
    
    spec2 = generate_encounter(
        encounter_id="DET-TEST-001",
        world_seed=str(seed),
        system_government_id=current_system2.government_id,
        active_situations=[],
    )
    
    context2 = EngineContext(
        command={"type": "test"},
        command_type="test",
        turn_before=int(get_current_turn()),
        turn_after=int(get_current_turn()),
    )
    engine2._resolve_encounter(
        context=context2,
        spec=spec2,
        player_action="attack",
        player_kwargs={"get_player_action": callback2},
    )
    
    # Verify same number of rounds and same choices
    assert len(choices1) == len(choices2), f"Same number of rounds expected: {len(choices1)} vs {len(choices2)}"
    assert choices1 == choices2, f"Same choices expected: {choices1} vs {choices2}"


def test_combat_initialization_returns_hard_stop():
    """Test that choosing Attack during an encounter initializes combat and returns hard_stop with pending_combat."""
    engine = GameEngine(world_seed=12345, config={"system_count": 5})
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    if current_system is None:
        pytest.skip("No current system available")
    
    spec = generate_encounter(
        encounter_id="HARD_STOP_TEST-001",
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
    
    # Resolve encounter with attack action
    engine._resolve_encounter(
        context=context,
        spec=spec,
        player_action="attack",
        player_kwargs={},
    )
    
    # Verify hard_stop is set
    assert context.hard_stop is True, "Combat should set hard_stop=True"
    assert context.hard_stop_reason == "pending_combat_action", f"Expected 'pending_combat_action', got '{context.hard_stop_reason}'"
    assert engine._pending_combat is not None, "Combat session should be initialized"
    assert engine._pending_combat["encounter_id"] == "HARD_STOP_TEST-001", "Combat session should have correct encounter_id"
    assert engine._pending_combat["round_number"] == 0, "Combat should start at round 0 (not yet started)"


def test_combat_action_processes_one_round():
    """Test that combat_action command processes exactly one round and updates state."""
    engine = GameEngine(world_seed=12345, config={"system_count": 5})
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    if current_system is None:
        pytest.skip("No current system available")
    
    spec = generate_encounter(
        encounter_id="ROUND_TEST-001",
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
    
    # Initialize combat
    engine._resolve_encounter(
        context=context,
        spec=spec,
        player_action="attack",
        player_kwargs={},
    )
    
    assert engine._pending_combat is not None, "Combat should be initialized"
    initial_round = engine._pending_combat["round_number"]
    
    # Process first round
    context2 = EngineContext(
        command={"type": "combat_action"},
        command_type="combat_action",
        turn_before=int(get_current_turn()),
        turn_after=int(get_current_turn()),
    )
    engine._execute_combat_action(context2, {"action": "focus_fire", "encounter_id": "ROUND_TEST-001"})
    
    # Verify round incremented or combat ended (including game over)
    # Combat can continue, end normally, or end with game over
    combat_continues = engine._pending_combat is not None
    combat_ended_normally = context2.hard_stop is False
    combat_ended_game_over = context2.hard_stop is True and context2.hard_stop_reason == "game_over"
    assert combat_continues or combat_ended_normally or combat_ended_game_over, "Combat should either continue, end normally, or end with game over"
    if engine._pending_combat is not None:
        assert engine._pending_combat["round_number"] > initial_round, "Round number should increment"
        assert context2.hard_stop is True, "Combat should continue with hard_stop"
        assert context2.hard_stop_reason == "pending_combat_action", "Should request next combat action"


def test_combat_actions_use_contract_labels():
    """Test that pending_combat.allowed_actions uses exact contract labels from combat_resolution_contract.md Section 3."""
    engine = GameEngine(world_seed=12345, config={"system_count": 5})
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    if current_system is None:
        pytest.skip("No current system available")
    
    spec = generate_encounter(
        encounter_id="LABEL_TEST-001",
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
    
    # Initialize combat
    engine._resolve_encounter(
        context=context,
        spec=spec,
        player_action="attack",
        player_kwargs={},
    )
    
    # Build step result to get pending_combat payload
    result = engine._build_step_result(context=context, ok=True, error=None)
    pending_combat = result.get("pending_combat")
    
    assert pending_combat is not None, "Should have pending_combat payload"
    allowed_actions = pending_combat.get("allowed_actions", [])
    assert len(allowed_actions) > 0, "Should have at least one allowed action"
    
    # Extract labels
    labels = [opt.get("label", "") for opt in allowed_actions]
    
    # Verify core actions use exact contract labels
    # Per combat_resolution_contract.md Section 3: "CORE ACTIONS"
    # Always available: Focus Fire, Reinforce Shields, Evasive Maneuvers, Attempt Escape, Surrender
    expected_core_actions = {
        "Focus Fire",
        "Reinforce Shields",
        "Evasive Maneuvers",
        "Attempt Escape",
        "Surrender",
    }
    
    # All core actions must be present with exact labels
    for expected in expected_core_actions:
        assert expected in labels, f"Core action '{expected}' must be present with exact contract label"
    
    # Verify no incorrect labels like "Focus Weapons" or "Focus Defenses"
    incorrect_labels = ["Focus Weapons", "Focus Defenses", "Focus Engines", "focus weapons", "focus defenses", "focus engines"]
    for label in labels:
        assert label not in incorrect_labels, f"Found incorrect label '{label}' - must use contract labels"


def test_encounter_decision_blocks_travel():
    """Test that pending_encounter_decision hard_stop blocks travel until resolved."""
    engine = GameEngine(world_seed=12345, config={"system_count": 5})
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    if current_system is None:
        pytest.skip("No current system available")
    
    # Create a travel that will trigger an encounter
    target_system_id = None
    for system in engine.sector.systems:
        if system.system_id != current_system.system_id:
            target_system_id = system.system_id
            break
    
    if not target_system_id:
        pytest.skip("No target system available for travel test")
    
    # Execute travel
    result = engine.execute({
        "type": "travel_to_destination",
        "target_system_id": target_system_id,
    })
    
    # If hard_stop with pending_encounter_decision, verify it blocks
    if result.get("hard_stop") is True and result.get("hard_stop_reason") == "pending_encounter_decision":
        pending_encounter = result.get("pending_encounter")
        assert pending_encounter is not None, "Should have pending_encounter payload"
        
        # Verify travel did not complete
        assert result.get("player", {}).get("system_id") != target_system_id, "Travel should not complete while encounter is pending"
        
        # Resolve encounter
        options = pending_encounter.get("options", [])
        if options:
            decision_id = options[0].get("id")
            if decision_id:
                result2 = engine.execute({
                    "type": "encounter_decision",
                    "encounter_id": pending_encounter.get("encounter_id"),
                    "decision_id": decision_id,
                })
                # After resolution, travel may complete or another encounter may occur
                # Just verify we can proceed (no assertion failure means it worked)


def test_combat_initialization_has_valid_hulls():
    """Regression test: Verify combat initialization uses valid hulls with hull_max > 0."""
    engine = GameEngine(world_seed=12345, config={"system_count": 5})
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    if current_system is None:
        pytest.skip("No current system available")
    
    # Generate an encounter and initialize combat
    spec = generate_encounter(
        encounter_id="HULL-TEST-001",
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
    
    # Verify pending combat exists
    assert engine.has_pending_combat(), "Combat session should be initialized"
    
    # Get pending combat info
    pending_info = engine.get_pending_combat_info()
    assert pending_info is not None, "Pending combat info should be available"
    
    # Verify hull_max > 0 (not 0% initialization bug)
    assert pending_info.get("player_hull_max", 0) > 0, f"Player hull_max should be > 0, got {pending_info.get('player_hull_max', 0)}"
    assert pending_info.get("enemy_hull_max", 0) > 0, f"Enemy hull_max should be > 0, got {pending_info.get('enemy_hull_max', 0)}"
    
    # Verify hull percentages are valid (not both 0% at round 1)
    round_number = pending_info.get("round_number", 0)
    player_hull_pct = pending_info.get("player_hull_pct", 0)
    enemy_hull_pct = pending_info.get("enemy_hull_pct", 0)
    
    if round_number == 1:
        # At round 1, at least one should have > 0% hull (both 0% indicates initialization failure)
        assert player_hull_pct > 0 or enemy_hull_pct > 0, \
            f"At round 1, at least one hull should be > 0%, got player={player_hull_pct}%, enemy={enemy_hull_pct}%"
    
    # Verify no invalid_state flag
    assert not pending_info.get("invalid_state", False), \
        f"Combat should not have invalid_state flag, error: {pending_info.get('error', 'None')}"
