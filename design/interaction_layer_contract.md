# EmojiSpace - Interaction Layer Contract

Status: Locked
Phase: 4b - Encounter Interaction and Dispatch
Target Version: 0.5.x
Location: /design/interaction_layer_contract.md

----------------------------------------------------------------

## 1. Purpose

The Interaction Layer is the mandatory dispatcher for all encounters.

It:
- Presents the allowed player actions for an encounter (UI-agnostic)
- Accepts the player choice (action + optional payload)
- Dispatches control to the appropriate resolution handler
- Terminates the encounter if the player chooses to exit

It does NOT resolve outcomes itself.

----------------------------------------------------------------

## 2. Scope and Authority

This contract governs:
- A stable vocabulary of encounter postures and actions
- Mapping from action to handler responsibility
- The structure of player choices and action payloads
- Deterministic state transitions between interaction and resolvers
- Logging required to reconstruct all interaction decisions

This contract does NOT govern:
- Encounter occurrence (Travel Resolution)
- Encounter definition (Encounter Generator)
- Combat resolution, damage, or ship destruction
- Law enforcement outcomes (fines, confiscation, arrest)
- Market pricing or legality interpretation
- Mission resolution
- Prose generation
- UI design or presentation

----------------------------------------------------------------

## 3. Core Principles (Non-Negotiable)

1. All encounters pass through the Interaction Layer
2. The Interaction Layer dispatches; resolvers decide outcomes
3. Actions are limited to a stable global vocabulary
4. Posture determines the base allowed actions
5. Subtype may restrict actions, but may not invent new actions
6. Determinism and log-reconstructibility are mandatory
7. No state mutation occurs in the Interaction Layer

----------------------------------------------------------------

## 4. Inputs (Authoritative)

The Interaction Layer consumes:

### 4.1 EncounterSpec (From Encounter Generator)
EncounterSpec MUST include:
- encounter_id
- posture (enum; Section 5)
- subtype_id
- threat_rating_tr (optional)
- participants (refs)
- reward_profile_id (optional)
- flags (list)
- hooks (optional)

### 4.2 Player Choice
- action_id (enum; Section 6)
- payload (optional; structured; Section 7)

### 4.3 Determinism
- world_seed (for any tie-break ordering only; no rolls)
- stable ordering rules (ASCII sort of action ids)

----------------------------------------------------------------

## 5. Encounter Postures (Authoritative Enum)

EncounterSpec.posture MUST be one of:

- neutral
- authority
- hostile
- opportunity

Posture definitions:

- neutral: non-hostile, non-authority contact; player may choose to hail
- authority: authority-initiated contact; player is being acted upon
- hostile: threat-initiated contact; violence is plausible by default
- opportunity: discovery/investigation contact; no opposing actor required

----------------------------------------------------------------

## 6. Action Vocabulary (Authoritative Enum)

The Interaction Layer recognizes ONLY these base actions:

- ignore
- hail
- attack
- comply
- bribe
- flee
- surrender
- investigate

Notes:
- Additional actions must be added only via explicit contract revision.
- UI may present actions with different labels, but the action_id must match.

----------------------------------------------------------------

## 7. Action Payloads (Optional Structured Data)

Some actions accept a payload. Payloads must be structured and validated.

### 7.1 hail payload
hail opens a hail submenu selection (Section 8).
Payload:
- hail_action (enum; trade, meet, intimidate)
- hail_payload (optional; per hail_action)

### 7.2 bribe payload
Payload:
- bribe_kind (enum: credits, goods)
- credits_amount (int; optional; if credits)
- goods_offered (list of sku refs; optional; if goods)

### 7.3 flee payload
Payload:
- flee_kind (enum: attempt_escape)
(no additional fields in v0.5.x)

### 7.4 investigate payload
Payload:
- investigate_kind (enum: scan, board, salvage_probe) (optional/future)
(v0.5.x default: scan)

### 7.5 surrender payload
Payload:
- surrender_kind (enum: unconditional)
(v0.5.x default: unconditional)

No other payload keys are permitted.

----------------------------------------------------------------

## 8. Hail Submenu (Authoritative)

hail is a base action that selects one hail sub-action:

Hail sub-actions (enum):
- trade
- meet
- intimidate

Hail sub-action routing:

- trade -> market_interaction handler
- meet -> npc_interaction handler
- intimidate -> reaction_evaluation handler, then dispatch based on outcome

Hail payload rules:

### trade payload (optional)
- trade_mode (enum: cargo_only)
(v0.5.x default: cargo_only)

### meet payload (optional)
- meet_mode (enum: short_contact)
(v0.5.x default: short_contact)

### intimidate payload (required)
- intimidate_intent (enum: demand_surrender, demand_credits, demand_cargo)
- demand_credits_amount (int; optional; if demand_credits)
- demand_cargo_constraints (optional object; if demand_cargo)

NOTE:
- intimidate does not resolve outcomes. It triggers Reaction Evaluation.

----------------------------------------------------------------

## 9. Base Allowed Actions Per Posture (Authoritative)

The Interaction Layer MUST enforce these base sets:

### neutral
- ignore
- hail
- attack

### authority
- comply
- bribe
- flee
- attack

### hostile
- surrender
- bribe
- flee
- attack

### opportunity
- ignore
- investigate

Subtype restrictions:
- EncounterSpec.subtype_id MAY remove actions from the base set.
- EncounterSpec.subtype_id MUST NOT add actions outside the global vocabulary.

Examples:
- Some hostile subtypes may forbid bribe (but posture allows it by default).
- Some neutral subtypes may forbid hail (rare).

----------------------------------------------------------------

## 10. Dispatch Targets (Handler Ownership)

The Interaction Layer dispatches to exactly one handler per player choice.

Handler targets (enum):
- end_encounter
- combat
- law_enforcement
- market_interaction
- npc_interaction
- pursuit
- exploration
- reaction_evaluation

Dispatch mapping:

- ignore -> end_encounter
- hail.trade -> market_interaction
- hail.meet -> npc_interaction
- hail.intimidate -> reaction_evaluation
- attack -> combat
- comply -> law_enforcement
- bribe -> law_enforcement (authority posture) OR reaction_evaluation (hostile posture)
- flee -> pursuit
- surrender -> reaction_evaluation (hostile posture) then law_enforcement/combat/end_encounter based on outcome
- investigate -> exploration

Clarification:
- bribe in hostile posture is not "law enforcement". It is evaluated as a
  negotiation attempt via reaction_evaluation, and may result in:
  - end_encounter
  - pursuit
  - combat

----------------------------------------------------------------

## 11. Reaction Evaluation Integration (Required)

The Interaction Layer relies on a Reaction Evaluation function for:
- player intimidate (hail.intimidate)
- hostile bribe attempts
- surrender response handling

Reaction Evaluation returns one of these outcomes (enum):
- accept_and_end
- accept_and_flee
- accept_and_attack
- refuse_and_end
- refuse_and_flee
- refuse_and_attack

The Interaction Layer then dispatches:

- *_and_end -> end_encounter
- *_and_flee -> pursuit
- *_and_attack -> combat

Reaction Evaluation must be deterministic and logged.
The Interaction Layer must log:
- input action and payload
- outcome enum
- resulting dispatch target

NOTE:
- A separate Reaction Evaluation contract will define inputs and weighting.
- The Interaction Layer does not implement weighting logic.

----------------------------------------------------------------

## 12. Pursuit Dispatch (Required)

On flee, Interaction Layer dispatches to pursuit.

Pursuit handler responsibilities (outside this contract):
- Determine escape success/failure deterministically
- If failure, transition to combat
- If success, return end_encounter

Population must not influence pursuit outcomes.

----------------------------------------------------------------

## 13. Reward Handling (Non-Responsibility)

The Interaction Layer does not apply rewards.

Rewards are applied only by resolvers (combat, law, mission, exploration)
after an outcome qualifies.

The Interaction Layer may pass reward_profile_id through unchanged.

----------------------------------------------------------------

## 14. Determinism and Ordering Rules

The Interaction Layer:
- performs no random rolls
- uses stable ordering for action presentation:
  ASCII sort by action_id, then hail_action

If UI presents a different order, it must still validate against the same
allowed action set.

----------------------------------------------------------------

## 15. Logging Requirements (Mandatory)

Logs must reconstruct:
- EncounterSpec.posture and subtype_id
- Allowed actions after posture + subtype restrictions
- Player chosen action_id and payload
- Dispatch target selected
- Reaction evaluation outcome (if used)
- Encounter termination path (end, combat, law, pursuit, etc.)

Failure to reconstruct dispatch from logs is a contract violation.

----------------------------------------------------------------
## Refuel

Availability:
Refuel is available if and only if the destination includes DataNet service.

Refuel does not directly check population.

Fuel Price:
fuel_price_per_unit = 5 credits (fixed).

Refuel Options:
- Partial refuel (player selects units)
- Full refuel (restore to fuel_capacity)

Constraints:
- Cannot exceed fuel_capacity.
- Deduct credits equal to units_purchased * fuel_price_per_unit.
- Must log fuel and credit changes.

Refuel does not:
- Affect combat.
- Affect degradation.
- Affect legality.
- Affect pricing systems.

## Shipdock Interaction Extensions (0.7.1)

The following actions are available only at destinations that include a Shipdock service.

All actions require the ship involved to be physically present at the destination.

Ship ownership and active/inactive state are governed by the entity layer.
This section extends interaction capabilities only.

---

### Buy Hull

Requirements:
- Destination includes Shipdock.
- Hull is present in shipdock inventory.
- Player has sufficient credits.

Behavior:
- Create new ship entity with:
  - hull_id = selected hull
  - module_instances = empty list
  - degradation_state = all zeros
  - current_hull_integrity = max_hull_integrity
  - current_fuel = fuel_capacity
  - location_id = current destination
  - active_flag = false
- Deduct credits equal to hull base_price_credits.
- Add ship to player fleet at this location.

Buy Hull does not:
- Automatically activate the ship.
- Transfer modules from other ships.

---

### Sell Hull

Requirements:
- Destination includes Shipdock.
- Ship is physically located at current destination.

Constraints:
- If selling active ship:
  - Player must have at least one other ship at this destination.
  - One remaining ship at this location becomes active immediately.

Sell Price:
sell_price = base_price_credits * 0.5

Modifier Hook:
final_price = sell_price * price_modifier_multiplier
Default price_modifier_multiplier = 1.0

Behavior:
- Remove ship entity from player fleet.
- Add credits equal to final_price.

Sell Hull does not:
- Affect other ships.
- Transfer modules.

---

### Buy Module

Requirements:
- Destination includes Shipdock.
- Module is present in shipdock inventory.
- Target ship is physically present at this destination.
- Slot constraints must pass assembler validation.
- Player has sufficient credits.

Behavior:
- Deduct module base_price_credits.
- Add module instance to target ship.
- Recompute ship stats via assembler.

Buy Module does not:
- Bypass slot limits.
- Apply secondary tags.

---

### Sell Module

Requirements:
- Destination includes Shipdock.
- Ship is physically present at this destination.
- Module is installed on that ship or stored with it.

Sell Price:
sell_price = base_price_credits * 0.5

Modifier Hook:
final_price = sell_price * price_modifier_multiplier
Default price_modifier_multiplier = 1.0

Behavior:
- Remove module instance from ship.
- Add credits equal to final_price.
- Recompute ship stats via assembler.

---
### Secondary Tag Resale Modifiers (0.7.2)

When selling a module at Shipdock, resale value is modified by secondary tags before applying global price_modifier_multiplier.

Base Sell Price:
sell_price = base_price_credits * 0.5

Secondary Multipliers:
If module includes secondary:prototype:
    resale_multiplier *= 1.5

If module includes secondary:alien:
    resale_multiplier *= 2.0

Multipliers stack multiplicatively.

Final Sell Price:
final_price = sell_price * resale_multiplier * price_modifier_multiplier

Notes:
- Secondary tags do not alter base_price_credits.
- Secondary tags do not affect market purchase price.
- This modifier applies only to sell operations.
- This rule does not alter rarity_weight.

### Repair Ship

Requirements:
- Destination includes Shipdock.
- Ship is physically present at this destination.

Repair restores:
- current_hull_integrity to max_hull_integrity
- All subsystem degradation_state values to 0

Repair Cost Calculation:

Let:
hull_damage = max_hull_integrity - current_hull_integrity
subsystem_damage = sum(degradation_state values)

Constants:
HULL_REPAIR_UNIT = 10
SUBSYSTEM_REPAIR_UNIT = 25

Base Cost:
base_cost =
(hull_damage * HULL_REPAIR_UNIT) +
(subsystem_damage * SUBSYSTEM_REPAIR_UNIT)

Population Modifier:
population_modifier:
1 -> 1.20
2 -> 1.10
3 -> 1.00
4 -> 0.90
5 -> 0.80

final_cost = round(base_cost * population_modifier)

Repair Behavior:
- If player has sufficient credits:
  - Deduct final_cost
  - Restore hull integrity
  - Reset degradation_state
- If insufficient credits:
  - Reject repair

Repair does not:
- Affect fuel
- Affect modules
- Affect cargo
- Affect legality
- Affect inventory generation


## 16. Explicit Non-Responsibilities

The Interaction Layer MUST NOT:
- Decide reaction outcomes
- Decide bribe success amounts
- Decide intimidation success
- Resolve combat, law, market, or exploration outcomes
- Mutate player/world state
- Generate prose
- Invent new actions outside the vocabulary

----------------------------------------------------------------

## 17. Contract Authority

This document becomes authoritative once locked.

Any system that dispatches encounters to handlers MUST conform to this
contract. Changes require explicit revision and version update.

----------------------------------------------------------------
