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
    adjusted_risk: float = 0.0
    adjusted_encounter_rate: float = 0.0
    route_id: str = ""
    special: str = ""


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
    world_state_engine: Any | None = None,
    current_system_id: str | None = None,
    route_id: str | None = None,
    route_tags: list[str] | None = None,
    rng: Any | None = None,
    base_risk: float = 0.0,
    base_encounter_rate: float = 0.0,
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

    resolved_route_id = route_id or _default_route_id(inter_system=inter_system, distance_ly=distance_ly)
    tags = [tag for tag in (route_tags or []) if isinstance(tag, str)]
    travel_modifiers = _resolve_travel_world_state_modifiers(
        world_state_engine=world_state_engine,
        current_system_id=current_system_id,
        route_id=resolved_route_id,
        route_tags=tags,
    )

    travel_days = _travel_days(inter_system=inter_system, distance_ly=distance_ly)
    wage_cost = calculate_travel_wage_cost(ship, travel_days)
    adjusted_risk = max(0.0, float(base_risk) * (1.0 + (float(travel_modifiers["travel_risk_percent"]) / 100.0)))
    adjusted_encounter_rate = max(
        0.0, float(base_encounter_rate) * (1.0 + (float(travel_modifiers["encounter_rate_percent"]) / 100.0))
    )

    if player_state is not None:
        if int(player_state.credits) < wage_cost:
            return TravelResult(
                success=False,
                fuel_cost=0,
                current_fuel=int(ship.current_fuel),
                time_advanced=False,
                reason="Insufficient credits to pay crew wages for travel.",
                adjusted_risk=adjusted_risk,
                adjusted_encounter_rate=adjusted_encounter_rate,
                route_id=resolved_route_id,
                special=str(travel_modifiers["special"]),
            )
        player_state.credits = int(player_state.credits) - wage_cost

    base_fuel_cost = compute_fuel_cost(inter_system=inter_system, distance_ly=distance_ly)
    crew_modifiers = compute_crew_modifiers(ship)
    base_fuel_with_crew = base_fuel_cost + int(crew_modifiers.fuel_delta)
    adjusted_fuel = max(
        0.0,
        float(base_fuel_with_crew) * (1.0 + (float(travel_modifiers["fuel_cost_percent"]) / 100.0)),
    )

    special = str(travel_modifiers["special"])
    if special == "unstable_wormhole":
        random_fn = getattr(rng, "random", None) if rng is not None else None
        if callable(random_fn) and float(random_fn()) < 0.5:
            adjusted_fuel = max(0.0, adjusted_fuel * 0.5)
        elif callable(random_fn):
            adjusted_fuel = max(0.0, adjusted_fuel * 1.5)

    fuel_cost = max(1, int(round(adjusted_fuel)))
    if int(ship.current_fuel) < fuel_cost:
        return TravelResult(
            success=False,
            fuel_cost=fuel_cost,
            current_fuel=int(ship.current_fuel),
            time_advanced=False,
            reason="insufficient_fuel",
            adjusted_risk=adjusted_risk,
            adjusted_encounter_rate=adjusted_encounter_rate,
            route_id=resolved_route_id,
            special=special,
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
        adjusted_risk=adjusted_risk,
        adjusted_encounter_rate=adjusted_encounter_rate,
        route_id=resolved_route_id,
        special=special,
    )


def _default_route_id(*, inter_system: bool, distance_ly: int) -> str:
    if inter_system:
        return f"route_ly_{int(distance_ly)}"
    return "route_in_system"


def _resolve_travel_world_state_modifiers(
    *,
    world_state_engine: Any | None,
    current_system_id: str | None,
    route_id: str,
    route_tags: list[str],
) -> dict[str, Any]:
    defaults = {
        "travel_time_percent": 0,
        "travel_risk_percent": 0,
        "encounter_rate_percent": 0,
        "fuel_cost_percent": 0,
        "special": "",
    }
    if world_state_engine is None or not current_system_id:
        return defaults

    resolved = world_state_engine.resolve_modifiers_for_entities(
        current_system_id,
        "travel",
        [
            {
                "entity_id": route_id,
                "category_id": None,
                "tags": list(route_tags),
            }
        ],
    )
    row = resolved.get("resolved", {}).get(route_id, {})

    defaults["travel_time_percent"] = int(row.get("travel_time_percent", row.get("travel_time_delta", 0)))
    defaults["travel_risk_percent"] = int(row.get("travel_risk_percent", row.get("risk_bias_delta", 0)))
    defaults["encounter_rate_percent"] = int(row.get("encounter_rate_percent", 0))
    defaults["fuel_cost_percent"] = int(row.get("fuel_cost_percent", 0))

    special_value = row.get("special", "")
    if isinstance(special_value, str):
        defaults["special"] = special_value
    elif int(row.get("special_flag", 0)) > 0:
        defaults["special"] = "unstable_wormhole"
    return defaults
