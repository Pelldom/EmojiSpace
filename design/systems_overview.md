EmojiSpace - Systems Overview
Purpose of this document

This document enumerates all core systems in EmojiSpace and defines their responsibilities, inputs, outputs, and dependencies. Its purpose is to prevent circular dependencies, clarify build order, and establish firm system boundaries before implementation begins.

This document intentionally avoids implementation details.

System dependency order (high level)

Time Engine
World Generator
Economy Engine
Government and Law Engine
NPC Engine
Situation Engine
Narrative Trigger Engine

All systems depend directly or indirectly on Time and World State.

1. Time Engine
Responsibility

Advance game time in discrete turns and act as the global simulation clock.

Inputs

Player action
Simulation step request

Outputs

Current turn number
Time advancement signal

Dependencies

None

Notes

All systems must be deterministic with respect to time steps. No system may advance time independently.

2. World Generator
Responsibility

Generate a sector-scale map including systems and planets, and assign all static attributes.

Inputs

Random seed
Generation constraints

Outputs

Systems
Planets
Spatial relationships
Initial world state

Dependencies

Time Engine (initialization only)

Notes

World generation occurs once per run and does not regenerate during play.

3. Economy Engine
Responsibility

Model production, consumption, scarcity, and price calculation.

Inputs

Resource profiles
Trade actions
Situation modifiers
NPC economic activity (future phases)

Outputs

Prices
Availability
Economic pressure signals

Dependencies

World Generator
Time Engine

Notes

Economic changes must be explainable. Randomness must be traceable and logged.

4. Government and Law Engine
Responsibility

Determine legality of goods and actions, enforce laws, and apply consequences.

Inputs

Government type
Player actions
NPC actions
Active situations

Outputs

Legal status
Enforcement events
Reputation changes

Dependencies

World Generator
Economy Engine
Time Engine

Notes

Governments modify outcomes but do not override core simulation rules.
Government outputs a policy result that includes legality_state, risk_tier, and consumed_tags.
Pricing consumes these outputs and skips interpretation of consumed tags.

5. NPC Engine
Responsibility

Create and manage persistent NPCs including identity, role, memory, and relationships.

Inputs

World state
Economy signals
Government rules
Player actions
Active situations

Outputs

NPC actions
Relationship state changes
World interaction events

Dependencies

World Generator
Economy Engine
Government and Law Engine
Time Engine

Notes

NPCs persist for the duration of a run. Memory must meaningfully affect future behavior.

6. Phase 3.2 - Prose and World Texture Layer
Responsibility

Provide read-only, non-authoritative presentation of the world through names,
descriptions, dialogue, and reflective flavor text.

Inputs

World state
Entity state
Player history (read-only)

Outputs

Names and descriptions
Dialogue and non-binding text
World reflection

Dependencies

All systems (read-only)
Time Engine

Notes

This layer is non-mutating and does not affect mechanics, outcomes, legality, risk, economy, or time.
Removing it does not change gameplay results.

7. Situation Engine
Responsibility

Create, advance, propagate, and resolve dynamic situations such as war, plague, or unrest.

Inputs

World conditions
Economic thresholds
Government instability
NPC actions
Time progression

Outputs

Active situations
Modifiers to economy, NPCs, and law
Situation propagation events

Dependencies

Economy Engine
Government and Law Engine
NPC Engine
Time Engine

Notes

Situations must resolve over time even without player involvement.

8. Narrative Trigger Engine
Responsibility

Detect meaningful state patterns and surface optional story hooks and long-term arcs.

Inputs

NPC state
Situation state
Player history
Unique items or locations

Outputs

Story hooks
Narrative state flags
Long-term outcomes

Dependencies

NPC Engine
Situation Engine
Economy Engine
Time Engine

Notes

Narrative systems observe and react. They never directly alter simulation state.

9. Player State System
Responsibility

Track player location, assets, reputation, and history, and translate player intent into simulation actions.

Inputs

Player decisions
World feedback

Outputs

Player actions
Reputation changes
Economic transactions

Dependencies

All systems (read-only)
Time Engine

Notes

The player is a participant, not a controller. Player state must be serializable.

10. Logging and Diagnostics System
Responsibility

Record simulation state changes for debugging, replay, and analysis.

Inputs

Events from all systems

Outputs

Structured logs
Debug traces
Version tagging

Dependencies

VERSION file
All systems (observer-only)

Notes

Logging is mandatory. All major state changes must be explainable after the fact.

11. Combat Resolver (Phase 4.x)
Responsibility

Resolve deterministic, simultaneous round-based combat using contract-locked bands, damage, degradation, repair, surrender, and escape.

Inputs

Ship loadouts (player and NPC parity)
Combat actions selected per round
World seed and combat id salt

Outputs

Combat outcome (destroyed, escape, surrender, max_rounds)
Round logs including RNG-derived values
Final combat states for both ships

Dependencies

Ship module and crew tags
Pursuit Resolver (escape attempt integration)
Logging and diagnostics

Notes

Combat scan success currently uses a deterministic placeholder in the resolver and is intended to be replaced by interaction-layer scan resolution.

## Fuel System Invariants

- Fuel is a travel gating resource.
- Fuel does not affect combat resolution.
- Fuel does not affect time cost.
- Fuel does not interact with government legality.
- Fuel availability for refueling depends on DataNet presence.
- Fuel price is fixed at 5 credits per unit.

Forbidden dependency rules (hard constraints)

Narrative systems may not directly modify simulation state.
Situations may not bypass government or economy rules.
NPCs may not advance time.
User interface code may not contain simulation logic.
No system may mutate another system's internal state directly.

All interaction occurs through declared inputs and outputs only.