import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from ship_assembler import assemble_ship  # noqa: E402


def test_assemble_basic_valid_loadout() -> None:
    result = assemble_ship(
        hull_id="civ_t1_midge",
        module_instances=[
            {"module_id": "weapon_energy_mk1"},
            {"module_id": "defense_shielded_mk1"},
            {"module_id": "combat_utility_engine_boost_mk1"},
        ],
    )
    assert result["slot_assignment"]["weapon"]["total_slots_used"] <= (
        result["slots"]["weapon_slots"] + result["slot_assignment"]["untyped_allocations"]["weapon"]
    )
    assert result["slot_assignment"]["defense"]["total_slots_used"] <= (
        result["slots"]["defense_slots"] + result["slot_assignment"]["untyped_allocations"]["defense"]
    )
    assert result["bonuses"]["slot_fill"]["weapon"] == result["slot_assignment"]["weapon"]["total_slots_used"]
    assert isinstance(result["bands"]["effective"]["weapon"], int)
    assert isinstance(result["bands"]["effective"]["defense"], int)
    assert isinstance(result["bands"]["effective"]["engine"], int)
    assert result["bands"]["effective"]["weapon"] >= 0
    assert result["bands"]["effective"]["defense"] >= 0
    assert result["bands"]["effective"]["engine"] >= 0


def test_compact_allows_two_in_one_slot() -> None:
    result = assemble_ship(
        hull_id="civ_t1_midge",
        module_instances=[
            {"module_id": "weapon_energy_mk1", "secondary_tags": ["secondary:compact"]},
            {"module_id": "weapon_kinetic_mk1", "secondary_tags": ["secondary:compact"]},
        ],
    )
    assert result["slot_assignment"]["weapon"]["module_count"] == 2
    assert result["slot_assignment"]["weapon"]["compact_count"] == 2
    assert result["slot_assignment"]["weapon"]["total_slots_used"] == 1
    assert result["bonuses"]["slot_fill"]["weapon"] == 1


def test_invalid_overfill_raises() -> None:
    with pytest.raises(ValueError):
        assemble_ship(
            hull_id="civ_t1_midge",
            module_instances=[
                {"module_id": "weapon_energy_mk1"},
                {"module_id": "weapon_kinetic_mk1"},
            ],
        )


def test_efficient_and_alien_bonus_rules() -> None:
    alien_result = assemble_ship(
        hull_id="aln_t1_trilobite",
        module_instances=[
            {
                "module_id": "weapon_energy_mk1",
                "secondary_tags": ["secondary:efficient", "secondary:alien"],
            }
        ],
    )
    assert alien_result["bonuses"]["module_bonus"]["weapon"] == 3
    assert alien_result["bonuses"]["slot_fill"]["weapon"] == 1

    non_alien_result = assemble_ship(
        hull_id="civ_t1_midge",
        module_instances=[
            {
                "module_id": "weapon_energy_mk1",
                "secondary_tags": ["secondary:efficient", "secondary:alien"],
            }
        ],
    )
    assert non_alien_result["bonuses"]["module_bonus"]["weapon"] == 2


def test_prototype_capacity_penalty_non_experimental() -> None:
    single = assemble_ship(
        hull_id="civ_t1_midge",
        module_instances=[{"module_id": "weapon_energy_mk1", "secondary_tags": ["secondary:prototype"]}],
    )
    assert single["degradation"]["capacity"]["weapon"] == 1

    double = assemble_ship(
        hull_id="civ_t3_mosquito",
        module_instances=[
            {"module_id": "weapon_energy_mk1", "secondary_tags": ["secondary:prototype"]},
            {"module_id": "weapon_kinetic_mk1", "secondary_tags": ["secondary:prototype"]},
        ],
    )
    assert double["degradation"]["capacity"]["weapon"] == 1


def test_prototype_no_penalty_on_experimental() -> None:
    result = assemble_ship(
        hull_id="xb_t2_eclipse",
        module_instances=[
            {"module_id": "weapon_energy_mk1", "secondary_tags": ["secondary:prototype"]},
            {"module_id": "weapon_kinetic_mk1", "secondary_tags": ["secondary:prototype"]},
        ],
    )
    assert result["degradation"]["capacity"]["weapon"] == 2


def test_red_override_when_degradation_meets_capacity() -> None:
    baseline = assemble_ship(
        hull_id="civ_t1_midge",
        module_instances=[{"module_id": "weapon_energy_mk1"}],
    )
    capacity = baseline["degradation"]["capacity"]["weapon"]
    degraded = assemble_ship(
        hull_id="civ_t1_midge",
        module_instances=[{"module_id": "weapon_energy_mk1"}],
        degradation_state={"weapon": capacity, "defense": 0, "engine": 0},
    )
    assert degraded["bands"]["red"]["weapon"] is True
    assert degraded["bands"]["effective"]["weapon"] == 0


def test_hull_max_output_matches_existing_rules() -> None:
    baseline = assemble_ship(hull_id="civ_t1_midge", module_instances=[])
    assert baseline["hull_max"] == 8

    armored = assemble_ship(
        hull_id="civ_t1_midge",
        module_instances=[{"module_id": "defense_armored_mk1"}],
    )
    assert armored["hull_max"] == 9