from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

from entities import EntityType


class OwnerType(str, Enum):
    PLAYER = "player"
    NPC = "npc"
    FACTION = "faction"


class ShipActivityState(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class StorageContext(str, Enum):
    IN_TRANSIT = "in_transit"
    ORBIT = "orbit"
    STATION = "station"
    SHIPDOCK = "shipdock"
    PLANET_SURFACE = "planet_surface"
    IMPOUNDED = "impounded"
    DESTROYED = "destroyed"


class ConditionState(str, Enum):
    OPERATIONAL = "operational"
    DAMAGED = "damaged"
    DISABLED = "disabled"
    DESTROYED = "destroyed"


@dataclass
class ShipEntity:
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

    # Identity and ownership
    ship_id: str = ""
    model_id: str = ""
    owner_type: str = "player"
    owner_id: str = ""
    display_name: str | None = None

    # Active vs inactive
    activity_state: str = "inactive"

    # Location and storage context
    storage_context: str = "station"
    current_system_id: str = ""
    current_destination_id: str | None = None
    current_location_id: str | None = None

    # Cargo capacities
    physical_cargo_capacity: int = 0
    data_cargo_capacity: int = 0
    fuel_capacity: int = 0
    current_fuel: int | None = None

    # Cargo manifests
    physical_cargo_manifest: List[Dict[str, int]] = field(default_factory=list)
    data_cargo_manifest: List[Dict[str, int]] = field(default_factory=list)

    # Condition
    condition_state: str = "operational"
    condition_emoji: str = "OP"

    def __post_init__(self) -> None:
        if self.current_fuel is None:
            self.current_fuel = self.fuel_capacity
        self._validate_fuel_bounds()

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ShipEntity":
        state = cls()
        for key, value in payload.items():
            if hasattr(state, key):
                setattr(state, key, value)
        state._validate_fuel_bounds()
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
            "ship_id": self.ship_id,
            "model_id": self.model_id,
            "owner_type": _enum_to_str(self.owner_type),
            "owner_id": self.owner_id,
            "display_name": self.display_name,
            "activity_state": _enum_to_str(self.activity_state),
            "storage_context": _enum_to_str(self.storage_context),
            "current_system_id": self.current_system_id,
            "current_destination_id": self.current_destination_id,
            "current_location_id": self.current_location_id,
            "physical_cargo_capacity": self.physical_cargo_capacity,
            "data_cargo_capacity": self.data_cargo_capacity,
            "fuel_capacity": self.fuel_capacity,
            "current_fuel": self.current_fuel,
            "physical_cargo_manifest": list(self.physical_cargo_manifest),
            "data_cargo_manifest": list(self.data_cargo_manifest),
            "condition_state": _enum_to_str(self.condition_state),
            "condition_emoji": self.condition_emoji,
        }

    def set_storage_context(self, value: str, logger=None, turn: int = 0) -> None:
        self.storage_context = _enum_to_str(value)
        _log_state_change(logger, turn, "storage_context", self.storage_context)

    def set_condition_state(self, value: str, logger=None, turn: int = 0) -> None:
        self.condition_state = _enum_to_str(value)
        _log_state_change(logger, turn, "condition_state", self.condition_state)

    def set_current_system_id(self, value: str, logger=None, turn: int = 0) -> None:
        self.current_system_id = value
        _log_state_change(logger, turn, "current_system_id", value)

    def set_current_destination_id(self, value: str | None, logger=None, turn: int = 0) -> None:
        self.current_destination_id = value
        _log_state_change(logger, turn, "current_destination_id", value)

    def set_current_location_id(self, value: str | None, logger=None, turn: int = 0) -> None:
        self.current_location_id = value
        _log_state_change(logger, turn, "current_location_id", value)

    def set_current_fuel(self, value: int, logger=None, turn: int = 0) -> None:
        self.current_fuel = value
        self._validate_fuel_bounds()
        _log_state_change(logger, turn, "current_fuel", value)

    def _validate_fuel_bounds(self) -> None:
        if not isinstance(self.fuel_capacity, int) or self.fuel_capacity < 0:
            raise ValueError("fuel_capacity must be a non-negative integer.")
        if self.current_fuel is None or not isinstance(self.current_fuel, int):
            raise ValueError("current_fuel must be an integer.")
        if self.current_fuel < 0 or self.current_fuel > self.fuel_capacity:
            raise ValueError("Fuel invariant violated: 0 <= current_fuel <= fuel_capacity.")


def _log_state_change(logger, turn: int, field: str, value: Any) -> None:
    if logger is None:
        return
    logger.log(turn=turn, action="ship_state_update", state_change=f"{field}={value}")


def _enum_to_str(value: Any) -> Any:
    if hasattr(value, "value"):
        return value.value
    return value
