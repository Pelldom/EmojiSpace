import sys
from pathlib import Path

from data_catalog import DataCatalog, load_data_catalog
from economy_engine import EconomyEngine
from government_law_engine import GovernmentLawEngine
from government_registry import GovernmentRegistry
from logger import Logger
from market_pricing import price_transaction
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
        catalog=catalog,
        government_registry=government_registry,
        world_seed=seed,
    )

    logger.log(
        turn=time_engine.current_turn,
        action="init",
        state_change=f"seed={seed} start_location={start_system_id}",
    )

    _log_system_stat_blocks(
        sector=sector,
        catalog=catalog,
        economy_engine=economy_engine,
        registry=government_registry,
        logger=logger,
        world_seed=seed,
        turn=time_engine.current_turn,
        label="initial",
    )

    _run_five_turn_demo(sector, turn_loop)

    _log_system_stat_blocks(
        sector=sector,
        catalog=catalog,
        economy_engine=economy_engine,
        registry=government_registry,
        logger=logger,
        world_seed=seed,
        turn=time_engine.current_turn,
        label="final",
    )


def _run_five_turn_demo(sector: Sector, turn_loop: TurnLoop) -> None:
    system_ids = sector.system_ids()
    if len(system_ids) < 2:
        return
    buy_sku = _first_market_sku(sector, role="produced")
    sell_sku = _first_market_sku(sector, role="consumed") or buy_sku

    turn_loop.execute_move(MoveAction(target_system_id=system_ids[1]))
    if buy_sku:
        turn_loop.execute_buy(BuyAction(sku=buy_sku))
    turn_loop.execute_move(MoveAction(target_system_id=system_ids[0]))
    if sell_sku:
        turn_loop.execute_sell(SellAction(sku=sell_sku))
    if len(system_ids) > 2:
        turn_loop.execute_move(MoveAction(target_system_id=system_ids[2]))


def _first_market_sku(sector: Sector, role: str) -> str | None:
    for system in sector.systems:
        market = system.attributes.get("market")
        if market is None:
            continue
        for category in market.categories.values():
            goods = getattr(category, role, ())
            if goods:
                return goods[0].sku
    return None


def _log_system_stat_blocks(
    *,
    sector: Sector,
    catalog: DataCatalog,
    economy_engine: EconomyEngine,
    registry: GovernmentRegistry,
    logger: Logger,
    world_seed: int,
    turn: int,
    label: str,
) -> None:
    logger.log(
        turn=turn,
        action="stat_block",
        state_change=f"[STAT_BLOCK] {label} systems",
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
            action="stat_block",
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
                action="stat_block",
                state_change=f"system_id={system.system_id} market=none",
            )
            continue
        for category_id, category in market.categories.items():
            for good in category.produced + category.consumed + category.neutral:
                scarcity = _safe_scarcity(economy_engine, system.system_id, category_id)
                buy = price_transaction(
                    catalog=catalog,
                    market=market,
                    government=government,
                    sku=good.sku,
                    action="buy",
                    world_seed=world_seed,
                    system_id=system.system_id,
                    scarcity_modifier=scarcity,
                )
                sell = price_transaction(
                    catalog=catalog,
                    market=market,
                    government=government,
                    sku=good.sku,
                    action="sell",
                    world_seed=world_seed,
                    system_id=system.system_id,
                    scarcity_modifier=scarcity,
                )
                logger.log(
                    turn=turn,
                    action="stat_block",
                    state_change=(
                        f"system_id={system.system_id} sku={good.sku} "
                        f"category={category_id} buy={buy.final_price:.2f} "
                        f"sell={sell.final_price:.2f}"
                    ),
                )


def _load_governments() -> GovernmentRegistry:
    governments_path = Path(__file__).resolve().parents[1] / "data" / "governments.json"
    return GovernmentRegistry.from_file(governments_path)


def _safe_scarcity(economy_engine: EconomyEngine, system_id: str, category_id: str) -> float:
    try:
        return economy_engine.scarcity_modifier(system_id, category_id)
    except KeyError:
        return 1.0


if __name__ == "__main__":
    main()
