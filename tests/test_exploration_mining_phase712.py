"""Phase 7.12 - Exploration and Mining: harvestable, resolvers, emoji_id, no *_stub."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from data_catalog import load_data_catalog  # noqa: E402
from exploration_resolver import resolve_exploration, ExplorationResult  # noqa: E402
from mining_resolver import resolve_mining, MiningResult, _yield_multiplier, YIELD_MULTIPLIER_TABLE, MULTIPLIER_FLOOR  # noqa: E402
from game_engine import GameEngine  # noqa: E402
import encounter_generator as eg  # noqa: E402


def test_harvestable_flag_correctly_applied() -> None:
    """Goods: ORE, METAL, CHEMICALS (except experimental_serums), standard_fuel are harvestable; others false."""
    catalog = load_data_catalog()
    # Contract: harvestable true for ORE, METAL, CHEMICALS except experimental_serums, and sku standard_fuel
    for good in catalog.goods:
        if good.category == "ORE":
            assert good.harvestable, f"ORE good {good.sku} must be harvestable"
        elif good.category == "METAL":
            assert good.harvestable, f"METAL good {good.sku} must be harvestable"
        elif good.category == "CHEMICALS":
            assert good.harvestable == (good.sku != "experimental_serums"), (
                f"CHEMICALS {good.sku}: harvestable must be False only for experimental_serums"
            )
        elif good.sku == "standard_fuel":
            assert good.harvestable, "standard_fuel must be harvestable"
        else:
            assert not good.harvestable, f"Good {good.sku} ({good.category}) must not be harvestable unless contract"


def test_mining_diminishing_returns_behavior() -> None:
    """Mining multiplier: 0->1.0, 1->0.8, 2->0.6, 3->0.4, 4->0.2, 5->0.1, 6+->0.05."""
    assert _yield_multiplier(0) == 1.0
    assert _yield_multiplier(1) == 0.8
    assert _yield_multiplier(2) == 0.6
    assert _yield_multiplier(3) == 0.4
    assert _yield_multiplier(4) == 0.2
    assert _yield_multiplier(5) == 0.1
    assert _yield_multiplier(6) == MULTIPLIER_FLOOR
    assert _yield_multiplier(99) == MULTIPLIER_FLOOR
    catalog = load_data_catalog()
    dest_id = "dest_mining_test"
    player_id = "player_1"
    for attempt_index in range(7):  # 0..6
        mining_attempts = {dest_id: attempt_index}
        result, new_attempts = resolve_mining(
            world_seed=42,
            destination_id=dest_id,
            player_id=player_id,
            mining_attempts=mining_attempts,
            player_ship_TR_band=10,
            catalog=catalog,
            current_cargo={},
            physical_cargo_capacity=1000,
        )
        expected_mult = YIELD_MULTIPLIER_TABLE.get(attempt_index, MULTIPLIER_FLOOR)
        assert result.multiplier == expected_mult, (attempt_index, result.multiplier, expected_mult)
        assert result.attempt_number == attempt_index + 1


def test_mining_diminishing_returns_attempt_6_and_10_use_floor() -> None:
    """Attempt 6 and attempt 10 both use 0.05 multiplier (extended depletion floor)."""
    assert MULTIPLIER_FLOOR == 0.05
    assert _yield_multiplier(6) == 0.05
    assert _yield_multiplier(10) == 0.05
    catalog = load_data_catalog()
    dest_id = "dest_floor_test"
    player_id = "p1"
    for attempt_index in (6, 10):
        mining_attempts = {dest_id: attempt_index}
        result, _ = resolve_mining(
            world_seed=99,
            destination_id=dest_id,
            player_id=player_id,
            mining_attempts=mining_attempts,
            player_ship_TR_band=100,
            catalog=catalog,
            current_cargo={},
            physical_cargo_capacity=10000,
        )
        assert result.multiplier == 0.05, f"attempt_index {attempt_index} should yield multiplier 0.05, got {result.multiplier}"
        assert result.attempt_number == attempt_index + 1


def test_exploration_progress_increments() -> None:
    """Exploration: attempts increment; on success progress increments."""
    dest_id = "dest_explore_test"
    player_id = "player_1"
    attempts = {}
    progress = {}
    result, new_attempts, new_progress = resolve_exploration(
        world_seed=999,
        destination_id=dest_id,
        player_id=player_id,
        exploration_attempts=attempts,
        exploration_progress=progress,
    )
    assert isinstance(result, ExplorationResult)
    assert new_attempts[dest_id] == 1
    assert result.stage_before == 0
    if result.success:
        assert new_progress[dest_id] == 1
        assert result.stage_after == 1
    else:
        assert new_progress.get(dest_id, 0) == 0
        assert result.stage_after == 0
    assert 0 <= result.rng_roll <= 1.0


def test_local_activity_exactly_one_encounter_roll() -> None:
    """With travel_context.mode == local_activity, generate_travel_encounters returns at most 1 encounter."""
    encounters = eg.generate_travel_encounters(
        world_seed=1,
        travel_id="local_act_1",
        population=100,
        system_government_id="democracy",
        active_situations=[],
        travel_context={"mode": "local_activity"},
    )
    assert len(encounters) <= 1, "local_activity must cap at one encounter roll"


def test_emoji_id_persists_on_generated_destinations() -> None:
    """Generated exploration_site and resource_field destinations have emoji_id set (defaults)."""
    engine = GameEngine(world_seed=12345, config={"system_count": 10})
    for system in engine.sector.systems:
        for dest in system.destinations:
            emoji_id = getattr(dest, "emoji_id", None)
            assert emoji_id is not None, f"Destination {dest.destination_id} missing emoji_id attribute"
            if dest.destination_type == "exploration_site":
                assert emoji_id == "location_unknown", (
                    f"exploration_site default emoji_id must be location_unknown, got {emoji_id}"
                )
            elif dest.destination_type == "resource_field":
                assert emoji_id == "goods_category_ore", (
                    f"resource_field default emoji_id must be goods_category_ore, got {emoji_id}"
                )


def test_no_stub_destination_types_in_generated_world() -> None:
    """Generated world must not use explorable_stub or mining_stub; only exploration_site and resource_field."""
    engine = GameEngine(world_seed=12345, config={"system_count": 20})
    stub_types = {"explorable_stub", "mining_stub"}
    for system in engine.sector.systems:
        for dest in system.destinations:
            assert dest.destination_type not in stub_types, (
                f"Generated destination must not have type {dest.destination_type}"
            )


def test_mining_attempts_increment_on_failure_false_cargo_capacity() -> None:
    """When mining_attempts_increment_on_failure is False, cargo capacity failure does not increment attempts."""
    catalog = load_data_catalog()
    dest_id = "dest_cap_fail"
    player_id = "p1"
    mining_attempts = {dest_id: 0}  # first attempt would get multiplier 1.0, yield > 0
    # Zero capacity so we get insufficient_cargo_capacity
    result, new_attempts = resolve_mining(
        world_seed=1,
        destination_id=dest_id,
        player_id=player_id,
        mining_attempts=mining_attempts,
        player_ship_TR_band=10,
        catalog=catalog,
        current_cargo={},
        physical_cargo_capacity=0,
        increment_on_failure=False,
    )
    assert result.success is False
    assert result.message == "insufficient_cargo_capacity"
    assert new_attempts[dest_id] == 0, "attempts must not increment when increment_on_failure=False and capacity fail"


def test_mining_attempts_increment_on_failure_true_cargo_capacity() -> None:
    """When mining_attempts_increment_on_failure is True, cargo capacity failure increments attempts."""
    catalog = load_data_catalog()
    dest_id = "dest_cap_fail_inc"
    player_id = "p1"
    mining_attempts = {dest_id: 0}
    result, new_attempts = resolve_mining(
        world_seed=1,
        destination_id=dest_id,
        player_id=player_id,
        mining_attempts=mining_attempts,
        player_ship_TR_band=10,
        catalog=catalog,
        current_cargo={},
        physical_cargo_capacity=0,
        increment_on_failure=True,
    )
    assert result.success is False
    assert result.message == "insufficient_cargo_capacity"
    assert new_attempts[dest_id] == 1, "attempts must increment when increment_on_failure=True and capacity fail"
