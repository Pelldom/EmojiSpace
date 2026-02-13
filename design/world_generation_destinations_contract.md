# world_generation_destinations_contract.md

Status: PROPOSED (Pending Lock)
Phase: World Generator (Foundational)
Target Version: 0.3.x -> 0.4.x (major world state shape change)
Location: /design/world_generation_destinations_contract.md

Consumes:
- world_seed
- economies.json
- governments.json
- location_availability.json

Produces:
- galaxy state (systems + destinations + locations skeleton)
- deterministic identifiers (system_id, destination_id, location_id)
- per-system population and government
- per-destination economy assignment
- per-destination population (bounded by system population)
- per-destination locations (gated by destination population, destination economy, and system government)

----------------------------------------------------------------

## 1. Purpose

This contract defines the authoritative world structure hierarchy:

Galaxy -> Star Systems -> Destinations -> Locations -> NPC presence hooks

It exists to prevent ambiguity between:
- "where the player travels" (star systems)
- "what exists inside a system" (destinations)
- "where the player interacts" (locations)
- "who the player interacts with" (NPCs, later systems)

----------------------------------------------------------------

## 2. Core Definitions

2.1 Galaxy
- The galaxy is the top-level container for all generated content.
- Everything in a run exists somewhere in the galaxy.
- The galaxy contains a list of star systems.

2.2 Star System (System)
A star system is the primary travel node.
A system defines shared traits for everything inside it.

System-scoped fields (authoritative):
- system_id (string)
- name (string)
- position (x,y or equivalent)
- population (int 1-5)
- government_id (string, from governments.json)

Hard rule:
- Government is system-wide. All destinations inherit it.
- Population is a system ceiling. Destination population must be <= system population.

2.3 Destination
A destination is an object inside a star system that the player can travel to
(intra-system travel) and discover content at.

Destination types (Phase 0-2.x worldgen output):
- planet
- station
- asteroid_field
- contact (unknown ship / unknown signal)

Destination-scoped fields (authoritative):
- destination_id (string, unique within galaxy)
- system_id (string, parent)
- destination_type (enum)
- display_name (string)
- population (int 0-5, must be <= system.population)
- primary_economy_id (string, from economies.json, optional if population=0)
- secondary_economy_ids (list, may be empty)

Rules:
- Destinations may have different economies within the same system.
- A destination with population=0 represents a non-settled or non-civil location.
- Economy assignment is destination-specific and is not inferred from system traits.

2.4 Location
A location is a specific interaction site within a destination.

Examples (non-exhaustive):
- market
- bar
- warehouse
- shipdock
- administration
- bank
- datanet_terminal (future, Phase 2.8+)

Location-scoped fields (authoritative):
- location_id (string, unique within galaxy)
- destination_id (string, parent)
- location_type (string)
- enabled (bool)
- notes (optional)

Rules:
- Locations are generated deterministically during worldgen.
- Locations do not generate NPC instances. They only provide NPC presence hooks.

2.5 NPCs (Worldgen)
Worldgen does not create NPC entities.
Worldgen only creates the structural anchors that NPC systems will use later:
- locations that can host NPC roles (bar -> bartender, administration -> administrator)

----------------------------------------------------------------

## 3. Deterministic Generation Requirements

- All IDs must be deterministic under (world_seed, generation order).
- No runtime regeneration is allowed for systems, destinations, or locations.
- Worldgen must log:
  - system list (population, government)
  - per-system destination list (type, population, economies)
  - per-destination locations generated and why

----------------------------------------------------------------

## 4. System-Level Rules (Population, Government)

4.1 Population Ceiling
- system.population is a ceiling.
- destination.population must be <= system.population.

4.2 Government Inheritance
- destination government is always system.government_id.
- no destination may override government_id.

----------------------------------------------------------------

## 5. Destination Population Resolution (Authoritative)

Destination population is resolved deterministically using:
- world_seed
- system_id
- destination_id (or destination index)

Rules:
- If system.population = 1, all populated destinations must be population 1.
- For system.population > 1, destination.population may vary but must not exceed the system.

Default destination population bands:
- Populated destinations choose a value in [1, system.population].
- Unpopulated destinations may be population 0.

No other modifiers are permitted at worldgen time.

----------------------------------------------------------------

## 6. Destination Economy Assignment (Authoritative)

Economies are assigned per destination, not per system.

Rules:
- Populated destinations (population >= 1) must have exactly one primary economy.
- Secondary economies use the same slot rules as the existing market contract,
  but applied per destination using destination.population as the cap input.

Secondary economy slot limits by destination.population:
- 1-2: max 1 slot
- 3: max 2 slots
- 4-5: max 3 slots

Secondary economy slot fill chance:
- 33% per slot attempt (deterministic roll)

No duplicates across primary and secondary.

----------------------------------------------------------------

## 7. Destination Counts (Phase 0-2.x Simple Rule)

This contract intentionally uses a simple, deterministic count model.

For each system, generate:
- 1 to 3 core destinations (planets/stations) based on system.population
- plus 0 to 2 non-settled destinations (asteroid_field/contact)

Authoritative bands:
- system.pop 1: core 1-2, extras 0-1
- system.pop 2: core 1-2, extras 0-1
- system.pop 3: core 2-3, extras 0-2
- system.pop 4: core 3,   extras 1-2
- system.pop 5: core 3,   extras 1-2

Exact choice within the band is deterministic using world_seed and system_id.

----------------------------------------------------------------

## 8. Location Generation Hook (Delegated)

Location generation is defined by:
- location_availability.json
- the Location Availability contract (updated to be destination-scoped)

Worldgen must generate locations per destination using:
- destination.population
- destination economies
- system government_id

----------------------------------------------------------------

## 9. Contract Statement

This document is authoritative once locked.

Any system that creates or interprets:
- systems
- destinations
- locations

must conform to this hierarchy and its invariants.

Changes require explicit revision and version update.
