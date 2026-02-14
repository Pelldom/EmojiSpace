import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from npc_entity import NPCEntity, NPCPersistenceTier  # noqa: E402
from player_state import PlayerState  # noqa: E402
from ship_entity import ShipEntity  # noqa: E402
from travel_resolution import calculate_travel_wage_cost, resolve_travel  # noqa: E402


def _crew(npc_id: str, role: str, daily_wage: int) -> NPCEntity:
    return NPCEntity(
        npc_id=npc_id,
        is_crew=True,
        crew_role_id=role,
        crew_tags=[f"crew:{role}"],
        daily_wage=daily_wage,
        persistence_tier=NPCPersistenceTier.TIER_2,
    )


def test_no_crew_no_wage_deduction() -> None:
    ship = ShipEntity(fuel_capacity=20, current_fuel=20)
    player = PlayerState(credits=100)
    result = resolve_travel(ship=ship, inter_system=True, distance_ly=2, player_state=player)
    assert result.success is True
    assert player.credits == 100


def test_single_day_travel_deducts_correct_wage() -> None:
    ship = ShipEntity(
        fuel_capacity=20,
        current_fuel=20,
        crew=[_crew("NPC-1", "pilot", daily_wage=5)],
    )
    player = PlayerState(credits=100)
    result = resolve_travel(ship=ship, inter_system=False, distance_ly=99, player_state=player)
    assert result.success is True
    assert player.credits == 95


def test_multi_day_travel_deducts_wage_times_days() -> None:
    ship = ShipEntity(
        fuel_capacity=20,
        current_fuel=20,
        crew=[_crew("NPC-1", "pilot", daily_wage=4)],
    )
    player = PlayerState(credits=100)
    result = resolve_travel(ship=ship, inter_system=True, distance_ly=3, player_state=player)
    assert result.success is True
    assert player.credits == 88


def test_insufficient_funds_blocks_travel_no_fuel_deducted() -> None:
    ship = ShipEntity(
        fuel_capacity=20,
        current_fuel=20,
        crew=[_crew("NPC-1", "pilot", daily_wage=5)],
    )
    player = PlayerState(credits=4)
    result = resolve_travel(ship=ship, inter_system=False, distance_ly=1, player_state=player)
    assert result.success is False
    assert result.reason == "Insufficient credits to pay crew wages for travel."
    assert ship.current_fuel == 20
    assert player.credits == 4


def test_wages_deducted_before_fuel() -> None:
    ship = ShipEntity(
        fuel_capacity=20,
        current_fuel=20,
        crew=[_crew("NPC-1", "pilot", daily_wage=5)],
    )
    player = PlayerState(credits=100)
    result = resolve_travel(ship=ship, inter_system=True, distance_ly=2, player_state=player)
    assert result.success is True
    assert player.credits == 90
    assert ship.current_fuel == 18


def test_deterministic_repeated_call_behavior() -> None:
    ship_a = ShipEntity(
        fuel_capacity=20,
        current_fuel=20,
        crew=[_crew("NPC-1", "navigator", daily_wage=6)],
    )
    player_a = PlayerState(credits=100)
    ship_b = ShipEntity(
        fuel_capacity=20,
        current_fuel=20,
        crew=[_crew("NPC-1", "navigator", daily_wage=6)],
    )
    player_b = PlayerState(credits=100)

    first = resolve_travel(ship=ship_a, inter_system=True, distance_ly=2, player_state=player_a)
    second = resolve_travel(ship=ship_b, inter_system=True, distance_ly=2, player_state=player_b)

    assert first.success == second.success
    assert first.fuel_cost == second.fuel_cost
    assert first.current_fuel == second.current_fuel
    assert player_a.credits == player_b.credits


def test_zero_crew_always_zero_wage_cost() -> None:
    ship = ShipEntity()
    assert calculate_travel_wage_cost(ship, travel_days=1) == 0
    assert calculate_travel_wage_cost(ship, travel_days=4) == 0
