from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import json

from economy_data import CATEGORY_MAP


@dataclass(frozen=True)
class Tag:
    tag_id: str
    description: str


@dataclass(frozen=True)
class Good:
    sku: str
    name: str
    category: str
    base_price: int
    tags: List[str]
    possible_tag: str | None


@dataclass(frozen=True)
class Economy:
    economy_id: str
    name: str
    produces: List[str]
    consumes: List[str]
    neutral_categories: List[str]
    possible_tag_bias: Dict[str, float]
    description: str


@dataclass(frozen=True)
class DataCatalog:
    tags: Dict[str, Tag]
    goods: List[Good]
    economies: Dict[str, Economy]

    def goods_by_category(self) -> Dict[str, List[Good]]:
        grouped: Dict[str, List[Good]] = {category_id: [] for category_id in CATEGORY_MAP}
        for good in self.goods:
            grouped.setdefault(good.category, []).append(good)
        return grouped

    def good_by_sku(self, sku: str) -> Good:
        for good in self.goods:
            if good.sku == sku:
                return good
        raise KeyError(f"Unknown SKU: {sku}")


def load_data_catalog() -> DataCatalog:
    root = Path(__file__).resolve().parents[1]
    categories = _load_categories(root / "data" / "categories.json")
    tags = _load_tags(root / "data" / "tags.json")
    goods = _load_goods(root / "data" / "goods.json", tags, categories)
    economies = _load_economies(root / "data" / "economies.json")
    _validate_economies(economies, categories)
    return DataCatalog(tags=tags, goods=goods, economies=economies)


def _load_categories(path: Path) -> Dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    categories = data.get("categories", {})
    if not categories:
        raise ValueError("No categories loaded from categories.json.")
    return {category_id: details.get("description", "") for category_id, details in categories.items()}


def _load_tags(path: Path) -> Dict[str, Tag]:
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    tag_data = data.get("tags", {})
    tags: Dict[str, Tag] = {}
    for tag_id, details in tag_data.items():
        tags[tag_id] = Tag(
            tag_id=tag_id,
            description=details.get("description", ""),
        )
    if not tags:
        raise ValueError("No tags loaded from tags.json.")
    return tags


def _load_goods(path: Path, tags: Dict[str, Tag], categories: Dict[str, str]) -> List[Good]:
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    goods_data = data.get("goods", [])
    goods: List[Good] = []
    allowed_possible_tags = {
        "luxury",
        "weaponized",
        "counterfeit",
        "propaganda",
        "stolen",
        "hazardous",
        "cybernetic",
    }
    for entry in goods_data:
        category = entry["category"]
        if category not in categories:
            raise ValueError(f"Good references unknown category: {category}")
        for tag in entry.get("tags", []):
            if tag not in tags:
                raise ValueError(f"Good {entry['sku']} references unknown tag: {tag}")
        possible_tag = entry.get("possible_tag")
        if possible_tag is not None and possible_tag not in tags:
            raise ValueError(
                f"Good {entry['sku']} references unknown possible_tag: {possible_tag}"
            )
        if possible_tag is not None and possible_tag not in allowed_possible_tags:
            raise ValueError(
                f"Good {entry['sku']} has possible_tag outside allowed list: {possible_tag}"
            )
        goods.append(
            Good(
                sku=entry["sku"],
                name=entry["name"],
                category=category,
                base_price=entry["base_price"],
                tags=list(entry.get("tags", [])),
                possible_tag=possible_tag,
            )
        )
    if not goods:
        raise ValueError("No goods loaded from goods.json.")
    return goods


def _load_economies(path: Path) -> Dict[str, Economy]:
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    economies_data = data.get("economies", [])
    economies: Dict[str, Economy] = {}
    for entry in economies_data:
        economy = Economy(
            economy_id=entry["id"],
            name=entry["name"],
            produces=list(entry.get("produces", [])),
            consumes=list(entry.get("consumes", [])),
            neutral_categories=list(entry.get("neutral_categories", [])),
            possible_tag_bias=dict(entry.get("possible_tag_bias", {})),
            description=entry.get("description", ""),
        )
        if economy.economy_id in economies:
            raise ValueError(f"Duplicate economy id: {economy.economy_id}")
        economies[economy.economy_id] = economy
    if not economies:
        raise ValueError("No economies loaded from economies.json.")
    return economies


def _validate_economies(economies: Dict[str, Economy], categories: Dict[str, str]) -> None:
    for economy in economies.values():
        for category_id in economy.produces + economy.consumes + economy.neutral_categories:
            if category_id not in categories:
                raise ValueError(
                    f"Economy {economy.economy_id} references unknown category: {category_id}"
                )
