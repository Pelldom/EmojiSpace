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
    entity_id: str
    entity_type: EntityType
    name: str
    emoji: str | None
    system_id: str
    location_id: str | None
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
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Location association
    home_location_id: str | None = None
    current_location_id: str | None = None
    current_system_id: str = ""
