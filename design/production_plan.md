EmojiSpace — Production Plan (Design Authority)
Purpose of this document

This production plan defines:

The order of construction

The systems dependency chain

Clear benchmarks and quality gates

Explicit stop / rethink criteria

Version targets tied to milestones

The goal is to prevent premature complexity, uncontrolled scope growth, and hard-to-debug emergent failures.

Guiding Production Principles

Simulation before presentation
No UI polish until the simulation is provably interesting in logs.

One new system at a time
Never introduce two interacting systems in the same milestone.

Debuggable first, fun second
If behavior cannot be explained, it is a failure regardless of “coolness”.

Design-approved expansion only
Codex may not invent systems. All expansion must originate here.

Phase Overview
Phase	Target Version	Focus
Phase 0	0.1.x	Skeleton & scaffolding
Phase 1	0.2.x	Economy core
Phase 2	0.3.x	Government & legality
Phase 3	0.4.x	NPC persistence
Phase 4	0.5.x	Situations & propagation
Phase 5	0.6.x	Emergent narrative
Phase 6	0.7–0.9.x	Stabilization & balance
Phase 0 — Skeleton & Scaffolding

Target: 0.1.x

Objective

Prove the project can:

Generate a sector

Advance time

Execute a player turn

Log outcomes deterministically

Required Systems

Sector generator (systems + planets, minimal attributes)

Turn loop

Player entity

Movement between systems

Logging framework

/VERSION integration

Explicit Exclusions

No economy logic

No NPC memory

No governments

No situations

No UI beyond text/log output

Benchmark to Advance

A complete run can execute 100+ turns without crashing

Logs clearly show:

player location

time progression

state changes

Kill Criteria

If state becomes inconsistent or opaque ? redesign before proceeding

Phase 1 — Economy Core

Target: 0.2.x

Objective

Introduce a living economy that reacts to scarcity and player action.

Required Systems

Goods catalog

Supply and demand model

Price calculation

Resource profiles per planet/system

Player trading loop (buy/sell/transport)

Explicit Exclusions

No NPC traders yet

No governments or legality

No dynamic situations

Benchmark to Advance

Player actions visibly alter prices

Scarcity propagates to nearby systems

Economic changes are explainable post-hoc

Kill Criteria

Prices fluctuate without identifiable cause

Economy collapses or trivializes profit

Phase 2 — Government & Legality

Target: 0.3.x

Objective

Make place matter through law and policy.

Required Systems

Government archetypes

Legality matrix (goods + actions)

Enforcement outcomes

Reputation effects tied to legality

Explicit Exclusions

No NPC memory yet

No situations like war/plague

Benchmark to Advance

Same action yields different outcomes on different planets

Law enforcement consequences are predictable but not always avoidable

Kill Criteria

Governments feel cosmetic

Legality has no meaningful impact on play

Phase 3 — NPC Persistence

Target: 0.4.x

Objective

Populate the sector with people who remember.

Required Systems

NPC generation

Roles/professions

Persistent identity

Memory flags

Relationship states (friend/neutral/enemy)

NPC movement and basic activity

Explicit Exclusions

No storyline system yet

No situation-driven role spawning

Benchmark to Advance

NPCs react differently based on past player behavior

NPC death/removal has downstream effects

Kill Criteria

NPCs feel interchangeable

Memory does not meaningfully affect outcomes

Phase 4 — Situations & Propagation

Target: 0.5.x

Objective

Make the sector self-destabilizing.

Required Systems

Situation types (war, plague, unrest, etc.)

Situation triggers

Time-based resolution

Propagation logic

Economic + NPC effects

Explicit Exclusions

No unique items yet

No narrative framing beyond state changes

Benchmark to Advance

Situations emerge without player input

Ignoring a situation produces consequences

Player intervention can alter, but not fully control, outcomes

Kill Criteria

Situations stall permanently

Cascades become chaotic and unreadable

Phase 5 — Emergent Narrative

Target: 0.6.x

Objective

Allow stories to coalesce naturally.

Required Systems

Story triggers (NPCs, locations, items, situations)

Long-arc state tracking

Optional player engagement

Resolution without player involvement

Explicit Exclusions

No authored campaigns

No branching dialogue trees

Benchmark to Advance

Distinct “stories” can be described after a run

Player absence is as meaningful as presence

Kill Criteria

Stories feel scripted

Player feels railroaded

Phase 6 — Stabilization & Balance

Target: 0.7.x ? 0.9.x

Objective

Turn a complex simulation into a playable system.

Focus Areas

Balance tuning

Failure-state fairness

Information surfacing

Performance

Save compatibility

Benchmark for 1.0 Consideration

Multiple viable playstyles

No dominant strategy

Bugs are reproducible via version number

Design intent matches actual behavior

Version Discipline (Enforced)

Every phase transition increments MINOR

Every simulation behavior change increments SIM

No phase skipping

No backfilling features from later phases

Authority & Change Control

This plan may only be modified here

Codex implements only what is approved

Any deviation requires explicit PM sign-off