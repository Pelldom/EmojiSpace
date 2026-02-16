# SANITY AUDIT PHASE 4

Repository: EmojiSpace
Audit mode: Read-only structural sanity audit
Primary authorities: `design/` and `data/`

----------------------------------------------------------------
1. PHASE ALIGNMENT REVIEW
----------------------------------------------------------------

- Current version is aligned on paper:
  - `VERSION` = `0.8.0`
  - status line = `Phase 4.11 NPC Ship Generation and Salvage Complete`
  - this matches `design/production_plan.md` Phase 4.11 target.

- Implemented outside assigned phase:
  - No clear hard implementation of Phase 5 narrative systems was found.
  - Contract metadata mismatch exists: `design/npc_ship_generation_and_salvage_contract.md` labels itself `Phase: 5.0` while `production_plan.md` places this work in Phase 4.11. This is a governance mismatch, not runtime behavior.

- Partially implemented relative to contract scope:
  - Interaction layer is partially contract-compliant and still stub-oriented (`combat_stub`, `law_stub`, `pursuit_stub`) while also containing direct mutating shipdock/refuel operations.
  - Travel-to-encounter-to-interaction runtime path is not integrated in the main gameplay loop.
  - Reaction and pursuit behavior diverges from their contract output/input model (band model and outcome vocabulary mismatch).
  - NPC generation and salvage are deterministic but do not satisfy full contract logging requirements.

- Phase leakage:
  - Responsibility leakage is more severe than feature leakage: multiple systems perform adjacent logic (especially enforcement/combat/interaction), blurring locked boundaries.

----------------------------------------------------------------
2. RESPONSIBILITY BOUNDARY AUDIT
----------------------------------------------------------------

Boundary violations found:

| File | Function | Description of boundary breach | Severity |
|---|---|---|---|
| `src/interaction_layer.py` | `execute_buy_hull`, `execute_sell_hull`, `execute_buy_module`, `execute_sell_module`, `execute_repair_ship`, `execute_refuel` | Interaction layer contract says dispatch-only, no state mutation; this module directly mutates fleet/player/ship state and computes prices/costs. | High |
| `src/interaction_layer.py` | `_compute_hull_integrity_max` | Duplicates combat hull-max rules instead of consuming a single combat/assembler authority. | High |
| `src/turn_loop.py` | `_inspect_trade`, `_inspect_transport`, `_border_checkpoint`, `_customs_checkpoint` | Turn loop orchestrates two enforcement paths (`GovernmentLawEngine` and `law_enforcement`) with overlapping consequence logic, causing split authority for law outcomes. | High |
| `src/mission_manager.py` | `_apply_rewards` | Mission contract states missions track state only and do not grant rewards directly; manager mutates player fields as reward engine. | High |
| `src/combat_resolver.py` | `_compute_hull_max_from_ship_state` | Combat 4.6 intent was assembler-backed authority; hull max is recomputed with duplicate tables and tag rules in combat layer. | Medium |
| `src/combat_resolver.py` | `resolve_combat` destruction branch | Salvage is generated for both destroyed player and enemy ships; Phase 4.11 contract scopes salvage trigger to destroyed NPC ships. | High |
| `src/reaction_engine.py` | `get_npc_outcome` | Returns outcomes (`ignore`, `hail`, `warn`, `pursue`) outside locked reaction outcome enum; overlaps interaction responsibility for flow semantics. | Medium |
| `src/pursuit_resolver.py` | `resolve_pursuit` | Pursuit contract expects band-based comparison with TR as a declared factor; implementation uses speed/pilot booleans and ignores TR input path. | Medium |
| `src/market_pricing.py` | `_interpret_tags` | Pricing computes its own tag risk output (even if not consumed) while contract requires pricing to react to government-provided legality/risk without redefining them. | Low |

Requested boundary checks:

- Economy does not define legality/risk: mostly compliant.
- Government defines legality/risk but not price: mostly compliant in output, but internal unused price-bias path exists.
- Pricing reacts to legality/risk but does not redefine: partially compliant; low-severity drift via internal risk interpretation.
- Enforcement consumes risk tiers but does not alter pricing: compliant.
- Ship schema contains no legality/pricing logic: compliant.
- NPC generation does not duplicate ship stat logic: partial; uses assembler but also pulls hull max from combat helper path.
- Combat consumes assembler outputs as authority: partial; effective bands do, hull max does not.

----------------------------------------------------------------
3. DETERMINISM AUDIT
----------------------------------------------------------------

System-by-system:

- Market creation (`src/market_creation.py`, `src/world_generator.py`)
  - Seed usage: deterministic `random.Random` seeded from world/system/destination.
  - RNG isolation: acceptable (separate seeded contexts).
  - Hidden randomness: none obvious.
  - Non-logged mutation: possible when logger is absent; deterministic but less reconstructible.
  - Flag: No deterministic violation found.

- Pricing (`src/market_pricing.py`)
  - Seed usage: substitute discount seeded by `world_seed + system_id + sku`.
  - RNG isolation: yes (per-call local RNG).
  - Hidden randomness: none.
  - Non-logged mutation: none (pure calculation + optional log).
  - Flag: Deterministic.

- Government tag interpretation (`src/government_law_engine.py`)
  - Seed usage: deterministic roll via stable hash over known inputs.
  - RNG isolation: per-check local RNG.
  - Hidden randomness: none.
  - Non-logged mutation: no direct mutation in evaluator.
  - Flag: Deterministic; contract-shape mismatch exists elsewhere.

- Enforcement outcomes (`src/law_enforcement.py`, plus `src/government_law_engine.py`)
  - Seed usage: deterministic stream tokens include world/system/turn/checkpoint/action.
  - RNG isolation: yes.
  - Hidden randomness: none.
  - Non-logged mutation: enforcement mutates `PlayerState`; logs exist but two enforcement implementations split the audit trail.
  - Flag: Deterministic but architecturally split authority.

- NPC generation (`src/npc_ship_generator.py`)
  - Seed usage: explicit isolated streams match contract names.
  - RNG isolation: strong.
  - Hidden randomness: none.
  - Non-logged mutation: no required generation logs emitted.
  - Flag: Deterministic behavior, logging compliance gap.

- Ship assembly (`src/ship_assembler.py`)
  - Seed usage: none (pure deterministic transform).
  - RNG isolation: n/a.
  - Hidden randomness: none.
  - Non-logged mutation: none.
  - Flag: Deterministic.

- Combat resolution (`src/combat_resolver.py`)
  - Seed usage: dedicated `CombatRng(world_seed|combat_id_salt)`.
  - RNG isolation: isolated per combat.
  - Hidden randomness: none.
  - Non-logged mutation: round logs include rng events and state changes.
  - Flag: Deterministic core loop; contract drift on salvage trigger and duplicated hull-max authority.

- Salvage generation (`src/salvage_resolver.py`)
  - Seed usage: explicit isolated streams (`npc_salvage_count/select/mutation`).
  - RNG isolation: strong.
  - Hidden randomness: none.
  - Non-logged mutation: contract-required salvage weighting/mutation logs are absent.
  - Flag: Deterministic behavior, logging compliance gap.

- Shipdock inventory (`src/shipdock_inventory.py`)
  - Seed usage: separate deterministic streams for modules/hulls.
  - RNG isolation: yes.
  - Hidden randomness: none.
  - Non-logged mutation: no generation log record.
  - Flag: Deterministic behavior, explainability gap.

Nondeterministic behavior found:
- No direct nondeterministic runtime paths were identified in audited core systems.
- Main risk is reproducibility/explainability degradation from missing required logs, not random nondeterminism.

----------------------------------------------------------------
4. CONTRACT COVERAGE MATRIX
----------------------------------------------------------------

Locked/authoritative contracts reviewed:

| Contract | Implemented | Tested | Missing | Notes |
|---|---|---|---|---|
| `design/production_plan.md` | Partial | Partial | Runtime phase gates | Version aligns at 0.8.0; implementation boundaries still leak. |
| `design/PROJECT_INSTRUCTIONS.md` | Partial | No | Boundary enforcement checks | Multiple cross-system responsibility drifts. |
| `design/market_pricing_contract.md` | Yes | Partial | Strict consumed-risk boundary assertions | Core order exists; government_bias hardcoded 0. |
| `design/government_tag_interpretation.md` | Yes | Partial | Explicit consumed-tag regression suite | Risk/legality path present and deterministic. |
| `design/law_enforcement_contract.md` | Partial | Yes | Single authoritative enforcement path | Two enforcement implementations create divergence risk. |
| `design/entity_contract.md` | Yes | Partial | Strong runtime role/tag constraints | Core entity shapes exist. |
| `design/time_engine_contract.md` | Mostly | Yes | Encounter-after-travel integration | Tick order and caps implemented. |
| `design/ship_system_contract.md` | Partial | Partial | Remove duplicate combat-side hull math | Core combat exists; authority duplication remains. |
| `design/ship_system_appendix_scaling.md` | Partial | Partial | Single source for hull max and modifiers | Assembler matches most numeric rules. |
| `design/ship_and_module_schema_contract.md` | Mostly | Yes | Full prohibited-field enforcement breadth | Loader validations are strong; some caps differ by interpretation. |
| `design/combat_and_ship_tag_contract.md` | Mostly | Partial | Outcome + slot/secondary edge assertions | Tag namespaces and RPS mostly implemented. |
| `design/combat_resolution_contract.md` | Partial | Yes | Restrict salvage trigger to NPC destruction | Deterministic loop and logs exist. |
| `design/shipdock_inventory_contract.md` | Yes | Yes | Deterministic generation logs | Selection and bans implemented. |
| `design/npc_ship_generation_and_salvage_contract.md` | Mostly | Yes | Contract-required logging; NPC-only salvage trigger | Streams and weighted behavior implemented. |
| `design/encounter_types_schema_contract.md` | Yes | Partial | Broader schema validation tests | Required fields validated in loader. |
| `design/encounter_generator_contract.md` | Mostly | Partial | Full travel-context integration tests | Authority scaling by enforcement_strength implemented. |
| `design/interaction_layer_contract.md` | Partial | Partial | Strict dispatcher-only compliance | Module currently mutates state and computes costs. |
| `design/reaction_evaluation_contract.md` | Partial | Partial | Output enum alignment | Implemented outcomes exceed contract enum. |
| `design/pursuit_resolver_contract.md` | Partial | Partial | TR-band factor + canonical inputs | Deterministic resolver exists but model mismatch. |
| `design/reward_profiles_schema_contract.md` | Mostly | Partial | Tests for all prohibited fields and scaling clauses | Materializer and schema loader exist; broad validation tests missing. |
| `design/end_goals.md` | Mostly | Partial | Integrated gameplay path coverage | End-game evaluator present and tested. |

Data authority coverage (`data/*.json`):
- Data files are actively consumed; validation tests cover hull/module strongly.
- Missing broad contract-level validation tests for `encounter_types.json`, `reward_profiles.json`, and cross-file consistency (encounter -> reward_profile linkage).

----------------------------------------------------------------
5. PLAYER-FACING CLI TESTING REVIEW
----------------------------------------------------------------

Current CLI state:

- Generate world: Yes (`src/main.py`, `src/cli_test.py`).
- Travel: Not in player-facing interactive loop.
- Encounter ships: No integrated player entry point.
- Engage combat: Only standalone sim harness (`src/cli_combat_sim.py`), not world loop.
- Trade: Engine path exists (`TurnLoop.execute_buy/sell`) but not exposed as full player CLI flow.
- Trigger enforcement: Mostly test/demo path (`ENFORCEMENT_DEMO`), not normal player loop.
- Use shipdock: No integrated player CLI entry point.
- Buy/sell ships/modules: Helper functions exist only.
- Refuel: Helper exists only.
- Salvage experience: Through combat resolver path, not exposed in playable loop.

Quality of current CLI:

- Logs readable: technical, mostly developer-facing.
- Outcomes explainable: moderate where logs exist; weak where logs are absent (shipdock, npc/salvage generation).
- State transitions visible: partial, fragmented across demos/tests.
- Error states handled: mostly via return dicts/exceptions, but not unified for player UX.

Missing CLI hooks:
- No unified interactive action loop that routes travel -> encounter -> interaction -> combat -> rewards -> persistence.
- No CLI path for shipdock/refuel operations despite backend helpers.
- No first-class command surface for salvage inspection/collection.

Unreachable systems / test-only:
- Encounter/interaction/reaction/pursuit stack is mostly validated via integration tests, not player loop.
- Shipdock inventory + shipdock actions are unit-test reachable, not gameplay reachable.

----------------------------------------------------------------
6. STRUCTURAL RISK AREAS
----------------------------------------------------------------

Top 5 architectural risks:

1) Dual enforcement implementations (`government_law_engine` and `law_enforcement`) with overlapping authority.
2) Interaction layer over-coupling: dispatch + mutating economic/ship operations in one module.
3) Combat authority split: assembler-backed effective bands but duplicated hull-max and salvage trigger logic.
4) Runtime orchestration gap: no single authoritative simulation loop wiring all phase-complete systems.
5) Destination-vs-system market authority shim still present, creating future integration ambiguity.

Additional risk signals:
- Duplicate logic across modules (hull integrity formulas, enforcement decision paths).
- Deep cross-boundary call stacks in `TurnLoop` (economy + law + pricing + cargo mutation).
- Hard-coded assumptions and constants spread across modules instead of centralized contract adapters.

----------------------------------------------------------------
7. WHAT IS MISSING
----------------------------------------------------------------

Structural glue still missing before UI:

- Unified game loop controller that owns deterministic step order for travel, encounter dispatch, enforcement, combat, reward, and persistence writes.
- Central state snapshot serializer for complete reproducible run state (player, world, ships, encounters, markets, legal state).
- Event log abstraction with subsystem-level structured events (not only ad hoc string logs).
- Player state summary/read model for CLI/UI consumption (credits, location, fuel, legal risk, active ship, mission status).
- Encounter presentation adapter that normalizes interaction/reaction/pursuit/combat payloads into one surface.
- Market/shipdock view adapters exposing actionable and validated command surfaces.
- Combat presentation adapter that transforms round logs into stable player-facing summaries.

----------------------------------------------------------------
8. WHAT IS NEXT (Simulation Layer Only)
----------------------------------------------------------------

Recommended next milestone (simulation-only, phase-aligned):

- Milestone: complete a single authoritative runtime orchestration pass for existing Phase 4.11 systems (no new mechanics).

Why:
- Most core systems exist but are not coherently connected in one deterministic player flow.
- Current coverage is module-level strong and integration-level weak for actual play progression.

Dependencies:
- Resolve enforcement authority split (choose one enforcement path).
- Enforce interaction-layer dispatch-only boundary; move mutating actions into dedicated resolvers/services.
- Align reaction/pursuit/interaction enums and payload contracts.
- Add missing deterministic logs for npc generation, salvage, shipdock generation.

Risk:
- Medium-high due to cross-module touchpoints and existing duplication.

Estimated complexity:
- Medium-high (integration-heavy, logic-light).

----------------------------------------------------------------
9. UI DEVELOPMENT STAGING PLAN
----------------------------------------------------------------

Stage 1: CLI stabilization layer
- Required backend refactors: unify enforcement path; extract shipdock/refuel resolvers out of interaction dispatcher; remove duplicated hull-max logic from non-authoritative modules.
- Adapter layers needed: command router + state read model + encounter/result formatter.
- Logging changes required: structured event schema per subsystem with deterministic seed/stream metadata.
- State exposure requirements: normalized snapshot endpoint/object for current world/player/ship/encounter state.

Stage 2: Text UI (structured terminal)
- Required backend refactors: strict typed action/result contracts for all player actions.
- Adapter layers needed: presentation DTO adapters for market, shipdock, combat, enforcement, and mission surfaces.
- Logging changes required: human-readable plus machine-readable dual logs.
- State exposure requirements: stable query interfaces for current options and resulting deltas.

Stage 3: Web UI wrapper
- Required backend refactors: isolate simulation tick API from CLI command parser.
- Adapter layers needed: API boundary adapter (request -> simulation action -> deterministic response envelope).
- Logging changes required: correlation ids per action/turn and replay bundle generation.
- State exposure requirements: incremental state diffs and full snapshot retrieval.

Stage 4: Player dashboard
- Required backend refactors: none major if previous stages are done.
- Adapter layers needed: aggregated player telemetry adapter (economy/legal/combat/mission summaries).
- Logging changes required: summarized event streams derived from structured logs.
- State exposure requirements: compact denormalized dashboard model with explicit provenance fields.

----------------------------------------------------------------
10. OVERALL STRUCTURAL GRADE
----------------------------------------------------------------

- Overall architecture rating: C
- Determinism rating: B-
- Separation-of-concerns rating: D+
- Production readiness rating: D

Blunt assessment:
The repository contains substantial deterministic simulation work, but architecture is not structurally clean enough for dependable expansion. Responsibility boundaries are repeatedly crossed (especially interaction, enforcement, and mission reward handling), authoritative paths are duplicated, and core phase-complete systems are still not integrated into one playable runtime loop. Without consolidation of authority and orchestration, UI integration will expose inconsistencies rather than simulation depth.

