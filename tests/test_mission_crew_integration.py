import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from mission_entity import MissionEntity  # noqa: E402
from mission_factory import create_mission  # noqa: E402
from mission_manager import MissionManager  # noqa: E402
from npc_entity import NPCEntity, NPCPersistenceTier  # noqa: E402
from player_state import PlayerState  # noqa: E402
from ship_entity import ShipEntity  # noqa: E402


def _crew(npc_id: str, tags: list[str]) -> NPCEntity:
    return NPCEntity(
        npc_id=npc_id,
        is_crew=True,
        crew_role_id="pilot",
        crew_tags=list(tags),
        persistence_tier=NPCPersistenceTier.TIER_2,
    )


def _offer_n(manager: MissionManager, count: int) -> list[str]:
    ids = []
    for idx in range(count):
        mission = MissionEntity(mission_id=f"MIS-{idx}")
        manager.offer(mission)
        ids.append(mission.mission_id)
    return ids


def test_no_crew_baseline_unchanged() -> None:
    manager = MissionManager()
    ids = _offer_n(manager, 2)
    player = PlayerState(mission_slots=1)
    ship = ShipEntity()
    assert manager.accept(ids[0], player, location_type="bar", ship=ship) is True
    assert manager.accept(ids[1], player, location_type="bar", ship=ship) is False


def test_connected_tag_adds_slot_at_bar() -> None:
    manager = MissionManager()
    ids = _offer_n(manager, 2)
    player = PlayerState(mission_slots=1)
    ship = ShipEntity(crew=[_crew("NPC-1", ["crew:connected"])])
    assert manager.accept(ids[0], player, location_type="bar", ship=ship) is True
    assert manager.accept(ids[1], player, location_type="bar", ship=ship) is True


def test_connected_tag_adds_slot_at_administration() -> None:
    manager = MissionManager()
    ids = _offer_n(manager, 2)
    player = PlayerState(mission_slots=1)
    ship = ShipEntity(crew=[_crew("NPC-1", ["crew:connected"])])
    assert manager.accept(ids[0], player, location_type="administration", ship=ship) is True
    assert manager.accept(ids[1], player, location_type="administration", ship=ship) is True


def test_no_effect_at_other_locations() -> None:
    manager = MissionManager()
    ids = _offer_n(manager, 2)
    player = PlayerState(mission_slots=1)
    ship = ShipEntity(crew=[_crew("NPC-1", ["crew:connected"])])
    assert manager.accept(ids[0], player, location_type="market", ship=ship) is True
    assert manager.accept(ids[1], player, location_type="market", ship=ship) is False


def test_stacking_multiple_connected_tags_increases_slots() -> None:
    manager = MissionManager()
    ids = _offer_n(manager, 3)
    player = PlayerState(mission_slots=1)
    ship = ShipEntity(
        crew=[
            _crew("NPC-1", ["crew:connected"]),
            _crew("NPC-2", ["crew:connected"]),
        ]
    )
    assert manager.accept(ids[0], player, location_type="bar", ship=ship) is True
    assert manager.accept(ids[1], player, location_type="bar", ship=ship) is True
    assert manager.accept(ids[2], player, location_type="bar", ship=ship) is True


def test_deterministic_repeated_calls_produce_identical_mission_sets_given_same_seed() -> None:
    def _run_once() -> list[str]:
        manager = MissionManager()
        player = PlayerState(mission_slots=1)
        ship = ShipEntity(crew=[_crew("NPC-1", ["crew:connected"])])
        created = [
            create_mission(
                source_type="npc",
                source_id=f"NPC-{idx}",
                system_id="SYS-1",
                destination_id="DST-1",
                mission_type="delivery",
                mission_tier=1,
            )
            for idx in range(3)
        ]
        # Keep ordering deterministic under fixed input list.
        for mission in created:
            manager.offer(mission)
        accepted = []
        for mission in created:
            if manager.accept(mission.mission_id, player, location_type="bar", ship=ship):
                accepted.append(mission.mission_id)
        return accepted

    first = _run_once()
    second = _run_once()
    assert first == second
