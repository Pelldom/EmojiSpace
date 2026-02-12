from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, List

from entities import EntityType


class NPCPersistenceTier(IntEnum):
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3


@dataclass
class NPCEntity:
    # Core entity alignment
    entity_id: str = ""
    entity_type: EntityType = EntityType.PERSON
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

    # NPC identity and persistence
    npc_id: str = ""
    persistence_tier: NPCPersistenceTier = NPCPersistenceTier.TIER_1
    display_name: str = ""
    role_tags: List[str] = field(default_factory=list)
    affiliation_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Location association
    home_location_id: str | None = None
    current_location_id: str | None = None
    current_ship_id: str | None = None
    current_system_id: str = ""

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "NPCEntity":
        state = cls()
        for key, value in payload.items():
            if hasattr(state, key):
                if key == "persistence_tier":
                    value = _normalize_persistence_tier(value)
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
            "npc_id": self.npc_id,
            "persistence_tier": _enum_to_str(self.persistence_tier),
            "display_name": self.display_name,
            "role_tags": list(self.role_tags),
            "affiliation_ids": list(self.affiliation_ids),
            "metadata": dict(self.metadata),
            "home_location_id": self.home_location_id,
            "current_location_id": self.current_location_id,
            "current_ship_id": self.current_ship_id,
            "current_system_id": self.current_system_id,
        }

    def set_location(self, location_id: str | None, logger=None, turn: int = 0) -> None:
        self.current_location_id = location_id
        _log_state_change(logger, turn, "current_location_id", location_id)

    def set_system(self, system_id: str, logger=None, turn: int = 0) -> None:
        self.current_system_id = system_id
        _log_state_change(logger, turn, "current_system_id", system_id)


def _log_state_change(logger, turn: int, field: str, value: Any) -> None:
    if logger is None:
        return
    logger.log(turn=turn, action="npc_state_update", state_change=f"{field}={value}")


def _enum_to_str(value: Any) -> Any:
    if hasattr(value, "value"):
        return value.value
    return value


def _normalize_persistence_tier(value: Any) -> NPCPersistenceTier:
    if isinstance(value, NPCPersistenceTier):
        return value
    if isinstance(value, int):
        return NPCPersistenceTier(value)
    if isinstance(value, str) and value.isdigit():
        return NPCPersistenceTier(int(value))
    return NPCPersistenceTier.TIER_1
