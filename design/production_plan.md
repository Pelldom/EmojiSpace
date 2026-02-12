#  EmojiSpace � Production Plan (Design Authority)

**Status:** Authoritative / Binding  
**Purpose:** Control scope, sequencing, and system boundaries for EmojiSpace development

This document defines:
- Build order
- Phase boundaries
- System responsibilities
- Explicit stop / rethink criteria

No system may be implemented outside its assigned phase.
Any deviation requires updating this document first.

---

## Guiding Production Principles (Unchanged)

### Simulation before presentation
No UI polish until the simulation is provably interesting in logs.

### One new system at a time
Never introduce two tightly interacting systems in the same milestone.

### Debuggable first, fun second
If behavior cannot be explained post-hoc, it is a failure.

### Design-approved expansion only
Codex may not invent systems or logic.
All expansion must originate here.

---

## Phase Overview (Updated)

| Phase | Target Version | Focus |
|------|----------------|-------|
| Phase 0 (COMPLETED) | 0.1.x | Skeleton & scaffolding |
| Phase 1 (COMPLETED) | 0.2.x | Economy core |
| Phase 1.5 (COMPLETED) | 0.2.x | Population & market variety |
| Phase 2 (COMPLETED) | 0.3.x | Government & legality |
| **Phase 2.6 (COMPLETED)** | **0.3.x** | **Market pricing & tag interpretation** |
| **Phase 2.7 (COMPLETED)** | **0.3.x** | **Law enforcement & consequence resolution** |
| **Phase 2.8 (COMPLETED)** | **0.3.x** | **End goals foundation** |
| **Phase 3 (COMPLETED)** | **0.4.x** | **NPC persistence** |
| Phase 3.1 (COMPLETED) | 0.4.x | Time Engine |
| **Phase 3.2 (COMPLETED)** | **0.4.x** | **Prose and world texture layer** |
| **Phase 4 (COMPLETED)** | **0.5.0** | **Travel and Encounter Scaffolding** |
| **Phase 4.2 (COMPLETED)** | **0.6.0** | **Ship and Module Data Layer** |
| **Phase 4.x (COMPLETED)** | **0.6.0** | **Combat Resolver + deterministic sim harness + tests** |
| Phase 5 | 0.6.x | Emergent narrative |
| Phase 6 | 0.7�0.9.x | Stabilization & balance |

---

## Phase 0 � Skeleton & Scaffolding (COMPLETED)

**Target:** 0.1.x

### Objective
Prove the project can:
- Generate a sector
- Advance time
- Execute player turns
- Log outcomes deterministically

### Required Systems
- World generator (systems + planets)
- Turn loop
- Player entity
- Movement
- Logging framework
- VERSION tracking

### Explicit Exclusions
- Economy logic
- NPCs
- Governments
- Situations
- UI beyond logs

### Benchmark to Advance
- 100+ turns execute without crash
- Logs clearly show state transitions

---

## Phase 1 � Economy Core (COMPLETED)

**Target:** 0.2.x

### Objective
Introduce a living economy based on supply, demand, and scarcity.

### Required Systems
- Goods catalog
- Category system
- Economy definitions
- Market creation (static)
- Player trading loop (buy / sell)

### Explicit Exclusions
- Governments
- Legality
- Pricing interpretation
- NPC traders
- Situations

### Benchmark to Advance
- Prices respond to scarcity
- Player actions influence markets
- Changes are explainable

---

## Phase 1.5 � Population & Market Variety (COMPLETED)

**Target:** 0.2.x

### Objective
Control market breadth without implying wealth or advancement.

### Required Systems
- Population levels (1�5)
- Goods-per-category caps
- Neutral category resolution

### Explicit Exclusions
- Pricing logic
- Governments
- Risk or legality

### Benchmark to Advance
- Population affects variety only
- No population-based price scaling

---

## Phase 2 � Government & Legality (COMPLETED)

**Target:** 0.3.x

### Objective
Make place matter via law, ideology, and enforcement.

### Required Systems
- Government archetypes
- Legality matrix
- Restricted vs illegal states
- Ideological modifiers

### Explicit Exclusions
- Pricing interpretation
- Enforcement outcomes
- NPC memory
- Situations

### Benchmark to Advance
- Same action yields different legality by system
- Outcomes are predictable but not avoidable

---

## Phase 2.6 � Market Pricing & Tag Interpretation (COMPLETED)

**Target:** 0.3.x

### Objective
Define how prices are calculated and how governments interpret tags.

### Required Systems
- Market pricing contract
- SKU-based buying
- Category-based selling
- Substitute discount logic
- Deterministic pricing
- Tag interpretation (price bias, risk signaling)
- Government � tag interpretation
- Category pressure multipliers (coarse, deterministic)
- Salvage floor enforcement

### Explicit Exclusions
- Enforcement consequences
- Situational demand spikes
- Cultural valuation
- NPC behavior

### Benchmark to Advance
- All prices are explainable from logs
- No double counting of effects
- Cursor can implement without inference

---

## Phase 2.7 � Law Enforcement & Consequence Resolution (COMPLETED)

**Target:** 0.3.x

### Objective
Resolve the consequences of risky or illegal actions.

### Required Systems
- Enforcement trigger logic
- Risk tier consumption
- Consequence resolution (fines, confiscation, arrest, reputation)
- Use of government enforcement and penalty fields

### Explicit Exclusions
- Price recalculation
- Market composition changes
- Situations
- Narrative arcs

### Benchmark to Advance
- Risk leads to meaningful outcomes
- Enforcement respects government traits
- Pricing and law remain decoupled

---

## Phase 2.8 End Goals Foundation (COMPLETED)

**Target:** 0.3.x

### Objective
Establish the required end goals foundation systems that enable win/lose
conditions and progression targets.

### Required Systems
- Player Entity (PE) - **IMPLEMENTED**
- Ship Entity (SE) - **IMPLEMENTED**
- Missions System - **IMPLEMENTED**
- Goods Storage System (Warehousing) - **IMPLEMENTED**
- Unused / Idle Ships System - **IMPLEMENTED**

### Explicit Exclusions
- NPC persistence
- Situations
- Emergent narrative
- UI beyond logs

### Benchmark to Advance
- End goals foundation systems exist as state holders and orchestration points
- Missions can target progression tracks and victory conditions
- Storage and idle ship risk are representable in logs

### Completion Status
End goals foundation is now functional and test-covered. End game evaluation system implemented (read-only, deterministic). Victory missions defined via `/data/victory_missions.json`. Failure penalties and tracker drops explicitly supported. Victory missions are Tier 5, multi-source, and slot-aware.

---

## Required Supporting Systems (End Goals)

The following systems are REQUIRED to support win/lose conditions,
progression tracks, and victory missions. These are not optional flavor.

### Player Entity (PE) (Required)
Responsibilities:
- Tracks player state required for progression and win conditions
- Stores all six progression tracks: Trust, Notoriety, Entrepreneur, Criminal, Law, Outlaw
- Tracks current ship assignment
- Tracks credits and economic state
- Tracks per-system reputation references (but does not own reputation logic)
- Tracks arrest state and loss eligibility
- Tracks titles or tags earned per progression threshold (player-facing only)

Clarifications:
- The PE does not resolve combat, economy, or reputation mechanics
- The PE is a state holder consumed by other systems
- The PE is required before missions, combat, economy, or UI systems can be built

### Ship Entity (SE) (Required)
Responsibilities:
- Represents a single ship owned or used by the player
- Tracks ship status (active, idle, destroyed, seized)
- Tracks cargo capacity and stored goods
- Tracks ship location
- Tracks Threat Rating classification (used by combat and progression systems)

Clarifications:
- Players may own multiple ships
- Only one ship is active at a time
- Idle ships are persistent assets
- Idle ships can store goods
- Idle ships can be discovered, seized, or destroyed
- Ship Entity does not define combat mechanics at this stage

### Missions System (Required)
Responsibilities:
- Drive progression for Trust and Notoriety tracks
- Serve as the primary mechanism for intentional progression and redemption
- Provide Victory Missions that finalize a win
- Support lawful, criminal, economic, and combat oriented missions
- Be explicitly outcome based (success, failure, abandonment)

Missions are a core progression and endgame system.

### Goods Storage System (Warehousing) (Required)
Responsibilities:
- Allow goods to be stored at locations (stations, facilities)
- Allow goods to be stored on unused or idle ships
- Storage persists across turns
- Stored goods are subject to legality, seizure, loss, and discovery
- Required to support Entrepreneur and Criminal economic tracks

This system is required even if full production or industry systems do not yet exist.

### Unused / Idle Ships System (Required)
Responsibilities:
- Players may own more than one ship
- Ships not currently piloted are considered idle
- Idle ships can store goods
- Idle ships can be seized, destroyed, or discovered
- Idle ships may be used as part of economic and criminal progression

Idle ships are assets with risk, not abstract inventory.

---

## Phase 3 NPC Persistence (COMPLETED)

**Target:** 0.4.x

### Objective
Populate the sector with persistent, memory-bearing NPCs.

### Required Systems
- NPC generation
- Roles & professions
- Memory flags
- Relationship states
- NPC movement

### Additional Required Systems (Phase 3 Prerequisites)
The following systems must be in place before Phase 3 can complete:
- Player Entity (PE)
- Ship Entity (SE)
- Missions System
- Goods Storage System (Warehousing)
- Unused / Idle Ships System

### Explicit Exclusions
- Situational role spawning
- Narrative arcs

### Benchmark to Advance
- NPCs react based on history
- NPC loss has downstream effects

### Phase 3 Completion (Locked)
Phase 3 scope is complete and locked.
Entity, NPC, Mission, Ship, DataNet, and PE contracts are authoritative.

### Completion Status
NPC Entity, Registry, Placement, and deterministic guarantees implemented. NPCs persist across turns with memory and relationship states.

---

## Phase 3.1 � Time Engine (COMPLETED)

**Target:** 0.4.x

### Objective
Establish the authoritative time system with explicit turn progression and daily tick order.

### Required Systems
- Time Engine (contract-defined, deterministic)

### Explicit Exclusions
- Any autonomous time advancement
- Any calendar-based logic

### Benchmark to Advance
- Time advances only via explicit player actions
- Daily tick order is deterministic and logged

---

## Phase 3.2 Prose and World Texture Layer (COMPLETED)

**Target:** 0.4.x

### Objective
Provide a presentation-only layer for names, descriptions, dialogue, and world reflection.

### Required Systems
- Prose and world texture layer (read-only, non-authoritative)

### Explicit Exclusions
- Any mutation of simulation state
- Any effect on mechanics, outcomes, legality, risk, economy, or time

### Clarifications
- This layer is required for immersion, not simulation.
- This layer is not a blocker for Situations, Events, or NPC persistence.
- Phase 3.2 is LOCKED once prose_contract.md exists.

### Completion Status
DataNet feed, prose generator, and victory mission prose support implemented. Prose layer provides read-only presentation for names, descriptions, dialogue, and world reflection.

---

## Phase 4 - Travel and Encounter Scaffolding (COMPLETED)

**Status:** COMPLETE  
**Version Achieved:** 0.5.0

### Completed Components
- Travel encounter loop (population cap and diminishing probability)
- Enforcement-based authority scaling
- Deterministic encounter generation
- Interaction dispatch layer
- Reaction engine with TR and reputation integration
- Reward materialization system
- Pursuit resolver (speed, cloak, interdiction, pilot skill)
- Unified deterministic integration test

---

## Phase 4.2 - Ship and Module Data Layer (COMPLETED)

**Status:** COMPLETE  
**Version Achieved:** 0.6.0

### Completion Summary
- Unified ship and module schema contract created.
- Bias values moved into hull JSON structure.
- Cargo (physical and data) explicitly defined per hull.
- Base pricing added for hulls and modules.
- Secondary distribution formally defined.
- Salvage mutation rules (unstable injection) defined.
- Inactive ship module stripping rule defined.
- NPC parity rule reinforced at schema level.
- No behavior implemented yet (structure only).

---

## Phase 4.x - Combat Resolver (COMPLETED)

**Status:** COMPLETE  
**Version Achieved:** 0.6.0

### Completed Components
- Standalone combat resolver module with deterministic RNG and round logs
- TR derivation (RCP -> TR) implemented for both player and NPC loadouts
- Combat repair, degradation, RED override, scan placeholder, surrender, and destruction outcomes
- Escape integration adapter invoking pursuit resolver path
- Deterministic CLI combat simulation harness with canned scenario loadouts
- Unit tests for determinism, TR mapping, repair usage, degradation thresholds, and escape integration

---

## Phase 5 � Emergent Narrative

**Target:** 0.6.x

### Objective
Allow stories to coalesce naturally from systems.

### Required Systems
- Narrative triggers
- Long-arc tracking
- Optional player engagement

### Benchmark to Advance
- Distinct stories can be described after a run
- Player absence matters

---

## Phase 6 � Stabilization & Balance

**Target:** 0.7�0.9.x

### Objective
Turn a complex simulation into a playable game.

### Focus Areas
- Balance tuning
- Information surfacing
- Failure fairness
- Performance
- Save compatibility

### Benchmark for 1.0 Consideration
- Multiple viable playstyles
- No dominant strategy
- Bugs are reproducible
- Design intent matches behavior

---

## Authority Statement

This document is **authoritative**.

Any feature, system, or behavior:
- Must belong to a defined phase
- Must respect phase boundaries
- Must update this document if altered

Failure to do so is a design failure.
