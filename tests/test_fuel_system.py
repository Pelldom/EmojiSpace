import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from interaction_layer import destination_actions, execute_refuel  # noqa: E402
from ship_assembler import assemble_ship  # noqa: E402
from ship_entity import ShipEntity  # noqa: E402
from travel_resolution import resolve_travel  # noqa: E402


def test_fuel_capacity_calculation() -> None:
    assembled = assemble_ship(
        "civ_t1_midge",
        [{"module_id": "ship_utility_extra_fuel_mk1"}],
    )
    assert assembled["fuel_capacity"] == 15


def test_initial_fuel_full() -> None:
    ship = ShipEntity(fuel_capacity=18)
    assert ship.current_fuel == 18


def test_travel_consumes_fuel() -> None:
    ship = ShipEntity(fuel_capacity=20, current_fuel=20)
    ticks = {"count": 0}

    def _advance() -> int:
        ticks["count"] += 1
        return ticks["count"]

    inter = resolve_travel(ship=ship, inter_system=True, distance_ly=3, advance_time=_advance)
    intra = resolve_travel(ship=ship, inter_system=False, distance_ly=999, advance_time=_advance)
    assert inter.success is True
    assert intra.success is True
    assert ship.current_fuel == 16
    assert ticks["count"] == 2


def test_travel_rejected_if_insufficient_fuel() -> None:
    ship = ShipEntity(fuel_capacity=2, current_fuel=1)
    ticks = {"count": 0}

    def _advance() -> int:
        ticks["count"] += 1
        return ticks["count"]

    result = resolve_travel(ship=ship, inter_system=True, distance_ly=2, advance_time=_advance)
    assert result.success is False
    assert result.reason == "insufficient_fuel"
    assert ship.current_fuel == 1
    assert ticks["count"] == 0


def test_refuel_partial_and_full() -> None:
    ship = ShipEntity(fuel_capacity=20, current_fuel=10)
    partial = execute_refuel(ship=ship, player_credits=100, requested_units=3)
    assert partial["ok"] is True
    assert partial["units_purchased"] == 3
    assert partial["total_cost"] == 15
    assert partial["credits"] == 85
    assert ship.current_fuel == 13

    full = execute_refuel(ship=ship, player_credits=1000, requested_units=None)
    assert full["ok"] is True
    assert full["units_purchased"] == 7
    assert full["total_cost"] == 35
    assert full["credits"] == 965
    assert ship.current_fuel == 20


def test_refuel_requires_datanet() -> None:
    with_datanet = {"locations": [{"location_type": "market"}, {"location_type": "datanet"}]}
    without_datanet = {"locations": [{"location_type": "market"}]}
    assert "refuel" in destination_actions(with_datanet, base_actions=["ignore"])
    assert "refuel" not in destination_actions(without_datanet, base_actions=["ignore"])
