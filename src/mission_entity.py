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
    mission_state: MissionState = MissionState.OFFERED

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
    mission_contact_seed: str | None = None

    # Objective and progress tracking
    objectives: List[Dict[str, Any]] = field(default_factory=list)
    progress: Dict[str, Any] = field(default_factory=dict)
    
    # Mission routing and distance
    source: Dict[str, Any] = field(default_factory=dict)
    origin: Dict[str, Any] = field(default_factory=dict)
    target: Dict[str, Any] = field(default_factory=dict)
    distance_ly: int = 0
    reward_profile_id: str = ""

    # Payout configuration (Phase 7.11.2 - Required)
    payout_policy: str = ""  # "auto" or "claim_required"
    claim_scope: str = ""  # "none", "source_entity", or "any_source_type"

    # Reward state tracking (Phase 7.11.2a - Required)
    reward_status: str = ""  # "ungranted" or "granted"
    reward_granted_turn: int | None = None  # Turn when reward was granted

    # Player association
    assigned_player_id: str | None = None

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "MissionEntity":
        state = cls()
        for key, value in payload.items():
            if hasattr(state, key):
                # Normalize mission_state to enum if it's a string
                if key == "mission_state" and isinstance(value, str):
                    try:
                        # Try direct value match first
                        value = MissionState(value)
                    except ValueError:
                        # Try uppercase name match
                        try:
                            value = MissionState[value.upper()]
                        except (KeyError, AttributeError):
                            # Fallback to OFFERED if invalid
                            value = MissionState.OFFERED
                # Normalize outcome to enum if it's a string
                elif key == "outcome" and isinstance(value, str) and value:
                    try:
                        value = MissionOutcome(value)
                    except ValueError:
                        try:
                            value = MissionOutcome[value.upper()]
                        except (KeyError, AttributeError):
                            value = None
                # Handle legacy string objectives - convert to structured format
                elif key == "objectives" and isinstance(value, list) and value and isinstance(value[0], str):
                    # Legacy format: convert string objectives to structured format
                    structured_objectives = []
                    for idx, obj_str in enumerate(value):
                        if isinstance(obj_str, str) and ":" in obj_str:
                            parts = obj_str.split(":", 1)
                            obj_type = parts[0] if len(parts) > 0 else "unknown"
                            structured_objectives.append({
                                "objective_id": f"OBJ-{idx + 1}",
                                "objective_type": obj_type,
                                "status": "pending",
                                "parameters": {}
                            })
                        else:
                            structured_objectives.append({
                                "objective_id": f"OBJ-{idx + 1}",
                                "objective_type": "unknown",
                                "status": "pending",
                                "parameters": {}
                            })
                    value = structured_objectives
                # Handle goods conversion: ensure goods is always a list
                elif key == "objectives" and isinstance(value, list):
                    for obj in value:
                        if isinstance(obj, dict) and "parameters" in obj:
                            params = obj["parameters"]
                            if isinstance(params, dict) and "goods" in params:
                                goods = params["goods"]
                                # If goods is a dict, convert to list
                                if isinstance(goods, dict):
                                    params["goods"] = [goods]
                                # Ensure it's a list
                                elif not isinstance(goods, list):
                                    params["goods"] = []
                # Ignore rewards field if present (legacy)
                elif key == "rewards":
                    # Silently ignore - rewards field removed
                    continue
                # Validate source_type if source field is being set
                elif key == "source" and isinstance(value, dict):
                    source_type = value.get("source_type")
                    if source_type and source_type not in {"bar", "administration", "datanet", "victory"}:
                        raise ValueError(
                            f"Invalid source_type '{source_type}' in source field. "
                            f"Allowed values: bar, administration, datanet, victory"
                        )
                setattr(state, key, value)
        
        # Validate payout_policy and claim_scope (Phase 7.11.2 - Required)
        _validate_payout_fields(state)
        
        # Validate reward_status and reward_granted_turn (Phase 7.11.2a - Required)
        _validate_reward_fields(state)
        
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
            "assigned_player_id": self.assigned_player_id,
            "mission_contact_seed": self.mission_contact_seed,
            "source": dict(self.source),
            "origin": dict(self.origin),
            "target": dict(self.target),
            "distance_ly": int(self.distance_ly),
            "reward_profile_id": str(self.reward_profile_id),
            "payout_policy": str(self.payout_policy),
            "claim_scope": str(self.claim_scope),
            "reward_status": str(self.reward_status),
            "reward_granted_turn": self.reward_granted_turn,
        }


def _validate_reward_fields(mission: MissionEntity) -> None:
    """
    Validate reward_status and reward_granted_turn fields (Phase 7.11.2a).
    
    Rules:
    1. reward_status must be present (not empty)
    2. reward_status must be "ungranted" or "granted"
    3. If reward_status == "ungranted", reward_granted_turn MUST be None
    4. If reward_status == "granted", reward_granted_turn MUST be int
    
    Raises ValueError on any validation failure.
    """
    # Check reward_status is present
    if not mission.reward_status:
        raise ValueError("reward_status is required and cannot be empty")
    
    # Validate allowed values
    ALLOWED_REWARD_STATUSES = {"ungranted", "granted"}
    if mission.reward_status not in ALLOWED_REWARD_STATUSES:
        raise ValueError(
            f"Invalid reward_status '{mission.reward_status}'. "
            f"Allowed values: {sorted(ALLOWED_REWARD_STATUSES)}"
        )
    
    # Validate combination rules
    if mission.reward_status == "ungranted":
        if mission.reward_granted_turn is not None:
            raise ValueError(
                f"Invalid combination: reward_status='ungranted' requires reward_granted_turn=None, "
                f"got reward_granted_turn={mission.reward_granted_turn}"
            )
    elif mission.reward_status == "granted":
        if not isinstance(mission.reward_granted_turn, int):
            raise ValueError(
                f"Invalid combination: reward_status='granted' requires reward_granted_turn to be int, "
                f"got {type(mission.reward_granted_turn).__name__}"
            )


def _validate_payout_fields(mission: MissionEntity) -> None:
    """
    Validate payout_policy and claim_scope fields (Phase 7.11.2).
    
    Rules:
    1. Both fields must be present (not empty)
    2. payout_policy must be "auto" or "claim_required"
    3. claim_scope must be "none", "source_entity", or "any_source_type"
    4. If payout_policy == "auto", claim_scope MUST be "none"
    5. If payout_policy == "claim_required", claim_scope MUST be "source_entity" or "any_source_type"
    
    Raises ValueError on any validation failure.
    """
    # Check both fields are present
    if not mission.payout_policy:
        raise ValueError("payout_policy is required and cannot be empty")
    if not mission.claim_scope:
        raise ValueError("claim_scope is required and cannot be empty")
    
    # Validate allowed values
    ALLOWED_PAYOUT_POLICIES = {"auto", "claim_required"}
    ALLOWED_CLAIM_SCOPES = {"none", "source_entity", "any_source_type"}
    
    if mission.payout_policy not in ALLOWED_PAYOUT_POLICIES:
        raise ValueError(
            f"Invalid payout_policy '{mission.payout_policy}'. "
            f"Allowed values: {sorted(ALLOWED_PAYOUT_POLICIES)}"
        )
    
    if mission.claim_scope not in ALLOWED_CLAIM_SCOPES:
        raise ValueError(
            f"Invalid claim_scope '{mission.claim_scope}'. "
            f"Allowed values: {sorted(ALLOWED_CLAIM_SCOPES)}"
        )
    
    # Validate combination rules
    if mission.payout_policy == "auto":
        if mission.claim_scope != "none":
            raise ValueError(
                f"Invalid combination: payout_policy='auto' requires claim_scope='none', "
                f"got claim_scope='{mission.claim_scope}'"
            )
    elif mission.payout_policy == "claim_required":
        if mission.claim_scope not in {"source_entity", "any_source_type"}:
            raise ValueError(
                f"Invalid combination: payout_policy='claim_required' requires "
                f"claim_scope in {{'source_entity', 'any_source_type'}}, "
                f"got claim_scope='{mission.claim_scope}'"
            )


def _enum_to_str(value: Any) -> Any:
    if hasattr(value, "value"):
        return value.value
    return value
