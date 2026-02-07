from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import json


@dataclass(frozen=True)
class Category:
    category_id: str
    description: str
    base_price: int


# TODO(Phase 3): Replace base prices with SKU-derived values when market logic lands.
CATEGORY_BASE_PRICES: Dict[str, int] = {
    "FOOD": 100,
    "ORE": 120,
    "MEDICINE": 180,
    "PARTS": 160,
}


def _load_categories() -> Dict[str, Category]:
    categories_path = Path(__file__).resolve().parents[1] / "data" / "categories.json"
    data = json.loads(categories_path.read_text(encoding="utf-8", errors="replace"))
    categories = data.get("categories", {})
    loaded: Dict[str, Category] = {}
    for category_id, category_data in categories.items():
        if category_id not in CATEGORY_BASE_PRICES:
            continue
        loaded[category_id] = Category(
            category_id=category_id,
            description=category_data.get("description", ""),
            base_price=CATEGORY_BASE_PRICES[category_id],
        )
    if not loaded:
        raise ValueError("No categories loaded for Phase 1 economy.")
    return loaded


CATEGORY_MAP: Dict[str, Category] = _load_categories()
CATEGORIES: List[Category] = list(CATEGORY_MAP.values())


def get_category(category_id: str) -> Category:
    if category_id not in CATEGORY_MAP:
        raise KeyError(f"Unknown category_id: {category_id}")
    return CATEGORY_MAP[category_id]


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
