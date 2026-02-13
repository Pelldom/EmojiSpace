# EmojiSpace - Player Entity Contract

Status: EVOLVING (NOT LOCKED)
Phase: 2.8 / 3 (Foundation)
Target Version: 0.4.x
Location: /design/pe_contract.md

This document defines the authoritative structure of the Player Entity (PE).

The Player Entity represents the persistent state of the player across
all systems. It is a central integration point for economy, law,
locations, missions, and end goals.

This contract is expected to evolve incrementally as new systems come
online. All changes must be explicit and versioned.

----------------------------------------------------------------

## 1. Purpose

The Player Entity:

- Tracks all persistent player state
- Acts as a state holder, not a rules engine
- Is consumed by other systems but does not control them
- Must be fully serializable and deterministic

The Player Entity does NOT:
- Resolve combat
- Calculate prices
- Determine legality
- Enforce laws
- Advance time
- Generate narrative meaning

----------------------------------------------------------------

## 2. Core Identity (Mandatory)

The Player Entity MUST define:

- player_id (string, immutable)
- display_name (string)
- current_system_id (string)
- current_location_id (string or null)

----------------------------------------------------------------

## 3. Financial State

The Player Entity MUST track:

- credits (integer, >= 0 unless bankrupt)
- outstanding_fines (map by system_id)

Rules:
- Credits are modified only by authorized systems
- Bankruptcy rules are defined in end_goals.md

----------------------------------------------------------------

## 4. Reputation and Legal State

Tracked per system.

### 4.1 Reputation

- reputation_by_system (map: system_id -> score)

Reputation is interpreted by other systems but stored here.

### 4.2 Heat

- heat_by_system (map: system_id -> value)

Heat represents short-term enforcement attention.

### 4.3 Warrants

- warrants_by_system (map: system_id -> warrant records)

Warrants are issued by enforcement and persist until resolved.

----------------------------------------------------------------

## 5. Arrest and Custody State

The Player Entity MUST track:

- arrest_state (enum: free, detained_tier_1, detained_tier_2)

Rules:
- Tier 2 detention is a hard loss condition
- Resolution is handled by Law Enforcement

----------------------------------------------------------------

## 6. Ships and Assets

### 6.1 Active Ship

- active_ship_id (entity_id)

Exactly one ship is active at a time.

### 6.2 Owned Ships

- owned_ship_ids (list of entity_id)

Ships may be:
- active
- idle
- seized
- destroyed

Ship state is stored on the Ship Entity but referenced here.

----------------------------------------------------------------

## 7. Cargo and Stored Goods

The Player Entity MUST reference:

- cargo_by_ship (map: ship_id -> cargo manifest)
- stored_goods (map: storage_location_id -> goods manifest)

Rules:
- Goods legality is resolved elsewhere
- Storage risk is resolved elsewhere

----------------------------------------------------------------

## 8. Warehouse Leases

The Player Entity MUST track warehouse access explicitly.

- warehouse_leases (list of lease records)

Each lease record includes:
- warehouse_entity_id
- system_id
- capacity
- recurring_cost
- start_turn
- status (active, expired, revoked)

Rules:
- Lease cost deduction is handled by future systems
- Loss of lease does not auto-delete goods

----------------------------------------------------------------

## 9. Financial Instruments

### 9.1 Loans

- loans (list of loan records)

Each loan record includes:
- issuing_system_id
- principal
- interest_rate
- start_turn
- repayment_state
- status (active, defaulted, repaid)

Rules:
- Loan enforcement is handled by future systems

### 9.2 Insurance Policies

- insurance_policies (list of policy records)

Each policy record includes:
- policy_type (cargo, ship)
- covered_asset_ids
- issuing_system_id
- start_turn
- end_turn
- status (active, expired, claimed)

Rules:
- Claims are resolved by future systems

----------------------------------------------------------------

## 10. Missions

The Player Entity MUST track mission state.

- active_missions (list of mission_id)
- completed_missions (list of mission_id)
- failed_missions (list of mission_id)

Mission meaning and rewards are resolved elsewhere.

----------------------------------------------------------------

## 11. Player History

The Player Entity MUST track curated historical records used for
endgame scoring, achievements, and legacy evaluation.

History represents summarized facts, not raw logs.

### 11.1 Historical Counters

The Player Entity MAY track cumulative counters, including but not limited to:

- total_credits_earned
- total_credits_lost
- total_trades_completed
- total_missions_completed
- total_missions_failed
- total_ships_owned
- total_ships_lost
- total_arrests
- total_inspections_submitted
- total_inspections_fled
- total_inspections_bribed
- total_inspections_attacked

Rules:
- Counters are monotonically increasing
- Counters are never decremented
- Counters are updated only by authorized systems

### 11.2 Milestones and Firsts

The Player Entity MAY track milestone flags, including:

- first_arrest_turn
- first_ship_loss_turn
- first_major_loan
- first_defaulted_loan
- first_faction_alignment
- first_system_blacklisted

Rules:
- Milestones are optional
- Milestones are set once
- Milestones are never cleared

### 11.3 Historical Timeline (Bounded)

The Player Entity MAY include a bounded list of major historical events.

- history_timeline (list, capped length)

Each entry MAY include:
- turn
- system_id
- event_type
- reference_ids (list of identifiers)

reference_ids may include, but are not limited to:
- entity_id
- mission_id
- ship_id
- location_id
- system_id
- faction_id

Rules:
- reference_ids are informational only
- reference_ids MUST NOT be interpreted as rules or triggers
- reference_ids exist to support scoring, summaries, achievements,
  narrative reconstruction, and post-run analysis


Rules:
- Timeline length must be capped
- Oldest entries may be discarded
- Timeline is informational only

### 11.4 History Usage

History may be used by:
- Endgame scoring
- Achievement systems
- Post-game summaries

- History entries must be sufficient to reconstruct
  "what mattered" without reprocessing full logs

History MUST NOT:
- Drive moment-to-moment gameplay
- Replace system logs
- Be used for rule enforcement

----------------------------------------------------------------

## 12. Progression Tracks (End Goals)

The Player Entity MUST track the six progression tracks:

- trust
- notoriety
- entrepreneur
- criminal
- law
- outlaw

Rules:
- Each track ranges from 0 to 100
- Tracks are modified only by authorized systems
- Playstyle summaries are derived, not stored

Win/loss conditions are defined in end_goals.md.

----------------------------------------------------------------

## 13. Titles and Flags

The Player Entity MAY track:

- earned_titles (list)
- global_flags (map)

Rules:
- Titles are informational only
- Flags are explicit and system-owned

----------------------------------------------------------------

## 14. Determinism and Persistence

The Player Entity MUST:

- Be fully serializable
- Be reproducible from logs
- Never mutate without logging

----------------------------------------------------------------

## 15. Versioning and Evolution

This contract is explicitly expected to evolve.

Rules:
- Any added field requires a version bump
- No field may be added implicitly
- Deprecated fields must be documented
- Cursor changes must reference the updated contract

----------------------------------------------------------------

## 16. Contract Statement

This document is authoritative for its current version.

Any system that:
- Reads player state
- Writes player state

MUST conform to this contract.

All changes require updating this document first.

----------------------------------------------------------------
## Mission Capacity (Evolving)

The Player Entity governs how many missions may be active
concurrently.

Fields:
- mission_slots (integer, minimum 1)
- active_mission_count (derived or tracked)

Rules:
- At game start, mission_slots = 1
- Each ACTIVE mission consumes one slot
- A mission slot is released when a mission is:
  - completed
  - failed
  - abandoned

The Player Entity determines whether a new mission
may be accepted based on available slots.

Slot expansion:
- Mission slot increases may occur via:
  - special missions
  - reputation thresholds
  - narrative or endgame progression
- Slot expansion logic is not defined here

The Player Entity does not resolve missions.
It only enforces mission capacity.


----------------------------------------------------------------
## Mission Discovery and Filtering (Evolving)

The Player Entity may define preferences that control
which missions are presented to the player.

Filtering affects visibility only.
Filtering does NOT restrict mission availability or acceptance.

Filterable attributes may include:
- mission_tier (minimum and/or maximum)
- mission_type
- mission_source (NPC, DataNet, faction, system)
- mission_scope (local, multi-system, systemic)

Rules:
- All missions remain technically available
- The player may choose to ignore or override filters
- Filters exist to reduce noise, not enforce progression

Mission systems must respect Player Entity filters
when presenting missions, but must not prevent
acceptance of unfiltered missions if explicitly selected.

----------------------------------------------------------------
