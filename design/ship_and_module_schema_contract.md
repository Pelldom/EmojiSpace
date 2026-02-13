# Ship and Module Schema Contract

Status: LOCKED
Phase: 4.2 - Ship and Module Data Layer
Target Version: 0.6.1
File: /design/ship_and_module_schema_contract.md

----------------------------------------------------------------
1. Purpose
----------------------------------------------------------------

This contract defines the authoritative JSON schema structures for:

- Ship hull definitions
- Module definitions
- Secondary tag distribution rules
- Salvage mutation rules
- Storage invariants
- NPC parity requirements

This contract defines STRUCTURE ONLY.

It does NOT define:
- Purchasing logic
- Inventory generation logic
- Mission logic
- UI logic
- Market behavior
- Government legality behavior

Those systems consume this schema but do not alter it.

----------------------------------------------------------------
2. Determinism Requirement (Non-Negotiable)
----------------------------------------------------------------

Given identical:

- world_seed
- hull definition
- installed module instances (including secondaries)
- crew list
- encounter context

The engine MUST deterministically compute:

- Weapon/Defense/Engine band base potentials
- Hull maximum
- Cargo capacities
- RCP and TR
- Repair module count (derived from primary_tag)
- Subsystem capacity
- Salvage mutation outcomes

No hidden modifiers are permitted.
No NPC-only stats are permitted.

----------------------------------------------------------------
3. Separation of Responsibility
----------------------------------------------------------------

- Economy defines pricing behavior.
- Government defines legality and enforcement.
- Ship and Module schema defines capability and intrinsic base value only.

Therefore, hull and module objects MUST NOT include:

- legality fields
- government fields
- dynamic pricing modifiers
- enforcement modifiers
- encounter weighting
- mission routing logic
- percent-based scaling fields

----------------------------------------------------------------
4. File Structure
----------------------------------------------------------------

Hull catalog:

{
  "version": "0.6.1",
  "hulls": [ HullObject, ... ]
}

Module catalog:

{
  "version": "0.6.1",
  "modules": [ ModuleObject, ... ]
}

IDs must be ASCII lowercase with underscores.
IDs must be stable once published.

----------------------------------------------------------------
5. Hull Schema (Authoritative)
----------------------------------------------------------------

HullObject:

{
  "hull_id": "string",
  "name": "string",

  "tier": 1..5,
  "frame": "MIL|CIV|FRG|XA|XB|XC|ALN",

  "traits": [ "ship:trait_*", ... ],

  "bias": {
    "weapon": integer,
    "defense": integer,
    "engine": integer,
    "hull": integer
  },

  "cargo": {
    "physical_base": integer,
    "data_base": integer
  },

  "crew_capacity": integer,

  "base_price_credits": integer,

  "rarity_tier": "common|uncommon|rare|unique",
  "mission_grantable": true|false,

  "availability_flags": [ string, ... ],

  "description": "string (optional)"
}

5.1 Slot Counts

Slot counts are NOT stored in HullObject.

They are derived exclusively from:
- tier
- frame
- the Ship System slot matrix

This prevents duplication of authority.

5.2 Bias

Bias values override any default frame bias table.
All hulls must explicitly define bias.

This enables variant hulls without inheritance.

5.3 Cargo

physical_base and data_base are required.

Cargo bonuses from modules are applied later by tag behavior.

5.4 Prohibited Hull Fields

HullObject MUST NOT include:

- slot counts
- band totals
- TR
- RCP
- installed module lists
- legality
- percent modifiers
- NPC-only modifiers

### Fuel Capacity

Field: fuel_capacity_base  
Type: integer  
Required: yes  
Minimum: 0  

Description:
Base fuel capacity for the hull before module bonuses.
Final fuel capacity is computed by the assembler as:

fuel_capacity = fuel_capacity_base + sum(module fuel bonuses)

This field must be explicitly defined per hull in hulls.json.
No implicit tier or frame scaling is permitted in engine logic.


----------------------------------------------------------------
6. Module Schema (Authoritative)
----------------------------------------------------------------

ModuleObject:

{
  "module_id": "string",
  "name": "string",
  "display_names": [ "string", ... ],

  "slot_type": "weapon|defense|utility",
  "primary_tag": "combat:*|ship:*",

  "numeric_bonus": {
    "weapon": integer (optional),
    "defense": integer (optional),
    "engine": integer (optional)
  },

  "base_price_credits": integer,

  "rarity_weight": integer,
  "rarity_tier": "common|uncommon|rare|unique",
  "mission_grantable": true|false,

  "secondary_policy": {
    "allowed": true|false
  },

  "salvage_policy": {
    "salvageable": true|false,
    "mutation_allowed": true|false,
    "unstable_inject_chance_override": number (optional; 0.0-1.0)
  },

  "allowed_on_frames": [ "MIL|CIV|FRG|XA|XB|XC|ALN", ... ] (optional),

  "description": "string (optional)"
}

6.X display_names (Required)

Rules:
- Must contain at least one entry.
- Entries must be ASCII strings only.
- Cosmetic only.
- Must not influence numeric_bonus, pricing, rarity, salvage, TR, legality, encounter weighting, or engine determinism.
- Deterministic selection deferred to Phase 4.4.
- Must exist inside each ModuleObject.
- No external naming catalogs allowed.

6.1 Primary Tag Authority

primary_tag defines all behavior.

Repair capability is determined by:
primary_tag == combat:utility_repair_system

No separate repair flag exists.

All action unlocking is tag-driven.

6.2 Numeric Bonus

numeric_bonus defines band contributions only.

Secondary tags modify numeric_bonus per appendix rules.

6.3 Cargo Invariant

ALL modules consume exactly 1 unit of PHYSICAL cargo when not installed.

This is a permanent invariant.
No module may override this.

6.4 Prohibited Module Fields

ModuleObject MUST NOT include:

- TR override
- repair flag
- action unlock list
- legality fields
- dynamic pricing multipliers
- percent scaling
- NPC-only modifiers

----------------------------------------------------------------
7. Storage Invariants
----------------------------------------------------------------

Modules exist in one of three states:

- installed
- cargo
- warehouse

7.1 Cargo

Uninstalled modules consume 1 physical cargo slot.

7.2 Warehouse

Warehouse storage is capacity-based.

Modules stored in warehouse consume 1 warehouse slot per module.

Warehouse is NOT unlimited.

7.3 Inactive Ships (Mothball Rule)

Non-negotiable rule:

Inactive ships MUST have zero installed modules.

When a ship becomes inactive:
- All installed modules are removed.
- Modules must be placed into cargo or warehouse.
- If insufficient storage capacity exists, the transition fails.

Inactive ships cannot function as storage pools.

----------------------------------------------------------------
8. Secondary Tag Distribution
----------------------------------------------------------------

Secondary tags apply to module INSTANCES.

Allowed stacking:

- none
- one non-alien secondary
- alien alone
- alien + one non-alien

Distribution weights (v0.6.0 baseline):

- none:      0.50
- unstable:  0.20
- prototype: 0.10
- compact:   0.05
- enhanced:  0.05
- efficient: 0.05
- alien:     0.05

Alien stacking rule:
If alien is rolled:
- apply alien
- reroll excluding alien
- apply second result if not none

Weights may only change via contract revision.

----------------------------------------------------------------
9. Salvage Rules
----------------------------------------------------------------

Default salvage policy:

- salvageable: true
- mutation_allowed: true

9.1 Salvage Secondary Mutation

If a salvaged module instance has NO secondary tags:

It may receive secondary:unstable.

Default unstable injection chance:

- common: 0.40
- uncommon: 0.40
- rare: 0.50
- unique: 0.50

If unstable_inject_chance_override exists, it overrides defaults.

If module already has any secondary tag:
No mutation occurs.

Normal secondary distribution is NOT rerolled during salvage.

----------------------------------------------------------------
10. NPC Parity Rule
----------------------------------------------------------------

NPC ships MUST use the same:

- Hull catalog
- Module catalog
- Secondary rules
- TR computation pipeline

Prohibited:

- NPC-only bonuses
- NPC-only TR overrides
- Hidden modifiers

----------------------------------------------------------------
11. Prohibited Fields Summary
----------------------------------------------------------------

The following fields are prohibited in hull/module catalogs:

- custom_tr
- rcp_override
- band_override
- npc_bonus_*
- hidden_*
- legality_*
- government_*
- dynamic_price_*
- percent_modifier_*
- encounter_weight_*
- mission_routing_*

Presence of these fields is a contract violation.

----------------------------------------------------------------
12. Version Control
----------------------------------------------------------------

Any change to:

- Schema shape
- Required fields
- Enums
- Secondary weights
- Salvage mutation rules

Requires:

- Version increment
- Explicit contract revision
- Matching data file version bump

12.1 Version 0.6.1 note

- Added required "display_names" field to ModuleObject.
- Change is cosmetic-only.
- No impact on numeric_bonus, pricing, rarity, salvage, TR, legality, or deterministic behavior.
- Deterministic selection deferred to Phase 4.4.

----------------------------------------------------------------
13. Contract Authority
----------------------------------------------------------------

This document is authoritative as of Version 0.6.1.

All systems consuming ship and module data MUST conform.
Any deviation requires explicit contract update.
