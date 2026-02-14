import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from npc_entity import NPCEntity, NPCPersistenceTier  # noqa: E402
from ship_entity import ShipEntity  # noqa: E402


def _crew(npc_id: str, role: str, tags: list[str] | None = None) -> NPCEntity:
    return NPCEntity(
        npc_id=npc_id,
        is_crew=True,
        crew_role_id=role,
        crew_tags=list(tags or []),
        persistence_tier=NPCPersistenceTier.TIER_2,
    )


def test_no_crew_capacity_unchanged() -> None:
    ship = ShipEntity(physical_cargo_capacity=12, data_cargo_capacity=4)
    assert ship.get_effective_physical_capacity() == 12
    assert ship.get_effective_data_capacity() == 4


def test_quartermaster_bonus() -> None:
    ship = ShipEntity(
        physical_cargo_capacity=12,
        crew=[_crew("NPC-1", role="quartermaster")],
    )
    assert ship.get_effective_physical_capacity() == 15


def test_science_data_bonus() -> None:
    ship = ShipEntity(
        data_cargo_capacity=4,
        crew=[_crew("NPC-1", role="science")],
    )
    assert ship.get_effective_data_capacity() == 6


def test_multiple_stack() -> None:
    ship = ShipEntity(
        physical_cargo_capacity=10,
        crew=[
            _crew("NPC-1", role="quartermaster"),
            _crew("NPC-2", role="quartermaster"),
        ],
    )
    assert ship.get_effective_physical_capacity() == 16


def test_alien_cargo_stack() -> None:
    ship = ShipEntity(
        physical_cargo_capacity=10,
        tags=["ship_trait_alien"],
        crew=[
            _crew("NPC-1", role="quartermaster", tags=["crew:alien"]),
        ],
    )
    # quartermaster +3, alien synergy +1 from aligned ship tag => +4 total
    assert ship.get_effective_physical_capacity() == 14


def test_no_cap_on_cargo() -> None:
    ship = ShipEntity(
        physical_cargo_capacity=10,
        crew=[
            _crew("NPC-1", role="quartermaster"),
            _crew("NPC-2", role="quartermaster"),
            _crew("NPC-3", role="quartermaster"),
            _crew("NPC-4", role="quartermaster"),
            _crew("NPC-5", role="quartermaster"),
        ],
    )
    assert ship.get_effective_physical_capacity() == 25


def test_deterministic_repeated_calls() -> None:
    ship = ShipEntity(
        physical_cargo_capacity=8,
        data_cargo_capacity=3,
        crew=[
            _crew("NPC-1", role="quartermaster"),
            _crew("NPC-2", role="science"),
            _crew("NPC-3", role="pilot", tags=["crew:organized"]),
        ],
    )
    first_physical = ship.get_effective_physical_capacity()
    first_data = ship.get_effective_data_capacity()
    second_physical = ship.get_effective_physical_capacity()
    second_data = ship.get_effective_data_capacity()
    assert first_physical == second_physical
    assert first_data == second_data
