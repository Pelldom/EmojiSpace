# Combat and Ship Tag Contract

Status: LOCKED
Version: 0.5.0
Applies To:
- Ship Entity System
- Combat Resolver (Phase 4.x)
- Pursuit Resolver
- Encounter Generator (Ship Loadouts)
- Reaction Evaluation (Ship Traits Only)
- UI Presentation Layer (Emoji Mapping Only)

----------------------------------------------------------------
1. Purpose
----------------------------------------------------------------

This contract defines the complete and authoritative tag vocabulary
for ship components and ship traits used in combat and ship systems.

Tags defined here:

- Do not overlap with goods tags.
- Do not redefine legality.
- Do not redefine pricing.
- Do not alter government authority rules.
- Do not introduce percentage math.
- Do not introduce immunity mechanics.

All tags are deterministic, namespaced, and ASCII identifiers.

Emoji representations are presentation-layer only and are not part
of this contract.

----------------------------------------------------------------
2. Namespaces
----------------------------------------------------------------

All tags must use one of the following namespaces:

combat:weapon_*
combat:defense_*
combat:utility_*
ship:utility_*
ship:trait_*
secondary:*

No other namespaces are valid for ship and combat systems.

----------------------------------------------------------------
3. Primary Tag Rules
----------------------------------------------------------------

Every component must have exactly one primary tag.

Primary tags define:
- Slot category
- Core identity
- RPS interaction (if weapon or defense)
- System ownership

A component may not have more than one primary tag.

Primary tags may not be mixed across slot categories.

----------------------------------------------------------------
4. Weapon Tags (RPS Core)
----------------------------------------------------------------

combat:weapon_energy
combat:weapon_kinetic
combat:weapon_disruptive

Rules:

- These are the only valid weapon types.
- No additional weapon types may be introduced without
  explicit contract revision.
- Each weapon type participates in the RPS matrix defined below.

----------------------------------------------------------------
5. Defense Tags (RPS Core)
----------------------------------------------------------------

combat:defense_shielded
combat:defense_armored
combat:defense_adaptive

Rules:

- These are the only valid defense types.
- No additional defense types may be introduced without
  explicit contract revision.
- Each defense type participates in the RPS matrix defined below.

----------------------------------------------------------------
6. RPS Matrix (Authoritative)
----------------------------------------------------------------

Each weapon has:

- One strength (+1 band bias)
- One weakness (-1 band bias)
- One neutral interaction (0 bias)

Matrix:

weapon_energy:
  +1 vs defense_armored
  -1 vs defense_shielded
   0 vs defense_adaptive

weapon_kinetic:
  +1 vs defense_shielded
  -1 vs defense_adaptive
   0 vs defense_armored

weapon_disruptive:
  +1 vs defense_adaptive
  -1 vs defense_armored
   0 vs defense_shielded

Rules:

- Bias magnitude is fixed at +1 or -1.
- No immunity is allowed.
- No stacking of RPS effects.
- Secondary tags may not alter this matrix.

----------------------------------------------------------------
7. Combat Utility Tags
----------------------------------------------------------------

combat:utility_engine_boost
combat:utility_cloak
combat:utility_targeting
combat:utility_repair_system
combat:utility_overcharger
combat:utility_signal_scrambler

Rules:

- Combat utility tags may modify band deltas or unlock
  bridge commands.
- They may not redefine RPS interactions.
- They may not introduce percentage math.
- They may not alter legality.

----------------------------------------------------------------
8. Non-Combat Utility Tags
----------------------------------------------------------------

ship:utility_interdiction
ship:utility_extra_cargo
ship:utility_data_array
ship:utility_smuggler_hold
ship:utility_mining_equipment
ship:utility_probe_array

Rules:

- Non-combat utility tags may affect:
  - Pursuit
  - Cargo capacity
  - Data capacity
  - Enforcement detection
  - Resource extraction
  - Encounter information visibility

- They do not modify combat band resolution directly.
- They do not modify RPS logic.

### ship:utility_extra_fuel

Category: Ship Utility  
Purchasable: Yes  
Effect: +5 fuel capacity  

Notes:
- Stackable.
- Does not affect combat bands.
- Applied during ship assembly.


----------------------------------------------------------------
9. Ship Trait Tags
----------------------------------------------------------------

ship:trait_military
ship:trait_civilian
ship:trait_freighter
ship:trait_experimental
ship:trait_alien

Rules:

- Traits are inherent to ship models.
- Traits are not slotted components.
- Traits may influence:
  - Reaction evaluation
  - Encounter weighting
  - Minor combat bias (if defined elsewhere)
- Traits do not modify RPS matrix.

----------------------------------------------------------------
10. Secondary Tags
----------------------------------------------------------------

secondary:compact
secondary:enhanced
secondary:unstable
secondary:efficient
secondary:prototype
secondary:alien

Rules:

- A component may have at most one secondary tag.
- Secondary tags may not redefine primary identity.
- Secondary tags may not introduce a second weapon type.
- Secondary tags may not alter RPS matrix.
- Secondary tags may modify:
  - Band contribution (within defined limits)
  - Command unlock
  - Risk behavior
  - Stability
  - Reaction modifiers

Secondary tags are rare and expensive by design intent.

----------------------------------------------------------------
11. Slot Integrity Rules
----------------------------------------------------------------

Primary tag category must match slot category.

Example:
- Weapon slot accepts combat:weapon_*
- Defense slot accepts combat:defense_*
- utility slot accepts combat:utility_* and ship:utility_*

Secondary tags do not define slot eligibility.

----------------------------------------------------------------
12. Hard Constraints
----------------------------------------------------------------

1. Weapon types are limited to 3.
2. Defense types are limited to 3.
3. RPS bias is fixed at +1 or -1.
4. No immunity mechanics are permitted.
5. No percentage-based scaling is permitted.
6. No multi-primary components are permitted.
7. No stacking identical tags beyond slot limits.
8. Maximum one secondary tag per component.

----------------------------------------------------------------
13. Determinism
----------------------------------------------------------------

Given identical:

- Ship loadouts
- TR values
- Encounter context
- Commands

Combat resolution must produce identical results.

Tags must not introduce randomness beyond defined combat
resolution mechanics.

----------------------------------------------------------------
14. Contract Authority
----------------------------------------------------------------

This document is authoritative as of Version 0.5.0.

Any addition or modification to tag vocabulary,
RPS logic, or secondary rules requires:

- Explicit version increment
- Formal contract update
- No implicit extension allowed
this 