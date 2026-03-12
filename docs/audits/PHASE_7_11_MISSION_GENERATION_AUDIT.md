# Phase 7.11 — Mission Generation Authority Audit

## Executive Summary

**Current State:** Mission generation uses a hybrid approach with both legacy and modern components.

**Key Findings:**
- `mission_generator.py` is **ACTIVE** and used for weighted type selection
- Mission creation is split between `create_delivery_mission()` (structured) and `create_mission()` (legacy)
- Hardcoded mission type list exists in `game_engine.py`
- No centralized mission type registry exists
- Escort and recovery missions are declared but use legacy creation path

**Recommendation:** Consolidate to single authoritative mission creation path through `mission_factory.py` with a registry-based type selection system.

---

## Mission Creation Paths

### 1. Primary Path: `game_engine.py` → `_ensure_location_mission_offers()`

**File:** `src/game_engine.py`  
**Function:** `_ensure_location_mission_offers()` (line 1497)  
**Status:** ACTIVE - Primary mission generation entry point

**Flow:**
1. Checks `player_state.mission_offers_by_location` for existing offers
2. If no offers exist, generates new missions
3. Calls `_mission_candidates()` to get eligible mission types (line 1490)
4. Calls `select_weighted_mission_type()` from `mission_generator.py` (line 1556)
5. Routes to appropriate factory function:
   - `"delivery"` → `create_delivery_mission()` (structured, line 1567)
   - Other types → `create_mission()` (legacy, line 1582)

**Mission Type Selection:**
- Uses `select_weighted_mission_type()` from `mission_generator.py`
- Input: `_mission_candidates()` returns hardcoded list (line 1490-1495)
- Weighted selection with world_state_engine modifiers
- Fallback to `"delivery"` if selection returns None

**Uses mission_factory:** ✓ YES (both `create_delivery_mission()` and `create_mission()`)

**Registry/Hardcoded:** Hardcoded list in `_mission_candidates()` method

---

### 2. Mission Type Candidates (Hardcoded List)

**File:** `src/game_engine.py`  
**Function:** `_mission_candidates()` (line 1490)  
**Status:** ACTIVE - Hardcoded mission type definitions

**Hardcoded List:**
```python
[
    {"mission_type_id": "delivery", "base_weight": 1.0, "mission_tags": ["data"]},
    {"mission_type_id": "recovery", "base_weight": 1.0, "mission_tags": ["industrial"]},
    {"mission_type_id": "escort", "base_weight": 1.0, "mission_tags": ["essential"]},
]
```

**Issues:**
- Hardcoded in game_engine.py (not data-driven)
- No external registry or configuration file
- Tags are defined but not used in current implementation
- Base weights are all 1.0 (no differentiation)

---

### 3. Weighted Selection: `mission_generator.py`

**File:** `src/mission_generator.py`  
**Status:** ACTIVE - Used for mission type selection

**Functions:**
- `select_weighted_mission_type()` - Main entry point (line 5)
- `_compute_adjusted_weights()` - Applies world_state_engine modifiers (line 33)
- `_weighted_pick()` - Performs weighted random selection (line 76)
- `_mission_type_id()` - Extracts mission_type_id from dict (line 89)

**How It Works:**
1. Takes list of eligible missions (from `_mission_candidates()`)
2. Computes base weights from `base_weight` field
3. Applies world_state_engine modifiers (if provided)
4. Performs weighted random selection using RNG
5. Returns selected `mission_type_id` or None

**Uses RNG:** ✓ YES (weighted random selection)

**Determinism:** ✓ YES (uses seeded RNG from game_engine)

**Registry Integration:** Partial - can accept world_state_engine modifiers but no central registry

---

### 4. Delivery Mission Creation (Structured)

**File:** `src/mission_factory.py`  
**Function:** `create_delivery_mission()` (line 106)  
**Status:** ACTIVE - Modern structured creation

**Characteristics:**
- Fully structured schema (target, origin, source, objectives)
- Deterministic target selection (80% inter-system, 20% same-system)
- Uses reward_profile_id
- Sets payout_policy="auto", claim_scope="none"
- Sets reward_status="ungranted"

**Mission Type:** Hardcoded to `"delivery"` (line 246, 257)

**Uses Registry:** ✗ NO (hardcoded mission_type)

---

### 5. Legacy Mission Creation (Non-Delivery)

**File:** `src/mission_factory.py`  
**Function:** `create_mission()` (line 10)  
**Status:** ACTIVE - Used for non-delivery missions

**Characteristics:**
- Generic mission creation
- Accepts `mission_type` as parameter
- Uses legacy objective format: `[f"{mission_type_id}:complete_objective"]`
- Sets payout_policy="claim_required", claim_scope="source_entity" (default)
- Sets reward_status="ungranted"

**Mission Type:** Passed as parameter (not validated against registry)

**Used For:**
- `"recovery"` missions (line 1587 in game_engine.py)
- `"escort"` missions (line 1587 in game_engine.py)
- Any other non-delivery type

**Issues:**
- Legacy objective format (string-based)
- No validation that mission_type is valid
- No structured target/origin/source fields
- No reward_profile_id assignment

---

## Mission Type Usage Analysis

### Declared Mission Types

| Mission Type | Creation Path | Factory Function | Status |
|--------------|---------------|------------------|--------|
| `"delivery"` | Structured | `create_delivery_mission()` | ✅ Fully implemented |
| `"recovery"` | Legacy | `create_mission()` | ⚠️ Declared but not implemented |
| `"escort"` | Legacy | `create_mission()` | ⚠️ Declared but not implemented |
| `"bounty"` | Legacy | `create_mission()` | ⚠️ Referenced in tests only |
| `"victory:charter_of_authority"` | Direct | `MissionEntity()` | ⚠️ Special case (end game) |

### Mission Type Selection Logic

**Current Flow:**
```
_mission_candidates() [hardcoded list]
    ↓
select_weighted_mission_type() [mission_generator.py]
    ↓
Weighted selection with world_state_engine modifiers
    ↓
Returns mission_type_id or None
    ↓
If "delivery" → create_delivery_mission()
Else → create_mission(mission_type=mission_type_id)
```

**Issues:**
- No validation that selected type is valid
- No registry lookup
- Hardcoded fallback to "delivery"
- Escort/recovery declared but not fully implemented

---

## Legacy Components

### 1. `mission_generator.py`

**Status:** ACTIVE but should be consolidated

**Purpose:** Weighted mission type selection

**Issues:**
- Separate module for selection logic (should be in factory or registry)
- No direct integration with mission_factory
- Uses world_state_engine but no central registry

**Recommendation:** Move selection logic into mission_factory or new mission_registry module

---

### 2. Hardcoded Mission Candidates

**Location:** `src/game_engine.py` → `_mission_candidates()` (line 1490)

**Issues:**
- Hardcoded in game_engine (should be data-driven)
- Not easily extensible
- No external configuration

**Recommendation:** Move to mission registry or data file

---

### 3. Legacy `create_mission()` Function

**Location:** `src/mission_factory.py` → `create_mission()` (line 10)

**Issues:**
- Uses legacy objective format (string-based)
- No structured schema (target, origin, source)
- No reward_profile_id assignment
- Generic fallback for all non-delivery types

**Recommendation:** 
- Either implement structured creation for each type
- Or deprecate and require all types to have dedicated factory functions

---

## Bypass Analysis

### Direct MissionEntity Creation

**Found In:**
- `src/integration_test.py` (line 340, 510) - Test code
- `src/validate_payout_fields.py` - Validation tests

**Status:** Test code only, not production

**Impact:** None (test code is acceptable)

---

### Victory Missions

**Location:** `src/integration_test.py` (line 510)

**Type:** `"victory:charter_of_authority"`

**Creation:** Direct `MissionEntity()` instantiation

**Status:** Special case for end game evaluation

**Recommendation:** Keep as special case or add to registry as Tier 5 mission

---

## Static Mission Type Arrays

### Found Arrays:

1. **`_mission_candidates()` in `game_engine.py`** (line 1490)
   - Hardcoded list of 3 mission types
   - Includes base_weight and mission_tags
   - Used for weighted selection

2. **No other static arrays found**

---

## Weighted Selection Logic

### Current Implementation:

**File:** `src/mission_generator.py`

**Algorithm:**
1. Extract base weights from candidate list
2. Apply world_state_engine modifiers (if available)
3. Calculate adjusted weights: `base_weight * (1 + modifier_percent / 100)`
4. Perform weighted random selection
5. Return selected mission_type_id

**Determinism:** ✓ YES (uses seeded RNG)

**RNG Usage:** ✓ YES (weighted random selection)

**Registry Integration:** Partial (world_state_engine can modify weights)

---

## Mission Type Strings Not in Factory

### Declared but Not Implemented:

1. **`"recovery"`**
   - Declared in `_mission_candidates()` (line 1493)
   - Uses legacy `create_mission()` path
   - No dedicated factory function
   - No structured schema

2. **`"escort"`**
   - Declared in `_mission_candidates()` (line 1494)
   - Uses legacy `create_mission()` path
   - No dedicated factory function
   - No structured schema

3. **`"bounty"`**
   - Referenced in tests (integration_test.py line 466)
   - Uses legacy `create_mission()` path
   - No dedicated factory function
   - No structured schema
   - Comment in mission_manager.py: "Other mission types (bounty, etc.) - not implemented yet"

---

## Mission Generation Flow Map

```
┌─────────────────────────────────────────────────────────────┐
│ game_engine.py::_ensure_location_mission_offers()          │
│ - Entry point for mission generation                        │
│ - Checks player_state.mission_offers_by_location            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ game_engine.py::_mission_candidates()                        │
│ - Returns hardcoded list:                                    │
│   [delivery, recovery, escort]                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ mission_generator.py::select_weighted_mission_type()        │
│ - Applies world_state_engine modifiers                      │
│ - Performs weighted random selection                         │
│ - Returns mission_type_id or None                            │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ "delivery"       │    │ Other types     │
│                  │    │ (recovery,      │
│                  │    │  escort, etc.)  │
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ create_delivery_ │    │ create_mission()  │
│ mission()        │    │ (legacy)         │
│                  │    │                  │
│ - Structured     │    │ - Generic        │
│ - Full schema    │    │ - Legacy format  │
│ - reward_profile │    │ - No reward_     │
│   _id            │    │   profile_id     │
└──────────────────┘    └──────────────────┘
```

---

## Consolidation Plan (Recommendations)

### Phase 1: Create Mission Registry

**Action:** Create `src/mission_registry.py`

**Purpose:**
- Central registry of all mission types
- Data-driven mission type definitions
- Replace hardcoded `_mission_candidates()` list
- Support weighted selection with modifiers

**Structure:**
```python
@dataclass
class MissionTypeDefinition:
    mission_type_id: str
    base_weight: float
    mission_tags: List[str]
    factory_function: Callable
    reward_profile_id: str
    payout_policy: str
    claim_scope: str
```

**Data Source:** Move from hardcoded list to data file or registry class

---

### Phase 2: Consolidate Selection Logic

**Action:** Move `select_weighted_mission_type()` into `mission_registry.py` or `mission_factory.py`

**Purpose:**
- Single location for mission type selection
- Remove dependency on separate `mission_generator.py` module
- Integrate with registry

**Benefits:**
- Clearer code organization
- Easier to maintain
- Single source of truth

---

### Phase 3: Implement Structured Creation for All Types

**Action:** Create dedicated factory functions for recovery, escort, bounty

**Purpose:**
- Replace legacy `create_mission()` usage
- Ensure all missions use structured schema
- Consistent reward_profile_id assignment

**Functions Needed:**
- `create_recovery_mission()`
- `create_escort_mission()`
- `create_bounty_mission()`

**Or:** Refactor `create_mission()` to support structured schema for all types

---

### Phase 4: Remove Legacy Paths

**Action:** Deprecate or remove:
- Legacy `create_mission()` function (or refactor to structured)
- Hardcoded `_mission_candidates()` method
- Separate `mission_generator.py` module (consolidate into registry)

**Timing:** After all mission types have structured creation paths

---

## Answers to Specific Questions

### Q: Is mission_generator.py still active?

**A:** ✓ YES - It is actively used in `game_engine.py` line 1556 via `select_weighted_mission_type()`

---

### Q: Are there multiple mission creation authorities?

**A:** ✓ YES - Two paths:
1. **Structured:** `create_delivery_mission()` for delivery missions
2. **Legacy:** `create_mission()` for all other types

Both are called from the same location (`_ensure_location_mission_offers()`), but use different factory functions.

---

### Q: Where are escort and recovery missions being selected?

**A:** 
- **Selection:** `game_engine.py::_mission_candidates()` (hardcoded list) → `mission_generator.py::select_weighted_mission_type()` (weighted selection)
- **Creation:** `mission_factory.py::create_mission()` (legacy path, line 1582 in game_engine.py)

---

### Q: Does any path bypass mission_factory?

**A:** ✗ NO - All production mission creation goes through `mission_factory.py`:
- Delivery: `create_delivery_mission()`
- Others: `create_mission()`

**Exception:** Test code directly instantiates `MissionEntity()` (acceptable for tests)

---

## Summary

### Current Architecture

- **Selection Authority:** `mission_generator.py` (weighted selection)
- **Creation Authority:** `mission_factory.py` (two functions: structured and legacy)
- **Type Registry:** Hardcoded list in `game_engine.py::_mission_candidates()`
- **Determinism:** ✓ Preserved (seeded RNG)

### Issues Identified

1. ✅ `mission_generator.py` is active but should be consolidated
2. ✅ Hardcoded mission type list (not data-driven)
3. ✅ Two creation paths (structured vs legacy)
4. ✅ Escort/recovery declared but not fully implemented
5. ✅ No centralized mission type registry

### Recommended Consolidation

1. Create `mission_registry.py` with data-driven type definitions
2. Move selection logic into registry or factory
3. Implement structured creation for all mission types
4. Remove legacy paths after migration

### Determinism Status

✓ **Preserved** - All selection uses seeded RNG from `game_engine.py::_mission_rng_for_location()`

---

**Audit Complete**  
**Date:** Phase 7.11  
**Status:** Ready for consolidation planning
