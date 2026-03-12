## Fog-of-War / Player Knowledge Handler Design

### 1. Current-state audit

#### 1.1 Where visited / visibility state lives

- **Player-state knowledge flags**
  - **File**: `src/player_state.py`
  - **Class**: `PlayerState`
    - **Fields**:
      - `visited_system_ids: set[str]`
      - `visited_destination_ids: set[str]`
    - **Deserialization**: `PlayerState.from_dict` normalizes `visited_system_ids` and `visited_destination_ids` from lists/sets to `set[str]`.
    - **Serialization**: `PlayerState.to_dict` writes `visited_system_ids` and `visited_destination_ids` as sorted lists.

- **Marking systems/destinations as visited (engine)**
  - **File**: `src/game_engine.py`
  - **Initialization / start-of-game**:
    - Marks the starting `current_system_id` and `current_destination_id` as visited and records whether that marking was newly applied in `_pending_initialization_event`.
  - **On travel completion**:
    - When a travel action resolves, the engine:
      - Updates `player_state.current_system_id`, `current_destination_id`, and `current_location_id`.
      - Adds `target_system_id` to `visited_system_ids`.
      - Adds `target_destination_id` (if non-empty string) to `visited_destination_ids`.
      - Mirrors current system/destination onto the active ship (`current_system_id`, `current_destination_id`, `destination_id`).
  - **Rumor / intel logic that checks knowledge**:
    - The engine chooses rumor text based on whether `hint_system_id` and `hint_destination_id` exist in the visited sets.

- **Visited helper accessors (CLI runner)**
  - **File**: `src/run_game_engine_cli.py`
  - **System helper**:
    - `_visited_system_ids(engine)` normalizes `engine.player_state.visited_system_ids` from set/list to `set[str]`.
  - **Destination helper**:
    - `_visited_destination_ids(engine)` does the same for `visited_destination_ids`.

#### 1.2 Where fog-of-war / visibility is enforced today

Current implementation is essentially **boolean visited/not-visited**, wired directly into CLI display helpers via a `visible: bool` flag. There is no central “knowledge level” abstraction yet.

- **Emoji/visibility rendering (CLI-only helpers)**
  - **File**: `src/emojispace_cli_v1.py`
    - `_entity_display(entity, name, visible: bool)`:
      - If `visible` is `False`, returns `name` only.
      - If `visible` is `True`, calls `format_entity_name` to build the emoji profile + name string.
  - **File**: `cli/cli_renderer.py`
    - `render_entity(entity, name, visible: bool = True)`:
      - If `visible` is `False`, returns `name` only.
      - If `visible` is `True`, calls `format_entity_name` with robust error handling.

- **System visibility hook points (CLI)**
  - **Galaxy map (screen-wide map)**
    - **Function**: `_render_galaxy_map` in `src/run_game_engine_cli.py`.
    - For each system in the legend, it checks `system.system_id in _visited_system_ids(engine)` and passes that boolean into `_format_name_with_profile` to decide whether to show emoji profile or plain name.
  - **Galaxy summary / debug visibility**
    - **Function**: `_galaxy_summary` in `src/run_game_engine_cli.py`.
    - For each system, computes `visible = system.system_id in _visited_system_ids(engine)` and uses it when building the display name.
  - **Travel menu (reachable systems listing)**
    - Uses `_visited_system_ids` to gate emoji profile when showing reachable systems in jump range (reachable systems menu).
  - **Mission summaries referring to systems**
    - When rendering mission targets, `target_system_id in _visited_system_ids(engine)` decides whether target system appears with emoji profile or plain name.
  - **Current system label in main HUD**
    - When printing the current system name in the main loop, `current_system.system_id in _visited_system_ids(engine)` is used as `visible` for `_format_name_with_profile`.

- **Destination visibility hook points (CLI)**
  - **System info block / destinations listing inside a system**
    - In `src/run_game_engine_cli.py`, when printing a system info block, destinations are listed with:
      - `visible = destination.destination_id in _visited_destination_ids(engine)`
      - Passed into `_format_name_with_profile(_destination_display_entity(destination), destination.display_name, visible)`.
  - **Destination context header (HUD panel)**
    - `_print_destination_context(engine)`:
      - Calls `engine.get_current_destination_context()` for structured system/destination info.
      - Retrieves `destination_id` and `system_id` from the context.
      - Computes:
        - `dest_visible = dest_id in _visited_destination_ids(engine)` if `dest_id` is set.
        - `sys_visible = system_id in _visited_system_ids(engine)` if `system_id` is set.
      - Uses those flags to decide whether to pass emoji-capable entities into `_format_name_with_profile` or show plain names.
  - **Intra-system destination chooser**
    - `_print_current_system_destinations(engine)`:
      - For each destination, `visible = destination.destination_id in _visited_destination_ids(engine)` and passed into `_format_name_with_profile`.
  - **Other menus referencing destinations**
    - Active mission targets, warehouse lists, rental menus, and destination summaries consistently follow the same pattern:
      - Compute `visible = destination_id in _visited_destination_ids(engine)` (or a similar check).
      - Pass that boolean into `_format_name_with_profile` or `render_entity`.

#### 1.3 Destination/system context and “sensitive” fields

- **File**: `src/game_engine.py`
- **Function**: `GameEngine.get_current_destination_context`
  - Returns a dict with:
    - Destination: `destination_name`, `destination_type`, `destination_id`, `emoji_id`, `population`.
    - System: `system_id`, `system_name`.
    - “Sensitive” / gated fields: `system_government`, `primary_economy`, `secondary_economies`, `active_situations`.
  - Behavior:
    - If there is no current destination, returns a fully-structured but mostly-empty context (unknown names and IDs).
    - If the system object is missing, returns destination data but no system government/economy/situations.
    - For a valid system and destination:
      - Always fills base fields (names, IDs, population).
      - Computes `system_visited = system.system_id in self.player_state.visited_system_ids`.
      - Only if `system_visited` is `True`:
        - Fills `system_government` from the government registry (or raw id).
        - Fills `primary_economy` and `secondary_economies` from the destination.
        - Fills `active_situations` from `_active_situation_rows_for_system(system_id=system.system_id)`.
  - Tests:
    - **File**: `tests/test_destination_context.py`
      - `test_destination_context_visited_system` asserts that:
        - For a visited system, government/economy/situations are present/populated.
      - `test_destination_context_unvisited_system` asserts that:
        - For an unvisited system, government string is empty, primary economy is `None`, secondary economies list is empty, and `active_situations` is empty.
      - `test_destination_context_deterministic` checks determinism across runs with the same seed.
      - `test_destination_context_no_destination` verifies robustness when `current_destination_id` is `None`.

#### 1.4 World mutation logic affecting “facts”

- **Situations (dynamic, time-based)**
  - Generated and expired via the time engine and world state.
  - Surface through:
    - `_active_situation_rows_for_system(system_id=...)`, which aggregates situation ids affecting a system.
    - `_active_destination_situations(destination_id=...)`, which filters system-scope situations to those targeting the current destination.
  - These are **live-only** facts; there is currently **no persistence** of “last-known situations” in `PlayerState`.
  - Visibility gating:
    - `get_current_destination_context` includes system-scope situations (`active_situations`) only when `system_visited` is `True`.
    - Destination-scope situations are fetched separately where needed (e.g., exploration/mining flows).

- **Structural facts (population, government, economies)**
  - Generated in:
    - `world_generator.py` (systems and destinations, including population and base naming).
    - `market_creation.py` (economy scaffolding).
  - As of this audit, there is no obvious runtime mutation of:
    - `system.name`, `system.government_id`, or any system-level population field.
    - `destination.display_name`, `destination.population`, `destination.primary_economy_id`, `destination.secondary_economy_ids`.
  - However, future mechanics (e.g., coups, disasters) could change these fields at runtime through:
    - `world_state_engine.py` and various resolvers.
  - The new design must assume such mutations can occur, and clearly distinguish **current world state** from **last-known player knowledge**.

#### 1.5 Summary of current visibility behavior

- **Systems**
  - Visibility is a **binary visited/not-visited** flag via `visited_system_ids`.
  - When `visible` is `False`:
    - CLI shows plain names, suppressing emoji profile.
  - When `visible` is `True`:
    - CLI shows emoji profile + name via `format_entity_name`.
  - System government/population/economy are gated mainly via `get_current_destination_context` and not through a dedicated system-knowledge layer.

- **Destinations**
  - Also a **binary** visited/not-visited decision via `visited_destination_ids`.
  - When not visited:
    - Only names are shown; emoji profiles (tier, economies, etc.) are suppressed in displays that use `_format_name_with_profile` or `render_entity`.
  - The only structured visibility-aware context is `get_current_destination_context`, which gates system government/economies by system visited state, not destination visited state.

- **Situations**
  - Exposed only through:
    - `active_situations` in `get_current_destination_context` (system-scope).
    - `_active_destination_situations` for destination-scope checks.
  - Not persisted on the player side; always recomputed from world state.

Overall, visibility and “knowledge” are currently driven by **two flat sets** (`visited_system_ids` / `visited_destination_ids`) plus some ad-hoc logic in `get_current_destination_context` and repeated CLI checks.

---

### 2. Proposed knowledge model

Design a centralized, reusable **player knowledge layer** that decouples:

- **Source-of-truth world state** (systems, destinations, situations).
- **Player knowledge snapshots** (what the player remembers).
- **Knowledge level** (unknown/detected/scanned_local/visited or unknown/local_visible/visited).

#### 2.1 Core concepts

- **System knowledge entry** (per `system_id`):
  - Snapshot of what the player last knew about that system.
  - Explicit knowledge level: `unknown`, `detected`, `scanned_local`, `visited`.
  - Fields that may diverge from live world state (government, population, etc.).
- **Destination knowledge entry** (per `destination_id`):
  - Snapshot of what the player last knew about that destination.
  - Knowledge level: `unknown`, `local_visible`, `visited`.
- **Live vs last-known**
  - For each field, the handler can answer:
    - “What should we display right now?”
    - “Is this data a **live view** (we are currently here) or a **snapshot** (stale but remembered)?”

#### 2.2 System knowledge snapshot

Conceptual data model (Python-ish, for design only):

```python
class SystemKnowledgeLevel(Enum):
    UNKNOWN = "unknown"
    DETECTED = "detected"
    SCANNED_LOCAL = "scanned_local"
    VISITED = "visited"


@dataclass
class SystemKnowledgeSnapshot:
    system_id: str
    level: SystemKnowledgeLevel

    # Learned, persistent facts (may differ from current world state)
    name: str | None = None                 # last-known system name
    primary_emoji_id: str | None = None     # last-known primary emoji source
    known_government_id: str | None = None  # last-known government id or display label
    known_population: int | None = None     # last-known population / tier proxy
    last_seen_turn: int | None = None       # last turn we saw authoritative info

    # Optional: provenance / extension hooks
    last_seen_source: str | None = None     # e.g. "visited", "scan", "intel"
```

Notes vs locked rules:

- **Primary emoji + system name are always visible once system is known enough to appear at all**:
  - `name` and `primary_emoji_id` are filled at least from `detected` onward.
- **Systems within jump range also show government emoji (local knowledge)**:
  - `known_government_id` is set when upgrading to `scanned_local` or better.
- **Population/tier ONLY visible once visited**:
  - `known_population` is only filled (or refreshed) in `mark_system_visited`.
- **If a system changes later**, snapshot fields remain “last-known” until revisited:
  - Handler may detect and flag staleness, but does not auto-refresh snapshots.

#### 2.3 Destination knowledge snapshot

```python
class DestinationKnowledgeLevel(Enum):
    UNKNOWN = "unknown"
    LOCAL_VISIBLE = "local_visible"
    VISITED = "visited"


@dataclass
class DestinationKnowledgeSnapshot:
    destination_id: str
    system_id: str | None
    level: DestinationKnowledgeLevel

    # Learned, persistent facts
    name: str | None = None
    destination_type: str | None = None
    known_population: int | None = None
    known_primary_economy: str | None = None
    known_secondary_economies: list[str] | None = None
    last_seen_turn: int | None = None
    last_seen_source: str | None = None     # e.g. "local_visibility", "visited"
```

Notes vs locked rules:

- **Once the player is in the same system, full destination Emoji Profile becomes visible EXCEPT situations**:
  - When player is in the same system, destinations move to at least `LOCAL_VISIBLE` and the handler can populate live fields for name, type, population, and economies.
- **Situations visible only while currently at that destination**:
  - Situations are not persisted in the snapshot (or, if ever stored, are clearly flagged as ephemeral and never used outside the “current destination” view).
- **Once visited / learned, destination information remains available later as last-known info**:
  - At `LOCAL_VISIBLE`, as soon as the player can see the info in-system, that data can be recorded as “learned” and later reused.
  - At `VISITED`, visiting the destination refreshes these fields with authoritative values.
- **If a destination changes later**, snapshot remains stale until revisiting:
  - `known_population` and `known_*_economy` are not updated until `mark_destination_visited` is called again.

#### 2.4 Storage location

Introduce a `PlayerKnowledgeState` container:

```python
@dataclass
class PlayerKnowledgeState:
    systems: dict[str, SystemKnowledgeSnapshot] = field(default_factory=dict)
    destinations: dict[str, DestinationKnowledgeSnapshot] = field(default_factory=dict)
```

This can be attached to `PlayerState`:

- As a `knowledge_state` field serialized by `PlayerState.to_dict()` / `from_dict()`.
- Or as a parallel object stored alongside `PlayerState` in the save file.

Long-term, `visited_system_ids` and `visited_destination_ids` can be derived from this knowledge model:

- `visited_system_ids = {s.system_id for s in knowledge.systems.values() if s.level == SystemKnowledgeLevel.VISITED}`
- `visited_destination_ids = {d.destination_id for d in knowledge.destinations.values() if d.level == DestinationKnowledgeLevel.VISITED}`

This allows a gradual migration where the new knowledge model becomes the single source of truth.

---

### 3. Knowledge levels: visibility matrices

Define exact visibility for each level.

#### 3.1 Systems: levels and fields

Levels: `unknown`, `detected`, `scanned_local`, `visited`.

Fields:

- **primary**: primary emoji / category (emoji profile primary symbol)
- **name**: system name string
- **government**: government emoji / name (via registry)
- **population/tier**: population or tier marker
- **economies**: currently N/A at system level (future extension)
- **situations**: dynamic events affecting system/destinations

**System visibility matrix**

| Level          | Appears in galaxy map/menus? | Primary | Name | Government | Population/Tier | Economies | Situations (system-scope) |
|----------------|-------------------------------|---------|------|------------|------------------|-----------|---------------------------|
| `unknown`      | No (or generic “unknown” symbol only) | No      | No   | No         | No               | N/A       | No                        |
| `detected`     | Yes (minimal “blip”)         | Yes     | Yes  | No         | No               | N/A       | No                        |
| `scanned_local`| Yes                           | Yes     | Yes  | Yes        | No               | N/A       | No                        |
| `visited`      | Yes                           | Yes     | Yes  | Yes        | Yes              | N/A       | Yes (live-only while at system) |

Clarifications:

- Systems within jump range can be upgraded to `scanned_local`, revealing government (emoji/name) but not population/tier.
- Population/tier are suppressed until `visited`.
- Situations:
  - Are visible only while **currently at that system**.
  - Even at `visited`, they are not persisted; they are derived from live world state when the player is in that system.

#### 3.2 Destinations: levels and fields

Levels: `unknown`, `local_visible`, `visited`.

Fields:

- **primary**: destination primary emoji / type
- **name**: destination display name
- **government**: inherited from system view (via system knowledge)
- **population/tier**: destination population / tier
- **economies**: primary and secondary economies
- **situations**: destination-scoped situations (events)

**Destination visibility matrix**

| Level           | Appears in in-system lists/menus? | Primary | Name | Government (via system) | Population/Tier | Economies | Situations (dest-scope) |
|-----------------|------------------------------------|---------|------|--------------------------|------------------|-----------|--------------------------|
| `unknown`       | No (unless revealed by future mechanics) | No      | No   | N/A                      | No               | No        | No                       |
| `local_visible` | Yes (when in same system)         | Yes     | Yes  | Yes (from system view)   | Yes              | Yes       | Yes, but only when currently at this destination |
| `visited`       | Yes (globally)                    | Yes     | Yes  | Yes (from system view)   | Yes (snapshot)   | Yes (snapshot) | Yes, but only when currently at this destination |

Clarifications:

- When the player is in the same system:
  - Destinations are at least `local_visible` and show full emoji profile (type/name/population/economies) in local menus.
  - Situations are visible for the **current destination only**.
- Once visited:
  - Destination fields in the snapshot (name/type/population/economies) are used for global views (e.g., mission logs, summaries).
  - If the destination changes later, views remain based on last-known snapshot until revisited.

---

### 4. Proposed handler/module API (`knowledge_state.py`)

The handler module should be a reusable **game-state layer** that frontends (CLI, UI, prose generators) query for “player-visible views”.

#### 4.1 Core types (interfaces)

Public types (conceptual):

- `SystemKnowledgeLevel`, `DestinationKnowledgeLevel` enums.
- `SystemKnowledgeSnapshot`, `DestinationKnowledgeSnapshot` dataclasses.
- `PlayerKnowledgeState` dataclass with `systems` and `destinations` mappings.

#### 4.2 View types returned to consumers

Provide view objects that represent what the player sees **right now**, including provenance:

```python
@dataclass
class SystemView:
    system_id: str
    level: SystemKnowledgeLevel

    name: str
    primary_emoji_id: str | None
    government_display: str | None
    population_display: int | None

    is_live: bool              # True if currently at this system and fields match live world
    last_seen_turn: int | None
    is_stale: bool             # True if snapshot differs from current world state


@dataclass
class DestinationView:
    destination_id: str
    system_id: str | None
    level: DestinationKnowledgeLevel

    name: str
    destination_type: str | None
    primary_emoji_id: str | None
    population_display: int | None
    primary_economy_display: str | None
    secondary_economies_display: list[str]

    live_situations: list[str]  # Only filled when currently at this destination

    is_live: bool
    last_seen_turn: int | None
    is_stale: bool
```

#### 4.3 Query functions

Core public functions:

- **System queries**
  - `get_system_knowledge_level(player_knowledge, system_id) -> SystemKnowledgeLevel`
    - Returns `unknown` if no entry exists.
  - `get_system_view(player_knowledge, player_state, world_state, system_id, current_turn) -> SystemView`
    - Inputs:
      - `player_knowledge`: `PlayerKnowledgeState`.
      - `player_state`: `PlayerState` (for current location).
      - `world_state`: abstraction over sector/systems (e.g., `GameEngine` or a thin wrapper).
      - `current_turn`: for staleness calculations.
    - Behavior:
      - Determines level from snapshots plus locality (jump range, current system).
      - Merges snapshot with live world state according to the system visibility matrix.

- **Destination queries**
  - `get_destination_knowledge_level(player_knowledge, destination_id) -> DestinationKnowledgeLevel`
  - `get_destination_view(player_knowledge, player_state, world_state, destination_id, current_turn) -> DestinationView`
    - Behavior:
      - Determines if destination is `unknown`, `local_visible`, or `visited`.
      - Populates:
        - Snapshot-derived fields for stable facts.
        - Live-only `live_situations` when currently at destination.
        - `is_live` / `is_stale` flags.

#### 4.4 Update/mutation functions

All knowledge updates should go through centralized functions:

- **Systems**
  - `ensure_system_detected(player_knowledge, system_id, *, current_turn)`
    - Called when a system should appear on the galaxy map at all.
    - Sets `UNKNOWN → DETECTED` (no other fields required).
  - `mark_system_scanned_local(player_knowledge, system_id, world_state, *, current_turn)`
    - Called when system is scanned locally (e.g., in jump range).
    - Upgrades to at least `SCANNED_LOCAL`.
    - Records `name`, `primary_emoji_id`, `known_government_id` in snapshot.
  - `mark_system_visited(player_knowledge, system_id, world_state, *, current_turn)`
    - Called when the player enters a system.
    - Upgrades to `VISITED`.
    - Refreshes snapshot fields, including `known_population` and `known_government_id`.

- **Destinations**
  - `ensure_destination_local_visible(player_knowledge, system_id, destination_id, world_state, *, current_turn)`
    - Called when listing in-system destinations.
    - Sets at least `LOCAL_VISIBLE`.
    - Fills name, type, population, primary/secondary economies in snapshot as “learned”.
  - `mark_destination_visited(player_knowledge, system_id, destination_id, world_state, *, current_turn)`
    - Called when the player arrives at a destination.
    - Upgrades to `VISITED`.
    - Refreshes stable snapshot fields (name/type/population/economies, last_seen_turn).

#### 4.5 Helper/introspection functions

Additional utilities:

- `get_last_known_system_snapshot(player_knowledge, system_id) -> SystemKnowledgeSnapshot | None`
- `get_last_known_destination_snapshot(player_knowledge, destination_id) -> DestinationKnowledgeSnapshot | None`
- `is_system_info_live(player_state, system_id) -> bool`
- `is_destination_info_live(player_state, destination_id) -> bool`
- Potential helpers to derive legacy sets:
  - `derive_visited_system_ids(player_knowledge) -> set[str]`
  - `derive_visited_destination_ids(player_knowledge) -> set[str]`

These helper functions make it easier for existing code to migrate gradually onto the new model.

---

### 5. Refresh / staleness rules

#### 5.1 System knowledge

- **Creating/upgrading**
  - At world generation / game start:
    - Mark all initially-known systems as at least `DETECTED`.
    - Mark the starting system as `VISITED` via `mark_system_visited`.
  - When a system enters jump range:
    - Call `ensure_system_detected`.
    - Call `mark_system_scanned_local` to upgrade to `SCANNED_LOCAL` and record government and primary emoji.
  - When traveling to a system (arrival event):
    - Call `mark_system_visited`:
      - Upgrades level to `VISITED`.
      - Refreshes snapshot fields, including population/tier.
  - When receiving intel/missions about a system:
    - At minimum, call `ensure_system_detected`.
    - Optionally call `mark_system_scanned_local` if the intel should reveal government.

- **Refreshing**
  - `mark_system_visited` is the **only path** that updates `known_population`.
  - `mark_system_scanned_local` may refresh `known_government_id` and `name` if scans reveal better data.

- **Staleness**
  - If the world state changes a system’s government or population:
    - `SystemKnowledgeSnapshot` remains unchanged until `mark_system_visited` is called again.
  - `SystemView.is_live`:
    - `True` when `player_state.current_system_id == system_id`.
    - `False` otherwise, even if level is `VISITED`.
  - `SystemView.is_stale` (optional) can compare snapshot vs current world state for UI hints like “(out of date)”.

#### 5.2 Destination knowledge

- **Creating/upgrading**
  - When the player is in a system and destinations are listed:
    - For each destination shown:
      - Call `ensure_destination_local_visible`.
      - This:
        - Ensures `level >= LOCAL_VISIBLE`.
        - Stores stable facts (name/type/population/economies) as learned.
  - When the player enters a destination:
    - Call `mark_destination_visited`.
      - Ensures `level == VISITED`.
      - Refreshes stable snapshot fields and `last_seen_turn`.

- **Refreshing**
  - For `VISITED` destinations:
    - Only `mark_destination_visited` should refresh snapshot fields, to keep rules deterministic.
  - For `LOCAL_VISIBLE` destinations:
    - Repeated in-system exposure can call `ensure_destination_local_visible` again:
      - This can refresh data for destinations that have not yet been visited, if desired.

- **Staleness**
  - When world state changes population or economies:
    - `DestinationKnowledgeSnapshot` remains as last-known until `mark_destination_visited` is called.
  - `DestinationView.is_live`:
    - `True` only when `destination_id == player_state.current_destination_id`.
  - `DestinationView.live_situations`:
    - Always fetched from current world state and **not persisted**.

#### 5.3 What does not permanently update knowledge

- Being in jump range:
  - Does **not** reveal population/tier.
  - Does **not** reveal destination details.
  - Only upgrades system to `DETECTED` / `SCANNED_LOCAL` and reveals government per rules.
- Being in the same system:
  - Does **not** persist system-level situations.
  - Does elevate destination knowledge to `LOCAL_VISIBLE` and learn stable facts, but does **not** mark the destination as `VISITED` until entering it.
- Situations:
  - Are never part of persistent snapshots.
  - Always taken live from world state for:
    - System-level situations (while in that system).
    - Destination-level situations (while at that destination).

---

### 6. Integration plan

#### Phase A: Introduce handler and knowledge snapshot storage

1. **Add knowledge model definitions**
   - Create `knowledge_state.py` with:
     - Enums: `SystemKnowledgeLevel`, `DestinationKnowledgeLevel`.
     - Dataclasses: `SystemKnowledgeSnapshot`, `DestinationKnowledgeSnapshot`, `PlayerKnowledgeState`.
     - View dataclasses: `SystemView`, `DestinationView`.
     - Basic getters that return `unknown` levels when no entries exist.

2. **Extend `PlayerState` with knowledge container**
   - Add `knowledge_state` (or similar) to `PlayerState`.
   - Wire into `from_dict` / `to_dict` for persistence.
   - Default to an empty knowledge state when loading old saves.

3. **Implement update/query APIs**
   - Implement:
     - `ensure_system_detected`, `mark_system_scanned_local`, `mark_system_visited`.
     - `ensure_destination_local_visible`, `mark_destination_visited`.
     - `get_system_view`, `get_destination_view`.

4. **Bridge old visited flags**
   - Maintain `visited_system_ids` and `visited_destination_ids` as the canonical truth initially.
   - Derive knowledge entries from these sets on first access.
   - Provide helper functions to derive visited sets from knowledge for later migration.

#### Phase B: Update engine and CLI to use knowledge-filtered views

1. **Engine-side integration**
   - In `GameEngine`:
     - Replace direct `visited_*` updates in:
       - Initialization/start.
       - Travel completion.
     - With calls to:
       - `mark_system_visited`.
       - `mark_destination_visited`.
   - In `get_current_destination_context`:
     - Use `get_system_view` and `get_destination_view` to decide:
       - Whether to include government/economy.
       - What to expose for population/economies.
     - Continue to derive `active_situations` from live world state, gated by current location.

2. **CLI (run_game_engine_cli.py)**
   - Replace `*_visited_ids` checks with knowledge-based helpers:
     - E.g., `_system_visible(system_id)` uses `get_system_view` and the visibility matrix.
     - `_destination_visible(destination_id)` uses `get_destination_view`.
   - For galaxy map, travel menus, and mission summaries:
     - Use `SystemView` / `DestinationView` to drive:
       - Whether emoji profile is shown.
       - Whether population/economies are visible.

3. **Renderer / emoji profile**
   - Keep `render_entity` and `_entity_display` unchanged:
     - They remain generic “show name with or without emoji” utilities.
   - Knowledge handler simply determines `visible: bool` and passes entity/name accordingly.

4. **Regression tests**
   - Ensure existing tests (e.g., `test_destination_context_*`, `test_phase76_fog_of_war_start`, `test_unified_fixes_abcd`) still pass.
   - Add tests that:
     - Force structural changes (mocked) between visits.
     - Assert that views show last-known values until revisited.

#### Phase C: Prepare for future UI/prose systems

1. **Abstract world access for the handler**
   - Define a minimal protocol/interface for `world_state` that supplies:
     - `get_system(system_id)` with fields used by knowledge handler.
     - `get_destination(destination_id)` with fields used by knowledge handler.
   - Make `GameEngine` (and other host code) supply this interface.

2. **Document API contracts**
   - Add a design contract (e.g., `design/knowledge_state_contract.md`) that specifies:
     - What `SystemView` / `DestinationView` guarantee.
     - How knowledge levels map to visibility in various frontends.
     - How to add new knowledge sources (intel, scans, quests) via the handler.

3. **Deprecate direct visited_* usage (later)**
   - Once everything consumes `PlayerKnowledgeState`:
     - Treat `visited_system_ids` / `visited_destination_ids` as derived or legacy.
     - Optionally phase them out after a migration window.

---

### 7. Risks and edge cases

#### 7.1 Hidden systems / secret destinations / undiscovered content

- `UNKNOWN` levels maintain space for:
  - Hidden systems.
  - Secret destinations.
  - Scan-gated or quest-gated content.
- Discovery flows promote:
  - Systems: `UNKNOWN → DETECTED → SCANNED_LOCAL → VISITED`.
  - Destinations: `UNKNOWN → LOCAL_VISIBLE → VISITED`.
- Systems/destinations at `UNKNOWN`:
  - Do not appear in maps/menus (or appear only as generic “unknown” entries).

#### 7.2 Changing governments/populations

- When world state changes `system.government_id` or `destination` populations:
  - Knowledge snapshots do **not** update automatically.
  - `SystemView` / `DestinationView` continue to show last-known values until:
    - `mark_system_visited` or `mark_destination_visited` is called.
- While the player is physically present:
  - `is_live=True` views can reflect current world state.
  - Clients may optionally indicate that previously-seen values were outdated.

#### 7.3 Destination economy changes

- Market or economy changes (e.g., due to events) can alter live economics without changing snapshot:
  - `known_primary_economy` and `known_secondary_economies` remain as last-known info.
  - Live price/market UIs can still use live world state independently.
- Future intel mechanics can update snapshots explicitly:
  - e.g., `apply_economic_report(...)` that writes reported values into knowledge snapshots with a `last_seen_source` of `"intel_report"`.

#### 7.4 Situations visibility

- System-level situations:
  - Visible only while `player_state.current_system_id == system_id`.
  - Not persisted in `SystemKnowledgeSnapshot`.
  - May optionally surface in `SystemView` as `live_situations` for current system only.
- Destination-level situations:
  - Visible only while `player_state.current_destination_id == destination_id`.
  - Not persisted in `DestinationKnowledgeSnapshot`.
  - Surface in `DestinationView.live_situations` only for the current destination.
- This strictly enforces:
  - “Situations are visible ONLY while currently at that system/destination.”

#### 7.5 Interactions with existing tests and flags

- Existing tests:
  - Use `visited_system_ids` / `visited_destination_ids` directly (or via `_visited_*` helpers).
  - Expect binary visited/not-visited behavior and specific destination context contracts.
- Migration risks:
  - Changing semantics of “visited” could break these tests.
- Mitigation:
  - Initially, implement knowledge state **on top** of existing visited flags.
  - Only later invert dependency once behavior is matched and tests are adjusted to use the new abstractions.

#### 7.6 Future scan/intel mechanics

- `DETECTED` and `SCANNED_LOCAL` are intentionally flexible:
  - `DETECTED`:
    - Set by long-range sensors, static maps, or mission intel.
    - Reveals presence, approximate location, and possibly a placeholder name.
  - `SCANNED_LOCAL`:
    - Set by local sensors or special scanner modules when in jump range.
    - Reveals government and potentially additional tags in the future.
- Centralizing all these transitions in `knowledge_state.py` ensures that:
  - CLI, UI, and narrative systems use the same fog-of-war rules.
  - Adding new intel mechanics only requires updating the handler, not sprinkling conditionals across frontends.

