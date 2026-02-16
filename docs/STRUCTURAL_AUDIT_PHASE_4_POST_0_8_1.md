# STRUCTURAL AUDIT - PHASE 4 POST 0.8.1

Scope: Read-only structural audit against `design/production_plan.md`, `design/PROJECT_INSTRUCTIONS.md`, and locked contracts under `design/`.

Rules applied: no code changes, no version changes, no contract rewrites.

---

## 1. PHASE ALIGNMENT CHECK

### Phase mapping for implemented systems in `src/`

- Phase 0 foundations:
  - `logger.py`, `world_generator.py`, `turn_loop.py`, `player_state.py`, `main.py`
- Phase 1 and 1.5 economy core and variety:
  - `economy_data.py`, `data_catalog.py`, `market.py`, `market_creation.py`, `economy_engine.py`
- Phase 2 government and legality:
  - `government_type.py`, `government_registry.py`, `government_law_engine.py`
- Phase 2.6 pricing and tag interpretation:
  - `market_pricing.py`
- Phase 2.7 enforcement:
  - `law_enforcement.py`
- Phase 2.8 end goals foundation:
  - `end_game_evaluator.py`
- Phase 3 NPC persistence:
  - `npc_entity.py`, `npc_registry.py`, `npc_placement.py`
- Phase 3.1 time engine:
  - `time_engine.py`
- Phase 3.2 prose and texture:
  - `prose_generator.py`, `datanet_entry.py`, `datanet_feed.py`
- Phase 4 travel and encounters:
  - `travel_resolution.py`, `encounter_generator.py`, `interaction_layer.py`, `reaction_engine.py`, `pursuit_resolver.py`, `reward_materializer.py`
- Phase 4.2 ship and module data layer:
  - `data_loader.py`, `ship_entity.py`, `warehouse_entity.py`, `entities.py`
- Phase 4.4 data validation and integration:
  - validation logic in `data_loader.py`, harnesses in `integration_test.py`, `phase4_integration_test.py`
- Phase 4.5 deterministic ship assembler:
  - `ship_assembler.py`
- Phase 4.6 combat integration:
  - `combat_resolver.py`, `cli_combat_sim.py`
- Phase 4.7 shipdock inventory:
  - `shipdock_inventory.py`
- Phase 4.8 and 4.9 shipdock and refuel interactions:
  - mutation resolver path in `interaction_resolvers.py`, dispatch surface in `interaction_layer.py`
- Phase 4.9.1 secondary tag resale:
  - resale multiplier logic in `interaction_resolvers.py`
- Phase 4.11 NPC ship generation and salvage:
  - `npc_ship_generator.py`, `salvage_resolver.py`
- Phase 4.11.1 stabilization and orchestration patch:
  - `cli_playable.py`, `reward_applicator.py`, boundary cleanups across `turn_loop.py`, `interaction_layer.py`, `reaction_engine.py`
- Mission skeleton contract support:
  - `mission_entity.py`, `mission_factory.py`, `mission_manager.py`
- Test harness modules under `src/`:
  - `cli_test.py`, `integration_test.py`, `phase4_integration_test.py`

### Phase 5 and 6 leakage check

- No direct Phase 5 emergent narrative system engine found (no narrative trigger orchestration or long-arc runtime manager).
- No direct Phase 6 balancing framework or UI framework implementation found.
- Existing files that could be mistaken for leakage are still phase-aligned:
  - `prose_generator.py` (Phase 3.2 texture layer)
  - `end_game_evaluator.py` (Phase 2.8 end goals foundation)

### Phase 4.11.1 "no new mechanics" check

- Stabilization patch behavior is primarily boundary and orchestration:
  - `interaction_layer.py` dispatch-only forwarding
  - `reward_applicator.py` central reward mutation path
  - `reaction_engine.py` contract vocabulary fallback correction
  - `cli_playable.py` harness orchestration updates

### Out-of-scope or exceeded-phase indicators

- No hard evidence of Phase 5 or 6 mechanics implemented in runtime code.
- Residual structural risk: multiple harness entry points (`main.py`, `cli_playable.py`, `phase4_integration_test.py`) may evolve unevenly if not kept synchronized.

---

## 2. AUTHORITY BOUNDARY VERIFICATION

### Economy does not define legality

- Verified in `economy_engine.py` and `market_creation.py`: economy handles scarcity, categories, market composition.
- Legality and risk are evaluated in `government_law_engine.py` and consumed by callers.

### Government does not define pricing

- `government_law_engine.py` evaluates legality and risk; it does not calculate transaction prices.
- Pricing is calculated in `market_pricing.py`.

### Pricing reacts to legality and does not redefine legality

- `market_pricing.py` accepts `GovernmentPolicyResult` and uses `policy.legality_state` and `policy.risk_tier` in output.
- No legality-state mutation in pricing code path.

### Law enforcement resolves consequences only

- Consequence mutations are centralized in `law_enforcement.py` (`enforcement_checkpoint`, `_apply_outcome`, confiscation and detention handlers).
- `turn_loop.py` uses `enforcement_checkpoint` for border/customs flow.
- `government_law_engine.py` contains `resolve_enforcement`, but no runtime call site was found in `src/`.

### Ship assembler authority

- Effective combat bands and capacities are derived via `assemble_ship(...)` in `combat_resolver.py`.
- NPC generation uses assembler output in `npc_ship_generator.py`.
- Shipdock buy/sell/module changes use assembler in `interaction_resolvers.py`.

### Interaction layer dispatch-only

- `interaction_layer.py` forwards destination actions and does not directly mutate player/ship state.
- Mutations are in `interaction_resolvers.py`.

### Reward application centralized

- Materialized rewards mutate player through `reward_applicator.apply_materialized_reward(...)` from `cli_playable.py`.
- Mission rewards mutate through `reward_applicator.apply_mission_rewards(...)` from `mission_manager.py`.

### Combat resolver duplication check

- Combat uses assembler for bands and degradation capacities.
- Hull max remains computed by canonical helper in `combat_resolver.py` and reused by dependent modules.

### Duplicate authority findings

- No active split-authority enforcement path detected in runtime flow.
- No direct interaction-layer mutation authority detected.
- Medium structural watch item: tag interpretation logic exists in both `government_law_engine.py` and `market_pricing.py`; currently used for different outputs, but drift risk exists if contracts change.

---

## 3. CONTRACT COMPLIANCE CHECK

Contracts reviewed as requested:

### `ship_and_module_schema_contract.md`

- Compliance signals:
  - `data_loader.py` enforces required hull/module keys and types.
  - `ship_assembler.py` validates module instance structure and slot/tag consistency.
- Drift observed:
  - No major drift found in schema validation path.

### `ship_system_contract.md`

- Compliance signals:
  - `combat_resolver.py` implements round loop, action handling, degradation, repair, surrender, destruction outcomes.
  - RCP/TR mapping and hull band reporting present.
- Drift observed:
  - Insurance remains externalized (`requires_external_insurance_resolution`) rather than fully resolved in combat path.

### `ship_system_appendix_scaling.md`

- Compliance signals:
  - Deterministic slot/band math and secondary effects in `ship_assembler.py`.
  - Deterministic combat application in `combat_resolver.py`.
- Drift observed:
  - Hull max computation remains outside assembler in `combat_resolver.py`; still single path, but should remain contract-checked to prevent scale drift.

### `npc_ship_generation_and_salvage_contract.md`

- Compliance signals:
  - `npc_ship_generator.py` uses isolated RNG streams (`npc_hull_select`, `npc_loadout_fill`, `npc_module_select`, `npc_secondary_rolls`).
  - `salvage_resolver.py` uses isolated RNG streams for count/select/mutation.
  - `combat_resolver.py` triggers salvage only on enemy destroyed branch.
- Drift observed:
  - No direct drift detected in trigger scope or stream isolation.

### `law_enforcement_contract.md`

- Compliance signals:
  - Deterministic checkpoint RNG in `law_enforcement.py`.
  - Consequence application and logging included in enforcement event path.
  - `turn_loop.py` uses border and customs checkpoints through law enforcement module.
- Drift observed:
  - `government_law_engine.resolve_enforcement` remains defined but unused; potential confusion risk, not active behavior drift.

### `market_pricing_contract.md`

- Compliance signals:
  - Deterministic substitute discount (`random.Random(_stable_seed(...))`).
  - Uses category role, scarcity, tag bias, and logs pricing breakdown.
- Drift observed:
  - `government_bias` currently fixed at `0.0` with TODO note in `market_pricing.py`; if contract requires non-zero policy effect, this is an implementation shortcut.

### `entity_contract.md`

- Compliance signals:
  - Entity dataclasses exist for player, NPC, ship, mission, warehouse with serialization support.
  - Fields for identity/state/progression are represented.
- Drift observed:
  - No hard contract mismatch found in spot-check.

### `mission_skeleton_contract.md`

- Compliance signals:
  - `mission_entity.py` tracks identity, lifecycle, references, objectives, rewards data.
  - `mission_manager.py` now delegates reward mutation to `reward_applicator`.
- Drift observed:
  - No inline reward-economy logic remains in mission manager.

### `time_engine_contract.md`

- Compliance signals:
  - Sequential advancement in `time_engine.py`.
  - Hard-stop interruptibility (`player_death`, `tier2_detention`) present.
- Drift observed:
  - Logging in time engine uses direct `print` rather than shared logger abstraction; reconstructibility works but is less uniform than other systems.

---

## 4. DETERMINISM AUDIT

### Deterministic RNG stream validation

- Combat RNG:
  - `combat_resolver.py` uses seeded `CombatRng` with hash seed text.
- NPC generation:
  - `npc_ship_generator.py` stream-specific deterministic RNG.
- Salvage:
  - `salvage_resolver.py` stream-specific deterministic RNG.
- Shipdock inventory:
  - `shipdock_inventory.py` deterministic seed per stream.
- Pricing substitute discount:
  - `market_pricing.py` uses stable seeded RNG.
- Enforcement:
  - `law_enforcement.py` deterministic `_rng_for(...)`.
- World generation:
  - `world_generator.py` seeded RNG and seeded sub-generators.

### Time advancement determinism

- `time_engine.py` advances in strict order of daily tick functions and supports hard-stop interruption.

### Non-seeded randomness search

- No `random.random`, `random.choice`, `random.shuffle`, or `random.randint` global-module usage found in `src/`.
- Randomness appears to be routed through seeded `random.Random(...)` instances.

Conclusion: Determinism posture is strong, with no obvious non-seeded random source in runtime modules.

---

## 5. CLI STATUS

Assessment target: `src/cli_playable.py`

- Classified as a visibility/testing harness.
- Not a UI system.
- Not a complete production game loop controller.

Checks:

- No local legality computation in CLI.
- No local pricing computation in CLI.
- No local combat math in CLI (delegates to `combat_resolver`).
- No duplicate reward mutation logic in CLI (delegates to `reward_applicator`).
- Enforcement checkpoints are not bypassed for movement because travel/system movement uses `TurnLoop.execute_move(...)`.

Note: CLI still performs orchestration state updates (destination/location and applying returned refuel credit value). This is orchestration behavior, not new mechanics.

---

## 6. PLAYER-FACING TEST COVERAGE

Current test surface from `tests/`:

- Economic loop:
  - `test_cli_playable.py`, `test_fuel_system.py`, trade and pricing effects via turn flow and pricing tests.
- Enforcement:
  - `test_law_enforcement.py` has strong coverage including checkpoint behavior and deterministic outcomes.
- Combat:
  - `test_combat_resolver.py`, `test_combat_with_assembler.py`
- Salvage:
  - `test_npc_ship_generation_and_salvage.py`
- Shipdock buy/sell:
  - `test_shipdock_interaction_extensions.py`, `test_shipdock_inventory.py`
- Refuel:
  - `test_fuel_system.py`, shipdock interaction tests
- Mission progression:
  - `test_mission_manager_boundary.py` for manager and reward delegation

Missing or thin validation surfaces:

- End-to-end multi-turn scenario that combines travel, customs enforcement, encounter dispatch, combat/pursuit, rewards, and mission state in one deterministic integration assertion.
- Save/load round-trip determinism checks for the full orchestrated run.
- Long-run orchestration stress tests across multiple harnesses (`main.py` vs `cli_playable.py`) for behavior parity.

---

## 7. WHAT IS GOOD

- Single-authority consolidations are largely in place:
  - enforcement consequences in `law_enforcement.py`
  - interaction dispatch boundary in `interaction_layer.py`
  - reward application in `reward_applicator.py`
- Deterministic RNG usage is consistent and explicit across major systems.
- Combat and assembler integration is stable, with broad targeted tests.
- NPC generation and salvage determinism have dedicated regression coverage.
- Phase 4.11.1 patch goals are represented and mostly reflected in runtime boundaries.

---

## 8. WHAT IS RISKY

- Shared interpretation logic risk:
  - tag interpretation behavior appears in both `government_law_engine.py` and `market_pricing.py`; contract drift could desync these.
- Hull max authority location:
  - canonical hull max helper is in `combat_resolver.py`, not `ship_assembler.py`; this remains centralized but increases coupling to combat module.
- Time engine logging consistency:
  - `time_engine.py` uses direct print logging, not shared logger abstraction used elsewhere.
- Multiple orchestration entry points:
  - `main.py`, `cli_playable.py`, and integration harness modules can diverge over time.
- UI layering risk:
  - orchestration state stitching in CLI may be copied into presentation layers unless adapters are formalized.

Potential Phase 5 leakage risks:

- If prose/datanet or mission text routing grows without a dedicated phase controller, narrative behavior could leak before explicit Phase 5 implementation governance.

---

## 9. WHAT IS MISSING BEFORE PHASE 5

Structural gaps to close before moving phase:

- Unified orchestration contract for runtime controllers:
  - define one authoritative simulation controller path and align `main.py` and `cli_playable.py`.
- Consistent logging abstraction:
  - normalize time engine logging into shared structured logger pipeline.
- Cross-system deterministic integration tests:
  - add one authoritative end-to-end deterministic path test spanning economy, enforcement, encounter, combat/pursuit, reward, and mission state.
- Contract drift guardrails:
  - add targeted tests asserting parity where mirrored interpretation logic exists (government vs pricing).
- Persistence validation hooks:
  - verify save/load state snapshots preserve deterministic continuation across at least one orchestrated multi-turn scenario.

No new mechanics are required in this list.

---

## 10. UI DEVELOPMENT STAGING PLAN

### Stage 1: CLI hardening

- Keep deterministic orchestration in CLI harness only.
- Add structured event schema stability checks for emitted turn events.
- Preserve zero mechanics changes; only tighten adapter and validation behavior.

### Stage 2: Read-only status dashboard

- Build read-only adapters that consume existing state snapshots and logs.
- No command execution that mutates simulation.
- Keep all calculations in simulation modules; dashboard only displays outputs.

### Stage 3: Interaction router

- Introduce thin UI-to-dispatch adapters that forward user intent to `interaction_layer` and existing resolvers.
- Enforce no pricing, legality, combat, reward, or mission mechanics in router code.
- Preserve deterministic seed/thread inputs from orchestration layer.

### Stage 4: Full turn orchestration UI

- UI invokes one authoritative orchestration controller (not parallel bespoke loops).
- State mutation remains in existing simulation modules.
- UI remains presentation and command dispatch only; deterministic core unchanged.

---

Overall structural verdict: mostly clean Phase 4 simulation with strong determinism and improved boundaries, plus identifiable consolidation tasks that should be completed before any Phase 5 expansion.

