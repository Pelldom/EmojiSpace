from dataclasses import dataclass
from typing import List, Optional
import random

from economy_data import PROFILE_IDS


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
    def __init__(self, seed: int, system_count: int = 5) -> None:
        self._seed = seed
        self._system_count = system_count

    def generate(self) -> Sector:
        rng = random.Random(self._seed)
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
            population_level = self._weighted_population_level(rng)
            attributes = {"profile_id": profile_id, "population_level": population_level}
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
