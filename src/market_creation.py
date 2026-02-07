from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple
import random

from data_catalog import DataCatalog, Economy, Good
from economy_data import CATEGORY_MAP
from logger import Logger
from market import Market, MarketCategory, MarketGood


NEUTRAL_CHANCE_BY_POPULATION: Dict[int, float] = {
    1: 0.20,
    2: 0.30,
    3: 0.40,
    4: 0.55,
    5: 0.70,
}

BASE_POSSIBLE_TAG_CHANCE = 0.10
MAX_POSSIBLE_TAG_CHANCE = 0.50
SECONDARY_ECONOMY_CHANCE = 0.33


@dataclass(frozen=True)
class EconomyAssignment:
    primary: str
    secondary: Tuple[str, ...]


class MarketCreator:
    def __init__(self, catalog: DataCatalog, rng: random.Random, logger: Logger | None = None) -> None:
        self._catalog = catalog
        self._rng = rng
        self._logger = logger

    def assign_economies(self, population_level: int) -> EconomyAssignment:
        economy_ids = sorted(self._catalog.economies.keys())
        if not economy_ids:
            raise ValueError("No economies available for assignment.")
        primary = self._rng.choice(economy_ids)
        secondary: List[str] = []
        max_secondary = self._max_secondary_economies(population_level)
        for _ in range(max_secondary):
            if self._rng.random() >= SECONDARY_ECONOMY_CHANCE:
                continue
            eligible = [eid for eid in economy_ids if eid not in secondary and eid != primary]
            if not eligible:
                break
            secondary.append(self._rng.choice(eligible))
        return EconomyAssignment(primary=primary, secondary=tuple(secondary))

    def create_market(
        self,
        system_id: str,
        population_level: int,
        primary_economy: str,
        secondary_economies: Sequence[str],
    ) -> Market:
        economies = self._economies_for(primary_economy, secondary_economies)
        self._log(
            f"system_id={system_id} economies primary={primary_economy} secondary={list(secondary_economies)}"
        )

        produced = self._aggregate_categories(economies, "produces")
        consumed = self._aggregate_categories(economies, "consumes")
        neutral_candidates = self._aggregate_categories(economies, "neutral_categories")

        categories: Dict[str, MarketCategory] = {}
        for category_id in self._market_categories(produced, consumed, neutral_candidates):
            neutral_allowed, neutral_roll = self._neutral_allowed(
                category_id, neutral_candidates, population_level
            )
            if neutral_roll is not None:
                self._log(
                    f"system_id={system_id} category={category_id} neutral_roll={neutral_roll:.2f} "
                    f"chance={self._neutral_chance(population_level):.2f} "
                    f"result={'yes' if neutral_allowed else 'no'}"
                )
            candidates = self._build_candidates(category_id, economies)
            produced_goods, candidates = self._assign_role(
                candidates, population_level, produced and category_id in produced
            )
            consumed_goods, candidates = self._assign_role(
                candidates, population_level, consumed and category_id in consumed
            )
            neutral_goods, _ = self._assign_role(
                candidates, population_level, neutral_allowed
            )
            if not (produced_goods or consumed_goods or neutral_goods):
                continue
            categories[category_id] = MarketCategory(
                produced=tuple(produced_goods),
                consumed=tuple(consumed_goods),
                neutral=tuple(neutral_goods),
            )
            self._log(
                f"system_id={system_id} category={category_id} "
                f"produced={[g.sku for g in produced_goods]} "
                f"consumed={[g.sku for g in consumed_goods]} "
                f"neutral={[g.sku for g in neutral_goods]}"
            )

        categories = self._enforce_minimum_roles(
            system_id=system_id,
            categories=categories,
            economies=economies,
        )

        return Market(
            categories=categories,
            primary_economy=primary_economy,
            secondary_economies=tuple(secondary_economies),
        )

    def _neutral_allowed(
        self,
        category_id: str,
        neutral_candidates: set[str],
        population_level: int,
    ) -> tuple[bool, float | None]:
        if category_id not in neutral_candidates:
            return False, None
        roll = self._rng.random()
        chance = self._neutral_chance(population_level)
        return roll < chance, roll

    def _build_candidates(self, category_id: str, economies: Sequence[Economy]) -> List[MarketGood]:
        goods_by_category = self._catalog.goods_by_category()
        base_goods = list(goods_by_category.get(category_id, []))
        candidates: List[MarketGood] = []
        for good in base_goods:
            candidates.append(self._to_market_good(good, extra_tag=None))
            if good.possible_tag:
                chance = self._possible_tag_chance(good.possible_tag, economies)
                roll = self._rng.random()
                applied = roll < chance
                self._log(
                    f"good={good.sku} possible_tag={good.possible_tag} "
                    f"chance={chance:.2f} roll={roll:.2f} applied={applied}"
                )
                if applied:
                    candidates.append(self._to_market_good(good, extra_tag=good.possible_tag))
        return candidates

    @staticmethod
    def _to_market_good(good: Good, extra_tag: str | None) -> MarketGood:
        tags = list(good.tags)
        sku = good.sku
        name = good.name
        if extra_tag:
            tags.append(extra_tag)
            sku = f"{extra_tag}_{sku}"
            name = f"{extra_tag.title()} {name}"
        return MarketGood(
            sku=sku,
            name=name,
            category=good.category,
            base_price=good.base_price,
            tags=tuple(tags),
        )

    def _assign_role(
        self,
        candidates: List[MarketGood],
        population_level: int,
        allowed: bool,
    ) -> tuple[List[MarketGood], List[MarketGood]]:
        if not allowed or not candidates:
            return [], candidates
        cap = population_level
        if len(candidates) <= cap:
            return candidates, []
        selected: List[MarketGood] = []
        pool = list(candidates)
        while pool and len(selected) < cap:
            index = self._rng.randrange(len(pool))
            selected.append(pool.pop(index))
        return selected, pool

    def _enforce_minimum_roles(
        self,
        system_id: str,
        categories: Dict[str, MarketCategory],
        economies: Sequence[Economy],
    ) -> Dict[str, MarketCategory]:
        produced_total = sum(len(category.produced) for category in categories.values())
        consumed_total = sum(len(category.consumed) for category in categories.values())

        produced_categories = self._aggregate_categories(economies, "produces")
        consumed_categories = self._aggregate_categories(economies, "consumes")

        if produced_total == 0:
            self._apply_fallback(
                system_id=system_id,
                categories=categories,
                candidate_categories=produced_categories,
                role="produced",
            )

        if consumed_total == 0:
            self._apply_fallback(
                system_id=system_id,
                categories=categories,
                candidate_categories=consumed_categories,
                role="consumed",
            )

        return categories

    def _apply_fallback(
        self,
        system_id: str,
        categories: Dict[str, MarketCategory],
        candidate_categories: set[str],
        role: str,
    ) -> None:
        if candidate_categories:
            category_id = self._rng.choice(sorted(candidate_categories))
        else:
            category_id = self._rng.choice(sorted(CATEGORY_MAP.keys()))
        goods_by_category = self._catalog.goods_by_category()
        base_goods = goods_by_category.get(category_id, [])
        if not base_goods:
            self._log(f"system_id={system_id} fallback_{role}=skipped no_goods category={category_id}")
            return
        existing = categories.get(category_id)
        used_skus = set()
        if existing:
            used_skus.update(g.sku for g in existing.produced)
            used_skus.update(g.sku for g in existing.consumed)
            used_skus.update(g.sku for g in existing.neutral)
        candidates = [good for good in base_goods if good.sku not in used_skus]
        if not candidates:
            self._log(
                f"system_id={system_id} fallback_{role}=skipped no_available_skus category={category_id}"
            )
            return
        chosen = self._rng.choice(candidates)
        market_good = self._to_market_good(chosen, extra_tag=None)

        if existing is None:
            existing = MarketCategory(produced=tuple(), consumed=tuple(), neutral=tuple())
        if role == "produced":
            updated = MarketCategory(
                produced=existing.produced + (market_good,),
                consumed=existing.consumed,
                neutral=existing.neutral,
            )
        else:
            updated = MarketCategory(
                produced=existing.produced,
                consumed=existing.consumed + (market_good,),
                neutral=existing.neutral,
            )
        categories[category_id] = updated
        self._log(
            f"system_id={system_id} fallback_{role}=applied category={category_id} sku={market_good.sku}"
        )

    def _possible_tag_chance(self, possible_tag: str, economies: Sequence[Economy]) -> float:
        bias = 0.0
        for economy in economies:
            bias += economy.possible_tag_bias.get(possible_tag, 0.0)
        return min(BASE_POSSIBLE_TAG_CHANCE + bias, MAX_POSSIBLE_TAG_CHANCE)

    @staticmethod
    def _market_categories(
        produced: set[str],
        consumed: set[str],
        neutral_candidates: set[str],
    ) -> List[str]:
        return sorted(set().union(produced, consumed, neutral_candidates))

    def _economies_for(self, primary: str, secondary: Sequence[str]) -> List[Economy]:
        ids = [primary, *secondary]
        return [self._catalog.economies[economy_id] for economy_id in ids]

    @staticmethod
    def _aggregate_categories(economies: Iterable[Economy], field: str) -> set[str]:
        categories: set[str] = set()
        for economy in economies:
            categories.update(getattr(economy, field))
        return categories

    @staticmethod
    def _neutral_chance(population_level: int) -> float:
        if population_level not in NEUTRAL_CHANCE_BY_POPULATION:
            raise ValueError(f"Invalid population level: {population_level}")
        return NEUTRAL_CHANCE_BY_POPULATION[population_level]

    @staticmethod
    def _max_secondary_economies(population_level: int) -> int:
        if population_level <= 2:
            return 1
        if population_level == 3:
            return 2
        return 3

    def _log(self, message: str) -> None:
        if self._logger is None:
            return
        self._logger.log(
            turn=0,
            action="market_create",
            state_change=message,
        )
