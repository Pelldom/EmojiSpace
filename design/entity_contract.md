# EmojiSpace - Entity System Contract

Status: LOCKED
Phase: 3 - NPC Persistence
Target Version: 0.4.x
Location: /design/entity_contract.md

This document defines the authoritative rules for all interactable entities
in EmojiSpace. Entities represent people, places, and things the player
may directly interact with.

Once approved, this document is binding.

----------------------------------------------------------------

## 1. Purpose

The Entity System defines:

- What entities exist in the world
- How they are identified and persisted
- What interactions they expose
- How they relate to factions, locations, and other entities
- How they remember the player
- How they are symbolically represented

This system provides structure only.
It does NOT define narrative meaning, world impact, or progression.

----------------------------------------------------------------

## 2. Definition

An Entity is anything the player can directly interact with.

Entities include, but are not limited to:

- People (bartenders, pirates, traders, officials)
- Places (markets, stations, docks, warehouses, asteroids)
- Things (ships, stored cargo, facilities, special objects)

All entities use the same base structure.

----------------------------------------------------------------

## 3. Core Entity Fields (Mandatory)

Every entity MUST define:

- entity_id (string, unique, immutable)
- entity_type (enum)
- name (string)
- emoji (string)
- system_id (string)
- location_id (string or null)
- roles (list of role identifiers)
- tags (list of entity tag identifiers)
- affiliations (list of faction identifiers)
- connections (list of entity_id references)
- interaction_types (list)
- persistent_state (object)
- memory_flags (object)

----------------------------------------------------------------

## 4. Entity Types (Canonical)

Entity type determines defaults only.
Behavior is driven by roles, tags, and interactions.

Allowed values:

- person
- place
- object

No other entity types are permitted in Phase 3.

----------------------------------------------------------------

## 5. Entity Emoji

Every entity MUST define exactly one emoji.

Rules:
- Emoji is a symbolic identifier, not presentation logic
- Emoji is owned by the entity, not the UI
- Emoji is immutable after entity creation
- Emoji selection rules are defined elsewhere
- Emoji has no intrinsic meaning without interpretation

UI systems must consume, not assign, emoji.

----------------------------------------------------------------

## 6. Roles and Professions

Roles define an entity's functional capabilities and participation
in structured interactions.

A role answers the question:
"What systems is this entity allowed to participate in?"

Examples:
- bartender
- pirate
- trader
- dockmaster
- warehouse_operator
- miner
- bounty_target
- ship
- market
- shipdock
- asteroid

Rules:
- Roles are capability classifiers, not descriptive labels
- Roles gate which interaction types may be exposed
- Roles are validated by systems
- Entities may have multiple roles
- Roles change rarely and only via explicit systems
- Roles are NOT tags

Roles do NOT:
- describe disposition, intent, or attitude
- signal danger, value, or legality
- imply morality or alignment

Those concerns belong exclusively to entity tags.

----------------------------------------------------------------

## 7. Entity Tags

Entity tags describe cross-cutting traits of entities.

Rules:
- Tags are single-word identifiers
- Tags are lowercase
- Tags are selected from a controlled vocabulary
- Tags have no intrinsic behavior
- Tags are not roles

In Phase 3:
- Tags are descriptive only
- Tags do not alter economy, law, enforcement, or progression
- Tags do not trigger situations
- Tags do not advance narrative state

Future systems may interpret entity tags but may not redefine them.

----------------------------------------------------------------

## 8. Affiliations

Affiliations represent formal or informal alignment.

Examples:
- faction membership
- corporate ownership
- criminal organization
- government authority

Rules:
- Affiliations are references only
- Affiliations do not enforce behavior in Phase 3
- Multiple affiliations are allowed

----------------------------------------------------------------

## 9. Connections

Connections define explicit relationships between entities.

Examples:
- bartender -> market
- pirate -> faction
- ship -> owner
- warehouse -> station
- trader -> ship

Rules:
- Connections are directional
- Connections must reference valid entity_id values
- Connections do not imply behavior by themselves

----------------------------------------------------------------

## 10. Location-Based Entity Contexts

Locations are entities that expose structured, repeatable interactions.
Location interactions are player-initiated and transactional.

Locations do not converse.
Locations do not negotiate.
Locations do not resolve consequences.

Enforcement, legality, pricing, and outcomes are handled by other systems.


----------------------------------------------------------------
## DataNet Terminal (Location)

A DataNet Terminal is a universal information and services terminal
installed at every major installation, station, and planet.

DataNet Terminals are treated as a location type.

----------------------------------------------------------------

### 1. Core Characteristics

- DataNet Terminals are always available
- Every planet and station MUST have DataNet Terminal access
- DataNet Terminals have no physical cargo capacity
- DataNet Terminals do not host NPCs
- DataNet Terminals do not participate in markets

DataNet Terminals provide access to information and limited
system-level services.

----------------------------------------------------------------

### 2. Primary Functions

A DataNet Terminal may provide access to:
- News dissemination
- Mail and message delivery
- Event and crisis notifications
- Rare, high-impact mission offerings
- Emergency systemic services

Not all functions are guaranteed to be available at all times.

----------------------------------------------------------------

### 3. DataNet Missions

Missions surfaced via DataNet Terminals represent major events
or systemic opportunities.

Rules:
- DataNet missions are rare
- DataNet missions are not filterable by the Player Entity
- DataNet missions are typically Tier 3 to Tier 5
- DataNet missions often have substantial or unique outcomes
- DataNet missions may affect world or system state

DataNet missions represent events, not routine work.

----------------------------------------------------------------

### 4. Emergency Transport Interaction

DataNet Terminals provide an emergency transport interaction that
exists solely to prevent player dead-end states.

Interaction behavior:
- Always available
- Relocates the Player Entity to the nearest Shipdock
- Does not move ships
- Does not move cargo (physical or data)
- Does not allow destination selection
- Incurs a substantial fee

Rules:
- This interaction is not intended as a convenience feature
- This interaction may trigger enforcement or inspections on arrival
- This interaction exists only to resolve shipless states

Emergency transport does not replace normal ship travel.

----------------------------------------------------------------

### 5. Non-Responsibilities

DataNet Terminals do NOT:
- Act as a fast travel system
- Allow arbitrary relocation
- Bypass enforcement or legality
- Store or transfer cargo
- Replace ships as the primary means of travel
- Guarantee mission availability

----------------------------------------------------------------


## 10.1 Market

Purpose:
- Buy and sell goods

Primary Interactions:
- buy
- sell

Customs Enforcement:
- Customs inspection MAY trigger once, on market entry only
- No further inspections occur during buy/sell actions

Rules:
- Markets do not expose social interactions
- Markets do not allow negotiation
- Markets do not perform enforcement directly

----------------------------------------------------------------

## 10.2 Warehouse / Storage Facility

Warehouses operate in two phases: access, then usage.

### 10.2.1 Warehouse (No Access)

Purpose:
- Acquire storage rights

Primary Interaction:
- rent_storage

Rules:
- No goods may be stored or retrieved without access
- Storage access creates a persistent lease record
- Ongoing rental costs are handled by the Player Entity

### 10.2.2 Warehouse (Access Granted)

Purpose:
- Store and retrieve goods

Primary Interactions:
- store_goods
- retrieve_goods

Enforcement Visibility:
- Warehouses may be subject to inspections
- Inspection risk is lower than markets
- Inspections are system-driven, not interaction-driven

Rules:
- Warehouses do not price goods
- Warehouses do not resolve legality
- Warehouses do not trigger inspections directly

----------------------------------------------------------------

## 10.3 Shipdock

Purpose:
- Ship services and asset management

Primary Interactions:
- repair_ship
- upgrade_ship
- buy_ship
- sell_ship

Rules:
- Shipdocks do not perform enforcement
- Shipdocks do not evaluate cargo legality
- Shipdocks handle asset transfer only

----------------------------------------------------------------

## 10.4 Asteroid / Resource Node

Purpose:
- Resource extraction

Primary Interactions:
- mine
- scan

Rules:
- No commerce
- No social interaction
- Resource resolution is handled by other systems

----------------------------------------------------------------

## 10.5 Bar

Purpose:
- Social aggregation point
- Discovery of NPCs
- Access to informal or private missions

Primary Interaction:
- enter_bar (implicit or explicit)

Rules:
- Bars do not sell goods
- Bars do not perform enforcement
- All meaningful interactions are NPC-driven
- Black market access is a future system hook

----------------------------------------------------------------

## 10.6 Administration

Purpose:
- Official authority and legal affairs
- Access to lawful missions
- Voluntary legal resolution

Primary Interactions:
- talk
- turn_self_in

Rules:
- Administration does not negotiate enforcement
- Bribery is not available here
- turn_self_in creates a voluntary enforcement event
- Enforcement resolution is delegated to the Law Enforcement system

----------------------------------------------------------------

## 10.7 Bank

Purpose:
- Financial instruments and recovery paths
- Credit, debt, and risk management

Primary Interactions:
- take_loan
- repay_loan
- purchase_insurance

Availability:
- Banking services are gated by player reputation in the system

Rules:
- Loans and insurance create persistent financial records
- Ongoing payments and penalties are handled by the Player Entity
- Banks do not perform enforcement
- Default consequences are handled by future systems

----------------------------------------------------------------

## 11. Ship-to-Ship Encounter Contexts

Ship-to-ship encounters represent transient interaction contexts
between mobile entities in space.

Encounters are state-based and event-driven.
They present player choices but do not resolve outcomes.

Encounter state is defined by interaction status, not by entity identity.

----------------------------------------------------------------

## 11.1 Passive Encounter

Definition:
- Two ships encounter each other
- No interaction has been initiated
- No authority or hostility has been asserted

Passive encounters may include ships that are capable of acting
but have not yet done so.

Examples:
- civilian traffic
- traders
- pirates observing
- patrols choosing not to inspect
- bounty hunters waiting

Player-Initiated Actions:
- ignore (implicit)
- attack
- demand_surrender

Rules:
- No stance resolution is available in a passive encounter
- Passive encounters persist until an action is taken
- Identity does not determine encounter state

----------------------------------------------------------------

## 11.2 Hostile Encounter (Non-Lawful)

Definition:
- An encounter where coercive intent has been asserted
- Not initiated by lawful authority

Initiating Action:
- demand_surrender (by player or NPC)
- attack (by player or NPC)

Examples:
- piracy
- bounty interception
- hostile factions

Stance Resolution Options:
- submit
- attempt_flee
- attempt_bribe
- attack

Rules:
- Hostile encounters always enter stance resolution
- Demand is a threat, not an attack
- Attack immediately escalates to combat resolution
- Resolution is handled by other systems

----------------------------------------------------------------

## 11.3 Inspection Encounter (Lawful Enforcement)

Definition:
- An encounter initiated by lawful authority
- Purpose is inspection or compliance

Initiating Action:
- demand_surrender (framed as inspection or compliance order)

Examples:
- border patrol
- customs ships
- police

Stance Resolution Options:
- submit
- attempt_flee
- attempt_bribe
- attack

Rules:
- Inspection encounters reuse the same stance vocabulary
- Authority is defined by roles and affiliations, not by encounter type
- Resolution is delegated to the Law Enforcement system

----------------------------------------------------------------

## 11.4 Encounter Transitions

Encounter states may transition only forward:

- Passive -> Hostile
- Passive -> Inspection
- Hostile -> Combat Resolution
- Inspection -> Hostile (if resisted)

Encounters do not de-escalate without resolution.

----------------------------------------------------------------

## 11.5 Explicit Non-Responsibilities

Ship-to-ship encounters do NOT:
- Resolve combat
- Apply damage
- Seize cargo
- Arrest the player
- Modify prices
- Advance time

They exist only to:
- Present choices
- Route to resolution systems
- Record history

----------------------------------------------------------------


## 12. NPC Interaction Contexts

NPC interactions represent direct engagements between the player
and individual entities classified as people.

NPC interactions are context-driven.
NPC identity does not define behavior on its own.

Available interactions depend on:
- location context
- NPC roles
- NPC affiliations
- encounter state

NPCs do not resolve outcomes.
NPCs expose interaction opportunities only.

----------------------------------------------------------------

## 12.1 Social NPC Interaction

Definition:
- Player-initiated, voluntary interaction
- No enforcement or coercion is active

Examples:
- bartenders
- fixers
- mission givers
- potential crew
- faction representatives

Primary Interactions:
- talk
- accept_mission (if applicable)

Rules:
- Declining interaction is implicit
- No stance resolution is available
- NPCs may expose different missions based on state
- Conversation does not imply obligation

----------------------------------------------------------------

## 12.2 Administrative NPC Interaction

Definition:
- Player-initiated interaction with official or gatekeeping NPCs
- Used for permissions, access, or formal communication

Examples:
- station administrators
- licensing officials
- port authorities
- government representatives

Primary Interaction:
- talk

Rules:
- Administrative NPCs do not negotiate enforcement
- Bribery is not available in this context
- Administrative interaction may expose missions or hooks
- No automatic enforcement is triggered

----------------------------------------------------------------

## 12.3 Enforcement NPC Interaction

Definition:
- Triggered interaction initiated by lawful authority
- Player compliance or resistance is required

Examples:
- customs officers
- border inspectors
- police
- station security

Available Stance Resolution Options:
- submit
- attempt_flee
- attempt_bribe
- attack

Rules:
- Enforcement NPC interactions reuse ship-to-ship stance vocabulary
- Context determines presentation (in-person vs space)
- Resolution is delegated to the Law Enforcement system
- NPC identity does not alter stance availability

----------------------------------------------------------------

## 12.4 Detention and Judgement (Voluntary)

Definition:
- Player voluntarily submits to legal authority
- Initiated by the player, not enforcement

Context:
- Administration locations

Primary Interaction:
- turn_self_in

Rules:
- turn_self_in creates a voluntary enforcement event
- Possible outcomes include:
  - fines
  - Tier 1 detention
  - warrant resolution
- Resolution is handled by the Law Enforcement system

----------------------------------------------------------------

## 12.5 Explicit Non-Responsibilities

NPC interactions do NOT:
- Resolve combat
- Calculate prices
- Determine legality
- Apply enforcement outcomes
- Advance missions directly
- Generate narrative meaning

NPCs exist to:
- Expose interaction opportunities
- Gate access via roles and context
- Route player actions to other systems

----------------------------------------------------------------


## 12. Persistent State

Persistent state stores entity-specific data.

Examples:
- inventory references
- stored goods references
- ship status (active, idle, seized)
- dock availability
- warehouse capacity

Rules:
- Persistent state is opaque to other systems
- Other systems may read but not mutate directly
- Changes must be logged

----------------------------------------------------------------

## 13. Memory Flags

Memory flags represent what the entity remembers about the player.

Examples:
- has_met_player
- was_helped
- was_attacked
- owes_favor
- hostile
- trusted

Rules:
- Memory flags are simple boolean or enum values
- No freeform text
- No narrative interpretation
- Flags may only be set or cleared explicitly

----------------------------------------------------------------

## 14. Determinism and Persistence

Entities MUST:

- Persist across turns
- Persist across revisits
- Be serializable
- Be reproducible from logs and saves

Random generation is allowed only at world generation
or when explicitly permitted by a later-phase system.

----------------------------------------------------------------

## 15. Explicit Non-Responsibilities

The Entity System does NOT:

- Advance time
- Modify prices
- Determine legality
- Trigger enforcement
- Create situations
- Advance progression
- Generate narrative meaning

----------------------------------------------------------------

## 16. Contract Statement

This document is authoritative.

Any system that:
- Creates entities
- Reads entities
- Modifies entity state

MUST conform to this contract.

Any deviation requires updating this document first.
