from dataclasses import dataclass, field
from typing import Any, Dict, List

from mission_entity import MissionEntity, MissionState, MissionOutcome
from player_state import PlayerState


VICTORY_IDS = {
    "charter_of_authority",
    "escape_the_datanet",
    "retirement_acquisition",
    "secure_the_hoard",
    "crown_of_order",
    "rule_through_fear",
}


VICTORY_SOURCES = {
    "datanet": list(VICTORY_IDS),
    "npc_administration": [
        "charter_of_authority",
        "retirement_acquisition",
        "crown_of_order",
    ],
    "npc_bar": [
        "escape_the_datanet",
        "secure_the_hoard",
        "rule_through_fear",
    ],
}


@dataclass
class EndGameResult:
    status: str = "ongoing"
    victory: str | None = None
    active_victory_missions: List[str] = field(default_factory=list)
    eligible_victory_missions: List[str] = field(default_factory=list)
    failure_reasons: List[str] = field(default_factory=list)


def evaluate_end_game(
    *,
    player: PlayerState,
    missions: List[MissionEntity],
) -> EndGameResult:
    failures = _failure_reasons(player)
    if failures:
        return EndGameResult(status="lose", failure_reasons=failures)

    active_victories: List[str] = []
    completed_victory: str | None = None
    for mission in missions:
        victory_id = _victory_id_from_mission(mission)
        if victory_id is None:
            continue
        if mission.mission_state == MissionState.ACTIVE:
            active_victories.append(victory_id)
        if mission.mission_state == MissionState.RESOLVED and mission.outcome == MissionOutcome.COMPLETED:
            completed_victory = victory_id

    if completed_victory is not None:
        return EndGameResult(
            status="win",
            victory=completed_victory,
            active_victory_missions=active_victories,
        )

    eligible = _eligible_victories(player)
    return EndGameResult(
        status="ongoing",
        victory=None,
        active_victory_missions=active_victories,
        eligible_victory_missions=eligible,
        failure_reasons=[],
    )


def victory_offers_for_source(source_type: str) -> List[str]:
    return list(VICTORY_SOURCES.get(source_type, []))


def _victory_id_from_mission(mission: MissionEntity) -> str | None:
    if mission.mission_tier != 5:
        return None
    victory_id = _extract_victory_id(mission)
    if victory_id not in VICTORY_IDS:
        return None
    return victory_id


def _extract_victory_id(mission: MissionEntity) -> str | None:
    victory_id = mission.persistent_state.get("victory_id")
    if isinstance(victory_id, str):
        return victory_id
    if mission.mission_type.startswith("victory:"):
        return mission.mission_type.split("victory:", 1)[1]
    return None


def _eligible_victories(player: PlayerState) -> List[str]:
    tracks = player.progression_tracks
    eligible: List[str] = []
    if _eligible_track(tracks, "trust", "notoriety"):
        eligible.append("charter_of_authority")
    if _eligible_track(tracks, "notoriety", "trust"):
        eligible.append("escape_the_datanet")
    if _eligible_track(tracks, "entrepreneur", "criminal"):
        eligible.append("retirement_acquisition")
    if _eligible_track(tracks, "criminal", "entrepreneur"):
        eligible.append("secure_the_hoard")
    if _eligible_track(tracks, "law", "outlaw"):
        eligible.append("crown_of_order")
    if _eligible_track(tracks, "outlaw", "law"):
        eligible.append("rule_through_fear")
    return eligible


def _eligible_track(tracks: Dict[str, int], primary: str, opposing: str) -> bool:
    return tracks.get(primary, 0) >= 100 and tracks.get(opposing, 0) <= 50


def _failure_reasons(player: PlayerState) -> List[str]:
    failures: List[str] = []
    if player.arrest_state == "detained_tier_2":
        failures.append("tier2_arrest")
    if _death_detected(player):
        failures.append("death")
    if _bankruptcy_detected(player):
        failures.append("bankruptcy")
    return failures


def _death_detected(player: PlayerState) -> bool:
    for entry in player.history_timeline:
        event_type = entry.get("event_type")
        if event_type in {"death", "player_death"}:
            return True
    return False


def _bankruptcy_detected(player: PlayerState) -> bool:
    # Liquidity-based bankruptcy: credits must be 0 AND warning turn must be set AND current turn must exceed warning turn
    if player.credits > 0:
        return False
    if player.bankruptcy_warning_turn is None:
        return False
    # Import here to avoid circular dependency
    from time_engine import get_current_turn
    current_turn = int(get_current_turn())
    if current_turn <= player.bankruptcy_warning_turn:
        return False
    return True
