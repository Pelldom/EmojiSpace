#!/usr/bin/env python3
"""
Validation script for Phase 7.11.1 — Centralized Mission Lifecycle Evaluation (Delivery Only)

Tests:
1. Delivery mission completion on arrival at target destination
2. days_remaining semantics (None = infinite, > 0 = turns remaining, 0 = expired)
3. Time limit expiration handling
4. resolved_turn metadata storage
5. Logging events
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mission_entity import MissionEntity, MissionState, MissionOutcome
from mission_manager import MissionManager, evaluate_active_missions
from player_state import PlayerState

# Configure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def test_delivery_completion():
    """Test delivery mission completion on arrival."""
    print("=" * 60)
    print("Test 1: Delivery Mission Completion")
    print("=" * 60)
    
    # Setup
    mission_manager = MissionManager()
    player_state = PlayerState()
    player_state.current_system_id = "SYS-001"
    player_state.current_destination_id = "SYS-001-DST-01"
    
    # Create delivery mission
    mission = MissionEntity(
        mission_id="MIS-TEST-001",
        mission_type="delivery",
        mission_tier=1,
        mission_state=MissionState.ACTIVE,
        system_id="SYS-001",
        target={
            "target_type": "destination",
            "target_id": "SYS-001-DST-02",  # Different destination
            "system_id": "SYS-001",
        },
        source={"source_type": "bar", "source_id": "test_source"},
        origin={"system_id": "SYS-001", "destination_id": "SYS-001-DST-01"},
        distance_ly=0,
        reward_profile_id="mission_delivery",
        objectives=[
            {
                "objective_id": "OBJ-1",
                "objective_type": "deliver_cargo",
                "status": "pending",
                "parameters": {"goods": [{"good_id": "GOOD-001", "quantity": 1}]},
            }
        ],
    )
    
    mission_manager.missions[mission.mission_id] = mission
    player_state.active_missions.append(mission.mission_id)
    
    # Before travel: mission should be active
    print(f"\nBefore travel:")
    print(f"  Mission state: {mission.mission_state}")
    print(f"  Active missions: {player_state.active_missions}")
    print(f"  Current destination: {player_state.current_destination_id}")
    print(f"  Target destination: {mission.target.get('target_id')}")
    
    # Evaluate before arrival (should not complete)
    result1 = evaluate_active_missions(
        mission_manager=mission_manager,
        player_state=player_state,
        current_system_id="SYS-001",
        current_destination_id="SYS-001-DST-01",
        event_context={"event": "turn_tick"},
        logger=None,
        turn=1,
    )
    
    print(f"\nAfter evaluation (not at target):")
    print(f"  Mission state: {mission.mission_state}")
    print(f"  Completed: {result1['completed_mission_ids']}")
    assert mission.mission_state == MissionState.ACTIVE, "Mission should still be active"
    assert len(result1["completed_mission_ids"]) == 0, "No missions should complete"
    
    # Travel to target destination
    player_state.current_destination_id = "SYS-001-DST-02"
    
    # Evaluate on arrival (should complete)
    result2 = evaluate_active_missions(
        mission_manager=mission_manager,
        player_state=player_state,
        current_system_id="SYS-001",
        current_destination_id="SYS-001-DST-02",
        event_context={"event": "travel_arrival", "target_destination_id": "SYS-001-DST-02"},
        logger=None,
        turn=2,
    )
    
    print(f"\nAfter arrival at target:")
    print(f"  Mission state: {mission.mission_state}")
    print(f"  Mission outcome: {mission.outcome}")
    print(f"  Active missions: {player_state.active_missions}")
    print(f"  Completed missions: {player_state.completed_missions}")
    print(f"  Resolved turn: {mission.persistent_state.get('resolved_turn')}")
    print(f"  Completed: {result2['completed_mission_ids']}")
    
    # Assertions
    assert mission.mission_state == MissionState.RESOLVED, f"Mission should be resolved, got {mission.mission_state}"
    assert mission.outcome == MissionOutcome.COMPLETED, f"Mission should be completed, got {mission.outcome}"
    assert mission.mission_id not in player_state.active_missions, "Mission should be removed from active"
    assert mission.mission_id in player_state.completed_missions, "Mission should be in completed"
    assert mission.persistent_state.get("resolved_turn") == 2, "Resolved turn should be set"
    assert len(result2["completed_mission_ids"]) == 1, "One mission should complete"
    
    print("\n✓ Test 1 PASSED: Delivery mission completes on arrival")
    return True


def test_days_remaining_none():
    """Test days_remaining = None (infinite duration)."""
    print("\n" + "=" * 60)
    print("Test 2: days_remaining = None (Infinite Duration)")
    print("=" * 60)
    
    # Setup
    mission_manager = MissionManager()
    player_state = PlayerState()
    
    # Create mission with days_remaining = None
    mission = MissionEntity(
        mission_id="MIS-TEST-002",
        mission_type="delivery",
        mission_tier=1,
        mission_state=MissionState.ACTIVE,
        system_id="SYS-001",
        target={"target_type": "destination", "target_id": "SYS-001-DST-01", "system_id": "SYS-001"},
        source={"source_type": "bar", "source_id": "test_source"},
        origin={"system_id": "SYS-001", "destination_id": "SYS-001-DST-01"},
        distance_ly=0,
        reward_profile_id="mission_delivery",
        objectives=[],
    )
    # days_remaining not set (defaults to None via persistent_state.get())
    
    mission_manager.missions[mission.mission_id] = mission
    player_state.active_missions.append(mission.mission_id)
    
    # Evaluate multiple times (should not expire)
    for turn in range(1, 6):
        result = evaluate_active_missions(
            mission_manager=mission_manager,
            player_state=player_state,
            current_system_id="SYS-001",
            current_destination_id="SYS-001-DST-02",  # Not at target
            event_context={"event": "turn_tick"},
            logger=None,
            turn=turn,
        )
        
        days_remaining = mission.persistent_state.get("days_remaining")
        print(f"  Turn {turn}: days_remaining={days_remaining}, state={mission.mission_state}")
        
        assert days_remaining is None, f"days_remaining should remain None, got {days_remaining}"
        assert mission.mission_state == MissionState.ACTIVE, "Mission should remain active"
        assert len(result["failed_mission_ids"]) == 0, "Mission should not fail"
    
    print("\n✓ Test 2 PASSED: days_remaining = None preserves infinite duration")
    return True


def test_days_remaining_expiration():
    """Test days_remaining expiration (0 = expired)."""
    print("\n" + "=" * 60)
    print("Test 3: days_remaining Expiration")
    print("=" * 60)
    
    # Setup
    mission_manager = MissionManager()
    player_state = PlayerState()
    
    # Create mission with days_remaining = 2
    mission = MissionEntity(
        mission_id="MIS-TEST-003",
        mission_type="delivery",
        mission_tier=1,
        mission_state=MissionState.ACTIVE,
        system_id="SYS-001",
        target={"target_type": "destination", "target_id": "SYS-001-DST-01", "system_id": "SYS-001"},
        source={"source_type": "bar", "source_id": "test_source"},
        origin={"system_id": "SYS-001", "destination_id": "SYS-001-DST-01"},
        distance_ly=0,
        reward_profile_id="mission_delivery",
        objectives=[],
    )
    mission.persistent_state["days_remaining"] = 2
    
    mission_manager.missions[mission.mission_id] = mission
    player_state.active_missions.append(mission.mission_id)
    
    # Turn 1: days_remaining = 2 -> 1
    result1 = evaluate_active_missions(
        mission_manager=mission_manager,
        player_state=player_state,
        current_system_id="SYS-001",
        current_destination_id="SYS-001-DST-02",
        event_context={"event": "turn_tick"},
        logger=None,
        turn=1,
    )
    
    print(f"  Turn 1: days_remaining={mission.persistent_state.get('days_remaining')}, state={mission.mission_state}")
    assert mission.persistent_state.get("days_remaining") == 1, "Should decrement to 1"
    assert mission.mission_state == MissionState.ACTIVE, "Should still be active"
    assert len(result1["failed_mission_ids"]) == 0, "Should not fail yet"
    
    # Turn 2: days_remaining = 1 -> 0 (expired)
    result2 = evaluate_active_missions(
        mission_manager=mission_manager,
        player_state=player_state,
        current_system_id="SYS-001",
        current_destination_id="SYS-001-DST-02",
        event_context={"event": "turn_tick"},
        logger=None,
        turn=2,
    )
    
    print(f"  Turn 2: days_remaining={mission.persistent_state.get('days_remaining')}, state={mission.mission_state}")
    assert mission.persistent_state.get("days_remaining") == 0, "Should decrement to 0"
    assert mission.mission_state == MissionState.RESOLVED, "Should be resolved"
    assert mission.outcome == MissionOutcome.FAILED, "Should be failed"
    assert mission.failure_reason == "expired", "Failure reason should be expired"
    assert mission.mission_id not in player_state.active_missions, "Should be removed from active"
    assert len(result2["failed_mission_ids"]) == 1, "Should be in failed list"
    assert mission.persistent_state.get("resolved_turn") == 2, "Resolved turn should be set"
    
    print("\n✓ Test 3 PASSED: days_remaining expiration works correctly")
    return True


def test_days_remaining_zero_initial():
    """Test days_remaining = 0 on first evaluation (should fail immediately)."""
    print("\n" + "=" * 60)
    print("Test 4: days_remaining = 0 (Immediate Expiration)")
    print("=" * 60)
    
    # Setup
    mission_manager = MissionManager()
    player_state = PlayerState()
    
    # Create mission with days_remaining = 0
    mission = MissionEntity(
        mission_id="MIS-TEST-004",
        mission_type="delivery",
        mission_tier=1,
        mission_state=MissionState.ACTIVE,
        system_id="SYS-001",
        target={"target_type": "destination", "target_id": "SYS-001-DST-01", "system_id": "SYS-001"},
        source={"source_type": "bar", "source_id": "test_source"},
        origin={"system_id": "SYS-001", "destination_id": "SYS-001-DST-01"},
        distance_ly=0,
        reward_profile_id="mission_delivery",
        objectives=[],
    )
    mission.persistent_state["days_remaining"] = 0
    
    mission_manager.missions[mission.mission_id] = mission
    player_state.active_missions.append(mission.mission_id)
    
    # Evaluate: days_remaining = 0 -> -1 (expired)
    result = evaluate_active_missions(
        mission_manager=mission_manager,
        player_state=player_state,
        current_system_id="SYS-001",
        current_destination_id="SYS-001-DST-02",
        event_context={"event": "turn_tick"},
        logger=None,
        turn=1,
    )
    
    print(f"  Turn 1: days_remaining={mission.persistent_state.get('days_remaining')}, state={mission.mission_state}")
    assert mission.persistent_state.get("days_remaining") == -1, "Should decrement to -1"
    assert mission.mission_state == MissionState.RESOLVED, "Should be resolved"
    assert mission.outcome == MissionOutcome.FAILED, "Should be failed"
    assert len(result["failed_mission_ids"]) == 1, "Should be in failed list"
    
    print("\n✓ Test 4 PASSED: days_remaining = 0 fails immediately")
    return True


def main():
    """Run all validation tests."""
    print("\n" + "=" * 60)
    print("Phase 7.11.1 — Mission Lifecycle Evaluation Validation")
    print("=" * 60)
    
    tests = [
        test_delivery_completion,
        test_days_remaining_none,
        test_days_remaining_expiration,
        test_days_remaining_zero_initial,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except AssertionError as e:
            print(f"\n✗ Test FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ Test ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✓ All tests PASSED")
        return 0
    else:
        print("\n✗ Some tests FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
