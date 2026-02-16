import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

import crew_generator as cg  # noqa: E402
from world_state_engine import WorldStateEngine  # noqa: E402


def test_baseline_no_world_state_unchanged() -> None:
    baseline = cg.generate_hireable_crew(world_seed=101, system_id="SYS-A", pool_size=3)
    explicit_none = cg.generate_hireable_crew(
        world_seed=101,
        system_id="SYS-A",
        pool_size=3,
        world_state_engine=None,
    )
    assert baseline == explicit_none


def test_positive_modifier_increases_role_weight() -> None:
    ws = WorldStateEngine()
    ws.register_system("SYS-CREW-POS")
    ws.active_modifiers_by_system["SYS-CREW-POS"] = [
        {
            "domain": "crew",
            "target_type": "id",
            "target_id": "pilot",
            "modifier_type": "crew_weight_percent",
            "modifier_value": 50,
            "source_type": "event",
            "source_id": "E-CREW-POS",
        }
    ]
    baseline = cg.compute_crew_role_weights(system_id="SYS-CREW-POS", world_state_engine=None)
    adjusted = cg.compute_crew_role_weights(system_id="SYS-CREW-POS", world_state_engine=ws)
    assert adjusted["pilot"] == baseline["pilot"] * 1.5


def test_negative_modifier_minus_100_sets_weight_zero() -> None:
    ws = WorldStateEngine()
    ws.register_system("SYS-CREW-NEG")
    ws.active_modifiers_by_system["SYS-CREW-NEG"] = [
        {
            "domain": "crew",
            "target_type": "id",
            "target_id": "pilot",
            "modifier_type": "crew_weight_percent",
            "modifier_value": -100,
            "source_type": "event",
            "source_id": "E-CREW-NEG",
        }
    ]
    adjusted = cg.compute_crew_role_weights(system_id="SYS-CREW-NEG", world_state_engine=ws)
    assert adjusted["pilot"] == 0.0


def test_determinism_fixed_seed_with_modifier() -> None:
    ws = WorldStateEngine()
    ws.register_system("SYS-CREW-DET")
    ws.active_modifiers_by_system["SYS-CREW-DET"] = [
        {
            "domain": "crew",
            "target_type": "id",
            "target_id": "broker",
            "modifier_type": "crew_weight_percent",
            "modifier_value": 75,
            "source_type": "event",
            "source_id": "E-CREW-DET",
        }
    ]
    first = cg.generate_hireable_crew(
        world_seed=999,
        system_id="SYS-CREW-DET",
        pool_size=4,
        world_state_engine=ws,
    )
    second = cg.generate_hireable_crew(
        world_seed=999,
        system_id="SYS-CREW-DET",
        pool_size=4,
        world_state_engine=ws,
    )
    assert first == second
