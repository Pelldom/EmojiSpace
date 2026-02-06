import sys
from pathlib import Path

from economy_data import GOODS
from economy_engine import EconomyEngine
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
    generator = WorldGenerator(seed=seed, system_count=5)
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
    )

    logger.log(
        turn=time_engine.current_turn,
        action="init",
        state_change=f"seed={seed} start_location={start_system_id}",
    )

    print("Initial prices:")
    _print_prices(sector, economy_engine)
    print("Population:")
    _print_population(sector, economy_engine)

    system_ids = sector.system_ids()
    if len(system_ids) > 1:
        turn_loop.execute_move(MoveAction(target_system_id=system_ids[1]))
    turn_loop.execute_buy(BuyAction(good_id="FOOD"))
    turn_loop.execute_buy(BuyAction(good_id="MEDICINE"))
    turn_loop.execute_sell(SellAction(good_id="FOOD"))
    if len(system_ids) > 2:
        turn_loop.execute_move(MoveAction(target_system_id=system_ids[2]))
        turn_loop.execute_sell(SellAction(good_id="MEDICINE"))

    print("Prices after actions:")
    _print_prices(sector, economy_engine)


def _print_population(sector: Sector, economy_engine: EconomyEngine) -> None:
    for system in sector.systems:
        level, scalar, values = economy_engine.population_summary(system.system_id)
        print(f"{system.system_id} {system.name} population_level={level} scalar={scalar:.2f}")
        for good in GOODS:
            data = values[good.good_id]
            print(
                "  "
                f"{good.good_id} "
                f"production={data['production']:.2f} "
                f"consumption={data['consumption']:.2f} "
                f"capacity={data['capacity']:.2f}"
            )


def _print_prices(sector: Sector, economy_engine: EconomyEngine) -> None:
    for system in sector.systems:
        parts = []
        for good in GOODS:
            price = economy_engine.price(system.system_id, good.good_id)
            parts.append(f"{good.good_id}={price:.2f}")
        print(f"{system.system_id} {system.name} " + " ".join(parts))


if __name__ == "__main__":
    main()
