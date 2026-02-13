import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from data_loader import load_hulls, load_modules  # noqa: E402
from shipdock_inventory import generate_shipdock_inventory  # noqa: E402


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
