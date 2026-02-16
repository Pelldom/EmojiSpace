import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from data_loader import load_hulls, load_modules  # noqa: E402
from shipdock_inventory import generate_shipdock_inventory  # noqa: E402
from world_state_engine import WorldStateEngine  # noqa: E402


def test_deterministic_inventory() -> None:
    first = generate_shipdock_inventory(world_seed=12345, system_id="SYS-A", system_population=3)
    second = generate_shipdock_inventory(world_seed=12345, system_id="SYS-A", system_population=3)
    assert first == second


def test_population_scaling_limits() -> None:
    module_max = {1: 2, 2: 3, 3: 5, 4: 6, 5: 8}
    hull_max = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6}
    for population in (1, 2, 3, 4, 5):
        inventory = generate_shipdock_inventory(world_seed=999, system_id=f"SYS-{population}", system_population=population)
        assert len(inventory["modules"]) <= module_max[population]
        assert len(inventory["hulls"]) <= hull_max[population]


def test_stock_gate_zero_possible() -> None:
    found = None
    for seed in range(0, 5000):
        inventory = generate_shipdock_inventory(world_seed=seed, system_id="SYS-ZERO", system_population=1)
        if not inventory["modules"] or not inventory["hulls"]:
            found = inventory
            break
    assert found is not None
    assert isinstance(found["modules"], list)
    assert isinstance(found["hulls"], list)


def test_rare_caps_enforced() -> None:
    modules_by_id = {entry["module_id"]: entry for entry in load_modules()["modules"]}
    for population, cap in ((1, 0), (2, 0), (3, 1)):
        inventory = generate_shipdock_inventory(world_seed=4321, system_id=f"SYS-RARE-{population}", system_population=population)
        rare_count = sum(1 for entry in inventory["modules"] if modules_by_id[entry["module_id"]]["rarity_tier"] == "rare")
        assert rare_count <= cap


def test_purchase_bans_enforced() -> None:
    modules_by_id = {entry["module_id"]: entry for entry in load_modules()["modules"]}
    hulls_by_id = {entry["hull_id"]: entry for entry in load_hulls()["hulls"]}
    inventory = generate_shipdock_inventory(world_seed=2024, system_id="SYS-BANS", system_population=5)

    for module in inventory["modules"]:
        source = modules_by_id[module["module_id"]]
        secondary_values = []
        for key in ("secondary", "secondary_tags", "secondaries", "secondary_defaults"):
            raw = source.get(key)
            if isinstance(raw, str):
                secondary_values.append(raw)
            elif isinstance(raw, list):
                secondary_values.extend(str(entry) for entry in raw)
        joined = " ".join(secondary_values)
        assert "prototype" not in joined
        assert "alien" not in joined

    for hull in inventory["hulls"]:
        source = hulls_by_id[hull["hull_id"]]
        flags = set(source.get("availability_flags", []))
        assert "experimental" not in flags
        assert "alien" not in flags


def _seed_with_stock(*, population: int) -> int:
    for seed in range(0, 5000):
        inventory = generate_shipdock_inventory(world_seed=seed, system_id="SYS-STOCK", system_population=population)
        if inventory["hulls"] and inventory["modules"]:
            return seed
    raise AssertionError("Could not find deterministic seed with both hull and module stock.")


def test_baseline_no_world_state_matches_none() -> None:
    seed = _seed_with_stock(population=5)
    baseline = generate_shipdock_inventory(world_seed=seed, system_id="SYS-BASELINE", system_population=5)
    explicit_none = generate_shipdock_inventory(
        world_seed=seed,
        system_id="SYS-BASELINE",
        system_population=5,
        world_state_engine=None,
    )
    assert baseline == explicit_none


def test_positive_ship_modifier_increases_weight_and_changes_selection(monkeypatch) -> None:
    import shipdock_inventory as inv

    monkeypatch.setitem(inv.MODULE_STOCK_CHANCE, 5, 0.0)
    monkeypatch.setitem(inv.HULL_STOCK_CHANCE, 5, 1.0)
    monkeypatch.setitem(inv.HULL_MAX_COUNT, 5, 1)
    monkeypatch.setattr(
        inv,
        "_eligible_hulls",
        lambda: [
            {"hull_id": "hull_a", "base_price_credits": 1000, "rarity_weight": 100, "traits": []},
            {"hull_id": "hull_b", "base_price_credits": 1000, "rarity_weight": 100, "traits": []},
        ],
    )

    ws = WorldStateEngine()
    ws.register_system("SYS-HULL")
    ws.active_modifiers_by_system["SYS-HULL"] = [
        {
            "domain": "ships",
            "target_type": "id",
            "target_id": "hull_b",
            "modifier_type": "ship_weight_percent",
            "modifier_value": 50,
            "source_type": "event",
            "source_id": "E-SHIP",
        }
    ]
    weighted_calls: list[list[float]] = []
    original_weighted_pick_index = inv._weighted_pick_index

    def _capture(weights, rng):
        weighted_calls.append(list(weights))
        return original_weighted_pick_index(weights, rng)

    monkeypatch.setattr(inv, "_weighted_pick_index", _capture)
    generate_shipdock_inventory(world_seed=5, system_id="SYS-HULL", system_population=5, world_state_engine=ws)
    assert weighted_calls
    assert weighted_calls[0] == [100.0, 150.0]


def test_negative_ship_modifier_sets_weight_to_zero(monkeypatch) -> None:
    import shipdock_inventory as inv

    monkeypatch.setitem(inv.MODULE_STOCK_CHANCE, 5, 0.0)
    monkeypatch.setitem(inv.HULL_STOCK_CHANCE, 5, 1.0)
    monkeypatch.setitem(inv.HULL_MAX_COUNT, 5, 1)
    monkeypatch.setattr(
        inv,
        "_eligible_hulls",
        lambda: [
            {"hull_id": "hull_a", "base_price_credits": 1000, "rarity_weight": 100, "traits": []},
            {"hull_id": "hull_b", "base_price_credits": 1000, "rarity_weight": 100, "traits": []},
        ],
    )

    ws = WorldStateEngine()
    ws.register_system("SYS-HULL-NEG")
    ws.active_modifiers_by_system["SYS-HULL-NEG"] = [
        {
            "domain": "ships",
            "target_type": "id",
            "target_id": "hull_a",
            "modifier_type": "ship_weight_percent",
            "modifier_value": -100,
            "source_type": "event",
            "source_id": "E-SHIP-NEG",
        }
    ]
    weighted_calls: list[list[float]] = []
    original_weighted_pick_index = inv._weighted_pick_index

    def _capture(weights, rng):
        weighted_calls.append(list(weights))
        return original_weighted_pick_index(weights, rng)

    monkeypatch.setattr(inv, "_weighted_pick_index", _capture)
    generate_shipdock_inventory(
        world_seed=5,
        system_id="SYS-HULL-NEG",
        system_population=5,
        world_state_engine=ws,
    )
    assert weighted_calls
    assert weighted_calls[0] == [0.0, 100.0]


def test_module_weight_modifier_applies(monkeypatch) -> None:
    import shipdock_inventory as inv

    monkeypatch.setitem(inv.MODULE_STOCK_CHANCE, 5, 1.0)
    monkeypatch.setitem(inv.HULL_STOCK_CHANCE, 5, 0.0)
    monkeypatch.setitem(inv.MODULE_MAX_COUNT, 5, 1)
    monkeypatch.setitem(inv.MODULE_RARE_CAP, 5, 5)
    monkeypatch.setattr(
        inv,
        "_eligible_modules",
        lambda: [
            {"module_id": "mod_a", "base_price_credits": 1000, "rarity_weight": 100, "rarity_tier": "common", "primary_tag": "combat:weapon_energy"},
            {"module_id": "mod_b", "base_price_credits": 1000, "rarity_weight": 100, "rarity_tier": "common", "primary_tag": "combat:weapon_kinetic"},
        ],
    )

    ws = WorldStateEngine()
    ws.register_system("SYS-MOD")
    ws.active_modifiers_by_system["SYS-MOD"] = [
        {
            "domain": "modules",
            "target_type": "id",
            "target_id": "mod_b",
            "modifier_type": "module_weight_percent",
            "modifier_value": 50,
            "source_type": "event",
            "source_id": "E-MOD",
        }
    ]
    weighted_calls: list[list[float]] = []
    original_weighted_pick_index = inv._weighted_pick_index

    def _capture(weights, rng):
        weighted_calls.append(list(weights))
        return original_weighted_pick_index(weights, rng)

    monkeypatch.setattr(inv, "_weighted_pick_index", _capture)
    for seed in range(0, 200):
        weighted_calls.clear()
        generate_shipdock_inventory(world_seed=seed, system_id="SYS-MOD", system_population=5, world_state_engine=ws)
        if weighted_calls:
            break
    assert weighted_calls
    assert weighted_calls[0] == [100.0, 150.0]


def test_shipdock_inventory_deterministic_with_world_state_modifiers() -> None:
    ws = WorldStateEngine()
    ws.register_system("SYS-DET")
    ws.active_modifiers_by_system["SYS-DET"] = [
        {
            "domain": "ships",
            "target_type": "ALL",
            "target_id": None,
            "modifier_type": "ship_weight_percent",
            "modifier_value": 20,
            "source_type": "event",
            "source_id": "E-DET-S",
        },
        {
            "domain": "modules",
            "target_type": "ALL",
            "target_id": None,
            "modifier_type": "module_weight_percent",
            "modifier_value": -25,
            "source_type": "event",
            "source_id": "E-DET-M",
        },
    ]
    first = generate_shipdock_inventory(
        world_seed=2048,
        system_id="SYS-DET",
        system_population=5,
        world_state_engine=ws,
    )
    second = generate_shipdock_inventory(
        world_seed=2048,
        system_id="SYS-DET",
        system_population=5,
        world_state_engine=ws,
    )
    assert first == second
