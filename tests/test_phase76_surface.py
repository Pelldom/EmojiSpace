import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from game_engine import GameEngine  # noqa: E402
from world_generator import Location  # noqa: E402


def _current_destination(engine: GameEngine):
    system = engine.sector.get_system(engine.player_state.current_system_id)
    for destination in system.destinations:
        if destination.destination_id == engine.player_state.current_destination_id:
            return destination
    raise AssertionError("current destination not found")


def _set_locations(engine: GameEngine, location_types: list[str]) -> dict[str, Location]:
    destination = _current_destination(engine)
    by_type: dict[str, Location] = {}
    locations: list[Location] = []
    for location_type in location_types:
        location = Location(
            location_id=f"{destination.destination_id}-LOC-{location_type}",
            destination_id=destination.destination_id,
            location_type=location_type,
            enabled=True,
            notes=None,
        )
        by_type[location_type] = location
        locations.append(location)
    object.__setattr__(destination, "locations", locations)
    return by_type


def _stage_detail(result: dict, stage: str) -> dict | None:
    for event in result.get("events", []):
        if isinstance(event, dict) and event.get("stage") == stage:
            detail = event.get("detail")
            if isinstance(detail, dict):
                return detail
    return None


def test_set_logging_command_enables_file_logging(tmp_path) -> None:
    engine = GameEngine(world_seed=12345)
    log_path = tmp_path / "phase76.log"
    result = engine.execute(
        {"type": "set_logging", "enabled": True, "log_path": str(log_path), "truncate": True}
    )
    assert result.get("ok") is True
    assert log_path.exists()


def test_bar_mission_list_and_accept_are_surfaced() -> None:
    engine = GameEngine(world_seed=12345)
    locations = _set_locations(engine, ["bar"])
    enter = engine.execute({"type": "enter_location", "location_id": locations["bar"].location_id})
    assert enter.get("ok") is True

    actions = engine.execute({"type": "list_location_actions"})
    detail = _stage_detail(actions, "location_actions")
    action_ids = {row.get("action_id") for row in detail.get("actions", [])}
    assert "mission_list" in action_ids
    # mission_accept is no longer a location action - it's internal via MissionCore

    mission_list = engine.execute({"type": "location_action", "action_id": "mission_list", "action_kwargs": {}})
    mission_detail = _stage_detail(mission_list, "location_action")
    if mission_detail is None:
        # Try alternative extraction
        for event in mission_list.get("events", []):
            if isinstance(event, dict) and event.get("stage") == "location_action":
                detail = event.get("detail")
                if isinstance(detail, dict) and detail.get("action_id") == "mission_list":
                    mission_detail = detail
                    break
    assert mission_detail is not None
    missions = mission_detail.get("missions", [])
    assert missions
    mission_id = missions[0]["mission_id"]

    # Use MissionCore API (mission_accept command type, not location_action)
    accept = engine.execute({"type": "mission_accept", "mission_id": mission_id})
    assert accept.get("ok") is True
    assert mission_id in engine.player_state.active_missions


def test_administration_pay_fines_and_turn_in_warrants() -> None:
    engine = GameEngine(world_seed=12345)
    locations = _set_locations(engine, ["administration"])
    enter = engine.execute({"type": "enter_location", "location_id": locations["administration"].location_id})
    assert enter.get("ok") is True

    system_id = engine.player_state.current_system_id
    engine.player_state.credits = 1000
    engine.player_state.outstanding_fines[system_id] = 200
    engine.player_state.warrants_by_system[system_id] = [{"warrant_id": "W-1"}]

    pay = engine.execute({"type": "location_action", "action_id": "admin_pay_fines", "action_kwargs": {}})
    assert pay.get("ok") is True
    assert engine.player_state.outstanding_fines.get(system_id) == 0
    assert engine.player_state.credits == 800

    turn_in = engine.execute({"type": "location_action", "action_id": "admin_turn_in", "action_kwargs": {}})
    assert turn_in.get("ok") is True
    assert engine.player_state.warrants_by_system.get(system_id) == []
