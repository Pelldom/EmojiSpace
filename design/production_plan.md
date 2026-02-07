#  EmojiSpace — Production Plan (Design Authority)

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
| Phase 0 | 0.1.x | Skeleton & scaffolding |
| Phase 1 | 0.2.x | Economy core |
| Phase 1.5 | 0.2.x | Population & market variety |
| Phase 2 | 0.3.x | Government & legality |
| **Phase 2.6** | **0.3.x** | **Market pricing & tag interpretation** |
| **Phase 2.7** | **0.3.x** | **Law enforcement & consequence resolution** |
| Phase 3 | 0.4.x | NPC persistence |
| Phase 4 | 0.5.x | Situations & propagation |
| Phase 5 | 0.6.x | Emergent narrative |
| Phase 6 | 0.7–0.9.x | Stabilization & balance |

---

## Phase 0 — Skeleton & Scaffolding

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

## Phase 1 — Economy Core

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

## Phase 1.5 — Population & Market Variety

**Target:** 0.2.x

### Objective
Control market breadth without implying wealth or advancement.

### Required Systems
- Population levels (1–5)
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

## Phase 2 — Government & Legality

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

## Phase 2.6 — Market Pricing & Tag Interpretation

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
- Government × tag interpretation
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

## Phase 2.7 — Law Enforcement & Consequence Resolution

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

## Phase 3 — NPC Persistence

**Target:** 0.4.x

### Objective
Populate the sector with persistent, memory-bearing NPCs.

### Required Systems
- NPC generation
- Roles & professions
- Memory flags
- Relationship states
- NPC movement

### Explicit Exclusions
- Situational role spawning
- Narrative arcs

### Benchmark to Advance
- NPCs react based on history
- NPC loss has downstream effects

---

## Phase 4 — Situations & Propagation

**Target:** 0.5.x

### Objective
Make the sector self-destabilizing.

### Required Systems
- Situations (war, plague, unrest)
- Situation triggers
- Time-based resolution
- Economic, legal, and NPC effects

### Explicit Exclusions
- Authored storylines
- Unique items

### Benchmark to Advance
- Situations emerge organically
- Ignoring them has consequences

---

## Phase 5 — Emergent Narrative

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

## Phase 6 — Stabilization & Balance

**Target:** 0.7–0.9.x

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
