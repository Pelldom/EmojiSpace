## Phase 7.11 – Mission Lifecycle Audit (Read‑Only)

Status: Audit only (no code changes performed)  
Scope date: v0.11.3 (Phase 7.10 complete)

---

## 1. Inventory of Mission Lifecycle Implementation

This section catalogs all mission‑related code, grouped by lifecycle responsibility.

### 1.1 `mission_entity.py` – Mission data model

- **Filename**: `src/mission_entity.py`
- **Key types**:
  - `MissionPersistenceScope` (`EPHEMERAL`, `PERSISTENT`, `SYSTEMIC`)
  - `MissionState` (`OFFERED`, `ACCEPTED`, `ACTIVE`, `RESOLVED`)  
  - `MissionOutcome` (`COMPLETED`, `FAILED`, `ABANDONED`)
  - `MissionEntity` dataclass with:
    - **Identity**: `mission_id`, `mission_type`, `mission_tier`, `persistence_scope`, `mission_state`, `outcome`, `failure_reason`
    - **References**: `mission_giver_npc_id`, `target_npc_id`, `origin_location_id`, `destination_location_id`, `system_scope`, `target_ship_id`, `player_ship_id`, `related_sku_ids`, `related_event_ids`, `mission_contact_seed`
    - **Objective/progress**: `objectives`, `progress`
    - **Rewards (data only)**: `rewards: List[Dict[str, Any]]`
    - **Player association**: `assigned_player_id`
- **Lifecycle ownership**:
  - **Offer / Accept / Activate / Resolve**: *not* owned here (no methods that change `mission_state` or `outcome`).
  - **State transitions**: purely storage; enums exist, but transitions happen elsewhere.
  - **Persistence**: `from_dict` / `to_dict` handle enum normalization and serialization.
- **State transitions** (indirect):
  - Allows any assignment to `mission_state` / `outcome`; contract enforcement occurs in `MissionManager`.
- **Contract notes**:
  - MissionEntity includes `rewards` field but does not itself grant rewards or mutate `PlayerState`.

---

### 1.2 `mission_factory.py` – Mission creation

- **Filename**: `src/mission_factory.py`
- **Key functions**:
  - `create_mission(...) -> MissionEntity`
    - Validates inputs via `_validate_inputs` (`source_type`, `source_id`, `system_id`, `mission_type`, `mission_tier`).
    - Computes deterministic `mission_id` via `_deterministic_mission_id(...)` (seeded by `source_type|source_id|system_id|destination_id|mission_type|mission_tier`).
    - Constructs `MissionEntity` with:
      - `mission_state=MissionState.OFFERED`
      - `persistence_scope=MissionPersistenceScope(persistence_scope)`
      - `system_id`, `origin_location_id=destination_id`
      - `objectives` and `rewards` from parameters.
  - `_deterministic_mission_id(...)` – deterministic ID generator (MD5 of seed).
  - `_log_creation(...)` – logs `"mission_create"` event.
- **Lifecycle ownership**:
  - **Offer**: Creates missions in the **OFFERED** state but does *not* attach to any location or player.
  - **List / Accept / Activate / Resolve**: not owned here.
- **State transitions**:
  - None beyond initial state (`OFFERED` at creation).

---

### 1.3 `mission_manager.py` – Mission registry and state transitions

- **Filename**: `src/mission_manager.py`
- **Key types / fields**:
  - `MissionManager` with:
    - `missions: Dict[str, MissionEntity]` – authoritative mission registry.
    - `offered: List[str]` – mission_ids currently offered (global list, not location‑scoped).
- **Key methods** and lifecycle roles:
  - `offer(mission: MissionEntity, logger=None, turn=0) -> None`
    - Adds/updates `missions[mission_id]`.
    - Appends `mission_id` to `self.offered` (if not present).
    - **Lifecycle**: registers a mission as *offerable*; does not set `mission_state` (relies on entity being `OFFERED` already).
  - `accept(mission_id, player, logger=None, turn=0, location_type=None, ship=None) -> (bool, str | None)`
    - Fetches `mission` from `self.missions`.
    - Enforces **global active mission caps** by tier:
      - `GLOBAL_CAP = 5` active missions (galaxy‑wide).
      - `TIER_CAPS = {1: 5, 2: 4, 3: 3, 4: 2, 5: 1}`.
      - Counts *all* missions with `mission_state == MissionState.ACTIVE` across the manager; not filtered by player.
    - On acceptance:
      - Sets `mission.mission_state = MissionState.ACTIVE`.
      - Removes `mission_id` from `self.offered` if present.
      - Appends `mission_id` to `player.active_missions` (per‑player slot tracking).
    - Returns `False` + error reason if caps exceeded.
    - **Lifecycle**: **Offer → Active** (skips explicit `ACCEPTED` state).
  - `complete(mission_id, player, logger=None, turn=0) -> None`
    - Fetches mission; if exists:
      - Sets `mission.mission_state = MissionState.RESOLVED`.
      - Sets `mission.outcome = MissionOutcome.COMPLETED`.
      - Removes `mission_id` from `player.active_missions`.
      - Appends `mission_id` to `player.completed_missions` if not present.
      - Calls `apply_mission_rewards(...)` with `mission.rewards`.
    - **Lifecycle**: `ACTIVE → RESOLVED` (completed); **applies mission rewards** (see contract mismatch).
  - `fail(mission_id, player, reason=None, logger=None, turn=0)`
    - Sets `mission_state = RESOLVED`, `outcome = FAILED`, `failure_reason = reason`.
    - Moves `mission_id` from `active_missions` to `failed_missions`.
    - **Lifecycle**: `ACTIVE → RESOLVED/FAILED` (no rewards applied).
  - `abandon(mission_id, player, reason=None, logger=None, turn=0)`
    - Same as `fail`, but `outcome = ABANDONED` and appended to `failed_missions`.
    - **Lifecycle**: `ACTIVE → RESOLVED/ABANDONED`.
  - `_effective_mission_slots(player, location_type, ship)`
    - Computes mission slot capacity: base `player.mission_slots` plus crew bonus for `{"bar","administration"}` locations (via `compute_crew_modifiers(ship).mission_slot_bonus`).
- **Lifecycle ownership summary**:
  - **Offer**: stores and tracks offered missions (global `offered` list).
  - **Accept/Activate**: transitions `OFFERED → ACTIVE` with manager‑level global/tier caps plus player active list mutation.
  - **Resolve**: handles RESOLVED/COMPLETED/FAILED/ABANDONED transitions and moves IDs between player lists.
  - **Reward**: `complete()` invokes `apply_mission_rewards`, violating the “missions do not grant rewards” contract.

---

### 1.4 `mission_core.py` – Unified mission API

- **Filename**: `src/mission_core.py`
- **Role**: Thin orchestration layer between `GameEngine` / CLI and `MissionManager`.
- **Key methods**:
  - `list_offered(location_id, location_type=None, ensure_offers_callback=None) -> list[dict]`
    - Uses `ensure_offers_callback(location_id=location_id)` to obtain mission_ids (in production, this callback is `GameEngine._ensure_location_mission_offers`).
    - Filters to missions with `mission_state == MissionState.OFFERED`.
    - Returns rows: `{"mission_id","mission_type","mission_tier","mission_state","rewards", optionally giver_npc_id/display_name}`.
    - **Lifecycle**: *Offer listing* only.
  - `get_details(mission_id)`
    - Branches on `mission.mission_state`:
      - `OFFERED`: returns details + `rewards` and `offer_only=True`.
      - `ACTIVE`: returns status `"active"` and text hint to complete objective.
      - `RESOLVED`: returns generic “already resolved” message.
      - Other: treated as active.
    - **Lifecycle**: read‑only inspection; no transitions.
  - `accept(mission_id, player, location_id, location_type, ship, logger, turn, create_contact_npc_callback)`
    - Delegates to `MissionManager.accept(...)`.
    - If accepted and `location_type == "bar"`, calls `create_contact_npc_callback` to create a deterministic mission contact NPC (`mission_contact_seed` is used elsewhere).
    - **Lifecycle**: orchestrates acceptance, but transition itself is in `MissionManager`.

---

### 1.5 `mission_generator.py` – Mission type selection by world state

- **Filename**: `src/mission_generator.py`
- **Key functions**:
  - `select_weighted_mission_type(eligible_missions, rng, world_state_engine=None, system_id=None)`
    - Computes base weights and adjusts them via world state modifiers (domain `"missions"`).
    - Returns `(mission_type_id, adjusted_weights)`.
- **Lifecycle role**:
  - Influences **which mission type** is created/selected, not mission state transitions.

---

### 1.6 `reward_applicator.py` – Mission reward application

- **Filename**: `src/reward_applicator.py`
- **Key functions**:
  - `apply_mission_rewards(mission_id, rewards, player, logger=None, turn=0)`
    - For each reward dict: `{ "field": <player_attr>, "delta": int }`:
      - If `player` has the attribute and it is `int`, increments by `delta`.
      - Logs via `_log_reward(...)` → `logger.log(action="reward_applied", state_change="mission_id=<id> field=value")`.
    - **Lifecycle role**: reward application for *completed missions* only, called from `MissionManager.complete`.
  - `apply_materialized_reward(...)` – used for loot, not mission rewards (separate path).
- **Contract implication**:
  - Rewards are applied **outside** `MissionEntity`, but are invoked by `MissionManager.complete(...)`, effectively making the “mission lifecycle” code responsible for rewards.

---

### 1.7 `end_game_evaluator.py` – Victory mission evaluation

- **Filename**: `src/end_game_evaluator.py`
- **Key functions**:
  - `evaluate_end_game(player, missions) -> EndGameResult`
    - Checks failure reasons (`_failure_reasons`) for arrest, death, bankruptcy.
    - Scans missions for Tier 5 victory missions:
      - If `mission.mission_tier == 5` and mission contains a recognized `victory_id` (from `persistent_state` or `mission_type` prefix `victory:`).
      - If `mission_state == ACTIVE` → added to `active_victories`.
      - If `mission_state == RESOLVED` and `outcome == COMPLETED` → declares a win for that victory_id.
    - Otherwise returns `"ongoing"` with a list of `eligible_victories` based on progression tracks.
  - `victory_offers_for_source(source_type)` – maps sources to victory IDs.
- **Lifecycle role**:
  - Post‑mission evaluation of **victory state**; does not change mission states or rewards.

---

### 1.8 `game_engine.py` – Mission orchestration and offers

- **Filename**: `src/game_engine.py`
- **Key mission‑related responsibilities**:
  - Holds a `MissionManager` and `MissionCore` instances:
    - `self._mission_manager = MissionManager()`
    - `self._mission_core = MissionCore(self._mission_manager)`
  - Initializes `player_state.mission_offers_by_location: dict[str, list[str]]` as **authoritative offer storage**.
  - **Offer lifecycle**:
    - `_ensure_location_mission_offers(location_id)`:
      - Uses `mission_offers_by_location[location_id]` if present.
      - Otherwise generates a set of mission_ids via `create_mission` and `MissionManager.offer(...)` and stores them in `mission_offers_by_location[location_id]`.
    - `_mission_rows_for_location(location_id, location_type)`:
      - Uses `MissionCore.list_offered(...)` with `ensure_offers_callback=_ensure_location_mission_offers`.
  - **Listing offers via commands**:
    - `command_type == "destination_action"` / `"enter_location"` lead to listing missions via `_mission_rows_for_location` and embedding them in location/destination profiles.
  - **Accepting missions**:
    - `command_type == "mission_accept"`:
      - Validates `mission_id` against `player_state.mission_offers_by_location[location_id]` (no re‑generation).
      - Calls `MissionCore.accept(...)` → `MissionManager.accept(...)` (which applies caps and sets `MissionState.ACTIVE`).
      - On success, removes `mission_id` from `mission_offers_by_location[location_id]`.
      - Logs event via `_event(..., stage="mission", subsystem="mission_core", detail={"action_id": "mission_accept", "mission_id": ..., "accepted": True})`.
  - **Active missions surfacing**:
    - Destination profile building uses `player_state.active_missions` + `_mission_manager.missions` to produce mission rows for UI.
  - **Lifecycle ownership summary**:
    - Owns **where** missions are offered (per location).
    - Delegates **state transitions** to `MissionManager` and `MissionCore`.
    - Does not apply mission rewards directly (that’s `MissionManager.complete`).

---

### 1.9 `player_state.py` – Mission slot and lists

- **Filename**: `src/player_state.py`
- **Mission‑relevant fields**:
  - `mission_slots: int = 1`
  - `active_missions: List[str]`
  - `completed_missions: List[str]`
  - `failed_missions: List[str]`
- **Lifecycle role**:
  - Tracks **capacity** (slots) and classification of missions by terminal outcome.
  - Slot enforcement itself is delegated to `_effective_mission_slots` in `MissionManager`.

---

### 1.10 `integration_test.py` – Mission tests

- **Filename**: `src/integration_test.py`
- **Relevant tests**:
  - `test_mission_serialization`: round‑trip `MissionEntity` serialization.
  - `test_mission_factory_determinism`: checks deterministic mission IDs.
  - `test_mission_manager_flow`: creates a mission, offers, accepts, completes it, and checks:
    - Mission states and lists move appropriately.
    - Credits increase via `apply_mission_rewards` path.
  - `end_game_goal_tests`: uses mission entities to validate victory evaluation logic.
- **Lifecycle role**:
  - Confirms **basic flow**: create → offer → accept/activate → complete + reward → mark as completed.

---

## 2. Lifecycle Diagrams

### 2.1 Current Implemented Lifecycle (as of v0.11.3)

**States** (MissionState): `OFFERED → ACTIVE → RESOLVED`  
(`ACCEPTED` exists in the enum but is not used as an intermediate state)

**Terminal outcomes** (MissionOutcome): `COMPLETED`, `FAILED`, `ABANDONED`

**High‑level flow**:

1. **Creation**
   - `MissionFactory.create_mission(...)` → `MissionEntity` with `mission_state=OFFERED`.
2. **Offering to player**
   - `GameEngine._ensure_location_mission_offers(location_id)`:
     - Builds one or more missions via `create_mission` and `MissionManager.offer`.
     - Stores mission_ids in `player_state.mission_offers_by_location[location_id]`.
3. **Listing offers**
   - `MissionCore.list_offered(location_id, location_type, ensure_offers_callback=...)`:
     - Returns mission rows only for missions with `mission_state == OFFERED`.
4. **Acceptance / Activation**
   - `GameEngine.execute({"type": "mission_accept", ...})`:
     - Verifies `mission_id` is in `mission_offers_by_location[location_id]`.
     - Calls `MissionCore.accept` → `MissionManager.accept`.
   - `MissionManager.accept`:
     - Enforces global caps (`GLOBAL_CAP`, `TIER_CAPS`) **based on manager‑wide ACTIVE missions**.
     - On success:
       - `mission_state` set to `ACTIVE`.
       - `mission_id` removed from `self.offered` and from `player_state.mission_offers_by_location[location_id]`.
       - `mission_id` appended to `player.active_missions`.
5. **Mission active phase**
   - Objective evaluation and progress updates are **not centrally implemented yet**; progression is out‑of‑scope for this audit, but no generic “mission tick” is present.
6. **Resolution**
   - `MissionManager.complete`:
     - `mission_state = RESOLVED`, `outcome = COMPLETED`.
     - `mission_id` removed from `player.active_missions`, added to `player.completed_missions`.
     - Applies rewards via `apply_mission_rewards` (mutates `PlayerState` fields).
   - `MissionManager.fail`:
     - `mission_state = RESOLVED`, `outcome = FAILED`, records `failure_reason`.
     - Moves mission to `player.failed_missions`.
   - `MissionManager.abandon`:
     - Same as `fail` but sets `outcome = ABANDONED` (`failed_missions` used for both failure and abandonment).
7. **Victory evaluation**
   - `evaluate_end_game(player, missions)` inspects Tier‑5 missions to determine win/lose/ongoing.

**Diagram (implemented)**:

```text
CREATE (factory)
  → MissionEntity(mission_state=OFFERED)

OFFER (manager.offer + engine._ensure_location_mission_offers)
  → listed in mission_offers_by_location[location_id]

ACCEPT (mission_core.accept + mission_manager.accept)
  → mission_state: OFFERED → ACTIVE
  → player.active_missions += mission_id
  → mission removed from offers

RESOLVE:
  - complete()  : ACTIVE → RESOLVED (outcome=COMPLETED, rewards APPLIED)
  - fail()      : ACTIVE → RESOLVED (outcome=FAILED)
  - abandon()   : ACTIVE → RESOLVED (outcome=ABANDONED)

VICTORY EVAL:
  - end_game_evaluator inspects Tier 5 missions for victory_id and outcome
```

---

### 2.2 Contract Lifecycle (from `design/mission_skeleton_contract.md`)

**States** (MissionState):

```text
offered → accepted → active → resolved
```

**Terminal outcomes**:

- `completed`
- `failed`
- `abandoned`

**Slot enforcement rules**:

- Missions **consume Player Entity mission slots while ACTIVE**.
- Mission acceptance requires available mission slots.
- Mission slot enforcement is handled by the **Player Entity** (i.e., mission layer tracks slot usage; mission manager should not implement its own independent global cap that conflicts with `mission_slots`).

**References** (required / advisory):

- `mission_giver_npc_id` – must reference Tier 2 or Tier 3 NPC.
- `origin_location_id` vs `destination_location_id`:
  - `origin_location_id`: where contract is given.
  - `destination_location_id`: where objective is fulfilled.

**Non‑responsibilities**:

- Missions (and their lifecycle code) **do NOT**:
  - grant credits
  - grant items
  - resolve combat
  - apply enforcement or consequences
  - manage Player progression

**Diagram (contract)**:

```text
CREATE (factory)
  → MissionEntity(mission_state=offered)

OFFERED → ACCEPTED  (player explicitly accepts; slots checked)
ACCEPTED → ACTIVE   (mission starts; consumes slot)
ACTIVE   → RESOLVED (completed / failed / abandoned)

Slots:
  - enforced by Player Entity (mission_slots)
  - all terminal outcomes release slots

Rewards:
  - declared by mission, applied by external systems
  - mission lifecycle must not directly grant rewards
```

---

## 3. Mismatch List (Code vs Contract)

Numbered mismatches with representative file/line regions (line numbers approximate).

1. **No distinct `ACCEPTED` state used in lifecycle**
   - **Code**: `MissionManager.accept` sets `mission.mission_state = MissionState.ACTIVE` immediately on acceptance.
     - `src/mission_manager.py` (around lines 97–103)
   - **Contract**: Lifecycle should include `offered → accepted → active → resolved`.
   - **Impact**: Cannot distinguish “accepted but not yet started” from “actively in progress” missions; may be acceptable for current scope but diverges from contract.

2. **Global mission caps enforce manager‑wide ACTIVE counts, not per‑player `mission_slots`**
   - **Code**:
     - `MissionManager.accept` uses `GLOBAL_CAP` and `TIER_CAPS` over all `MissionEntity` with `mission_state == ACTIVE` in `self.missions` (galaxy‑wide).
       - `src/mission_manager.py` lines ~49–95.
     - `player.mission_slots` is only used by `_effective_mission_slots` to conditionally gate acceptance at specific **location types** via crew bonuses, not as the *sole* authority for number of concurrent missions.
   - **Contract**:
     - Player Entity `mission_slots` is the authoritative slot model; missions “consume Player Entity mission slots while ACTIVE”; mission acceptance “requires available mission slots” (per player).
   - **Impact**:
     - Possible discrepancy between global caps and per‑player slot expectations, especially in multi‑player or NPC mission scenarios (future phases), and inconsistent with contract’s slot authority statement.

3. **Mission lifecycle layer directly applies rewards**
   - **Code**:
     - `MissionManager.complete` calls `apply_mission_rewards(...)`:
       - `src/mission_manager.py` lines ~106–123.
     - `apply_mission_rewards` mutates `PlayerState` fields and logs `"reward_applied"` events:
       - `src/reward_applicator.py` lines ~140–168.
   - **Contract**:
     - Section 9 and 12: “Missions declare outcomes; other systems apply effects. Missions do not grant rewards directly.” and “Missions do NOT grant credits / items / experience.”
   - **Impact**:
     - Reward application is currently tightly coupled to mission lifecycle completion, blurring the boundary between “mission tracks state” and “systems apply effects”.

4. **MissionState / MissionOutcome type use mixed between enums and bare strings**
   - **Code**:
     - `MissionEntity.to_dict` converts enums to `.value` strings; `from_dict` attempts to normalize back to enums, with fallbacks to default enum values.
     - Some code compares `mission.mission_state` to `MissionState.<VALUE>` (enum), while others rely on string forms in logs.
   - **Contract**:
     - States and outcomes are conceptually enums, but no strict requirement; current behavior is functionally aligned but slightly looser than ideal.
   - **Impact**:
     - Minor; not a functional mismatch, but can lead to inconsistent state if external deserializers do not pass through `from_dict`.

5. **`mission_giver_npc_id` Tier 2/3 requirement is advisory but not enforced**
   - **Code**:
     - `mission_giver_npc_id` field exists on `MissionEntity`, but:
       - Creation (`create_mission`) does not set it.
       - Bar missions derive `giver_npc_id` on the fly from `mission_contact_seed` rather than using `mission_giver_npc_id` consistently.
       - Deterministic contact NPCs are resolved in `GameEngine` (around NPC placement and `_create_mission_contact_npc`), not strictly validated against Tier 2/3 NPCs in `MissionEntity` or `MissionManager`.
   - **Contract**:
     - `mission_giver_npc_id` should reference Tier 2 or Tier 3 NPC; mission skeleton treats this as a structural guarantee.
   - **Impact**:
     - Structural compliance is mostly advisory today; the system may generate valid NPCs but does not enforce Tier 2/3 at the mission entity level.

6. **`origin_location_id` vs `destination_location_id` usage is partial**
   - **Code**:
     - `create_mission` sets `origin_location_id=destination_id` (by name), which is slightly confusing: the destination parameter is used as the origin field.
     - `destination_location_id` is present but not widely used in mission logic yet.
   - **Contract**:
     - Distinguishes origin (where contract is given) from destination (where objective is fulfilled).
   - **Impact**:
     - Semantics are under‑specified in code; current usage may be sufficient for prototype delivery missions but does not strictly follow the contract’s naming and separation intent.

7. **Abandonment and failure both map to `failed_missions`**
   - **Code**:
     - `MissionManager.fail` and `MissionManager.abandon` both append `mission_id` to `player.failed_missions`.
   - **Contract**:
     - Treats abandonment as voluntary failure but still conceptually distinguishes it from system failure.
   - **Impact**:
     - Minor; semantics are consistent with “voluntary failure,” but differentiation between failed vs abandoned is only in `mission.outcome` / `failure_reason`, not in player lists.

---

## 4. Proposed Fix Plan

This is **design only**, no code changes have been made for this section.

### 4.1 Contract updates (if we choose to align with current implementation)

1. **Relax explicit requirement for `accepted` intermediate state**
   - Clarify that `ACCEPTED` and `ACTIVE` may be merged for early phases, with a note that future UIs/narrative systems might reintroduce a distinct `ACCEPTED` state if needed.

2. **Clarify slot enforcement authority**
   - Update `mission_skeleton_contract.md` to acknowledge that:
     - Mission slots are surfaced on `PlayerState` but mission caps may be enforced via a `MissionManager` (global or per‑player) as long as the behavior is deterministic and documented.

3. **Document reward coupling in Phase 5+**
   - Explicitly state that, in current implementation, mission completion triggers reward application through `MissionManager.complete + apply_mission_rewards`, and that a future refactor may separate these concerns once a generic reward routing system is fully in place.

4. **Clarify `origin_location_id` semantics**
   - Update contract wording to allow current usage (creation‑time overloading) as valid for Phase 3/5 while flagging it as a candidate for future refinement.

### 4.2 Code updates (if we choose to align code with original contract)

1. **Introduce explicit `ACCEPTED` state transition**
   - In `MissionManager.accept`:
     - `OFFERED → ACCEPTED` on acceptance, with slot check only.
     - `ACCEPTED → ACTIVE` when first objective‑relevant action occurs (e.g., departure from origin, first travel step, or explicit “begin mission” command).
   - This would likely require a small engine hook to promote missions from ACCEPTED to ACTIVE.

2. **Align slot enforcement to `player.mission_slots`**
   - Replace global/tier caps with a slot model driven by:
     - `player.mission_slots` (+ crew bonuses) as the hard upper bound on `len(player.active_missions)`.
     - Optional: keep `GLOBAL_CAP`/`TIER_CAPS` as a soft guard but document them as a higher‑level pacing rule, not as the primary slot model.

3. **Decouple reward application from `MissionManager.complete`**
   - Move `apply_mission_rewards` calls into a dedicated reward handling layer (e.g., `GameEngine` or a mission reward router) that:
     - Receives a sealed “mission resolution” event (`mission_id`, `outcome`, `rewards`) and decides when/how to apply them.
   - `MissionManager` would then only mark state and log, not mutate `PlayerState` directly.

4. **Enforce `mission_giver_npc_id` Tier 2/3 constraint**
   - At mission creation / offer time:
     - When binding a mission to an NPC, validate that `mission_giver_npc_id` refers to a Tier 2 or Tier 3 NPC in `NPCRegistry` (or equivalent) and raise if not.
   - Optionally, update `MissionEntity` construction to store `mission_giver_npc_id` explicitly once NPC contact is created.

5. **Clarify and fix `origin_location_id` / `destination_location_id` usage**
   - Adjust `create_mission` to set:
     - `origin_location_id` to the source location (where mission is offered).
     - Optionally, `destination_location_id` to the objective location (if known).
   - Update any dependent code (especially delivery missions) to use the correct field for progression checks.

6. **Optionally differentiate `abandon` vs `fail` in player lists**
   - Introduce a separate `abandoned_missions` list or a tagged entry in `failed_missions` to distinguish them more clearly at the profile layer.

---

## 5. Minimal Deterministic CLI Test Plan

These are **manual or scripted CLI tests** to validate mission lifecycle behavior and logs without requiring new code paths.

### 5.1 Basic mission lifecycle (single mission)

1. Start a new game with a fixed seed (e.g., `12345`).
2. Travel to a destination with a `bar` or `administration` location.
3. Enter the location and list missions:
   - Verify `mission_offers_by_location[location_id]` is populated.
   - Logs: `action=mission_list_instance_check`, `stage=mission` events for list output.
4. Accept a mission:
   - Command: `mission_accept` via CLI.
   - Verify:
     - `mission_state` for that mission is now `ACTIVE`.
     - Mission appears in `player.active_missions`.
     - `mission_id` removed from `mission_offers_by_location[location_id]`.
   - Logs: `action=mission_accept_instance_check`, `stage=mission subsystem=mission_core action_id=mission_accept`.
5. Force mission completion via a stub or scripted harness (since objective logic may not be fully wired yet):
   - Call `MissionManager.complete(mission_id, player, logger)` from a test harness.
   - Verify:
     - `mission_state == RESOLVED`, `outcome == COMPLETED`.
     - `mission_id` moved from `active_missions` to `completed_missions`.
     - Player fields adjusted per `apply_mission_rewards` (if rewards list is non‑empty).
   - Logs: `action=mission_manager state_change="complete mission_id=..."`, `action=reward_applied` lines for each reward.

### 5.2 Mission caps and slot behavior

1. In a deterministic integration test:
   - Set `player.mission_slots = 1` or 2.
   - Create >5 missions of various tiers.
   - Offer them through `MissionManager.offer` and location wiring.
2. Attempt to accept more than:
   - `GLOBAL_CAP` (5) missions total.
   - Tier‑specific caps per `TIER_CAPS`.
3. Verify:
   - Acceptance fails with correct error reason (`mission_accept_failed_total_cap` / `mission_accept_failed_tier_cap`).
   - Logs show `accept_failed_total_cap` or `accept_failed_tier_cap` in `mission_manager` events.
   - `player.active_missions` never exceeds intended cap in practice.

### 5.3 Victory mission lifecycle

1. In a deterministic harness, construct a Tier‑5 mission with:
   - `mission_type="victory:charter_of_authority"` or `persistent_state["victory_id"]="charter_of_authority"`.
   - `mission_state=RESOLVED`, `outcome=COMPLETED`.
2. Call `evaluate_end_game(player, [mission])`:
   - Expect `EndGameResult.status == "win"` and `victory == "charter_of_authority"`.
   - Confirm no unexpected rewards are applied during evaluation (pure read‑only check).

### 5.4 NPC mission giver integration (bar missions)

1. At a `bar` location with mission offers:
   - Use `mission_list` to fetch rows including `giver_npc_id` and `giver_display_name` fields.
2. Accept a mission and then call `get_player_profile` / `get_destination_profile`:
   - Confirm that NPC contact exists for that mission (via mission_contact_seed‑derived NPC).
3. Logs:
   - `action=mission_create` for mission creation.
   - `action=mission_manager` accept events.
   - NPC placement / registry logs showing deterministic NPC IDs.

---

## 6. Summary

- The **mission lifecycle implementation** is structurally close to the contract:
  - Mission entities are pure state holders with objectives, progress, and rewards as declarative data.
  - A central `MissionManager` and `MissionCore` provide a unified lifecycle and listing/acceptance API.
  - `GameEngine` handles location‑scoped mission offers and mission acceptance orchestration.
- The primary **contract mismatches** are:
  - The absence of a distinct `ACCEPTED` state in practice.
  - Slot enforcement being implemented as global/tier caps at the manager level instead of purely via `PlayerState.mission_slots`.
  - Direct reward application from the lifecycle (`MissionManager.complete` → `apply_mission_rewards`), rather than via a dedicated reward routing subsystem.
  - Soft enforcement of `mission_giver_npc_id` semantics and partial usage of `origin_location_id` vs `destination_location_id`.
- These gaps are well‑scoped and can be addressed in a focused Phase 7.11–7.12 effort without large structural refactors, primarily via:
  - Narrowed code changes in `mission_manager.py` and `game_engine.py`.
  - A small contract addendum clarifying transitional behavior while preserving the core design principle that **missions track state; other systems apply effects**.

