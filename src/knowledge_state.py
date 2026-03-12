from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


# ---------------------------------------------------------------------------
# Knowledge level constants (string-based for simple serialization)
# ---------------------------------------------------------------------------

SYSTEM_LEVEL_UNKNOWN = "unknown"
SYSTEM_LEVEL_DETECTED = "detected"
SYSTEM_LEVEL_SCANNED_LOCAL = "scanned_local"
SYSTEM_LEVEL_VISITED = "visited"

DEST_LEVEL_UNKNOWN = "unknown"
DEST_LEVEL_LOCAL_VISIBLE = "local_visible"
DEST_LEVEL_VISITED = "visited"


@dataclass
class SystemKnowledgeSnapshot:
    system_id: str
    level: str = SYSTEM_LEVEL_UNKNOWN
    name: Optional[str] = None
    primary_emoji_id: Optional[str] = None
    government_id: Optional[str] = None
    population: Optional[int] = None
    last_seen_turn: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "system_id": self.system_id,
            "level": self.level,
            "name": self.name,
            "primary_emoji_id": self.primary_emoji_id,
            "government_id": self.government_id,
            "population": self.population,
            "last_seen_turn": self.last_seen_turn,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemKnowledgeSnapshot":
        return cls(
            system_id=str(data.get("system_id", "")),
            level=str(data.get("level", SYSTEM_LEVEL_UNKNOWN)),
            name=data.get("name"),
            primary_emoji_id=data.get("primary_emoji_id"),
            government_id=data.get("government_id"),
            population=int(data["population"]) if isinstance(data.get("population"), (int, float)) else None,
            last_seen_turn=int(data["last_seen_turn"]) if isinstance(data.get("last_seen_turn"), (int, float)) else None,
        )


@dataclass
class DestinationKnowledgeSnapshot:
    destination_id: str
    system_id: Optional[str] = None
    level: str = DEST_LEVEL_UNKNOWN
    name: Optional[str] = None
    destination_type: Optional[str] = None
    population: Optional[int] = None
    primary_economy_id: Optional[str] = None
    secondary_economy_ids: List[str] = field(default_factory=list)
    last_seen_turn: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "destination_id": self.destination_id,
            "system_id": self.system_id,
            "level": self.level,
            "name": self.name,
            "destination_type": self.destination_type,
            "population": self.population,
            "primary_economy_id": self.primary_economy_id,
            "secondary_economy_ids": list(self.secondary_economy_ids),
            "last_seen_turn": self.last_seen_turn,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DestinationKnowledgeSnapshot":
        secondary_raw = data.get("secondary_economy_ids") or []
        secondary_list = [str(x) for x in secondary_raw] if isinstance(secondary_raw, (list, tuple)) else []
        return cls(
            destination_id=str(data.get("destination_id", "")),
            system_id=str(data["system_id"]) if isinstance(data.get("system_id"), str) else None,
            level=str(data.get("level", DEST_LEVEL_UNKNOWN)),
            name=data.get("name"),
            destination_type=data.get("destination_type"),
            population=int(data["population"]) if isinstance(data.get("population"), (int, float)) else None,
            primary_economy_id=data.get("primary_economy_id"),
            secondary_economy_ids=secondary_list,
            last_seen_turn=int(data["last_seen_turn"]) if isinstance(data.get("last_seen_turn"), (int, float)) else None,
        )


@dataclass
class SystemView:
    system_id: str
    level: str
    name: str
    primary_emoji_id: Optional[str]
    government_display: Optional[str]
    population_display: Optional[int]
    live_situations: List[str]
    is_live: bool
    last_seen_turn: Optional[int]
    is_stale: bool


@dataclass
class DestinationView:
    destination_id: str
    system_id: Optional[str]
    level: str
    name: str
    destination_type: Optional[str]
    primary_emoji_id: Optional[str]
    population_display: Optional[int]
    primary_economy_display: Optional[str]
    secondary_economies_display: List[str]
    live_situations: List[str]
    is_live: bool
    last_seen_turn: Optional[int]
    is_stale: bool


def _get_or_create_system_snapshot(player_state, system_id: str) -> SystemKnowledgeSnapshot:
    store: Dict[str, Dict[str, Any]] = getattr(player_state, "known_systems", {})
    raw = store.get(system_id)
    if isinstance(raw, dict):
        snapshot = SystemKnowledgeSnapshot.from_dict(raw)
    else:
        snapshot = SystemKnowledgeSnapshot(system_id=system_id)
    store[system_id] = snapshot.to_dict()
    player_state.known_systems = store
    return snapshot


def _get_or_create_destination_snapshot(player_state, destination_id: str, system_id: Optional[str]) -> DestinationKnowledgeSnapshot:
    store: Dict[str, Dict[str, Any]] = getattr(player_state, "known_destinations", {})
    raw = store.get(destination_id)
    if isinstance(raw, dict):
        snapshot = DestinationKnowledgeSnapshot.from_dict(raw)
    else:
        snapshot = DestinationKnowledgeSnapshot(destination_id=destination_id, system_id=system_id)
    # Ensure system_id is always set once known
    if system_id and not snapshot.system_id:
        snapshot.system_id = system_id
    store[destination_id] = snapshot.to_dict()
    player_state.known_destinations = store
    return snapshot


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

def initialize_player_knowledge(player_state, sector, *, current_turn: int) -> None:
    """
    Initialize knowledge for a new game.

    Current-phase assumption: all systems start at least detected.
    This does NOT mark systems as visited and does NOT reveal destination knowledge.
    """
    known_systems: Dict[str, Dict[str, Any]] = {}
    for system in getattr(sector, "systems", []) or []:
        system_id = getattr(system, "system_id", None)
        if not isinstance(system_id, str) or not system_id:
            continue
        name = getattr(system, "name", None)
        primary_emoji_id = getattr(system, "emoji_id", None)
        snapshot = SystemKnowledgeSnapshot(
            system_id=system_id,
            level=SYSTEM_LEVEL_DETECTED,
            name=str(name) if isinstance(name, str) else None,
            primary_emoji_id=str(primary_emoji_id) if isinstance(primary_emoji_id, str) and primary_emoji_id else None,
            government_id=None,
            population=None,
            last_seen_turn=None,
        )
        known_systems[system_id] = snapshot.to_dict()
    player_state.known_systems = known_systems
    if not hasattr(player_state, "known_destinations"):
        player_state.known_destinations = {}


# ---------------------------------------------------------------------------
# System knowledge updates
# ---------------------------------------------------------------------------

def mark_system_scanned_local(player_state, system, *, current_turn: int) -> None:
    """
    Upgrade a system to at least scanned_local and record government information.
    Caller is responsible for only calling this when the system is actually in range
    according to the authoritative travel logic.
    """
    system_id = getattr(system, "system_id", None)
    if not isinstance(system_id, str) or not system_id:
        return
    snapshot = _get_or_create_system_snapshot(player_state, system_id)
    if snapshot.level == SYSTEM_LEVEL_UNKNOWN:
        snapshot.level = SYSTEM_LEVEL_DETECTED
    if snapshot.level == SYSTEM_LEVEL_DETECTED:
        snapshot.level = SYSTEM_LEVEL_SCANNED_LOCAL
    name = getattr(system, "name", None)
    if isinstance(name, str) and name:
        snapshot.name = name
    primary_emoji_id = getattr(system, "emoji_id", None)
    if isinstance(primary_emoji_id, str) and primary_emoji_id:
        snapshot.primary_emoji_id = primary_emoji_id
    government_id = getattr(system, "government_id", None)
    if isinstance(government_id, str) and government_id:
        snapshot.government_id = government_id
    snapshot.last_seen_turn = current_turn
    player_state.known_systems[system_id] = snapshot.to_dict()


def mark_system_visited(player_state, system, *, current_turn: int) -> None:
    """
    Upgrade a system to visited and refresh stable facts:
    name, primary emoji, government, population, last_seen_turn.
    """
    system_id = getattr(system, "system_id", None)
    if not isinstance(system_id, str) or not system_id:
        return
    snapshot = _get_or_create_system_snapshot(player_state, system_id)
    snapshot.level = SYSTEM_LEVEL_VISITED
    name = getattr(system, "name", None)
    if isinstance(name, str) and name:
        snapshot.name = name
    primary_emoji_id = getattr(system, "emoji_id", None)
    if isinstance(primary_emoji_id, str) and primary_emoji_id:
        snapshot.primary_emoji_id = primary_emoji_id
    government_id = getattr(system, "government_id", None)
    if isinstance(government_id, str) and government_id:
        snapshot.government_id = government_id
    population = getattr(system, "population", None)
    if isinstance(population, (int, float)):
        snapshot.population = int(population)
    snapshot.last_seen_turn = current_turn
    player_state.known_systems[system_id] = snapshot.to_dict()


# ---------------------------------------------------------------------------
# Destination knowledge updates
# ---------------------------------------------------------------------------

def mark_system_destinations_local_visible(player_state, system, *, current_turn: int) -> None:
    """
    Mark all destinations in the given system as local_visible for current observability.

    This does NOT promote them to visited and does NOT by itself constitute persistent
    visited knowledge, but it may record stable facts as learned for later use.
    """
    system_id = getattr(system, "system_id", None)
    if not isinstance(system_id, str) or not system_id:
        return
    destinations = getattr(system, "destinations", None) or []
    store: Dict[str, Dict[str, Any]] = getattr(player_state, "known_destinations", {})
    for destination in destinations:
        dest_id = getattr(destination, "destination_id", None)
        if not isinstance(dest_id, str) or not dest_id:
            continue
        snapshot = _get_or_create_destination_snapshot(player_state, dest_id, system_id)
        # Upgrade level to at least local_visible, but never to visited here
        if snapshot.level in (DEST_LEVEL_UNKNOWN,):
            snapshot.level = DEST_LEVEL_LOCAL_VISIBLE
        name = getattr(destination, "display_name", None)
        if isinstance(name, str) and name:
            snapshot.name = name
        dest_type = getattr(destination, "destination_type", None)
        if isinstance(dest_type, str) and dest_type:
            snapshot.destination_type = dest_type
        population = getattr(destination, "population", None)
        if isinstance(population, (int, float)):
            snapshot.population = int(population)
        primary_econ = getattr(destination, "primary_economy_id", None)
        if isinstance(primary_econ, str) and primary_econ:
            snapshot.primary_economy_id = primary_econ
        secondary_econs = getattr(destination, "secondary_economy_ids", None) or []
        if isinstance(secondary_econs, (list, tuple)):
            snapshot.secondary_economy_ids = [str(x) for x in secondary_econs]
        snapshot.last_seen_turn = current_turn
        store[dest_id] = snapshot.to_dict()
    player_state.known_destinations = store


def mark_destination_visited(player_state, system_id: Optional[str], destination, *, current_turn: int) -> None:
    """
    Upgrade a destination to visited and refresh stable facts.
    """
    dest_id = getattr(destination, "destination_id", None)
    if not isinstance(dest_id, str) or not dest_id:
        return
    snapshot = _get_or_create_destination_snapshot(player_state, dest_id, system_id)
    snapshot.level = DEST_LEVEL_VISITED
    name = getattr(destination, "display_name", None)
    if isinstance(name, str) and name:
        snapshot.name = name
    dest_type = getattr(destination, "destination_type", None)
    if isinstance(dest_type, str) and dest_type:
        snapshot.destination_type = dest_type
    population = getattr(destination, "population", None)
    if isinstance(population, (int, float)):
        snapshot.population = int(population)
    primary_econ = getattr(destination, "primary_economy_id", None)
    if isinstance(primary_econ, str) and primary_econ:
        snapshot.primary_economy_id = primary_econ
    secondary_econs = getattr(destination, "secondary_economy_ids", None) or []
    if isinstance(secondary_econs, (list, tuple)):
        snapshot.secondary_economy_ids = [str(x) for x in secondary_econs]
    snapshot.last_seen_turn = current_turn
    player_state.known_destinations[destination.destination_id] = snapshot.to_dict()


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

def get_system_view(
    player_state,
    sector,
    *,
    system_id: str,
    current_system_id: str,
    current_turn: int,
    live_situations: Optional[Iterable[str]] = None,
) -> SystemView:
    """
    Build a player-visible view of a system that respects knowledge levels and
    stale knowledge rules. Situations are live-only and only attached if this
    is the current system.
    """
    systems_store: Dict[str, Dict[str, Any]] = getattr(player_state, "known_systems", {})
    snapshot_data = systems_store.get(system_id)
    if isinstance(snapshot_data, dict):
        snapshot = SystemKnowledgeSnapshot.from_dict(snapshot_data)
    else:
        snapshot = SystemKnowledgeSnapshot(system_id=system_id)
    # Derive base fields from snapshot
    level = snapshot.level
    name = snapshot.name or system_id
    primary_emoji_id = snapshot.primary_emoji_id
    government_display = snapshot.government_id
    population_display = snapshot.population if level == SYSTEM_LEVEL_VISITED else None

    is_live = current_system_id == system_id
    if is_live:
        # For live views, we may choose to show current world state, but snapshot remains as stored knowledge.
        pass
    is_stale = False  # Staleness detection can be added later if needed.

    visible_situations: List[str] = []
    if is_live and live_situations:
        visible_situations = [str(s) for s in live_situations]

    return SystemView(
        system_id=system_id,
        level=level,
        name=name,
        primary_emoji_id=primary_emoji_id,
        government_display=government_display,
        population_display=population_display,
        live_situations=visible_situations,
        is_live=is_live,
        last_seen_turn=snapshot.last_seen_turn,
        is_stale=is_stale,
    )


def get_destination_view(
    player_state,
    sector,
    *,
    destination_id: str,
    current_system_id: str,
    current_destination_id: Optional[str],
    current_turn: int,
    live_situations: Optional[Iterable[str]] = None,
) -> DestinationView:
    """
    Build a player-visible view of a destination that respects knowledge levels
    and stale knowledge rules. Situations are live-only and only attached if
    this is the current destination.
    """
    dest_store: Dict[str, Dict[str, Any]] = getattr(player_state, "known_destinations", {})
    snapshot_data = dest_store.get(destination_id)
    if isinstance(snapshot_data, dict):
        snapshot = DestinationKnowledgeSnapshot.from_dict(snapshot_data)
    else:
        snapshot = DestinationKnowledgeSnapshot(destination_id=destination_id, system_id=None)

    level = snapshot.level
    name = snapshot.name or destination_id
    destination_type = snapshot.destination_type
    primary_emoji_id: Optional[str] = None
    population_display = snapshot.population if level in (DEST_LEVEL_LOCAL_VISIBLE, DEST_LEVEL_VISITED) else None
    primary_economy_display = snapshot.primary_economy_id if level in (DEST_LEVEL_LOCAL_VISIBLE, DEST_LEVEL_VISITED) else None
    secondary_economies_display = snapshot.secondary_economy_ids if level in (DEST_LEVEL_LOCAL_VISIBLE, DEST_LEVEL_VISITED) else []

    is_live = current_destination_id == destination_id
    visible_situations: List[str] = []
    if is_live and live_situations:
        visible_situations = [str(s) for s in live_situations]

    is_stale = False  # As with systems, explicit staleness detection is optional for now.

    return DestinationView(
        destination_id=destination_id,
        system_id=snapshot.system_id,
        level=level,
        name=name,
        destination_type=destination_type,
        primary_emoji_id=primary_emoji_id,
        population_display=population_display,
        primary_economy_display=primary_economy_display,
        secondary_economies_display=secondary_economies_display,
        live_situations=visible_situations,
        is_live=is_live,
        last_seen_turn=snapshot.last_seen_turn,
        is_stale=is_stale,
    )

