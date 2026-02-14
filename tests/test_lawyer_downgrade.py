import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from government_law_engine import GovernmentPolicyResult, LegalityStatus, RiskTier  # noqa: E402
from government_registry import GovernmentRegistry  # noqa: E402
from law_enforcement import PlayerOption, TriggerType, enforcement_checkpoint  # noqa: E402
from npc_entity import NPCEntity, NPCPersistenceTier  # noqa: E402
from player_state import PlayerState  # noqa: E402
from ship_entity import ShipEntity  # noqa: E402


class NullLogger:
    def log(self, turn: int, action: str, state_change: str) -> None:
        return


def _cargo(illegal: bool, restricted: bool):
    from law_enforcement import CargoSnapshot

    return CargoSnapshot(illegal_present=illegal, restricted_unlicensed_present=restricted)


def _crew(npc_id: str, role: str) -> NPCEntity:
    return NPCEntity(
        npc_id=npc_id,
        is_crew=True,
        crew_role_id=role,
        crew_tags=[f"crew:{role}"],
        persistence_tier=NPCPersistenceTier.TIER_2,
    )


def _tier2_setup() -> tuple[object, PlayerState, GovernmentPolicyResult]:
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government = registry.get_government("fascist")
    player = PlayerState(current_system_id="SYS-TEST")
    player.reputation_by_system["SYS-TEST"] = 1
    player.heat_by_system["SYS-TEST"] = 100
    policy = GovernmentPolicyResult(
        legality_state=LegalityStatus.ILLEGAL,
        risk_tier=RiskTier.SEVERE,
        consumed_tags=["piracy"],
    )
    return government, player, policy


def test_tier2_no_lawyer_still_game_over() -> None:
    government, player, policy = _tier2_setup()
    ship = ShipEntity(crew=[_crew("NPC-ENG-1", "engineer")])
    outcome = enforcement_checkpoint(
        system_id="SYS-TEST",
        trigger_type=TriggerType.CUSTOMS,
        government=government,
        policy_results=[("piracy_payload", policy)],
        player=player,
        world_seed=5,
        turn=5,
        cargo_snapshot=_cargo(True, False),
        logger=NullLogger(),
        option=PlayerOption.ATTACK,
        ship=ship,
    )
    assert outcome is not None
    assert outcome.detention_tier == 2
    assert outcome.dead is True
    assert outcome.lawyer_used is False
    assert outcome.consumed_lawyer_id is None


def test_tier2_with_lawyer_downgrades_to_tier1_and_consumes_lawyer() -> None:
    government, player, policy = _tier2_setup()
    player.active_ship_id = "SHIP-1"
    player.cargo_by_ship["active"] = {"piracy_payload": 2}
    ship = ShipEntity(ship_id="SHIP-1", crew=[_crew("NPC-LAW-1", "lawyer")])
    outcome = enforcement_checkpoint(
        system_id="SYS-TEST",
        trigger_type=TriggerType.CUSTOMS,
        government=government,
        policy_results=[("piracy_payload", policy)],
        player=player,
        world_seed=5,
        turn=5,
        cargo_snapshot=_cargo(True, False),
        logger=NullLogger(),
        option=PlayerOption.ATTACK,
        ship=ship,
    )
    assert outcome is not None
    assert outcome.detention_tier == 1
    assert outcome.dead is False
    assert outcome.lawyer_used is True
    assert outcome.consumed_lawyer_id == "NPC-LAW-1"
    assert player.arrest_state != "detained_tier_2"
    assert player.active_ship_id is None
    assert player.cargo_by_ship["active"].get("piracy_payload", 0) == 0
    assert len(ship.crew) == 0


def test_tier2_with_multiple_lawyers_default_consumes_lowest_npc_id() -> None:
    government, player, policy = _tier2_setup()
    ship = ShipEntity(
        crew=[
            _crew("NPC-LAW-9", "lawyer"),
            _crew("NPC-LAW-2", "lawyer"),
            _crew("NPC-LAW-5", "lawyer"),
        ]
    )
    outcome = enforcement_checkpoint(
        system_id="SYS-TEST",
        trigger_type=TriggerType.CUSTOMS,
        government=government,
        policy_results=[("piracy_payload", policy)],
        player=player,
        world_seed=5,
        turn=5,
        cargo_snapshot=_cargo(True, False),
        logger=NullLogger(),
        option=PlayerOption.ATTACK,
        ship=ship,
    )
    assert outcome is not None
    assert outcome.lawyer_used is True
    assert outcome.consumed_lawyer_id == "NPC-LAW-2"


def test_tier2_with_lawyer_id_consumes_specified_one() -> None:
    government, player, policy = _tier2_setup()
    ship = ShipEntity(
        crew=[
            _crew("NPC-LAW-1", "lawyer"),
            _crew("NPC-LAW-2", "lawyer"),
        ]
    )
    outcome = enforcement_checkpoint(
        system_id="SYS-TEST",
        trigger_type=TriggerType.CUSTOMS,
        government=government,
        policy_results=[("piracy_payload", policy)],
        player=player,
        world_seed=5,
        turn=5,
        cargo_snapshot=_cargo(True, False),
        logger=NullLogger(),
        option=PlayerOption.ATTACK,
        ship=ship,
        lawyer_id="NPC-LAW-2",
    )
    assert outcome is not None
    assert outcome.lawyer_used is True
    assert outcome.consumed_lawyer_id == "NPC-LAW-2"
    remaining_ids = sorted(member.npc_id for member in ship.crew)
    assert remaining_ids == ["NPC-LAW-1"]


def test_invalid_lawyer_id_raises_value_error() -> None:
    government, player, policy = _tier2_setup()
    ship = ShipEntity(crew=[_crew("NPC-LAW-1", "lawyer")])
    try:
        enforcement_checkpoint(
            system_id="SYS-TEST",
            trigger_type=TriggerType.CUSTOMS,
            government=government,
            policy_results=[("piracy_payload", policy)],
            player=player,
            world_seed=5,
            turn=5,
            cargo_snapshot=_cargo(True, False),
            logger=NullLogger(),
            option=PlayerOption.ATTACK,
            ship=ship,
            lawyer_id="NPC-LAW-404",
        )
        assert False, "Expected ValueError for invalid lawyer_id."
    except ValueError as exc:
        assert "lawyer_id" in str(exc)


def test_ensure_only_lawyer_role_is_consumed() -> None:
    government, player, policy = _tier2_setup()
    ship = ShipEntity(
        crew=[
            _crew("NPC-LAW-1", "lawyer"),
            _crew("NPC-ENG-1", "engineer"),
            _crew("NPC-PIL-1", "pilot"),
        ]
    )
    outcome = enforcement_checkpoint(
        system_id="SYS-TEST",
        trigger_type=TriggerType.CUSTOMS,
        government=government,
        policy_results=[("piracy_payload", policy)],
        player=player,
        world_seed=5,
        turn=5,
        cargo_snapshot=_cargo(True, False),
        logger=NullLogger(),
        option=PlayerOption.ATTACK,
        ship=ship,
    )
    assert outcome is not None
    assert outcome.lawyer_used is True
    remaining_roles = sorted(member.crew_role_id for member in ship.crew)
    assert remaining_roles == ["engineer", "pilot"]
