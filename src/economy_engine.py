from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from economy_data import GOODS, RESOURCE_PROFILES
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
    good_id: str
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
            for good in GOODS:
                self._availability[system.system_id][good.good_id] = "STABLE"
                self._prices[system.system_id][good.good_id] = self._price_for(
                    availability="STABLE",
                    good_id=good.good_id,
                )
                self._last_cause[system.system_id][good.good_id] = "production"
                self._pressure[system.system_id][good.good_id] = 0

    def availability(self, system_id: str, good_id: str) -> str:
        return self._availability[system_id][good_id]

    def price(self, system_id: str, good_id: str) -> float:
        return self._prices[system_id][good_id]

    def all_prices(self) -> Dict[str, Dict[str, float]]:
        return self._prices

    def population_summary(self, system_id: str) -> tuple[int, float, Dict[str, Dict[str, float]]]:
        profile_id = self._profile_id(system_id)
        profile = RESOURCE_PROFILES[profile_id]
        level = self._population_level(system_id)
        scalar = self._population_scalar(level)
        values: Dict[str, Dict[str, float]] = {}
        for good in GOODS:
            production, consumption, capacity = self._scaled_values(
                system_id=system_id,
                production=profile.production[good.good_id],
                consumption=profile.consumption[good.good_id],
            )
            values[good.good_id] = {
                "production": production,
                "consumption": consumption,
                "capacity": capacity,
            }
        return level, scalar, values

    def advance_turn(self, turn: int, trade_action: Optional[TradeAction] = None) -> None:
        trade_delta: Dict[Tuple[str, str], TradeAction] = {}
        if trade_action is not None:
            trade_delta[(trade_action.system_id, trade_action.good_id)] = trade_action

        old_availability = {
            system_id: dict(goods)
            for system_id, goods in self._availability.items()
        }
        old_prices = {system_id: dict(goods) for system_id, goods in self._prices.items()}

        for system in self._sector.systems:
            profile_id = system.attributes.get("profile_id")
            profile = RESOURCE_PROFILES[profile_id]
            for good in GOODS:
                key = (system.system_id, good.good_id)
                trade = trade_delta.get(key)
                production, consumption, capacity = self._scaled_values(
                    system_id=system.system_id,
                    production=profile.production[good.good_id],
                    consumption=profile.consumption[good.good_id],
                )
                pressure_change = production - consumption
                if trade is not None:
                    pressure_change += trade.delta

                self._pressure[system.system_id][good.good_id] += pressure_change
                pressure = self._pressure[system.system_id][good.good_id]
                threshold = capacity * 2
                new_state = self._state_from_pressure(pressure, threshold)
                if new_state != old_availability[system.system_id][good.good_id]:
                    if trade is not None:
                        cause = trade.cause
                    else:
                        cause = "net_positive" if pressure_change > 0 else "net_negative"
                    self._availability[system.system_id][good.good_id] = new_state
                    self._last_cause[system.system_id][good.good_id] = cause

        for system in self._sector.systems:
            for good in GOODS:
                system_id = system.system_id
                good_id = good.good_id
                availability = self._availability[system_id][good_id]
                if availability == old_availability[system_id][good_id]:
                    self._prices[system_id][good_id] = old_prices[system_id][good_id]
                    continue
                new_price = self._price_for(availability=availability, good_id=good_id)
                self._prices[system_id][good_id] = new_price

        for system in self._sector.systems:
            for good in GOODS:
                system_id = system.system_id
                good_id = good.good_id
                old_state = old_availability[system_id][good_id]
                new_state = self._availability[system_id][good_id]
                old_price = old_prices[system_id][good_id]
                new_price = self._prices[system_id][good_id]
                if old_state == new_state and old_price == new_price:
                    continue

                cause = self._last_cause[system_id][good_id]
                self._logger.log(
                    turn=turn,
                    action="economy_update",
                    state_change=(
                        f"system_id={system_id} good_id={good_id} "
                        f"availability {old_state}->{new_state} "
                        f"price {old_price:.2f}->{new_price:.2f} "
                        f"cause={cause}"
                    ),
                )

    def _price_for(self, availability: str, good_id: str) -> float:
        modifier = AVAILABILITY_MODIFIERS[availability]
        base_price = next(g for g in GOODS if g.good_id == good_id).base_price
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

    def _scaled_values(
        self,
        system_id: str,
        production: int,
        consumption: int,
    ) -> tuple[float, float, float]:
        population_level = self._population_level(system_id)
        scalar = self._population_scalar(population_level)
        scaled_production = production * scalar
        scaled_consumption = consumption * scalar
        base_capacity = max(production, consumption)
        scaled_capacity = base_capacity * scalar
        return scaled_production, scaled_consumption, scaled_capacity

    def _population_level(self, system_id: str) -> int:
        system = self._sector.get_system(system_id)
        if system is None:
            raise ValueError(f"Unknown system_id: {system_id}")
        level = system.attributes.get("population_level", 3)
        if level not in (0, 1, 2, 3, 4, 5):
            raise ValueError(f"Invalid population level: {level}")
        return level

    def _profile_id(self, system_id: str) -> str:
        system = self._sector.get_system(system_id)
        if system is None:
            raise ValueError(f"Unknown system_id: {system_id}")
        profile_id = system.attributes.get("profile_id")
        if profile_id not in RESOURCE_PROFILES:
            raise ValueError(f"Unknown profile_id: {profile_id}")
        return profile_id

    @staticmethod
    def _population_scalar(level: int) -> float:
        table = {
            0: 0.0,
            1: 0.25,
            2: 0.50,
            3: 1.00,
            4: 1.75,
            5: 2.50,
        }
        return table[level]

    @staticmethod
    def _step_state(state: str, direction: int) -> str:
        index = AVAILABILITY_STATES.index(state)
        new_index = max(0, min(len(AVAILABILITY_STATES) - 1, index + direction))
        return AVAILABILITY_STATES[new_index]
