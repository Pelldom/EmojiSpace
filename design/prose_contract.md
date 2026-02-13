# EmojiSpace - Phase 3.2 Prose and World Texture Contract

Status: DRAFT (Proposed for Lock)
Phase: 3.2 - World Texture
Location: /design/prose_contract.md

This document defines the authoritative rules governing all prose,
naming, descriptive text, and narrative framing in EmojiSpace.

This phase introduces a prose-generation layer intended to enhance
clarity, immersion, and perceived world reactivity without altering
simulation logic, outcomes, or state.

This contract is binding once locked.

----------------------------------------------------------------

## 1. Purpose

Phase 3.2 exists to answer one question only:

"How is an already-determined world state presented to the player?"

This layer enhances:
- readability
- tone
- contextual framing
- narrative cohesion

It does NOT:
- create gameplay
- decide outcomes
- modify state
- introduce mechanics

If Phase 3.2 is removed, the game must remain mechanically identical.

----------------------------------------------------------------

## 2. Core Principle (Non-Negotiable)

Prose may describe outcomes.
Prose may not decide outcomes.

No text generated under this contract may:
- alter rules
- imply hidden mechanics
- invent consequences
- contradict system outputs

If removing prose changes gameplay results, this contract is violated.

----------------------------------------------------------------

## 3. Scope of Authority

Phase 3.2 is the sole authority for **prose-only outputs**.

It MAY generate:

- Entity display names
- Mission titles
- Mission descriptions
- NPC dialogue text
- NPC reaction framing
- Rumors and DataNet summaries
- Event and situation summaries (descriptive only)
- UI-facing explanatory text

It MAY NOT generate:

- Numeric values
- State changes
- Conditions
- Modifiers
- Triggers
- Decisions
- Instructions to systems

----------------------------------------------------------------

## 4. Naming Authority

Phase 3.2 is the only system allowed to generate names.

This includes:
- NPC display names
- Ship names
- Planet names
- System names
- Optional epithets or subtitles

Rules:
- Naming occurs once per entity
- Names are persisted
- Names are never regenerated
- Deterministic fallback naming must exist

No other system may invent or override names.

----------------------------------------------------------------

## 5. Mission Prose Rules

Phase 3.2 may generate mission-facing prose only after a mission
skeleton has been created.

Inputs are authoritative and include:
- objectives
- rewards
- distance tiers
- legality state
- risk tier
- allowed modifiers

Phase 3.2 may:
- title the mission
- describe objectives
- frame risks and rewards
- contextualize the mission giver

Phase 3.2 may NOT:
- modify objectives
- scale rewards
- add or remove modifiers
- invent hazards
- promise outcomes

All mechanics are decided before prose is applied.

----------------------------------------------------------------

## 6. NPC Dialogue and Reactions

Phase 3.2 may generate NPC dialogue and reaction text.

Inputs may include:
- NPC role tags
- affiliation
- persistence tier
- reputation bands
- known interaction outcomes

Rules:
- Dialogue must reflect provided facts only
- NPCs do not gain agency through prose
- Dialogue must not imply mechanical decisions

NPCs expose context, not outcomes.

----------------------------------------------------------------

## 7. World Reflection Outputs

Phase 3.2 may generate informational world reflection, including:

- rumors
- news blurbs
- DataNet chatter
- summaries of recent events

Rules:
- These outputs are descriptive only
- They do not change world state
- They may be ephemeral unless explicitly persisted

World reflection may summarize what happened,
never what will happen.

----------------------------------------------------------------

## 8. Truthfulness and Banding Constraints

All prose must be grounded in explicit inputs.

Phase 3.2 must not exaggerate beyond provided bands or tiers.

Example:
- Risk Tier: Medium
  Allowed: "tense", "heightened scrutiny"
  Forbidden: "extremely dangerous", "near certain death"

Adjective sets must be constrained to input bands.

----------------------------------------------------------------

## 9. Tone and Style Anchors

Prose generation must respect provided style anchors, including:

- government tone
- faction voice
- NPC role voice

Freeform personality invention is forbidden.

Style anchors exist to ensure consistency across time and scale.

----------------------------------------------------------------

## 10. Input and Output Constraints

### 10.1 Inputs (Read-Only)

Phase 3.2 may consume:
- entity identifiers
- tags
- numeric bands (risk, reputation, enforcement)
- mission skeletons
- world descriptors
- resolved system outputs

Inputs are authoritative and must not be reinterpreted.

### 10.2 Outputs (Constrained)

Outputs may include:
- strings
- tone labels
- selected option identifiers from provided lists

Outputs may NOT include:
- numeric values
- new identifiers
- instructions
- state mutation directives

----------------------------------------------------------------

## 11. Persistence Rules

Persisted prose:
- entity names
- mission titles
- mission descriptions
- first-contact NPC dialogue

Ephemeral prose:
- rumors
- chatter
- encounter flavor
- UI-only summaries

If prose is presented as authoritative, it must be persisted.

----------------------------------------------------------------

## 12. Determinism, Logging, and Fallback

Phase 3.2 must be:

- optional
- disableable
- replaceable with deterministic fallback text

Required logging:
- input snapshot reference
- output produced
- model or generator identifier
- fallback usage (if any)

Failure to reconstruct prose decisions from logs is a violation.

----------------------------------------------------------------

## 13. Relationship to Other Systems

Phase 3.2:
- occurs after entity and mission skeleton creation
- precedes Situations and Narrative Triggers
- observes all systems
- modifies none

Future systems may consume prose for presentation only.

----------------------------------------------------------------

## 14. Explicit Non-Responsibilities

Phase 3.2 does NOT:

- create missions
- advance time
- modify economy
- influence legality or enforcement
- escalate or resolve situations
- determine success or failure
- store long-term world state

Any such behavior is forbidden.

----------------------------------------------------------------

## 15. Contract Authority

This document is authoritative for Phase 3.2.

Any system generating prose, names, or narrative framing
MUST conform to this contract.

Changes require:
- explicit revision
- version update
- review prior to implementation

----------------------------------------------------------------

End of Phase 3.2 Prose and World Texture Contract
