import random
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from player_state import PlayerState  # noqa: E402
from ship_entity import ShipEntity  # noqa: E402
from travel_resolution import resolve_travel  # noqa: E402


class _StubWorldStateEngine:
    def __init__(self, row: dict[str, int | str]) -> None:
        self._row = dict(row)

    def resolve_modifiers_for_entities(self, system_id, domain, entity_views):
        assert domain == "travel"
        route_id = entity_views[0]["entity_id"]
        return {"domain": domain, "system_id": system_id, "resolved": {route_id: dict(self._row)}}


def _make_ship() -> ShipEntity:
    return ShipEntity(fuel_capacity=20, current_fuel=20)


def test_baseline_unchanged_when_world_state_none() -> None:
    ship = _make_ship()
    player = PlayerState(credits=100)
    result = resolve_travel(
        ship=ship,
        inter_system=True,
        distance_ly=2,
        player_state=player,
        world_state_engine=None,
        current_system_id="SYS-1",
        route_id="ROUTE-A",
        base_risk=0.2,
        base_encounter_rate=0.4,
    )
    assert result.success is True
    assert result.fuel_cost == 2
    assert result.adjusted_risk == 0.2
    assert result.adjusted_encounter_rate == 0.4


def test_positive_travel_risk_percent_increases_risk_deterministically() -> None:
    ws = _StubWorldStateEngine({"travel_risk_percent": 50})
    ship = _make_ship()
    result = resolve_travel(
        ship=ship,
        inter_system=True,
        distance_ly=1,
        world_state_engine=ws,
        current_system_id="SYS-1",
        route_id="ROUTE-RISK",
        base_risk=0.2,
    )
    assert result.adjusted_risk == pytest.approx(0.3)


def test_negative_travel_risk_percent_floors_at_zero() -> None:
    ws = _StubWorldStateEngine({"travel_risk_percent": -200})
    ship = _make_ship()
    result = resolve_travel(
        ship=ship,
        inter_system=True,
        distance_ly=1,
        world_state_engine=ws,
        current_system_id="SYS-1",
        route_id="ROUTE-RISK-NEG",
        base_risk=0.2,
    )
    assert result.adjusted_risk == 0.0


def test_encounter_rate_percent_adjusts_encounter_probability() -> None:
    ws = _StubWorldStateEngine({"encounter_rate_percent": 25})
    ship = _make_ship()
    result = resolve_travel(
        ship=ship,
        inter_system=True,
        distance_ly=1,
        world_state_engine=ws,
        current_system_id="SYS-1",
        route_id="ROUTE-ENC",
        base_encounter_rate=0.4,
    )
    assert result.adjusted_encounter_rate == 0.5


def test_deterministic_results_across_identical_runs() -> None:
    ws = _StubWorldStateEngine({"fuel_cost_percent": 10, "special": "unstable_wormhole"})

    def _run_once():
        ship = _make_ship()
        return resolve_travel(
            ship=ship,
            inter_system=True,
            distance_ly=2,
            world_state_engine=ws,
            current_system_id="SYS-1",
            route_id="ROUTE-DET",
            rng=random.Random(123),
            base_risk=0.1,
            base_encounter_rate=0.2,
        )

    first = _run_once()
    second = _run_once()
    assert first.fuel_cost == second.fuel_cost
    assert first.adjusted_risk == second.adjusted_risk
    assert first.adjusted_encounter_rate == second.adjusted_encounter_rate


def test_no_change_to_travel_duration_behavior() -> None:
    ticks = {"count": 0}

    def _advance():
        ticks["count"] += 1
        return ticks["count"]

    ship = _make_ship()
    result = resolve_travel(
        ship=ship,
        inter_system=True,
        distance_ly=3,
        advance_time=_advance,
    )
    assert result.success is True
    assert result.time_advanced is True
    assert ticks["count"] == 1
