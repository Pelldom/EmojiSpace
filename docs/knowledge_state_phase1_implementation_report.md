# Knowledge State / Fog-of-War — Phase 1 Implementation Report

## 1. Files Created/Modified

- **Created**
  - `src/knowledge_state.py`

- **Modified**
  - `src/player_state.py`
  - `src/game_engine.py`

---

## 2. Knowledge-State Module API (Phase 1)

**Module**: `src/knowledge_state.py`

### Constants

- `SYSTEM_LEVEL_UNKNOWN`, `SYSTEM_LEVEL_DETECTED`, `SYSTEM_LEVEL_SCANNED_LOCAL`, `SYSTEM_LEVEL_VISITED`
- `DEST_LEVEL_UNKNOWN`, `DEST_LEVEL_LOCAL_VISIBLE`, `DEST_LEVEL_VISITED`

### Snapshot dataclasses

- **SystemKnowledgeSnapshot**
  - Fields: `system_id`, `level`, `name`, `primary_emoji_id`, `government_id`, `population`, `last_seen_turn`
  - Methods: `to_dict()`, `from_dict()`

- **DestinationKnowledgeSnapshot**
  - Fields: `destination_id`, `system_id`, `level`, `name`, `destination_type`, `population`, `primary_economy_id`, `secondary_economy_ids`, `last_seen_turn`
  - Methods: `to_dict()`, `from_dict()`

### View dataclasses

- **SystemView**
  - Fields: `system_id`, `level`, `name`, `primary_emoji_id`, `government_display`, `population_display`, `live_situations`, `is_live`, `last_seen_turn`, `is_stale`

- **DestinationView**
  - Fields: `destination_id`, `system_id`, `level`, `name`, `destination_type`, `primary_emoji_id`, `population_display`, `primary_economy_display`, `secondary_economies_display`, `live_situations`, `is_live`, `last_seen_turn`, `is_stale`

### Initialization

- **`initialize_player_knowledge(player_state, sector, *, current_turn: int) -> None`**
  - For each system in `sector.systems`, inserts a `SystemKnowledgeSnapshot` at **`detected`** level into `player_state.known_systems`.
  - Does **not** mark any system as visited.
  - Does **not** create any destination knowledge.
  - Leaves `unknown` available but unused for normal systems per current-phase assumption.

### System updates

- **`mark_system_scanned_local(player_state, system, *, current_turn: int) -> None`**
  - Ensures a snapshot exists for `system.system_id`.
  - Upgrades level at most to `scanned_local` (`unknown → detected → scanned_local`).
  - Records `name`, `primary_emoji_id` (if present), `government_id` (from `system.government_id`), updates `last_seen_turn`.
  - Caller is responsible for only using this when the system is in range using authoritative travel logic (no range math here).

- **`mark_system_visited(player_state, system, *, current_turn: int) -> None`**
  - Ensures a snapshot exists and sets `level = visited`.
  - Refreshes stable facts from world state: `name`, `primary_emoji_id`, `government_id`, `population` (if numeric), `last_seen_turn`.

### Destination updates

- **`mark_system_destinations_local_visible(player_state, system, *, current_turn: int) -> None`**
  - For each destination in `system.destinations`:
    - Ensures a snapshot exists (with `system_id`).
    - If level is `unknown`, upgrades to `local_visible` (never to `visited`).
    - Records stable facts for **current observability**: `name` (`display_name`), `destination_type`, `population`, `primary_economy_id`, `secondary_economy_ids`, `last_seen_turn`.
  - This satisfies “entering a system gives local visibility only” and does **not** auto-visit destinations.

- **`mark_destination_visited(player_state, system_id: str | None, destination, *, current_turn: int) -> None`**
  - Ensures a snapshot exists and sets `level = visited`.
  - Refreshes stable facts from world state: `name`, `destination_type`, `population`, `primary_economy_id`, `secondary_economy_ids`, `last_seen_turn`.

### Views (no CLI coupling yet)

- **`get_system_view(player_state, sector, *, system_id: str, current_system_id: str, current_turn: int, live_situations: Iterable[str] | None = None) -> SystemView`**
  - Uses `player_state.known_systems[system_id]` (or default snapshot) to determine `level`, `name` (defaulting to `system_id`), `primary_emoji_id`, `government_display`, `population_display` (only when `level == visited`).
  - `is_live` is `True` only if `current_system_id == system_id`.
  - Attaches `live_situations` **only when `is_live`**; otherwise empty.
  - `is_stale` is wired but left as `False` until explicit staleness detection is needed.

- **`get_destination_view(player_state, sector, *, destination_id: str, current_system_id: str, current_destination_id: str | None, current_turn: int, live_situations: Iterable[str] | None = None) -> DestinationView`**
  - Uses `player_state.known_destinations[destination_id]` (or default snapshot) to determine `level`, `name` (defaulting to `destination_id`), `destination_type`.
  - `population_display`, `primary_economy_display`, `secondary_economies_display` only when `level in {local_visible, visited}`.
  - `is_live` is `True` only if `current_destination_id == destination_id`.
  - Attaches `live_situations` **only when `is_live`**.
  - `is_stale` set to `False` for now.

Situations are explicitly **not** stored in snapshots; they are only passed in via `live_situations` when the caller chooses (typically from engine’s active situation queries).

---

## 3. Player-State Extensions

**File**: `src/player_state.py`

### New fields on `PlayerState`

- `known_systems: Dict[str, Dict[str, Any]] = field(default_factory=dict)`
- `known_destinations: Dict[str, Dict[str, Any]] = field(default_factory=dict)`

### `from_dict` normalization

- Existing normalization for `visited_system_ids` / `visited_destination_ids` preserved.
- New normalization:
  - **known_systems**: Accepts any dict-like payload; filters to `str` keys with dict values and copies each snapshot as `dict(snapshot)`. Non-dict or malformed entries are ignored.
  - **known_destinations**: Same normalization behavior as `known_systems`.

### `to_dict` serialization

- New keys added to the payload:
  - `"known_systems": {str(k): dict(v) for k, v in self.known_systems.items()}`
  - `"known_destinations": {str(k): dict(v) for k, v in self.known_destinations.items()}`

---

## 4. Minimal Integration Points Added

**File**: `src/game_engine.py`

### Imports

```python
from knowledge_state import (
    initialize_player_knowledge,
    mark_destination_visited,
    mark_system_destinations_local_visible,
    mark_system_visited,
)
```

### 4.1 New game initialization

In `GameEngine.__init__` after sector generation and before time engine setup:

- **Existing behavior (unchanged):**
  - Create `PlayerState` with `current_system_id` set to `self.sector.systems[0].system_id`.
  - `_apply_default_start_location()` resolves starting destination.
  - Mark starting system and starting destination in `visited_system_ids` / `visited_destination_ids`.
  - Populate `_pending_initialization_event` flags used by Phase 7.6 fog-of-war tests.

- **New knowledge initialization** (added immediately after `_pending_initialization_event`):
  - `initialize_player_knowledge(self.player_state, self.sector, current_turn=0)`
  - `mark_system_visited(self.player_state, starting_system, current_turn=0)`
  - `mark_system_destinations_local_visible(self.player_state, starting_system, current_turn=0)`
  - If starting destination is set, find it in `starting_system.destinations` and call `mark_destination_visited(...)` for it.

**Effects:**

- All systems start at **`detected`** level via `initialize_player_knowledge`.
- Starting system is immediately upgraded to **`visited`** knowledge and its stable facts are snapshotted.
- All starting-system destinations are marked **`local_visible`** for observability.
- Starting destination, if present, is marked **`visited`** at destination level and its stable facts are captured.
- Legacy `visited_system_ids` / `visited_destination_ids` behavior remains intact.

### 4.2 Travel arrival (system/destination entry)

In the travel resolution code (where movement is finalized), after updating `current_system_id`, `current_destination_id`, and `visited_*` sets:

- `target_system = self.sector.get_system(target_system_id)`
- If `target_system` is not None:
  - `mark_system_visited(self.player_state, target_system, current_turn=context.turn_before)`
  - `mark_system_destinations_local_visible(self.player_state, target_system, current_turn=context.turn_before)`
  - If `target_destination_id` is a string, find the matching destination in `target_system.destinations` and call `mark_destination_visited(...)` for it.

**Effects:**

- System entry: legacy `visited_system_ids` updated; knowledge layer upgrades that system to `visited` and refreshes its snapshot.
- Destination local visibility: all destinations in the target system become `local_visible`; they are **not** marked `visited`.
- Destination entry: only the destination actually entered is upgraded to `visited` and its snapshot refreshed.

**Note:** `mark_system_scanned_local` is implemented but **not yet called** anywhere; it is available for future wiring wherever the authoritative reachable-systems logic exists.

---

## 5. Phase-1 Validation Against Requirements

| Requirement | Status |
|-------------|--------|
| All systems begin detected | Yes — `initialize_player_knowledge` sets every `sector.systems` entry to `detected` level with minimal snapshots. |
| Visited systems store population/government snapshots | Yes — `mark_system_visited` records `name`, `primary_emoji_id`, `government_id`, `population`, `last_seen_turn` on each visit. |
| Entering a system does not auto-visit all destinations | Yes — `mark_system_destinations_local_visible` only upgrades destination level to `local_visible`; only the destination actually entered is upgraded via `mark_destination_visited`. |
| Destinations in current system can be treated as local_visible | Yes — On new game and on each travel arrival, `mark_system_destinations_local_visible` is called for the current system. |
| Visiting a destination stores its stable facts | Yes — `mark_destination_visited` captures destination-level stable facts whenever the player actually enters that destination. |
| Situations are not persisted as stored knowledge | Yes — No snapshot structures include situations; views accept `live_situations` only when `is_live`. |
| Knowledge snapshots remain separate from live world state | Yes — Snapshots live in `PlayerState.known_systems` / `known_destinations` and are updated only by explicit `mark_*` functions. |
| No broad UI/CLI rewrite attempted | Yes — No CLI or renderer files were modified. |

---

## 6. Follow-up Needed Before Phase 2 CLI Adoption

- **Range-based scanned_local wiring**
  - `mark_system_scanned_local` is implemented but **not yet used**.
  - Phase 2 should identify the authoritative reachable-systems logic and call `mark_system_scanned_local` for those in-range systems, without duplicating range math.

- **Front-end integration with views**
  - CLI and future UIs should replace direct checks on `visited_system_ids` / `visited_destination_ids` with `get_system_view(...)` and `get_destination_view(...)`, and use `level` and the contract visibility matrices to decide emoji profile, population/tier, economies, and live situations.

- **Optional staleness indicators**
  - `SystemView.is_stale` / `DestinationView.is_stale` are currently always `False`; future work can introduce explicit staleness detection and UI hints.

- **Additional tests**
  - Add unit/integration tests that verify `known_systems` is populated at `detected` on new game, that visited system/destination snapshots persist across travel and save/load, and that entering a system only elevates destinations to `local_visible` and not `visited`.
