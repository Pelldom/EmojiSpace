# EmojiSpace - NPC Entity Contract

Status: DRAFT (Evolving)
Phase: 3
Applies To: NPC entities only

This document defines the structure, persistence tiers, and
responsibilities of NPC entities in EmojiSpace.

NPCs are entities that provide continuity, context, and interaction
anchors. NPCs do not resolve outcomes or perform system logic.

----------------------------------------------------------------

## 1. Core Definition

An NPC is an entity representing a person that the player may
encounter, interact with, or reference over time.

NPCs may:
- expose interaction opportunities
- hold identity and affiliation
- persist across encounters
- move between locations
- be referenced by missions or events

NPCs do NOT:
- resolve combat
- enforce law
- determine prices
- apply rewards
- advance missions automatically
- decide outcomes

----------------------------------------------------------------

## 2. NPC Persistence Tiers

NPCs are divided into three persistence tiers.

Persistence tier determines:
- whether an NPC has an ID
- how long the NPC persists
- how much memory the NPC retains

----------------------------------------------------------------

### 2.1 Tier 1 NPCs - Fleeting

Definition:
- Background or functional NPCs
- Exist only for the duration of an interaction

Examples:
- unnamed bartenders
- customs officers
- generic traders
- background pirates

Rules:
- Tier 1 NPCs do NOT have persistent IDs
- Tier 1 NPCs are not saved
- Tier 1 NPCs hold no memory
- Tier 1 NPCs may be freely generated and discarded

Tier 1 NPCs represent roles, not individuals.

----------------------------------------------------------------

### 2.2 Tier 2 NPCs - Limited Persistence

Definition:
- Named or semi-important NPCs
- Persist for a limited scope

Examples:
- mission givers
- fixers
- notable bartenders
- temporary allies
- local administrators

Characteristics:
- Have a persistent NPC ID
- May persist beyond a single interaction
- Persistence may expire after conditions are met

Memory:
- Small set of flags only
- Examples:
  - met_player
  - mission_active
  - mission_completed
  - hostile
  - cooperative

Rules:
- Tier 2 NPCs may be removed when no longer relevant
- Tier 2 NPCs do not maintain full event logs
- Tier 2 NPCs may be promoted or retired

----------------------------------------------------------------

### 2.3 Tier 3 NPCs - Persistent Figures

Definition:
- Important or narrative-significant NPCs

Examples:
- faction leaders
- famous pirates
- long-term allies
- crew members
- celebrities
- recurring antagonists

Characteristics:
- Have stable, permanent NPC IDs
- Persist indefinitely unless explicitly removed
- May impact multiple systems and storylines

Memory:
- Reference to substantial event history
- May record:
  - major interactions
  - betrayals
  - alliances
  - long-term reputation effects

Rules:
- Tier 3 NPCs are never auto-expired
- Tier 3 NPCs may evolve over time
- Tier 3 NPCs may move freely if logically permitted

----------------------------------------------------------------

## 3. Identity and Core Fields

Persistent NPCs (Tier 2 and Tier 3) MUST have:

- npc_id (unique identifier)
- persistence_tier (2 or 3)
- display_name
- role_tags (e.g. bartender, pirate, administrator)
- affiliation_ids (optional)
- current_location_id or current_ship_id

Tier 1 NPCs do not require these fields.

----------------------------------------------------------------

## 4. Roles and Tags

NPC behavior and interaction exposure is defined by tags.

Examples:
- bartender
- customs_officer
- pirate
- trader
- mission_giver
- crew_candidate
- administrator

Rules:
- Tags describe capability, not logic
- NPCs do not execute behavior
- Other systems interpret tags

----------------------------------------------------------------

## 5. Affiliation

NPCs may be affiliated with:
- factions
- governments
- organizations
- other NPCs

Rules:
- Affiliation influences how systems treat the NPC
- NPCs do not interpret affiliation themselves

----------------------------------------------------------------

## 6. Location and Movement

NPCs may be:
- bound to a location
- bound to a ship
- mobile across systems

Rules:
- Movement must be logically justified
- System administrators are typically location-bound
- Pirates, traders, and explorers may move freely
- Movement is controlled by systems, not NPCs

----------------------------------------------------------------

## 7. Interaction Participation

NPCs may be involved in:
- location-based interactions
- ship-to-ship encounters
- missions and events

Rules:
- NPCs expose interaction options
- NPCs do not resolve interactions
- Interaction outcomes are handled elsewhere

----------------------------------------------------------------

## 8. Memory and History

NPC memory depends on persistence tier.

Tier 1:
- No memory

Tier 2:
- Limited flags only
- No full history tracking

Tier 3:
- May reference event logs
- May accumulate long-term state

NPCs do not analyze or act on memory autonomously.

----------------------------------------------------------------

## 9. Promotion and Demotion

NPCs may change persistence tier.

Examples:
- Tier 1 promoted to Tier 2 when named
- Tier 2 promoted to Tier 3 when narratively significant
- Tier 2 retired after mission completion

Rules:
- Promotion requires explicit system action
- Demotion or removal must be deliberate

----------------------------------------------------------------

## 10. Explicit Non-Responsibilities

NPC entities do NOT:
- resolve combat or enforcement
- grant rewards directly
- advance missions
- calculate prices
- store world logic
- manage player progression

NPCs are state holders and reference anchors only.

----------------------------------------------------------------

## 11. Evolution Notes

This contract is intentionally incomplete.

Future phases may add:
- dialogue systems
- relationship scoring
- crew mechanics
- advanced faction interaction
- narrative branching

All additions MUST preserve the principle that
NPCs expose context but do not resolve outcomes.


----------------------------------------------------------------
## NPC Generation Notes (Advisory)

This section provides non-binding guidance for how NPCs
may be generated and surfaced in locations and encounters.

These notes describe intent and world texture.
They do not define NPC behavior or outcomes.

----------------------------------------------------------------

### 1. NPC Presence Philosophy

NPC generation should favor:
- plausibility
- uneven distribution
- contextual appearance
- discovery over guarantees

However, certain roles are considered structurally required
for specific locations.

----------------------------------------------------------------

### 2. NPC Generation by Location Type

#### Bars

Rules:
- Every Bar MUST have exactly one bartender NPC
- The bartender is always present
- The bartender is typically Tier 2

Additional NPCs:
- Bars may generate additional NPCs such as:
  - fixers
  - smugglers
  - mercenaries
  - rumor brokers
  - independent traders
- These additional NPCs:
  - are often Tier 1 or Tier 2
  - may or may not be present on each visit

Bars are the primary hub for informal mission discovery.

----------------------------------------------------------------

#### Administration

Rules:
- Every Administration location MUST have exactly one Administrator NPC
- The Administrator is always present
- The Administrator is typically Tier 2 or Tier 3

Additional NPCs:
- Administration may include:
  - government agents
  - faction representatives
  - customs officials
- These NPCs are fewer in number and more stable

Administration NPCs are formal, authoritative, and visible.

----------------------------------------------------------------

#### Planets and Stations

- Planets and stations function identically for NPC generation
- NPC presence depends entirely on available locations:
  - Bar
  - Administration
- No planet-specific NPC rules are required

----------------------------------------------------------------

### 3. Ship-to-Ship Encounter NPCs

NPCs may be generated dynamically during ship-to-ship encounters.

Examples:
- pirates
- traders
- patrol officers
- explorers
- distress callers

Rules:
- Encounter NPCs are generated as Tier 1 by default
- An encounter NPC MAY offer a mission

Mission offer behavior:
- If the player ACCEPTS the mission:
  - The NPC is immediately promoted to Tier 2
  - The NPC becomes persistent
- If the player DECLINES the mission:
  - The mission is discarded
  - The NPC is discarded
  - No second offer is possible

Encounter-based NPCs are single-opportunity interactions.

----------------------------------------------------------------

### 4. Persistence Tier Distribution (Clarified)

Typical expectations:

- Tier 1 NPCs:
  - background characters
  - unnamed encounter NPCs
  - disposable and non-persistent

- Tier 2 NPCs:
  - bartenders
  - administrators
  - mission givers
  - promoted encounter NPCs
  - limited memory and scope

- Tier 3 NPCs:
  - important figures
  - faction leaders
  - long-term allies or antagonists
  - persistent across large narrative arcs

Promotion between tiers must be explicit and deliberate.

----------------------------------------------------------------

### 5. NPC Refresh and Turnover

Rules:
- Required NPCs (bartender, administrator) are stable
- Non-required NPCs may change based on:
  - time passage
  - leaving and re-entering a system
  - mission completion
  - world state changes

NPC disappearance without explanation is acceptable
for non-required NPCs.

----------------------------------------------------------------

### 6. World State Sensitivity

NPC generation may consider world conditions such as:
- plagues
- economic distress
- faction control
- recent major events
- enforcement pressure

World state may influence:
- which non-required NPCs appear
- how frequently encounter NPCs occur
- which mission offers are possible

These influences are probabilistic, not guaranteed.

----------------------------------------------------------------

### 7. Non-Goals

NPC generation rules do NOT aim to:
- guarantee mission availability beyond required NPCs
- prevent empty or quiet locations
- simulate daily schedules or routines
- ensure fairness or balance of NPC offerings

NPCs exist to provide interaction anchors,
not to simulate populations.

----------------------------------------------------------------

## 12. Contract Authority

This document is authoritative for NPC persistence.

Changes require:
- explicit revision
- version update
- review before Cursor implementation
