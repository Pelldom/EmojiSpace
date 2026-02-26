# Phase 7.10 Combat System Audit

**Date:** 2024  
**Scope:** Complete architectural audit of combat-related systems and integrations  
**Objective:** Determine combat unification status, identify duplicate logic, hidden mutations, RNG determinism, and integration compliance

---

## 1. Combat Entry Points

### Primary Entry Points

#### 1.1 `src/interaction_layer.py` - `dispatch_player_action()`
- **Function:** `dispatch_player_action()`
- **Lines:** 155-233
- **Who calls it:**
  - `src/game_engine.py` - `_resolve_encounter()` (line ~2170)
  - `src/simulation_controller.py` - `_resolve_encounter()` (line 254)
- **Conditions:**
  - Player action is `ACTION_ATTACK` → routes to `HANDLER_COMBAT_STUB` (line 193)
  - NPC outcome is `NPC_OUTCOME_ATTACK` → routes to `HANDLER_COMBAT_STUB` (line 143)
  - NPC outcome is `NPC_OUTCOME_ACCEPT_AND_ATTACK` → routes to `HANDLER_COMBAT_STUB` (line 151)

#### 1.2 `src/game_engine.py` - `_resolve_encounter_combat()`
- **Function:** `_resolve_encounter_combat()`
- **Lines:** 2267-2302
- **Who calls it:**
  - `src/game_engine.py` - `_resolve_encounter()` (line 2218)
- **Conditions:**
  - Handler is `HANDLER_COMBAT_STUB` (line 2217)
- **Action:** Calls `resolve_combat()` from `combat_resolver.py`

#### 1.3 `src/simulation_controller.py` - `_resolve_encounter()`
- **Function:** `_resolve_encounter()`
- **Lines:** 253-332
- **Who calls it:**
  - `src/simulation_controller.py` - `_execute_encounter_action()` (line 249)
  - `src/simulation_controller.py` - `_execute_travel_to_destination()` (line 140)
- **Conditions:**
  - `dispatch.next_handler == HANDLER_COMBAT_STUB` (line 286)
- **Action:** Calls `resolve_combat()` from `combat_resolver.py` (line 304)

#### 1.4 `src/law_enforcement.py` - `resolve_option()` (ATTACK option)
- **Function:** `resolve_option()`
- **Lines:** 242-393
- **Who calls it:**
  - `src/law_enforcement.py` - `enforcement_checkpoint()` (line ~470)
- **Conditions:**
  - `option == PlayerOption.ATTACK` (line 344)
- **Note:** This does NOT call `resolve_combat()`. It uses a simplified escape/arrest resolution (lines 344-351). This is a **separate combat-like path** for law enforcement.

---

## 2. Combat Resolution Authority

### Primary Combat Resolver

#### 2.1 `src/combat_resolver.py` - `resolve_combat()`
- **Function:** `resolve_combat()`
- **Lines:** 667-1026
- **Full Signature:**
  ```python
  def resolve_combat(
      world_seed: str | int,
      combat_id: str,
      player_loadout: ShipLoadout | None = None,
      enemy_loadout: ShipLoadout | None = None,
      player_ship_state: dict[str, Any] | None = None,
      enemy_ship_state: dict[str, Any] | None = None,
      player_action_selector: Optional[Callable[..., ActionName]] = None,
      enemy_action_selector: Optional[Callable[..., ActionName]] = None,
      max_rounds: int = 20,
      system_id: str = "",
  ) -> CombatResult
  ```
- **Return Type:** `CombatResult` (dataclass defined lines 87-100)
- **State Mutations:**
  - **Inside resolver:** Mutates local `CombatState` objects (player_state, enemy_state) during combat rounds
  - **Does NOT mutate:** External ship objects, player state, world state
  - **Returns:** `CombatResult` containing final states as dictionaries (not references to original objects)

### Is there exactly ONE combat resolution authority?

**Answer: NO**

#### Duplicate/Alternative Combat Paths:

1. **`src/law_enforcement.py` - `resolve_option()` ATTACK path (lines 344-351)**
   - **File:** `src/law_enforcement.py`
   - **Function:** `resolve_option()`
   - **Lines:** 344-351
   - **Description:** When player chooses ATTACK during law enforcement, uses simplified RNG-based escape/arrest resolution instead of calling `resolve_combat()`
   - **Risk:** This is a separate combat-like resolution path that does not use the combat resolver
   - **Note:** This may be intentional for law enforcement, but it represents a duplicate resolution mechanism

2. **`src/government_law_engine.py` - `resolve_enforcement()` ATTACK path (lines 187-193)**
   - **File:** `src/government_law_engine.py`
   - **Function:** `resolve_enforcement()`
   - **Lines:** 187-193
   - **Description:** Returns placeholder `EnforcementOutcome` with `notes="combat_placeholder"` for ATTACK response
   - **Risk:** This is a placeholder that does not resolve combat

---

## 3. Ship State Mutations

### Mutations Inside Combat Resolver

#### 3.1 `src/combat_resolver.py` - Internal State Mutations
- **File:** `src/combat_resolver.py`
- **Function:** `resolve_combat()` and helper functions
- **Mutations:**
  - `CombatState.hull_current` - modified in `_apply_damage_and_degradation()` (line 514)
  - `CombatState.degradation` - modified in `_apply_damage_and_degradation()` (line 520)
  - `CombatState.repair_uses_remaining` - modified in `_repair_once()` (line 479)
  - `CombatState.scanned` - modified during scan actions (lines 800, 811)
- **Is inside combat resolver?** YES
- **Risk:** None - these are local state objects, not external ship objects

### Mutations Outside Combat Resolver

#### 3.2 `src/game_engine.py` - Post-Combat Ship State Application
- **File:** `src/game_engine.py`
- **Function:** `_resolve_encounter_combat()`
- **Lines:** 2295-2301
- **Mutations:**
  - `player_ship.persistent_state["degradation_state"]` - set from combat result (line 2297-2299)
  - `player_ship.persistent_state["current_hull_integrity"]` - set from combat result (line 2300-2301)
- **Is inside combat resolver?** NO
- **Risk:** **MEDIUM** - This is the authorized post-combat application point. However, it directly mutates ship persistent state. This is the expected pattern, but it should be verified that this is the ONLY place where combat results are applied to ship state.

#### 3.3 `src/simulation_controller.py` - No Post-Combat Ship State Application
- **File:** `src/simulation_controller.py`
- **Function:** `_resolve_encounter()`
- **Lines:** 304-320
- **Mutations:** NONE
- **Is inside combat resolver?** NO
- **Risk:** **HIGH** - `simulation_controller.py` calls `resolve_combat()` but does NOT apply the final state to the player ship. This means combat damage/degradation is not persisted when using `simulation_controller.py`. This is a **critical missing integration**.

#### 3.4 Direct Hull/Degradation Mutations (Non-Combat)
- **File:** `src/game_engine.py`
- **Function:** Various ship assembly/repair functions
- **Lines:** 2593-2597 (ship assembly)
- **Mutations:** Ship persistent state during non-combat operations
- **Is inside combat resolver?** NO
- **Risk:** **LOW** - These are authorized non-combat mutations (repair, assembly)

### Summary of State Mutation Risks

**Flagged Violations:**
1. **`src/simulation_controller.py`** - Missing post-combat state application (HIGH RISK)
2. **`src/law_enforcement.py`** - Separate combat-like resolution path (MEDIUM RISK - may be intentional)

---

## 4. RNG Determinism Audit

### RNG Usage Inside Combat

#### 4.1 `src/combat_resolver.py` - `CombatRng` Class
- **File:** `src/combat_resolver.py`
- **Class:** `CombatRng`
- **Lines:** 103-124
- **Seed Input:**
  - `world_seed: str | int`
  - `salt: str` (format: `f"{combat_id}_combat"` - line 717)
- **Stream Name:** `"{combat_id}_combat"`
- **Encounter ID Usage:** YES - `combat_id` is used as salt (line 717)
- **Determinism:** YES - Uses SHA256 hash of seed text, deterministic

#### 4.2 RNG Usage in Combat Resolver
- **Damage rolls:** `rng.randint()` with label `f"damage_roll_{attacker_side}_to_{defender_side}"` (line 594)
- **Mitigation rolls:** `rng.randint()` with label `f"mitigation_roll_{defender_side}_vs_{attacker_side}"` (line 602)
- **Degradation subsystem selection:** `rng.randint()` with label `"degradation_subsystem"` (line 491)
- **Scan rolls:** `rng.randint()` with labels `"scan_roll_player"`, `"scan_roll_enemy"` (lines 797, 808)
- **All RNG calls:** Logged to event log with counter, label, range, value, round (lines 111-124)

#### 4.3 Escape Attempt RNG
- **File:** `src/combat_resolver.py`
- **Function:** `_escape_attempt()`
- **Lines:** 540-579
- **RNG Usage:** Delegates to `resolve_pursuit()` from `pursuit_resolver.py` (line 563)
- **Stream Isolation:** Uses separate encounter_id: `f"{combat_id}_escape_r{round_number}"` (line 562)
- **Risk:** **LOW** - Properly isolated with unique encounter_id

#### 4.4 Salvage RNG (Called from Combat)
- **File:** `src/combat_resolver.py`
- **Function:** `resolve_combat()` calls `resolve_salvage_modules()` (line 987)
- **File:** `src/salvage_resolver.py`
- **Function:** `resolve_salvage_modules()`
- **Lines:** 97-136
- **RNG Streams:**
  - `"npc_salvage_count"` (line 107)
  - `"npc_salvage_select"` (line 108)
  - `"npc_salvage_mutation"` (line 109)
- **Seed Input:** `world_seed`, `system_id`, `encounter_id` (format: `f"{combat_id}_enemy_destroyed"` - line 990)
- **Stream Isolation:** YES - Uses separate streams with unique encounter_id
- **Risk:** **LOW** - Properly isolated

### RNG Usage Adjacent to Combat

#### 4.5 Law Enforcement RNG (Separate from Combat)
- **File:** `src/law_enforcement.py`
- **Function:** `enforcement_checkpoint()`
- **Lines:** 419-420
- **RNG Stream:** `_rng_for(world_seed, system_id, turn, trigger_type.value, "inspection")`
- **Stream Name:** `"inspection"`
- **Risk:** **LOW** - Separate stream, not combat-related

#### 4.6 Reward Materialization RNG
- **File:** `src/reward_materializer.py`
- **Function:** `materialize_reward()`
- **RNG Usage:** Uses `world_seed` for deterministic reward generation
- **Stream Isolation:** Separate from combat
- **Risk:** **LOW** - Properly isolated

### RNG Determinism Summary

**Are RNG channels isolated per subsystem?** YES
- Combat uses `CombatRng` with stream `"{combat_id}_combat"`
- Salvage uses separate streams: `"npc_salvage_count"`, `"npc_salvage_select"`, `"npc_salvage_mutation"`
- Escape uses pursuit resolver with separate encounter_id
- Law enforcement uses separate `"inspection"` stream

**Is combat using dedicated deterministic streams?** YES
- All combat RNG uses `CombatRng` class with deterministic seeding
- All RNG calls are logged to event log

**Any shared RNG usage that risks cross-system contamination?** NO
- All subsystems use isolated RNG streams with unique identifiers

---

## 5. Post-Combat Outcome Flow

### Flow from CombatResult to Application

#### 5.1 Combat Result Structure
- **File:** `src/combat_resolver.py`
- **Class:** `CombatResult`
- **Lines:** 87-100
- **Fields:**
  - `outcome: OutcomeName` ("destroyed", "escape", "surrender", "max_rounds")
  - `winner: Optional[Literal["player", "enemy", "none"]]`
  - `final_state_player: dict`
  - `final_state_enemy: dict`
  - `salvage_modules: list[dict[str, Any]]`
  - `destruction_event: Optional[dict]`
  - `surrendered_by: Optional[SideName]`

#### 5.2 Game Engine Flow (`src/game_engine.py`)

**Step 1: Combat Resolution**
- `_resolve_encounter_combat()` calls `resolve_combat()` (line 2287)
- Returns `CombatResult`

**Step 2: Ship State Application**
- `_resolve_encounter_combat()` applies final state to player ship (lines 2295-2301)
  - Sets `player_ship.persistent_state["degradation_state"]` from `final_state_player["degradation"]`
  - Sets `player_ship.persistent_state["current_hull_integrity"]` from `final_state_player["current_hull"]`

**Step 3: Reward Qualification Check**
- `_reward_qualifies()` checks if combat outcome qualifies for reward (lines 2377-2396)
  - For combat resolver: returns `True` only if `winner == "player"` (line 2384)

**Step 4: Reward Materialization**
- `materialize_reward()` called if qualified (line 2250)
- Uses encounter spec and system market data

**Step 5: Reward Application**
- `apply_materialized_reward()` called (line 2255)
- Mutates `player.credits` and `player.cargo_by_ship["active"]`

**Step 6: Salvage Application**
- **MISSING** - `salvage_modules` from `CombatResult` are NOT applied to player inventory in `game_engine.py`
- Salvage is generated but not materialized/applied

#### 5.3 Simulation Controller Flow (`src/simulation_controller.py`)

**Step 1: Combat Resolution**
- `_resolve_encounter()` calls `resolve_combat()` (line 304)
- Returns `CombatResult`

**Step 2: Ship State Application**
- **MISSING** - No application of final state to player ship
- Combat damage/degradation is NOT persisted

**Step 3: Event Logging**
- Logs combat resolved event (lines 312-319)
- Includes `salvage_count` but does not apply salvage

**Step 4: Reward Materialization**
- `materialize_reward()` called unconditionally (line 322)
- **Note:** Does not check `_reward_qualifies()` like `game_engine.py` does

**Step 5: Reward Application**
- `apply_materialized_reward()` called (line 323)
- Mutates player credits/cargo

**Step 6: Salvage Application**
- **MISSING** - `salvage_modules` are NOT applied

### Post-Combat Flow Issues

**Flagged Issues:**

1. **Salvage Not Applied (HIGH RISK)**
   - `CombatResult.salvage_modules` is generated by combat resolver
   - Neither `game_engine.py` nor `simulation_controller.py` applies salvage to player inventory
   - Salvage is logged but never materialized

2. **Ship State Not Applied in Simulation Controller (HIGH RISK)**
   - `simulation_controller.py` does not apply combat final state to player ship
   - Combat damage/degradation is lost

3. **Reward Qualification Inconsistency (MEDIUM RISK)**
   - `game_engine.py` checks `_reward_qualifies()` before materializing rewards
   - `simulation_controller.py` does not check qualification
   - Rewards may be applied when they should not be

4. **No XP/Reputation Application (MEDIUM RISK)**
   - Combat outcomes do not directly update progression tracks (law/outlaw)
   - No reputation changes based on combat outcomes
   - No XP system integration visible

5. **No Mission Integration (MEDIUM RISK)**
   - No code found that updates mission success/failure based on combat outcomes
   - Mission system may need to hook into combat results

6. **No World State Tagging (LOW RISK)**
   - No code found that tags destinations as destroyed based on combat
   - No structural mutations (population, government) from combat

### Post-Combat Application Order (Current)

1. Combat resolution → `CombatResult`
2. Ship state application (game_engine only)
3. Reward qualification check (game_engine only)
4. Reward materialization
5. Reward application
6. **MISSING:** Salvage application
7. **MISSING:** XP/Reputation updates
8. **MISSING:** Mission updates
9. **MISSING:** World state tagging

---

## 6. Escape and Surrender Logic Mapping

### Surrender Handling

#### 6.1 Combat Resolver Surrender
- **File:** `src/combat_resolver.py`
- **Function:** `resolve_combat()`
- **Lines:** 747-780
- **Handling:**
  - If player action is "Surrender" → returns `CombatResult` with `outcome="surrender"`, `winner="enemy"`, `surrendered_by="player"` (lines 747-763)
  - If enemy action is "Surrender" → returns `CombatResult` with `outcome="surrender"`, `winner="player"`, `surrendered_by="enemy"` (lines 764-780)
- **Location:** Inside combat resolver
- **Is surrender handled in more than one location?** NO (for combat)

#### 6.2 Law Enforcement Surrender
- **File:** `src/law_enforcement.py`
- **Function:** `resolve_option()`
- **Lines:** 248-252 (SUBMIT option, not explicit surrender)
- **Note:** Law enforcement has `PlayerOption.SUBMIT` but no explicit `SURRENDER` option in combat context
- **Is surrender handled in more than one location?** NO (different context)

### Escape Handling

#### 6.3 Combat Resolver Escape
- **File:** `src/combat_resolver.py`
- **Function:** `resolve_combat()`
- **Lines:** 884-937
- **Handling:**
  - If player action is "Attempt Escape" → calls `_escape_attempt()` (line 885)
  - `_escape_attempt()` delegates to `resolve_pursuit()` from `pursuit_resolver.py` (line 563)
  - If escape succeeds → returns `CombatResult` with `outcome="escape"`, `winner="player"` (lines 898-910)
  - If enemy attempts escape → similar logic (lines 911-937)
- **Location:** Inside combat resolver
- **Uses pursuit resolver:** YES

#### 6.4 Pursuit Resolver Escape
- **File:** `src/pursuit_resolver.py`
- **Function:** `resolve_pursuit()`
- **Called from:** Combat resolver `_escape_attempt()` (line 563)
- **Is escape logic duplicated?** NO - Combat escape uses pursuit resolver

#### 6.5 Law Enforcement Escape
- **File:** `src/law_enforcement.py`
- **Function:** `resolve_option()`
- **Lines:** 332-343 (FLEE option)
- **Handling:** Uses RNG roll (50% chance) to determine escape success
- **Is escape logic duplicated?** YES - Law enforcement has separate escape logic that does not use pursuit resolver

### Escape and Surrender Summary

**Is surrender handled in more than one location?** NO
- Combat surrender is handled only in combat resolver
- Law enforcement has SUBMIT (different context)

**Is escape logic duplicated?** YES
- Combat escape uses pursuit resolver (properly delegated)
- Law enforcement escape uses separate RNG-based logic (duplicate)

---

## 7. Mission Integration

### Mission System Files
- **File:** `src/mission_manager.py`
- **Functions:** Mission creation, acceptance, completion
- **Combat Integration:** **NOT FOUND**

### How Combat Outcomes Inform Mission Success/Failure

**Answer: NO INTEGRATION FOUND**

- No code found that:
  - Checks combat outcomes against mission objectives
  - Updates mission status based on combat results
  - Applies mission rewards based on combat victories
  - Tracks combat-related mission progress

### Mission Lifecycle Hooks into Combat Results

**Answer: NO HOOKS FOUND**

- No code found that:
  - Subscribes to combat events
  - Queries combat results for mission evaluation
  - Updates mission state from combat outcomes

### Whether Mission Resolution Logic Mutates Ship State Directly

**Answer: NO DIRECT MUTATIONS FOUND**

- Mission system uses `reward_applicator.apply_mission_rewards()` (line 11 of `mission_manager.py`)
- This mutates player state (credits, progression tracks) but not ship state
- No direct ship state mutations from mission system

### Mission Integration Summary

**Status:** **NOT INTEGRATED**
- Combat outcomes do not inform mission success/failure
- No mission lifecycle hooks into combat results
- Mission system does not mutate ship state directly

---

## 8. World State Integration

### World State Engine
- **File:** `src/world_state_engine.py` (referenced but not examined in detail)
- **Usage:** Referenced in `game_engine.py` and `simulation_controller.py`

### Whether Combat Can Directly Mutate World State

**Answer: NO DIRECT MUTATIONS FOUND**

- No code found in combat resolver that mutates:
  - Destination destroyed tags
  - System state
  - Population
  - Government

### Whether These Are Correctly Routed Through World State Engine

**Answer: NOT ROUTED**

- Combat resolver does not interact with world state engine
- No code found that applies combat outcomes to world state
- No structural mutations from combat

### World State Integration Summary

**Status:** **NOT INTEGRATED**
- Combat does not mutate world state directly
- Combat outcomes are not routed through World State Engine
- No structural effects (destroyed tags, population, government) from combat

---

## 9. NPC Persistence Tier Integration

### NPC Persistence System
- **File:** `src/game_engine.py`
- **NPC Persistence Tiers:** `NPCPersistenceTier.TIER_1`, `TIER_2`, `TIER_3`
- **Usage:** NPCs have `persistence_tier` attribute

### How Combat Outcomes Affect NPC Persistence Tiers

**Answer: NO INTEGRATION FOUND**

- No code found that:
  - Updates NPC persistence tiers based on combat outcomes
  - Marks NPCs as destroyed/killed from combat
  - Changes NPC relationships based on combat results

### Whether Persistence Changes Occur Outside Authorized Systems

**Answer: NO UNAUTHORIZED CHANGES FOUND**

- NPC persistence tier changes found only in:
  - `src/game_engine.py` - crew dismissal (line 1330)
  - `src/game_engine.py` - NPC generation (lines 829, 3160)
- No combat-related persistence tier changes found

### NPC Persistence Integration Summary

**Status:** **NOT INTEGRATED**
- Combat outcomes do not affect NPC persistence tiers
- No persistence changes from combat found
- No unauthorized persistence changes detected

---

## 10. Time Engine Compliance

### Time Engine
- **File:** `src/time_engine.py` (referenced)
- **Usage:** `TimeEngine.advance()` called in various places

### Combat Does NOT Advance Time

**Answer: YES - COMPLIANT**

- **File:** `src/combat_resolver.py`
- **Search:** No references to `time_engine`, `advance`, or `TimeEngine` found
- **Conclusion:** Combat resolver does not advance time

### No Direct Time Mutation Inside Combat Resolver

**Answer: YES - COMPLIANT**

- Combat resolver has no time-related code
- All time advancement occurs outside combat resolver
- Time is advanced by:
  - `src/turn_loop.py` - `execute_move()`, `execute_buy()`, `execute_sell()`
  - `src/game_engine.py` - travel and other actions
  - `src/simulation_controller.py` - travel actions

### Time Engine Compliance Summary

**Status:** **COMPLIANT**
- Combat does not advance time
- No direct time mutation inside combat resolver
- Time advancement is handled by authorized systems outside combat

---

## 11. Risk Assessment

### High Risk

1. **Missing Salvage Application**
   - **Location:** `src/game_engine.py`, `src/simulation_controller.py`
   - **Issue:** `CombatResult.salvage_modules` is generated but never applied to player inventory
   - **Impact:** Players do not receive salvage from destroyed enemy ships
   - **Files:** `src/game_engine.py` (lines 2267-2302), `src/simulation_controller.py` (lines 304-320)

2. **Missing Ship State Application in Simulation Controller**
   - **Location:** `src/simulation_controller.py`
   - **Issue:** Combat final state (damage, degradation) is not applied to player ship
   - **Impact:** Combat damage/degradation is lost when using simulation controller
   - **Files:** `src/simulation_controller.py` (lines 304-320)

3. **Duplicate Combat Resolution Path (Law Enforcement)**
   - **Location:** `src/law_enforcement.py`
   - **Issue:** ATTACK option uses separate RNG-based resolution instead of combat resolver
   - **Impact:** Inconsistent combat resolution, potential balance issues
   - **Files:** `src/law_enforcement.py` (lines 344-351)

### Medium Risk

4. **Reward Qualification Inconsistency**
   - **Location:** `src/game_engine.py` vs `src/simulation_controller.py`
   - **Issue:** `game_engine.py` checks reward qualification, `simulation_controller.py` does not
   - **Impact:** Rewards may be applied when they should not be
   - **Files:** `src/game_engine.py` (lines 2377-2396), `src/simulation_controller.py` (line 322)

5. **Missing XP/Reputation Integration**
   - **Location:** Post-combat flow
   - **Issue:** Combat outcomes do not update progression tracks (law/outlaw)
   - **Impact:** Combat victories do not contribute to progression
   - **Files:** No integration found

6. **Missing Mission Integration**
   - **Location:** Mission system
   - **Issue:** Combat outcomes do not inform mission success/failure
   - **Impact:** Combat-related missions cannot be completed
   - **Files:** No integration found

7. **Duplicate Escape Logic (Law Enforcement)**
   - **Location:** `src/law_enforcement.py`
   - **Issue:** Law enforcement escape uses separate RNG logic instead of pursuit resolver
   - **Impact:** Inconsistent escape mechanics
   - **Files:** `src/law_enforcement.py` (lines 332-343)

### Low Risk

8. **Missing World State Integration**
   - **Location:** Post-combat flow
   - **Issue:** Combat outcomes do not affect world state (destroyed tags, population, government)
   - **Impact:** Combat has no structural world effects
   - **Files:** No integration found

9. **Missing NPC Persistence Integration**
   - **Location:** Post-combat flow
   - **Issue:** Combat outcomes do not affect NPC persistence tiers
   - **Impact:** NPCs are not marked as destroyed/killed from combat
   - **Files:** No integration found

---

## 12. Unified Combat Contract Requirements

Based on findings, the unified Combat Contract must explicitly specify:

### Single Authority Definition
- **Requirement:** `src/combat_resolver.py` - `resolve_combat()` is the ONLY authorized combat resolution function
- **Exception:** Law enforcement ATTACK path must be clarified - either integrate with combat resolver or document as intentional separate system
- **Files to Update:** Combat contract documentation

### Allowed State Mutations
- **Inside Combat Resolver:**
  - Local `CombatState` objects (hull_current, degradation, repair_uses_remaining, scanned)
  - NO mutations to external ship objects, player state, or world state
- **Post-Combat Application (Authorized):**
  - `player_ship.persistent_state["degradation_state"]` - from `final_state_player["degradation"]`
  - `player_ship.persistent_state["current_hull_integrity"]` - from `final_state_player["current_hull"]`
  - **Location:** `src/game_engine.py` - `_resolve_encounter_combat()` (lines 2295-2301)

### Forbidden Mutations
- **Forbidden:** Direct mutations to ship objects inside combat resolver
- **Forbidden:** Mutations to player state (credits, cargo, reputation) inside combat resolver
- **Forbidden:** Mutations to world state inside combat resolver
- **Forbidden:** Time advancement inside combat resolver
- **Forbidden:** Mission state mutations inside combat resolver

### Required RNG Isolation
- **Requirement:** Combat must use `CombatRng` class with stream `"{combat_id}_combat"`
- **Requirement:** Salvage must use separate streams: `"npc_salvage_count"`, `"npc_salvage_select"`, `"npc_salvage_mutation"`
- **Requirement:** Escape must use pursuit resolver with separate encounter_id
- **Requirement:** All RNG calls must be logged to event log

### Required Post-Combat Application Ordering
1. Combat resolution → `CombatResult`
2. Ship state application (from `final_state_player` to `player_ship.persistent_state`)
3. Salvage application (from `salvage_modules` to player inventory)
4. Reward qualification check
5. Reward materialization (if qualified)
6. Reward application (credits, cargo)
7. XP/Reputation updates (if applicable)
8. Mission updates (if applicable)
9. World state tagging (if applicable)

### Required Integration Boundaries
- **Combat Resolver:** Pure function, no side effects, returns `CombatResult`
- **Post-Combat Application:** Must occur in authorized integration points (`game_engine.py`, `simulation_controller.py`)
- **Salvage Application:** Must be implemented in post-combat flow
- **Reward Application:** Must use `reward_applicator.apply_materialized_reward()`
- **Mission Integration:** Must hook into combat results for mission evaluation
- **World State Integration:** Must route through World State Engine (if structural effects are desired)

---

## 13. Final Verdict

### Is combat currently unified?

**Answer: PARTIALLY**

- **Primary Authority:** YES - `src/combat_resolver.py` - `resolve_combat()` is the primary combat resolution function
- **Duplicate Paths:** YES - Law enforcement ATTACK path uses separate resolution
- **Integration Consistency:** NO - `simulation_controller.py` does not apply ship state, salvage is not applied anywhere

### Is determinism preserved?

**Answer: YES**

- Combat uses deterministic `CombatRng` with proper seeding
- All RNG calls are logged
- RNG streams are isolated per subsystem
- No shared RNG usage detected

### Are hidden state mutations present?

**Answer: YES**

- **Hidden Mutation 1:** `simulation_controller.py` does not apply combat final state (damage/degradation lost)
- **Hidden Mutation 2:** Salvage modules are generated but never applied to player inventory
- **Hidden Mutation 3:** Law enforcement ATTACK path uses separate resolution (may be intentional but not documented)

### Estimated Refactor Complexity

**Answer: MEDIUM**

**Required Changes:**
1. **High Priority:**
   - Implement salvage application in post-combat flow (2 files)
   - Implement ship state application in `simulation_controller.py` (1 file)
   - Clarify/integrate law enforcement ATTACK path (1 file)

2. **Medium Priority:**
   - Standardize reward qualification check (1 file)
   - Implement XP/Reputation updates (new integration)
   - Implement mission integration (new integration)

3. **Low Priority:**
   - Implement world state integration (if desired)
   - Implement NPC persistence integration (if desired)

**Complexity Factors:**
- Multiple integration points need updates
- New integrations required (salvage, XP, missions)
- Law enforcement path needs clarification
- Testing required for all integration points

**Estimated Effort:** 3-5 days for high priority items, 1-2 weeks for full integration

---

## Appendix: File Reference Index

### Combat-Related Files
- `src/combat_resolver.py` - Primary combat resolver (1027 lines)
- `src/game_engine.py` - Game engine integration (lines 2267-2302)
- `src/simulation_controller.py` - Simulation controller integration (lines 286-320)
- `src/interaction_layer.py` - Combat entry point routing (lines 155-233)
- `src/salvage_resolver.py` - Salvage generation (137 lines)
- `src/reward_applicator.py` - Reward application (54 lines)
- `src/reward_materializer.py` - Reward materialization
- `src/law_enforcement.py` - Law enforcement (includes separate combat-like path, lines 344-351)
- `src/government_law_engine.py` - Government law engine (includes combat placeholder, lines 187-193)

### Integration Files
- `src/mission_manager.py` - Mission system (no combat integration found)
- `src/world_state_engine.py` - World state engine (referenced, not examined)
- `src/time_engine.py` - Time engine (referenced, not examined)
- `src/player_state.py` - Player state (no direct combat mutations)
- `src/pursuit_resolver.py` - Pursuit resolver (used by combat escape)

---

## Implementation Notes (Phase 7.10)

**Date:** 2024  
**Version:** 0.11.2+phase7_10_combat_unification

### Changes Made

1. **Created `src/combat_application.py`**
   - Added `apply_combat_result()` function to unify combat outcome application
   - Applies player ship final hull + degradation to persistent_state
   - Applies enemy ship state if enemy is persisted
   - Applies salvage_modules to player_state.salvage_modules list
   - Returns summary dict for logging

2. **Updated `src/game_engine.py`**
   - Modified `_resolve_encounter_combat()` to accept optional `get_player_action` callback for interactive combat
   - Added deterministic enemy action selector based on encounter_id and round_number
   - Integrated `apply_combat_result()` to persist combat outcomes
   - Added structured logging: `combat_started`, `combat_resolved`, `combat_applied`
   - Updated law enforcement routing to use unified combat/pursuit systems when `route_to_handler` is set

3. **Updated `src/simulation_controller.py`**
   - Integrated `apply_combat_result()` to ensure combat outcomes are persisted
   - Added salvage application to prevent dropped salvage modules

4. **Updated `src/law_enforcement.py`**
   - Removed duplicate ATTACK and FLEE resolution logic from `resolve_option()`
   - Added `route_to_handler` field to `EnforcementOutcome` dataclass
   - ATTACK option now routes to unified combat system (sets `route_to_handler="combat"`)
   - FLEE option now routes to unified pursuit system (sets `route_to_handler="pursuit"`)
   - Heat deltas are still calculated but applied after combat/pursuit resolution

5. **Updated `src/game_engine.py` - Pursuit Ships**
   - Modified `_pursuit_ships_for_spec()` to use assembled ship data
   - Uses `assemble_ship()` to get proper engine_band, tr_band, and module detection
   - Calculates speed from engine_band
   - Detects cloaking_device and interdiction_device from module instances
   - Calculates TR from assembled ship state (weapon, defense, engine bands, hull_max, repairs)

6. **Updated `src/player_state.py`**
   - Added `salvage_modules: List[Dict[str, Any]]` field to store salvaged modules
   - Updated `to_dict()` to include salvage_modules in serialization

### Integration Points

- **Combat Application:** All combat outcomes now flow through `apply_combat_result()`
- **Law Enforcement:** ATTACK and FLEE now route to unified systems instead of resolving internally
- **Pursuit:** Uses assembled ship fields consistently (speed, engine_band, tr_band, modules)
- **Salvage:** Salvage modules are applied to player_state.salvage_modules list
- **Logging:** Structured combat events logged at start, resolution, and application

### Remaining Work

- **Interactive Combat:** Infrastructure is in place (callback mechanism), but CLI needs to provide `get_player_action` callback to enable round-by-round prompting
- **Mission Integration:** Combat outcomes do not yet inform mission success/failure (future work)
- **XP/Reputation:** Combat outcomes do not yet update progression tracks (future work)

### Testing

- All existing tests pass (360 tests)
- No breaking changes to existing functionality
- Determinism preserved (all RNG uses world_seed + encounter_id salt)

---

**End of Audit Report**
