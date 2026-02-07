from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from economy_data import CATEGORIES, RESOURCE_PROFILES
from logger import Logger
from world_generator import Sector


AVAILABILITY_STATES: List[str] = ["SCARCE", "LOW", "STABLE", "ABUNDANT", "SURPLUS"]
AVAILABILITY_MODIFIERS: Dict[str, float] = {
    "SCARCE": 1.75,
    "LOW": 1.25,
    "STABLE": 1.00,
    "ABUNDANT": 0.85,
    "SURPLUS": 0.65,
}


@dataclass(frozen=True)
class TradeAction:
    system_id: str
    category_id: str
    delta: int  # +1 for sell, -1 for buy
    cause: str  # player_buy or player_sell


class EconomyEngine:
    def __init__(self, sector: Sector, logger: Logger) -> None:
        self._sector = sector
        self._logger = logger
        self._availability: Dict[str, Dict[str, str]] = {}
        self._prices: Dict[str, Dict[str, float]] = {}
        self._last_cause: Dict[str, Dict[str, str]] = {}
        self._pressure: Dict[str, Dict[str, float]] = {}
        self._init_state()

    def _init_state(self) -> None:
        for system in self._sector.systems:
            self._availability[system.system_id] = {}
            self._prices[system.system_id] = {}
            self._last_cause[system.system_id] = {}
            self._pressure[system.system_id] = {}
            for category in CATEGORIES:
                self._availability[system.system_id][category.category_id] = "STABLE"
                self._prices[system.system_id][category.category_id] = self._price_for(
                    availability="STABLE",
                    category_id=category.category_id,
                )
                self._last_cause[system.system_id][category.category_id] = "production"
                self._pressure[system.system_id][category.category_id] = 0

    def availability(self, system_id: str, category_id: str) -> str:
        return self._availability[system_id][category_id]

    def price(self, system_id: str, category_id: str) -> float:
        return self._prices[system_id][category_id]

    def scarcity_modifier(self, system_id: str, category_id: str) -> float:
        availability = self._availability[system_id][category_id]
        return AVAILABILITY_MODIFIERS[availability]

    def all_prices(self) -> Dict[str, Dict[str, float]]:
        return self._prices

    def category_summary(self, system_id: str) -> Dict[str, Dict[str, float]]:
        profile_id = self._profile_id(system_id)
        profile = RESOURCE_PROFILES[profile_id]
        values: Dict[str, Dict[str, float]] = {}
        for category in CATEGORIES:
            production = profile.production[category.category_id]
            consumption = profile.consumption[category.category_id]
            capacity = max(production, consumption)
            values[category.category_id] = {
                "production": float(production),
                "consumption": float(consumption),
                "capacity": float(capacity),
            }
        return values

    def advance_turn(self, turn: int, trade_action: Optional[TradeAction] = None) -> None:
        trade_delta: Dict[Tuple[str, str], TradeAction] = {}
        if trade_action is not None:
            trade_delta[(trade_action.system_id, trade_action.category_id)] = trade_action

        old_availability = {
            system_id: dict(goods)
            for system_id, goods in self._availability.items()
        }
        old_prices = {system_id: dict(goods) for system_id, goods in self._prices.items()}

        for system in self._sector.systems:
            profile_id = system.attributes.get("profile_id")
            profile = RESOURCE_PROFILES[profile_id]
            for category in CATEGORIES:
                key = (system.system_id, category.category_id)
                trade = trade_delta.get(key)
                production = profile.production[category.category_id]
                consumption = profile.consumption[category.category_id]
                capacity = max(production, consumption)
                pressure_change = production - consumption
                if trade is not None:
                    pressure_change += trade.delta

                self._pressure[system.system_id][category.category_id] += pressure_change
                pressure = self._pressure[system.system_id][category.category_id]
                threshold = capacity * 2
                new_state = self._state_from_pressure(pressure, threshold)
                if new_state != old_availability[system.system_id][category.category_id]:
                    if trade is not None:
                        cause = trade.cause
                    else:
                        cause = "net_positive" if pressure_change > 0 else "net_negative"
                    self._availability[system.system_id][category.category_id] = new_state
                    self._last_cause[system.system_id][category.category_id] = cause

        for system in self._sector.systems:
            for category in CATEGORIES:
                system_id = system.system_id
                category_id = category.category_id
                availability = self._availability[system_id][category_id]
                if availability == old_availability[system_id][category_id]:
                    self._prices[system_id][category_id] = old_prices[system_id][category_id]
                    continue
                new_price = self._price_for(availability=availability, category_id=category_id)
                self._prices[system_id][category_id] = new_price

        for system in self._sector.systems:
            for category in CATEGORIES:
                system_id = system.system_id
                category_id = category.category_id
                old_state = old_availability[system_id][category_id]
                new_state = self._availability[system_id][category_id]
                old_price = old_prices[system_id][category_id]
                new_price = self._prices[system_id][category_id]
                if old_state == new_state and old_price == new_price:
                    continue

                cause = self._last_cause[system_id][category_id]
                self._logger.log(
                    turn=turn,
                    action="economy_update",
                    state_change=(
                        f"system_id={system_id} category_id={category_id} "
                        f"availability {old_state}->{new_state} "
                        f"price {old_price:.2f}->{new_price:.2f} "
                        f"cause={cause}"
                    ),
                )

    def _price_for(self, availability: str, category_id: str) -> float:
        modifier = AVAILABILITY_MODIFIERS[availability]
        base_price = next(c for c in CATEGORIES if c.category_id == category_id).base_price
        return base_price * modifier

    @staticmethod
    def _state_from_pressure(pressure: float, threshold: float) -> str:
        if pressure <= -threshold:
            return "SCARCE"
        if pressure <= -threshold / 2:
            return "LOW"
        if pressure >= threshold:
            return "SURPLUS"
        if pressure >= threshold / 2:
            return "ABUNDANT"
        return "STABLE"

    def _profile_id(self, system_id: str) -> str:
        system = self._sector.get_system(system_id)
        if system is None:
            raise ValueError(f"Unknown system_id: {system_id}")
        profile_id = system.attributes.get("profile_id")
        if profile_id not in RESOURCE_PROFILES:
            raise ValueError(f"Unknown profile_id: {profile_id}")
        return profile_id

    @staticmethod
    def _step_state(state: str, direction: int) -> str:
        index = AVAILABILITY_STATES.index(state)
        new_index = max(0, min(len(AVAILABILITY_STATES) - 1, index + direction))
        return AVAILABILITY_STATES[new_index]
