from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class PlayerState:
    HISTORY_TIMELINE_MAX = 100

    # Identity
    player_id: str = "player"
    display_name: str = "Player"
    current_system_id: str = ""
    current_destination_id: str | None = None
    current_location_id: str | None = None

    # Financial state
    credits: int = 0
    outstanding_fines: Dict[str, int] = field(default_factory=dict)

    # Legal state (system-scoped)
    reputation_by_system: Dict[str, int] = field(default_factory=dict)
    heat_by_system: Dict[str, int] = field(default_factory=dict)
    warrants_by_system: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    arrest_state: str = "free"

    # Ships
    active_ship_id: str | None = None
    owned_ship_ids: List[str] = field(default_factory=list)

    # Cargo and storage references
    cargo_by_ship: Dict[str, Dict[str, int]] = field(default_factory=dict)
    stored_goods: Dict[str, Dict[str, int]] = field(default_factory=dict)

    # Warehousing
    warehouse_leases: List[Dict[str, Any]] = field(default_factory=list)

    # Financial instruments
    loans: List[Dict[str, Any]] = field(default_factory=list)
    insurance_policies: List[Dict[str, Any]] = field(default_factory=list)

    # Missions
    mission_slots: int = 1
    active_missions: List[str] = field(default_factory=list)
    completed_missions: List[str] = field(default_factory=list)
    failed_missions: List[str] = field(default_factory=list)

    # History and progression
    history_timeline: List[Dict[str, Any]] = field(default_factory=list)
    progression_tracks: Dict[str, int] = field(
        default_factory=lambda: {
            "trust": 0,
            "notoriety": 0,
            "entrepreneur": 0,
            "criminal": 0,
            "law": 0,
            "outlaw": 0,
        }
    )

    total_credits_earned: int = 0
    total_credits_lost: int = 0
    total_trades_completed: int = 0
    total_missions_completed: int = 0
    total_missions_failed: int = 0
    total_ships_owned: int = 0
    total_ships_lost: int = 0
    total_arrests: int = 0
    total_inspections_submitted: int = 0
    total_inspections_fled: int = 0
    total_inspections_bribed: int = 0
    total_inspections_attacked: int = 0
    last_customs_turn: int | None = None
    last_customs_destination_id: str | None = None
    last_customs_kind: str | None = None

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "PlayerState":
        state = cls()
        for key, value in payload.items():
            if hasattr(state, key):
                setattr(state, key, value)
        return state

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player_id": self.player_id,
            "display_name": self.display_name,
            "current_system_id": self.current_system_id,
            "current_destination_id": self.current_destination_id,
            "current_location_id": self.current_location_id,
            "credits": self.credits,
            "outstanding_fines": dict(self.outstanding_fines),
            "reputation_by_system": dict(self.reputation_by_system),
            "heat_by_system": dict(self.heat_by_system),
            "warrants_by_system": {k: list(v) for k, v in self.warrants_by_system.items()},
            "arrest_state": _enum_to_str(self.arrest_state),
            "active_ship_id": self.active_ship_id,
            "owned_ship_ids": list(self.owned_ship_ids),
            "cargo_by_ship": {k: dict(v) for k, v in self.cargo_by_ship.items()},
            "stored_goods": {k: dict(v) for k, v in self.stored_goods.items()},
            "warehouse_leases": list(self.warehouse_leases),
            "loans": list(self.loans),
            "insurance_policies": list(self.insurance_policies),
            "mission_slots": self.mission_slots,
            "active_missions": list(self.active_missions),
            "completed_missions": list(self.completed_missions),
            "failed_missions": list(self.failed_missions),
            "history_timeline": list(self.history_timeline),
            "progression_tracks": dict(self.progression_tracks),
            "total_credits_earned": self.total_credits_earned,
            "total_credits_lost": self.total_credits_lost,
            "total_trades_completed": self.total_trades_completed,
            "total_missions_completed": self.total_missions_completed,
            "total_missions_failed": self.total_missions_failed,
            "total_ships_owned": self.total_ships_owned,
            "total_ships_lost": self.total_ships_lost,
            "total_arrests": self.total_arrests,
            "total_inspections_submitted": self.total_inspections_submitted,
            "total_inspections_fled": self.total_inspections_fled,
            "total_inspections_bribed": self.total_inspections_bribed,
            "total_inspections_attacked": self.total_inspections_attacked,
            "last_customs_turn": self.last_customs_turn,
            "last_customs_destination_id": self.last_customs_destination_id,
            "last_customs_kind": self.last_customs_kind,
        }

    def set_arrest_state(self, value: str, logger=None, turn: int = 0) -> None:
        self.arrest_state = _enum_to_str(value)
        _log_state_change(logger, turn, "arrest_state", self.arrest_state)

    def set_credits(self, value: int, logger=None, turn: int = 0) -> None:
        self.credits = value
        _log_state_change(logger, turn, "credits", value)

    def set_current_system_id(self, value: str, logger=None, turn: int = 0) -> None:
        self.current_system_id = value
        _log_state_change(logger, turn, "current_system_id", value)

    def set_current_destination_id(self, value: str | None, logger=None, turn: int = 0) -> None:
        self.current_destination_id = value
        _log_state_change(logger, turn, "current_destination_id", value)

    def set_current_location_id(self, value: str | None, logger=None, turn: int = 0) -> None:
        self.current_location_id = value
        _log_state_change(logger, turn, "current_location_id", value)

    def add_history_entry(self, entry: Dict[str, Any], logger=None, turn: int = 0) -> None:
        self.history_timeline.append(entry)
        if len(self.history_timeline) > self.HISTORY_TIMELINE_MAX:
            self.history_timeline = self.history_timeline[-self.HISTORY_TIMELINE_MAX :]
        _log_state_change(logger, turn, "history_timeline", f"len={len(self.history_timeline)}")


def _log_state_change(logger, turn: int, field: str, value: Any) -> None:
    if logger is None:
        return
    logger.log(turn=turn, action="player_state_update", state_change=f"{field}={value}")


def _enum_to_str(value: Any) -> Any:
    if hasattr(value, "value"):
        return value.value
    return value
