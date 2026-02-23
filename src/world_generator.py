from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib
import json
import math
import random

from economy_data import PROFILE_IDS
from data_catalog import DataCatalog, load_data_catalog
from logger import Logger
from market import Market
from market_creation import MarketCreator


@dataclass(frozen=True)
class Location:
    location_id: str
    destination_id: str
    location_type: str
    enabled: bool
    notes: str | None = None


@dataclass(frozen=True)
class Destination:
    destination_id: str
    system_id: str
    destination_type: str
    display_name: str
    population: int
    primary_economy_id: str | None
    secondary_economy_ids: List[str]
    locations: List[Location]
    market: Market | None
    tags: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class System:
    system_id: str
    name: str
    position: Tuple[int, int]
    population: int
    government_id: str
    destinations: List[Destination]
    # Derived compatibility fields may exist inside attributes["market"/"primary_economy"/"secondary_economies"].
    # These are not authoritative and should not be used by new logic.
    attributes: dict
    neighbors: List[str]
    x: float = 0.0
    y: float = 0.0


@dataclass(frozen=True)
class Galaxy:
    systems: List[System]

    def system_ids(self) -> List[str]:
        return [system.system_id for system in self.systems]

    def get_system(self, system_id: str) -> Optional[System]:
        for system in self.systems:
            if system.system_id == system_id:
                return system
        return None


class Sector(Galaxy):
    pass


class WorldGenerator:
    GALAXY_RADIUS = 100.0

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

    def generate(self) -> Galaxy:
        rng = random.Random(self._seed)
        availability_rules = _load_location_availability()
        names_data = _load_names()
        system_names = list(names_data["systems"])
        rng.shuffle(system_names)

        profiles = list(PROFILE_IDS)
        rng.shuffle(profiles)

        systems: List[System] = []
        for index in range(self._system_count):
            system_id = f"SYS-{index + 1:03d}"
            name = system_names[index % len(system_names)]
            profile_id = profiles[index % len(profiles)]
            # Population changes require explicit Situation Engine handling.
            population_level = self._weighted_population_level(rng)
            government_id = self._choose_government_id(rng)
            position = (index, 0)
            destinations = _generate_destinations(
                seed=self._seed,
                system_id=system_id,
                system_name=name,
                system_population=population_level,
                government_id=government_id,
                catalog=self._catalog,
                availability_rules=availability_rules,
                logger=self._logger,
                names_data=names_data,
            )
            primary_market = _first_destination_market(destinations)
            primary_economy, secondary_economies = _first_destination_economies(destinations)
            attributes = {
                "profile_id": profile_id,
                "population_level": population_level,
                "government_id": government_id,
                "destinations": destinations,
                # Deprecated compatibility shim. Do not use for new logic.
                # Derived fields only. Not authoritative.
                # TODO(Phase 3.x): Remove once all callers are destination-scoped.
                "market": primary_market,
                "primary_economy": primary_economy,
                "secondary_economies": secondary_economies,
            }
            systems.append(
                System(
                    system_id=system_id,
                    name=name,
                    position=position,
                    population=population_level,
                    government_id=government_id,
                    destinations=destinations,
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
                position=system.position,
                population=system.population,
                government_id=system.government_id,
                destinations=system.destinations,
                attributes=system.attributes,
                neighbors=neighbors,
                x=system.x,
                y=system.y,
            )

        systems = self._assign_spatial_coordinates(systems)
        return Galaxy(systems=systems)

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

    def _assign_spatial_coordinates(self, systems: List[System]) -> List[System]:
        by_id = {system.system_id: system for system in systems}
        updated: Dict[str, System] = {}
        for system_id in sorted(by_id):
            system = by_id[system_id]
            x, y = _deterministic_system_coordinates(
                world_seed=self._seed,
                system_id=system_id,
                stream_name="world_spatial_coordinates",
                radius=float(self.GALAXY_RADIUS),
            )
            updated[system_id] = System(
                system_id=system.system_id,
                name=system.name,
                position=system.position,
                population=system.population,
                government_id=system.government_id,
                destinations=system.destinations,
                attributes=system.attributes,
                neighbors=system.neighbors,
                x=float(x),
                y=float(y),
            )
        return [updated[system.system_id] for system in systems]


def _load_location_availability() -> Dict[str, dict]:
    path = Path(__file__).resolve().parents[1] / "data" / "location_availability.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return data


def _load_names() -> Dict[str, List[str]]:
    """Load system, planet, and station names from data/names.json."""
    path = Path(__file__).resolve().parents[1] / "data" / "names.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {
            "systems": list(data.get("systems", [])),
            "planets": list(data.get("planets", [])),
            "stations": list(data.get("stations", [])),
        }
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to hardcoded names if file missing
        return {
            "systems": ["Aster", "Beacon", "Cirrus", "Drift", "Ember", "Flux", "Gleam", "Haven", "Ion", "Jade"],
            "planets": ["Terra", "Mars", "Venus", "Jupiter", "Saturn"],
            "stations": ["Orbital", "Deep", "Space", "Outpost", "Hub"],
        }


def _generate_destinations(
    *,
    seed: int,
    system_id: str,
    system_name: str,
    system_population: int,
    government_id: str,
    catalog: DataCatalog,
    availability_rules: Dict[str, dict],
    logger: Logger | None,
    names_data: Dict[str, List[str]],
) -> List[Destination]:
    destinations: List[Destination] = []
    
    # Deterministic counts for each destination type
    planet_rng = _seeded_rng(seed, "dst_planet_count", system_id)
    station_rng = _seeded_rng(seed, "dst_station_count", system_id)
    explorable_rng = _seeded_rng(seed, "dst_explorable_count", system_id)
    mining_rng = _seeded_rng(seed, "dst_mining_count", system_id)
    
    planet_count = planet_rng.randint(2, 4)
    station_count = station_rng.randint(1, 2)
    explorable_count = explorable_rng.randint(0, 2)
    mining_count = mining_rng.randint(0, 2)
    
    # Shuffle name lists deterministically per system
    planet_names = list(names_data["planets"])
    station_names = list(names_data["stations"])
    planet_name_rng = _seeded_rng(seed, "planet_names", system_id)
    station_name_rng = _seeded_rng(seed, "station_names", system_id)
    planet_name_rng.shuffle(planet_names)
    station_name_rng.shuffle(station_names)
    
    destination_index = 1
    
    # Generate planets (population centers)
    for i in range(planet_count):
        destination_id = f"{system_id}-DST-{destination_index:02d}"
        destination_index += 1
        display_name = planet_names[i % len(planet_names)]
        destination_type = "planet"
        population = _destination_population(
            seed=seed,
            system_id=system_id,
            destination_id=destination_id,
            destination_type=destination_type,
            system_population=system_population,
        )
        primary_economy_id: str | None = None
        secondary_economy_ids: List[str] = []
        market: Market | None = None
        if population >= 1:
            assignment_rng = _seeded_rng(seed, "economies", system_id, destination_id)
            market_creator = MarketCreator(catalog, assignment_rng, logger)
            economy_assignment = market_creator.assign_economies(population)
            primary_economy_id = economy_assignment.primary
            secondary_economy_ids = list(economy_assignment.secondary)
            from interaction_resolvers import destination_has_shipdock_service
            temp_dest = Destination(
                destination_id=destination_id,
                system_id=system_id,
                destination_type=destination_type,
                display_name=display_name,
                population=population,
                primary_economy_id=primary_economy_id,
                secondary_economy_ids=secondary_economy_ids,
                locations=[],
                market=None,
            )
            has_shipdock = destination_has_shipdock_service(temp_dest)
            market = market_creator.create_market(
                destination_id=destination_id,
                population_level=population,
                primary_economy=primary_economy_id,
                secondary_economies=secondary_economy_ids,
                world_seed=seed,
                has_shipdock=has_shipdock,
            )
        destination = Destination(
            destination_id=destination_id,
            system_id=system_id,
            destination_type=destination_type,
            display_name=display_name,
            population=population,
            primary_economy_id=primary_economy_id,
            secondary_economy_ids=secondary_economy_ids,
            locations=[],
            market=market,
        )
        destinations.append(destination)
    
    # Generate stations (population centers)
    for i in range(station_count):
        destination_id = f"{system_id}-DST-{destination_index:02d}"
        destination_index += 1
        display_name = station_names[i % len(station_names)]
        destination_type = "station"
        population = _destination_population(
            seed=seed,
            system_id=system_id,
            destination_id=destination_id,
            destination_type=destination_type,
            system_population=system_population,
        )
        primary_economy_id: str | None = None
        secondary_economy_ids: List[str] = []
        market: Market | None = None
        if population >= 1:
            assignment_rng = _seeded_rng(seed, "economies", system_id, destination_id)
            market_creator = MarketCreator(catalog, assignment_rng, logger)
            economy_assignment = market_creator.assign_economies(population)
            primary_economy_id = economy_assignment.primary
            secondary_economy_ids = list(economy_assignment.secondary)
            from interaction_resolvers import destination_has_shipdock_service
            temp_dest = Destination(
                destination_id=destination_id,
                system_id=system_id,
                destination_type=destination_type,
                display_name=display_name,
                population=population,
                primary_economy_id=primary_economy_id,
                secondary_economy_ids=secondary_economy_ids,
                locations=[],
                market=None,
            )
            has_shipdock = destination_has_shipdock_service(temp_dest)
            market = market_creator.create_market(
                destination_id=destination_id,
                population_level=population,
                primary_economy=primary_economy_id,
                secondary_economies=secondary_economy_ids,
                world_seed=seed,
                has_shipdock=has_shipdock,
            )
        destination = Destination(
            destination_id=destination_id,
            system_id=system_id,
            destination_type=destination_type,
            display_name=display_name,
            population=population,
            primary_economy_id=primary_economy_id,
            secondary_economy_ids=secondary_economy_ids,
            locations=[],
            market=market,
        )
        destinations.append(destination)
    
    # Generate explorable stubs (no population, no markets)
    for i in range(explorable_count):
        destination_id = f"{system_id}-DST-{destination_index:02d}"
        destination_index += 1
        display_name = f"Explorable Site {i + 1}"
        destination_type = "explorable_stub"
        destination = Destination(
            destination_id=destination_id,
            system_id=system_id,
            destination_type=destination_type,
            display_name=display_name,
            population=0,
            primary_economy_id=None,
            secondary_economy_ids=[],
            locations=[],
            market=None,
        )
        destinations.append(destination)
    
    # Generate mining stubs (no population, no markets)
    for i in range(mining_count):
        destination_id = f"{system_id}-DST-{destination_index:02d}"
        destination_index += 1
        display_name = f"Mining Site {i + 1}"
        destination_type = "mining_stub"
        destination = Destination(
            destination_id=destination_id,
            system_id=system_id,
            destination_type=destination_type,
            display_name=display_name,
            population=0,
            primary_economy_id=None,
            secondary_economy_ids=[],
            locations=[],
            market=None,
        )
        destinations.append(destination)

    destinations = _assign_locations_and_markets(
        seed=seed,
        system_id=system_id,
        system_name=system_name,
        government_id=government_id,
        destinations=destinations,
        availability_rules=availability_rules,
        catalog=catalog,
        logger=logger,
    )
    return destinations


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


def _assign_locations_and_markets(
    *,
    seed: int,
    system_id: str,
    system_name: str,
    government_id: str,
    destinations: List[Destination],
    availability_rules: Dict[str, dict],
    catalog: DataCatalog,
    logger: Logger | None,
) -> List[Destination]:
    destinations_by_id = {destination.destination_id: destination for destination in destinations}
    placed_locations: Dict[str, set[str]] = {destination.destination_id: set() for destination in destinations}

    for destination in destinations:
        if destination.population <= 0:
            continue
        _add_location_if_missing(
            destination,
            placed_locations,
            location_type="datanet",
            enabled=True,
            notes="population-gated destination access",
        )

    for location_type, rules in availability_rules.items():
        if location_type == "datanet":
            continue
        eligible, system_result = _eligible_destinations_for_location(
            destinations=destinations,
            rules=rules,
            government_id=government_id,
        )
        if system_result == "NO":
            _log_location(
                logger,
                system_id,
                system_name,
                None,
                government_id,
                None,
                location_type,
                "NO",
                "no eligible destinations",
            )
            continue
        if system_result == "YES":
            for destination in eligible:
                _add_location_if_missing(destination, placed_locations, location_type, True, None)
            _log_location(
                logger,
                system_id,
                system_name,
                None,
                government_id,
                None,
                location_type,
                "YES",
                f"placed={len(eligible)} destinations",
            )
        elif system_result == "LIMITED":
            chosen = _choose_limited_destination(seed, system_id, location_type, eligible)
            if chosen is None:
                _log_location(
                    logger,
                    system_id,
                    system_name,
                    None,
                    government_id,
                    None,
                    location_type,
                    "NO",
                    "limited with no eligible destinations",
                )
            else:
                _add_location_if_missing(chosen, placed_locations, location_type, True, "limited placement")
                _log_location(
                    logger,
                    system_id,
                    system_name,
                    None,
                    government_id,
                    None,
                    location_type,
                    "LIMITED",
                    f"placed destination_id={chosen.destination_id}",
                )

    updated_destinations: List[Destination] = []
    for destination in destinations:
        market = destination.market
        if destination.population >= 1 and _destination_has_location(destination, "market"):
            assignment_rng = _seeded_rng(seed, "market", destination.destination_id)
            market_creator = MarketCreator(catalog, assignment_rng, logger)
            if destination.primary_economy_id is None:
                raise ValueError(f"Destination {destination.destination_id} missing primary economy.")
            market = market_creator.create_market(
                destination_id=destination.destination_id,
                population_level=destination.population,
                primary_economy=destination.primary_economy_id,
                secondary_economies=destination.secondary_economy_ids,
                world_seed=seed,
            )
        updated_destinations.append(
            Destination(
                destination_id=destination.destination_id,
                system_id=destination.system_id,
                destination_type=destination.destination_type,
                display_name=destination.display_name,
                population=destination.population,
                primary_economy_id=destination.primary_economy_id,
                secondary_economy_ids=list(destination.secondary_economy_ids),
                locations=list(destination.locations),
                market=market,
                tags=list(destination.tags),
            )
        )
    return updated_destinations


def _eligible_destinations_for_location(
    *,
    destinations: List[Destination],
    rules: dict,
    government_id: str,
) -> tuple[List[Destination], str]:
    eligible: List[Destination] = []
    any_yes = False
    any_limited = False
    min_population = rules.get("min_population", 0)
    government_gate = rules.get("government", {})
    economy_gate = rules.get("economy", {})
    government_result = government_gate.get(government_id, "NO")
    for destination in destinations:
        if destination.population < min_population:
            continue
        if government_result == "NO":
            continue
        economies = _destination_economies(destination)
        economy_result = _evaluate_economy_gate(economy_gate, economies)
        if economy_result == "NO":
            continue
        if government_result == "YES" or economy_result == "YES":
            any_yes = True
        if government_result == "LIMITED" or economy_result == "LIMITED":
            any_limited = True
        eligible.append(destination)
    if any_yes:
        return eligible, "YES"
    if any_limited:
        return eligible, "LIMITED"
    return [], "NO"


def _choose_limited_destination(
    seed: int,
    system_id: str,
    location_type: str,
    eligible: List[Destination],
) -> Destination | None:
    if not eligible:
        return None
    rng = _seeded_rng(seed, "limited_location", system_id, location_type)
    ordered = sorted(eligible, key=lambda destination: destination.destination_id)
    return rng.choice(ordered)


def _destination_economies(destination: Destination) -> List[str]:
    if destination.population < 1 or destination.primary_economy_id is None:
        return []
    return [destination.primary_economy_id, *destination.secondary_economy_ids]


def _destination_has_location(destination: Destination, location_type: str) -> bool:
    return any(location.location_type == location_type for location in destination.locations)


def _add_location_if_missing(
    destination: Destination,
    placed_locations: Dict[str, set[str]],
    location_type: str,
    enabled: bool,
    notes: str | None,
) -> None:
    if location_type in placed_locations[destination.destination_id]:
        return
    location_id = f"{destination.destination_id}-LOC-{location_type}"
    destination.locations.append(
        Location(
            location_id=location_id,
            destination_id=destination.destination_id,
            location_type=location_type,
            enabled=enabled,
            notes=notes,
        )
    )
    placed_locations[destination.destination_id].add(location_type)


def _destination_counts(population: int, rng: random.Random) -> tuple[int, int]:
    bands = {
        1: ((1, 2), (0, 1)),
        2: ((1, 2), (0, 1)),
        3: ((2, 3), (0, 2)),
        4: ((3, 3), (1, 2)),
        5: ((3, 3), (1, 2)),
    }
    core_band, extra_band = bands.get(population, ((1, 2), (0, 1)))
    core_count = rng.randint(core_band[0], core_band[1])
    extra_count = rng.randint(extra_band[0], extra_band[1])
    return core_count, extra_count


def _choose_destination_types(rng: random.Random, options: List[str], count: int) -> List[str]:
    selected: List[str] = []
    for _ in range(count):
        selected.append(rng.choice(options))
    return selected


def _destination_population(
    *,
    seed: int,
    system_id: str,
    destination_id: str,
    destination_type: str,
    system_population: int,
) -> int:
    if destination_type in {"asteroid_field", "contact", "explorable_stub", "mining_stub"}:
        return 0
    if system_population <= 1:
        return max(system_population, 1)
    rng = _seeded_rng(seed, "destination_population", system_id, destination_id)
    return rng.randint(1, system_population)


def _seeded_rng(seed: int, *parts: str) -> random.Random:
    digest = hashlib.md5((f"{seed}|" + "|".join(parts)).encode("utf-8")).hexdigest()
    return random.Random(int(digest[:8], 16))


def _deterministic_system_coordinates(
    *,
    world_seed: int,
    system_id: str,
    stream_name: str,
    radius: float,
) -> tuple[float, float]:
    seed_token = f"{world_seed}|{system_id}|{stream_name}"
    digest = hashlib.sha256(seed_token.encode("ascii")).hexdigest()
    rng = random.Random(int(digest[:16], 16))
    angle = rng.random() * (2.0 * math.pi)
    radial = math.sqrt(rng.random()) * float(radius)
    return radial * math.cos(angle), radial * math.sin(angle)


def _first_destination_market(destinations: List[Destination]) -> Market | None:
    for destination in destinations:
        if destination.market is not None:
            return destination.market
    return None


def _first_destination_economies(destinations: List[Destination]) -> tuple[str | None, List[str]]:
    for destination in destinations:
        if destination.primary_economy_id is not None:
            return destination.primary_economy_id, list(destination.secondary_economy_ids)
    return None, []


def _log_location(
    logger: Logger | None,
    system_id: str,
    system_name: str,
    destination_id: str | None,
    government_id: str,
    economies: List[str] | None,
    location_type: str,
    result: str,
    reason: str,
) -> None:
    if logger is None:
        return
    destination_text = f" destination_id={destination_id}" if destination_id else ""
    economies_text = f" economies={economies}" if economies is not None else ""
    logger.log(
        turn=0,
        action="location_availability",
        state_change=(
            f"system_id={system_id} system_name={system_name}"
            f"{destination_text} government={government_id}"
            f"{economies_text} location={location_type} "
            f"result={result} reason={reason}"
        ),
    )
