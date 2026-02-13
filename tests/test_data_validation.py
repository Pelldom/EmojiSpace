import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from data_loader import load_hulls, load_modules  # noqa: E402


def test_hulls_load_success() -> None:
    payload = load_hulls()
    assert isinstance(payload, dict)
    assert isinstance(payload["hulls"], list)
    assert len(payload["hulls"]) > 0


def test_modules_load_success() -> None:
    payload = load_modules()
    assert isinstance(payload, dict)
    assert isinstance(payload["modules"], list)
    assert len(payload["modules"]) > 0


def test_module_bonus_cap() -> None:
    payload = load_modules()
    for module in payload["modules"]:
        numeric_bonus = module.get("numeric_bonus", {})
        for value in numeric_bonus.values():
            assert value <= 2


def test_crew_band_validation() -> None:
    payload = load_hulls()
    crew_bands = {
        1: (0, 1),
        2: (1, 2),
        3: (2, 3),
        4: (3, 4),
        5: (4, 5),
    }
    exceptions = {
        "frg_t1_carpenter_ant": 2,
        "mil_t1_paper_wasp": 2,
    }
    for hull in payload["hulls"]:
        hull_id = hull["hull_id"]
        if hull_id in exceptions:
            assert hull["crew_capacity"] == exceptions[hull_id]
            continue
        low, high = crew_bands[hull["tier"]]
        assert low <= hull["crew_capacity"] <= high


def test_display_names_present() -> None:
    payload = load_modules()
    for module in payload["modules"]:
        display_names = module["display_names"]
        assert isinstance(display_names, list)
        assert len(display_names) >= 1
