# PHASE 7.8 – GAME ENGINE UNIFICATION AUDIT
## SHIPDOCK + CREW (BAR LOCATION)

**Status:** Audit Report Only (No Code Changes)  
**Date:** Phase 7.8  
**Scope:** Structural audit of Shipdock and Crew (Bar) systems against authoritative contracts

---

## A. AUTHORITY MAP

### A.1 Shipdock System

| Function/Component | Authority Delegation | Contract Reference |
|-------------------|---------------------|-------------------|
| `shipdock_inventory.generate_shipdock_inventory()` | Inventory generation only | `shipdock_inventory_contract.md` |
| `shipdock_inventory._eligible_modules()` | Module filtering (bans prototype/alien) | `shipdock_inventory_contract.md` Section 3 |
| `shipdock_inventory._eligible_hulls()` | Hull filtering (bans experimental/alien) | `shipdock_inventory_contract.md` Section 3 |
| `shipdock_inventory._resolved_weight_percents()` | World State modifier resolution | `world_state_contract.md` Section 13.4 (MODULES), 13.3 (SHIPS) |
| `interaction_resolvers.execute_buy_hull()` | Uses `assemble_ship()` for ship creation | `ship_entity_contract.md`, `ship_and_module_schema_contract.md` |
| `interaction_resolvers.execute_buy_module()` | Uses `assemble_ship()` for slot validation | `ship_and_module_schema_contract.md` |
| `interaction_resolvers.execute_sell_module()` | Applies resale multiplier (prototype/alien) | `interaction_layer_contract.md` Section 7.2 |
| `interaction_resolvers.execute_sell_hull()` | Base price * 0.5 (no resale multiplier) | `interaction_layer_contract.md` Section 7.1 |
| `game_engine._prepare_action_kwargs()` | Generates inventory via `generate_shipdock_inventory()` | `shipdock_inventory_contract.md` |
| `simulation_controller._execute_location_action()` | Generates inventory (duplicate path) | `shipdock_inventory_contract.md` |

**Pricing Authority:**
- **Hull/Module BUY pricing:** Uses `base_price_credits` from inventory directly (no delegation to `market_pricing.price_transaction()`)
- **Hull/Module SELL pricing:** Hardcoded 0.5 multiplier in `interaction_resolvers.py` (no delegation to pricing contract)
- **Resale multiplier:** Applied in `execute_sell_module()` for prototype/alien secondaries (contract-compliant)

**Assembler Authority:**
- ✅ `execute_buy_hull()` calls `assemble_ship()` for fuel capacity
- ✅ `execute_buy_module()` calls `assemble_ship()` for slot validation
- ✅ `execute_sell_module()` calls `assemble_ship()` for post-removal validation

### A.2 Crew (Bar Location) System

| Function/Component | Authority Delegation | Contract Reference |
|-------------------|---------------------|-------------------|
| `crew_generator.generate_hireable_crew()` | Crew pool generation | `crew_contract.md` Section 14 |
| `crew_generator._adjust_role_weights_with_world_state()` | World State modifier resolution | `world_state_contract.md` Section 13.5 (CREW) |
| `crew_generator._seed_from_parts()` | Deterministic seed generation | `crew_contract.md` Section 14 |
| `game_engine._execute_bar_hire_crew()` | **NOT IMPLEMENTED** (returns `not_implemented`) | `crew_contract.md` Section 10 |
| `game_engine._world_state_engine()` | Retrieves world_state_engine from time_engine | `world_state_contract.md` |

**Crew Generation Authority:**
- ✅ Uses deterministic seed: `hash(world_seed, system_id, "crew_pool")`
- ✅ Applies `hire_weight_delta` via world_state modifier resolution
- ❌ **Missing:** `wage_bias_percent` application (not found in generation path)
- ❌ **Missing:** Crew capacity enforcement (no check in `_execute_bar_hire_crew()`)
- ❌ **Missing:** Emoji profile construction (derived, not stored per contract)
- ❌ **Missing:** Persistence and relocation logic (Section 11)

**Modifier Aggregation:**
- ✅ `_adjust_role_weights_with_world_state()` resolves modifiers for "crew" domain
- ✅ Supports both `hire_weight_delta` and `crew_weight_percent` (compatibility)
- ❌ **Missing:** `wage_bias_percent` application to `daily_wage` calculation

---

## B. VIOLATIONS

### B.1 Contract Boundary Violations

#### B.1.1 Shipdock Pricing Violation
**Location:** `src/interaction_resolvers.py`  
**Violation:** Shipdock buy/sell pricing does NOT delegate to `market_pricing.price_transaction()`  
**Contract:** `market_pricing_contract.md` states pricing must be deterministic and explainable  
**Impact:** 
- Hull/module pricing bypasses market pricing contract
- No substitute discount application
- No tag-based interpretation
- No government price bias
- No world_state price_bias_percent application

**Evidence:**
- `execute_buy_hull()`: Uses `_inventory_hull_price()` (base_price_credits only)
- `execute_sell_hull()`: Uses `base_price_credits * 0.5` (hardcoded)
- `execute_buy_module()`: Uses `_inventory_module_price()` (base_price_credits only)
- `execute_sell_module()`: Uses `base_price_credits * 0.5 * resale_multiplier` (partial)

#### B.1.2 Crew Hiring Not Implemented
**Location:** `src/game_engine.py:894-900`  
**Violation:** `_execute_bar_hire_crew()` returns `{"ok": False, "reason": "not_implemented"}`  
**Contract:** `crew_contract.md` Section 10 requires hiring at `location_bar`  
**Impact:** Crew system is non-functional despite generation logic existing

#### B.1.3 Duplicate Shipdock Logic
**Location:** `src/game_engine.py` and `src/simulation_controller.py`  
**Violation:** Both files generate shipdock inventory independently  
**Evidence:**
- `game_engine.py:2890-2894`: Generates inventory in `_prepare_action_kwargs()`
- `simulation_controller.py:164-166`: Generates inventory in `_execute_location_action()`
**Impact:** Potential inconsistency if world_state_engine differs between paths

### B.2 Duplication of Assembler Logic

**Status:** ✅ **NO VIOLATION**  
- All shipdock operations correctly delegate to `assemble_ship()`
- No duplicate band/hull_max/capacity calculations found

### B.3 Duplication of Pricing Logic

**Status:** ⚠️ **PARTIAL VIOLATION**  
- Shipdock pricing uses hardcoded multipliers instead of `price_transaction()`
- Resale multiplier logic (prototype/alien) is correct but isolated
- No integration with market pricing contract's order of operations

### B.4 Duplication of Legality Logic

**Status:** ✅ **NO VIOLATION**  
- Shipdock does not handle legality (correctly deferred to other systems)
- Crew generation does not handle legality (correctly deferred)

---

## C. DETERMINISM RISKS

### C.1 RNG Stream Violations

#### C.1.1 Shipdock RNG Streams
**Status:** ✅ **COMPLIANT**  
- Uses isolated streams: `"shipdock_modules"` and `"shipdock_hulls"`
- Seed construction: `hash(world_seed, system_id, stream_name)`
- No cross-stream contamination observed

#### C.1.2 Crew RNG Streams
**Status:** ✅ **COMPLIANT**  
- Uses isolated stream: `"crew_pool"`
- Seed construction: `hash(world_seed, system_id, "crew_pool")`
- No cross-stream contamination observed

#### C.1.3 World State Modifier Resolution
**Status:** ✅ **COMPLIANT**  
- Both systems use `world_state_engine.resolve_modifiers_for_entities()`
- Deterministic aggregation per `world_state_contract.md` Section 20

### C.2 Non-Isolated Stream Usage

**Status:** ✅ **NO VIOLATIONS**  
- All RNG streams are properly isolated
- No shared state between generation calls

### C.3 Deterministic Caching

#### C.3.1 Shipdock Inventory Caching
**Status:** ⚠️ **POTENTIAL RISK**  
- `game_engine._prepare_action_kwargs()` generates inventory on-demand
- No explicit caching mechanism
- **Risk:** Multiple calls may regenerate (acceptable if deterministic, but inefficient)
- **Contract:** `shipdock_inventory_contract.md` requires deterministic output (met)

#### C.3.2 Crew Pool Caching
**Status:** ⚠️ **POTENTIAL RISK**  
- `generate_hireable_crew()` is called on-demand (when implemented)
- No explicit caching mechanism
- **Risk:** Multiple calls may regenerate (acceptable if deterministic, but inefficient)

---

## D. MISSING INTEGRATIONS

### D.1 World State Modifier Propagation

#### D.1.1 Shipdock World State Integration
**Status:** ✅ **PARTIALLY INTEGRATED**  
- ✅ `generate_shipdock_inventory()` accepts `world_state_engine` parameter
- ✅ Resolves modifiers for "modules" and "ships" domains
- ✅ Applies `availability_delta` and weight percent modifiers
- ❌ **Missing:** `price_bias_percent` application (pricing bypasses world_state)
- ⚠️ **Risk:** `game_engine._prepare_action_kwargs()` may not pass `world_state_engine`

**Evidence:**
- `shipdock_inventory.py:100`: Function signature includes `world_state_engine: Any | None = None`
- `shipdock_inventory.py:115-129`: `_resolved_weight_percents()` resolves modifiers
- `game_engine.py:2894`: Call does NOT pass `world_state_engine` parameter

#### D.1.2 Crew World State Integration
**Status:** ✅ **PARTIALLY INTEGRATED**  
- ✅ `generate_hireable_crew()` accepts `world_state_engine` parameter
- ✅ Resolves modifiers for "crew" domain
- ✅ Applies `hire_weight_delta` (via `crew_weight_percent`)
- ❌ **Missing:** `wage_bias_percent` application to `daily_wage`
- ❌ **Missing:** Integration in `game_engine._execute_bar_hire_crew()` (not implemented)

**Evidence:**
- `crew_generator.py:15`: Function signature includes `world_state_engine: Any | None = None`
- `crew_generator.py:77-110`: `_adjust_role_weights_with_world_state()` resolves modifiers
- `crew_generator.py:56`: `daily_wage` uses `role.get("base_daily_wage", 0)` (no world_state bias)

### D.2 Pricing Delegation

#### D.2.1 Shipdock Pricing Integration
**Status:** ❌ **NOT INTEGRATED**  
- Shipdock buy/sell operations do NOT use `market_pricing.price_transaction()`
- Pricing is hardcoded in `interaction_resolvers.py`
- **Missing:** Integration with market pricing contract

**Required Integration Points:**
- Hull buy: Should delegate to pricing contract (if applicable)
- Hull sell: Should apply resale multiplier via pricing contract
- Module buy: Should delegate to pricing contract (if applicable)
- Module sell: Should apply resale multiplier + pricing contract

### D.3 Crew Capacity Enforcement

**Status:** ❌ **NOT INTEGRATED**  
- `crew_contract.md` Section 8 requires `crew_capacity` enforcement
- No capacity check found in `_execute_bar_hire_crew()` (not implemented)
- **Missing:** ShipEntity crew_capacity field validation
- **Missing:** Blocking logic when capacity full

### D.4 Emoji Profile Construction

**Status:** ❌ **NOT INTEGRATED**  
- `crew_contract.md` Section 6 requires emoji profile construction
- `emoji_profile_contract.md` requires derived (not stored) profiles
- **Missing:** Emoji profile construction in crew generation/hiring path
- **Missing:** Integration with emoji.json resolution

### D.5 Crew Persistence and Relocation

**Status:** ❌ **NOT INTEGRATED**  
- `crew_contract.md` Section 11 requires relocation algorithm
- **Missing:** Relocation logic for dismissed crew
- **Missing:** Nearest system with location_bar selection
- **Missing:** `current_location_id` update on dismissal

### D.6 Wage System Integration

**Status:** ❌ **NOT INTEGRATED**  
- `crew_contract.md` Section 9 requires wage deduction at day advancement
- **Missing:** TimeEngine day advancement hook for wage deduction
- **Missing:** Insufficient funds blocking logic
- **Missing:** `wage_bias_percent` application from world_state modifiers

---

## E. EXPLICIT TODO LIST

### E.1 Shipdock System

#### E.1.1 Pricing Integration (HIGH PRIORITY)
- [ ] **TODO:** Integrate `market_pricing.price_transaction()` for shipdock buy/sell operations
- [ ] **TODO:** Apply world_state `price_bias_percent` modifiers to hull/module pricing
- [ ] **TODO:** Ensure pricing contract order of operations is followed
- [ ] **TODO:** Add pricing delegation for hull buy (if market pricing applies)
- [ ] **TODO:** Add pricing delegation for module buy (if market pricing applies)
- [ ] **TODO:** Verify resale multiplier application aligns with pricing contract

#### E.1.2 World State Engine Propagation (MEDIUM PRIORITY)
- [ ] **TODO:** Pass `world_state_engine` parameter in `game_engine._prepare_action_kwargs()` when calling `generate_shipdock_inventory()`
- [ ] **TODO:** Verify `simulation_controller` passes `world_state_engine` (if available)
- [ ] **TODO:** Ensure world_state modifier resolution is consistent across both paths

#### E.1.3 Duplicate Logic Elimination (LOW PRIORITY)
- [ ] **TODO:** Consolidate shipdock inventory generation to single authoritative path
- [ ] **TODO:** Remove duplicate generation in `simulation_controller.py` if `game_engine` is authoritative

### E.2 Crew (Bar Location) System

#### E.2.1 Core Implementation (HIGH PRIORITY)
- [ ] **TODO:** Implement `game_engine._execute_bar_hire_crew()` (currently returns `not_implemented`)
- [ ] **TODO:** Integrate `crew_generator.generate_hireable_crew()` into hiring flow
- [ ] **TODO:** Add crew capacity enforcement (check `ship.crew_capacity` vs `len(ship.crew_slots)`)
- [ ] **TODO:** Implement crew assignment to ship on hire
- [ ] **TODO:** Deduct `hiring_cost` from player credits
- [ ] **TODO:** Create crew entity (NPCEntity Tier 2) with proper structure

#### E.2.2 Emoji Profile Construction (HIGH PRIORITY)
- [ ] **TODO:** Construct emoji profile per `emoji_profile_contract.md` Section 3
- [ ] **TODO:** Integrate with `emoji.json` resolution
- [ ] **TODO:** Apply deterministic ordering (role emoji + tier emoji + sorted tag emojis)
- [ ] **TODO:** Ensure profile is derived (not stored) per contract

#### E.2.3 World State Modifier Application (MEDIUM PRIORITY)
- [ ] **TODO:** Apply `wage_bias_percent` from world_state modifiers to `daily_wage` calculation
- [ ] **TODO:** Ensure `hire_weight_delta` is applied in hiring flow (already in generation)
- [ ] **TODO:** Pass `world_state_engine` to `generate_hireable_crew()` in hiring flow

#### E.2.4 Wage System Integration (MEDIUM PRIORITY)
- [ ] **TODO:** Implement wage deduction at TimeEngine day advancement
- [ ] **TODO:** Add insufficient funds blocking logic (prevent time advancement)
- [ ] **TODO:** Calculate total `wage_per_day` from all assigned crew
- [ ] **TODO:** Apply `wage_bias_percent` modifiers when calculating wages

#### E.2.5 Persistence and Relocation (MEDIUM PRIORITY)
- [ ] **TODO:** Implement crew dismissal logic
- [ ] **TODO:** Implement relocation algorithm (nearest system with location_bar)
- [ ] **TODO:** Update `crew.current_location_id` on dismissal
- [ ] **TODO:** Set `assigned_ship_id = null` on dismissal
- [ ] **TODO:** Ensure relocation does not consume time

#### E.2.6 Crew Capacity Enforcement (HIGH PRIORITY)
- [ ] **TODO:** Verify ShipEntity has `crew_capacity` field
- [ ] **TODO:** Verify ShipEntity has `crew_slots` list field
- [ ] **TODO:** Add capacity check before hiring: `len(ship.crew_slots) < ship.crew_capacity`
- [ ] **TODO:** Block hiring if capacity full

### E.3 Engine Integration

#### E.3.1 Game Engine Orchestration (MEDIUM PRIORITY)
- [ ] **TODO:** Ensure `game_engine.py` is authoritative for shipdock operations
- [ ] **TODO:** Remove or deprecate `simulation_controller` shipdock path if redundant
- [ ] **TODO:** Verify all shipdock actions route through `game_engine` orchestration

#### E.3.2 Simulation Controller Authority (LOW PRIORITY)
- [ ] **TODO:** Clarify `simulation_controller` role vs `game_engine` role
- [ ] **TODO:** Ensure no duplicate logic between controllers
- [ ] **TODO:** Document which controller is authoritative for which operations

### E.4 Contract Compliance Verification

#### E.4.1 Shipdock Contract Compliance (HIGH PRIORITY)
- [ ] **TODO:** Verify all shipdock operations comply with `shipdock_inventory_contract.md`
- [ ] **TODO:** Verify pricing complies with `market_pricing_contract.md` (currently violated)
- [ ] **TODO:** Verify assembler authority is never duplicated
- [ ] **TODO:** Verify deterministic caching requirements are met

#### E.4.2 Crew Contract Compliance (HIGH PRIORITY)
- [ ] **TODO:** Verify all crew operations comply with `crew_contract.md`
- [ ] **TODO:** Verify emoji profile construction complies with `emoji_profile_contract.md`
- [ ] **TODO:** Verify world_state modifier application complies with `world_state_contract.md`
- [ ] **TODO:** Verify wage system complies with `time_engine_contract.md` (if applicable)

---

## SUMMARY

### Contract Compliance Status

| System | Overall Status | Critical Issues |
|--------|---------------|----------------|
| **Shipdock** | ⚠️ **PARTIAL** | Pricing not delegated to contract; world_state_engine not always passed |
| **Crew (Bar)** | ❌ **INCOMPLETE** | Core hiring not implemented; wage system not integrated; emoji profiles missing |

### Critical Path Items

1. **Shipdock Pricing Integration** - Must delegate to `market_pricing.price_transaction()`
2. **Crew Hiring Implementation** - `_execute_bar_hire_crew()` must be fully implemented
3. **Crew Capacity Enforcement** - Must check capacity before hiring
4. **Emoji Profile Construction** - Must construct derived profiles per contract
5. **Wage System Integration** - Must deduct wages at day advancement
6. **World State Propagation** - Must pass `world_state_engine` consistently

### Determinism Status

✅ **COMPLIANT** - All RNG streams are properly isolated and deterministic.  
⚠️ **RISK** - Caching not implemented (acceptable but inefficient).

---

**END OF AUDIT REPORT**
