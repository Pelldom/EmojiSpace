import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from game_engine import GameEngine  # noqa: E402
from npc_entity import NPCPersistenceTier  # noqa: E402
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


def test_bar_structural_npc_is_tier3_and_first() -> None:
    engine = GameEngine(world_seed=12345)
    locations = _set_locations(engine, ["bar"])
    enter = engine.execute({"type": "enter_location", "location_id": locations["bar"].location_id})
    assert enter.get("ok") is True

    rows_result = engine.execute({"type": "list_location_npcs"})
    rows = (_stage_detail(rows_result, "location_npcs") or {}).get("npcs", [])
    assert isinstance(rows, list) and rows
    first = rows[0]
    assert first.get("role") == "bartender"
    assert int(first.get("persistence_tier")) == int(NPCPersistenceTier.TIER_3)


def test_administration_structural_npc_is_tier3_and_first() -> None:
    engine = GameEngine(world_seed=12345)
    locations = _set_locations(engine, ["administration"])
    enter = engine.execute({"type": "enter_location", "location_id": locations["administration"].location_id})
    assert enter.get("ok") is True

    rows_result = engine.execute({"type": "list_location_npcs"})
    rows = (_stage_detail(rows_result, "location_npcs") or {}).get("npcs", [])
    assert isinstance(rows, list) and rows
    first = rows[0]
    assert first.get("role") == "administrator"
    assert int(first.get("persistence_tier")) == int(NPCPersistenceTier.TIER_3)


def test_bartender_interactions_and_rumor_payload_are_deterministic_same_turn() -> None:
    engine = GameEngine(world_seed=12345)
    locations = _set_locations(engine, ["bar"])
    assert engine.execute({"type": "enter_location", "location_id": locations["bar"].location_id}).get("ok") is True

    npc_rows = (_stage_detail(engine.execute({"type": "list_location_npcs"}), "location_npcs") or {}).get("npcs", [])
    bartender_id = str(npc_rows[0]["npc_id"])

    interactions_result = engine.execute({"type": "list_npc_interactions", "npc_id": bartender_id})
    interactions = (_stage_detail(interactions_result, "npc_interactions") or {}).get("interactions", [])
    interaction_ids = [row.get("action_id") for row in interactions if isinstance(row, dict)]
    assert interaction_ids == ["npc_talk", "bartender_rumors"]

    first = engine.execute({"type": "npc_interact", "npc_id": bartender_id, "interaction_id": "bartender_rumors"})
    second = engine.execute({"type": "npc_interact", "npc_id": bartender_id, "interaction_id": "bartender_rumors"})
    first_payload = (_stage_detail(first, "npc_interaction") or {}).get("result", {})
    second_payload = (_stage_detail(second, "npc_interaction") or {}).get("result", {})
    assert first_payload == second_payload
    assert first_payload.get("ok") is True
    assert first_payload.get("rumor_type") in {"red_herring", "lore", "world_state_hint"}
    assert isinstance(first_payload.get("rumor_text"), str)

    legacy = engine.execute({"type": "location_action", "action_id": "bar_rumors", "action_kwargs": {}})
    legacy_payload = (_stage_detail(legacy, "location_action") or {}).get("result", {})
    assert legacy_payload.get("ok") is True
    assert legacy_payload.get("rumor_type") in {"red_herring", "lore", "world_state_hint"}
    assert isinstance(legacy_payload.get("rumor_text"), str)


def test_administrator_interactions_include_pay_fines_and_no_missions() -> None:
    engine = GameEngine(world_seed=12345)
    locations = _set_locations(engine, ["administration"])
    assert (
        engine.execute({"type": "enter_location", "location_id": locations["administration"].location_id}).get("ok")
        is True
    )
    npc_rows = (_stage_detail(engine.execute({"type": "list_location_npcs"}), "location_npcs") or {}).get("npcs", [])
    admin_id = str(npc_rows[0]["npc_id"])

    interactions_result = engine.execute({"type": "list_npc_interactions", "npc_id": admin_id})
    interactions = (_stage_detail(interactions_result, "npc_interactions") or {}).get("interactions", [])
    interaction_ids = [row.get("action_id") for row in interactions if isinstance(row, dict)]
    assert "npc_talk" in interaction_ids
    assert "admin_pay_fines" in interaction_ids
    assert "admin_apply_license" in interaction_ids
    assert "admin_turn_in" in interaction_ids
    assert "admin_mission_board" in interaction_ids
    assert "mission_list" not in interaction_ids
    assert "mission_accept" not in interaction_ids
    assert "bar_hire_crew" not in interaction_ids

    system_id = engine.player_state.current_system_id
    engine.player_state.credits = 500
    engine.player_state.outstanding_fines[system_id] = 200
    result = engine.execute({"type": "npc_interact", "npc_id": admin_id, "interaction_id": "admin_pay_fines"})
    payload = (_stage_detail(result, "npc_interaction") or {}).get("result", {})
    assert payload.get("ok") is True
    assert payload.get("paid") == 200
    assert engine.player_state.credits == 300
    assert engine.player_state.outstanding_fines.get(system_id) == 0
