# EmojiSpace - Ship Entity Contract

Status: DRAFT (Evolving)
Phase: 3
Applies To: Ship entities only

This document defines the structure, state, and responsibilities of
Ship entities in EmojiSpace.

Ships are persistent entities that hold state.
They do not resolve outcomes or perform logic.

----------------------------------------------------------------

## 1. Core Definition

A Ship is a persistent entity representing a mobile asset that can
be owned by a player, NPC, or faction.

Ships may:
- carry cargo
- store cargo
- participate in encounters
- be damaged, seized, or destroyed

Ships do NOT:
- resolve combat
- determine legality
- price goods
- resolve inspections or enforcement
- advance missions

----------------------------------------------------------------

## 2. Identity and Ownership

Each Ship entity MUST have:

- ship_id (unique identifier)
- model_id (reference to ship model data)
- owner_type (player | npc | faction)
- owner_id (identifier of owner)

Optional:
- name (player-assigned or narrative)

Ownership is authoritative and persistent.

----------------------------------------------------------------

## 3. Active vs Inactive State

A player may own multiple ships.

Rules:
- Exactly ONE ship may be ACTIVE at a time
- All other ships are INACTIVE

ACTIVE ship:
- participates in ship-to-ship encounters
- travels between systems
- carries cargo during travel
- may be inspected, damaged, seized, or destroyed

INACTIVE ships:
- do not travel
- do not participate in encounters
- may store cargo
- act as stationary assets or stashes

----------------------------------------------------------------

## 4. Location and Storage Context

Each Ship entity MUST track its current storage context.

Possible contexts include:
- in_transit
- orbit
- station
- shipdock
- planet_surface
- impounded
- destroyed

Rules:
- Storage context determines exposure to risk
- Ship entities do NOT resolve storage risk outcomes

Special cases:
- Ships stored in shipdock MUST have no cargo
- Ships stored elsewhere MAY store cargo

----------------------------------------------------------------

## 5. Cargo Classification

Goods are classified by SKU tags.

Rules:
- Goods with the "data" tag are DIGITAL cargo
- Goods without the "data" tag are PHYSICAL cargo
- Ships do NOT define cargo type logic

Cargo type is inferred from SKU data only.

----------------------------------------------------------------

## 6. Cargo Capacity

Ships maintain two independent cargo capacities:

- physical_cargo_capacity
- data_cargo_capacity

Rules:
- Physical cargo consumes physical capacity
- Digital cargo consumes data capacity
- Capacities are finite
- Overflow is forbidden

Capacities are typically derived from ship model data
but are stored on the Ship entity for persistence.

----------------------------------------------------------------

## 7. Cargo Manifests

Each Ship entity maintains two cargo manifests:

- physical_cargo_manifest
- data_cargo_manifest

Each manifest entry includes:
- sku_id
- quantity

Rules:
- No SKU-specific volume logic exists
- Each unit consumes one unit of the relevant capacity
- Ships do NOT determine legality or value of cargo

### Fuel State

Field: current_fuel  
Type: integer  
Required: yes  
Minimum: 0  

Invariant:
0 <= current_fuel <= fuel_capacity

Notes:
- fuel_capacity is computed by assembler.
- current_fuel is persistent state.
- Fuel is consumed during travel.
- Fuel is restored via refuel interaction.

----------------------------------------------------------------

## 8. Damage and Condition

Ship damage represents physical condition only.

Each Ship entity MUST track:

- condition_state
- condition_emoji

Canonical condition states include:
- operational
- damaged
- disabled
- destroyed

Emoji representation is thematic and informational.

Rules:
- Physical damage may affect usability
- Physical damage may expose cargo to risk
- Digital cargo is not affected by physical damage
- Ships do NOT resolve damage effects

----------------------------------------------------------------

## 9. Interaction Participation

Ships may participate in:
- passive encounters
- hostile encounters
- inspection encounters

Rules:
- Ships do not choose actions
- Ships do not expose interactions
- Ships only hold state used by other systems

Encounter resolution is handled elsewhere.

----------------------------------------------------------------

## 10. Seizure, Loss, and Destruction

Ships may be:
- seized
- impounded
- destroyed

Rules:
- Ship entity reflects resulting state only
- Ownership, cargo loss, and consequences are handled
  by enforcement or event systems

Destroyed ships:
- cannot be reactivated
- may persist as historical records

----------------------------------------------------------------

## 11. Explicit Non-Responsibilities

Ship entities do NOT:
- calculate combat outcomes
- determine enforcement results
- apply upgrades
- manage insurance logic
- resolve theft or discovery
- determine win or loss conditions

Ships are state containers only.

----------------------------------------------------------------

## 12. Evolution Notes

This contract is intentionally incomplete.

Future phases may add:
- component effects
- upgrade systems
- insurance integration
- fleet abstractions (non-tactical)
- deeper damage modeling

All additions MUST preserve the principle that
Ships hold state but do not resolve outcomes.

----------------------------------------------------------------

## 13. Contract Authority

This document is authoritative for Ship entity structure.

Changes require:
- explicit revision
- version update
- review before Cursor implementation
