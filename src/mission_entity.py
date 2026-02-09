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

    # Mission identity and lifecycle
    mission_id: str = ""
    mission_type: str = ""
    mission_tier: int = 1
    persistence_scope: MissionPersistenceScope = MissionPersistenceScope.EPHEMERAL
    mission_state: MissionState = MissionState.OFFERED

    # Outcome tracking
    outcome: MissionOutcome | None = None
    failure_reason: str | None = None

    # References
    mission_giver_npc_id: str | None = None
    target_npc_id: str | None = None
    origin_location_id: str | None = None
    destination_location_id: str | None = None
    related_ship_id: str | None = None
    related_sku_ids: List[str] = field(default_factory=list)
    related_event_ids: List[str] = field(default_factory=list)

    # Objective and progress tracking
    objectives: List[str] = field(default_factory=list)
    progress: Dict[str, Any] = field(default_factory=dict)

    # Player association
    assigned_player_id: str | None = None
