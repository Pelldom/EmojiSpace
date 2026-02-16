# STRUCTURAL VERIFICATION POST 4.11.2

Scope: read-only verification after hygiene cleanup.

Constraints applied: no code changes, no contract changes, no version changes.

---

## 1. ORCHESTRATION AUTHORITY CHECK

### A) Files coordinating two or more target systems in sequence

1) `src/simulation_controller.py`  
Function(s): `execute`, `_execute_travel_to_destination`, `_execute_location_action`, `_execute_encounter_action`, `_resolve_encounter`  
Coordinates: travel resolution, movement/enforcement/time via `TurnLoop`, encounter generation, reaction dispatch, pursuit/combat, reward materialization, reward application  
Classification: runtime orchestrator (legitimate)

2) `src/turn_loop.py`  
Function(s): `execute_move`, `execute_buy`, `execute_sell`, `_border_checkpoint`, `_customs_checkpoint`  
Coordinates: time advancement, economy ticks, enforcement checkpoints, legality/policy evaluation, pricing quotes  
Classification: runtime subsystem orchestrator (movement/economy/enforcement scope), not full encounter/combat/reward flow

3) `src/combat_resolver.py`  
Function(s): `resolve_combat`, `_escape_attempt`  
Coordinates: combat plus pursuit branch on escape attempt  
Classification: subsystem orchestration only

4) `src/interaction_layer.py`  
Function(s): `dispatch_player_action`, `_smoke_test_dispatch_structure`  
Coordinates: interaction dispatch, smoke-test encounter generation path  
Classification: dispatcher + smoke helper, not runtime full flow

### B) Files besides `src/simulation_controller.py` coordinating full turn flow

No runtime file besides `src/simulation_controller.py` coordinates:
- travel -> encounter generation -> reaction/pursuit/combat -> reward materialize/apply -> hard-stop reporting.

Verdict:
- SimulationController is the only runtime full-turn orchestrator.
- Legacy harness orchestrator in `src/phase4_integration_test.py` is removed.

---

## 2. HARNESS CLEANUP CHECK

Findings:

- `src/cli_run.py` is the only active CLI runner.
- `src/main.py` is a thin wrapper that calls `cli_run.main()`.
- `src/cli_playable.py` is absent.
- `src/phase4_integration_test.py` is absent.
- `src/cli_test.py`, `src/cli_combat_sim.py`, `src/integration_test.py` still contain utility/demo code, but `__main__` blocks are deprecation prints.

Leftover runtime orchestration outside SimulationController:
- None found.

---

## 3. HULL MAX AUTHORITY CHECK

Findings:

- Canonical hull max computation is in `src/ship_assembler.py`:
  - `compute_hull_max_from_ship_state(...)`
  - `assemble_ship(...)` emits `hull_max`.
- `src/combat_resolver.py` consumes `assembled["hull_max"]` and has no local hull-max formula.
- `src/interaction_resolvers.py` and `src/npc_ship_generator.py` call assembler hull-max function.
- No duplicate hull-max computation path found.

Duplicate computation count: 0.

---

## 4. TAG POLICY CENTRALIZATION CHECK

Findings:

- `src/government_law_engine.py` imports `tag_policy_engine` and delegates interpretation.
- `src/market_pricing.py` imports `tag_policy_engine` and delegates interpretation.
- Per-tag effect logic is centralized in `src/tag_policy_engine.py`.
- No duplicate interpretation table remains in government/pricing modules.

Non-policy tag handling observed:
- `src/turn_loop.py` `_strip_possible_tag(...)` handles SKU prefix normalization only; this is not legality/risk interpretation.

Bypasses of `tag_policy_engine` for policy interpretation: none found.

---

## 5. TIME ENGINE LOGGING CONSISTENCY

Findings:

- `src/time_engine.py` uses shared logger when `_shared_logger` is set.
- Direct `print(...)` remains only as fallback when logger is unavailable.

Assessment:
- Logger abstraction is primary.
- Print fallback is conditional and limited.

---

## 6. DETERMINISM RECONFIRMATION

Findings:

- No `random.random(...)`, `random.choice(...)`, `random.shuffle(...)`, or raw global roll calls detected.
- Randomness remains routed through seeded `random.Random(...)` instances in simulation subsystems.
- `src/simulation_controller.py` does not import or use RNG directly.

Unseeded randomness introduced post-cleanup: none detected.

---

## 7. TEST COVERAGE ALIGNMENT

Findings:

- No tests reference deleted `src/cli_playable.py`.
- No tests reference deleted `src/phase4_integration_test.py`.
- End-to-end orchestration test uses SimulationController:
  - `tests/test_simulation_controller_e2e.py`
- Legacy phase4 test coverage now uses SimulationController:
  - `tests/test_phase4_integration_legacy.py`
- Naming drift fixed:
  - `tests/test_cli_run.py` replaces `tests/test_cli_playable.py`

Outdated test references: none found.

---

## 8. STRUCTURAL VERDICT

- Orchestration violations found: 0 runtime violations.
- Duplicate authority findings: 0.
- Determinism status: PASS.
- Boundary integrity rating: A-.
- Phase 4 simulation layer status: CLEAN.

