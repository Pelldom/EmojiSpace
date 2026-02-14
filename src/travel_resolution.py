from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from crew_modifiers import compute_crew_modifiers


@dataclass(frozen=True)
class TravelResult:
    success: bool
    fuel_cost: int
    current_fuel: int
    time_advanced: bool
    reason: str


def compute_fuel_cost(*, inter_system: bool, distance_ly: int) -> int:
    if inter_system:
        if distance_ly < 0:
            raise ValueError("distance_ly must be >= 0.")
        return int(distance_ly)
    return 1


def calculate_travel_wage_cost(ship, travel_days: int) -> int:
    if travel_days < 0:
        raise ValueError("travel_days must be >= 0.")
    return int(ship.get_total_daily_wages()) * int(travel_days)


def _travel_days(*, inter_system: bool, distance_ly: int) -> int:
    if inter_system:
        if distance_ly < 0:
            raise ValueError("distance_ly must be >= 0.")
        return max(1, int(distance_ly))
    return 1


def resolve_travel(
    *,
    ship,
    inter_system: bool,
    distance_ly: int,
    emergency_transport: bool = False,
    advance_time: Callable[[], int] | None = None,
    player_state: Any | None = None,
) -> TravelResult:
    if emergency_transport:
        if advance_time is not None:
            advance_time()
        return TravelResult(
            success=True,
            fuel_cost=0,
            current_fuel=int(ship.current_fuel),
            time_advanced=advance_time is not None,
            reason="emergency_transport",
        )

    travel_days = _travel_days(inter_system=inter_system, distance_ly=distance_ly)
    wage_cost = calculate_travel_wage_cost(ship, travel_days)
    if player_state is not None:
        if int(player_state.credits) < wage_cost:
            return TravelResult(
                success=False,
                fuel_cost=0,
                current_fuel=int(ship.current_fuel),
                time_advanced=False,
                reason="Insufficient credits to pay crew wages for travel.",
            )
        player_state.credits = int(player_state.credits) - wage_cost

    base_fuel_cost = compute_fuel_cost(inter_system=inter_system, distance_ly=distance_ly)
    crew_modifiers = compute_crew_modifiers(ship)
    fuel_cost = max(1, base_fuel_cost + int(crew_modifiers.fuel_delta))
    if int(ship.current_fuel) < fuel_cost:
        return TravelResult(
            success=False,
            fuel_cost=fuel_cost,
            current_fuel=int(ship.current_fuel),
            time_advanced=False,
            reason="insufficient_fuel",
        )

    ship.current_fuel = int(ship.current_fuel) - fuel_cost
    if advance_time is not None:
        advance_time()
    return TravelResult(
        success=True,
        fuel_cost=fuel_cost,
        current_fuel=int(ship.current_fuel),
        time_advanced=advance_time is not None,
        reason="ok",
    )
