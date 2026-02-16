import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from npc_entity import NPCEntity, NPCPersistenceTier  # noqa: E402
from ship_entity import ShipActivityState, ShipEntity  # noqa: E402


def test_npc_entity_backward_compatible_non_crew_payload() -> None:
    payload = {
        "npc_id": "NPC-legacy",
        "persistence_tier": 1,
        "display_name": "Legacy NPC",
    }
    npc = NPCEntity.from_dict(payload)
    assert npc.is_crew is False
    assert npc.crew_role_id is None
    assert npc.crew_tags == []
    assert npc.hire_cost == 0
    assert npc.daily_wage == 0


def test_npc_entity_crew_validation_requires_tier2_and_role() -> None:
    with pytest.raises(ValueError):
        NPCEntity(is_crew=True, crew_role_id="pilot", persistence_tier=NPCPersistenceTier.TIER_1)

    with pytest.raises(ValueError):
        NPCEntity(is_crew=True, crew_role_id=None, persistence_tier=NPCPersistenceTier.TIER_2)

    with pytest.raises(ValueError):
        NPCEntity(is_crew=True, crew_role_id="pilot", persistence_tier=NPCPersistenceTier.TIER_2, crew_tags=["pilot"])


def test_ship_entity_add_remove_and_wages_respect_capacity() -> None:
    ship = ShipEntity(activity_state=ShipActivityState.ACTIVE, crew_capacity=1, fuel_capacity=10, current_fuel=10)
    crew_npc = NPCEntity(
        npc_id="NPC-crew-1",
        is_crew=True,
        crew_role_id="pilot",
        crew_tags=["crew:pilot"],
        persistence_tier=NPCPersistenceTier.TIER_2,
        daily_wage=7,
    )
    ship.add_crew(crew_npc)
    assert len(ship.crew) == 1
    assert ship.get_total_daily_wages() == 7

    with pytest.raises(ValueError):
        ship.add_crew(
            NPCEntity(
                npc_id="NPC-crew-2",
                is_crew=True,
                crew_role_id="gunner",
                crew_tags=["crew:gunner"],
                persistence_tier=NPCPersistenceTier.TIER_2,
                daily_wage=5,
            )
        )

    ship.remove_crew("NPC-crew-1")
    assert ship.crew == []
    assert ship.get_total_daily_wages() == 0


def test_ship_entity_serialization_embeds_crew_payloads() -> None:
    ship = ShipEntity(activity_state=ShipActivityState.ACTIVE, crew_capacity=2, fuel_capacity=5, current_fuel=5)
    ship.add_crew(
        NPCEntity(
            npc_id="NPC-crew-3",
            is_crew=True,
            crew_role_id="engineer",
            crew_tags=["crew:engineer"],
            persistence_tier=NPCPersistenceTier.TIER_2,
            daily_wage=6,
        )
    )
    payload = ship.to_dict()
    restored = ShipEntity.from_dict(payload)
    assert len(restored.crew) == 1
    assert restored.crew[0].npc_id == "NPC-crew-3"
    assert restored.crew[0].crew_role_id == "engineer"
