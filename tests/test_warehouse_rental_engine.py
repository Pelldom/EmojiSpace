import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from game_engine import GameEngine  # noqa: E402


def _ensure_warehouse_location(engine: GameEngine) -> tuple[str, str]:
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    destination = current_system.destinations[0]
    warehouse_location_id = None
    for location in list(getattr(destination, "locations", []) or []):
        if str(getattr(location, "location_type", "")) == "warehouse":
            warehouse_location_id = str(getattr(location, "location_id"))
            break
    if warehouse_location_id is None:
        synthetic = type("SyntheticLocation", (), {})()
        synthetic.location_id = "warehouse_test_location"
        synthetic.location_type = "warehouse"
        destination.locations.append(synthetic)
        warehouse_location_id = synthetic.location_id
    engine.player_state.current_destination_id = destination.destination_id
    engine.player_state.current_location_id = destination.destination_id
    enter = engine.execute({"type": "enter_location", "location_id": warehouse_location_id})
    assert enter["ok"] is True
    return destination.destination_id, warehouse_location_id


def test_warehouse_rent_increases_capacity() -> None:
    engine = GameEngine(world_seed=12345)
    destination_id, _ = _ensure_warehouse_location(engine)
    before_capacity = int((engine.player_state.warehouses.get(destination_id, {}) or {}).get("capacity", 0))

    result = engine.execute(
        {"type": "location_action", "action_id": "warehouse_rent", "action_kwargs": {"units": 3}}
    )

    assert result["ok"] is True
    after_capacity = int((engine.player_state.warehouses.get(destination_id, {}) or {}).get("capacity", 0))
    assert after_capacity == before_capacity + 3


def test_warehouse_deposit_reduces_cargo() -> None:
    engine = GameEngine(world_seed=12345)
    destination_id, _ = _ensure_warehouse_location(engine)
    engine.player_state.cargo_by_ship["active"] = {"sku_test": 4}
    rent = engine.execute({"type": "location_action", "action_id": "warehouse_rent", "action_kwargs": {"units": 5}})
    assert rent["ok"] is True

    deposit = engine.execute(
        {
            "type": "location_action",
            "action_id": "warehouse_deposit",
            "action_kwargs": {"sku_id": "sku_test", "quantity": 3},
        }
    )
    assert deposit["ok"] is True
    assert int(engine.player_state.cargo_by_ship["active"].get("sku_test", 0)) == 1
    goods = ((engine.player_state.warehouses.get(destination_id, {}) or {}).get("goods", {}) or {})
    assert int(goods.get("sku_test", 0)) == 3


def test_warehouse_deposit_exceeding_capacity_fails() -> None:
    engine = GameEngine(world_seed=12345)
    _, _ = _ensure_warehouse_location(engine)
    engine.player_state.cargo_by_ship["active"] = {"sku_test": 5}
    assert engine.execute(
        {"type": "location_action", "action_id": "warehouse_rent", "action_kwargs": {"units": 1}}
    )["ok"] is True

    deposit = engine.execute(
        {
            "type": "location_action",
            "action_id": "warehouse_deposit",
            "action_kwargs": {"sku_id": "sku_test", "quantity": 2},
        }
    )
    assert deposit["ok"] is False
    assert deposit["error"] == "warehouse_capacity_exceeded"


def test_warehouse_withdraw_restores_cargo() -> None:
    engine = GameEngine(world_seed=12345)
    destination_id, _ = _ensure_warehouse_location(engine)
    engine.player_state.cargo_by_ship["active"] = {"sku_test": 2}
    assert engine.execute(
        {"type": "location_action", "action_id": "warehouse_rent", "action_kwargs": {"units": 3}}
    )["ok"] is True
    assert engine.execute(
        {
            "type": "location_action",
            "action_id": "warehouse_deposit",
            "action_kwargs": {"sku_id": "sku_test", "quantity": 2},
        }
    )["ok"] is True

    withdraw = engine.execute(
        {
            "type": "location_action",
            "action_id": "warehouse_withdraw",
            "action_kwargs": {"sku_id": "sku_test", "quantity": 1},
        }
    )
    assert withdraw["ok"] is True
    assert int(engine.player_state.cargo_by_ship["active"].get("sku_test", 0)) == 1
    goods = ((engine.player_state.warehouses.get(destination_id, {}) or {}).get("goods", {}) or {})
    assert int(goods.get("sku_test", 0)) == 1


def test_warehouse_withdraw_exceeding_stored_fails() -> None:
    engine = GameEngine(world_seed=12345)
    _, _ = _ensure_warehouse_location(engine)
    engine.player_state.cargo_by_ship["active"] = {"sku_test": 2}
    assert engine.execute(
        {"type": "location_action", "action_id": "warehouse_rent", "action_kwargs": {"units": 3}}
    )["ok"] is True
    assert engine.execute(
        {
            "type": "location_action",
            "action_id": "warehouse_deposit",
            "action_kwargs": {"sku_id": "sku_test", "quantity": 1},
        }
    )["ok"] is True

    withdraw = engine.execute(
        {
            "type": "location_action",
            "action_id": "warehouse_withdraw",
            "action_kwargs": {"sku_id": "sku_test", "quantity": 2},
        }
    )
    assert withdraw["ok"] is False
    assert withdraw["error"] == "insufficient_stored_goods"


def test_warehouse_billing_applied_on_time_advance() -> None:
    engine = GameEngine(world_seed=12345)
    _, _ = _ensure_warehouse_location(engine)
    active_ship = engine.fleet_by_id[engine.player_state.active_ship_id]
    active_ship.crew = []
    engine.player_state.insurance_policies = []
    assert engine.execute(
        {"type": "location_action", "action_id": "warehouse_rent", "action_kwargs": {"units": 4}}
    )["ok"] is True
    credits_before = int(engine.player_state.credits)

    wait = engine.execute({"type": "wait", "days": 3})
    assert wait["ok"] is True
    assert int(engine.player_state.credits) == credits_before - (4 * 2 * 3)


def test_warehouse_cancel_deletes_and_forfeits() -> None:
    engine = GameEngine(world_seed=12345)
    destination_id, _ = _ensure_warehouse_location(engine)
    engine.player_state.cargo_by_ship["active"] = {"sku_test": 2}
    assert engine.execute(
        {"type": "location_action", "action_id": "warehouse_rent", "action_kwargs": {"units": 2}}
    )["ok"] is True
    assert engine.execute(
        {
            "type": "location_action",
            "action_id": "warehouse_deposit",
            "action_kwargs": {"sku_id": "sku_test", "quantity": 2},
        }
    )["ok"] is True
    assert destination_id in engine.player_state.warehouses

    cancel = engine.execute({"type": "warehouse_cancel", "destination_id": destination_id})
    assert cancel["ok"] is True
    assert destination_id not in engine.player_state.warehouses
