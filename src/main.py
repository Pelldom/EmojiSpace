import os
import sys
from pathlib import Path

from data_catalog import DataCatalog, load_data_catalog
from economy_engine import EconomyEngine
from government_law_engine import Commodity, GovernmentLawEngine
from government_registry import GovernmentRegistry
from logger import Logger
from law_enforcement import CargoSnapshot, PlayerOption, TriggerType, enforcement_checkpoint
from market import Market
from player_state import PlayerState
from time_engine import TimeEngine
from turn_loop import BuyAction, MoveAction, SellAction, TurnLoop
from world_generator import Destination, Sector, System, WorldGenerator


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

    _log_galaxy_overview(
        sector=sector,
        logger=logger,
        world_seed=seed,
        turn=time_engine.current_turn,
        label="initial",
    )

    # Diagnostics only: no automated turn loop demo while destination markets are authoritative.

    _log_galaxy_overview(
        sector=sector,
        logger=logger,
        world_seed=seed,
        turn=time_engine.current_turn,
        label="final",
    )
    if os.environ.get("ENFORCEMENT_DEMO") == "1":
        _enforcement_demo(
            sector=sector,
            registry=government_registry,
            logger=logger,
            player_state=player_state,
            law_engine=law_engine,
            world_seed=seed,
            turn=time_engine.current_turn,
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


def _log_galaxy_overview(
    *,
    sector: Sector,
    logger: Logger,
    world_seed: int,
    turn: int,
    label: str,
) -> None:
    logger.log(
        turn=turn,
        action="galaxy_overview",
        state_change=f"[GALAXY] {label} systems={len(sector.systems)} seed={world_seed}",
    )
    printed_system_market = False
    for system in sector.systems:
        _log_system_warning_for_shim(system, logger, turn)
        logger.log(
            turn=turn,
            action="galaxy_overview",
            state_change=(
                f"[SYSTEM] id={system.system_id} name={system.name} "
                f"population={system.population} government_id={system.government_id}"
            ),
        )
        for destination in system.destinations:
            logger.log(
                turn=turn,
                action="galaxy_overview",
                state_change=(
                    f"  [DESTINATION] id={destination.destination_id} "
                    f"type={destination.destination_type} population={destination.population} "
                    f"primary_economy={destination.primary_economy_id} "
                    f"secondary_economies={destination.secondary_economy_ids}"
                ),
            )
            _log_destination_locations(destination, logger, turn)
            if destination.market is not None:
                _log_destination_market_summary(destination.destination_id, destination.market, logger, turn)
        assert not printed_system_market, "System-level market output is forbidden."


def _load_governments() -> GovernmentRegistry:
    governments_path = Path(__file__).resolve().parents[1] / "data" / "governments.json"
    return GovernmentRegistry.from_file(governments_path)


def _enforcement_demo(
    *,
    sector: Sector,
    registry: GovernmentRegistry,
    logger: Logger,
    player_state: PlayerState,
    law_engine: GovernmentLawEngine,
    world_seed: int,
    turn: int,
) -> None:
    system_id = sector.system_ids()[0]
    anarchic = registry.get_government("anarchic")
    fascist = registry.get_government("fascist")
    corporate = registry.get_government("corporate_authority")
    illegal_sku = fascist.illegal_goods[0]
    restricted_tag = "recreational"
    restricted_sku = "demo_recreational"

    player_state.set_reputation(system_id, 100)
    player_state.set_heat(system_id, 0)
    policy_low = law_engine.evaluate_policy(
        government_id=anarchic.id,
        commodity=Commodity(commodity_id=illegal_sku, tags=set()),
        action="demo_border_no_trigger",
        turn=turn,
    )
    enforcement_checkpoint(
        system_id=system_id,
        trigger_type=TriggerType.BORDER,
        government=anarchic,
        policy_results=[(illegal_sku, policy_low)],
        player=player_state,
        world_seed=world_seed,
        turn=turn,
        cargo_snapshot=CargoSnapshot(illegal_present=False, restricted_unlicensed_present=False),
        logger=logger,
        option=None,
    )

    player_state.set_reputation(system_id, 1)
    player_state.set_heat(system_id, 100)
    policy_restricted = law_engine.evaluate_policy(
        government_id=corporate.id,
        commodity=Commodity(commodity_id=restricted_sku, tags={restricted_tag}),
        action="demo_customs_trigger",
        turn=turn + 1,
    )
    policy_illegal = law_engine.evaluate_policy(
        government_id=fascist.id,
        commodity=Commodity(commodity_id=illegal_sku, tags=set()),
        action="demo_customs_illegal",
        turn=turn + 4,
    )
    enforcement_checkpoint(
        system_id=system_id,
        trigger_type=TriggerType.CUSTOMS,
        government=corporate,
        policy_results=[(restricted_sku, policy_restricted)],
        player=player_state,
        world_seed=world_seed,
        turn=turn + 1,
        cargo_snapshot=CargoSnapshot(illegal_present=False, restricted_unlicensed_present=True),
        logger=logger,
        option=PlayerOption.BRIBE,
        bribe_tier="LARGE",
    )

    enforcement_checkpoint(
        system_id=system_id,
        trigger_type=TriggerType.CUSTOMS,
        government=corporate,
        policy_results=[(restricted_sku, policy_restricted)],
        player=player_state,
        world_seed=world_seed,
        turn=turn + 3,
        cargo_snapshot=CargoSnapshot(illegal_present=False, restricted_unlicensed_present=True),
        logger=logger,
        option=PlayerOption.FLEE,
        bribe_tier="SMALL",
    )

    player_state.set_warrant(system_id, True)
    enforcement_checkpoint(
        system_id=system_id,
        trigger_type=TriggerType.CUSTOMS,
        government=fascist,
        policy_results=[(illegal_sku, policy_illegal)],
        player=player_state,
        world_seed=world_seed,
        turn=turn + 4,
        cargo_snapshot=CargoSnapshot(illegal_present=True, restricted_unlicensed_present=False),
        logger=logger,
        option=PlayerOption.SUBMIT,
        bribe_tier="SMALL",
    )


def _log_system_warning_for_shim(system: System, logger: Logger, turn: int) -> None:
    if system.attributes.get("market") is not None:
        logger.log(
            turn=turn,
            action="galaxy_overview",
            state_change=(
                f"[WARN] system_id={system.system_id} has derived market shim "
                "in attributes; destination markets are authoritative"
            ),
        )


def _log_destination_locations(destination: Destination, logger: Logger, turn: int) -> None:
    if not destination.locations:
        logger.log(
            turn=turn,
            action="galaxy_overview",
            state_change=f"    [LOCATIONS] none",
        )
        return
    labels: list[str] = []
    for location in destination.locations:
        suffix = ""
        if location.notes and "limited" in location.notes:
            suffix = " (limited)"
        labels.append(f"{location.location_type}{suffix}")
    logger.log(
        turn=turn,
        action="galaxy_overview",
        state_change=f"    [LOCATIONS] {labels}",
    )


def _log_destination_market_summary(
    destination_id: str, market: Market, logger: Logger, turn: int
) -> None:
    category_count = len(market.categories)
    produced_total = sum(len(category.produced) for category in market.categories.values())
    consumed_total = sum(len(category.consumed) for category in market.categories.values())
    neutral_total = sum(len(category.neutral) for category in market.categories.values())
    logger.log(
        turn=turn,
        action="galaxy_overview",
        state_change=(
            f"    [MARKET] destination_id={destination_id} categories={category_count} "
            f"produced_skus={produced_total} consumed_skus={consumed_total} "
            f"neutral_skus={neutral_total}"
        ),
    )


if __name__ == "__main__":
    main()
