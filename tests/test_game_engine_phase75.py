import sys
from pathlib import Path
import math

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from game_engine import GameEngine  # noqa: E402


def _first_target(engine: GameEngine) -> tuple[str, str | None]:
    if len(engine.sector.systems) < 2:
        system = engine.sector.systems[0]
    else:
        system = engine.sector.systems[1]
    destination_id = system.destinations[0].destination_id if system.destinations else None
    return system.system_id, destination_id


def test_phase75_game_engine_determinism_scripted_steps() -> None:
    engine_probe = GameEngine(world_seed=12345)
    target_system_id, target_destination_id = _first_target(engine_probe)

    commands = [
        {"type": "wait", "days": 1},
        {
            "type": "travel_to_destination",
            "target_system_id": target_system_id,
            "target_destination_id": target_destination_id,
        },
        {"type": "wait", "days": 2},
    ]

    engine_a = GameEngine(world_seed=12345)
    results_a = [engine_a.execute(command) for command in commands]
    engine_b = GameEngine(world_seed=12345)
    results_b = [engine_b.execute(command) for command in commands]
    assert results_a == results_b


def test_phase75_location_action_does_not_advance_time() -> None:
    engine = GameEngine(world_seed=12345)
    before = engine.execute({"type": "wait", "days": 1})
    turn_before = before["turn_after"]

    # Ensure refuel has room so the action path is actually exercised.
    ship = engine.fleet_by_id[engine.player_state.active_ship_id]
    if ship.current_fuel > 0:
        ship.current_fuel -= 1

    result = engine.execute({"type": "location_action", "action_id": "refuel", "kwargs": {"requested_units": 1}})
    if result["ok"] is False:
        pytest.skip("No safe location action available in current deterministic start state.")
    assert result["turn_before"] == turn_before
    assert result["turn_after"] == turn_before


def test_phase751_system_coordinates_are_deterministic() -> None:
    engine_a = GameEngine(world_seed=12345)
    engine_b = GameEngine(world_seed=12345)
    coords_a = sorted((system.system_id, float(system.x), float(system.y)) for system in engine_a.sector.systems)
    coords_b = sorted((system.system_id, float(system.x), float(system.y)) for system in engine_b.sector.systems)
    assert coords_a == coords_b


def test_phase751_warp_range_exceeded_has_no_mutation_or_time_advance() -> None:
    engine = GameEngine(world_seed=12345)
    if len(engine.sector.systems) < 2:
        pytest.skip("Need at least two systems for inter-system warp test.")
    current = engine.sector.get_system(engine.player_state.current_system_id)
    target = sorted(
        [system for system in engine.sector.systems if system.system_id != current.system_id],
        key=lambda system: system.system_id,
    )[0]
    ship = engine.fleet_by_id[engine.player_state.active_ship_id]
    ship.fuel_capacity = 1
    ship.current_fuel = 1
    before_turn = engine.execute({"type": "wait", "days": 1})["turn_after"]
    before_system_id = engine.player_state.current_system_id
    before_destination_id = engine.player_state.current_destination_id
    before_fuel = ship.current_fuel

    result = engine.execute({"type": "travel_to_destination", "target_system_id": target.system_id})
    assert result["ok"] is False
    assert result["error"] == "warp_range_exceeded"
    assert result["turn_before"] == before_turn
    assert result["turn_after"] == before_turn
    assert engine.player_state.current_system_id == before_system_id
    assert engine.player_state.current_destination_id == before_destination_id
    assert ship.current_fuel == before_fuel


def test_phase751_successful_warp_uses_ceil_distance_for_time_and_fuel() -> None:
    engine = GameEngine(world_seed=12345)
    if len(engine.sector.systems) < 2:
        pytest.skip("Need at least two systems for inter-system warp test.")

    current = engine.sector.get_system(engine.player_state.current_system_id)
    candidates = [system for system in engine.sector.systems if system.system_id != current.system_id]
    candidates.sort(
        key=lambda system: (
            math.sqrt(((float(system.x) - float(current.x)) ** 2) + ((float(system.y) - float(current.y)) ** 2)),
            system.system_id,
        )
    )
    target = candidates[0]
    distance = math.sqrt(((float(target.x) - float(current.x)) ** 2) + ((float(target.y) - float(current.y)) ** 2))
    distance_ceil = int(math.ceil(distance))
    ship = engine.fleet_by_id[engine.player_state.active_ship_id]
    ship.fuel_capacity = max(5, distance_ceil + 1)
    ship.current_fuel = ship.fuel_capacity
    fuel_before = int(ship.current_fuel)
    turn_before = engine.execute({"type": "wait", "days": 1})["turn_after"]

    result = engine.execute({"type": "travel_to_destination", "target_system_id": target.system_id})
    assert result["ok"] is True
    assert result["turn_before"] == turn_before
    assert result["turn_after"] == turn_before + distance_ceil
    assert int(ship.current_fuel) == fuel_before - distance_ceil


def test_same_location_travel_blocked() -> None:
    engine = GameEngine(world_seed=12345)
    ship = engine.fleet_by_id[engine.player_state.active_ship_id]
    fuel_before = int(ship.current_fuel)
    current_system_id = engine.player_state.current_system_id
    current_destination_id = engine.player_state.current_destination_id

    result = engine.execute(
        {
            "type": "travel_to_destination",
            "target_system_id": current_system_id,
            "target_destination_id": current_destination_id,
        }
    )
    assert result["ok"] is False
    assert result["error"] == "already_at_destination"
    assert result["turn_before"] == result["turn_after"]
    assert int(ship.current_fuel) == fuel_before
    assert len(result["events"]) == 1
    assert result["events"][0]["stage"] == "start"


def test_inter_system_minimum_clamp() -> None:
    engine = GameEngine(world_seed=12345)
    if len(engine.sector.systems) < 2:
        pytest.skip("Need at least two systems for inter-system warp test.")

    current = engine.sector.get_system(engine.player_state.current_system_id)
    target = sorted(
        [system for system in engine.sector.systems if system.system_id != current.system_id],
        key=lambda system: system.system_id,
    )[0]

    # Force a deterministic near-zero inter-system distance while keeping distinct systems.
    object.__setattr__(target, "x", float(current.x))
    object.__setattr__(target, "y", float(current.y))

    ship = engine.fleet_by_id[engine.player_state.active_ship_id]
    ship.fuel_capacity = max(int(ship.fuel_capacity), 5)
    ship.current_fuel = max(int(ship.current_fuel), 5)
    fuel_before = int(ship.current_fuel)
    turn_before = engine.execute({"type": "wait", "days": 1})["turn_after"]

    result = engine.execute({"type": "travel_to_destination", "target_system_id": target.system_id})
    assert result["ok"] is True
    assert result["turn_before"] == turn_before
    assert result["turn_after"] == turn_before + 1

    travel_events = [event for event in result["events"] if event.get("stage") == "travel"]
    assert len(travel_events) >= 2
    travel_resolution = travel_events[1]["detail"]
    assert int(travel_resolution["fuel_cost"]) == 1
    assert int(ship.current_fuel) == fuel_before - 1


def test_inter_system_arrival_defaults_to_first_destination() -> None:
    engine = GameEngine(world_seed=12345)
    current = engine.sector.get_system(engine.player_state.current_system_id)
    candidates = [system for system in engine.sector.systems if system.system_id != current.system_id]
    candidates.sort(
        key=lambda system: (
            math.sqrt(((float(system.x) - float(current.x)) ** 2) + ((float(system.y) - float(current.y)) ** 2)),
            system.system_id,
        )
    )
    if not candidates:
        pytest.skip("Need at least one inter-system destination.")

    target = candidates[0]
    first_destination = sorted(target.destinations, key=lambda entry: entry.destination_id)[0].destination_id
    ship = engine.fleet_by_id[engine.player_state.active_ship_id]
    distance = math.sqrt(((float(target.x) - float(current.x)) ** 2) + ((float(target.y) - float(current.y)) ** 2))
    distance_ceil = int(math.ceil(distance))
    ship.fuel_capacity = max(int(ship.fuel_capacity), distance_ceil + 5)
    ship.current_fuel = max(int(ship.current_fuel), distance_ceil + 5)

    result = engine.execute({"type": "travel_to_destination", "target_system_id": target.system_id})
    assert result["ok"] is True
    assert result["player"]["destination_id"] == first_destination
