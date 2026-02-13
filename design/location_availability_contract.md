# EmojiSpace - Location Availability Contract

Status: DRAFT (Lock So Far)
Phase: 3 (World Generation)
Applies To: Destination and Location Generation Only

This document defines the authoritative rules used to determine
which location types exist at a destination.

----------------------------------------------------------------

## 0. Scope Clarification (Destination-Scoped)

- Location availability is evaluated per destination, not per system.
- Availability is resolved once during World Generation and persisted.
- Runtime systems MUST NOT infer, recalculate, or override availability.

Location availability is determined during World Generation and
persisted on location entities. Runtime systems MUST NOT infer,
recalculate, or override availability.

----------------------------------------------------------------

## 1. Core Principle

Location availability is deterministic and data-driven.

A location exists if and only if all required availability gates
evaluate to true.

Availability is evaluated ONCE during World Generation.

----------------------------------------------------------------

## 1.1 Destination vs System Scope (Critical Clarification)

- Location availability is evaluated per destination.
- HOWEVER, LIMITED is a system-level cap, not a destination-level cap.
- If a location type resolves to LIMITED:
  - It may exist in at most ONE destination in the system.
  - Additional eligible destinations MUST NOT receive that location.
- Which destination receives the LIMITED location MUST be chosen deterministically
  using world_seed and system_id.

----------------------------------------------------------------

## 2. Availability Gates

Each location type is evaluated against three independent gates:

1. Population Gate
2. Government Gate
3. Economy Gate

All three gates must pass for a location to exist.

----------------------------------------------------------------

## 3. Population Gate (Hard Requirement)

Each location type defines a minimum population requirement.

Rules:
- Population checks use destination.population
- destination.population must be <= system.population (inherited invariant)
- If destination.population is below the minimum, the location CANNOT exist
- Population is evaluated first
- Failure at this gate halts further evaluation

Population is an infrastructure capacity constraint.

----------------------------------------------------------------

## 4. Government Gate (Permission)

Each location type defines which government types allow it to exist.

Rules:
- Government permissions are explicit
- Government is inherited from the parent system
- Government checks use system.government_id
- Destinations may not override government
- If the system government is marked NO for a location, it CANNOT exist
- Government does not guarantee existence, it only permits it

Permission values:
- YES      : location allowed
- NO       : location forbidden
- LIMITED  : location allowed, but capped to one instance per system

----------------------------------------------------------------

## 5. Economy Gate (Demand)

Each location type defines which economy types support it.

Destinations may have one or more economies.

Rules:
- Economy checks use the destination's economies:
  - primary economy
  - all secondary economies
- System-level economies are not consulted
- All present economies are evaluated
- If ANY economy returns YES, the location is supported
- Else if ANY economy returns LIMITED, the location is supported as LIMITED
- Else the location is NOT supported

Economy demand answers the question:
"Is there a reason for this location to exist here?"

----------------------------------------------------------------

## 6. YES / LIMITED / NO Semantics

YES:
- Location may exist at any eligible destination
- Subject to per-destination uniqueness (one per destination)

LIMITED:
- Location may exist in the system
- At most ONE instance may exist across the entire system
- The instance is assigned to exactly one eligible destination

NO:
- Location does not exist anywhere in the system

YES takes precedence over LIMITED.
LIMITED takes precedence over NO.

----------------------------------------------------------------

## 7. Evaluation Order (Authoritative)

For each location type:

1. Determine all eligible destinations based on:
   - destination.population
   - destination economies
   - system government
2. If result is NO: place zero locations.
3. If result is YES: place the location at all eligible destinations,
   respecting per-destination uniqueness.
4. If result is LIMITED: place the location at exactly one eligible
   destination, chosen deterministically from world_seed and system_id.

----------------------------------------------------------------

## 7.1 Destination Uniqueness (Structural Rule)

- A destination may not host more than one instance of the same location type.
- This rule applies regardless of YES or LIMITED status.
- This is a structural constraint, not an availability gate.

----------------------------------------------------------------

## 8. DataNet Terminals

- DataNet is a destination-scoped civic location.
- DataNet terminals exist at all destinations with population > 0.
- DataNet placement is not subject to government limits or random rolls.
- Destinations with population = 0 do not receive DataNet terminals.
- DataNet content is locally reflective of the destination, but may include
  external system or neighboring system information.

Notes:
- DataNet follows the same population-based presence rule as Markets.
- No special-case exclusions by destination type are permitted.


----------------------------------------------------------------

## 9. Scope and Responsibilities

World Generation MUST:
- Apply this contract per destination
- Determine availability for each location type at each destination
- Persist availability on generated location entities

Runtime systems MUST:
- Trust location availability data
- Never infer availability from population, government, or economy

----------------------------------------------------------------

## 10. Non-Responsibilities

This contract does NOT:
- Decide how many locations are created (beyond LIMITED caps)
- Place locations on specific planets or stations
- Handle narrative or event-driven overrides
- Apply enforcement, pricing, or missions

Those concerns are handled by other systems.

----------------------------------------------------------------

## 11. Contract Authority

This document is authoritative.

Any system that creates, removes, or interprets locations MUST
conform to this contract.

Changes require:
- Explicit revision
- Version update
- Review before Cursor implementation
