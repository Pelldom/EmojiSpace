# STRUCTURAL VERIFICATION - PHASE 4.12

## SECTION 1 - CLI ORCHESTRATION AUTHORITY

### Inspection target
- `src/cli_playable.py`

### Findings
- `src/cli_playable.py` is **not pure orchestration**.
- It orchestrates existing systems (`WorldGenerator`, `TurnLoop`, `generate_encounter`, `dispatch_player_action`, `resolve_combat`, `resolve_pursuit`, `materialize_reward`), but also performs direct state mutation in local helper `_apply_reward`.
- It applies reward effects directly (`player.credits += ...`, cargo increments) instead of delegating to `reward_applicator`.

### Orchestration entry points found
- `src/cli_playable.py` -> `run_playable()` (closest to full playable flow: travel -> encounter -> interaction -> pursuit/combat -> reward -> persistence).
- `src/phase4_integration_test.py` -> `run_phase4_integration_test()` (integration harness; partial flow validation, not full gameplay controller).
- `src/main.py` -> `main()` (world + turn loop setup/logging; no full encounter/combat/reward loop).
- `src/cli_combat_sim.py` -> `run_simulation()` (combat-only harness).

### Full-flow controller count
- One practical full-flow controller exists: `src/cli_playable.py`.
- Additional harnesses are partial/scope-limited.

### CLI role classification
- **Secondary Authority / Duplicate Flow Risk**

---

## SECTION 2 - INTERACTION LAYER BOUNDARY

### Verification
- `src/interaction_layer.py` does not directly mutate `PlayerState` or ship persistent state.
- No direct credit/cargo mutation found in `interaction_layer`.
- No pricing math in `interaction_layer`.
- No hull max computation in `interaction_layer`.
- No combat band math in `interaction_layer`.
- `interaction_layer` dispatches to `src/interaction_resolvers.py` via wrapper functions and `dispatch_destination_action()`.

### Violations
- None found in `src/interaction_layer.py`.

---

## SECTION 3 - ENFORCEMENT SINGLE AUTHORITY

### Verification
- Consequence application path in runtime flow (`src/turn_loop.py`) routes through `law_enforcement.enforcement_checkpoint(...)`.
- `src/government_law_engine.py` still defines `resolve_enforcement(...)`, but repository scan shows no runtime call sites.
- `src/law_enforcement.py` performs consequence mutations (`_apply_outcome`, confiscation, detention tier handling, arrest/game-over state).

### Violations
- None found for active runtime authority split.

---

## SECTION 4 - COMBAT AUTHORITY

### Verification
- Canonical hull max computation function found in `src/combat_resolver.py`:
  - `_compute_hull_max_from_ship_state(...)`
- Other modules (`src/npc_ship_generator.py`, `src/interaction_resolvers.py`) call this helper, rather than duplicating hull max formulas.
- Combat uses assembler-derived values in multiple paths (`assemble_ship(...)` with pre/effective/red bands).
- No interaction-layer pricing path recomputes combat bands.

### Duplicate math implementations found
- No duplicate hull max function found outside `combat_resolver`.
- `ship_assembler` contains its own tier baseline logic for assembler stat bands (expected assembler authority scope), not a second hull max formula path.

---

## SECTION 5 - SALVAGE SCOPE

### Verification
- Salvage generation hook exists in `src/combat_resolver.py` via `resolve_salvage_modules(...)`.
- Repository scan shows no other salvage generation caller in `src/`.
- In combat destruction branch, salvage is only generated under `if enemy_destroyed:` path.
- No salvage logic found in `mission_manager` or `interaction_layer`.

### Additional salvage hooks
- `src/salvage_resolver.py` (resolver implementation only; not a trigger site).
- `src/encounter_generator.py` contains `salvage_possible` flag vocabulary only.

---

## SECTION 6 - REWARD MUTATION ENTRY POINT

### Verification
- `src/mission_manager.py` delegates mission rewards to `reward_applicator.apply_mission_rewards(...)`.
- `src/reward_applicator.py` exists as reward mutation component.
- `src/reward_materializer.py` remains materialization-only.

### Violations

1. **High**
   - **File:** `src/cli_playable.py`
   - **Function:** `_apply_reward`
   - **Line:** 77-89
   - **Description:** Direct reward mutation authority exists outside `reward_applicator` (`player.credits += ...` and cargo mutation). This duplicates reward-application authority.

2. **Medium**
   - **File:** `src/cli_playable.py`
   - **Function:** `run_playable`
   - **Line:** 268-270
   - **Description:** Reward path materializes reward and applies it through local `_apply_reward` instead of a shared authoritative reward applicator.

---

## SECTION 7 - REACTION AND PURSUIT CONTRACT SHAPE

### Reaction verification
- `reaction_engine` includes mapping of reaction-action outcomes into contract vocabulary for intimidate/bribe/surrender (`accept`, `accept_and_attack`, `refuse_stand`, `refuse_flee`, `refuse_attack`).
- **Mismatch found:** early-return paths still emit `"ignore"` before mapping is applied.

### Pursuit verification
- `pursuit_resolver` returns:
  - `outcome` in `{escape_success, escape_fail}`
  - compatibility `escaped` boolean
- TR and engine band factors are consumed (`tr_band`, `engine_band`, `tr_delta`, `engine_delta`) and logged.

### Violations

1. **Medium**
   - **File:** `src/reaction_engine.py`
   - **Function:** `get_npc_outcome`
   - **Line:** 103-104
   - **Description:** Returns `"ignore"` on zero-total-weight path, which is outside contract output enum for reaction evaluation actions.

2. **Medium**
   - **File:** `src/reaction_engine.py`
   - **Function:** `get_npc_outcome`
   - **Line:** 171-172
   - **Description:** Returns `"ignore"` on zero-after-modifiers path, also outside contract output enum for reaction evaluation actions.

---

## SECTION 8 - OVERALL BOUNDARY STATUS

1) **Boundary violations found:** 4

2) **Severity breakdown:**
- High: 1
- Medium: 3
- Low: 0

3) **Determinism risk summary:**
- Core deterministic plumbing remains intact (seeded encounter/combat/pursuit/salvage paths still centralized).
- Main risk is not RNG drift; it is **authority drift**: reward mutation is duplicated in CLI orchestration, and reaction contract vocabulary can leak non-contract value (`ignore`) through early returns.

4) **Simulation layer status:**
- **Mostly Clean (minor issues)**
- Reason: major split authorities (interaction/enforcement/combat hull max/salvage trigger) are largely consolidated, but two contract-boundary leaks remain and should be resolved to prevent authority regression.

