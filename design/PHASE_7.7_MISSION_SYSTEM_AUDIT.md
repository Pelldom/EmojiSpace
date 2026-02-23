# Phase 7.7 - Mission System Engine Baseline Audit

**Date:** 2024-12-19  
**Status:** Inspection-Only (No Code Modifications)  
**Purpose:** Pre-implementation audit for Mission integration across Bar, Administration, and DataNet

---

## 1. Mission System

### 1.1 Mission Generation Centralization

**Answer:** Location-based generation with centralized components

**File:** `src/game_engine.py`

**Implementation Details:**
- Mission generation is **location-scoped** via `_ensure_location_mission_offers(location_id: str)`
- Generation occurs lazily on first `mission_list` or `mission_accept` for a location
- Uses `_location_offered_mission_ids: dict[str, list[str]]` to cache per-location offers
- Generation is **NOT** centralized globally; each location generates independently

**Lines:** 591-620 (`_ensure_location_mission_offers`)

---

### 1.2 Mission Generation Implementation Location

**Answer:** Implemented in `GameEngine` class

**Files:**
- `src/game_engine.py` (lines 576-638)
  - `_mission_rng_for_location()` - deterministic RNG per location
  - `_mission_candidates()` - hardcoded candidate list
  - `_ensure_location_mission_offers()` - lazy generation logic
  - `_mission_rows_for_location()` - row formatting for display
- `src/mission_generator.py` - weighted selection utility
- `src/mission_factory.py` - mission entity creation

---

### 1.3 Mission Tier Distribution Enforcement

**Answer:** **PARTIALLY IMPLEMENTED**

**Current Behavior:**
- Tier selection: `mission_tier=1 + int(rng.randint(0, 2))` (lines 612)
- Generates tiers 1, 2, or 3 only
- **No explicit tier distribution rules**
- **No tier limits by location type**
- **No tier gating logic**

**Missing:**
- Tier 4-5 generation logic
- Tier distribution weighting
- Location-based tier limits (e.g., Bar: 1-3, Administration: 2-4, DataNet: 3-5)

**File:** `src/game_engine.py:612`

---

### 1.4 Population Reference

**Answer:** **NO**

**Evidence:**
- `_mission_rng_for_location()` uses: `world_seed`, `system_id`, `destination_id`, `location_id`
- `_mission_candidates()` returns hardcoded list with no population input
- `select_weighted_mission_type()` accepts `system_id` but does not use population
- No population parameter passed to mission creation

**Files:**
- `src/game_engine.py:576-589`
- `src/mission_generator.py:5-31`

---

### 1.5 Government Reference

**Answer:** **NO**

**Evidence:**
- Mission generation does not reference `system.government_id`
- `create_mission()` does not accept government parameter
- No government-based mission filtering or weighting

**Files:**
- `src/game_engine.py:606-616`
- `src/mission_factory.py:7-42`

---

### 1.6 World State Mission Domain Modifiers

**Answer:** **PARTIALLY IMPLEMENTED**

**Current Behavior:**
- `select_weighted_mission_type()` accepts `world_state_engine` and `system_id` (line 602)
- Calls `world_state_engine.resolve_modifiers_for_entities(domain="missions", ...)` (line 58-62 in `mission_generator.py`)
- Applies `mission_weight_percent` modifier to base weights (line 71)
- **Modifier application exists but is optional** (falls back to base weights if `world_state_engine` is `None`)

**Missing:**
- No explicit logging of modifier application
- No validation that modifiers are applied correctly
- No contract verification that modifier caps are enforced

**Files:**
- `src/mission_generator.py:33-73`
- `src/world_state_engine.py:51-52` (defines missions domain caps)

---

### 1.7 Deterministic RNG Streams

**Answer:** **YES**

**Implementation:**
- `_mission_rng_for_location()` creates deterministic `random.Random` from:
  - `world_seed`
  - `system_id`
  - `destination_id`
  - `location_id`
- Seed calculation: `(seed_value * 31 + ord(char)) % (2**32)` per character
- Used for: offer count (1-3), tier selection (1-3), mission type selection

**File:** `src/game_engine.py:576-582`

---

### 1.8 Mission Tier Storage and Validation

**Answer:** **STORED, NOT VALIDATED**

**Storage:**
- `MissionEntity.mission_tier: int` (line 47 in `mission_entity.py`)
- Validated at creation: `if mission_tier < 1 or mission_tier > 5: raise ValueError` (line 60 in `mission_factory.py`)

**Validation:**
- Creation-time validation exists
- **No runtime tier validation**
- **No tier-based filtering at offer/accept time**
- **No tier-based gating by location type**

**Files:**
- `src/mission_entity.py:47`
- `src/mission_factory.py:60`

---

### 1.9 Missions Bound to NPCEntity Instances

**Answer:** **NOT IMPLEMENTED**

**Current State:**
- `MissionEntity` has fields: `mission_giver_npc_id: str | None`, `target_npc_id: str | None` (lines 56-57 in `mission_entity.py`)
- **Current generation path does NOT set these fields**
- `create_mission()` called with `source_type="system"` and `source_id=f"{location_id}:{index}"` (line 607)
- **No NPC binding logic in generation**

**Evidence:**
- `_ensure_location_mission_offers()` does not resolve NPCs
- No `npc_id` passed to `create_mission()`
- Bar/Administration NPCs exist (Tier 3 bartender/administrator) but are not linked to missions

**Files:**
- `src/mission_entity.py:56-57`
- `src/game_engine.py:606-616`

---

### 1.10 Mission Storage Location

**Answer:** **MissionManager (Runtime Registry)**

**Storage:**
- `GameEngine._mission_manager: MissionManager` (line 157)
- `MissionManager.missions: Dict[str, MissionEntity]` (line 16 in `mission_manager.py`)
- `PlayerState.active_missions: List[str]` - stores mission IDs only (line 43 in `player_state.py`)
- `PlayerState.completed_missions: List[str]` (line 44)
- `PlayerState.failed_missions: List[str]` (line 45)

**Persistence:**
- `MissionManager.to_dict()` / `from_dict()` exist (lines 91-106 in `mission_manager.py`)
- **Not stored in PlayerState directly**
- **Not stored in save/load system** (no evidence of serialization in game_engine)

**Files:**
- `src/mission_manager.py:15-16`
- `src/player_state.py:43-45`
- `src/game_engine.py:157`

---

### 1.11 Legality Checks Applied

**Answer:** **NOT IMPLEMENTED**

**Current State:**
- No legality checks at generation time
- No legality checks at acceptance time
- No legality checks at resolution time
- No government-based mission filtering

**Missing:**
- No `legality_state` field on `MissionEntity`
- No government policy evaluation for missions
- No filtering of illegal missions by location type

**Files:**
- `src/mission_entity.py` (no legality fields)
- `src/game_engine.py:655-679` (`_execute_mission_accept` - no legality checks)

---

### 1.12 Mission Emoji Profiles

**Answer:** **FIELD EXISTS, NOT IMPLEMENTED**

**Current State:**
- `MissionEntity.emoji: str | None` field exists (line 33 in `mission_entity.py`)
- **Not set during generation** (line 606-616 in `game_engine.py`)
- **No emoji profile construction logic**
- **No tier emoji display** (mission_tier exists but no tier emoji)

**Contract Compliance:**
- `emoji_profile_contract.md` requires emoji profiles for tiered entities
- Missions are tiered (1-5) but do not implement emoji profile construction
- No reference to `emoji.json` for mission emoji resolution

**Files:**
- `src/mission_entity.py:33, 47`
- `src/game_engine.py:606-616` (emoji not set)

---

## 2. Bar Location

### 2.1 Bar Implementation

**Answer:** **IMPLEMENTED**

**File:** `src/game_engine.py`

**Location Type Handling:**
- `location_type == "bar"` recognized (line 1969, 2045)
- Action IDs: `["bar_talk", "bar_rumors", "mission_list", "mission_accept", "bar_hire_crew"]` (line 1970, 2046)

**Lines:** 1969-1970, 2045-2046, 681-706

---

### 2.2 Bar NPC Generation Determinism

**Answer:** **YES**

**Implementation:**
- `resolve_npcs_for_location()` called on `enter_location` for `bar` type (line 2217 in `game_engine.py`)
- Uses `_deterministic_npc_id(location_id, "bartender")` (line 20 in `npc_placement.py`)
- ID generation: `md5(f"{location_id}:{role}")` -> `NPC-<8 hex>` (line 38-40)
- **Bartender created as Tier 3** (line 25 in `npc_placement.py`)

**File:** `src/npc_placement.py:17-35`

---

### 2.3 Bar Mission Generation Call

**Answer:** **YES (Indirect)**

**Current Behavior:**
- `mission_list` action available at bar (line 1970, 2046)
- `_execute_mission_list()` calls `_mission_rows_for_location()` (line 647)
- `_mission_rows_for_location()` calls `_ensure_location_mission_offers()` (line 623)
- **Generation occurs on-demand when mission_list is called**

**File:** `src/game_engine.py:640-653, 622-638`

---

### 2.4 Bar Mission Attachment Logic

**Answer:** **NOT IMPLEMENTED**

**Current State:**
- Missions generated with `source_type="system"` and `source_id=f"{location_id}:{index}"` (line 607-608)
- **No `mission_giver_npc_id` set**
- **No binding to bartender NPC**
- Bartender exists but is not linked to missions

**Files:**
- `src/game_engine.py:606-616`

---

### 2.5 Bar Crew Hiring Logic

**Answer:** **STUB ONLY**

**Implementation:**
- `bar_hire_crew` action exists (line 1970, 2046)
- `_execute_bar_hire_crew()` returns `{"ok": False, "reason": "not_implemented"}` (line 700-705)
- **No actual crew hiring implementation**

**File:** `src/game_engine.py:700-705`

---

### 2.6 Bar Government Legality Respect

**Answer:** **NO**

**Current State:**
- No government checks in mission generation
- No government checks in mission listing
- No government checks in mission acceptance
- No filtering of illegal missions

**Files:**
- `src/game_engine.py:591-679` (no government references)

---

## 3. Administration Location

### 3.1 Mission Board Implementation

**Answer:** **PARTIALLY IMPLEMENTED**

**Current State:**
- `location_type == "administration"` recognized (line 1971, 2047)
- Actions include: `["admin_talk", "admin_pay_fines", "admin_apply_license", "admin_turn_in", "mission_list", "mission_accept"]` (line 1972-1978, 2048)
- **No explicit "Mission Board" concept**
- **No separate mission board filtering logic**
- Uses same `_ensure_location_mission_offers()` as bar

**File:** `src/game_engine.py:1971-1978, 2047-2048`

---

### 3.2 Administration Legality Filtering

**Answer:** **NO**

**Current State:**
- No legality checks in mission generation
- No legality checks in mission listing
- No government-based filtering
- All missions generated identically regardless of location type

**Files:**
- `src/game_engine.py:591-620` (no location_type-specific logic)

---

### 3.3 Administration Tier Limits (1-4)

**Answer:** **NOT IMPLEMENTED**

**Current State:**
- Tier selection: `1 + int(rng.randint(0, 2))` (tiers 1-3 only)
- **No location-specific tier limits**
- **No tier 4 generation**
- **No tier filtering by location type**

**File:** `src/game_engine.py:612`

---

### 3.4 Administration Sanctioning Logic

**Answer:** **NOT IMPLEMENTED**

**Current State:**
- No sanctioning concept
- No government-based mission approval
- No license/permit checks
- `admin_apply_license` action exists but returns `{"ok": False, "reason": "not_implemented"}` (line 725-730)

**Files:**
- `src/game_engine.py:725-730`

---

## 4. DataNet

### 4.1 DataNet Mission Listing Support

**Answer:** **PARTIALLY IMPLEMENTED**

**Current State:**
- `_build_datanet_profile()` extracts `available_missions` from `destination_detail.get("active_missions", [])` (line 894-896)
- **`active_missions` refers to player's active missions, not available offers**
- **No mission generation for DataNet location**
- **No mission listing action for DataNet**

**Evidence:**
- `location_type == "datanet"` returns empty action set (line 2037-2038)
- `_allowed_action_ids_for_location_type("datanet")` returns `set()` (line 2038)
- CLI shows missions from `destination_profile.active_missions` (player's active missions, not offers)

**Files:**
- `src/game_engine.py:2037-2038`
- `src/run_game_engine_cli.py:874-912`

---

### 4.2 DataNet Tier 4-5 Gating

**Answer:** **NOT IMPLEMENTED**

**Current State:**
- No DataNet-specific mission generation
- No tier 4-5 generation logic exists
- No tier gating by location type

**Files:**
- `src/game_engine.py:591-620` (no DataNet-specific logic)

---

### 4.3 DataNet Special Circumstance Logic

**Answer:** **NOT IMPLEMENTED**

**Current State:**
- No special circumstance detection
- No world state integration for DataNet missions
- No event-driven mission generation
- No crisis/opportunity mission logic

**Files:**
- `src/game_engine.py` (no DataNet mission generation)

---

## 5. Interaction Layer

### 5.1 Mission Acceptance Support

**Answer:** **YES**

**Implementation:**
- `mission_accept` action exists (line 1970, 1978, 2046, 2048)
- `_execute_mission_accept()` calls `MissionManager.accept()` (line 666-671)
- Routes through interaction layer via `_execute_location_action()` (line 796-797)

**File:** `src/game_engine.py:655-679, 796-797`

---

### 5.2 Mission Offer Logging

**Answer:** **PARTIALLY IMPLEMENTED**

**Current State:**
- `MissionManager.offer()` calls `_log_manager(logger, turn, "offer", mission_id)` (line 23 in `mission_manager.py`)
- `_log_manager()` logs: `f"{action} mission_id={mission_id}{detail_text}"` (line 128)
- **No logging of:**
  - Mission modifiers applied
  - Tier selection rationale
  - Location-specific generation parameters
  - World state modifier values

**Files:**
- `src/mission_manager.py:19-23, 124-128`
- `src/mission_factory.py:78-96` (logs creation but not modifiers)

---

### 5.3 Deterministic State Transitions

**Answer:** **YES**

**Implementation:**
- Mission state transitions: `OFFERED -> ACTIVE -> RESOLVED` (lines 41, 53, 71 in `mission_manager.py`)
- State changes are explicit and logged
- No non-deterministic transitions

**File:** `src/mission_manager.py:25-89`

---

## 6. Logging

### 6.1 Mission Spawn Decision Reconstruction

**Answer:** **PARTIALLY IMPLEMENTED**

**Current Logging:**
- Mission creation logged: `mission_create mission_id=... source_type=... system_id=...` (line 89-95 in `mission_factory.py`)
- Mission offer logged: `offer mission_id=...` (line 128 in `mission_manager.py`)
- **Missing:**
  - RNG seed values used
  - Offer count selection
  - Tier selection rationale
  - Mission type selection weights
  - World state modifier values applied

**Files:**
- `src/mission_factory.py:78-96`
- `src/mission_manager.py:124-128`

---

### 6.2 Mission Modifier Logging

**Answer:** **NO**

**Current State:**
- `select_weighted_mission_type()` returns `adjusted_weights` dict (line 30 in `mission_generator.py`)
- **Not logged**
- **No logging of world state modifier application**
- **No logging of final weights used for selection**

**Files:**
- `src/mission_generator.py:33-73` (no logging)

---

### 6.3 Mission Legality Decision Logging

**Answer:** **NOT APPLICABLE (No Legality Checks)**

**Current State:**
- No legality checks exist
- No legality decision logging

---

## 7. Missing Systems

### 7.1 Not Implemented

1. **NPC-Mission Binding**
   - Missions do not bind to `mission_giver_npc_id`
   - Bar/Administration NPCs exist but are not linked to missions

2. **Legality System for Missions**
   - No government-based mission filtering
   - No legality checks at generation/acceptance/resolution

3. **Tier Distribution Rules**
   - No location-based tier limits
   - No tier 4-5 generation
   - No tier weighting by location type

4. **Population-Based Mission Generation**
   - Population not referenced in generation
   - No population-based mission variety scaling

5. **Government-Based Mission Generation**
   - Government not referenced in generation
   - No government-specific mission types

6. **DataNet Mission Generation**
   - No DataNet-specific mission generation
   - No tier 4-5 gating
   - No special circumstance logic

7. **Administration Mission Board**
   - No explicit mission board concept
   - No sanctioning logic
   - No tier 1-4 filtering

8. **Mission Emoji Profiles**
   - Emoji field exists but not set
   - No emoji profile construction
   - No tier emoji display

9. **Crew Hiring at Bar**
   - Stub only (`not_implemented`)

10. **License Application at Administration**
    - Stub only (`not_implemented`)

---

### 7.2 Partially Implemented

1. **World State Modifier Integration**
   - Modifier resolution exists but is optional
   - No logging of modifier application
   - No validation of modifier caps

2. **Mission Generation**
   - Basic generation exists but lacks:
    - Location-specific rules
    - Tier distribution
    - NPC binding
    - Legality filtering

3. **Mission Tier System**
   - Tiers stored and validated at creation
   - No tier-based filtering or gating
   - Only tiers 1-3 generated

4. **DataNet Mission Display**
   - Shows player's active missions
   - Does not show available mission offers
   - No DataNet-specific generation

---

### 7.3 Implemented but Non-Compliant with Contract

1. **Mission Generation Location**
   - Contract: Should support location-based and NPC-based generation
   - Current: Only location-based, no NPC binding

2. **Mission Tier Distribution**
   - Contract: Tiers 1-5, location-specific distributions
   - Current: Only tiers 1-3, no location-specific rules

3. **Mission Emoji Profiles**
   - Contract: Required for tiered entities
   - Current: Field exists but not implemented

4. **Bar Mission Source**
   - Contract: Bar missions should bind to bartender NPC
   - Current: Uses `source_type="system"`, no NPC binding

5. **Administration Mission Board**
   - Contract: Should filter by legality and tier (1-4)
   - Current: No filtering, uses same generation as bar

6. **DataNet Missions**
   - Contract: Tier 4-5, special circumstances
   - Current: No DataNet mission generation

---

## Summary

### Mission System Status

**Core Infrastructure:** ✅ Implemented
- Mission entity structure
- Mission manager (offer/accept/complete/fail/abandon)
- Location-based lazy generation
- Deterministic RNG streams

**Missing Critical Features:**
- NPC-mission binding
- Legality system integration
- Tier distribution rules (1-5, location-specific)
- Population/government integration
- DataNet mission generation
- Mission emoji profiles
- Administration mission board filtering

**Partially Implemented:**
- World state modifier integration (exists but optional, not logged)
- Tier system (stored but not used for filtering/gating)

### Bar Location Status

**Implemented:** ✅
- Location type recognition
- NPC generation (Tier 3 bartender)
- Mission list/accept actions
- Deterministic NPC placement

**Missing:**
- Mission-NPC binding
- Government legality filtering
- Crew hiring (stub only)

### Administration Location Status

**Implemented:** ✅
- Location type recognition
- NPC generation (Tier 3 administrator)
- Mission list/accept actions
- Pay fines / turn in actions

**Missing:**
- Mission board concept
- Legality filtering
- Tier 1-4 limits
- Sanctioning logic
- License application (stub only)

### DataNet Status

**Implemented:** ✅
- Location type recognition
- Profile display (situations, notices)

**Missing:**
- Mission generation
- Mission listing action
- Tier 4-5 gating
- Special circumstance logic

### Interaction Layer Status

**Implemented:** ✅
- Mission acceptance routing
- State transition logging

**Missing:**
- Comprehensive modifier logging
- Legality decision logging

### Logging Status

**Implemented:** ✅
- Basic mission creation/offer/accept logging

**Missing:**
- RNG seed logging
- Modifier application logging
- Tier selection rationale
- World state modifier values

---

## File Reference Summary

**Mission System Core:**
- `src/mission_entity.py` - Entity structure
- `src/mission_manager.py` - State management
- `src/mission_factory.py` - Creation logic
- `src/mission_generator.py` - Weighted selection

**Game Engine Integration:**
- `src/game_engine.py:576-679` - Mission generation and execution

**NPC Integration:**
- `src/npc_placement.py` - Bar/Administration NPC creation

**World State Integration:**
- `src/world_state_engine.py:51-52` - Missions domain modifier caps

**CLI Display:**
- `src/run_game_engine_cli.py:874-912` - DataNet profile building

---

**End of Audit Report**
