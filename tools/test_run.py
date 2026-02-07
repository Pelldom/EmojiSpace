import random
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from economy_data import CATEGORIES, RESOURCE_PROFILES  # noqa: E402
from data_catalog import load_data_catalog  # noqa: E402
from world_generator import Sector, System, WorldGenerator  # noqa: E402


@dataclass(frozen=True)
class PopulationConfig:
    level_weights: dict[int, int]
    scalar_by_level: dict[int, float]


POPULATION_CONFIG = PopulationConfig(
    level_weights={
        1: 1,  # Rare
        2: 3,  # Uncommon
        3: 6,  # Common
        4: 3,  # Uncommon
        5: 1,  # Rare
    },
    scalar_by_level={
        0: 0.0,
        1: 0.25,
        2: 0.50,
        3: 1.00,
        4: 1.75,
        5: 2.50,
    },
)


def parse_seed(argv: list[str]) -> int:
    if len(argv) >= 2:
        return int(argv[1])
    return 12345


def weighted_population_level(rng: random.Random) -> int:
    weighted_levels: list[int] = []
    for level, weight in POPULATION_CONFIG.level_weights.items():
        weighted_levels.extend([level] * weight)
    return rng.choice(weighted_levels)


def assign_population_levels(sector: Sector, rng: random.Random) -> Sector:
    updated_systems: list[System] = []
    for system in sector.systems:
        level = weighted_population_level(rng)
        attributes = dict(system.attributes)
        attributes["population_level"] = level
        updated_systems.append(
            System(
                system_id=system.system_id,
                name=system.name,
                attributes=attributes,
                neighbors=list(system.neighbors),
            )
        )
    return Sector(systems=updated_systems)


def report_population_scaling(sector: Sector) -> None:
    for system in sector.systems:
        profile_id = system.attributes.get("profile_id")
        population_level = system.attributes.get("population_level", 3)
        if population_level not in POPULATION_CONFIG.scalar_by_level:
            raise ValueError(f"Invalid population level: {population_level}")
        scalar = POPULATION_CONFIG.scalar_by_level[population_level]
        profile = RESOURCE_PROFILES[profile_id]

        print(f"{system.system_id} {system.name}")
        print(f"  population_level={population_level} scalar={scalar:.2f}")
        for category in CATEGORIES:
            base_production = profile.production[category.category_id]
            base_consumption = profile.consumption[category.category_id]
            base_capacity = max(base_production, base_consumption)
            final_production = base_production * scalar
            final_consumption = base_consumption * scalar
            final_capacity = base_capacity * scalar
            print(
                "  "
                f"{category.category_id} "
                f"base(prod={base_production} cons={base_consumption} cap={base_capacity}) "
                f"final(prod={final_production:.2f} cons={final_consumption:.2f} cap={final_capacity:.2f})"
            )


def main() -> None:
    seed = parse_seed(sys.argv)
    rng = random.Random(seed)
    catalog = load_data_catalog()
    generator = WorldGenerator(seed=seed, system_count=5, catalog=catalog)
    sector = generator.generate()
    test_sector = assign_population_levels(sector, rng)
    report_population_scaling(test_sector)


if __name__ == "__main__":
    main()
