# Phase 7.11 Mission Lifecycle Resolution - Focused Audit Answers

**Date:** 2024  
**Purpose:** Read-only audit to confirm what is implemented and identify what is missing for mission lifecycle resolution phase.

---

## 1. Mission Sources Currently Implemented

### 1.1 Are Bar missions implemented end-to-end (offer -> list -> accept -> appear in active missions)?

**Answer:** YES

**Evidence:**
- Mission generation: `src/game_engine.py:1214-1278` (`_ensure_location_mission_offers`)
- Mission listing: `src/game_engine.py:1303-1339` (`_execute_mission_list`)
- Mission acceptance: `src/game_engine.py:1366-1408` (`_execute_mission_accept`)
- Bar location actions: `src/game_engine.py:5049-5050` (includes `mission_list`, `mission_accept`)
- CLI integration: `src/run_game_engine_cli.py:1909-1926` (accept flow)
- Active missions tracking: `src/mission_manager.py:98-104` (sets `mission_state = ACTIVE`, adds to `player.active_missions`)

**Notes:**
- Bar missions use same generation logic as other location types via `_ensure_location_mission_offers`
- Mission offers are persisted in `player_state.mission_offers_by_location[location_id]`
- Mission contact NPCs are created on acceptance for Bar locations (`_create_mission_contact_npc`)

---

### 1.2 Are Administration / Mission Board missions implemented end-to-end?

**Answer:** YES

**Evidence:**
- Mission board action: `src/game_engine.py:1571-1573` (`_execute_admin_mission_board` delegates to `_execute_mission_list`)
- Administration location actions: `src/game_engine.py:5051-5059` (includes `admin_mission_board`, `mission_accept`)
- Mission generation: Uses same `_ensure_location_mission_offers` as Bar (`src/game_engine.py:1214-1278`)
- CLI integration: `src/run_game_engine_cli.py:1717-1795` (administration menu with mission board)

**Notes:**
- Administration uses identical mission generation pipeline as Bar
- `admin_mission_board` action routes to same `_execute_mission_list` handler
- Mission acceptance works identically via `mission_accept` command type

---

### 1.3 Are DataNet missions implemented as an offer/list/accept pipeline anywhere in GameEngine/CLI?

**Answer:** NO

**Evidence:**
- DataNet location menu exists: `src/run_game_engine_cli.py:2100-2124` (`_datanet_location_menu`)
- DataNet profile building: `src/run_game_engine_cli.py:2955-2996` (`_build_datanet_profile`, `_print_datanet_profile`)
- DataNet accept stub: `src/run_game_engine_cli.py:3013` (`_accept_mission_from_datanet`)
- No mission generation: `src/game_engine.py:1214-1278` (`_ensure_location_mission_offers`) - no DataNet-specific logic
- No location action: `src/game_engine.py:5118` (datanet location type returns empty action set)
- No mission listing action: `src/game_engine.py:2037-2038` (`_allowed_action_ids_for_location_type("datanet")` returns `set()`)

**Notes:**
- DataNet location exists in world generation (`src/world_generator.py:711-717`)
- DataNet is used for refuel service gating (`src/interaction_resolvers.py:21-32`)
- No mission source generator, no command type, no location action for DataNet missions
- Previous audit confirms: `docs/PHASE_7.7_MISSION_SYSTEM_AUDIT.md:385-433` (DataNet mission generation not implemented)

---

## 2. NPC Mission Provider Persistence Promotion

### 2.1 When accepting a Bar mission, does the engine create or bind a mission-giver NPC entity in NPCRegistry?

**Answer:** YES

**Evidence:**
- NPC creation callback: `src/game_engine.py:1341-1364` (`_create_mission_contact_npc`)
- NPC creation on acceptance: `src/mission_core.py:179-181` (calls `create_contact_npc_callback` if `location_type == "bar"`)
- NPC registration: `src/game_engine.py:1361` (`self._npc_registry.add(npc, logger=logger, turn=turn)`)
- NPC entity creation: `src/game_engine.py:1351-1358` (creates `NPCEntity` with `persistence_tier=TIER_2`)

**Notes:**
- NPC is created deterministically from `mission_contact_seed` hash
- NPC ID format: `NPC-MSN-{hash}` where hash is first 8 chars of MD5(seed)
- NPC is only created if `mission_contact_seed` exists and `mission_giver_npc_id` is not already set

---

### 2.2 If an NPC is created/bound, is its persistence tier upgraded from Tier 1 to Tier 2 on acceptance?

**Answer:** YES (created at Tier 2, not upgraded)

**Evidence:**
- NPC creation with Tier 2: `src/game_engine.py:1353` (`persistence_tier=NPCPersistenceTier.TIER_2`)
- NPC is created new, not upgraded: `src/game_engine.py:1346` (checks `mission_giver_npc_id is not None` to skip if already exists)

**Notes:**
- NPC is created at Tier 2 directly, not upgraded from Tier 1
- No Tier 1 NPC exists before mission acceptance for Bar missions
- NPC creation is deterministic and idempotent (skips if `mission_giver_npc_id` already set)

---

### 2.3 Is mission_giver_npc_id written into MissionEntity on offer or on acceptance?

**Answer:** On acceptance

**Evidence:**
- Mission offer: `src/game_engine.py:1259-1273` (creates mission, sets `mission_contact_seed`, does NOT set `mission_giver_npc_id`)
- NPC creation on acceptance: `src/game_engine.py:1362` (`mission.mission_giver_npc_id = npc_id`)
- Acceptance flow: `src/mission_core.py:179-181` (calls callback after `accept()` succeeds)

**Notes:**
- `mission_contact_seed` is set during offer generation (`src/game_engine.py:1272`)
- `mission_giver_npc_id` is set during acceptance when NPC is created (`src/game_engine.py:1362`)
- Mission entity field exists: `src/mission_entity.py:56` (`mission_giver_npc_id: str | None = None`)

---

### 2.4 Where is _create_mission_contact_npc implemented, and what exactly does it do (tier, placement, persistence, IDs)?

**Answer:** `src/game_engine.py:1341-1364`

**Evidence:**
- Function location: `src/game_engine.py:1341-1364` (`_create_mission_contact_npc`)
- Tier: `src/game_engine.py:1353` (`persistence_tier=NPCPersistenceTier.TIER_2`)
- Placement: `src/game_engine.py:1355-1356` (`current_location_id=location_id`, `current_system_id=system_id`)
- Persistence: Tier 2 (explicitly set, not ephemeral)
- IDs: `src/game_engine.py:1348-1349` (generates `npc_id = f"NPC-MSN-{npc_hash}"` from `mission_contact_seed` hash)
- Role tags: `src/game_engine.py:1357` (`role_tags=["mission_giver"]`)
- Binding: `src/game_engine.py:1362` (`mission.mission_giver_npc_id = npc_id`)

**Notes:**
- Only creates NPC if `mission_contact_seed` exists and `mission_giver_npc_id` is None
- NPC is registered in `NPCRegistry` via `self._npc_registry.add()`
- Logs creation event: `src/game_engine.py:1363-1364`

---

## 3. Mission Lifecycle Resolution Wiring (The Real Phase 7.11 Gap)

### 3.1 Is there any generic "mission tick" / evaluation loop that updates objectives/progress?

**Answer:** NO

**Evidence:**
- No mission tick function found in `src/game_engine.py`
- No mission evaluation loop in `src/turn_loop.py`
- Mission progress field exists but unused: `src/mission_entity.py:69` (`progress: Dict[str, Any] = field(default_factory=dict)`)
- Objectives are placeholder strings: `src/game_engine.py:1267` (`objectives=[f"{mission_type_id}:complete_objective"]`)

**Notes:**
- Mission objectives are stored but never evaluated
- No periodic check for mission completion conditions
- No integration with travel, combat, cargo, or other game systems to update mission progress

---

### 3.2 Is there any code path in GameEngine/CLI that triggers:
   - MissionManager.complete(...)
   - MissionManager.fail(...)
   - MissionManager.abandon(...)
   outside of tests?

**Answer:** PARTIAL (abandon only, complete/fail not called)

**Evidence:**
- `MissionManager.abandon` called: `src/game_engine.py:1018` (`self._mission_manager.abandon(...)`)
- Abandon command exists: `src/game_engine.py:354-355` (`command_type == "abandon_mission"`)
- Abandon CLI: `src/run_game_engine_cli.py:597-633` (`_abandon_mission`)
- `MissionManager.complete` NOT called: No matches in `src/game_engine.py` or `src/run_game_engine_cli.py` (only in `src/integration_test.py:380`)
- `MissionManager.fail` NOT called: No matches in `src/game_engine.py` or `src/run_game_engine_cli.py`

**Notes:**
- Abandon is fully wired: command type, engine handler, CLI menu option
- Complete and fail methods exist (`src/mission_manager.py:106-134`) but are never invoked outside tests
- No automatic completion detection (e.g., on arrival at destination, cargo delivery, combat victory)

---

### 3.3 Is there a player-facing CLI option/command_type to abandon an active mission?

**Answer:** YES

**Evidence:**
- Command type: `src/game_engine.py:354-355` (`command_type == "abandon_mission"`)
- Engine handler: `src/game_engine.py:1009-1034` (`_execute_abandon_mission`)
- CLI menu: `src/run_game_engine_cli.py:581-588` (main menu option "1) Abandon Mission")
- CLI function: `src/run_game_engine_cli.py:597-633` (`_abandon_mission`)

**Notes:**
- Abandon flow is complete: menu -> CLI function -> engine command -> MissionManager.abandon
- Validates mission is active before abandoning
- Logs abandon event: `src/game_engine.py:1026-1034`

---

### 3.4 Are there any mission types with real completion conditions implemented (delivery, bounty, escort, etc.), or are objectives currently placeholders only?

**Answer:** NO (objectives are placeholders only)

**Evidence:**
- Objective format: `src/game_engine.py:1267` (`objectives=[f"{mission_type_id}:complete_objective"]`)
- No objective evaluation: No code checks mission objectives against game state
- Mission types exist: `src/game_engine.py:1251-1256` (selects from `_mission_candidates()`)
- No completion logic: No code path checks if delivery cargo is at destination, if bounty target is defeated, etc.

**Notes:**
- Objectives are string placeholders like `"delivery:complete_objective"`
- No integration with cargo system, combat system, or travel system to evaluate objectives
- Mission progress dict exists (`src/mission_entity.py:69`) but is never populated or checked

---

## 4. Rewards (Defer Implementation Changes, But Confirm Current Behavior)

### 4.1 Are mission rewards currently applied via apply_mission_rewards (field/delta) only?

**Answer:** YES

**Evidence:**
- Reward application: `src/mission_manager.py:115-121` (`apply_mission_rewards(...)`)
- Reward format: `src/game_engine.py:1268` (`rewards=[{"type": "credits", "amount": 100 + (index * 50)}]`)
- Reward applicator: `src/reward_applicator.py:140-158` (`apply_mission_rewards` uses field/delta pattern)
- Field/delta logic: `src/reward_applicator.py:148-157` (reads `reward.get("field")` and `reward.get("delta")`)

**Notes:**
- Rewards are applied only on `MissionManager.complete()` (which is never called in production)
- Reward structure uses `{"field": "credits", "delta": 100}` format
- No materialized reward pipeline used for missions

---

### 4.2 Is reward_materializer/materialized reward pipeline used by missions anywhere today?

**Answer:** NO

**Evidence:**
- Mission rewards use direct field/delta: `src/reward_applicator.py:140-158` (`apply_mission_rewards`)
- Materialized rewards used for encounters: `src/game_engine.py:427, 2950-2956` (encounter rewards use `materialize_reward` + `apply_materialized_reward`)
- No mission reward_profile_id: Missions do not have `reward_profile_id` field
- No materialization in mission flow: `src/mission_manager.py:115-121` (calls `apply_mission_rewards` directly)

**Notes:**
- Materialized reward pipeline exists (`src/reward_materializer.py`, `src/reward_applicator.py:34-50`) but is not used by missions
- Missions use simpler field/delta pattern instead of reward profiles

---

### 4.3 Are there any existing reward kinds for "module as cargo" or "hull frame grants inactive ship at destination"?

**Answer:** NO

**Evidence:**
- Mission reward types: `src/game_engine.py:1268` (only `{"type": "credits", "amount": ...}`)
- Reward applicator supports: `src/reward_applicator.py:148-157` (only field/delta on PlayerState fields)
- No module rewards: No reward type for modules or cargo items
- No ship rewards: No reward type for hull frames or inactive ships

**Notes:**
- Current reward system only supports numeric field deltas (credits, etc.)
- No structured rewards for items, modules, ships, or cargo

---

## 5. "Do Not Regress" Inventory

### Mission Offer Generation Per Location

**Files:**
- `src/game_engine.py:1214-1278` (`_ensure_location_mission_offers`)
  - Generates missions lazily on first access
  - Persists mission_ids in `player_state.mission_offers_by_location[location_id]`
  - Uses deterministic RNG based on location_id (no turn dependency)
  - MUST REMAIN STABLE: This is the source of truth for mission offers

**Flow:**
```
Location access -> _ensure_location_mission_offers(location_id)
  -> Check if offers exist in player_state.mission_offers_by_location
  -> If not, generate missions via create_mission()
  -> Store mission_ids in player_state.mission_offers_by_location
  -> Return mission_ids
```

---

### Mission Listing UI Rows

**Files:**
- `src/game_engine.py:1303-1339` (`_execute_mission_list`)
  - Uses `MissionCore.list_offered()` with `ensure_offers_callback`
  - Returns mission rows with mission_id, mission_type, mission_tier, rewards
  - Adds giver_npc_id for Bar locations
  - MUST REMAIN STABLE: UI depends on this row format

- `src/mission_core.py:24-77` (`MissionCore.list_offered`)
  - Filters to OFFERED state missions only
  - Builds row dicts with mission metadata
  - MUST REMAIN STABLE: Core API contract

**Flow:**
```
mission_list action -> _execute_mission_list()
  -> MissionCore.list_offered(location_id, ensure_offers_callback=_ensure_location_mission_offers)
  -> Returns list of mission row dicts
  -> Emits event with missions array
```

---

### Acceptance Command Flow

**Files:**
- `src/game_engine.py:1366-1408` (`_execute_mission_accept`)
  - Validates mission_id is in persisted offers
  - Calls `MissionCore.accept()` with create_contact_npc_callback
  - Removes accepted mission from `mission_offers_by_location`
  - MUST REMAIN STABLE: Acceptance validation and persistence cleanup

- `src/mission_core.py:136-183` (`MissionCore.accept`)
  - Delegates to `MissionManager.accept()`
  - Calls create_contact_npc_callback for Bar locations
  - MUST REMAIN STABLE: Core API contract

- `src/mission_manager.py:25-104` (`MissionManager.accept`)
  - Validates tier caps and global caps
  - Sets mission_state = ACTIVE
  - Adds to player.active_missions
  - MUST REMAIN STABLE: Cap enforcement and state transitions

**Flow:**
```
mission_accept command -> _execute_mission_accept()
  -> Validate mission_id in player_state.mission_offers_by_location[location_id]
  -> MissionCore.accept(mission_id, create_contact_npc_callback=_create_mission_contact_npc)
    -> MissionManager.accept() [validates caps, sets ACTIVE]
    -> If Bar location: _create_mission_contact_npc() [creates Tier 2 NPC]
  -> Remove mission_id from mission_offers_by_location
  -> Emit event
```

---

### Contact NPC Creation (Bar Locations Only)

**Files:**
- `src/game_engine.py:1341-1364` (`_create_mission_contact_npc`)
  - Creates Tier 2 NPC deterministically from mission_contact_seed
  - Registers NPC in NPCRegistry
  - Binds mission.mission_giver_npc_id
  - MUST REMAIN STABLE: NPC creation determinism and Tier 2 persistence

**Flow:**
```
Mission acceptance (Bar location) -> _create_mission_contact_npc(mission_id, location_id)
  -> Generate npc_id from mission_contact_seed hash
  -> Create NPCEntity (Tier 2, role_tags=["mission_giver"])
  -> Register in NPCRegistry
  -> Set mission.mission_giver_npc_id = npc_id
```

---

### Concise Flow Diagram

```
[Location Access]
    |
    v
[_ensure_location_mission_offers(location_id)]
    | (lazy generation, persisted)
    v
[player_state.mission_offers_by_location[location_id]]
    |
    v
[mission_list action] -> [MissionCore.list_offered()] -> [UI rows]
    |
    v
[mission_accept command] -> [MissionCore.accept()]
    |                          |
    |                          v
    |                    [MissionManager.accept()]
    |                          | (validates caps)
    |                          v
    |                    [mission_state = ACTIVE]
    |                          |
    |                          v
    |                    [player.active_missions.append()]
    |                          |
    |                          v
    |                    [If Bar: _create_mission_contact_npc()]
    |                          | (creates Tier 2 NPC)
    |                          v
    |                    [mission.mission_giver_npc_id = npc_id]
    |
    v
[Remove from mission_offers_by_location]
```

**MUST REMAIN STABLE:**
- `_ensure_location_mission_offers` persistence logic
- `MissionCore.list_offered` row format
- `MissionManager.accept` cap validation
- `_create_mission_contact_npc` determinism
- `player_state.mission_offers_by_location` storage

---

## Phase 7.11 Resolution Work Needed

### Critical Gaps (Must Implement)

1. **Mission Objective Evaluation System**
   - Implement objective evaluation logic for mission types (delivery, bounty, escort, etc.)
   - Integrate with cargo system (check cargo at destination)
   - Integrate with combat system (check target defeat)
   - Integrate with travel system (check arrival at destination)
   - Update `mission.progress` dict based on objective state

2. **Mission Completion Detection**
   - Add mission evaluation hook in game loop (after travel, combat, cargo operations)
   - Call `MissionManager.complete()` when objectives are satisfied
   - Wire completion to appropriate game events (arrival, combat victory, cargo delivery)

3. **Mission Failure Detection**
   - Implement failure conditions (timeout, target destroyed, cargo lost, etc.)
   - Call `MissionManager.fail()` when failure conditions are met
   - Wire failure to appropriate game events

4. **Mission Progress Tracking**
   - Populate `mission.progress` dict during gameplay
   - Track objective completion state
   - Display progress in mission details/UI

### Secondary Gaps (Can Defer)

5. **DataNet Mission Pipeline**
   - Implement DataNet mission generation (Tier 3-5)
   - Add DataNet location action for mission listing
   - Add DataNet mission accept flow

6. **Reward System Enhancement**
   - Add reward types for modules, cargo items, ships
   - Consider materialized reward pipeline for missions (optional)

7. **Mission Type-Specific Logic**
   - Implement delivery mission cargo tracking
   - Implement bounty mission target tracking
   - Implement escort mission NPC tracking
   - Add other mission type handlers as needed

### Notes

- Abandon flow is complete and working
- Offer/list/accept pipeline is stable for Bar and Administration
- NPC contact creation is deterministic and working
- Mission rewards are structured but only applied on completion (which never happens)
- No mission tick/evaluation loop exists - this is the core Phase 7.11 gap
