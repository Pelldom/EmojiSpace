# EmojiSpace - Travel Resolution Contract

Status: Locked
Phase: 4 - Travel and Encounter Scaffolding
Target Version: 0.5.x
Location: /design/travel_resolution_contract.md

----------------------------------------------------------------

## 1. Purpose

This contract defines the authoritative rules governing travel between
destinations and the generation of encounter contexts during travel.

Travel introduces risk and opportunity without simulating space,
distance, or movement, and without resolving outcomes.

This system creates encounter CONTEXTS only.
All outcomes are resolved by downstream systems.

----------------------------------------------------------------

## 2. Scope and Authority

This contract governs:
- Travel as a discrete player action
- Encounter opportunity generation during travel
- Encounter sequencing and limits
- Integration with Situations and Events (read-only)

This contract does NOT govern:
- Destination discovery or filtering
- Ship range calculation
- Combat resolution
- Law enforcement resolution
- NPC behavior
- Mission resolution
- Pricing or legality determination
- Situation or event creation, escalation, or resolution
- UI or presentation

----------------------------------------------------------------

## 3. Core Principles (Non-Negotiable)

1. Travel is a single, atomic player action
2. Travel does not simulate space, routes, or distance
3. Travel may generate zero or more encounters
4. Encounter probability diminishes after each encounter
5. Encounters are contexts, not outcomes
6. All behavior is deterministic and log-reconstructible
7. Situations and Events expose modifiers; Travel consumes them verbatim

----------------------------------------------------------------

## 4. Travel Action Definition

A Travel Action occurs when the player selects a valid destination
entity and confirms intent to travel.

A Travel Action:
- Advances time by one travel tick
- Triggers Travel Resolution exactly once
- Produces a Travel Result Record

Travel Resolution assumes that the destination is valid and reachable.
Validation of legality, discovery, and ship range occurs upstream.

----------------------------------------------------------------

## 5. Travel Eligibility Assumption

Travel Resolution assumes:
- The destination entity exists
- The destination is known to the player
- The destination is not hard-blocked by legality
- The active ship can reach the destination

Filtering based on ship range, legality, or mission constraints
is outside the scope of this contract.

----------------------------------------------------------------

## 6. Authoritative Inputs (Read-Only)

Travel Resolution may consume ONLY the following inputs.

### 6.1 World and Location State
- origin_system_id
- destination_system_id
- destination_type
- system.population
- system.government_id

### 6.2 Player State
- player heat (per system)
- player warrants (per system)
- active ship identifier
- pre-resolved cargo legality snapshot

### 6.3 Situations and Events
- active system-level situations
- active destination-level situations (future)
- active systemic events (future)

Situations and Events may expose encounter modifiers.
Travel Resolution must not reinterpret or invent meaning.

### 6.4 Determinism
- world_seed
- travel_index (per turn)

----------------------------------------------------------------

## 7. Encounter Generation Loop

During a Travel Action, encounter generation proceeds as follows:

1. Initialize encounter_count = 0
2. Set cap = system.population * 2
3. While encounter_count < cap:
   a. Calculate base_chance (after all modifiers)
   b. Apply diminishing probability based on encounter_count
   c. Roll deterministically
   d. If roll fails, terminate the loop
   e. If roll succeeds:
      - Generate an Encounter Context
      - Append it to the Travel Result Record
      - Increment encounter_count
4. End loop

Encounter generation must terminate naturally or at the hard cap.

----------------------------------------------------------------

## 8. Diminishing Probability Rule (Authoritative)

Each generated encounter MUST reduce the probability of subsequent
encounters within the same Travel Action.

Definitions:
- cap = system.population * 2
- base_chance = encounter chance after all modifiers,
  clamped to the range [0.0, 0.95]
- encounter_index k is 0-based within this travel action
  (first roll uses k = 0)

Authoritative diminishing model:
- step = base_chance / (cap + 1)
- effective_chance(k) = max(0.0, base_chance - (step * k))

Properties:
- effective_chance(k) never reaches zero within valid indices
- Zero probability is reached only beyond the encounter cap
- Higher population systems taper more slowly
- Lower population systems taper more aggressively

Requirements:
- effective_chance(k) MUST be logged per roll
- The diminishing model MUST NOT be bypassed by Situations or Events
- The encounter cap remains absolute

----------------------------------------------------------------

## 9. Encounter Hard Cap (Authoritative)

The maximum number of encounter contexts per Travel Action is:

cap = system.population * 2

This cap is absolute.
Situations and Events may not override or bypass this limit.

----------------------------------------------------------------

## 10. Situation and Event Integration

Situations and Events may expose:
- encounter_chance_modifiers
- encounter_type_bias maps
- scope (system or destination)

Rules:
- Modifiers are consumed verbatim
- No modifier may force an encounter
- No modifier may bypass diminishing probability
- No modifier may bypass the encounter cap
- Absence of Situations or Events must not break Travel Resolution

Travel Resolution never escalates or mutates Situations or Events.

----------------------------------------------------------------

## 11. Travel Result Record (Output)

Travel Resolution produces a Travel Result Record containing:

- origin_destination_id
- destination_destination_id
- ordered encounter_contexts list
- encounter_roll_log
- applied_modifier_log
- termination_reason (roll failure or cap reached)

Each Encounter Context includes:
- encounter_id
- encounter_class (passive, inspection, hostile, mission_hook, other)
- routing_target (law, encounter, mission, npc)
- involved_entity_refs (IDs only)

Encounter Contexts contain no outcomes or consequences.

## Fuel Consumption Rules

Fuel is required for standard ship travel.

### Inter-System Travel

fuel_cost = distance_ly

### Intra-System Travel

fuel_cost = 1

### Travel Preconditions

Before travel begins:

If current_fuel < fuel_cost:
- Travel is rejected.
- No time passes.
- No encounter resolution occurs.

If current_fuel >= fuel_cost:
- Deduct fuel_cost from current_fuel.
- Proceed with travel.
- Time advances per Time Engine rules.

### Emergency Transport

Emergency transport does not consume fuel.
Emergency transport still advances time per Time Engine rules.

----------------------------------------------------------------

## 12. Logging Requirements (Mandatory)

Logs must be sufficient to reconstruct:
- Base encounter chance
- All Situation/Event modifiers applied
- Diminishing step and effective_chance per roll
- Deterministic roll results
- Encounter ordering
- Loop termination reason

If encounter generation cannot be reconstructed from logs,
this contract is violated.

----------------------------------------------------------------

## 13. Explicit Non-Responsibilities

Travel Resolution MUST NOT:
- Resolve encounters
- Apply enforcement or penalties
- Modify legality, prices, or markets
- Spawn persistent NPCs
- Advance or escalate Situations or Events
- Apply damage, loss, or arrest
- Create UI or presentation elements

----------------------------------------------------------------

## 14. Contract Authority

This document becomes authoritative once locked.

Any system that performs travel resolution or generates
travel-based encounters MUST conform to this contract.

All changes require explicit revision and version update.

----------------------------------------------------------------
