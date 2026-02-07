import sys
from pathlib import Path

from economy_data import CATEGORIES
from economy_engine import EconomyEngine
from data_catalog import DataCatalog, load_data_catalog
from government_registry import GovernmentRegistry
from government_law_engine import GovernmentLawEngine
from logger import Logger
from player_state import PlayerState
from time_engine import TimeEngine
from turn_loop import BuyAction, MoveAction, SellAction, TurnLoop
from world_generator import Sector, WorldGenerator


def read_version() -> tuple[str, str]:
    version_path = Path(__file__).resolve().parents[1] / "VERSION"
    if not version_path.exists():
        raise FileNotFoundError("VERSION file is required at the project root.")
    contents = version_path.read_text(encoding="utf-8").strip()
    version = _parse_version_line(contents)
    return version, contents


def _parse_version_line(contents: str) -> str:
    for line in contents.splitlines():
        if line.startswith("Version:"):
            return line.split("Version:", 1)[1].strip()
    raise ValueError("VERSION file must include a line starting with 'Version:'.")


def parse_seed(argv: list[str]) -> int:
    if len(argv) >= 2:
        return int(argv[1])
    return 12345


def main() -> None:
    version, version_contents = read_version()
    logger = Logger(version=version)
    print(version_contents)

    seed = parse_seed(sys.argv)
    catalog = load_data_catalog()
    _log_data_catalog(catalog, logger, seed=seed)
    government_registry = _load_governments()
    law_engine = GovernmentLawEngine(registry=government_registry, logger=logger, seed=seed)
    generator = WorldGenerator(
        seed=seed,
        system_count=5,
        government_ids=government_registry.government_ids(),
        catalog=catalog,
        logger=logger,
    )
    sector = generator.generate()

    start_system_id = sector.system_ids()[0]
    player_state = PlayerState(start_system_id=start_system_id)
    time_engine = TimeEngine()
    economy_engine = EconomyEngine(sector=sector, logger=logger)
    turn_loop = TurnLoop(
        time_engine=time_engine,
        sector=sector,
        player_state=player_state,
        logger=logger,
        economy_engine=economy_engine,
        law_engine=law_engine,
    )

    logger.log(
        turn=time_engine.current_turn,
        action="init",
        state_change=f"seed={seed} start_location={start_system_id}",
    )
    _log_system_stat_blocks(sector, government_registry, logger, time_engine.current_turn)

    print("System Stat Blocks:")
    _print_system_stat_blocks(sector, government_registry)

    system_ids = sector.system_ids()
    if len(system_ids) > 1:
        turn_loop.execute_move(MoveAction(target_system_id=system_ids[1]))
    turn_loop.execute_buy(BuyAction(category_id="FOOD"))
    turn_loop.execute_buy(BuyAction(category_id="MEDICINE"))
    turn_loop.execute_sell(SellAction(category_id="FOOD"))
    if len(system_ids) > 2:
        turn_loop.execute_move(MoveAction(target_system_id=system_ids[2]))
        turn_loop.execute_sell(SellAction(category_id="MEDICINE"))

    print("Prices after actions:")
    _print_prices(sector, economy_engine)


def _print_system_stat_blocks(sector: Sector, registry: GovernmentRegistry) -> None:
    for system in sector.systems:
        government_id = system.attributes.get("government_id")
        government = registry.get_government(government_id)
        population_level = system.attributes.get("population_level", 3)
        primary_economy = system.attributes.get("primary_economy")
        secondary_economies = system.attributes.get("secondary_economies", [])
        market = system.attributes.get("market")
        print(f"{system.system_id} {system.name}")
        print(f"  government={government.name} ({government.id})")
        print(f"  population={population_level}")
        print(f"  economy primary={primary_economy} secondary={secondary_economies}")
        if market is None:
            print("  market=none")
            continue
        for category_id, market_category in market.categories.items():
            produced = ", ".join(good.sku for good in market_category.produced)
            consumed = ", ".join(good.sku for good in market_category.consumed)
            neutral = ", ".join(good.sku for good in market_category.neutral)
            print(
                f"  market {category_id} "
                f"produced=[{produced}] consumed=[{consumed}] neutral=[{neutral}]"
            )


def _log_governments(
    sector: Sector,
    registry: GovernmentRegistry,
    logger: Logger,
    turn: int,
) -> None:
    for system in sector.systems:
        government_id = system.attributes.get("government_id")
        government = registry.get_government(government_id)
        logger.log(
            turn=turn,
            action="government_assign",
            state_change=(
                f"system_id={system.system_id} "
                f"government_id={government.id} government_name={government.name}"
            ),
        )


def _log_system_stat_blocks(
    sector: Sector,
    registry: GovernmentRegistry,
    logger: Logger,
    turn: int,
) -> None:
    logger.log(
        turn=turn,
        action="diagnostic",
        state_change="[DIAGNOSTIC] System Stat Blocks",
    )
    for system in sector.systems:
        government_id = system.attributes.get("government_id")
        government = registry.get_government(government_id)
        population_level = system.attributes.get("population_level", 3)
        primary_economy = system.attributes.get("primary_economy")
        secondary_economies = system.attributes.get("secondary_economies", [])
        market = system.attributes.get("market")
        economy_block = f"primary={primary_economy} secondary={secondary_economies}"
        logger.log(
            turn=turn,
            action="diagnostic",
            state_change=(
                f"System {system.system_id} {system.name} | "
                f"Government {government.name} ({government.id}) | "
                f"Population {population_level} | "
                f"Economy {economy_block}"
            ),
        )
        if market is None:
            logger.log(
                turn=turn,
                action="diagnostic",
                state_change=f"system_id={system.system_id} market=none",
            )
            continue
        for category_id, market_category in market.categories.items():
            produced = [good.sku for good in market_category.produced]
            consumed = [good.sku for good in market_category.consumed]
            neutral = [good.sku for good in market_category.neutral]
            logger.log(
                turn=turn,
                action="diagnostic",
                state_change=(
                    f"system_id={system.system_id} market_category={category_id} "
                    f"produced={produced} consumed={consumed} neutral={neutral}"
                ),
            )


def _log_data_catalog(catalog: DataCatalog, logger: Logger, seed: int) -> None:
    logger.log(
        turn=0,
        action="diagnostic",
        state_change=(
            f"[DIAGNOSTIC] Data Catalog seed={seed} "
            f"tags={len(catalog.tags)} goods={len(catalog.goods)} "
            f"economies={len(catalog.economies)}"
        ),
    )
    goods_by_category = catalog.goods_by_category()
    for category_id, goods in goods_by_category.items():
        if not goods:
            continue
        logger.log(
            turn=0,
            action="diagnostic",
            state_change=f"[DIAGNOSTIC] Goods {category_id} count={len(goods)}",
        )


def _load_governments() -> GovernmentRegistry:
    governments_path = Path(__file__).resolve().parents[1] / "data" / "governments.json"
    return GovernmentRegistry.from_file(governments_path)


def _print_prices(sector: Sector, economy_engine: EconomyEngine) -> None:
    for system in sector.systems:
        parts = []
        for category in CATEGORIES:
            price = economy_engine.price(system.system_id, category.category_id)
            parts.append(f"{category.category_id}={price:.2f}")
        print(f"{system.system_id} {system.name} " + " ".join(parts))


if __name__ == "__main__":
    main()
