from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

from entities import EntityType


class ShipActivityState(str, Enum):
    ACTIVE = "active"
    DOCKED = "docked"
    STORED = "stored"
    ABANDONED = "abandoned"


@dataclass
class ShipEntity:
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

    # Ship identity and ownership
    ship_id: str = ""
    owner_player_id: str = ""
    ship_class: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Activity and location state
    activity_state: ShipActivityState = ShipActivityState.DOCKED
    current_location_id: str | None = None
    current_system_id: str = ""

    # Cargo and capacity
    physical_capacity: int = 0
    data_capacity: int = 0
    physical_cargo: Dict[str, int] = field(default_factory=dict)
    data_cargo: Dict[str, int] = field(default_factory=dict)
