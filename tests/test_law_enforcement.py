import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from government_law_engine import GovernmentPolicyResult, LegalityStatus, RiskTier  # noqa: E402
from government_registry import GovernmentRegistry  # noqa: E402
from law_enforcement import (  # noqa: E402
    PlayerOption,
    TriggerType,
    band_index_from_1_100,
    compute_bribery_chance,
    compute_inspection_score,
    enforcement_checkpoint,
    get_consequences,
)
from player_state import PlayerState  # noqa: E402
from market import Market  # noqa: E402
from world_generator import Sector, System  # noqa: E402
from turn_loop import TurnLoop, MoveAction  # noqa: E402
from economy_engine import EconomyEngine  # noqa: E402
from government_law_engine import GovernmentLawEngine  # noqa: E402
from data_catalog import load_data_catalog  # noqa: E402
from time_engine import TimeEngine  # noqa: E402


class NullLogger:
    def log(self, turn: int, action: str, state_change: str) -> None:
        return


def test_inspection_determinism() -> None:
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government = registry.get_government("anarchic")
    player = PlayerState(start_system_id="SYS-TEST")
    player.set_reputation("SYS-TEST", 50)
    player.set_heat("SYS-TEST", 10)
    policy = GovernmentPolicyResult(
        legality_state=LegalityStatus.LEGAL,
        risk_tier=RiskTier.NONE,
        consumed_tags=[],
    )
    logger = NullLogger()
    event1 = enforcement_checkpoint(
        system_id="SYS-TEST",
        trigger_type=TriggerType.BORDER,
        government=government,
        policy_results=[("sku", policy)],
        player=player,
        world_seed=12345,
        turn=1,
        cargo_snapshot=_cargo(False, False),
        logger=logger,
    )
    event2 = enforcement_checkpoint(
        system_id="SYS-TEST",
        trigger_type=TriggerType.BORDER,
        government=government,
        policy_results=[("sku", policy)],
        player=player,
        world_seed=12345,
        turn=1,
        cargo_snapshot=_cargo(False, False),
        logger=logger,
    )
    assert (event1 is None) == (event2 is None)


def test_warrant_does_not_change_inspection_score() -> None:
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government = registry.get_government("anarchic")
    player = PlayerState(start_system_id="SYS-TEST")
    player.set_reputation("SYS-TEST", 50)
    player.set_heat("SYS-TEST", 10)
    base_score = compute_inspection_score(
        government,
        rep_band=band_index_from_1_100(player.get_reputation("SYS-TEST")),
        heat_band=band_index_from_1_100(max(1, player.get_heat("SYS-TEST"))),
    )
    player.set_warrant("SYS-TEST", True)
    warrant_score = compute_inspection_score(
        government,
        rep_band=band_index_from_1_100(player.get_reputation("SYS-TEST")),
        heat_band=band_index_from_1_100(max(1, player.get_heat("SYS-TEST"))),
    )
    assert base_score == warrant_score


def test_fines_do_not_change_inspection_score() -> None:
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government = registry.get_government("anarchic")
    player = PlayerState(start_system_id="SYS-TEST")
    player.set_reputation("SYS-TEST", 50)
    player.set_heat("SYS-TEST", 10)
    base_score = compute_inspection_score(
        government,
        rep_band=band_index_from_1_100(player.get_reputation("SYS-TEST")),
        heat_band=band_index_from_1_100(max(1, player.get_heat("SYS-TEST"))),
    )
    player.add_fines("SYS-TEST", 100)
    fines_score = compute_inspection_score(
        government,
        rep_band=band_index_from_1_100(player.get_reputation("SYS-TEST")),
        heat_band=band_index_from_1_100(max(1, player.get_heat("SYS-TEST"))),
    )
    assert base_score == fines_score


def test_bribery_chance_bounds() -> None:
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government = registry.get_government("anarchic")
    chance = compute_bribery_chance(
        government,
        enforcement_strength=government.enforcement_strength,
        bribe_tier="LARGE",
        post_inspection=True,
    )
    assert 0 <= chance <= 85


def test_warrant_forces_arrest_on_inspection() -> None:
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government = registry.get_government("anarchic")
    player = PlayerState(start_system_id="SYS-TEST")
    player.set_reputation("SYS-TEST", 1)
    player.set_heat("SYS-TEST", 100)
    player.set_warrant("SYS-TEST", True)
    policy = GovernmentPolicyResult(
        legality_state=LegalityStatus.ILLEGAL,
        risk_tier=RiskTier.SEVERE,
        consumed_tags=[],
    )
    outcome = enforcement_checkpoint(
        system_id="SYS-TEST",
        trigger_type=TriggerType.CUSTOMS,
        government=government,
        policy_results=[("sku", policy)],
        player=player,
        world_seed=1,
        turn=1,
        cargo_snapshot=_cargo(True, True),
        logger=NullLogger(),
    )
    assert outcome is not None
    assert outcome.arrested is True


def test_heat_decay_per_turn() -> None:
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government_ids = registry.government_ids()
    dummy_market = Market(categories={}, primary_economy="trade", secondary_economies=())
    sector = Sector(
        systems=[
            System(
                system_id="SYS-A",
                name="A",
                attributes={"government_id": government_ids[0], "profile_id": "AGRICULTURAL", "market": dummy_market},
                neighbors=[],
            ),
            System(
                system_id="SYS-B",
                name="B",
                attributes={"government_id": government_ids[0], "profile_id": "AGRICULTURAL", "market": dummy_market},
                neighbors=[],
            ),
        ]
    )
    player = PlayerState(start_system_id="SYS-A")
    player.set_heat("SYS-A", 50)
    player.set_heat("SYS-B", 50)
    turn_loop = TurnLoop(
        time_engine=TimeEngine(),
        sector=sector,
        player_state=player,
        logger=NullLogger(),
        economy_engine=EconomyEngine(sector=sector, logger=NullLogger()),
        law_engine=GovernmentLawEngine(registry=registry, logger=NullLogger(), seed=1),
        catalog=load_data_catalog(),
        government_registry=registry,
        world_seed=1,
    )
    turn_loop.execute_move(MoveAction(target_system_id="SYS-B"))
    assert player.get_heat("SYS-B") == 40
    assert player.get_heat("SYS-A") == 30


def test_restricted_checked_only_at_customs() -> None:
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    gov = registry.get_government("communist")
    dummy_market = Market(categories={}, primary_economy="trade", secondary_economies=())
    sector = Sector(
        systems=[
            System(
                system_id="SYS-A",
                name="A",
                attributes={"government_id": gov.id, "profile_id": "AGRICULTURAL", "market": dummy_market},
                neighbors=[],
            ),
            System(
                system_id="SYS-B",
                name="B",
                attributes={"government_id": gov.id, "profile_id": "AGRICULTURAL", "market": dummy_market},
                neighbors=[],
            ),
        ]
    )
    logger = CollectLogger()
    player = PlayerState(start_system_id="SYS-A")
    player.buy("luxury_basic_rations")
    turn_loop = TurnLoop(
        time_engine=TimeEngine(),
        sector=sector,
        player_state=player,
        logger=logger,
        economy_engine=EconomyEngine(sector=sector, logger=logger),
        law_engine=GovernmentLawEngine(registry=registry, logger=logger, seed=1),
        catalog=load_data_catalog(),
        government_registry=registry,
        world_seed=1,
    )
    turn_loop.execute_move(MoveAction(target_system_id="SYS-B"))
    assert not any("law_enforcement_checkpoint" in entry for entry in logger.entries)


def test_fines_added_on_inspection() -> None:
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government = registry.get_government("fascist")
    player = PlayerState(start_system_id="SYS-TEST")
    player.set_reputation("SYS-TEST", 1)
    player.set_heat("SYS-TEST", 100)
    player.add_fines("SYS-TEST", 123)
    policy = GovernmentPolicyResult(
        legality_state=LegalityStatus.ILLEGAL,
        risk_tier=RiskTier.SEVERE,
        consumed_tags=[],
    )
    outcome = enforcement_checkpoint(
        system_id="SYS-TEST",
        trigger_type=TriggerType.CUSTOMS,
        government=government,
        policy_results=[("sku", policy)],
        player=player,
        world_seed=1,
        turn=1,
        cargo_snapshot=_cargo(True, True),
        logger=NullLogger(),
    )
    assert outcome is not None
    expected_fine = get_consequences("illegal_goods_possession", outcome.severity_final)["fine"]["base"]
    assert outcome.fines_added == expected_fine + 123


def test_reputation_delta_from_consequences() -> None:
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government = registry.get_government("fascist")
    player = PlayerState(start_system_id="SYS-TEST")
    player.set_reputation("SYS-TEST", 50)
    player.set_heat("SYS-TEST", 100)
    policy = GovernmentPolicyResult(
        legality_state=LegalityStatus.ILLEGAL,
        risk_tier=RiskTier.SEVERE,
        consumed_tags=[],
    )
    outcome = enforcement_checkpoint(
        system_id="SYS-TEST",
        trigger_type=TriggerType.CUSTOMS,
        government=government,
        policy_results=[("sku", policy)],
        player=player,
        world_seed=1,
        turn=1,
        cargo_snapshot=_cargo(True, True),
        logger=NullLogger(),
    )
    assert outcome is not None
    expected = get_consequences("illegal_goods_possession", outcome.severity_final)["reputation"]
    assert player.get_reputation("SYS-TEST") == 50 + {"negligible": 0, "minor": -2, "moderate": -5, "major": -10, "extreme": -20}[expected]


def test_dominant_violation_priority_illegal_over_stolen() -> None:
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government = registry.get_government("fascist")
    player = PlayerState(start_system_id="SYS-TEST")
    player.set_reputation("SYS-TEST", 1)
    player.set_heat("SYS-TEST", 100)
    policy = GovernmentPolicyResult(
        legality_state=LegalityStatus.ILLEGAL,
        risk_tier=RiskTier.SEVERE,
        consumed_tags=["stolen"],
    )
    outcome = enforcement_checkpoint(
        system_id="SYS-TEST",
        trigger_type=TriggerType.CUSTOMS,
        government=government,
        policy_results=[("sku", policy)],
        player=player,
        world_seed=1,
        turn=1,
        cargo_snapshot=_cargo(True, False),
        logger=NullLogger(),
    )
    assert outcome is not None
    assert "illegal_goods_possession" in outcome.consequences_applied


def test_border_restricted_no_confiscation() -> None:
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government = registry.get_government("fascist")
    player = PlayerState(start_system_id="SYS-TEST")
    player.set_reputation("SYS-TEST", 1)
    player.set_heat("SYS-TEST", 100)
    policy = GovernmentPolicyResult(
        legality_state=LegalityStatus.RESTRICTED,
        risk_tier=RiskTier.MEDIUM,
        consumed_tags=["recreational"],
    )
    outcome = enforcement_checkpoint(
        system_id="SYS-TEST",
        trigger_type=TriggerType.BORDER,
        government=government,
        policy_results=[("sku", policy)],
        player=player,
        world_seed=1,
        turn=1,
        cargo_snapshot=_cargo(False, True),
        logger=NullLogger(),
    )
    assert outcome is not None
    assert outcome.confiscation_percent == 0
    assert outcome.confiscated_amount == 0
    assert outcome.fines_added == 0
    assert outcome.arrested is False


def test_warrant_only_on_escape_even_if_eligible() -> None:
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government = registry.get_government("fascist")
    player = PlayerState(start_system_id="SYS-TEST")
    player.set_reputation("SYS-TEST", 1)
    player.set_heat("SYS-TEST", 100)
    policy = GovernmentPolicyResult(
        legality_state=LegalityStatus.ILLEGAL,
        risk_tier=RiskTier.SEVERE,
        consumed_tags=[],
    )
    turn = _first_attack_failure_turn(seed=2, system_id="SYS-TEST")
    outcome = enforcement_checkpoint(
        system_id="SYS-TEST",
        trigger_type=TriggerType.CUSTOMS,
        government=government,
        policy_results=[("sku", policy)],
        player=player,
        world_seed=2,
        turn=turn,
        cargo_snapshot=_cargo(False, True),
        logger=NullLogger(),
        option=PlayerOption.ATTACK,
    )
    assert outcome is not None
    assert outcome.warrant_issued is False


def test_no_consequence_block_no_action() -> None:
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government = registry.get_government("fascist")
    player = PlayerState(start_system_id="SYS-TEST")
    player.set_reputation("SYS-TEST", 50)
    player.set_heat("SYS-TEST", 100)
    policy = GovernmentPolicyResult(
        legality_state=LegalityStatus.RESTRICTED,
        risk_tier=RiskTier.HIGH,
        consumed_tags=["recreational"],
    )
    outcome = enforcement_checkpoint(
        system_id="SYS-TEST",
        trigger_type=TriggerType.CUSTOMS,
        government=government,
        policy_results=[("sku", policy)],
        player=player,
        world_seed=3,
        turn=3,
        cargo_snapshot=_cargo(False, True),
        logger=NullLogger(),
    )
    assert outcome is not None
    assert "no_consequences_defined" in outcome.consequences_applied


class CollectLogger:
    def __init__(self) -> None:
        self.entries: list[str] = []

    def log(self, turn: int, action: str, state_change: str) -> None:
        self.entries.append(f"{action}:{state_change}")


def _cargo(illegal: bool, restricted: bool):
    from law_enforcement import CargoSnapshot

    return CargoSnapshot(illegal_present=illegal, restricted_unlicensed_present=restricted)


def _first_attack_failure_turn(seed: int, system_id: str) -> int:
    import random

    for turn in range(1, 20):
        token = f"{seed}:{system_id}:{turn}:CUSTOMS:ATTACK"
        value = 0
        for ch in token:
            value = (value * 31 + ord(ch)) % (2**32)
        roll = random.Random(value).randint(1, 100)
        if roll > 50:
            return turn
    return 1
