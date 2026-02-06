from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Good:
    good_id: str
    name: str
    category: str
    tags: List[str]
    base_price: int
    description: str


GOODS: List[Good] = [
    Good(
        good_id="FOOD",
        name="Food",
        category="BIO",
        tags=[],
        base_price=100,
        description="Basic nutrition and staples.",
    ),
    Good(
        good_id="ORE",
        name="Ore",
        category="RAW",
        tags=[],
        base_price=120,
        description="Unrefined mineral resources.",
    ),
    Good(
        good_id="MEDICINE",
        name="Medicine",
        category="BIO",
        tags=[],
        base_price=180,
        description="Medical supplies and treatments.",
    ),
    Good(
        good_id="PARTS",
        name="Parts",
        category="INDUSTRIAL",
        tags=[],
        base_price=160,
        description="Industrial components and machinery parts.",
    ),
]


def get_good(good_id: str) -> Good:
    for good in GOODS:
        if good.good_id == good_id:
            return good
    raise KeyError(f"Unknown good_id: {good_id}")


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
