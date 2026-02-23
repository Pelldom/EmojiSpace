PowerShell 7.5.4
PS D:\GitHub\EmojiSpace> python .\src\run_game_engine_cli.py
Seed [12345]:
[v0.11.1][turn 0] action=engine_init change=mission_manager_id=1947282772304
[v0.11.1][turn 0] action=engine:initialization change={"detail": {"starting_destination_marked_visited": true, "starting_system_marked_visited": true}, "stage": "initialization", "subsystem": "engine"}
[v0.11.1][turn 0] action=engine:logging change={"command_type": "set_logging", "detail": {"enabled": true, "log_path": "D:\\GitHub\\EmojiSpace\\logs\\gameplay_seed_12345.log", "truncate": true}, "stage": "logging", "subsystem": "engine", "turn": 0, "world_seed": 12345}
Logging to D:\GitHub\EmojiSpace\logs\gameplay_seed_12345.log
{"event": "engine_init", "seed": 12345}
DESTINATION: Ion 1 (SYS-001)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 5
0) Back
1) SYS-001-DST-01-LOC-datanet type=datanet
2) SYS-001-DST-01-LOC-market type=market
3) SYS-001-DST-01-LOC-bar type=bar
4) SYS-001-DST-01-LOC-warehouse type=warehouse
Select location index: 3
[v0.11.1][turn 0] action=engine:start change={"command_type": "enter_location", "detail": {"command_type": "enter_location"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.1][turn 0] action=npc_registry change=add npc_id=NPC-952663a0
[v0.11.1][turn 0] action=npc_placement change=created location_id=SYS-001-DST-01-LOC-bar npc_id=NPC-952663a0
[v0.11.1][turn 0] action=engine:location_navigation change={"command_type": "enter_location", "detail": {"action": "enter_location", "location_id": "SYS-001-DST-01-LOC-bar", "location_type": "bar", "resolved_npc_ids": ["NPC-952663a0"]}, "stage": "location_navigation", "subsystem": "engine", "turn": 0, "world_seed": 12345}
Entered location: SYS-001-DST-01-LOC-bar
[v0.11.1][turn 0] action=engine:start change={"command_type": "list_location_npcs", "detail": {"command_type": "list_location_npcs"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.1][turn 0] action=engine:location_npcs change={"command_type": "list_location_npcs", "detail": {"location_id": "SYS-001-DST-01-LOC-bar", "npcs": [{"display_name": "Bartender", "npc_id": "NPC-952663a0", "persistence_tier": 3, "role": "bartender"}, {"display_name": "Mission Contact (escort)", "npc_id": "NPC-MSN-48781caf", "persistence_tier": 1, "role": "mission_giver"}]}, "stage": "location_npcs", "subsystem": "engine", "turn": 0, "world_seed": 12345}
LOCATION: SYS-001-DST-01-LOC-bar
NPCs:
  1) Bartender (bartender)
  2) Mission Contact (escort) (mission_giver)
0) Return to destination
Select option: 0
[v0.11.1][turn 0] action=engine:start change={"command_type": "return_to_destination", "detail": {"command_type": "return_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.1][turn 0] action=engine:location_navigation change={"command_type": "return_to_destination", "detail": {"action": "return_to_destination", "destination_id": "SYS-001-DST-01"}, "stage": "location_navigation", "subsystem": "engine", "turn": 0, "world_seed": 12345}
Returned to destination: SYS-001-DST-01
DESTINATION: Ion 1 (SYS-001)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 3
Current system: SYS-001 (Ion)
1) Inter-system warp
2) Intra-system destination travel
3) Back
Travel mode: 2
1) SYS-001-DST-01 Ion 1
2) SYS-001-DST-02 Ion 2
3) SYS-001-DST-03 Ion 3
4) SYS-001-DST-04 Ion 4
Select destination index: 2
[v0.11.1][turn 0] action=engine:start change={"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.1][turn 0] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-001-DST-02", "target_system_id": "SYS-001", "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 0, "world_seed": 12345}
[v0.11.1][turn 0] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"current_fuel": 55, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 0, "world_seed": 12345}
[time_engine] action=time_advance_requested change=start_turn=0 days=1 reason=travel:TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route
[time_engine] action=galaxy_tick change=day=1
[time_engine] action=system_tick change=day=1
[time_engine] action=planet_station_tick change=day=1
[time_engine] action=location_tick change=day=1
[time_engine] action=npc_tick change=day=1
[time_engine] action=end_of_day_log change=day=1
Spawn gate cooldown check: system_id=SYS-001 current_day=1 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=1 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.3377655004504335
[time_engine] action=time_advance_day_completed change=turn=1 hard_stop=None
[v0.11.1][turn 1] action=time_engine:time_advance change={"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 1, "world_seed": 12345}
[v0.11.1][turn 1] action=law_enforcement:law_checkpoint change={"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 1, "world_seed": 12345}
[v0.11.1][turn 1] action=encounter_generator:encounter_gen change={"command_type": "travel_to_destination", "detail": {"encounter_count": 5, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 1, "world_seed": 12345}
[v0.11.1][turn 1] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_0", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 1, "world_seed": 12345}
[v0.11.1][turn 1] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_0", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_0ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 1, "world_seed": 12345}
[v0.11.1][turn 1] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 1, "world_seed": 12345}
[v0.11.1][turn 1] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_2", "handler_payload": {"npc_outcome": "attack"}, "next_handler": "combat_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 1, "world_seed": 12345}
[v0.11.1][turn 1] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_2", "resolver_outcome": {"outcome": "destroyed", "resolver": "combat", "rounds": 3, "winner": "enemy"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 1, "world_seed": 12345}
[v0.11.1][turn 1] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 1, "world_seed": 12345}
[v0.11.1][turn 1] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_3", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 1, "world_seed": 12345}
[v0.11.1][turn 1] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_3", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 1, "world_seed": 12345}
[v0.11.1][turn 1] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_3", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 1, "world_seed": 12345}
[v0.11.1][turn 1] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_4", "handler_payload": {"npc_outcome": "attack"}, "next_handler": "combat_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 1, "world_seed": 12345}
[v0.11.1][turn 1] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_4", "resolver_outcome": {"outcome": "destroyed", "resolver": "combat", "rounds": 1, "winner": "enemy"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 1, "world_seed": 12345}
[v0.11.1][turn 1] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_4", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 1, "world_seed": 12345}
[v0.11.1][turn 1] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_5", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 1, "world_seed": 12345}
[v0.11.1][turn 1] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_5", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 4, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_5ignore0", "selected_outcome": "hail", "tr_delta": 3, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 1, "world_seed": 12345}
[v0.11.1][turn 1] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_5", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 1, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-001-DST-02", "target_system_id": "SYS-001", "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 0, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 55, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 0, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 5, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_0", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_0", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_0ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_2", "handler_payload": {"npc_outcome": "attack"}, "next_handler": "combat_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_2", "resolver_outcome": {"outcome": "destroyed", "resolver": "combat", "rounds": 3, "winner": "enemy"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_3", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_3", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_3", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_4", "handler_payload": {"npc_outcome": "attack"}, "next_handler": "combat_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_4", "resolver_outcome": {"outcome": "destroyed", "resolver": "combat", "rounds": 1, "winner": "enemy"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_4", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_5", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_5", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 4, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_5ignore0", "selected_outcome": "hail", "tr_delta": 3, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_5", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 1, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 5000, "destination_id": "SYS-001-DST-02", "location_id": "SYS-001-DST-02", "system_id": "SYS-001"}, "turn_after": 1, "turn_before": 0, "version": "0.11.1"}
DESTINATION: Ion 2 (SYS-001)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 5
0) Back
1) SYS-001-DST-02-LOC-datanet type=datanet
2) SYS-001-DST-02-LOC-market type=market
Select location index: 0
DESTINATION: Ion 2 (SYS-001)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 3
Current system: SYS-001 (Ion)
1) Inter-system warp
2) Intra-system destination travel
3) Back
Travel mode: 2
1) SYS-001-DST-01 Ion 1
2) SYS-001-DST-02 Ion 2
3) SYS-001-DST-03 Ion 3
4) SYS-001-DST-04 Ion 4
Select destination index: 3
[v0.11.1][turn 1] action=engine:start change={"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 1, "world_seed": 12345}
[v0.11.1][turn 1] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-001-DST-03", "target_system_id": "SYS-001", "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 1, "world_seed": 12345}
[v0.11.1][turn 1] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"current_fuel": 55, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 1, "world_seed": 12345}
[time_engine] action=time_advance_requested change=start_turn=1 days=1 reason=travel:TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route
[time_engine] action=galaxy_tick change=day=2
[time_engine] action=system_tick change=day=2
[time_engine] action=planet_station_tick change=day=2
[time_engine] action=location_tick change=day=2
[time_engine] action=npc_tick change=day=2
[time_engine] action=end_of_day_log change=day=2
Spawn gate cooldown check: system_id=SYS-001 current_day=2 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=2 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.9054936065510267
[time_engine] action=time_advance_day_completed change=turn=2 hard_stop=None
[v0.11.1][turn 2] action=time_engine:time_advance change={"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 2, "world_seed": 12345}
[v0.11.1][turn 2] action=law_enforcement:law_checkpoint change={"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 2, "world_seed": 12345}
[v0.11.1][turn 2] action=encounter_generator:encounter_gen change={"command_type": "travel_to_destination", "detail": {"encounter_count": 4, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 2, "world_seed": 12345}
[v0.11.1][turn 2] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_0", "handler_payload": {"npc_outcome": "pursue"}, "next_handler": "pursuit_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 2, "world_seed": 12345}
[v0.11.1][turn 2] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_0", "resolver_outcome": {"escaped": false, "outcome": "escape_fail", "resolver": "pursuit", "threshold": 0.5}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 2, "world_seed": 12345}
[v0.11.1][turn 2] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 2, "world_seed": 12345}
[v0.11.1][turn 2] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_1", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 2, "world_seed": 12345}
[v0.11.1][turn 2] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_1", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_1ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [2, 5, 1], "weights_after_notoriety": [2, 5, 1], "weights_after_reputation": [2, 5, 1], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 2, "world_seed": 12345}
[v0.11.1][turn 2] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 2, "world_seed": 12345}
[v0.11.1][turn 2] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_2", "handler_payload": {"npc_outcome": "pursue"}, "next_handler": "pursuit_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 2, "world_seed": 12345}
[v0.11.1][turn 2] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_2", "resolver_outcome": {"escaped": false, "outcome": "escape_fail", "resolver": "pursuit", "threshold": 0.45}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 2, "world_seed": 12345}
[v0.11.1][turn 2] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 2, "world_seed": 12345}
[v0.11.1][turn 2] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_3", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 2, "world_seed": 12345}
[v0.11.1][turn 2] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_3", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 2, "world_seed": 12345}
[v0.11.1][turn 2] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_3", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 2, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-001-DST-03", "target_system_id": "SYS-001", "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 55, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 4, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_0", "handler_payload": {"npc_outcome": "pursue"}, "next_handler": "pursuit_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_0", "resolver_outcome": {"escaped": false, "outcome": "escape_fail", "resolver": "pursuit", "threshold": 0.5}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_1", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_1", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_1ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [2, 5, 1], "weights_after_notoriety": [2, 5, 1], "weights_after_reputation": [2, 5, 1], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_2", "handler_payload": {"npc_outcome": "pursue"}, "next_handler": "pursuit_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_2", "resolver_outcome": {"escaped": false, "outcome": "escape_fail", "resolver": "pursuit", "threshold": 0.45}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_3", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_3", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_3", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 2, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 5000, "destination_id": "SYS-001-DST-03", "location_id": "SYS-001-DST-03", "system_id": "SYS-001"}, "turn_after": 2, "turn_before": 1, "version": "0.11.1"}
DESTINATION: Ion 3 (SYS-001)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 5
0) Back
1) SYS-001-DST-03-LOC-datanet type=datanet
2) SYS-001-DST-03-LOC-market type=market
3) SYS-001-DST-03-LOC-bar type=bar
4) SYS-001-DST-03-LOC-warehouse type=warehouse
Select location index: 3
[v0.11.1][turn 2] action=engine:start change={"command_type": "enter_location", "detail": {"command_type": "enter_location"}, "stage": "start", "subsystem": "engine", "turn": 2, "world_seed": 12345}
[v0.11.1][turn 2] action=npc_registry change=add npc_id=NPC-fbeb3b26
[v0.11.1][turn 2] action=npc_placement change=created location_id=SYS-001-DST-03-LOC-bar npc_id=NPC-fbeb3b26
[v0.11.1][turn 2] action=engine:location_navigation change={"command_type": "enter_location", "detail": {"action": "enter_location", "location_id": "SYS-001-DST-03-LOC-bar", "location_type": "bar", "resolved_npc_ids": ["NPC-fbeb3b26"]}, "stage": "location_navigation", "subsystem": "engine", "turn": 2, "world_seed": 12345}
Entered location: SYS-001-DST-03-LOC-bar
[v0.11.1][turn 2] action=engine:start change={"command_type": "list_location_npcs", "detail": {"command_type": "list_location_npcs"}, "stage": "start", "subsystem": "engine", "turn": 2, "world_seed": 12345}
[v0.11.1][turn 2] action=engine:location_npcs change={"command_type": "list_location_npcs", "detail": {"location_id": "SYS-001-DST-03-LOC-bar", "npcs": [{"display_name": "Bartender", "npc_id": "NPC-fbeb3b26", "persistence_tier": 3, "role": "bartender"}, {"display_name": "Mission Contact (delivery)", "npc_id": "NPC-MSN-ae3b4b58", "persistence_tier": 1, "role": "mission_giver"}, {"display_name": "Mission Contact (recovery)", "npc_id": "NPC-MSN-cbc30e58", "persistence_tier": 1, "role": "mission_giver"}]}, "stage": "location_npcs", "subsystem": "engine", "turn": 2, "world_seed": 12345}
LOCATION: SYS-001-DST-03-LOC-bar
NPCs:
  1) Bartender (bartender)
  2) Mission Contact (delivery) (mission_giver)
  3) Mission Contact (recovery) (mission_giver)
0) Return to destination
Select option: 0
[v0.11.1][turn 2] action=engine:start change={"command_type": "return_to_destination", "detail": {"command_type": "return_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 2, "world_seed": 12345}
[v0.11.1][turn 2] action=engine:location_navigation change={"command_type": "return_to_destination", "detail": {"action": "return_to_destination", "destination_id": "SYS-001-DST-03"}, "stage": "location_navigation", "subsystem": "engine", "turn": 2, "world_seed": 12345}
Returned to destination: SYS-001-DST-03
DESTINATION: Ion 3 (SYS-001)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 3
Current system: SYS-001 (Ion)
1) Inter-system warp
2) Intra-system destination travel
3) Back
Travel mode: 1
1) SYS-004 Flux distance_ly=51.844
2) SYS-005 Beacon distance_ly=50.078
Select target system index: 2
[v0.11.1][turn 2] action=engine:start change={"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 2, "world_seed": 12345}
[v0.11.1][turn 2] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"distance_ly": 50.07785749565051, "distance_ly_ceiled": 51, "inter_system": true, "target_destination_id": "SYS-005-DST-01", "target_system_id": "SYS-005", "travel_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 2, "world_seed": 12345}
[v0.11.1][turn 2] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"current_fuel": 4, "fuel_capacity": 55, "fuel_cost": 51, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 2, "world_seed": 12345}
[time_engine] action=time_advance_requested change=start_turn=2 days=10 reason=travel:TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route
[time_engine] action=galaxy_tick change=day=3
[time_engine] action=system_tick change=day=3
[time_engine] action=planet_station_tick change=day=3
[time_engine] action=location_tick change=day=3
[time_engine] action=npc_tick change=day=3
[time_engine] action=end_of_day_log change=day=3
Spawn gate cooldown check: system_id=SYS-005 current_day=3 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=3 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.6731645571630119
[time_engine] action=time_advance_day_completed change=turn=3 hard_stop=None
[time_engine] action=galaxy_tick change=day=4
[time_engine] action=system_tick change=day=4
[time_engine] action=planet_station_tick change=day=4
[time_engine] action=location_tick change=day=4
[time_engine] action=npc_tick change=day=4
[time_engine] action=end_of_day_log change=day=4
Spawn gate cooldown check: system_id=SYS-005 current_day=4 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=4 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.4359311217196765
[time_engine] action=time_advance_day_completed change=turn=4 hard_stop=None
[time_engine] action=galaxy_tick change=day=5
[time_engine] action=system_tick change=day=5
[time_engine] action=planet_station_tick change=day=5
[time_engine] action=location_tick change=day=5
[time_engine] action=npc_tick change=day=5
[time_engine] action=end_of_day_log change=day=5
Spawn gate cooldown check: system_id=SYS-005 current_day=5 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=5 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.5682743811172472
[time_engine] action=time_advance_day_completed change=turn=5 hard_stop=None
[time_engine] action=galaxy_tick change=day=6
[time_engine] action=system_tick change=day=6
[time_engine] action=planet_station_tick change=day=6
[time_engine] action=location_tick change=day=6
[time_engine] action=npc_tick change=day=6
[time_engine] action=end_of_day_log change=day=6
Spawn gate cooldown check: system_id=SYS-005 current_day=6 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=6 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.5145296465009546
[time_engine] action=time_advance_day_completed change=turn=6 hard_stop=None
[time_engine] action=galaxy_tick change=day=7
[time_engine] action=system_tick change=day=7
[time_engine] action=planet_station_tick change=day=7
[time_engine] action=location_tick change=day=7
[time_engine] action=npc_tick change=day=7
[time_engine] action=end_of_day_log change=day=7
Spawn gate cooldown check: system_id=SYS-005 current_day=7 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=7 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.4928969498426904
[time_engine] action=time_advance_day_completed change=turn=7 hard_stop=None
[time_engine] action=galaxy_tick change=day=8
[time_engine] action=system_tick change=day=8
[time_engine] action=planet_station_tick change=day=8
[time_engine] action=location_tick change=day=8
[time_engine] action=npc_tick change=day=8
[time_engine] action=end_of_day_log change=day=8
Spawn gate cooldown check: system_id=SYS-005 current_day=8 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=8 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.8917611854599735
[time_engine] action=time_advance_day_completed change=turn=8 hard_stop=None
[time_engine] action=galaxy_tick change=day=9
[time_engine] action=system_tick change=day=9
[time_engine] action=planet_station_tick change=day=9
[time_engine] action=location_tick change=day=9
[time_engine] action=npc_tick change=day=9
[time_engine] action=end_of_day_log change=day=9
Spawn gate cooldown check: system_id=SYS-005 current_day=9 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=9 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.846688711026966
[time_engine] action=time_advance_day_completed change=turn=9 hard_stop=None
[time_engine] action=galaxy_tick change=day=10
[time_engine] action=system_tick change=day=10
[time_engine] action=planet_station_tick change=day=10
[time_engine] action=location_tick change=day=10
[time_engine] action=npc_tick change=day=10
[time_engine] action=end_of_day_log change=day=10
Spawn gate cooldown check: system_id=SYS-005 current_day=10 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=10 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.1646664001003756
[time_engine] action=time_advance_day_completed change=turn=10 hard_stop=None
[time_engine] action=galaxy_tick change=day=11
[time_engine] action=system_tick change=day=11
[time_engine] action=planet_station_tick change=day=11
[time_engine] action=location_tick change=day=11
[time_engine] action=npc_tick change=day=11
[time_engine] action=end_of_day_log change=day=11
Spawn gate cooldown check: system_id=SYS-005 current_day=11 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=11 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.866968660653858
[time_engine] action=time_advance_day_completed change=turn=11 hard_stop=None
[time_engine] action=galaxy_tick change=day=12
[time_engine] action=system_tick change=day=12
[time_engine] action=planet_station_tick change=day=12
[time_engine] action=location_tick change=day=12
[time_engine] action=npc_tick change=day=12
[time_engine] action=end_of_day_log change=day=12
Spawn gate cooldown check: system_id=SYS-005 current_day=12 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=12 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.6094992726035052
[time_engine] action=time_advance_day_completed change=turn=12 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=12 days=10 reason=travel:TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route
[time_engine] action=galaxy_tick change=day=13
[time_engine] action=system_tick change=day=13
[time_engine] action=planet_station_tick change=day=13
[time_engine] action=location_tick change=day=13
[time_engine] action=npc_tick change=day=13
[time_engine] action=end_of_day_log change=day=13
Spawn gate cooldown check: system_id=SYS-005 current_day=13 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=13 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.7962839280928398
[time_engine] action=time_advance_day_completed change=turn=13 hard_stop=None
[time_engine] action=galaxy_tick change=day=14
[time_engine] action=system_tick change=day=14
[time_engine] action=planet_station_tick change=day=14
[time_engine] action=location_tick change=day=14
[time_engine] action=npc_tick change=day=14
[time_engine] action=end_of_day_log change=day=14
Spawn gate cooldown check: system_id=SYS-005 current_day=14 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=14 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.19564741513578277
[time_engine] action=time_advance_day_completed change=turn=14 hard_stop=None
[time_engine] action=galaxy_tick change=day=15
[time_engine] action=system_tick change=day=15
[time_engine] action=planet_station_tick change=day=15
[time_engine] action=location_tick change=day=15
[time_engine] action=npc_tick change=day=15
[time_engine] action=end_of_day_log change=day=15
Spawn gate cooldown check: system_id=SYS-005 current_day=15 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=15 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.5629714357260357
[time_engine] action=time_advance_day_completed change=turn=15 hard_stop=None
[time_engine] action=galaxy_tick change=day=16
[time_engine] action=system_tick change=day=16
[time_engine] action=planet_station_tick change=day=16
[time_engine] action=location_tick change=day=16
[time_engine] action=npc_tick change=day=16
[time_engine] action=end_of_day_log change=day=16
Spawn gate cooldown check: system_id=SYS-005 current_day=16 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=16 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.15807987466913043
[time_engine] action=time_advance_day_completed change=turn=16 hard_stop=None
[time_engine] action=galaxy_tick change=day=17
[time_engine] action=system_tick change=day=17
[time_engine] action=planet_station_tick change=day=17
[time_engine] action=location_tick change=day=17
[time_engine] action=npc_tick change=day=17
[time_engine] action=end_of_day_log change=day=17
Spawn gate cooldown check: system_id=SYS-005 current_day=17 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=17 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.771068946117502
[time_engine] action=time_advance_day_completed change=turn=17 hard_stop=None
[time_engine] action=galaxy_tick change=day=18
[time_engine] action=system_tick change=day=18
[time_engine] action=planet_station_tick change=day=18
[time_engine] action=location_tick change=day=18
[time_engine] action=npc_tick change=day=18
[time_engine] action=end_of_day_log change=day=18
Spawn gate cooldown check: system_id=SYS-005 current_day=18 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=18 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.3788517681764936
[time_engine] action=time_advance_day_completed change=turn=18 hard_stop=None
[time_engine] action=galaxy_tick change=day=19
[time_engine] action=system_tick change=day=19
[time_engine] action=planet_station_tick change=day=19
[time_engine] action=location_tick change=day=19
[time_engine] action=npc_tick change=day=19
[time_engine] action=end_of_day_log change=day=19
Spawn gate cooldown check: system_id=SYS-005 current_day=19 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=19 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.3566354804809717
[time_engine] action=time_advance_day_completed change=turn=19 hard_stop=None
[time_engine] action=galaxy_tick change=day=20
[time_engine] action=system_tick change=day=20
[time_engine] action=planet_station_tick change=day=20
[time_engine] action=location_tick change=day=20
[time_engine] action=npc_tick change=day=20
[time_engine] action=end_of_day_log change=day=20
Spawn gate cooldown check: system_id=SYS-005 current_day=20 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=20 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.6159021456131522
[time_engine] action=time_advance_day_completed change=turn=20 hard_stop=None
[time_engine] action=galaxy_tick change=day=21
[time_engine] action=system_tick change=day=21
[time_engine] action=planet_station_tick change=day=21
[time_engine] action=location_tick change=day=21
[time_engine] action=npc_tick change=day=21
[time_engine] action=end_of_day_log change=day=21
Spawn gate cooldown check: system_id=SYS-005 current_day=21 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate type+tier selected: system_id=SYS-005 current_day=21 selected_type=situation selected_tier=2 spawn_type_roll=0.5736687270070092 severity_roll=0.4205093108060547
Spawn gate candidate filter: system_id=SYS-005 selected_type=situation selected_tier=2 candidates_found=12
Situation added: luxury_goods_demand system=SYS-005 scope=system_or_destination
Spawn gate cooldown set: system_id=SYS-005 current_day=21 cooldown_until=26 generated_any=true reason=spawn_gate_generation
[time_engine] action=time_advance_day_completed change=turn=21 hard_stop=None
[time_engine] action=galaxy_tick change=day=22
[time_engine] action=system_tick change=day=22
[time_engine] action=planet_station_tick change=day=22
[time_engine] action=location_tick change=day=22
[time_engine] action=npc_tick change=day=22
[time_engine] action=end_of_day_log change=day=22
Spawn gate cooldown check: system_id=SYS-005 current_day=22 cooldown_until=26 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=22 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=22 days=10 reason=travel:TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route
[time_engine] action=galaxy_tick change=day=23
[time_engine] action=system_tick change=day=23
[time_engine] action=planet_station_tick change=day=23
[time_engine] action=location_tick change=day=23
[time_engine] action=npc_tick change=day=23
[time_engine] action=end_of_day_log change=day=23
Spawn gate cooldown check: system_id=SYS-005 current_day=23 cooldown_until=26 skipped=true reason=cooldown_active
Situation expired: luxury_goods_demand system=SYS-005
[time_engine] action=time_advance_day_completed change=turn=23 hard_stop=None
[time_engine] action=galaxy_tick change=day=24
[time_engine] action=system_tick change=day=24
[time_engine] action=planet_station_tick change=day=24
[time_engine] action=location_tick change=day=24
[time_engine] action=npc_tick change=day=24
[time_engine] action=end_of_day_log change=day=24
Spawn gate cooldown check: system_id=SYS-005 current_day=24 cooldown_until=26 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=24 hard_stop=None
[time_engine] action=galaxy_tick change=day=25
[time_engine] action=system_tick change=day=25
[time_engine] action=planet_station_tick change=day=25
[time_engine] action=location_tick change=day=25
[time_engine] action=npc_tick change=day=25
[time_engine] action=end_of_day_log change=day=25
Spawn gate cooldown check: system_id=SYS-005 current_day=25 cooldown_until=26 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=25 hard_stop=None
[time_engine] action=galaxy_tick change=day=26
[time_engine] action=system_tick change=day=26
[time_engine] action=planet_station_tick change=day=26
[time_engine] action=location_tick change=day=26
[time_engine] action=npc_tick change=day=26
[time_engine] action=end_of_day_log change=day=26
Spawn gate cooldown check: system_id=SYS-005 current_day=26 cooldown_until=26 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=26 hard_stop=None
[time_engine] action=galaxy_tick change=day=27
[time_engine] action=system_tick change=day=27
[time_engine] action=planet_station_tick change=day=27
[time_engine] action=location_tick change=day=27
[time_engine] action=npc_tick change=day=27
[time_engine] action=end_of_day_log change=day=27
Spawn gate cooldown check: system_id=SYS-005 current_day=27 cooldown_until=26 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=27 cooldown_until=26 reason=spawn_gate_roll_failed spawn_gate_roll=0.9880899047881916
[time_engine] action=time_advance_day_completed change=turn=27 hard_stop=None
[time_engine] action=galaxy_tick change=day=28
[time_engine] action=system_tick change=day=28
[time_engine] action=planet_station_tick change=day=28
[time_engine] action=location_tick change=day=28
[time_engine] action=npc_tick change=day=28
[time_engine] action=end_of_day_log change=day=28
Spawn gate cooldown check: system_id=SYS-005 current_day=28 cooldown_until=26 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=28 cooldown_until=26 reason=spawn_gate_roll_failed spawn_gate_roll=0.17749767393864613
[time_engine] action=time_advance_day_completed change=turn=28 hard_stop=None
[time_engine] action=galaxy_tick change=day=29
[time_engine] action=system_tick change=day=29
[time_engine] action=planet_station_tick change=day=29
[time_engine] action=location_tick change=day=29
[time_engine] action=npc_tick change=day=29
[time_engine] action=end_of_day_log change=day=29
Spawn gate cooldown check: system_id=SYS-005 current_day=29 cooldown_until=26 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=29 cooldown_until=26 reason=spawn_gate_roll_failed spawn_gate_roll=0.7522922243477242
[time_engine] action=time_advance_day_completed change=turn=29 hard_stop=None
[time_engine] action=galaxy_tick change=day=30
[time_engine] action=system_tick change=day=30
[time_engine] action=planet_station_tick change=day=30
[time_engine] action=location_tick change=day=30
[time_engine] action=npc_tick change=day=30
[time_engine] action=end_of_day_log change=day=30
Spawn gate cooldown check: system_id=SYS-005 current_day=30 cooldown_until=26 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=30 cooldown_until=26 reason=spawn_gate_roll_failed spawn_gate_roll=0.6263084762953393
[time_engine] action=time_advance_day_completed change=turn=30 hard_stop=None
[time_engine] action=galaxy_tick change=day=31
[time_engine] action=system_tick change=day=31
[time_engine] action=planet_station_tick change=day=31
[time_engine] action=location_tick change=day=31
[time_engine] action=npc_tick change=day=31
[time_engine] action=end_of_day_log change=day=31
Spawn gate cooldown check: system_id=SYS-005 current_day=31 cooldown_until=26 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=31 cooldown_until=26 reason=spawn_gate_roll_failed spawn_gate_roll=0.9369552591831481
[time_engine] action=time_advance_day_completed change=turn=31 hard_stop=None
[time_engine] action=galaxy_tick change=day=32
[time_engine] action=system_tick change=day=32
[time_engine] action=planet_station_tick change=day=32
[time_engine] action=location_tick change=day=32
[time_engine] action=npc_tick change=day=32
[time_engine] action=end_of_day_log change=day=32
Spawn gate cooldown check: system_id=SYS-005 current_day=32 cooldown_until=26 skipped=false reason=cooldown_clear
Spawn gate type+tier selected: system_id=SYS-005 current_day=32 selected_type=situation selected_tier=2 spawn_type_roll=0.3282176977950291 severity_roll=0.34701187072896034
Spawn gate candidate filter: system_id=SYS-005 selected_type=situation selected_tier=2 candidates_found=12
Situation added: medical_shortage system=SYS-005 scope=system_or_destination
Spawn gate cooldown set: system_id=SYS-005 current_day=32 cooldown_until=37 generated_any=true reason=spawn_gate_generation
[time_engine] action=time_advance_day_completed change=turn=32 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=32 days=10 reason=travel:TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route
[time_engine] action=galaxy_tick change=day=33
[time_engine] action=system_tick change=day=33
[time_engine] action=planet_station_tick change=day=33
[time_engine] action=location_tick change=day=33
[time_engine] action=npc_tick change=day=33
[time_engine] action=end_of_day_log change=day=33
Spawn gate cooldown check: system_id=SYS-005 current_day=33 cooldown_until=37 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=33 hard_stop=None
[time_engine] action=galaxy_tick change=day=34
[time_engine] action=system_tick change=day=34
[time_engine] action=planet_station_tick change=day=34
[time_engine] action=location_tick change=day=34
[time_engine] action=npc_tick change=day=34
[time_engine] action=end_of_day_log change=day=34
Spawn gate cooldown check: system_id=SYS-005 current_day=34 cooldown_until=37 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=34 hard_stop=None
[time_engine] action=galaxy_tick change=day=35
[time_engine] action=system_tick change=day=35
[time_engine] action=planet_station_tick change=day=35
[time_engine] action=location_tick change=day=35
[time_engine] action=npc_tick change=day=35
[time_engine] action=end_of_day_log change=day=35
Spawn gate cooldown check: system_id=SYS-005 current_day=35 cooldown_until=37 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=35 hard_stop=None
[time_engine] action=galaxy_tick change=day=36
[time_engine] action=system_tick change=day=36
[time_engine] action=planet_station_tick change=day=36
[time_engine] action=location_tick change=day=36
[time_engine] action=npc_tick change=day=36
[time_engine] action=end_of_day_log change=day=36
Spawn gate cooldown check: system_id=SYS-005 current_day=36 cooldown_until=37 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=36 hard_stop=None
[time_engine] action=galaxy_tick change=day=37
[time_engine] action=system_tick change=day=37
[time_engine] action=planet_station_tick change=day=37
[time_engine] action=location_tick change=day=37
[time_engine] action=npc_tick change=day=37
[time_engine] action=end_of_day_log change=day=37
Spawn gate cooldown check: system_id=SYS-005 current_day=37 cooldown_until=37 skipped=true reason=cooldown_active
Situation expired: medical_shortage system=SYS-005
[time_engine] action=time_advance_day_completed change=turn=37 hard_stop=None
[time_engine] action=galaxy_tick change=day=38
[time_engine] action=system_tick change=day=38
[time_engine] action=planet_station_tick change=day=38
[time_engine] action=location_tick change=day=38
[time_engine] action=npc_tick change=day=38
[time_engine] action=end_of_day_log change=day=38
Spawn gate cooldown check: system_id=SYS-005 current_day=38 cooldown_until=37 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=38 cooldown_until=37 reason=spawn_gate_roll_failed spawn_gate_roll=0.11118087800611776
[time_engine] action=time_advance_day_completed change=turn=38 hard_stop=None
[time_engine] action=galaxy_tick change=day=39
[time_engine] action=system_tick change=day=39
[time_engine] action=planet_station_tick change=day=39
[time_engine] action=location_tick change=day=39
[time_engine] action=npc_tick change=day=39
[time_engine] action=end_of_day_log change=day=39
Spawn gate cooldown check: system_id=SYS-005 current_day=39 cooldown_until=37 skipped=false reason=cooldown_clear
Spawn gate type+tier selected: system_id=SYS-005 current_day=39 selected_type=situation selected_tier=2 spawn_type_roll=0.6048129842803233 severity_roll=0.5689654544939294
Spawn gate candidate filter: system_id=SYS-005 selected_type=situation selected_tier=2 candidates_found=12
Situation added: luxury_goods_demand system=SYS-005 scope=system_or_destination
Spawn gate cooldown set: system_id=SYS-005 current_day=39 cooldown_until=44 generated_any=true reason=spawn_gate_generation
[time_engine] action=time_advance_day_completed change=turn=39 hard_stop=None
[time_engine] action=galaxy_tick change=day=40
[time_engine] action=system_tick change=day=40
[time_engine] action=planet_station_tick change=day=40
[time_engine] action=location_tick change=day=40
[time_engine] action=npc_tick change=day=40
[time_engine] action=end_of_day_log change=day=40
Spawn gate cooldown check: system_id=SYS-005 current_day=40 cooldown_until=44 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=40 hard_stop=None
[time_engine] action=galaxy_tick change=day=41
[time_engine] action=system_tick change=day=41
[time_engine] action=planet_station_tick change=day=41
[time_engine] action=location_tick change=day=41
[time_engine] action=npc_tick change=day=41
[time_engine] action=end_of_day_log change=day=41
Spawn gate cooldown check: system_id=SYS-005 current_day=41 cooldown_until=44 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=41 hard_stop=None
[time_engine] action=galaxy_tick change=day=42
[time_engine] action=system_tick change=day=42
[time_engine] action=planet_station_tick change=day=42
[time_engine] action=location_tick change=day=42
[time_engine] action=npc_tick change=day=42
[time_engine] action=end_of_day_log change=day=42
Spawn gate cooldown check: system_id=SYS-005 current_day=42 cooldown_until=44 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=42 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=42 days=10 reason=travel:TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route
[time_engine] action=galaxy_tick change=day=43
[time_engine] action=system_tick change=day=43
[time_engine] action=planet_station_tick change=day=43
[time_engine] action=location_tick change=day=43
[time_engine] action=npc_tick change=day=43
[time_engine] action=end_of_day_log change=day=43
Spawn gate cooldown check: system_id=SYS-005 current_day=43 cooldown_until=44 skipped=true reason=cooldown_active
Situation expired: luxury_goods_demand system=SYS-005
[time_engine] action=time_advance_day_completed change=turn=43 hard_stop=None
[time_engine] action=galaxy_tick change=day=44
[time_engine] action=system_tick change=day=44
[time_engine] action=planet_station_tick change=day=44
[time_engine] action=location_tick change=day=44
[time_engine] action=npc_tick change=day=44
[time_engine] action=end_of_day_log change=day=44
Spawn gate cooldown check: system_id=SYS-005 current_day=44 cooldown_until=44 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=44 hard_stop=None
[time_engine] action=galaxy_tick change=day=45
[time_engine] action=system_tick change=day=45
[time_engine] action=planet_station_tick change=day=45
[time_engine] action=location_tick change=day=45
[time_engine] action=npc_tick change=day=45
[time_engine] action=end_of_day_log change=day=45
Spawn gate cooldown check: system_id=SYS-005 current_day=45 cooldown_until=44 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=45 cooldown_until=44 reason=spawn_gate_roll_failed spawn_gate_roll=0.8726766123681278
[time_engine] action=time_advance_day_completed change=turn=45 hard_stop=None
[time_engine] action=galaxy_tick change=day=46
[time_engine] action=system_tick change=day=46
[time_engine] action=planet_station_tick change=day=46
[time_engine] action=location_tick change=day=46
[time_engine] action=npc_tick change=day=46
[time_engine] action=end_of_day_log change=day=46
Spawn gate cooldown check: system_id=SYS-005 current_day=46 cooldown_until=44 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=46 cooldown_until=44 reason=spawn_gate_roll_failed spawn_gate_roll=0.4930359871727662
[time_engine] action=time_advance_day_completed change=turn=46 hard_stop=None
[time_engine] action=galaxy_tick change=day=47
[time_engine] action=system_tick change=day=47
[time_engine] action=planet_station_tick change=day=47
[time_engine] action=location_tick change=day=47
[time_engine] action=npc_tick change=day=47
[time_engine] action=end_of_day_log change=day=47
Spawn gate cooldown check: system_id=SYS-005 current_day=47 cooldown_until=44 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=47 cooldown_until=44 reason=spawn_gate_roll_failed spawn_gate_roll=0.1145726035773158
[time_engine] action=time_advance_day_completed change=turn=47 hard_stop=None
[time_engine] action=galaxy_tick change=day=48
[time_engine] action=system_tick change=day=48
[time_engine] action=planet_station_tick change=day=48
[time_engine] action=location_tick change=day=48
[time_engine] action=npc_tick change=day=48
[time_engine] action=end_of_day_log change=day=48
Spawn gate cooldown check: system_id=SYS-005 current_day=48 cooldown_until=44 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=48 cooldown_until=44 reason=spawn_gate_roll_failed spawn_gate_roll=0.24886063063449648
[time_engine] action=time_advance_day_completed change=turn=48 hard_stop=None
[time_engine] action=galaxy_tick change=day=49
[time_engine] action=system_tick change=day=49
[time_engine] action=planet_station_tick change=day=49
[time_engine] action=location_tick change=day=49
[time_engine] action=npc_tick change=day=49
[time_engine] action=end_of_day_log change=day=49
Spawn gate cooldown check: system_id=SYS-005 current_day=49 cooldown_until=44 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=49 cooldown_until=44 reason=spawn_gate_roll_failed spawn_gate_roll=0.8718986822911942
[time_engine] action=time_advance_day_completed change=turn=49 hard_stop=None
[time_engine] action=galaxy_tick change=day=50
[time_engine] action=system_tick change=day=50
[time_engine] action=planet_station_tick change=day=50
[time_engine] action=location_tick change=day=50
[time_engine] action=npc_tick change=day=50
[time_engine] action=end_of_day_log change=day=50
Spawn gate cooldown check: system_id=SYS-005 current_day=50 cooldown_until=44 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=50 cooldown_until=44 reason=spawn_gate_roll_failed spawn_gate_roll=0.5656289444248135
[time_engine] action=time_advance_day_completed change=turn=50 hard_stop=None
[time_engine] action=galaxy_tick change=day=51
[time_engine] action=system_tick change=day=51
[time_engine] action=planet_station_tick change=day=51
[time_engine] action=location_tick change=day=51
[time_engine] action=npc_tick change=day=51
[time_engine] action=end_of_day_log change=day=51
Spawn gate cooldown check: system_id=SYS-005 current_day=51 cooldown_until=44 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=51 cooldown_until=44 reason=spawn_gate_roll_failed spawn_gate_roll=0.6740341124629388
[time_engine] action=time_advance_day_completed change=turn=51 hard_stop=None
[time_engine] action=galaxy_tick change=day=52
[time_engine] action=system_tick change=day=52
[time_engine] action=planet_station_tick change=day=52
[time_engine] action=location_tick change=day=52
[time_engine] action=npc_tick change=day=52
[time_engine] action=end_of_day_log change=day=52
Spawn gate cooldown check: system_id=SYS-005 current_day=52 cooldown_until=44 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=52 cooldown_until=44 reason=spawn_gate_roll_failed spawn_gate_roll=0.14265560275428735
[time_engine] action=time_advance_day_completed change=turn=52 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=52 days=1 reason=travel:TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route
[time_engine] action=galaxy_tick change=day=53
[time_engine] action=system_tick change=day=53
[time_engine] action=planet_station_tick change=day=53
[time_engine] action=location_tick change=day=53
[time_engine] action=npc_tick change=day=53
[time_engine] action=end_of_day_log change=day=53
Spawn gate cooldown check: system_id=SYS-005 current_day=53 cooldown_until=44 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=53 cooldown_until=44 reason=spawn_gate_roll_failed spawn_gate_roll=0.6270872769334502
[time_engine] action=time_advance_day_completed change=turn=53 hard_stop=None
[v0.11.1][turn 53] action=time_engine:time_advance change={"command_type": "travel_to_destination", "detail": {"days_completed": 51, "days_requested": 51, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=law_enforcement:law_checkpoint change={"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=encounter_generator:encounter_gen change={"command_type": "travel_to_destination", "detail": {"encounter_count": 5, "travel_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_0", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_0", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": ["attack_plus_one_high_tr_delta"], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_0ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [2, 5, 2], "weights_after_notoriety": [2, 5, 2], "weights_after_reputation": [2, 5, 2], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_1", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_1", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 4, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_1ignore0", "selected_outcome": "hail", "tr_delta": 3, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_3", "handler_payload": {"npc_outcome": "attack"}, "next_handler": "combat_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_3", "resolver_outcome": {"outcome": "max_rounds", "resolver": "combat", "rounds": 3, "winner": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_3", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_4", "handler_payload": {"npc_outcome": "pursue"}, "next_handler": "pursuit_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_4", "resolver_outcome": {"escaped": true, "outcome": "escape_success", "resolver": "pursuit", "threshold": 0.55}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_4", "qualifies": true}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=reward_applicator:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"applied": {"cargo": null, "context": "game_engine", "credits": 1385, "quantity": 0}, "encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_4", "reward_profile_id": "bounty_credit"}, "stage": "conditional_rewards", "subsystem": "reward_applicator", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_5", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_5", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_5", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 53, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 50.07785749565051, "distance_ly_ceiled": 51, "inter_system": true, "target_destination_id": "SYS-005-DST-01", "target_system_id": "SYS-005", "travel_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 4, "fuel_capacity": 55, "fuel_cost": 51, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 51, "days_requested": 51, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 5, "travel_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_0", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_0", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": ["attack_plus_one_high_tr_delta"], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_0ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [2, 5, 2], "weights_after_notoriety": [2, 5, 2], "weights_after_reputation": [2, 5, 2], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_1", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_1", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 4, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_1ignore0", "selected_outcome": "hail", "tr_delta": 3, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_3", "handler_payload": {"npc_outcome": "attack"}, "next_handler": "combat_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_3", "resolver_outcome": {"outcome": "max_rounds", "resolver": "combat", "rounds": 3, "winner": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_3", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_4", "handler_payload": {"npc_outcome": "pursue"}, "next_handler": "pursuit_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_4", "resolver_outcome": {"escaped": true, "outcome": "escape_success", "resolver": "pursuit", "threshold": 0.55}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_4", "qualifies": true}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"applied": {"cargo": null, "context": "game_engine", "credits": 1385, "quantity": 0}, "encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_4", "reward_profile_id": "bounty_credit"}, "stage": "conditional_rewards", "subsystem": "reward_applicator", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_5", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_5", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:2:auto_route_enc_5", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 53, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 6385, "destination_id": "SYS-005-DST-01", "location_id": "SYS-005-DST-01", "system_id": "SYS-005"}, "turn_after": 53, "turn_before": 2, "version": "0.11.1"}
You have arrived in Beacon.
Intra-system destinations:
  1) SYS-005-DST-01 Beacon 1
  2) SYS-005-DST-02 Beacon 2
  3) SYS-005-DST-03 Beacon 3
  4) SYS-005-DST-04 Beacon 4
DESTINATION: Beacon 1 (SYS-005)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 5
0) Back
1) SYS-005-DST-01-LOC-datanet type=datanet
2) SYS-005-DST-01-LOC-market type=market
3) SYS-005-DST-01-LOC-bar type=bar
4) SYS-005-DST-01-LOC-warehouse type=warehouse
Select location index: 3
[v0.11.1][turn 53] action=engine:start change={"command_type": "enter_location", "detail": {"command_type": "enter_location"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=npc_registry change=add npc_id=NPC-5818aff8
[v0.11.1][turn 53] action=npc_placement change=created location_id=SYS-005-DST-01-LOC-bar npc_id=NPC-5818aff8
[v0.11.1][turn 53] action=engine:location_navigation change={"command_type": "enter_location", "detail": {"action": "enter_location", "location_id": "SYS-005-DST-01-LOC-bar", "location_type": "bar", "resolved_npc_ids": ["NPC-5818aff8"]}, "stage": "location_navigation", "subsystem": "engine", "turn": 53, "world_seed": 12345}
Entered location: SYS-005-DST-01-LOC-bar
[v0.11.1][turn 53] action=engine:start change={"command_type": "list_location_npcs", "detail": {"command_type": "list_location_npcs"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=engine:location_npcs change={"command_type": "list_location_npcs", "detail": {"location_id": "SYS-005-DST-01-LOC-bar", "npcs": [{"display_name": "Bartender", "npc_id": "NPC-5818aff8", "persistence_tier": 3, "role": "bartender"}, {"display_name": "Mission Contact (recovery)", "npc_id": "NPC-MSN-063d3ffe", "persistence_tier": 1, "role": "mission_giver"}, {"display_name": "Mission Contact (recovery)", "npc_id": "NPC-MSN-23519d43", "persistence_tier": 1, "role": "mission_giver"}, {"display_name": "Mission Contact (escort)", "npc_id": "NPC-MSN-f521270c", "persistence_tier": 1, "role": "mission_giver"}]}, "stage": "location_npcs", "subsystem": "engine", "turn": 53, "world_seed": 12345}
LOCATION: SYS-005-DST-01-LOC-bar
NPCs:
  1) Bartender (bartender)
  2) Mission Contact (recovery) (mission_giver)
  3) Mission Contact (recovery) (mission_giver)
  4) Mission Contact (escort) (mission_giver)
0) Return to destination
Select option: 0
[v0.11.1][turn 53] action=engine:start change={"command_type": "return_to_destination", "detail": {"command_type": "return_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=engine:location_navigation change={"command_type": "return_to_destination", "detail": {"action": "return_to_destination", "destination_id": "SYS-005-DST-01"}, "stage": "location_navigation", "subsystem": "engine", "turn": 53, "world_seed": 12345}
Returned to destination: SYS-005-DST-01
DESTINATION: Beacon 1 (SYS-005)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 3
Current system: SYS-005 (Beacon)
1) Inter-system warp
2) Intra-system destination travel
3) Back
Travel mode: 2
1) SYS-005-DST-01 Beacon 1
2) SYS-005-DST-02 Beacon 2
3) SYS-005-DST-03 Beacon 3
4) SYS-005-DST-04 Beacon 4
Select destination index: 2
[v0.11.1][turn 53] action=engine:start change={"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-005-DST-02", "target_system_id": "SYS-005", "travel_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 53, "world_seed": 12345}
[v0.11.1][turn 53] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"current_fuel": 4, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 53, "world_seed": 12345}
[time_engine] action=time_advance_requested change=start_turn=53 days=1 reason=travel:TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route
[time_engine] action=galaxy_tick change=day=54
[time_engine] action=system_tick change=day=54
[time_engine] action=planet_station_tick change=day=54
[time_engine] action=location_tick change=day=54
[time_engine] action=npc_tick change=day=54
[time_engine] action=end_of_day_log change=day=54
Spawn gate cooldown check: system_id=SYS-005 current_day=54 cooldown_until=44 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=54 cooldown_until=44 reason=spawn_gate_roll_failed spawn_gate_roll=0.24477651757612784
[time_engine] action=time_advance_day_completed change=turn=54 hard_stop=None
[v0.11.1][turn 54] action=time_engine:time_advance change={"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=law_enforcement:law_checkpoint change={"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=encounter_generator:encounter_gen change={"command_type": "travel_to_destination", "detail": {"encounter_count": 5, "travel_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_0", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_0", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_0ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [2, 5, 1], "weights_after_notoriety": [2, 5, 1], "weights_after_reputation": [2, 5, 1], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_1", "handler_payload": {"npc_outcome": "attack"}, "next_handler": "combat_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_1", "resolver_outcome": {"outcome": "max_rounds", "resolver": "combat", "rounds": 3, "winner": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_3", "handler_payload": {"npc_outcome": "pursue"}, "next_handler": "pursuit_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_3", "resolver_outcome": {"escaped": true, "outcome": "escape_success", "resolver": "pursuit", "threshold": 0.5}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_3", "qualifies": true}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=reward_applicator:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"applied": {"cargo": null, "context": "game_engine", "credits": 1936, "quantity": 0}, "encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_3", "reward_profile_id": "bounty_credit"}, "stage": "conditional_rewards", "subsystem": "reward_applicator", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_4", "handler_payload": {"npc_outcome": "attack"}, "next_handler": "combat_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_4", "resolver_outcome": {"outcome": "destroyed", "resolver": "combat", "rounds": 3, "winner": "enemy"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_4", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_5", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_5", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_5ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_5", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-005-DST-02", "target_system_id": "SYS-005", "travel_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 4, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 5, "travel_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_0", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_0", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_0ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [2, 5, 1], "weights_after_notoriety": [2, 5, 1], "weights_after_reputation": [2, 5, 1], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_1", "handler_payload": {"npc_outcome": "attack"}, "next_handler": "combat_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_1", "resolver_outcome": {"outcome": "max_rounds", "resolver": "combat", "rounds": 3, "winner": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_3", "handler_payload": {"npc_outcome": "pursue"}, "next_handler": "pursuit_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_3", "resolver_outcome": {"escaped": true, "outcome": "escape_success", "resolver": "pursuit", "threshold": 0.5}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_3", "qualifies": true}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"applied": {"cargo": null, "context": "game_engine", "credits": 1936, "quantity": 0}, "encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_3", "reward_profile_id": "bounty_credit"}, "stage": "conditional_rewards", "subsystem": "reward_applicator", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_4", "handler_payload": {"npc_outcome": "attack"}, "next_handler": "combat_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_4", "resolver_outcome": {"outcome": "destroyed", "resolver": "combat", "rounds": 3, "winner": "enemy"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_4", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_5", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_5", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_5ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-02:53:auto_route_enc_5", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 8321, "destination_id": "SYS-005-DST-02", "location_id": "SYS-005-DST-02", "system_id": "SYS-005"}, "turn_after": 54, "turn_before": 53, "version": "0.11.1"}
DESTINATION: Beacon 2 (SYS-005)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 5
0) Back
1) SYS-005-DST-02-LOC-datanet type=datanet
2) SYS-005-DST-02-LOC-market type=market
3) SYS-005-DST-02-LOC-bar type=bar
4) SYS-005-DST-02-LOC-warehouse type=warehouse
5) SYS-005-DST-02-LOC-shipdock type=shipdock
6) SYS-005-DST-02-LOC-administration type=administration
Select location index: 3
[v0.11.1][turn 54] action=engine:start change={"command_type": "enter_location", "detail": {"command_type": "enter_location"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=npc_registry change=add npc_id=NPC-c34f97fa
[v0.11.1][turn 54] action=npc_placement change=created location_id=SYS-005-DST-02-LOC-bar npc_id=NPC-c34f97fa
[v0.11.1][turn 54] action=engine:location_navigation change={"command_type": "enter_location", "detail": {"action": "enter_location", "location_id": "SYS-005-DST-02-LOC-bar", "location_type": "bar", "resolved_npc_ids": ["NPC-c34f97fa"]}, "stage": "location_navigation", "subsystem": "engine", "turn": 54, "world_seed": 12345}
Entered location: SYS-005-DST-02-LOC-bar
[v0.11.1][turn 54] action=engine:start change={"command_type": "list_location_npcs", "detail": {"command_type": "list_location_npcs"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
LOCATION: SYS-005-DST-02-LOC-bar
No NPCs or actions present.
0) Return to destination
Select option: 0
[v0.11.1][turn 54] action=engine:start change={"command_type": "return_to_destination", "detail": {"command_type": "return_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=engine:location_navigation change={"command_type": "return_to_destination", "detail": {"action": "return_to_destination", "destination_id": "SYS-005-DST-02"}, "stage": "location_navigation", "subsystem": "engine", "turn": 54, "world_seed": 12345}
Returned to destination: SYS-005-DST-02
DESTINATION: Beacon 2 (SYS-005)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 5
0) Back
1) SYS-005-DST-02-LOC-datanet type=datanet
2) SYS-005-DST-02-LOC-market type=market
3) SYS-005-DST-02-LOC-bar type=bar
4) SYS-005-DST-02-LOC-warehouse type=warehouse
5) SYS-005-DST-02-LOC-shipdock type=shipdock
6) SYS-005-DST-02-LOC-administration type=administration
Select location index: 2
[v0.11.1][turn 54] action=engine:start change={"command_type": "enter_location", "detail": {"command_type": "enter_location"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=law_enforcement:law_checkpoint change={"command_type": "enter_location", "detail": {"skipped": true, "trigger_type": "CUSTOMS"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=engine:location_navigation change={"command_type": "enter_location", "detail": {"action": "enter_location", "location_id": "SYS-005-DST-02-LOC-market", "location_type": "market", "resolved_npc_ids": []}, "stage": "location_navigation", "subsystem": "engine", "turn": 54, "world_seed": 12345}
Entered location: SYS-005-DST-02-LOC-market
[v0.11.1][turn 54] action=engine:start change={"command_type": "get_market_profile", "detail": {"command_type": "get_market_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=market:market_profile change={"command_type": "get_market_profile", "detail": {"active_situations": [], "categories": {"CHEMICALS": {"consumed": [], "neutral": [], "produced": ["experimental_serums", "industrial_chemicals", "toxic_agents"]}, "ENERGY": {"consumed": ["fusion_cores", "power_cells"], "neutral": [], "produced": ["experimental_reactors", "high_density_fuel", "standard_fuel"]}, "FOOD": {"consumed": [], "neutral": [], "produced": ["fresh_produce", "protein_blocks", "spice_wine"]}, "LUXURY": {"consumed": [], "neutral": ["consumer_goods", "counterfeit_fine_art", "designer_goods"], "produced": []}, "MACHINERY": {"consumed": [], "neutral": [], "produced": ["automated_factories", "industrial_machinery", "mining_equipment"]}, "METAL": {"consumed": ["aluminum_alloy", "decorative_metals", "steel_ingots"], "neutral": [], "produced": []}, "ORE": {"consumed": ["nickel_ore", "radioactive_ore", "rare_earth_ore"], "neutral": [], "produced": []}, "PARTS": {"consumed": ["autonomous_robots", "mechanical_parts", "synthetic_intelligences"], "neutral": [], "produced": ["cybernetic_implants", "electronic_components", "servitor_units"]}}, "destination_id": "SYS-005-DST-02", "primary_economy_id": "agricultural", "secondary_economy_ids": ["industrial"], "system_id": "SYS-005"}, "stage": "market_profile", "subsystem": "market", "turn": 54, "world_seed": 12345}
MARKET PROFILE
  System: SYS-005
  Destination: SYS-005-DST-02
  Primary economy: agricultural
  Active situations: none
  CHEMICALS: produced=['experimental_serums', 'industrial_chemicals', 'toxic_agents'] consumed=[] neutral=[]
  ENERGY: produced=['experimental_reactors', 'high_density_fuel', 'standard_fuel'] consumed=['fusion_cores', 'power_cells'] neutral=[]
  FOOD: produced=['fresh_produce', 'protein_blocks', 'spice_wine'] consumed=[] neutral=[]
  LUXURY: produced=[] consumed=[] neutral=['consumer_goods', 'counterfeit_fine_art', 'designer_goods']
  MACHINERY: produced=['automated_factories', 'industrial_machinery', 'mining_equipment'] consumed=[] neutral=[]
  METAL: produced=[] consumed=['aluminum_alloy', 'decorative_metals', 'steel_ingots'] neutral=[]
  ORE: produced=[] consumed=['nickel_ore', 'radioactive_ore', 'rare_earth_ore'] neutral=[]
  PARTS: produced=['cybernetic_implants', 'electronic_components', 'servitor_units'] consumed=['autonomous_robots', 'mechanical_parts', 'synthetic_intelligences'] neutral=[]
[v0.11.1][turn 54] action=engine:start change={"command_type": "market_buy_list", "detail": {"command_type": "market_buy_list"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=market:market_buy_list change={"command_type": "market_buy_list", "detail": {"destination_id": "SYS-005-DST-02", "rows": [{"available_units": null, "display_name": "Aluminum Alloy", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "aluminum_alloy", "unit_price": 200}, {"available_units": null, "display_name": "Automated Factories", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "automated_factories", "unit_price": 283}, {"available_units": null, "display_name": "Autonomous Robots", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "autonomous_robots", "unit_price": 236}, {"available_units": null, "display_name": "Consumer Goods", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "consumer_goods", "unit_price": 255}, {"available_units": null, "display_name": "Counterfeit Fine Art", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "counterfeit_fine_art", "unit_price": 255}, {"available_units": null, "display_name": "Cybernetic Implants", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "cybernetic_implants", "unit_price": 204}, {"available_units": null, "display_name": "Decorative Metals", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "decorative_metals", "unit_price": 337}, {"available_units": null, "display_name": "Designer Goods", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "designer_goods", "unit_price": 383}, {"available_units": null, "display_name": "Electronic Components", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "electronic_components", "unit_price": 141}, {"available_units": null, "display_name": "Experimental Reactors", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "experimental_reactors", "unit_price": 330}, {"available_units": null, "display_name": "Experimental Serums", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "experimental_serums", "unit_price": 236}, {"available_units": null, "display_name": "Fresh Produce", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "fresh_produce", "unit_price": 94}, {"available_units": null, "display_name": "Fusion Cores", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "fusion_cores", "unit_price": 267}, {"available_units": null, "display_name": "High-Density Fuel", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "high_density_fuel", "unit_price": 157}, {"available_units": null, "display_name": "Industrial Chemicals", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "industrial_chemicals", "unit_price": 118}, {"available_units": null, "display_name": "Industrial Machinery", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "industrial_machinery", "unit_price": 204}, {"available_units": null, "display_name": "Mechanical Parts", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "mechanical_parts", "unit_price": 126}, {"available_units": null, "display_name": "Mining Equipment", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "mining_equipment", "unit_price": 220}, {"available_units": null, "display_name": "Nickel Ore", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "nickel_ore", "unit_price": 165}, {"available_units": null, "display_name": "Power Cells", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "power_cells", "unit_price": 141}, {"available_units": null, "display_name": "Protein Blocks", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "protein_blocks", "unit_price": 110}, {"available_units": null, "display_name": "Radioactive Ore", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "radioactive_ore", "unit_price": 259}, {"available_units": null, "display_name": "Rare Earth Ore", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "rare_earth_ore", "unit_price": 212}, {"available_units": null, "display_name": "Servitor Units", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "servitor_units", "unit_price": 173}, {"available_units": null, "display_name": "Spice Wine", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "spice_wine", "unit_price": 126}, {"available_units": null, "display_name": "Standard Fuel", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "standard_fuel", "unit_price": 118}, {"available_units": null, "display_name": "Steel Ingots", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "steel_ingots", "unit_price": 188}, {"available_units": null, "display_name": "Synthetic Intelligences", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "synthetic_intelligences", "unit_price": 330}, {"available_units": null, "display_name": "Toxic Agents", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "toxic_agents", "unit_price": 204}]}, "stage": "market_buy_list", "subsystem": "market", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=engine:start change={"command_type": "market_sell_list", "detail": {"command_type": "market_sell_list"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=market:market_sell_list change={"command_type": "market_sell_list", "detail": {"destination_id": "SYS-005-DST-02", "rows": []}, "stage": "market_sell_list", "subsystem": "market", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {}, "credits": 8321, "crew_wages_per_turn": 0, "destination_id": "SYS-005-DST-02", "fuel_capacity": 55, "fuel_current": 4, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-005-DST-02-LOC-market", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "ship": {"crew": [], "crew_capacity": 0, "crew_current": 0, "current_fuel": 4, "data_cargo_capacity": 3, "effective_data_cargo_capacity": 3, "effective_physical_cargo_capacity": 8, "fuel_capacity": 55, "hull_id": "civ_t1_midge", "installed_modules": [], "model_id": "civ_t1_midge", "physical_cargo_capacity": 8, "ship_id": "PLAYER-SHIP-001", "subsystem_bands": {"defense": 0, "engine": 0, "weapon": 0}, "tier": 1}, "system_id": "SYS-005", "total_recurring_cost_per_turn": 0, "turn": 54, "warehouse_cost_per_turn": 0, "warehouses": [], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
MARKET SKUS
  aluminum_alloy | Aluminum Alloy | buy=200 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  automated_factories | Automated Factories | buy=283 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  autonomous_robots | Autonomous Robots | buy=236 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  consumer_goods | Consumer Goods | buy=255 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  counterfeit_fine_art | Counterfeit Fine Art | buy=255 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  cybernetic_implants | Cybernetic Implants | buy=204 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  decorative_metals | Decorative Metals | buy=337 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  designer_goods | Designer Goods | buy=383 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  electronic_components | Electronic Components | buy=141 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  experimental_reactors | Experimental Reactors | buy=330 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  experimental_serums | Experimental Serums | buy=236 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  fresh_produce | Fresh Produce | buy=94 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  fusion_cores | Fusion Cores | buy=267 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  high_density_fuel | High-Density Fuel | buy=157 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  industrial_chemicals | Industrial Chemicals | buy=118 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  industrial_machinery | Industrial Machinery | buy=204 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  mechanical_parts | Mechanical Parts | buy=126 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  mining_equipment | Mining Equipment | buy=220 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  nickel_ore | Nickel Ore | buy=165 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  power_cells | Power Cells | buy=141 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  protein_blocks | Protein Blocks | buy=110 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  radioactive_ore | Radioactive Ore | buy=259 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  rare_earth_ore | Rare Earth Ore | buy=212 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  servitor_units | Servitor Units | buy=173 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  spice_wine | Spice Wine | buy=126 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  standard_fuel | Standard Fuel | buy=118 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  steel_ingots | Steel Ingots | buy=188 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  synthetic_intelligences | Synthetic Intelligences | buy=330 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  toxic_agents | Toxic Agents | buy=204 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index:
Invalid action index.
[v0.11.1][turn 54] action=engine:start change={"command_type": "get_market_profile", "detail": {"command_type": "get_market_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=market:market_profile change={"command_type": "get_market_profile", "detail": {"active_situations": [], "categories": {"CHEMICALS": {"consumed": [], "neutral": [], "produced": ["experimental_serums", "industrial_chemicals", "toxic_agents"]}, "ENERGY": {"consumed": ["fusion_cores", "power_cells"], "neutral": [], "produced": ["experimental_reactors", "high_density_fuel", "standard_fuel"]}, "FOOD": {"consumed": [], "neutral": [], "produced": ["fresh_produce", "protein_blocks", "spice_wine"]}, "LUXURY": {"consumed": [], "neutral": ["consumer_goods", "counterfeit_fine_art", "designer_goods"], "produced": []}, "MACHINERY": {"consumed": [], "neutral": [], "produced": ["automated_factories", "industrial_machinery", "mining_equipment"]}, "METAL": {"consumed": ["aluminum_alloy", "decorative_metals", "steel_ingots"], "neutral": [], "produced": []}, "ORE": {"consumed": ["nickel_ore", "radioactive_ore", "rare_earth_ore"], "neutral": [], "produced": []}, "PARTS": {"consumed": ["autonomous_robots", "mechanical_parts", "synthetic_intelligences"], "neutral": [], "produced": ["cybernetic_implants", "electronic_components", "servitor_units"]}}, "destination_id": "SYS-005-DST-02", "primary_economy_id": "agricultural", "secondary_economy_ids": ["industrial"], "system_id": "SYS-005"}, "stage": "market_profile", "subsystem": "market", "turn": 54, "world_seed": 12345}
MARKET PROFILE
  System: SYS-005
  Destination: SYS-005-DST-02
  Primary economy: agricultural
  Active situations: none
  CHEMICALS: produced=['experimental_serums', 'industrial_chemicals', 'toxic_agents'] consumed=[] neutral=[]
  ENERGY: produced=['experimental_reactors', 'high_density_fuel', 'standard_fuel'] consumed=['fusion_cores', 'power_cells'] neutral=[]
  FOOD: produced=['fresh_produce', 'protein_blocks', 'spice_wine'] consumed=[] neutral=[]
  LUXURY: produced=[] consumed=[] neutral=['consumer_goods', 'counterfeit_fine_art', 'designer_goods']
  MACHINERY: produced=['automated_factories', 'industrial_machinery', 'mining_equipment'] consumed=[] neutral=[]
  METAL: produced=[] consumed=['aluminum_alloy', 'decorative_metals', 'steel_ingots'] neutral=[]
  ORE: produced=[] consumed=['nickel_ore', 'radioactive_ore', 'rare_earth_ore'] neutral=[]
  PARTS: produced=['cybernetic_implants', 'electronic_components', 'servitor_units'] consumed=['autonomous_robots', 'mechanical_parts', 'synthetic_intelligences'] neutral=[]
[v0.11.1][turn 54] action=engine:start change={"command_type": "market_buy_list", "detail": {"command_type": "market_buy_list"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=market:market_buy_list change={"command_type": "market_buy_list", "detail": {"destination_id": "SYS-005-DST-02", "rows": [{"available_units": null, "display_name": "Aluminum Alloy", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "aluminum_alloy", "unit_price": 200}, {"available_units": null, "display_name": "Automated Factories", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "automated_factories", "unit_price": 283}, {"available_units": null, "display_name": "Autonomous Robots", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "autonomous_robots", "unit_price": 236}, {"available_units": null, "display_name": "Consumer Goods", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "consumer_goods", "unit_price": 255}, {"available_units": null, "display_name": "Counterfeit Fine Art", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "counterfeit_fine_art", "unit_price": 255}, {"available_units": null, "display_name": "Cybernetic Implants", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "cybernetic_implants", "unit_price": 204}, {"available_units": null, "display_name": "Decorative Metals", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "decorative_metals", "unit_price": 337}, {"available_units": null, "display_name": "Designer Goods", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "designer_goods", "unit_price": 383}, {"available_units": null, "display_name": "Electronic Components", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "electronic_components", "unit_price": 141}, {"available_units": null, "display_name": "Experimental Reactors", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "experimental_reactors", "unit_price": 330}, {"available_units": null, "display_name": "Experimental Serums", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "experimental_serums", "unit_price": 236}, {"available_units": null, "display_name": "Fresh Produce", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "fresh_produce", "unit_price": 94}, {"available_units": null, "display_name": "Fusion Cores", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "fusion_cores", "unit_price": 267}, {"available_units": null, "display_name": "High-Density Fuel", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "high_density_fuel", "unit_price": 157}, {"available_units": null, "display_name": "Industrial Chemicals", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "industrial_chemicals", "unit_price": 118}, {"available_units": null, "display_name": "Industrial Machinery", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "industrial_machinery", "unit_price": 204}, {"available_units": null, "display_name": "Mechanical Parts", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "mechanical_parts", "unit_price": 126}, {"available_units": null, "display_name": "Mining Equipment", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "mining_equipment", "unit_price": 220}, {"available_units": null, "display_name": "Nickel Ore", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "nickel_ore", "unit_price": 165}, {"available_units": null, "display_name": "Power Cells", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "power_cells", "unit_price": 141}, {"available_units": null, "display_name": "Protein Blocks", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "protein_blocks", "unit_price": 110}, {"available_units": null, "display_name": "Radioactive Ore", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "radioactive_ore", "unit_price": 259}, {"available_units": null, "display_name": "Rare Earth Ore", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "rare_earth_ore", "unit_price": 212}, {"available_units": null, "display_name": "Servitor Units", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "servitor_units", "unit_price": 173}, {"available_units": null, "display_name": "Spice Wine", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "spice_wine", "unit_price": 126}, {"available_units": null, "display_name": "Standard Fuel", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "standard_fuel", "unit_price": 118}, {"available_units": null, "display_name": "Steel Ingots", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "steel_ingots", "unit_price": 188}, {"available_units": null, "display_name": "Synthetic Intelligences", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "synthetic_intelligences", "unit_price": 330}, {"available_units": null, "display_name": "Toxic Agents", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "toxic_agents", "unit_price": 204}]}, "stage": "market_buy_list", "subsystem": "market", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=engine:start change={"command_type": "market_sell_list", "detail": {"command_type": "market_sell_list"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=market:market_sell_list change={"command_type": "market_sell_list", "detail": {"destination_id": "SYS-005-DST-02", "rows": []}, "stage": "market_sell_list", "subsystem": "market", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {}, "credits": 8321, "crew_wages_per_turn": 0, "destination_id": "SYS-005-DST-02", "fuel_capacity": 55, "fuel_current": 4, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-005-DST-02-LOC-market", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "ship": {"crew": [], "crew_capacity": 0, "crew_current": 0, "current_fuel": 4, "data_cargo_capacity": 3, "effective_data_cargo_capacity": 3, "effective_physical_cargo_capacity": 8, "fuel_capacity": 55, "hull_id": "civ_t1_midge", "installed_modules": [], "model_id": "civ_t1_midge", "physical_cargo_capacity": 8, "ship_id": "PLAYER-SHIP-001", "subsystem_bands": {"defense": 0, "engine": 0, "weapon": 0}, "tier": 1}, "system_id": "SYS-005", "total_recurring_cost_per_turn": 0, "turn": 54, "warehouse_cost_per_turn": 0, "warehouses": [], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
MARKET SKUS
  aluminum_alloy | Aluminum Alloy | buy=200 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  automated_factories | Automated Factories | buy=283 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  autonomous_robots | Autonomous Robots | buy=236 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  consumer_goods | Consumer Goods | buy=255 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  counterfeit_fine_art | Counterfeit Fine Art | buy=255 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  cybernetic_implants | Cybernetic Implants | buy=204 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  decorative_metals | Decorative Metals | buy=337 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  designer_goods | Designer Goods | buy=383 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  electronic_components | Electronic Components | buy=141 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  experimental_reactors | Experimental Reactors | buy=330 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  experimental_serums | Experimental Serums | buy=236 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  fresh_produce | Fresh Produce | buy=94 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  fusion_cores | Fusion Cores | buy=267 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  high_density_fuel | High-Density Fuel | buy=157 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  industrial_chemicals | Industrial Chemicals | buy=118 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  industrial_machinery | Industrial Machinery | buy=204 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  mechanical_parts | Mechanical Parts | buy=126 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  mining_equipment | Mining Equipment | buy=220 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  nickel_ore | Nickel Ore | buy=165 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  power_cells | Power Cells | buy=141 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  protein_blocks | Protein Blocks | buy=110 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  radioactive_ore | Radioactive Ore | buy=259 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  rare_earth_ore | Rare Earth Ore | buy=212 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  servitor_units | Servitor Units | buy=173 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  spice_wine | Spice Wine | buy=126 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  standard_fuel | Standard Fuel | buy=118 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  steel_ingots | Steel Ingots | buy=188 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  synthetic_intelligences | Synthetic Intelligences | buy=330 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  toxic_agents | Toxic Agents | buy=204 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index:
Invalid action index.
[v0.11.1][turn 54] action=engine:start change={"command_type": "get_market_profile", "detail": {"command_type": "get_market_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=market:market_profile change={"command_type": "get_market_profile", "detail": {"active_situations": [], "categories": {"CHEMICALS": {"consumed": [], "neutral": [], "produced": ["experimental_serums", "industrial_chemicals", "toxic_agents"]}, "ENERGY": {"consumed": ["fusion_cores", "power_cells"], "neutral": [], "produced": ["experimental_reactors", "high_density_fuel", "standard_fuel"]}, "FOOD": {"consumed": [], "neutral": [], "produced": ["fresh_produce", "protein_blocks", "spice_wine"]}, "LUXURY": {"consumed": [], "neutral": ["consumer_goods", "counterfeit_fine_art", "designer_goods"], "produced": []}, "MACHINERY": {"consumed": [], "neutral": [], "produced": ["automated_factories", "industrial_machinery", "mining_equipment"]}, "METAL": {"consumed": ["aluminum_alloy", "decorative_metals", "steel_ingots"], "neutral": [], "produced": []}, "ORE": {"consumed": ["nickel_ore", "radioactive_ore", "rare_earth_ore"], "neutral": [], "produced": []}, "PARTS": {"consumed": ["autonomous_robots", "mechanical_parts", "synthetic_intelligences"], "neutral": [], "produced": ["cybernetic_implants", "electronic_components", "servitor_units"]}}, "destination_id": "SYS-005-DST-02", "primary_economy_id": "agricultural", "secondary_economy_ids": ["industrial"], "system_id": "SYS-005"}, "stage": "market_profile", "subsystem": "market", "turn": 54, "world_seed": 12345}
MARKET PROFILE
  System: SYS-005
  Destination: SYS-005-DST-02
  Primary economy: agricultural
  Active situations: none
  CHEMICALS: produced=['experimental_serums', 'industrial_chemicals', 'toxic_agents'] consumed=[] neutral=[]
  ENERGY: produced=['experimental_reactors', 'high_density_fuel', 'standard_fuel'] consumed=['fusion_cores', 'power_cells'] neutral=[]
  FOOD: produced=['fresh_produce', 'protein_blocks', 'spice_wine'] consumed=[] neutral=[]
  LUXURY: produced=[] consumed=[] neutral=['consumer_goods', 'counterfeit_fine_art', 'designer_goods']
  MACHINERY: produced=['automated_factories', 'industrial_machinery', 'mining_equipment'] consumed=[] neutral=[]
  METAL: produced=[] consumed=['aluminum_alloy', 'decorative_metals', 'steel_ingots'] neutral=[]
  ORE: produced=[] consumed=['nickel_ore', 'radioactive_ore', 'rare_earth_ore'] neutral=[]
  PARTS: produced=['cybernetic_implants', 'electronic_components', 'servitor_units'] consumed=['autonomous_robots', 'mechanical_parts', 'synthetic_intelligences'] neutral=[]
[v0.11.1][turn 54] action=engine:start change={"command_type": "market_buy_list", "detail": {"command_type": "market_buy_list"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=market:market_buy_list change={"command_type": "market_buy_list", "detail": {"destination_id": "SYS-005-DST-02", "rows": [{"available_units": null, "display_name": "Aluminum Alloy", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "aluminum_alloy", "unit_price": 200}, {"available_units": null, "display_name": "Automated Factories", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "automated_factories", "unit_price": 283}, {"available_units": null, "display_name": "Autonomous Robots", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "autonomous_robots", "unit_price": 236}, {"available_units": null, "display_name": "Consumer Goods", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "consumer_goods", "unit_price": 255}, {"available_units": null, "display_name": "Counterfeit Fine Art", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "counterfeit_fine_art", "unit_price": 255}, {"available_units": null, "display_name": "Cybernetic Implants", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "cybernetic_implants", "unit_price": 204}, {"available_units": null, "display_name": "Decorative Metals", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "decorative_metals", "unit_price": 337}, {"available_units": null, "display_name": "Designer Goods", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "designer_goods", "unit_price": 383}, {"available_units": null, "display_name": "Electronic Components", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "electronic_components", "unit_price": 141}, {"available_units": null, "display_name": "Experimental Reactors", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "experimental_reactors", "unit_price": 330}, {"available_units": null, "display_name": "Experimental Serums", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "experimental_serums", "unit_price": 236}, {"available_units": null, "display_name": "Fresh Produce", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "fresh_produce", "unit_price": 94}, {"available_units": null, "display_name": "Fusion Cores", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "fusion_cores", "unit_price": 267}, {"available_units": null, "display_name": "High-Density Fuel", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "high_density_fuel", "unit_price": 157}, {"available_units": null, "display_name": "Industrial Chemicals", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "industrial_chemicals", "unit_price": 118}, {"available_units": null, "display_name": "Industrial Machinery", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "industrial_machinery", "unit_price": 204}, {"available_units": null, "display_name": "Mechanical Parts", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "mechanical_parts", "unit_price": 126}, {"available_units": null, "display_name": "Mining Equipment", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "mining_equipment", "unit_price": 220}, {"available_units": null, "display_name": "Nickel Ore", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "nickel_ore", "unit_price": 165}, {"available_units": null, "display_name": "Power Cells", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "power_cells", "unit_price": 141}, {"available_units": null, "display_name": "Protein Blocks", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "protein_blocks", "unit_price": 110}, {"available_units": null, "display_name": "Radioactive Ore", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "radioactive_ore", "unit_price": 259}, {"available_units": null, "display_name": "Rare Earth Ore", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "rare_earth_ore", "unit_price": 212}, {"available_units": null, "display_name": "Servitor Units", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "servitor_units", "unit_price": 173}, {"available_units": null, "display_name": "Spice Wine", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "spice_wine", "unit_price": 126}, {"available_units": null, "display_name": "Standard Fuel", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "standard_fuel", "unit_price": 118}, {"available_units": null, "display_name": "Steel Ingots", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "steel_ingots", "unit_price": 188}, {"available_units": null, "display_name": "Synthetic Intelligences", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "synthetic_intelligences", "unit_price": 330}, {"available_units": null, "display_name": "Toxic Agents", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "toxic_agents", "unit_price": 204}]}, "stage": "market_buy_list", "subsystem": "market", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=engine:start change={"command_type": "market_sell_list", "detail": {"command_type": "market_sell_list"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=market:market_sell_list change={"command_type": "market_sell_list", "detail": {"destination_id": "SYS-005-DST-02", "rows": []}, "stage": "market_sell_list", "subsystem": "market", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {}, "credits": 8321, "crew_wages_per_turn": 0, "destination_id": "SYS-005-DST-02", "fuel_capacity": 55, "fuel_current": 4, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-005-DST-02-LOC-market", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "ship": {"crew": [], "crew_capacity": 0, "crew_current": 0, "current_fuel": 4, "data_cargo_capacity": 3, "effective_data_cargo_capacity": 3, "effective_physical_cargo_capacity": 8, "fuel_capacity": 55, "hull_id": "civ_t1_midge", "installed_modules": [], "model_id": "civ_t1_midge", "physical_cargo_capacity": 8, "ship_id": "PLAYER-SHIP-001", "subsystem_bands": {"defense": 0, "engine": 0, "weapon": 0}, "tier": 1}, "system_id": "SYS-005", "total_recurring_cost_per_turn": 0, "turn": 54, "warehouse_cost_per_turn": 0, "warehouses": [], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
MARKET SKUS
  aluminum_alloy | Aluminum Alloy | buy=200 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  automated_factories | Automated Factories | buy=283 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  autonomous_robots | Autonomous Robots | buy=236 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  consumer_goods | Consumer Goods | buy=255 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  counterfeit_fine_art | Counterfeit Fine Art | buy=255 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  cybernetic_implants | Cybernetic Implants | buy=204 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  decorative_metals | Decorative Metals | buy=337 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  designer_goods | Designer Goods | buy=383 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  electronic_components | Electronic Components | buy=141 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  experimental_reactors | Experimental Reactors | buy=330 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  experimental_serums | Experimental Serums | buy=236 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  fresh_produce | Fresh Produce | buy=94 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  fusion_cores | Fusion Cores | buy=267 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  high_density_fuel | High-Density Fuel | buy=157 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  industrial_chemicals | Industrial Chemicals | buy=118 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  industrial_machinery | Industrial Machinery | buy=204 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  mechanical_parts | Mechanical Parts | buy=126 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  mining_equipment | Mining Equipment | buy=220 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  nickel_ore | Nickel Ore | buy=165 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  power_cells | Power Cells | buy=141 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  protein_blocks | Protein Blocks | buy=110 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  radioactive_ore | Radioactive Ore | buy=259 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  rare_earth_ore | Rare Earth Ore | buy=212 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  servitor_units | Servitor Units | buy=173 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  spice_wine | Spice Wine | buy=126 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  standard_fuel | Standard Fuel | buy=118 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  steel_ingots | Steel Ingots | buy=188 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  synthetic_intelligences | Synthetic Intelligences | buy=330 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  toxic_agents | Toxic Agents | buy=204 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 3
[v0.11.1][turn 54] action=engine:start change={"command_type": "return_to_destination", "detail": {"command_type": "return_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=engine:location_navigation change={"command_type": "return_to_destination", "detail": {"action": "return_to_destination", "destination_id": "SYS-005-DST-02"}, "stage": "location_navigation", "subsystem": "engine", "turn": 54, "world_seed": 12345}
Returned to destination: SYS-005-DST-02
DESTINATION: Beacon 2 (SYS-005)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 5
0) Back
1) SYS-005-DST-02-LOC-datanet type=datanet
2) SYS-005-DST-02-LOC-market type=market
3) SYS-005-DST-02-LOC-bar type=bar
4) SYS-005-DST-02-LOC-warehouse type=warehouse
5) SYS-005-DST-02-LOC-shipdock type=shipdock
6) SYS-005-DST-02-LOC-administration type=administration
Select location index: 6
[v0.11.1][turn 54] action=engine:start change={"command_type": "enter_location", "detail": {"command_type": "enter_location"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=npc_registry change=add npc_id=NPC-cdd44d54
[v0.11.1][turn 54] action=npc_placement change=created location_id=SYS-005-DST-02-LOC-administration npc_id=NPC-cdd44d54
[v0.11.1][turn 54] action=engine:location_navigation change={"command_type": "enter_location", "detail": {"action": "enter_location", "location_id": "SYS-005-DST-02-LOC-administration", "location_type": "administration", "resolved_npc_ids": ["NPC-cdd44d54"]}, "stage": "location_navigation", "subsystem": "engine", "turn": 54, "world_seed": 12345}
Entered location: SYS-005-DST-02-LOC-administration
[v0.11.1][turn 54] action=engine:start change={"command_type": "list_location_npcs", "detail": {"command_type": "list_location_npcs"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=engine:location_npcs change={"command_type": "list_location_npcs", "detail": {"location_id": "SYS-005-DST-02-LOC-administration", "npcs": [{"display_name": "Administrator", "npc_id": "NPC-cdd44d54", "persistence_tier": 3, "role": "administrator"}]}, "stage": "location_npcs", "subsystem": "engine", "turn": 54, "world_seed": 12345}
LOCATION: SYS-005-DST-02-LOC-administration
[v0.11.1][turn 54] action=engine:start change={"command_type": "list_location_actions", "detail": {"command_type": "list_location_actions"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=interaction_layer:location_actions change={"command_type": "list_location_actions", "detail": {"actions": [{"action_id": "admin_apply_license", "description": "Apply for restricted trade license.", "display_name": "Apply License", "fuel_cost": 0, "parameters": [], "requires_confirm": false, "time_cost_days": 0}, {"action_id": "admin_mission_board", "description": "Review officially posted contracts.", "display_name": "View Mission Board", "fuel_cost": 0, "parameters": [], "requires_confirm": false, "time_cost_days": 0}, {"action_id": "admin_pay_fines", "description": "Pay outstanding fines for this system.", "display_name": "Pay Fines", "fuel_cost": 0, "parameters": [], "requires_confirm": false, "time_cost_days": 0}, {"action_id": "admin_talk", "description": "Talk to administration personnel.", "display_name": "Talk", "fuel_cost": 0, "parameters": [], "requires_confirm": false, "time_cost_days": 0}, {"action_id": "admin_turn_in", "description": "Turn in outstanding warrants.", "display_name": "Turn In", "fuel_cost": 0, "parameters": [], "requires_confirm": false, "time_cost_days": 0}], "location_id": "SYS-005-DST-02-LOC-administration"}, "stage": "location_actions", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
NPCs:
  1) Administrator (administrator)
Location Actions:
  2) View Mission Board
0) Return to destination
Select option: 2
[v0.11.1][turn 54] action=engine:start change={"command_type": "location_action", "detail": {"command_type": "location_action"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=mission_list_instance_check change=mission_manager_id=1947282772304 location_id=SYS-005-DST-02-LOC-administration
[v0.11.1][turn 54] action=mission:location_action change={"command_type": "location_action", "detail": {"action_id": "mission_list", "missions": [{"mission_id": "MIS-133a9c576e", "mission_state": "MissionState.OFFERED", "mission_tier": 2, "mission_type": "escort", "rewards": [{"amount": 100, "type": "credits"}]}, {"mission_id": "MIS-ceee4e9a54", "mission_state": "MissionState.OFFERED", "mission_tier": 3, "mission_type": "delivery", "rewards": [{"amount": 150, "type": "credits"}]}]}, "stage": "location_action", "subsystem": "mission", "turn": 54, "world_seed": 12345}
MISSION BOARD
  1) escort (Tier 2) – 100 credits
  2) delivery (Tier 3) – 150 credits

Select mission index to discuss (0 to cancel): 0
[v0.11.1][turn 54] action=engine:start change={"command_type": "list_location_npcs", "detail": {"command_type": "list_location_npcs"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=engine:location_npcs change={"command_type": "list_location_npcs", "detail": {"location_id": "SYS-005-DST-02-LOC-administration", "npcs": [{"display_name": "Administrator", "npc_id": "NPC-cdd44d54", "persistence_tier": 3, "role": "administrator"}]}, "stage": "location_npcs", "subsystem": "engine", "turn": 54, "world_seed": 12345}
LOCATION: SYS-005-DST-02-LOC-administration
[v0.11.1][turn 54] action=engine:start change={"command_type": "list_location_actions", "detail": {"command_type": "list_location_actions"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=interaction_layer:location_actions change={"command_type": "list_location_actions", "detail": {"actions": [{"action_id": "admin_apply_license", "description": "Apply for restricted trade license.", "display_name": "Apply License", "fuel_cost": 0, "parameters": [], "requires_confirm": false, "time_cost_days": 0}, {"action_id": "admin_mission_board", "description": "Review officially posted contracts.", "display_name": "View Mission Board", "fuel_cost": 0, "parameters": [], "requires_confirm": false, "time_cost_days": 0}, {"action_id": "admin_pay_fines", "description": "Pay outstanding fines for this system.", "display_name": "Pay Fines", "fuel_cost": 0, "parameters": [], "requires_confirm": false, "time_cost_days": 0}, {"action_id": "admin_talk", "description": "Talk to administration personnel.", "display_name": "Talk", "fuel_cost": 0, "parameters": [], "requires_confirm": false, "time_cost_days": 0}, {"action_id": "admin_turn_in", "description": "Turn in outstanding warrants.", "display_name": "Turn In", "fuel_cost": 0, "parameters": [], "requires_confirm": false, "time_cost_days": 0}], "location_id": "SYS-005-DST-02-LOC-administration"}, "stage": "location_actions", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
NPCs:
  1) Administrator (administrator)
Location Actions:
  2) View Mission Board
0) Return to destination
Select option: 0
[v0.11.1][turn 54] action=engine:start change={"command_type": "return_to_destination", "detail": {"command_type": "return_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=engine:location_navigation change={"command_type": "return_to_destination", "detail": {"action": "return_to_destination", "destination_id": "SYS-005-DST-02"}, "stage": "location_navigation", "subsystem": "engine", "turn": 54, "world_seed": 12345}
Returned to destination: SYS-005-DST-02
DESTINATION: Beacon 2 (SYS-005)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 5
0) Back
1) SYS-005-DST-02-LOC-datanet type=datanet
2) SYS-005-DST-02-LOC-market type=market
3) SYS-005-DST-02-LOC-bar type=bar
4) SYS-005-DST-02-LOC-warehouse type=warehouse
5) SYS-005-DST-02-LOC-shipdock type=shipdock
6) SYS-005-DST-02-LOC-administration type=administration
Select location index: 5
[v0.11.1][turn 54] action=engine:start change={"command_type": "enter_location", "detail": {"command_type": "enter_location"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=engine:location_navigation change={"command_type": "enter_location", "detail": {"action": "enter_location", "location_id": "SYS-005-DST-02-LOC-shipdock", "location_type": "shipdock", "resolved_npc_ids": []}, "stage": "location_navigation", "subsystem": "engine", "turn": 54, "world_seed": 12345}
Entered location: SYS-005-DST-02-LOC-shipdock
[v0.11.1][turn 54] action=engine:start change={"command_type": "list_location_actions", "detail": {"command_type": "list_location_actions"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=interaction_layer:location_actions change={"command_type": "list_location_actions", "detail": {"actions": [{"action_id": "buy_hull", "description": "Purchase a hull from shipdock inventory.", "display_name": "Buy Hull", "fuel_cost": 0, "parameters": [{"name": "ship_id", "prompt": "Ship ID to buy the hull for (example: PLAYER-SHIP-001)", "type": "str"}, {"name": "hull_id", "prompt": "Hull ID to purchase (from shipdock inventory)", "type": "str"}], "requires_confirm": false, "time_cost_days": 0}, {"action_id": "buy_module", "description": "Purchase a module for an eligible ship.", "display_name": "Buy Module", "fuel_cost": 0, "parameters": [{"name": "ship_id", "prompt": "Ship ID to install the module on (example: PLAYER-SHIP-001)", "type": "str"}, {"name": "module_id", "prompt": "Module ID to purchase (from shipdock inventory)", "type": "str"}], "requires_confirm": false, "time_cost_days": 0}, {"action_id": "repair_ship", "description": "Restore hull and subsystem degradation at shipdock.", "display_name": "Repair Ship", "fuel_cost": 0, "parameters": [], "requires_confirm": false, "time_cost_days": 0}, {"action_id": "sell_hull", "description": "Sell an owned hull currently present at destination.", "display_name": "Sell Hull", "fuel_cost": 0, "parameters": [{"name": "ship_id", "prompt": "Ship ID (hull) to sell", "type": "str"}], "requires_confirm": true, "time_cost_days": 0}, {"action_id": "sell_module", "description": "Sell a module installed on an eligible ship.", "display_name": "Sell Module", "fuel_cost": 0, "parameters": [{"name": "ship_id", "prompt": "Ship ID with the module to sell (example: PLAYER-SHIP-001)", "type": "str"}, {"name": "module_id", "prompt": "Module ID to sell", "type": "str"}], "requires_confirm": false, "time_cost_days": 0}], "location_id": "SYS-005-DST-02-LOC-shipdock"}, "stage": "location_actions", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
SHIPDOCK: SYS-005-DST-02-LOC-shipdock
1) Buy Hull
2) Buy Module
3) Sell Hull
4) Sell Module
5) Repair Ship
6) Return to Destination
Select action: 1
[v0.11.1][turn 54] action=engine:start change={"command_type": "shipdock_hull_list", "detail": {"command_type": "shipdock_hull_list"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=price_hull_transaction change=hull_id=mil_t5_dragonfly system_id=SYS-005 transaction_type=buy base=420000.00 ws_bias_percent=0 resale_mult=1.00 final=420000.00
[v0.11.1][turn 54] action=price_hull_transaction change=hull_id=frg_t5_scarab system_id=SYS-005 transaction_type=buy base=360000.00 ws_bias_percent=0 resale_mult=1.00 final=360000.00
[v0.11.1][turn 54] action=price_hull_transaction change=hull_id=frg_t3_beetle system_id=SYS-005 transaction_type=buy base=52000.00 ws_bias_percent=0 resale_mult=1.00 final=52000.00
[v0.11.1][turn 54] action=shipdock:shipdock_hull_list change={"command_type": "shipdock_hull_list", "detail": {"destination_id": "SYS-005-DST-02", "rows": [{"display_name": "Dragonfly", "hull_id": "mil_t5_dragonfly", "price": 420000, "tier": 5}, {"display_name": "Scarab", "hull_id": "frg_t5_scarab", "price": 360000, "tier": 5}, {"display_name": "Beetle", "hull_id": "frg_t3_beetle", "price": 52000, "tier": 3}]}, "stage": "shipdock_hull_list", "subsystem": "shipdock", "turn": 54, "world_seed": 12345}
AVAILABLE HULLS:
1) Dragonfly (Tier 5) - 420000 credits
2) Scarab (Tier 5) - 360000 credits
3) Beetle (Tier 3) - 52000 credits
Select hull index (0 to cancel): 0
SHIPDOCK: SYS-005-DST-02-LOC-shipdock
1) Buy Hull
2) Buy Module
3) Sell Hull
4) Sell Module
5) Repair Ship
6) Return to Destination
Select action: 6
[v0.11.1][turn 54] action=engine:start change={"command_type": "return_to_destination", "detail": {"command_type": "return_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=engine:location_navigation change={"command_type": "return_to_destination", "detail": {"action": "return_to_destination", "destination_id": "SYS-005-DST-02"}, "stage": "location_navigation", "subsystem": "engine", "turn": 54, "world_seed": 12345}
Returned to destination: SYS-005-DST-02
DESTINATION: Beacon 2 (SYS-005)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 3
Current system: SYS-005 (Beacon)
1) Inter-system warp
2) Intra-system destination travel
3) Back
Travel mode: 2
1) SYS-005-DST-01 Beacon 1
2) SYS-005-DST-02 Beacon 2
3) SYS-005-DST-03 Beacon 3
4) SYS-005-DST-04 Beacon 4
Select destination index: 4
[v0.11.1][turn 54] action=engine:start change={"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-005-DST-04", "target_system_id": "SYS-005", "travel_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 54, "world_seed": 12345}
[v0.11.1][turn 54] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"current_fuel": 4, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 54, "world_seed": 12345}
[time_engine] action=time_advance_requested change=start_turn=54 days=1 reason=travel:TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route
[time_engine] action=galaxy_tick change=day=55
[time_engine] action=system_tick change=day=55
[time_engine] action=planet_station_tick change=day=55
[time_engine] action=location_tick change=day=55
[time_engine] action=npc_tick change=day=55
[time_engine] action=end_of_day_log change=day=55
Spawn gate cooldown check: system_id=SYS-005 current_day=55 cooldown_until=44 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=55 cooldown_until=44 reason=spawn_gate_roll_failed spawn_gate_roll=0.5994556750245268
[time_engine] action=time_advance_day_completed change=turn=55 hard_stop=None
[v0.11.1][turn 55] action=time_engine:time_advance change={"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 55, "world_seed": 12345}
[v0.11.1][turn 55] action=law_enforcement:law_checkpoint change={"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 55, "world_seed": 12345}
[v0.11.1][turn 55] action=encounter_generator:encounter_gen change={"command_type": "travel_to_destination", "detail": {"encounter_count": 3, "travel_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 55, "world_seed": 12345}
[v0.11.1][turn 55] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route_enc_1", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 55, "world_seed": 12345}
[v0.11.1][turn 55] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route_enc_1", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 55, "world_seed": 12345}
[v0.11.1][turn 55] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 55, "world_seed": 12345}
[v0.11.1][turn 55] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route_enc_2", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 55, "world_seed": 12345}
[v0.11.1][turn 55] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route_enc_2", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 55, "world_seed": 12345}
[v0.11.1][turn 55] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 55, "world_seed": 12345}
[v0.11.1][turn 55] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route_enc_3", "handler_payload": {"npc_outcome": "pursue"}, "next_handler": "pursuit_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 55, "world_seed": 12345}
[v0.11.1][turn 55] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route_enc_3", "resolver_outcome": {"escaped": false, "outcome": "escape_fail", "resolver": "pursuit", "threshold": 0.5}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 55, "world_seed": 12345}
[v0.11.1][turn 55] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route_enc_3", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 55, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-005-DST-04", "target_system_id": "SYS-005", "travel_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 4, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 3, "travel_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route_enc_1", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route_enc_1", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route_enc_2", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route_enc_2", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route_enc_3", "handler_payload": {"npc_outcome": "pursue"}, "next_handler": "pursuit_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route_enc_3", "resolver_outcome": {"escaped": false, "outcome": "escape_fail", "resolver": "pursuit", "threshold": 0.5}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-005:SYS-005-DST-04:54:auto_route_enc_3", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 55, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 8321, "destination_id": "SYS-005-DST-04", "location_id": "SYS-005-DST-04", "system_id": "SYS-005"}, "turn_after": 55, "turn_before": 54, "version": "0.11.1"}
DESTINATION: Beacon 4 (SYS-005)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 5
No locations available.
DESTINATION: Beacon 4 (SYS-005)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 6
[v0.11.1][turn 55] action=engine:start change={"command_type": "quit", "detail": {"command_type": "quit"}, "stage": "start", "subsystem": "engine", "turn": 55, "world_seed": 12345}
[v0.11.1][turn 55] action=engine:command change={"command_type": "quit", "detail": {"quit": true}, "stage": "command", "subsystem": "engine", "turn": 55, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "quit", "error": null, "events": [{"command_type": "quit", "detail": {"command_type": "quit"}, "stage": "start", "subsystem": "engine", "turn": 55, "world_seed": 12345}, {"command_type": "quit", "detail": {"quit": true}, "stage": "command", "subsystem": "engine", "turn": 55, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 8321, "destination_id": "SYS-005-DST-04", "location_id": "SYS-005-DST-04", "system_id": "SYS-005"}, "turn_after": 55, "turn_before": 55, "version": "0.11.1"}
PS D:\GitHub\EmojiSpace>