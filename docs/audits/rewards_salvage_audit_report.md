# Rewards + Salvage Integration Audit Report

**Date:** 2024-12-19  
**Scope:** Complete architectural audit of combat → reward → salvage pipeline  
**Status:** READ-ONLY AUDIT (No code changes)

---

## Executive Summary

This audit examines the current implementation of the rewards and salvage system against authoritative contracts and user requirements. The system has **partial implementation** with several critical gaps:

- **Rewards:** Materialization exists and is triggered conditionally, but lacks combat-outcome-aware gating and cargo capacity enforcement.
- **Salvage:** Generation is fully implemented and deterministic, but **application to player inventory is incomplete** (modules stored in `PlayerState.salvage_modules` but no capacity checks or installation paths).
- **UI/Prompts:** **Completely missing** - no loot acceptance/jettison/decline flows exist.
- **Contract Compliance:** Multiple violations identified, particularly around cargo overflow and stolen goods handling.

---

## A) Current Behavior Map

### A.1 Reward Trigger Points

#### **Function:** `GameEngine._apply_conditional_rewards()`
- **Location:** `src/game_engine.py:2500-2532`
- **Trigger Condition:** Called after encounter resolution via `_reward_qualifies()` check
- **Timing:** **After encounter decision/resolution**, NOT directly tied to combat outcome
- **Gating Logic:** `_reward_qualifies()` at line 3470-3489:
  - For `resolver == "combat"`: Returns `True` if `winner == "player"` (any combat outcome where player wins)
  - For `resolver == "pursuit"`: Returns `True` if `outcome == "escape_success"`
  - For `resolver == "reaction"`: Returns `True` if `outcome == "accept"`
  - **Issue:** Does NOT distinguish between combat outcomes (destroyed vs surrender vs escape)
- **Materialization Call:** `materialize_reward(spec, system_markets, world_seed)` at line 2517
- **Application Call:** `apply_materialized_reward(player, reward_payload, context="game_engine")` at line 2522

#### **Function:** `GameEngine._apply_post_combat_rewards_and_salvage()`
- **Location:** **MISSING** - Function is called at `src/game_engine.py:3350` but **does not exist**
- **Call Site:** `src/game_engine.py:3349-3354` (only when `combat_result.winner == "player"` AND `combat_result.outcome == "destroyed"`)
- **Status:** **DEAD CODE** - This function call will raise `AttributeError` at runtime

#### **Function:** `SimulationController._apply_rewards()`
- **Location:** `src/simulation_controller.py:338-348`
- **Trigger:** After encounter resolution in simulation loop
- **Timing:** Unconditional (no gating check like `_reward_qualifies`)
- **Materialization:** `materialize_reward(encounter, [_market_payload(...)], world_seed)`
- **Application:** `apply_materialized_reward(player, reward_payload, context="simulation_controller")`

### A.2 Reward Generation Timing

**Current State:**
- Rewards are **NOT generated at combat start**
- Rewards are **generated AFTER combat ends** (via `_apply_conditional_rewards` after encounter resolution)
- **Problem:** The reward materialization happens in the generic encounter pipeline, not in a dedicated post-combat handler
- **Missing:** Explicit reward trigger based on `CombatResult.outcome` and `CombatResult.winner`

### A.3 Salvage Generation

#### **Function:** `resolve_salvage_modules()`
- **Location:** `src/salvage_resolver.py:97-136`
- **Trigger Points:**
  1. `src/combat_resolver.py:1289-1295` (in `resolve_combat()` when enemy destroyed)
  2. `src/game_engine.py:3306-3314` (in `_execute_combat_action()` when enemy destroyed in step-based combat)
  3. `src/game_engine.py:3013-3019` (in older combat path, when enemy destroyed)
- **Input Data:**
  - `world_seed`: From engine
  - `system_id`: From `player_state.current_system_id`
  - `encounter_id`: Format `f"{combat_id}_enemy_destroyed"`
  - `destroyed_ship`: Dict with `module_instances` from enemy ship state
- **Output:** List of module instance dicts (with potential `secondary:unstable` mutation)
- **RNG Streams:** Isolated streams (`npc_salvage_count`, `npc_salvage_select`, `npc_salvage_mutation`)
- **Determinism:** Fully deterministic given identical inputs

#### **Salvage Application:**
- **Function:** `combat_application.apply_combat_result()`
- **Location:** `src/combat_application.py:89-108`
- **Behavior:** Appends `CombatResult.salvage_modules` to `player_state.salvage_modules` (list append, no capacity checks)
- **Called From:** `src/game_engine.py:3336-3346` (after combat ends in step-based path)
- **Status:** **Partially implemented** - Salvage is stored but:
  - No cargo capacity enforcement (modules consume 1 physical cargo unit per contract)
  - No installation path (modules remain in `salvage_modules` list indefinitely)
  - No UI/prompt for accepting/declining/jettisoning

### A.4 UI/Prompt Status

**Current State:** **COMPLETELY MISSING**

- No function exists to prompt player for loot acceptance
- No function exists to prompt player to jettison existing cargo
- No function exists to decline rewards/salvage
- No CLI menu for post-combat loot management
- **Result:** All rewards and salvage are applied automatically without player choice

### A.5 Cargo Capacity Enforcement

#### **Current State:**
- **`apply_materialized_reward()`** (`src/reward_applicator.py:8-22`):
  - **NO capacity checks**
  - Directly increments `player.cargo_by_ship["active"][sku_id]` without validation
  - **Contract Violation:** `ship_entity_contract.md` Section 6 states "Overflow is forbidden"

#### **Capacity Calculation:**
- **Function:** `GameEngine._compute_ship_cargo_capacities()`
- **Location:** `src/game_engine.py:2123-2167`
- **Behavior:** Computes `physical_cargo_capacity` and `data_cargo_capacity` from hull base + module bonuses
- **Usage:** Used for display/info, **NOT used for validation** during reward application

#### **Capacity Validation (Partial):**
- **Function:** `GameEngine._ensure_cargo_capacity_for_add()`
- **Location:** `src/game_engine.py:5271-5281`
- **Behavior:** Raises `ValueError("cargo_capacity_exceeded")` if adding `quantity` would exceed capacity
- **Usage:** Called in `_execute_buy_action()` (line 2039) for market purchases
- **Missing:** **NOT called** in `apply_materialized_reward()` or salvage application

---

## B) Contract Compliance Check

### B.1 Ship Entity Contract Violations

#### **Violation 1: Cargo Overflow Allowed**
- **Contract:** `design/ship_entity_contract.md` Section 6: "Overflow is forbidden"
- **Current Behavior:** `apply_materialized_reward()` allows unlimited cargo addition
- **Severity:** **CRITICAL** - Direct contract violation
- **Location:** `src/reward_applicator.py:18-19`

#### **Violation 2: Module Cargo Consumption Not Enforced**
- **Contract:** `design/ship_and_module_schema_contract.md` Section 6.3: "ALL modules consume exactly 1 unit of PHYSICAL cargo when not installed"
- **Current Behavior:** Salvage modules appended to `player_state.salvage_modules` without cargo capacity check
- **Severity:** **CRITICAL** - Direct contract violation
- **Location:** `src/combat_application.py:104-107`

### B.2 NPC Ship Generation and Salvage Contract Compliance

#### **Compliance: Salvage Generation**
- **Contract:** `design/npc_ship_generation_and_salvage_contract.md` Section 7
- **Status:** **FULLY COMPLIANT**
  - Salvage count weights: `{0: 50, 1: 40, 2: 10}` ✓ (matches contract)
  - Rarity factors: `{"common": 1.0, "uncommon": 2.0, "rare": 4.0, "unique": 8.0}` ✓
  - Secondary factors: Alien/prototype bonuses applied correctly ✓
  - Mutation chance: 0.20 for modules with no secondaries ✓
  - RNG streams: Isolated and deterministic ✓

#### **Compliance: Salvage Mutation**
- **Contract:** `design/ship_and_module_schema_contract.md` Section 9.1
- **Status:** **FULLY COMPLIANT**
  - Only modules with NO secondary tags receive `secondary:unstable` ✓
  - Mutation probability: 0.20 (default) ✓
  - `salvage_policy.mutation_allowed` respected ✓

### B.3 Reward Profiles Schema Contract Compliance

#### **Compliance: Materialization**
- **Contract:** `design/reward_profiles_schema_contract.md`
- **Status:** **FULLY COMPLIANT**
  - TR multiplier applied: `quantity = base_quantity * spec.threat_rating_tr` ✓
  - SKU selection from system markets ✓
  - Stolen behavior resolved deterministically ✓
  - Seed format: `f"{world_seed}{spec.encounter_id}{spec.reward_profile_id}"` ✓

#### **Non-Compliance: Stolen Goods Handling**
- **Contract:** `design/reward_profiles_schema_contract.md` Section 4.6-4.7
- **Status:** **PARTIALLY COMPLIANT**
  - `stolen_applied` is computed and stored in `RewardResult` ✓
  - **BUT:** `apply_materialized_reward()` ignores `stolen_applied` entirely
  - **Missing:** No connection to law enforcement system (`consequences.json` has `stolen_goods_possession` violation but no linkage)
  - **Severity:** **HIGH** - Design intent not implemented

### B.4 Missing Implementations (Contract-Implied)

#### **Missing 1: Module Installation Path**
- **Contract Implication:** `design/ship_and_module_schema_contract.md` Section 7.1 states modules can be in "cargo" or "installed" states
- **Current State:** Salvage modules stored in `player_state.salvage_modules` with no installation mechanism
- **Missing:** Function to install modules from `salvage_modules` into ship slots (likely should be in shipdock system, outside this audit scope)

#### **Missing 2: Cargo Classification (Physical vs Data)**
- **Contract:** `design/ship_entity_contract.md` Section 5: Goods with "data" tag are DIGITAL cargo
- **Current State:** `apply_materialized_reward()` does not check SKU tags to determine cargo type
- **Missing:** Logic to route cargo to `physical_cargo_manifest` vs `data_cargo_manifest` based on SKU tags

---

## C) Gaps vs User Requirements

### C.1 Requirement 1: Rewards Trigger Primarily on Combat Win

**Status:** **PARTIALLY SATISFIED**

- **Current:** `_reward_qualifies()` returns `True` for `resolver == "combat"` AND `winner == "player"` (any player win)
- **Gap:** Does NOT distinguish between:
  - Combat win via destruction (should grant rewards)
  - Combat win via enemy surrender (should grant rewards per requirement)
  - Combat win via player escape (should NOT grant rewards per requirement)
- **Gap:** Derelict encounters can grant rewards, but there's no explicit derelict-specific reward path
- **Gap:** Hailing is separate (correct), but no explicit check that rewards don't trigger on hailing-only encounters

**Recommendation:** Update `_reward_qualifies()` to check `CombatResult.outcome`:
- `outcome == "destroyed"` AND `winner == "player"` → rewards
- `outcome == "surrender"` AND `surrendered_by == "enemy"` → rewards
- `outcome == "escape"` → no rewards (player escaped, didn't win)

### C.2 Requirement 2: Salvage Optional and Module-Dependent

**Status:** **FULLY SATISFIED**

- **Current:** `resolve_salvage_modules()` returns empty list if `module_instances` is empty ✓
- **Current:** Alien/prototype modules increase salvage likelihood via `_secondary_factor()` ✓
- **Current:** Salvage mutation applies `secondary:unstable` to modules with no secondaries per contract ✓

**No gaps identified.**

### C.3 Requirement 3: Salvaged Modules as Cargo or Installation

**Status:** **NOT SATISFIED**

- **Current:** Salvage modules stored in `player_state.salvage_modules` (holding area)
- **Missing:** No function to:
  - Install modules into open ship slots
  - Convert modules to cargo (1 module = 1 physical cargo unit)
  - Prompt player to choose installation vs cargo storage
- **Gap:** Modules remain in `salvage_modules` indefinitely with no consumption path

**Recommendation:** Implement:
1. Function to install salvage modules (likely in shipdock system)
2. Function to convert modules to cargo with capacity checks
3. Post-combat prompt: "Install [module] or store as cargo?"

### C.4 Requirement 4: Player Prompt + Cargo Capacity Enforcement

**Status:** **NOT SATISFIED**

- **Missing:** No UI/prompt for loot acceptance
- **Missing:** No jettison mechanism for existing cargo
- **Missing:** No decline option for rewards/salvage
- **Missing:** Cargo capacity checks during reward application
- **Missing:** Excess cargo jettison logic

**Recommendation:** Implement:
1. Post-combat loot prompt function (CLI menu)
2. Cargo capacity validation in `apply_materialized_reward()`
3. Jettison logic (player selects cargo to drop)
4. Automatic jettison of excess if player doesn't respond (or explicit "decline all")

---

## D) Recommendations (No Code Changes)

### D.1 Minimal Change Set

#### **Module 1: Reward Gating Enhancement**
- **File:** `src/game_engine.py`
- **Function:** `_reward_qualifies()` (line 3470)
- **Change:** Add `CombatResult.outcome` check to distinguish destroyed/surrender vs escape
- **Dependencies:** None (uses existing `resolver_outcome` dict)

#### **Module 2: Post-Combat Reward Handler**
- **File:** `src/game_engine.py`
- **Function:** `_apply_post_combat_rewards_and_salvage()` (CREATE - currently missing)
- **Responsibilities:**
  - Load `EncounterSpec` from active encounter registry
  - Call `materialize_reward()` if `spec.reward_profile_id` exists
  - Call `apply_materialized_reward()` with capacity checks
  - Trigger salvage application (already handled by `apply_combat_result()`)
- **Dependencies:** `EncounterSpec` must be accessible from `encounter_id`

#### **Module 3: Cargo Capacity Enforcement**
- **File:** `src/reward_applicator.py`
- **Function:** `apply_materialized_reward()` (line 8)
- **Change:** Add capacity validation before cargo addition
- **Logic:**
  1. Compute current cargo usage (sum of all SKUs in `cargo_by_ship["active"]`)
  2. Check SKU tags to determine physical vs data cargo
  3. Validate `current_usage + quantity <= capacity`
  4. If overflow: return error or trigger jettison prompt
- **Dependencies:** Access to `ShipEntity` to get cargo capacities (or pass capacities as parameter)

#### **Module 4: Salvage Cargo Conversion**
- **File:** `src/combat_application.py` OR new `src/salvage_applicator.py`
- **Function:** `apply_salvage_to_player()` (CREATE)
- **Responsibilities:**
  - Check physical cargo capacity for salvage modules (1 unit per module)
  - If capacity available: Convert modules to cargo entries
  - If capacity insufficient: Store in `salvage_modules` OR prompt for jettison
- **Dependencies:** Cargo capacity calculation, module-to-cargo conversion logic

#### **Module 5: Loot Acceptance UI**
- **File:** `src/run_game_engine_cli.py` OR new `src/loot_prompt.py`
- **Function:** `_prompt_loot_acceptance()` (CREATE)
- **Responsibilities:**
  - Display available rewards (credits, cargo SKUs, salvage modules)
  - Prompt: "Accept all / Select items / Decline all"
  - If "Select items": Allow player to choose which rewards to take
  - If capacity exceeded: Prompt for jettison of existing cargo
- **Dependencies:** CLI input handling, cargo capacity display

### D.2 Deterministic Seed Strategy

#### **Reward Materialization Seeds (Current - Compliant)**
- **Format:** `f"{world_seed}{spec.encounter_id}{spec.reward_profile_id}"`
- **Sub-seeds:**
  - SKU selection: `f"{world_seed}{spec.encounter_id}_sku"`
  - Quantity roll: `f"{world_seed}{spec.encounter_id}_qty"`
  - Stolen roll: `f"{world_seed}{spec.encounter_id}{spec.reward_profile_id}_stolen"`
  - Credits roll: `f"{world_seed}{spec.encounter_id}{spec.reward_profile_id}_credits"`
- **Status:** ✓ Already deterministic and isolated

#### **Salvage Resolution Seeds (Current - Compliant)**
- **Format:** `f"{world_seed}|{system_id}|{encounter_id}|{stream_name}"`
- **Streams:**
  - `"npc_salvage_count"`: Salvage count selection (0, 1, or 2)
  - `"npc_salvage_select"`: Module selection from destroyed ship
  - `"npc_salvage_mutation"`: Unstable injection roll
- **Status:** ✓ Already deterministic and isolated

#### **Recommendation: No Changes Needed**
- Current seed strategy is contract-compliant and deterministic
- All RNG streams are properly isolated
- No cross-contamination risks identified

### D.3 Architectural Contradictions

#### **Contradiction 1: Stolen Goods Design vs Implementation**
- **Design:** `reward_profiles.json` encodes rich stolen behavior (`always`, `none`, `probabilistic`)
- **Implementation:** `apply_materialized_reward()` ignores `stolen_applied` flag
- **Impact:** Stolen goods are never marked, never trigger law enforcement consequences
- **Resolution:** Add stolen flag to cargo entries, connect to law enforcement system

#### **Contradiction 2: Module Storage States**
- **Design:** Modules can be "installed", "cargo", or "warehouse" per `ship_and_module_schema_contract.md`
- **Implementation:** Salvage modules stored in `player_state.salvage_modules` (fourth state, not in contract)
- **Impact:** Modules stuck in limbo, no consumption path
- **Resolution:** Implement installation path OR cargo conversion path (or both with player choice)

#### **Contradiction 3: Cargo Overflow Forbidden vs Allowed**
- **Design:** `ship_entity_contract.md` explicitly forbids overflow
- **Implementation:** `apply_materialized_reward()` allows unlimited overflow
- **Impact:** Direct contract violation, breaks game balance
- **Resolution:** Add capacity checks and jettison logic

---

## E) Dead or Unreachable Paths

### E.1 Unreachable Code

#### **Function Call: `_apply_post_combat_rewards_and_salvage()`**
- **Location:** `src/game_engine.py:3350`
- **Status:** **DEAD CODE** - Function does not exist
- **Impact:** Will raise `AttributeError` at runtime when player wins combat via destruction
- **Severity:** **CRITICAL** - Game will crash

### E.2 Unused Metadata

#### **Field: `RewardResult.stolen_applied`**
- **Location:** `src/reward_materializer.py:33`
- **Status:** Computed and stored, but **never consumed**
- **Impact:** Design intent for stolen goods tracking is lost
- **Severity:** **MEDIUM** - Functional gap, not a crash

#### **Field: `PlayerState.salvage_modules`**
- **Location:** `src/player_state.py:38`
- **Status:** Populated by `combat_application.apply_combat_result()`, but **never consumed**
- **Impact:** Salvage modules accumulate indefinitely with no use
- **Severity:** **MEDIUM** - Functional gap, not a crash

---

## F) File-by-File Summary

### `src/game_engine.py`
- **Reward Trigger:** `_apply_conditional_rewards()` exists, called after encounter resolution
- **Reward Gating:** `_reward_qualifies()` exists but too permissive (doesn't check combat outcome)
- **Post-Combat Handler:** `_apply_post_combat_rewards_and_salvage()` **MISSING** (called but not defined)
- **Salvage Generation:** Called in `_execute_combat_action()` when enemy destroyed ✓
- **Capacity Calculation:** `_compute_ship_cargo_capacities()` exists but not used for validation

### `src/reward_materializer.py`
- **Status:** **FULLY COMPLIANT** with contract
- **Determinism:** ✓ Proper seed strategy
- **TR Multiplier:** ✓ Applied correctly
- **Stolen Behavior:** ✓ Computed correctly (but not consumed downstream)

### `src/reward_applicator.py`
- **Status:** **NON-COMPLIANT** (cargo overflow allowed)
- **Capacity Checks:** **MISSING**
- **Stolen Handling:** **MISSING** (ignores `stolen_applied`)

### `src/salvage_resolver.py`
- **Status:** **FULLY COMPLIANT** with contract
- **Determinism:** ✓ Proper RNG stream isolation
- **Mutation Rules:** ✓ Follows contract exactly

### `src/combat_application.py`
- **Status:** **PARTIALLY COMPLIANT**
- **Salvage Storage:** ✓ Appends to `player_state.salvage_modules`
- **Capacity Checks:** **MISSING** (modules don't consume cargo capacity)

### `src/npc_ship_generator.py`
- **Status:** **FULLY COMPLIANT** with contract
- **Determinism:** ✓ Proper RNG streams
- **NPC Parity:** ✓ Uses same hull/module catalogs as player

### `data/reward_profiles.json`
- **Status:** **CONTRACT-COMPLIANT**
- **Schema:** ✓ All required fields present
- **Stolen Behaviors:** ✓ Properly encoded

### `data/encounter_types.json`
- **Status:** **CONTRACT-COMPLIANT**
- **Reward Profiles:** ✓ Linked correctly to encounter subtypes
- **Default Flags:** ✓ `salvage_possible` flag present on relevant subtypes

---

## G) Priority Fixes

### **P0 (Critical - Game Breaking)**
1. **Implement `_apply_post_combat_rewards_and_salvage()`** - Currently dead code, will crash
2. **Add cargo capacity checks to `apply_materialized_reward()`** - Contract violation, breaks balance

### **P1 (High - Functional Gaps)**
3. **Enhance `_reward_qualifies()` to check combat outcome** - Rewards trigger incorrectly on escape
4. **Implement salvage module cargo conversion** - Modules stuck in limbo
5. **Connect stolen goods to law enforcement** - Design intent lost

### **P2 (Medium - UX Improvements)**
6. **Implement loot acceptance prompt** - No player agency
7. **Implement jettison mechanism** - No way to make room for loot
8. **Implement module installation path** - Salvage modules unusable

---

## H) Test Coverage Gaps

### **Missing Tests:**
1. Cargo capacity overflow during reward application
2. Salvage module cargo conversion
3. Stolen goods flag propagation to law enforcement
4. Reward gating based on combat outcome (destroyed vs escape)
5. Post-combat reward handler (function doesn't exist, can't be tested)

---

## End of Audit Report

**Next Steps:** Implement fixes in priority order (P0 → P1 → P2), ensuring contract compliance and deterministic behavior throughout.
