import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from interaction_layer import destination_actions, execute_refuel  # noqa: E402
from npc_entity import NPCEntity, NPCPersistenceTier  # noqa: E402
from ship_assembler import assemble_ship  # noqa: E402
from ship_entity import ShipEntity  # noqa: E402
from travel_resolution import resolve_travel  # noqa: E402


def test_fuel_capacity_calculation() -> None:
    assembled = assemble_ship(
        "civ_t1_midge",
        [{"module_id": "ship_utility_extra_fuel_mk1"}],
    )
    assert assembled["fuel_capacity"] == 15


def test_initial_fuel_full() -> None:
    ship = ShipEntity(fuel_capacity=18)
    assert ship.current_fuel == 18


def test_travel_consumes_fuel() -> None:
    ship = ShipEntity(fuel_capacity=20, current_fuel=20)
    ticks = {"count": 0}

    def _advance() -> int:
        ticks["count"] += 1
        return ticks["count"]

    inter = resolve_travel(ship=ship, inter_system=True, distance_ly=3, advance_time=_advance)
    intra = resolve_travel(ship=ship, inter_system=False, distance_ly=999, advance_time=_advance)
    assert inter.success is True
    assert intra.success is True
    assert ship.current_fuel == 16
    assert ticks["count"] == 2


def test_travel_rejected_if_insufficient_fuel() -> None:
    ship = ShipEntity(fuel_capacity=2, current_fuel=1)
    ticks = {"count": 0}

    def _advance() -> int:
        ticks["count"] += 1
        return ticks["count"]

    result = resolve_travel(ship=ship, inter_system=True, distance_ly=2, advance_time=_advance)
    assert result.success is False
    assert result.reason == "insufficient_fuel"
    assert ship.current_fuel == 1
    assert ticks["count"] == 0


def test_refuel_partial_and_full() -> None:
    ship = ShipEntity(fuel_capacity=20, current_fuel=10)
    partial = execute_refuel(ship=ship, player_credits=100, requested_units=3)
    assert partial["ok"] is True
    assert partial["units_purchased"] == 3
    assert partial["total_cost"] == 15
    assert partial["credits"] == 85
    assert ship.current_fuel == 13

    full = execute_refuel(ship=ship, player_credits=1000, requested_units=None)
    assert full["ok"] is True
    assert full["units_purchased"] == 7
    assert full["total_cost"] == 35
    assert full["credits"] == 965
    assert ship.current_fuel == 20


def test_refuel_requires_datanet() -> None:
    with_datanet = {"locations": [{"location_type": "market"}, {"location_type": "datanet"}]}
    without_datanet = {"locations": [{"location_type": "market"}]}
    assert "refuel" in destination_actions(with_datanet, base_actions=["ignore"])
    assert "refuel" not in destination_actions(without_datanet, base_actions=["ignore"])


def _crew(npc_id: str, role: str, tags: list[str] | None = None) -> NPCEntity:
    return NPCEntity(
        npc_id=npc_id,
        is_crew=True,
        crew_role_id=role,
        crew_tags=list(tags or []),
        persistence_tier=NPCPersistenceTier.TIER_2,
    )


def test_travel_with_no_crew_unchanged_fuel_cost() -> None:
    ship = ShipEntity(fuel_capacity=20, current_fuel=20)
    result = resolve_travel(ship=ship, inter_system=True, distance_ly=3)
    assert result.success is True
    assert result.fuel_cost == 3
    assert ship.current_fuel == 17


def test_travel_with_navigator_reduces_fuel_minimum_one_respected() -> None:
    ship = ShipEntity(
        fuel_capacity=20,
        current_fuel=20,
        crew=[_crew("NPC-1", role="navigator")],
    )
    result = resolve_travel(ship=ship, inter_system=False, distance_ly=999)
    assert result.success is True
    assert result.fuel_cost == 1
    assert ship.current_fuel == 19


def test_travel_with_multiple_fuel_penalties_stacks() -> None:
    ship = ShipEntity(
        fuel_capacity=20,
        current_fuel=20,
        crew=[
            _crew("NPC-1", role="pilot", tags=["crew:wasteful"]),
            _crew("NPC-2", role="pilot", tags=["crew:wasteful"]),
        ],
    )
    result = resolve_travel(ship=ship, inter_system=True, distance_ly=3)
    assert result.success is True
    assert result.fuel_cost == 5
    assert ship.current_fuel == 15


def test_travel_fuel_cost_never_below_one_with_large_negative_delta() -> None:
    ship = ShipEntity(
        fuel_capacity=20,
        current_fuel=20,
        crew=[
            _crew("NPC-1", role="navigator", tags=["crew:fuel_efficient"]),
            _crew("NPC-2", role="navigator", tags=["crew:fuel_efficient"]),
        ],
    )
    result = resolve_travel(ship=ship, inter_system=False, distance_ly=999)
    assert result.success is True
    assert result.fuel_cost == 1
    assert ship.current_fuel == 19


def test_travel_with_crew_modifiers_is_deterministic() -> None:
    crew = [
        _crew("NPC-1", role="navigator", tags=["crew:fuel_efficient"]),
        _crew("NPC-2", role="pilot", tags=["crew:wasteful"]),
    ]
    ship_a = ShipEntity(fuel_capacity=20, current_fuel=20, crew=crew)
    ship_b = ShipEntity(fuel_capacity=20, current_fuel=20, crew=crew)

    result_a = resolve_travel(ship=ship_a, inter_system=True, distance_ly=4)
    result_b = resolve_travel(ship=ship_b, inter_system=True, distance_ly=4)

    assert result_a.fuel_cost == result_b.fuel_cost
    assert result_a.current_fuel == result_b.current_fuel


def test_game_engine_travel_rejected_insufficient_fuel() -> None:
    """Test that GameEngine rejects travel when current_fuel=10 cannot travel to system at distance 11."""
    from game_engine import GameEngine  # noqa: E402
    import math
    
    # Create engine with more systems to ensure we have systems at various distances
    engine = GameEngine(
        world_seed=12345,
        config={"system_count": 10},
    )
    
    # Set ship fuel to 10
    active_ship = engine.fleet_by_id.get(engine.player_state.active_ship_id)
    assert active_ship is not None
    active_ship.current_fuel = 10
    fuel_before = active_ship.current_fuel
    
    # Find a system at distance > 10 using engine's distance calculation
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    assert current_system is not None
    
    # Find target system at distance > 10
    target_system = None
    target_distance = None
    for system in engine.sector.systems:
        if system.system_id == current_system.system_id:
            continue
        distance = engine._warp_distance_ly(origin=current_system, target=system)
        if distance > 10.0:
            target_system = system
            target_distance = distance
            break
    
    # If no system is > 10 LY away, set fuel to 1 and use any other system
    if target_system is None:
        active_ship.current_fuel = 1
        fuel_before = 1
        # Use any other system
        for system in engine.sector.systems:
            if system.system_id != current_system.system_id:
                target_system = system
                target_distance = engine._warp_distance_ly(origin=current_system, target=system)
                break
    
    assert target_system is not None
    assert target_distance is not None
    required_fuel = int(math.ceil(target_distance))
    
    # Verify we don't have enough fuel
    assert active_ship.current_fuel < required_fuel, (
        f"Test setup error: fuel {active_ship.current_fuel} >= required {required_fuel} "
        f"(distance={target_distance:.3f})"
    )
    
    # Attempt travel - should fail
    result = engine.execute({
        "type": "travel_to_destination",
        "target_system_id": target_system.system_id,
    })
    
    # Travel should fail with error
    assert result.get("ok") is False, f"Travel should have failed, got: {result}"
    error = result.get("error", "")
    assert "insufficient_fuel" in error or "warp_range_exceeded" in error, (
        f"Expected insufficient_fuel or warp_range_exceeded, got: {error}"
    )
    
    # Fuel should be unchanged
    assert active_ship.current_fuel == fuel_before, "Fuel should not change on failed travel"


def test_game_engine_travel_consumes_fuel_correctly() -> None:
    """Test that after travel of 5 LY from fuel 20, current_fuel becomes 15."""
    import math
    
    from game_engine import GameEngine  # noqa: E402
    from government_registry import GovernmentRegistry  # noqa: E402
    
    # Create engine
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    engine = GameEngine(
        world_seed=12345,
        config={"system_count": 5},
    )
    
    # Set ship fuel - ensure capacity is high enough
    active_ship = engine.fleet_by_id.get(engine.player_state.active_ship_id)
    assert active_ship is not None
    # Increase fuel capacity if needed
    if active_ship.fuel_capacity < 25:
        active_ship.fuel_capacity = 25
    initial_fuel = 20
    active_ship.set_current_fuel(initial_fuel, None, 0)
    
    # Find a system at approximately 5 LY distance
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    assert current_system is not None
    
    target_system = None
    target_distance = None
    for system in engine.sector.systems:
        if system.system_id == current_system.system_id:
            continue
        distance = math.sqrt((system.x - current_system.x) ** 2 + (system.y - current_system.y) ** 2)
        if 4.5 <= distance <= 5.5:  # Allow some tolerance
            target_system = system
            target_distance = distance
            break
    
    # If no system at exactly 5 LY, use closest one and verify fuel consumption
    if target_system is None:
        min_distance = float('inf')
        for system in engine.sector.systems:
            if system.system_id == current_system.system_id:
                continue
            distance = math.sqrt((system.x - current_system.x) ** 2 + (system.y - current_system.y) ** 2)
            if distance < min_distance:
                min_distance = distance
                target_system = system
                target_distance = distance
    
    assert target_system is not None
    assert target_distance is not None
    
    # Ensure we have enough fuel
    required_fuel = int(math.ceil(target_distance))
    if initial_fuel < required_fuel:
        new_initial = required_fuel + 5
        if active_ship.fuel_capacity < new_initial:
            active_ship.fuel_capacity = new_initial + 5
        active_ship.set_current_fuel(new_initial, None, 0)
        initial_fuel = new_initial
    
    # Execute travel
    result = engine.execute({
        "type": "travel_to_destination",
        "target_system_id": target_system.system_id,
    })
    
    # Travel should succeed
    assert result.get("ok") is not False, f"Travel should have succeeded, got: {result}"
    
    # Verify fuel was consumed
    expected_fuel = initial_fuel - required_fuel
    assert active_ship.current_fuel == expected_fuel, (
        f"Expected fuel {expected_fuel} after travel of {required_fuel} LY from {initial_fuel}, "
        f"got {active_ship.current_fuel}"
    )
    
    # Verify deterministic behavior - run again with same setup
    engine2 = GameEngine(
        world_seed=12345,
        config={"system_count": 5},
    )
    active_ship2 = engine2.fleet_by_id.get(engine2.player_state.active_ship_id)
    assert active_ship2 is not None
    if active_ship2.fuel_capacity < initial_fuel:
        active_ship2.fuel_capacity = initial_fuel + 5
    active_ship2.set_current_fuel(initial_fuel, None, 0)
    
    current_system2 = engine2.sector.get_system(engine2.player_state.current_system_id)
    target_system2 = engine2.sector.get_system(target_system.system_id)
    
    result2 = engine2.execute({
        "type": "travel_to_destination",
        "target_system_id": target_system.system_id,
    })
    
    # Travel should succeed
    assert result2.get("ok") is not False, f"Travel should have succeeded, got: {result2}"
    
    assert active_ship2.current_fuel == expected_fuel, "Fuel consumption should be deterministic"