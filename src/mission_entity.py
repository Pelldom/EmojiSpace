from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

from entities import EntityType


class MissionPersistenceScope(str, Enum):
    EPHEMERAL = "ephemeral"
    PERSISTENT = "persistent"
    SYSTEMIC = "systemic"


class MissionState(str, Enum):
    OFFERED = "offered"
    ACCEPTED = "accepted"
    ACTIVE = "active"
    RESOLVED = "resolved"


class MissionOutcome(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


@dataclass
class MissionEntity:
    # Core entity alignment
    entity_id: str = ""
    entity_type: EntityType = EntityType.OBJECT
    name: str = ""
    emoji: str | None = None
    system_id: str = ""
    location_id: str | None = None
    roles: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    affiliations: List[str] = field(default_factory=list)
    connections: List[str] = field(default_factory=list)
    interaction_types: List[str] = field(default_factory=list)
    persistent_state: Dict[str, Any] = field(default_factory=dict)
    memory_flags: Dict[str, Any] = field(default_factory=dict)

    # Mission identity and lifecycle
    mission_id: str = ""
    mission_type: str = ""
    mission_tier: int = 1
    persistence_scope: str = "ephemeral"
    mission_state: str = "offered"

    # Outcome tracking
    outcome: str | None = None
    failure_reason: str | None = None

    # References
    mission_giver_npc_id: str | None = None
    target_npc_id: str | None = None
    origin_location_id: str | None = None
    destination_location_id: str | None = None
    system_scope: str | None = None
    target_ship_id: str | None = None
    player_ship_id: str | None = None
    related_sku_ids: List[str] = field(default_factory=list)
    related_event_ids: List[str] = field(default_factory=list)

    # Objective and progress tracking
    objectives: List[str] = field(default_factory=list)
    progress: Dict[str, Any] = field(default_factory=dict)

    # Rewards (structured data only)
    rewards: List[Dict[str, Any]] = field(default_factory=list)

    # Player association
    assigned_player_id: str | None = None

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "MissionEntity":
        state = cls()
        for key, value in payload.items():
            if hasattr(state, key):
                setattr(state, key, value)
        return state

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "entity_type": _enum_to_str(self.entity_type),
            "name": self.name,
            "emoji": self.emoji,
            "system_id": self.system_id,
            "location_id": self.location_id,
            "roles": list(self.roles),
            "tags": list(self.tags),
            "affiliations": list(self.affiliations),
            "connections": list(self.connections),
            "interaction_types": list(self.interaction_types),
            "persistent_state": dict(self.persistent_state),
            "memory_flags": dict(self.memory_flags),
            "mission_id": self.mission_id,
            "mission_type": self.mission_type,
            "mission_tier": self.mission_tier,
            "persistence_scope": _enum_to_str(self.persistence_scope),
            "mission_state": _enum_to_str(self.mission_state),
            "outcome": _enum_to_str(self.outcome) if self.outcome else None,
            "failure_reason": self.failure_reason,
            "mission_giver_npc_id": self.mission_giver_npc_id,
            "target_npc_id": self.target_npc_id,
            "origin_location_id": self.origin_location_id,
            "destination_location_id": self.destination_location_id,
            "system_scope": self.system_scope,
            "target_ship_id": self.target_ship_id,
            "player_ship_id": self.player_ship_id,
            "related_sku_ids": list(self.related_sku_ids),
            "related_event_ids": list(self.related_event_ids),
            "objectives": list(self.objectives),
            "progress": dict(self.progress),
            "rewards": list(self.rewards),
            "assigned_player_id": self.assigned_player_id,
        }


def _enum_to_str(value: Any) -> Any:
    if hasattr(value, "value"):
        return value.value
    return value
