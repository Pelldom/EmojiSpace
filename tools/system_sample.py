import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from data_catalog import load_data_catalog  # noqa: E402
from government_law_engine import Commodity, GovernmentLawEngine  # noqa: E402
from government_registry import GovernmentRegistry  # noqa: E402
from logger import Logger  # noqa: E402
from market_creation import MarketCreator  # noqa: E402
from market_pricing import price_transaction  # noqa: E402


def main() -> None:
    seed = _prompt_seed()
    catalog = load_data_catalog()
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    law_engine = GovernmentLawEngine(registry=registry, logger=NullLogger(), seed=seed)

    government_id = _prompt_government(registry)
    population_level = _prompt_population()
    primary_economy = _prompt_primary_economy(catalog)
    secondary_economies = _prompt_secondary_economies(catalog, primary_economy)

    creator = MarketCreator(catalog=catalog, rng=_rng(seed), logger=None)
    market = creator.create_market(
        system_id="SYS-TEST",
        population_level=population_level,
        primary_economy=primary_economy,
        secondary_economies=secondary_economies,
    )

    government = registry.get_government(government_id)
    print("System Stat Block")
    print(f"  system_id=SYS-TEST")
    print(f"  government={government.name} ({government.id})")
    print(f"  population={population_level}")
    print(f"  economy primary={primary_economy} secondary={list(secondary_economies)}")
    restricted_tags = government.ideological_modifiers.get("restricted_tags", [])
    illegal_skus = list(government.illegal_goods)
    print(f"  restricted_tags={restricted_tags}")
    print(f"  illegal_tags={restricted_tags}")
    print(f"  illegal_skus={illegal_skus}")
    print("  market:")
    for category_id, category in market.categories.items():
        for good in category.produced + category.consumed + category.neutral:
            tags = list(good.tags)
            policy = law_engine.evaluate_policy(
                government_id=government_id,
                commodity=Commodity(commodity_id=good.sku, tags=set(tags)),
                action="buy",
                turn=0,
            )
            buy = price_transaction(
                catalog=catalog,
                market=market,
                government=government,
                policy=policy,
                sku=good.sku,
                action="buy",
                world_seed=seed,
                system_id="SYS-TEST",
                scarcity_modifier=1.0,
            )
            sell_policy = law_engine.evaluate_policy(
                government_id=government_id,
                commodity=Commodity(commodity_id=good.sku, tags=set(tags)),
                action="sell",
                turn=0,
            )
            sell = price_transaction(
                catalog=catalog,
                market=market,
                government=government,
                policy=sell_policy,
                sku=good.sku,
                action="sell",
                world_seed=seed,
                system_id="SYS-TEST",
                scarcity_modifier=1.0,
            )
            print(
                f"    {category_id} sku={good.sku} tags={tags} "
                f"buy={buy.final_price:.2f} sell={sell.final_price:.2f}"
            )


def _prompt_government(registry: GovernmentRegistry) -> str:
    ids = registry.government_ids()
    print("Available governments:")
    for index, gov_id in enumerate(ids, start=1):
        print(f"  {index}) {gov_id}")
    selection = input("Government number: ").strip()
    if not selection.isdigit():
        raise ValueError("Government selection must be a number.")
    idx = int(selection)
    if idx < 1 or idx > len(ids):
        raise ValueError("Government selection out of range.")
    return ids[idx - 1]


def _prompt_seed() -> int:
    raw = input("World seed (default 12345): ").strip()
    if not raw:
        return 12345
    return int(raw)


def _prompt_population() -> int:
    raw = input("Population level (1-5): ").strip()
    population_level = int(raw)
    if population_level not in (1, 2, 3, 4, 5):
        raise ValueError(f"Invalid population level: {population_level}")
    return population_level


def _prompt_primary_economy(catalog) -> str:
    ids = sorted(catalog.economies.keys())
    print("Available economies:")
    for index, economy_id in enumerate(ids, start=1):
        print(f"  {index}) {economy_id}")
    selection = input("Primary economy number: ").strip()
    if not selection.isdigit():
        raise ValueError("Primary economy selection must be a number.")
    idx = int(selection)
    if idx < 1 or idx > len(ids):
        raise ValueError("Primary economy selection out of range.")
    return ids[idx - 1]


def _prompt_secondary_economies(catalog, primary: str):
    raw = input("Add secondary economies? (y/n): ").strip().lower()
    if raw != "y":
        return ()
    ids = sorted(catalog.economies.keys())
    print("Available economies:")
    for index, economy_id in enumerate(ids, start=1):
        print(f"  {index}) {economy_id}")
    secondary_raw = input("Secondary economy numbers (comma-separated): ").strip()
    if not secondary_raw:
        return ()
    selected_numbers = [item.strip() for item in secondary_raw.split(",") if item.strip()]
    selected: list[str] = []
    for number in selected_numbers:
        if not number.isdigit():
            raise ValueError("Secondary economy selections must be numbers.")
        idx = int(number)
        if idx < 1 or idx > len(ids):
            raise ValueError("Secondary economy selection out of range.")
        economy_id = ids[idx - 1]
        if economy_id == primary:
            raise ValueError("Secondary economy cannot match primary.")
        if economy_id not in selected:
            selected.append(economy_id)
    return tuple(selected)


def _rng(seed: int):
    import random

    return random.Random(seed)


class NullLogger:
    def log(self, turn: int, action: str, state_change: str) -> None:
        return


if __name__ == "__main__":
    main()
