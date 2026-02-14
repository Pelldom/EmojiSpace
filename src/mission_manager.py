from dataclasses import dataclass, field
from typing import Any, Dict, List

try:
    from crew_modifiers import compute_crew_modifiers
except ModuleNotFoundError:
    from src.crew_modifiers import compute_crew_modifiers

from mission_entity import MissionEntity, MissionOutcome, MissionState
from player_state import PlayerState
from reward_applicator import apply_mission_rewards


@dataclass
class MissionManager:
    missions: Dict[str, MissionEntity] = field(default_factory=dict)
    offered: List[str] = field(default_factory=list)

    def offer(self, mission: MissionEntity, logger=None, turn: int = 0) -> None:
        self.missions[mission.mission_id] = mission
        if mission.mission_id not in self.offered:
            self.offered.append(mission.mission_id)
        _log_manager(logger, turn, "offer", mission.mission_id)

    def accept(
        self,
        mission_id: str,
        player: PlayerState,
        logger=None,
        turn: int = 0,
        location_type: str | None = None,
        ship: Any | None = None,
    ) -> bool:
        mission = self.missions.get(mission_id)
        if mission is None:
            return False
        mission_slots = _effective_mission_slots(player=player, location_type=location_type, ship=ship)
        if len(player.active_missions) >= mission_slots:
            _log_manager(logger, turn, "accept_failed_slots", mission_id)
            return False
        mission.mission_state = MissionState.ACTIVE
        if mission_id in self.offered:
            self.offered.remove(mission_id)
        if mission_id not in player.active_missions:
            player.active_missions.append(mission_id)
        _log_manager(logger, turn, "accept", mission_id)
        return True

    def complete(self, mission_id: str, player: PlayerState, logger=None, turn: int = 0) -> None:
        mission = self.missions.get(mission_id)
        if mission is None:
            return
        mission.mission_state = MissionState.RESOLVED
        mission.outcome = MissionOutcome.COMPLETED
        _remove_from_list(player.active_missions, mission_id)
        if mission_id not in player.completed_missions:
            player.completed_missions.append(mission_id)
        apply_mission_rewards(
            mission_id=mission.mission_id,
            rewards=mission.rewards,
            player=player,
            logger=logger,
            turn=turn,
        )
        _log_manager(logger, turn, "complete", mission_id)

    def fail(self, mission_id: str, player: PlayerState, reason: str | None = None, logger=None, turn: int = 0) -> None:
        mission = self.missions.get(mission_id)
        if mission is None:
            return
        mission.mission_state = MissionState.RESOLVED
        mission.outcome = MissionOutcome.FAILED
        mission.failure_reason = reason
        _remove_from_list(player.active_missions, mission_id)
        if mission_id not in player.failed_missions:
            player.failed_missions.append(mission_id)
        _log_manager(logger, turn, "fail", mission_id)

    def abandon(self, mission_id: str, player: PlayerState, reason: str | None = None, logger=None, turn: int = 0) -> None:
        mission = self.missions.get(mission_id)
        if mission is None:
            return
        mission.mission_state = MissionState.RESOLVED
        mission.outcome = MissionOutcome.ABANDONED
        mission.failure_reason = reason
        _remove_from_list(player.active_missions, mission_id)
        if mission_id not in player.failed_missions:
            player.failed_missions.append(mission_id)
        _log_manager(logger, turn, "abandon", mission_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "missions": {mission_id: mission.to_dict() for mission_id, mission in self.missions.items()},
            "offered": list(self.offered),
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "MissionManager":
        manager = cls()
        missions_payload = payload.get("missions", {})
        for mission_id, data in missions_payload.items():
            mission = MissionEntity.from_dict(data)
            mission.mission_id = mission_id
            manager.missions[mission_id] = mission
        manager.offered = list(payload.get("offered", []))
        return manager


def _remove_from_list(items: List[str], value: str) -> None:
    if value in items:
        items.remove(value)


def _effective_mission_slots(*, player: PlayerState, location_type: str | None, ship: Any | None) -> int:
    slots = int(player.mission_slots)
    if location_type not in {"bar", "administration"}:
        return slots
    if ship is None:
        return slots
    crew_mods = compute_crew_modifiers(ship)
    return slots + int(crew_mods.mission_slot_bonus)


def _log_manager(logger, turn: int, action: str, mission_id: str, detail: str | None = None) -> None:
    if logger is None:
        return
    detail_text = f" {detail}" if detail else ""
    logger.log(turn=turn, action="mission_manager", state_change=f"{action} mission_id={mission_id}{detail_text}")
