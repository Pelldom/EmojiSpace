from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class MarketGood:
    sku: str
    name: str
    category: str
    tags: Tuple[str, ...]


@dataclass(frozen=True)
class MarketCategory:
    produced: Tuple[MarketGood, ...]
    consumed: Tuple[MarketGood, ...]
    neutral: Tuple[MarketGood, ...]


@dataclass(frozen=True)
class Market:
    categories: Dict[str, MarketCategory]
    primary_economy: str
    secondary_economies: Tuple[str, ...]
