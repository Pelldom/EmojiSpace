import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from entities import EntityType  # noqa: E402
from mission_entity import MissionEntity  # noqa: E402
from npc_entity import NPCEntity, NPCPersistenceTier  # noqa: E402
from player_state import PlayerState  # noqa: E402
from ship_entity import ShipActivityState, ShipEntity  # noqa: E402


def test_ship_entity_defaults() -> None:
    ship = ShipEntity(
        entity_id="ship-1",
        entity_type=EntityType.OBJECT,
        name="Test Ship",
        emoji=None,
        system_id="SYS-1",
        location_id=None,
    )
    assert ship.ship_id == ""
    assert ship.owner_id == ""
    assert ship.model_id == ""
    assert ship.activity_state == ShipActivityState.INACTIVE
    assert ship.current_location_id is None
    assert ship.current_system_id == ""
    assert ship.physical_cargo_capacity == 0
    assert ship.data_cargo_capacity == 0
    assert ship.physical_cargo_manifest == []
    assert ship.data_cargo_manifest == []
    assert isinstance(asdict(ship), dict)


def test_npc_entity_defaults() -> None:
    npc = NPCEntity(
        entity_id="npc-1",
        entity_type=EntityType.PERSON,
        name="Test NPC",
        emoji=None,
        system_id="SYS-1",
        location_id=None,
    )
    assert npc.npc_id == ""
    assert npc.persistence_tier == NPCPersistenceTier.TIER_1
    assert npc.home_location_id is None
    assert npc.current_location_id is None
    assert npc.current_system_id == ""
    assert isinstance(asdict(npc), dict)


def test_mission_entity_defaults() -> None:
    mission = MissionEntity(
        entity_id="mission-1",
        entity_type=EntityType.OBJECT,
        name="Test Mission",
        emoji=None,
        system_id="SYS-1",
        location_id=None,
    )
    assert mission.mission_id == ""
    assert mission.mission_type == ""
    assert mission.mission_tier == 1
    assert mission.outcome is None
    assert mission.failure_reason is None
    assert mission.related_sku_ids == []
    assert mission.related_event_ids == []
    assert mission.objectives == []
    assert mission.progress == {}
    assert mission.assigned_player_id is None
    assert isinstance(asdict(mission), dict)


def test_player_state_scaffolding_defaults() -> None:
    player = PlayerState(current_system_id="SYS-1")
    assert player.player_id == "player"
    assert player.active_ship_id is None
    assert player.owned_ship_ids == []
    assert player.credits == 0
    assert player.current_system_id == "SYS-1"
    assert player.mission_slots == 1
    assert player.active_missions == []
    assert player.history_timeline == []
    assert isinstance(player.reputation_by_system, dict)
    assert isinstance(player.heat_by_system, dict)
    assert isinstance(player.warrants_by_system, dict)

