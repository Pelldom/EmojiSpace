from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import json
import random

from economy_data import PROFILE_IDS
from data_catalog import DataCatalog, load_data_catalog
from logger import Logger
from market_creation import MarketCreator


@dataclass(frozen=True)
class System:
    system_id: str
    name: str
    attributes: dict
    neighbors: List[str]


@dataclass(frozen=True)
class Sector:
    systems: List[System]

    def system_ids(self) -> List[str]:
        return [system.system_id for system in self.systems]

    def get_system(self, system_id: str) -> Optional[System]:
        for system in self.systems:
            if system.system_id == system_id:
                return system
        return None


class WorldGenerator:
    def __init__(
        self,
        seed: int,
        system_count: int = 5,
        government_ids: List[str] | None = None,
        catalog: DataCatalog | None = None,
        logger: Logger | None = None,
    ) -> None:
        self._seed = seed
        self._system_count = system_count
        self._government_ids = government_ids or []
        self._catalog = catalog or load_data_catalog()
        self._logger = logger

    def generate(self) -> Sector:
        rng = random.Random(self._seed)
        market_creator = MarketCreator(self._catalog, rng, self._logger)
        availability_rules = _load_location_availability()
        base_names = [
            "Aster",
            "Beacon",
            "Cirrus",
            "Drift",
            "Ember",
            "Flux",
            "Gleam",
            "Haven",
            "Ion",
            "Jade",
        ]
        rng.shuffle(base_names)

        profiles = list(PROFILE_IDS)
        rng.shuffle(profiles)

        systems: List[System] = []
        for index in range(self._system_count):
            system_id = f"SYS-{index + 1:03d}"
            name = base_names[index % len(base_names)]
            profile_id = profiles[index % len(profiles)]
            # Population changes require explicit Situation Engine handling.
            population_level = self._weighted_population_level(rng)
            government_id = self._choose_government_id(rng)
            economy_assignment = market_creator.assign_economies(population_level)
            market = market_creator.create_market(
                system_id=system_id,
                population_level=population_level,
                primary_economy=economy_assignment.primary,
                secondary_economies=economy_assignment.secondary,
            )
            available_locations = _evaluate_location_availability(
                availability_rules=availability_rules,
                system_id=system_id,
                system_name=name,
                population_level=population_level,
                government_id=government_id,
                economies=[economy_assignment.primary, *economy_assignment.secondary],
                logger=self._logger,
            )
            attributes = {
                "profile_id": profile_id,
                "population_level": population_level,
                "government_id": government_id,
                "primary_economy": economy_assignment.primary,
                "secondary_economies": list(economy_assignment.secondary),
                "market": market,
                "available_locations": available_locations,
            }
            systems.append(
                System(
                    system_id=system_id,
                    name=name,
                    attributes=attributes,
                    neighbors=[],
                )
            )

        for index, system in enumerate(systems):
            neighbors: List[str] = []
            if index > 0:
                neighbors.append(systems[index - 1].system_id)
            if index < len(systems) - 1:
                neighbors.append(systems[index + 1].system_id)
            systems[index] = System(
                system_id=system.system_id,
                name=system.name,
                attributes=system.attributes,
                neighbors=neighbors,
            )

        return Sector(systems=systems)

    def _choose_government_id(self, rng: random.Random) -> str:
        if not self._government_ids:
            raise ValueError("No government ids available for assignment.")
        government_id = rng.choice(self._government_ids)
        if government_id not in self._government_ids:
            raise ValueError(f"Invalid government id: {government_id}")
        return government_id

    @staticmethod
    def _weighted_population_level(rng: random.Random) -> int:
        weights = {
            1: 10,
            2: 20,
            3: 40,
            4: 20,
            5: 10,
        }
        weighted_levels: List[int] = []
        for level, weight in weights.items():
            weighted_levels.extend([level] * weight)
        if not weighted_levels:
            return 3
        chosen = rng.choice(weighted_levels)
        if chosen not in weights:
            raise ValueError(f"Invalid population level: {chosen}")
        return chosen


def _load_location_availability() -> Dict[str, dict]:
    path = Path(__file__).resolve().parents[1] / "data" / "location_availability.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return data


def _evaluate_location_availability(
    *,
    availability_rules: Dict[str, dict],
    system_id: str,
    system_name: str,
    population_level: int,
    government_id: str,
    economies: List[str],
    logger: Logger | None,
) -> Dict[str, str]:
    results: Dict[str, str] = {}
    for location_type, rules in availability_rules.items():
        if location_type == "datanet":
            results[location_type] = "YES"
            _log_location(
                logger,
                system_id,
                system_name,
                population_level,
                government_id,
                economies,
                location_type,
                "YES",
                "passed",
            )
            continue
        min_population = rules.get("min_population", 0)
        if population_level < min_population:
            results[location_type] = "NO"
            _log_location(
                logger,
                system_id,
                system_name,
                population_level,
                government_id,
                economies,
                location_type,
                "NO",
                "failed population",
            )
            continue
        government_gate = rules.get("government", {})
        government_result = government_gate.get(government_id, "NO")
        if government_result == "NO":
            results[location_type] = "NO"
            _log_location(
                logger,
                system_id,
                system_name,
                population_level,
                government_id,
                economies,
                location_type,
                "NO",
                "failed government",
            )
            continue
        economy_gate = rules.get("economy", {})
        economy_result = _evaluate_economy_gate(economy_gate, economies)
        if economy_result == "NO":
            results[location_type] = "NO"
            _log_location(
                logger,
                system_id,
                system_name,
                population_level,
                government_id,
                economies,
                location_type,
                "NO",
                "failed economy",
            )
            continue
        final_result = "YES"
        if government_result == "LIMITED" or economy_result == "LIMITED":
            final_result = "LIMITED"
        results[location_type] = final_result
        _log_location(
            logger,
            system_id,
            system_name,
            population_level,
            government_id,
            economies,
            location_type,
            final_result,
            f"passed ({final_result})",
        )
    return results


def _evaluate_economy_gate(economy_gate: Dict[str, str], economies: List[str]) -> str:
    if not economies:
        return "NO"
    any_limited = False
    for economy_id in economies:
        result = economy_gate.get(economy_id, "NO")
        if result == "YES":
            return "YES"
        if result == "LIMITED":
            any_limited = True
    return "LIMITED" if any_limited else "NO"


def _log_location(
    logger: Logger | None,
    system_id: str,
    system_name: str,
    population_level: int,
    government_id: str,
    economies: List[str],
    location_type: str,
    result: str,
    reason: str,
) -> None:
    if logger is None:
        return
    logger.log(
        turn=0,
        action="location_availability",
        state_change=(
            f"system_id={system_id} system_name={system_name} "
            f"population={population_level} government={government_id} "
            f"economies={economies} location={location_type} "
            f"result={result} reason={reason}"
        ),
    )
