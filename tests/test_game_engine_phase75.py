import sys
from pathlib import Path

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
            "inter_system": True,
            "distance_ly": 1,
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
