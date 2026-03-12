Combat resolution pipeline audit report
1. CombatResult definition (src/combat_resolver.py)
CombatResult (lines 86–101) is a dataclass with these fields:

Field	Type
outcome	OutcomeName ("destroyed", "escape", "surrender", "max_rounds")
rounds	int
winner	Optional[Literal["player", "enemy", "none"]]
final_state_player	dict
final_state_enemy	dict
log	list[dict]
tr_player	int
tr_enemy	int
rcp_player	int
rcp_enemy	int
destruction_event	Optional[dict] = None
surrendered_by	Optional[SideName] = None
salvage_modules	list[dict] = field(default_factory=list)
combat_rng_seed	int = 0
There is no player_won attribute. Victory is represented by winner == "player".

2. Encounter pipeline and where the error happens
There is no encounter_resolver.py in the repo (there is encounter_generator.py, exploration_resolver.py, etc.).
Combat is driven entirely from game_engine.py:
_execute_combat_action(context, payload) runs per-round combat.
It calls resolve_combat_round in combat_resolver.py and gets a round result dict (combat_ended, outcome, round_summary, etc.).
When round_result["combat_ended"] is True, the engine builds a CombatResult instance (e.g. lines 5368, 5249, 5308) and passes it to:
apply_combat_result (combat_application),
then _apply_post_combat_rewards_and_salvage,
then builds combat_result_dict for on_combat_resolved (mission evaluation).
The object that reaches the failing code is that same CombatResult instance built in game_engine; it is not wrapped in an EncounterResult. The pipeline is:

resolve_combat_round ? engine builds CombatResult ? apply_combat_result(combat_result=CombatResult) ? engine builds combat_result_dict from that CombatResult ? on_combat_resolved(combat_result=combat_result_dict).

The CLI only sees the step result from _build_step_result (which does not add combat_ended or combat_result). The crash happens inside the engine before any step result is returned, so the CLI receives the exception path: ok=False, error=str(exc).

3. What the CLI actually receives
When the bug does not trigger (if the fix is applied), the CLI gets the normal _build_step_result dict: ok, error, command_type, turn_before/turn_after, hard_stop, hard_stop_reason, events, player, etc. It does not get combat_ended or combat_result from this path.
The traceback shows the failure inside the engine, not in the CLI: the exception is in game_engine.py at line 5445, in _execute_combat_action, when building combat_result_dict for on_combat_resolved. So at the moment of the error, the code is using the CombatResult instance (same one used a few lines above with .outcome and .winner).
So: the object that triggers the bug is a CombatResult instance with the schema above (no player_won). The CLI does not receive a CombatResult here; it receives an error result from the engine’s exception handler.

4. Where victory is expected and where it’s wrong
Failing code (only place that uses player_won):
src/game_engine.py line 5445
"outcome": "victory" if combat_result.player_won else "defeat",
Here combat_result is the CombatResult dataclass; it has no player_won ? AttributeError.

CLI (src/run_game_engine_cli.py):
Uses result.get("combat_result") and then combat_result.get("outcome", ...) / combat_result.get("winner", ...) (e.g. 1832–1836, 2069–2071, 2252–2254). So the CLI expects combat_result to be a dict with keys like "outcome" and "winner". It never references player_won. The bug is not in the CLI; it’s in the engine.

5. Correct source of victory
CombatResult (and any dict that mirrors it) should derive victory from:
winner == "player"
So:
result.outcome – use for raw outcome ("destroyed", "escape", "surrender", "max_rounds"); for “victory vs defeat” in the mission sense, combine with result.winner == "player".
result.winner == "player" – this is the correct replacement for the non-existent result.player_won.
result.enemy_destroyed – not a field on CombatResult; destruction is implied by outcome == "destroyed" and winner.
result.player_destroyed – not a field; use winner == "enemy" (or destruction_event if you need details).
result.combat_result.player_won – not applicable; the engine builds a single CombatResult and never nests it under another .combat_result in this path.
6. Actual structure and minimal fix
Actual structure of the object used at the failure site

Type: CombatResult (dataclass from combat_resolver).
Relevant attributes: outcome, winner, rounds, final_state_*, log, tr_*, rcp_*, surrendered_by, salvage_modules, combat_rng_seed, etc. No player_won.
Where to read player victory

Use combat_result.winner == "player" everywhere the code currently assumes combat_result.player_won.
Minimal patch (no other changes)

File: src/game_engine.py
Line: 5445
Change:

# Before
"outcome": "victory" if combat_result.player_won else "defeat",
# After
"outcome": "victory" if combat_result.winner == "player" else "defeat",
That is the single change required to fix the observed error. No change to the CLI or to CombatResult is needed for this bug.

Optional note: Line 5446 uses getattr(combat_result, "destroyed_ship_ids", []). CombatResult has no destroyed_ship_ids, so this always yields []. It does not raise; if “destroyed NPCs” for missions should ever be populated from combat, that would be a separate change (e.g. add a field or derive from outcome/winner/destruction_event).

Summary
Item	Finding
Root cause	game_engine.py line 5445 uses combat_result.player_won, which does not exist on CombatResult.
Actual type at failure	CombatResult instance (from combat_resolver), not an EncounterResult wrapper.
Correct victory check	combat_result.winner == "player"
Minimal fix	In src/game_engine.py line 5445, replace combat_result.player_won with combat_result.winner == "player".
CLI	Expects a dict with "winner"/"outcome"; no change needed 