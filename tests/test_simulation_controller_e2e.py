import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from cli_run import build_simulation  # noqa: E402
from npc_entity import NPCEntity, NPCPersistenceTier  # noqa: E402


def test_simulation_controller_e2e_deterministic_sequence() -> None:
    first = _run_once(seed=4001)
    second = _run_once(seed=4001)
    assert first == second
    assert first["ok"] is True
    event_types = [event.get("event_type") for event in first["events"]]
    assert event_types[:5] == [
        "travel_resolution",
        "enforcement_checkpoint_processed",
        "travel_applied",
        "encounter_generated",
        "encounter_dispatch",
    ]
    assert ("pursuit_resolved" in event_types) or ("combat_resolved" in event_types)
    assert "reward_applied" in event_types
    assert first["events"][-1]["event_type"] == "reward_applied"


def _run_once(seed: int) -> dict:
    controller, world_state = build_simulation(seed)
    sector = world_state["sector"]
    player = world_state["turn_loop"]._player_state  # noqa: SLF001
    target_system = sector.systems[1]
    player.reputation_by_system[target_system.system_id] = 1
    player.heat_by_system[target_system.system_id] = 100
    result = controller.execute(
        {
            "action_type": "travel_to_destination",
            "payload": {
                "target_system_id": target_system.system_id,
                "distance_ly": 1,
                "encounter_action": "attack",
            },
        }
    )
    return result


def test_simulation_controller_travel_path_enforces_wages() -> None:
    controller, world_state = build_simulation(5001)
    player = world_state["turn_loop"]._player_state  # noqa: SLF001
    sector = world_state["sector"]
    target_system = sector.systems[1]
    active_ship = world_state["fleet_by_id"][player.active_ship_id]
    active_ship.crew.append(
        NPCEntity(
            npc_id="NPC-WAGE-1",
            is_crew=True,
            crew_role_id="pilot",
            crew_tags=["crew:pilot"],
            daily_wage=50,
            persistence_tier=NPCPersistenceTier.TIER_2,
        )
    )
    player.credits = 10
    fuel_before = int(active_ship.current_fuel)
    turn_before = world_state["turn_loop"]._time_engine.current_turn  # noqa: SLF001
    system_before = player.current_system_id

    result = controller.execute(
        {
            "action_type": "travel_to_destination",
            "payload": {
                "target_system_id": target_system.system_id,
                "distance_ly": 1,
            },
        }
    )

    assert result["ok"] is True
    assert result["events"][0]["event_type"] == "travel_resolution"
    assert result["events"][0]["success"] is False
    assert result["events"][0]["reason"] == "Insufficient credits to pay crew wages for travel."
    assert len(result["events"]) == 1
    assert player.credits == 10
    assert int(active_ship.current_fuel) == fuel_before
    assert world_state["turn_loop"]._time_engine.current_turn == turn_before  # noqa: SLF001
    assert player.current_system_id == system_before

