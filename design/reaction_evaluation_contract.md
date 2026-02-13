# EmojiSpace - Reaction Evaluation Contract

Status: Locked
Phase: 4c - Reaction Evaluation
Target Version: 0.5.x
Location: /design/reaction_evaluation_contract.md

----------------------------------------------------------------

## 1. Purpose

Reaction Evaluation determines how an NPC responds to a player-initiated
interaction attempt that requires a decision.

It is used for:

- Player intimidation attempts (hail.intimidate)
- Player bribe attempts in hostile posture
- Player surrender attempts in hostile posture
- Future negotiation cases (if explicitly added)

Reaction Evaluation returns a deterministic NPC intent outcome.
The Interaction Layer retains control flow authority and dispatches
to the appropriate resolver.

Reaction Evaluation does NOT resolve combat, law, or reward outcomes.

----------------------------------------------------------------

## 2. Scope and Authority

This contract governs:

- Deterministic evaluation of NPC compliance or refusal
- Input variables allowed for reaction weighting
- The NPC intent outcome enum
- Logging required for reconstructibility

This contract does NOT govern:

- Combat resolution
- Bribe deduction (handled by Interaction Layer before evaluation)
- Reward application
- Law enforcement logic
- Market pricing
- Mission acceptance logic
- Prose generation
- Creation or mutation of world state

----------------------------------------------------------------

## 3. Core Principles (Non-Negotiable)

1. Reaction outcomes must be deterministic
2. Reaction logic must use only banded or categorical inputs
3. Reaction logic must not mutate world state
4. Reaction logic must be fully log-reconstructible
5. Reaction logic must not introduce new actions
6. Reaction logic must not use SLM for decision making
7. NPC refusal does NOT automatically end an encounter

----------------------------------------------------------------

## 4. Inputs (Authoritative)

### 4.1 Encounter Context

- encounter_id
- posture (neutral, authority, hostile)
- subtype_id
- threat_rating_tr (if present)
- flags (list)
- system_government_id
- active_system_situations (ids)

### 4.2 Player Action Context

- action_type (intimidate, bribe, surrender)
- action_payload (structured)

For intimidate:
- intimidate_intent (demand_surrender, demand_credits, demand_cargo)
- demand_credits_amount (optional)
- demand_cargo_constraints (optional)

For bribe:
- bribe_kind (credits, goods)
- bribe_value_band (low, medium, high)

For surrender:
- surrender_kind (unconditional)

### 4.3 Player State (Banded)

- player_TR_band (1..5)
- player_reputation_band
- player_notoriety_band
- player_criminal_track_band
- player_law_track_band

### 4.4 NPC State (Banded)

- npc_TR_band (1..5)
- npc_faction_type
- npc_tech_tier_band (optional; 1..5)
- npc_government_alignment (if authority)

### 4.5 Determinism

- world_seed
- stable_salt = encounter_id + action_type

----------------------------------------------------------------

## 5. Output (Authoritative Enum)

Reaction Evaluation MUST return exactly one of:

- accept
- accept_and_attack
- refuse_stand
- refuse_flee
- refuse_attack

Meaning:

accept:
- NPC complies with player demand or accepts surrender/bribe.
- Interaction Layer determines appropriate end state.

accept_and_attack:
- NPC appears to accept (eg takes bribe) but initiates combat.

refuse_stand:
- NPC refuses demand but does not escalate.
- Control returns to player.

refuse_flee:
- NPC refuses and attempts escape (dispatch to pursuit).

refuse_attack:
- NPC refuses and initiates combat.

Important:
NPC refusal does NOT automatically terminate the encounter.

----------------------------------------------------------------

## 6. Control Flow Authority (Interaction Layer Integration)

The Interaction Layer MUST map outcomes as follows:

accept:
- For intimidation/bribe: end encounter (unless subtype rules override)
- For surrender: dispatch to law_enforcement or appropriate handler

accept_and_attack:
- dispatch to combat

refuse_stand:
- return control to player
- allowed actions reduced to:
  - ignore
  - attack

refuse_flee:
- dispatch to pursuit

refuse_attack:
- dispatch to combat

----------------------------------------------------------------

## 7. Reaction Evaluation Logic Model

Reaction Evaluation computes a Compliance Score using:

- Relative TR difference (player_TR_band - npc_TR_band)
- Tech tier delta
- Player reputation band
- Player notoriety band
- Player criminal/law track bands
- Government ideology (if authority)
- Situation modifiers
- Bribe value band (if applicable)

Philosophical Rules:

- High notoriety increases intimidation compliance likelihood
- High reputation decreases intimidation compliance likelihood
- High reputation increases authority compliance likelihood
- Large positive TR delta strongly increases compliance
- Large negative TR delta strongly decreases compliance
- Strict governments reduce bribe compliance likelihood

The Compliance Score is mapped to an outcome distribution.

----------------------------------------------------------------

## 8. Deterministic Outcome Selection

Procedure:

1. Compute compliance_score (numeric or banded)
2. Map compliance_score to probability distribution
3. Use deterministic RNG:
   seed = world_seed + stable_salt
4. Select outcome
5. Log all intermediate values

Outcome distribution must allow:
- accept_and_attack only for subtypes permitting betrayal
- refuse_stand only where logical (neutral posture primarily)

----------------------------------------------------------------

## 9. Logging Requirements (Mandatory)

Reaction Evaluation must log:

- encounter_id
- action_type
- all input bands
- compliance_score breakdown by factor
- compliance_score total
- probability distribution
- deterministic roll value
- final outcome enum

Failure to reconstruct outcome from logs is a contract violation.

----------------------------------------------------------------

## 10. Explicit Non-Responsibilities

Reaction Evaluation MUST NOT:

- Deduct bribe credits
- Apply stolen tags
- Apply warrants
- Trigger combat directly
- Modify player reputation
- Modify NPC state
- Generate prose

----------------------------------------------------------------

## 11. Contract Authority

This document becomes authoritative once locked.

All NPC reaction decisions must conform to this contract.
Changes require explicit revision and version update.

----------------------------------------------------------------
