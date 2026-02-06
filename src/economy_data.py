from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Good:
    good_id: str
    name: str
    category: str
    base_price: int
    description: str


GOODS: List[Good] = [
    Good(
        good_id="FOOD",
        name="Food",
        category="BIO",
        base_price=100,
        description="Basic nutrition and staples.",
    ),
    Good(
        good_id="ORE",
        name="Ore",
        category="RAW",
        base_price=120,
        description="Unrefined mineral resources.",
    ),
    Good(
        good_id="MEDICINE",
        name="Medicine",
        category="BIO",
        base_price=180,
        description="Medical supplies and treatments.",
    ),
    Good(
        good_id="PARTS",
        name="Parts",
        category="INDUSTRIAL",
        base_price=160,
        description="Industrial components and machinery parts.",
    ),
]


@dataclass(frozen=True)
class ResourceProfile:
    production: Dict[str, int]
    consumption: Dict[str, int]


RESOURCE_PROFILES: Dict[str, ResourceProfile] = {
    "AGRICULTURAL": ResourceProfile(
        production={"FOOD": 3, "ORE": 0, "MEDICINE": 1, "PARTS": 0},
        consumption={"FOOD": 1, "ORE": 1, "MEDICINE": 1, "PARTS": 1},
    ),
    "MINING": ResourceProfile(
        production={"FOOD": 0, "ORE": 3, "MEDICINE": 0, "PARTS": 1},
        consumption={"FOOD": 1, "ORE": 0, "MEDICINE": 1, "PARTS": 1},
    ),
    "INDUSTRIAL": ResourceProfile(
        production={"FOOD": 0, "ORE": 1, "MEDICINE": 0, "PARTS": 3},
        consumption={"FOOD": 1, "ORE": 1, "MEDICINE": 1, "PARTS": 0},
    ),
    "HUB": ResourceProfile(
        production={"FOOD": 1, "ORE": 1, "MEDICINE": 1, "PARTS": 1},
        consumption={"FOOD": 1, "ORE": 1, "MEDICINE": 1, "PARTS": 1},
    ),
}


PROFILE_IDS: List[str] = list(RESOURCE_PROFILES.keys())
