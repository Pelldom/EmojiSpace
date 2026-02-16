#  EmojiSpace - Production Plan (Design Authority)

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
| **Phase 4.4 (COMPLETED)** | **0.6.2** | **Data Validation and Integration** |
| **Phase 4.5 (COMPLETED)** | **0.6.3** | **Deterministic Ship Assembler (scope C)** |
| **Phase 4.6 (COMPLETED)** | **0.6.4** | **Combat integration with deterministic assembler** |
| **Phase 4.7 (COMPLETED)** | **0.6.5** | **Deterministic shipdock inventory generator** |
| **Phase 4.8 (COMPLETED)** | **0.7.0** | **Fuel system integration and refuel interaction** |
| **Phase 4.9 (COMPLETED)** | **0.7.1** | **Shipdock interaction extensions** |
| **Phase 4.9.1 (COMPLETED)** | **0.7.2** | **Secondary tag resale multipliers** |
| **Phase 4.11 (COMPLETED)** | **0.8.0** | **NPC ship generation and salvage** |
| **Phase 4.11.1 (COMPLETED)** | **0.8.1** | **Stabilization and orchestration patch (boundary cleanup + single-authority consolidation + playable CLI wiring)** |
| **Phase 4.11.2 (COMPLETED)** | **0.8.2** | **Structural consolidation (SimulationController authority + harness consolidation)** |
| **Phase 4.x (COMPLETED)** | **0.6.0** | **Combat Resolver + deterministic sim harness + tests** |
| Phase 5 - Crew and Social Systems (COMPLETED) | 0.9.10 | Crew and Social Systems |
| Phase 6 - Situations, Events, and Dynamic World State (IN DESIGN) | 0.10.0 | Situations, Events, and Dynamic World State |
| Phase 7 | 1.1.x | UI Framework (Android + Emoji Integration) |
| Phase 8 | 1.2.x | Monetization and Play Store Deployment |

---

## Phase 0 - Skeleton & Scaffolding (COMPLETED)

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

## Phase 1 - Economy Core (COMPLETED)

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

## Phase 1.5 - Population & Market Variety (COMPLETED)

**Target:** 0.2.x

### Objective
Control market breadth without implying wealth or advancement.

### Required Systems
- Population levels (1-5)
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

## Phase 2 - Government & Legality (COMPLETED)

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

## Phase 2.6 - Market Pricing & Tag Interpretation (COMPLETED)

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
- Government - tag interpretation
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

## Phase 2.7 - Law Enforcement & Consequence Resolution (COMPLETED)

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

## Phase 3.1 - Time Engine (COMPLETED)

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

## Phase 4.4 - Data Validation and Integration (COMPLETED)

**Status:** COMPLETE  
**Version Achieved:** 0.6.2

### Completed Components
- Added load-time hull and module schema validation with explicit erroring.
- Added automated tests for hull and module data validation coverage.
- Enforced required field presence and type constraints for hull and module catalogs.
- Enforced module slot_type and primary_tag alignment constraints at data load.
- Enforced numeric_bonus cap and tier-based crew_capacity band validation.

---

## Phase 4.5 - Deterministic Ship Assembler (scope C) (COMPLETED)

**Status:** COMPLETE  
**Version Achieved:** 0.6.3

### Completed Components
- Deterministic slot distribution and assignment implementation for hull + module instances.
- Compact slot math and untyped slot allocation rules enforced.
- Deterministic module bonus aggregation with secondary modifiers.
- Subsystem degradation capacity computation and RED override integration.
- Deterministic ship utility effect outputs for ship utility tags.
- Automated unit tests for assembler behavior and contract-constrained edge cases.

---

## Phase 4.6 - Combat Integration with Assembler (COMPLETED)

**Status:** COMPLETE  
**Version Achieved:** 0.6.4

### Completed Components
- Combat resolution refactored to consume assembler effective bands as authority.
- Duplicate combat-side band/capacity/RED math removed from runtime resolution path.
- Degradation updates retained in combat with RED state derived from assembler outputs.
- Integration tests added to validate deterministic behavior and assembler coupling.

---

## Phase 4.7 - Deterministic Shipdock Inventory Generator (COMPLETED)

**Status:** COMPLETE  
**Version Achieved:** 0.6.5

### Completed Components
- Deterministic shipdock module and hull inventory generation by world_seed/system_id/population.
- Population-based stock chance gates and inventory breadth limits enforced.
- Weighted, without-replacement module and hull selection implemented.
- Rare module caps enforced by population with deterministic replacement behavior.
- Purchase bans and defensive filtering applied for prohibited inventory entries.

---

## Phase 4.8 - Fuel System Integration (COMPLETED)

**Status:** COMPLETE  
**Version Achieved:** 0.7.0

### Completed Components
- Added explicit per-hull base fuel capacity field in hull data and load-time validation.
- Added ship utility module support for `ship:utility_extra_fuel`.
- Extended deterministic ship assembly output with final `fuel_capacity`.
- Added persistent ship fuel state (`current_fuel`) with strict bounds invariant.
- Added deterministic travel fuel consumption/rejection flow including emergency transport bypass.
- Added refuel interaction helpers with DataNet-gated action availability and fixed unit pricing.

---

## Phase 4.9 - Shipdock Interaction Extensions (COMPLETED)

**Status:** COMPLETE  
**Version Achieved:** 0.7.1

### Completed Components
- Added Shipdock-gated interaction actions: buy/sell hull, buy/sell module, and repair ship.
- Enforced physical presence checks for ships at destination before shipdock actions execute.
- Added deterministic buy/sell pricing paths with modifier hook for sale operations.
- Added assembler-validated module purchase flow with rejection on slot constraint failures.
- Added repair cost flow based on hull damage, subsystem degradation, and population modifier.

---
## Phase 4.9.1 - Secondary Tag Resale Multipliers (COMPLETED)

**Status:** COMPLETE  
**Version Achieved:** 0.7.2

### Completed Components
- Added module resale multipliers for `secondary:prototype` and `secondary:alien`.
- Applied multipliers multiplicatively when both tags are present.
- Restricted multiplier behavior to module resale only.

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

### Phase 4.9 - Shipdock Interaction Extensions (0.7.1)

- Added buy/sell hull logic
- Added buy/sell module logic
- Added repair system with multi-factor cost
- Enforced physical location constraints
- Added price modifier hook placeholder

---
# production_plan.md (add this section)

## Phase 4.11 - NPC Ship Generation and Salvage (COMPLETED)

**Status:** COMPLETE  
**Version Achieved:** 0.8.0

### Completed Components
- Added deterministic NPC ship generation using isolated RNG streams and assembler-backed ship state.
- Added deterministic salvage resolver with weighted salvage count, rarity/secondary weighting, and unstable injection constraints.
- Integrated combat destruction outcomes with `salvage_modules` payload output.
- Preserved reward profile schema and reward materialization boundaries.
- Added focused tests for generation determinism, salvage rules, and combat salvage integration.

## Phase 4.11.1 - Stabilization and Orchestration Patch (COMPLETED)

**Status:** COMPLETE
**Version Achieved:** 0.8.1

Patch phase under 4.11. No new mechanics; boundary cleanup + orchestration wiring only.

### Completed Components
- Boundary cleanup across existing Phase 2.7-4.11 systems.
- Single-authority consolidation for duplicated runtime logic paths.
- Minimal playable CLI wiring across already-implemented simulation systems.

## Phase 4.11.2 - Structural Consolidation (COMPLETED)

**Status:** COMPLETE
**Version Achieved:** 0.8.2

### Completed Components
- Added `SimulationController` as single orchestration authority for command execution.
- Consolidated CLI runner to `cli_run.py` and reduced legacy harness entry points.
- Centralized shared tag interpretation logic into `tag_policy_engine.py`.
- Moved hull max authority into ship assembler output and removed combat-local duplicate.
- Added deterministic SimulationController end-to-end coverage.

## Phase 5 - Crew and Social Systems

**Target:** 0.9.x

### Objective
Introduce deterministic crew as a simulation layer extension without adding narrative or UI dependencies.

### Scope
- Implement hireable crew system.
- Enforce crew_capacity usage in Ship Entity.
- Define crew roles (mechanic, gunner, navigator, etc.).
- Crew provide additive deterministic stat modifiers only.
- Crew recruitment sources:
  - Bar locations.
  - Encounter locations.
  - Rare random encounters.
- Crew persist attached to player ship.
- Deterministic crew generation required.

### Explicit Exclusions
- No loyalty or morale system yet.
- No crew betrayal system.
- No crew death mechanics.
- No narrative arcs tied to crew (deferred to Phase 6).
- No UI implementation.

## Phase 5 - Crew and Social Systems (COMPLETED)

Completion Summary:

- Hireable crew system implemented.
- Crew stored as Tier 2 NPCs attached to ships.
- Crew capacity enforced via hull crew_capacity.
- Roles and tags defined and centralized.
- Deterministic Crew Modifier Aggregation Engine implemented.
- Crew effects integrated into:
  - Travel fuel consumption.
  - Cargo and data capacity.
  - Combat bands and focus actions.
  - Market pricing.
  - Mission slot availability.
  - Law enforcement (lawyer Tier 2 downgrade).
  - Pre-travel wage enforcement.
- All crew mechanical effects centralized through compute_crew_modifiers().
- No system layers directly inspect crew roles or tags.
- Determinism preserved across all integrations.
- Full structural compliance audit passed.
- Full test suite passing (145 tests).

---

## Phase 6 - Events, Situations, and Mission Arcs

**Target:** 0.10.0

## Phase 6 - Situations, Events, and Dynamic World State (IN DESIGN)

- Introduces deterministic World State layer
- Adds Situations (persistent modifiers)
- Adds Events (discrete mutations)
- Adds domain-typed ModifierEntry system
- Adds severity tier model (1-5)
- Adds spawn gate with configurable frequency (Low 5%, Normal 8%, High 10%)
- Enforces Worldgen Lock structural persistence
- Integrates with Time Engine via daily evaluation
- Maintains strict authority boundaries (Government, Pricing, Population, Travel, Ship Systems)

Event and Situation architecture finalized.
Implementation pending.
Phase 6 - Slice 1 Core WorldStateEngine (COMPLETED)
Phase 6 - Slice 2 Random Situation Spawn (COMPLETED)
Patch: unified spawn gate implements 70/30 Situation vs Event outcome split per contract.
Phase 6 - Spawn Gate Repair (COMPLETED)
Phase 6 - Slice 3 Event Execution Layer (COMPLETED)
Phase 6 - Slice 4 Scheduled Event Execution (COMPLETED)
Phase 6 - Slice 5 Propagation Execution (COMPLETED)
Phase 6 - Slice 6 TimeEngine Integration (COMPLETED)
Phase 6 - Slice 7 Shared Modifier Resolver (COMPLETED)
Phase 6 - Slice 8 Goods Pricing Consumption (COMPLETED)
Phase 6 - Slice 9 Mission Weight Consumption (COMPLETED)
Phase 6 - Slice 10 Shipdock Inventory Consumption (COMPLETED)

### Objective
Expand simulation continuity through persistent event pressure, mission progression, and narrative consequence layering.

### Scope
- Situational system (system-wide conditions).
- Event engine with triggers.
- Multi-stage mission arcs.
- Branching encounter chains.
- Persistent narrative consequences.
- Faction evolution.
- NPC promotions/demotions.
- Reputation ripple effects.

### Explicit Exclusions
- No UI framework.
- No monetization systems.

---

## Phase 7 - UI Framework (Android + Emoji Integration)

**Target:** 1.0.x

### Objective
Add a deterministic presentation and interaction layer that consumes simulation authority without introducing mechanics.

### Scope
- Presentation adapter layer.
- Emoji metadata integration into schema: via Emoji Profiles
  - emoji_profile_contract.md
  - Ship frames.
  - Modules.
  - SKUs.
  - Tags.
  - Destination types.
  - Location types.
- Touch interaction routing.
- Android wrapper.
- Deterministic action/result interface boundary.

### Constraints
- No simulation mechanics in UI layer.
- No RNG in UI layer.
- UI consumes SimulationController only.

### Future Enhancements
For future addtion of adventure packages, or theme packs and general additions to increase lore, flavour, and options.

- build architechture to allow for easy addtion of:
  - new/expanded missions
  - new/expanded encounters
  - new/expanded Situations
  - new/expanded Events
---

## Phase 8 - Monetization and Play Store Deployment

**Target:** 1.1.x

### Objective
Prepare commercial packaging and monetization with strict isolation from simulation outcomes.

### Scope
- Banner ad integration.
- Premium no-ads purchase option.
- Premium flag stored in Player Entity.
- Ads must not affect simulation outcomes.
- Ads must not alter RNG, pricing, enforcement, or rewards.
- Build preparation for Play Store.
- Release packaging and version gating.

### Constraints
- Monetization strictly isolated to UI layer.
- No gameplay advantage tied to purchase.

---

Current Development Version: 0.10.0
Event and Situation architecture finalized.
Implementation pending.

## Authority Statement

This document is **authoritative**.

Any feature, system, or behavior:
- Must belong to a defined phase
- Must respect phase boundaries
- Must update this document if altered

Failure to do so is a design failure.
