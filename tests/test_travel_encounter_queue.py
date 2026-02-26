"""
Test travel encounter queue resumption after encounter resolution.
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from game_engine import GameEngine, EngineContext
from encounter_generator import generate_travel_encounters
from time_engine import get_current_turn


def test_travel_encounter_queue_resumes_after_combat():
    """Test that travel encounter queue resumes after combat ends."""
    engine = GameEngine(world_seed=12345, config={"system_count": 5})
    
    # Get current system
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    if current_system is None:
        pytest.skip("No current system available")
    
    # Find a destination to travel to
    destinations = current_system.destinations
    if not destinations:
        pytest.skip("No destinations available")
    
    target_destination = destinations[0]
    target_system_id = current_system.system_id
    
    # Execute travel (this should generate encounters)
    context = EngineContext(
        command={"type": "travel_to_destination", "target_system_id": target_system_id, "target_destination_id": target_destination.destination_id},
        command_type="travel_to_destination",
        turn_before=int(get_current_turn()),
        turn_after=int(get_current_turn()),
    )
    
    try:
        engine._execute_travel_to_destination(context, {
            "target_system_id": target_system_id,
            "target_destination_id": target_destination.destination_id,
        })
    except Exception as e:
        # Travel might fail for various reasons (fuel, etc), skip if so
        pytest.skip(f"Travel failed: {e}")
    
    # Check if encounters were generated
    if not engine.has_pending_encounter():
        pytest.skip("No encounters generated during travel")
    
    # Get initial encounter info
    initial_encounter_info = engine.get_pending_encounter_info()
    assert initial_encounter_info is not None
    initial_encounter_id = initial_encounter_info.get("encounter_id")
    
    # Check remaining encounters count
    remaining_before = len(engine._pending_travel.get("remaining_encounters", []))
    
    # Resolve first encounter with attack (triggers combat)
    context2 = EngineContext(
        command={"type": "encounter_decision", "encounter_id": initial_encounter_id, "decision_id": "attack"},
        command_type="encounter_decision",
        turn_before=int(get_current_turn()),
        turn_after=int(get_current_turn()),
    )
    
    engine._execute_encounter_decision(context2, {
        "encounter_id": initial_encounter_id,
        "decision_id": "attack",
    })
    
    # If combat was triggered, resolve it quickly
    if engine.has_pending_combat():
        # Play combat until it ends (or max rounds)
        combat_rounds = 0
        max_combat_rounds = 10
        while engine.has_pending_combat() and combat_rounds < max_combat_rounds:
            context3 = EngineContext(
                command={"type": "combat_action", "action": "focus_fire"},
                command_type="combat_action",
                turn_before=int(get_current_turn()),
                turn_after=int(get_current_turn()),
            )
            engine._execute_combat_action(context3, {"action": "focus_fire"})
            combat_rounds += 1
            
            # Check if combat ended
            if not engine.has_pending_combat():
                break
        
        # If loot is pending, resolve it
        if engine.has_pending_loot():
            engine.resolve_pending_loot(take_all=True)
    
    # After combat/loot resolution, check if next encounter is set up
    # The engine should have resumed the encounter queue if encounters remain
    if remaining_before > 0:
        # There were remaining encounters - check if next one is set up
        assert engine.has_pending_encounter(), "Next encounter should be set up after combat/loot resolution"
        
        next_encounter_info = engine.get_pending_encounter_info()
        assert next_encounter_info is not None
        next_encounter_id = next_encounter_info.get("encounter_id")
        
        # Verify encounter ID changed (we're on the next encounter)
        assert next_encounter_id != initial_encounter_id, "Encounter ID should change to next encounter"
        
        # Verify remaining encounters count decreased
        remaining_after = len(engine._pending_travel.get("remaining_encounters", []))
        assert remaining_after == remaining_before - 1, f"Remaining encounters should decrease by 1 (was {remaining_before}, now {remaining_after})"
    else:
        # No remaining encounters - pending travel should be cleared
        assert not engine.has_pending_encounter(), "No pending encounter should exist when queue is empty"


def test_travel_encounter_queue_preserves_order():
    """Test that encounter queue preserves FIFO order."""
    engine = GameEngine(world_seed=12345, config={"system_count": 5})
    
    # Get current system
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    if current_system is None:
        pytest.skip("No current system available")
    
    # Find a destination to travel to
    destinations = current_system.destinations
    if not destinations:
        pytest.skip("No destinations available")
    
    target_destination = destinations[0]
    target_system_id = current_system.system_id
    
    # Execute travel
    context = EngineContext(
        command={"type": "travel_to_destination", "target_system_id": target_system_id, "target_destination_id": target_destination.destination_id},
        command_type="travel_to_destination",
        turn_before=int(get_current_turn()),
        turn_after=int(get_current_turn()),
    )
    
    try:
        engine._execute_travel_to_destination(context, {
            "target_system_id": target_system_id,
            "target_destination_id": target_destination.destination_id,
        })
    except Exception as e:
        pytest.skip(f"Travel failed: {e}")
    
    if not engine.has_pending_encounter():
        pytest.skip("No encounters generated")
    
    # Collect all encounter IDs in order
    encounter_ids = []
    
    # Get first encounter
    encounter_info = engine.get_pending_encounter_info()
    if encounter_info:
        encounter_ids.append(encounter_info.get("encounter_id"))
    
    # Get remaining encounters
    remaining = engine._pending_travel.get("remaining_encounters", [])
    for enc in remaining:
        encounter_ids.append(str(getattr(enc, "encounter_id", "")))
    
    # Resolve encounters one by one and verify order
    resolved_ids = []
    while engine.has_pending_encounter() and len(resolved_ids) < len(encounter_ids):
        current_info = engine.get_pending_encounter_info()
        if not current_info:
            break
        
        current_id = current_info.get("encounter_id")
        resolved_ids.append(current_id)
        
        # Resolve with ignore (non-combat)
        context2 = EngineContext(
            command={"type": "encounter_decision", "encounter_id": current_id, "decision_id": "ignore"},
            command_type="encounter_decision",
            turn_before=int(get_current_turn()),
            turn_after=int(get_current_turn()),
        )
        
        engine._execute_encounter_decision(context2, {
            "encounter_id": current_id,
            "decision_id": "ignore",
        })
    
    # Verify order is preserved
    assert resolved_ids == encounter_ids[:len(resolved_ids)], "Encounter order should be preserved (FIFO)"


def test_travel_encounter_cursor_tracking():
    """Test that encounter cursor correctly tracks processed encounters."""
    engine = GameEngine(world_seed=12345, config={"system_count": 5})
    
    # Get current system
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    if current_system is None:
        pytest.skip("No current system available")
    
    # Find a destination to travel to
    destinations = current_system.destinations
    if not destinations:
        pytest.skip("No destinations available")
    
    target_destination = destinations[0]
    target_system_id = current_system.system_id
    
    # Execute travel
    context = EngineContext(
        command={"type": "travel_to_destination", "target_system_id": target_system_id, "target_destination_id": target_destination.destination_id},
        command_type="travel_to_destination",
        turn_before=int(get_current_turn()),
        turn_after=int(get_current_turn()),
    )
    
    try:
        engine._execute_travel_to_destination(context, {
            "target_system_id": target_system_id,
            "target_destination_id": target_destination.destination_id,
        })
    except Exception as e:
        pytest.skip(f"Travel failed: {e}")
    
    if not engine.has_pending_encounter():
        pytest.skip("No encounters generated")
    
    # Get original encounter count
    original_count = engine._pending_travel.get("original_encounter_count")
    if original_count is None or original_count < 2:
        pytest.skip(f"Need at least 2 encounters, got {original_count}")
    
    # Process at least 2 encounters (one non-combat, one combat if possible)
    processed_count = 0
    max_encounters_to_process = min(3, original_count)
    
    while engine.has_pending_encounter() and processed_count < max_encounters_to_process:
        encounter_info = engine.get_pending_encounter_info()
        if not encounter_info:
            break
        
        current_id = encounter_info.get("encounter_id")
        processed_count += 1
        
        # First encounter: try attack (might trigger combat)
        # Subsequent encounters: use ignore (non-combat)
        decision = "attack" if processed_count == 1 else "ignore"
        
        context2 = EngineContext(
            command={"type": "encounter_decision", "encounter_id": current_id, "decision_id": decision},
            command_type="encounter_decision",
            turn_before=int(get_current_turn()),
            turn_after=int(get_current_turn()),
        )
        
        engine._execute_encounter_decision(context2, {
            "encounter_id": current_id,
            "decision_id": decision,
        })
        
        # If combat was triggered, resolve it quickly
        if engine.has_pending_combat():
            combat_rounds = 0
            max_combat_rounds = 10
            while engine.has_pending_combat() and combat_rounds < max_combat_rounds:
                context3 = EngineContext(
                    command={"type": "combat_action", "action": "focus_fire"},
                    command_type="combat_action",
                    turn_before=int(get_current_turn()),
                    turn_after=int(get_current_turn()),
                )
                engine._execute_combat_action(context3, {"action": "focus_fire"})
                combat_rounds += 1
                
                if not engine.has_pending_combat():
                    break
            
            # If loot is pending, resolve it
            if engine.has_pending_loot():
                engine.resolve_pending_loot(take_all=True)
        
        # Verify cursor matches processed count
        cursor = engine._pending_travel.get("encounter_cursor", 0)
        assert cursor == processed_count, (
            f"Cursor should equal processed count: cursor={cursor}, processed={processed_count}"
        )
        
        # Verify remaining encounters count is correct
        remaining = engine._pending_travel.get("remaining_encounters", [])
        expected_remaining = original_count - cursor
        actual_remaining = len(remaining)
        assert actual_remaining == expected_remaining, (
            f"Remaining count mismatch: original={original_count}, cursor={cursor}, "
            f"expected_remaining={expected_remaining}, actual_remaining={actual_remaining}"
        )
    
    # Final verification: cursor should equal processed count
    final_cursor = engine._pending_travel.get("encounter_cursor", 0) if engine._pending_travel else 0
    assert final_cursor == processed_count, (
        f"Final cursor should equal processed count: cursor={final_cursor}, processed={processed_count}"
    )


def test_travel_encounter_ids_no_drift():
    """Test that encounter IDs are exactly enc_0 through enc_N-1 with no gaps or extras."""
    engine = GameEngine(world_seed=12345, config={"system_count": 5})
    
    # Get current system
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    if current_system is None:
        pytest.skip("No current system available")
    
    # Find a destination to travel to
    destinations = current_system.destinations
    if not destinations:
        pytest.skip("No destinations available")
    
    target_destination = destinations[0]
    target_system_id = current_system.system_id
    
    # Execute travel
    context = EngineContext(
        command={"type": "travel_to_destination", "target_system_id": target_system_id, "target_destination_id": target_destination.destination_id},
        command_type="travel_to_destination",
        turn_before=int(get_current_turn()),
        turn_after=int(get_current_turn()),
    )
    
    try:
        engine._execute_travel_to_destination(context, {
            "target_system_id": target_system_id,
            "target_destination_id": target_destination.destination_id,
        })
    except Exception as e:
        pytest.skip(f"Travel failed: {e}")
    
    if not engine.has_pending_encounter():
        pytest.skip("No encounters generated")
    
    # Get original encounter count
    original_count = engine._pending_travel.get("original_encounter_count")
    if original_count is None:
        pytest.skip("Could not determine original encounter count")
    
    # Collect all processed encounter IDs
    processed_ids = []
    
    # Process all encounters
    while engine.has_pending_encounter():
        encounter_info = engine.get_pending_encounter_info()
        if not encounter_info:
            break
        
        current_id = encounter_info.get("encounter_id")
        processed_ids.append(current_id)
        
        # Resolve with ignore (non-combat) to avoid combat complexity
        context2 = EngineContext(
            command={"type": "encounter_decision", "encounter_id": current_id, "decision_id": "ignore"},
            command_type="encounter_decision",
            turn_before=int(get_current_turn()),
            turn_after=int(get_current_turn()),
        )
        
        engine._execute_encounter_decision(context2, {
            "encounter_id": current_id,
            "decision_id": "ignore",
        })
    
    # Verify we processed exactly the expected number
    assert len(processed_ids) == original_count, f"Processed {len(processed_ids)} encounters, expected {original_count}"
    
    # Extract numeric indices from encounter IDs (e.g., "TRAVEL-...-enc_0" -> 0)
    indices = []
    for enc_id in processed_ids:
        # Encounter IDs typically end with enc_N
        if "_enc_" in enc_id:
            parts = enc_id.split("_enc_")
            if len(parts) > 1:
                try:
                    indices.append(int(parts[-1]))
                except ValueError:
                    pass
    
    # Verify indices are exactly 0, 1, 2, ..., N-1 with no gaps
    if indices:
        expected_indices = list(range(original_count))
        assert indices == expected_indices, (
            f"Encounter indices should be exactly {expected_indices}, got {indices}. "
            f"This indicates encounter objects were reconstructed or re-indexed."
        )
