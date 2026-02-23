PowerShell 7.5.4
PS D:\GitHub\EmojiSpace> python .\src\run_game_engine_cli.py
Seed [12345]:
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
Select location index: 2
Entered location: SYS-001-DST-01-LOC-market
MARKET PROFILE
  System: SYS-001
  Destination: SYS-001-DST-01
  Primary economy: industrial
  Active situations: none
  ENERGY: produced=['high_density_fuel', 'power_cells'] consumed=[] neutral=[]
  MACHINERY: produced=['automated_factories', 'military_hardware'] consumed=[] neutral=[]
  MEDICINE: produced=[] consumed=[] neutral=['designer_drugs', 'field_stimulants']
  METAL: produced=[] consumed=['decorative_metals', 'precision_alloys'] neutral=[]
  ORE: produced=[] consumed=['copper_ore', 'rare_earth_ore'] neutral=[]
  PARTS: produced=['electronic_components', 'mechanical_parts'] consumed=[] neutral=[]
MARKET SKUS
  automated_factories | Automated Factories | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  copper_ore | Copper Ore | buy=156 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  decorative_metals | Decorative Metals | buy=264 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  designer_drugs | Designer Drugs | buy=300 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  electronic_components | Electronic Components | buy=144 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  field_stimulants | Field Stimulants | buy=240 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  high_density_fuel | High-Density Fuel | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  mechanical_parts | Mechanical Parts | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  military_hardware | Military Hardware | buy=269 | sell=-- | cargo=0 | legality=LEGAL | risk=High
  power_cells | Power Cells | buy=144 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  precision_alloys | Precision Alloys | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  rare_earth_ore | Rare Earth Ore | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 1
1) automated_factories Automated Factories price=288 legality=LEGAL risk=Medium
2) copper_ore Copper Ore price=156 legality=LEGAL risk=Medium
3) decorative_metals Decorative Metals price=264 legality=LEGAL risk=Medium
4) designer_drugs Designer Drugs price=300 legality=LEGAL risk=Medium
5) electronic_components Electronic Components price=144 legality=LEGAL risk=Medium
6) field_stimulants Field Stimulants price=240 legality=LEGAL risk=Medium
7) high_density_fuel High-Density Fuel price=160 legality=LEGAL risk=Medium
8) mechanical_parts Mechanical Parts price=128 legality=LEGAL risk=Medium
9) military_hardware Military Hardware price=269 legality=LEGAL risk=High
10) power_cells Power Cells price=144 legality=LEGAL risk=Medium
11) precision_alloys Precision Alloys price=288 legality=LEGAL risk=Medium
12) rare_earth_ore Rare Earth Ore price=216 legality=LEGAL risk=Medium
Select buy sku index: 0
Quantity: 0
Invalid buy index.
MARKET PROFILE
  System: SYS-001
  Destination: SYS-001-DST-01
  Primary economy: industrial
  Active situations: none
  ENERGY: produced=['high_density_fuel', 'power_cells'] consumed=[] neutral=[]
  MACHINERY: produced=['automated_factories', 'military_hardware'] consumed=[] neutral=[]
  MEDICINE: produced=[] consumed=[] neutral=['designer_drugs', 'field_stimulants']
  METAL: produced=[] consumed=['decorative_metals', 'precision_alloys'] neutral=[]
  ORE: produced=[] consumed=['copper_ore', 'rare_earth_ore'] neutral=[]
  PARTS: produced=['electronic_components', 'mechanical_parts'] consumed=[] neutral=[]
MARKET SKUS
  automated_factories | Automated Factories | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  copper_ore | Copper Ore | buy=156 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  decorative_metals | Decorative Metals | buy=264 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  designer_drugs | Designer Drugs | buy=300 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  electronic_components | Electronic Components | buy=144 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  field_stimulants | Field Stimulants | buy=240 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  high_density_fuel | High-Density Fuel | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  mechanical_parts | Mechanical Parts | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  military_hardware | Military Hardware | buy=269 | sell=-- | cargo=0 | legality=LEGAL | risk=High
  power_cells | Power Cells | buy=144 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  precision_alloys | Precision Alloys | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  rare_earth_ore | Rare Earth Ore | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 3
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
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-001-DST-02", "target_system_id": "SYS-001", "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 0, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 55, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 0, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 5, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_0", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_0", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_0ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_2", "handler_payload": {"npc_outcome": "attack"}, "next_handler": "combat_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_2", "resolver_outcome": {"outcome": "destroyed", "resolver": "combat", "rounds": 3, "winner": "enemy"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_3", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_3", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_3", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_4", "handler_payload": {"npc_outcome": "attack"}, "next_handler": "combat_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_4", "resolver_outcome": {"outcome": "destroyed", "resolver": "combat", "rounds": 1, "winner": "enemy"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_4", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_5", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_5", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 4, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_5ignore0", "selected_outcome": "hail", "tr_delta": 3, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:0:auto_route_enc_5", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 1, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 5000, "destination_id": "SYS-001-DST-02", "location_id": "SYS-001-DST-02", "system_id": "SYS-001"}, "turn_after": 1, "turn_before": 0, "version": "0.11.0"}
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
Select location index: 2
Entered location: SYS-001-DST-02-LOC-market
MARKET PROFILE
  System: SYS-001
  Destination: SYS-001-DST-02
  Primary economy: agricultural
  Active situations: none
  CHEMICALS: produced=['industrial_chemicals'] consumed=[] neutral=[]
  ENERGY: produced=[] consumed=['experimental_reactors'] neutral=[]
  FOOD: produced=['luxury_fresh_produce'] consumed=[] neutral=[]
  METAL: produced=[] consumed=['precision_alloys'] neutral=[]
  PARTS: produced=[] consumed=['mechanical_parts'] neutral=[]
MARKET SKUS
  experimental_reactors | Experimental Reactors | buy=504 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  industrial_chemicals | Industrial Chemicals | buy=120 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  luxury_fresh_produce | Luxury Fresh Produce | buy=96 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  mechanical_parts | Mechanical Parts | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  precision_alloys | Precision Alloys | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 1
1) experimental_reactors Experimental Reactors price=504 legality=LEGAL risk=Medium
2) industrial_chemicals Industrial Chemicals price=120 legality=LEGAL risk=Medium
3) luxury_fresh_produce Luxury Fresh Produce price=96 legality=LEGAL risk=Medium
4) mechanical_parts Mechanical Parts price=192 legality=LEGAL risk=Medium
5) precision_alloys Precision Alloys price=288 legality=LEGAL risk=Medium
Select buy sku index: 3
Quantity: 10
{"active_encounter_count": 0, "command_type": "market_buy", "error": null, "events": [{"command_type": "market_buy", "detail": {"command_type": "market_buy"}, "stage": "start", "subsystem": "engine", "turn": 1, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 1, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"action": "buy", "cargo_after": 10, "credits_after": 4040, "credits_before": 5000, "quantity": 10, "sku_id": "luxury_fresh_produce", "total_cost": 960, "unit_price": 96}, "stage": "market_trade", "subsystem": "market", "turn": 1, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 4040, "destination_id": "SYS-001-DST-02", "location_id": "SYS-001-DST-02-LOC-market", "system_id": "SYS-001"}, "turn_after": 1, "turn_before": 1, "version": "0.11.0"}
MARKET PROFILE
  System: SYS-001
  Destination: SYS-001-DST-02
  Primary economy: agricultural
  Active situations: none
  CHEMICALS: produced=['industrial_chemicals'] consumed=[] neutral=[]
  ENERGY: produced=[] consumed=['experimental_reactors'] neutral=[]
  FOOD: produced=['luxury_fresh_produce'] consumed=[] neutral=[]
  METAL: produced=[] consumed=['precision_alloys'] neutral=[]
  PARTS: produced=[] consumed=['mechanical_parts'] neutral=[]
MARKET SKUS
  experimental_reactors | Experimental Reactors | buy=504 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  industrial_chemicals | Industrial Chemicals | buy=120 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  luxury_fresh_produce | Luxury Fresh Produce | buy=96 | sell=96 | cargo=10 | legality=LEGAL | risk=Medium
  mechanical_parts | Mechanical Parts | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  precision_alloys | Precision Alloys | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 3
Returned to destination: SYS-001-DST-02
DESTINATION: Ion 2 (SYS-001)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 1
PLAYER / SHIP INFO
  Credits: 4040
  Fuel: 55/55
  Cargo manifest: {'luxury_fresh_produce': 10}
  Reputation: 50 band=0
  Heat: 0
  Notoriety: 0 band=-2
  Arrest state: free
  Warrants: []
  Location: SYS-001 / SYS-001-DST-02 / SYS-001-DST-02
  Turn: 1
  Active crew: []
  Active missions: []
ONGOING COSTS
  Insurance: 0
  Warehouse rental: 0
  Crew wages: 0
  Total recurring cost: 0
WAREHOUSE RENTALS
  none
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
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-001-DST-03", "target_system_id": "SYS-001", "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 55, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 1, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 4, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_0", "handler_payload": {"npc_outcome": "pursue"}, "next_handler": "pursuit_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_0", "resolver_outcome": {"escaped": false, "outcome": "escape_fail", "resolver": "pursuit", "threshold": 0.5}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_1", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_1", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_1ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [2, 5, 1], "weights_after_notoriety": [2, 5, 1], "weights_after_reputation": [2, 5, 1], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_2", "handler_payload": {"npc_outcome": "pursue"}, "next_handler": "pursuit_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_2", "resolver_outcome": {"escaped": false, "outcome": "escape_fail", "resolver": "pursuit", "threshold": 0.45}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_3", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_3", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:1:auto_route_enc_3", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 2, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 4040, "destination_id": "SYS-001-DST-03", "location_id": "SYS-001-DST-03", "system_id": "SYS-001"}, "turn_after": 2, "turn_before": 1, "version": "0.11.0"}
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
Select location index: 2
Entered location: SYS-001-DST-03-LOC-market
MARKET PROFILE
  System: SYS-001
  Destination: SYS-001-DST-03
  Primary economy: trade
  Active situations: none
  ORE: produced=[] consumed=['rare_earth_ore'] neutral=[]
  PARTS: produced=['mechanical_parts'] consumed=[] neutral=[]
MARKET SKUS
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=-- | cargo=10 | legality=-- | risk=--
  mechanical_parts | Mechanical Parts | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  rare_earth_ore | Rare Earth Ore | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 0
Invalid action index.
MARKET PROFILE
  System: SYS-001
  Destination: SYS-001-DST-03
  Primary economy: trade
  Active situations: none
  ORE: produced=[] consumed=['rare_earth_ore'] neutral=[]
  PARTS: produced=['mechanical_parts'] consumed=[] neutral=[]
MARKET SKUS
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=-- | cargo=10 | legality=-- | risk=--
  mechanical_parts | Mechanical Parts | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  rare_earth_ore | Rare Earth Ore | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 0
Invalid action index.
MARKET PROFILE
  System: SYS-001
  Destination: SYS-001-DST-03
  Primary economy: trade
  Active situations: none
  ORE: produced=[] consumed=['rare_earth_ore'] neutral=[]
  PARTS: produced=['mechanical_parts'] consumed=[] neutral=[]
MARKET SKUS
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=-- | cargo=10 | legality=-- | risk=--
  mechanical_parts | Mechanical Parts | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  rare_earth_ore | Rare Earth Ore | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 3
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
Travel mode: 2
1) SYS-001-DST-01 Ion 1
2) SYS-001-DST-02 Ion 2
3) SYS-001-DST-03 Ion 3
4) SYS-001-DST-04 Ion 4
Select destination index: 4
[time_engine] action=time_advance_requested change=start_turn=2 days=1 reason=travel:TRAVEL-SYS-001:SYS-001:SYS-001-DST-04:2:auto_route
[time_engine] action=galaxy_tick change=day=3
[time_engine] action=system_tick change=day=3
[time_engine] action=planet_station_tick change=day=3
[time_engine] action=location_tick change=day=3
[time_engine] action=npc_tick change=day=3
[time_engine] action=end_of_day_log change=day=3
Spawn gate cooldown check: system_id=SYS-001 current_day=3 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=3 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.3375616037463346
[time_engine] action=time_advance_day_completed change=turn=3 hard_stop=None
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-001-DST-04", "target_system_id": "SYS-001", "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-04:2:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 55, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-04:2:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 2, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-04:2:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 3, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 3, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 3, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-04:2:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 3, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-04:2:auto_route_enc_0", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 3, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-04:2:auto_route_enc_0", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 3, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-04:2:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 3, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-04:2:auto_route_enc_1", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 3, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-04:2:auto_route_enc_1", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-04:2:auto_route_enc_1ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 3, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-04:2:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 3, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-04:2:auto_route_enc_2", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 3, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-04:2:auto_route_enc_2", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-04:2:auto_route_enc_2ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 3, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-04:2:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 3, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 4040, "destination_id": "SYS-001-DST-04", "location_id": "SYS-001-DST-04", "system_id": "SYS-001"}, "turn_after": 3, "turn_before": 2, "version": "0.11.0"}
DESTINATION: Ion 4 (SYS-001)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 5
No locations available.
DESTINATION: Ion 4 (SYS-001)
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
Select target system index: 1
[time_engine] action=time_advance_requested change=start_turn=3 days=10 reason=travel:TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route
[time_engine] action=galaxy_tick change=day=4
[time_engine] action=system_tick change=day=4
[time_engine] action=planet_station_tick change=day=4
[time_engine] action=location_tick change=day=4
[time_engine] action=npc_tick change=day=4
[time_engine] action=end_of_day_log change=day=4
Spawn gate cooldown check: system_id=SYS-004 current_day=4 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=4 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.2613829509113217
[time_engine] action=time_advance_day_completed change=turn=4 hard_stop=None
[time_engine] action=galaxy_tick change=day=5
[time_engine] action=system_tick change=day=5
[time_engine] action=planet_station_tick change=day=5
[time_engine] action=location_tick change=day=5
[time_engine] action=npc_tick change=day=5
[time_engine] action=end_of_day_log change=day=5
Spawn gate cooldown check: system_id=SYS-004 current_day=5 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=5 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.1321242071648071
[time_engine] action=time_advance_day_completed change=turn=5 hard_stop=None
[time_engine] action=galaxy_tick change=day=6
[time_engine] action=system_tick change=day=6
[time_engine] action=planet_station_tick change=day=6
[time_engine] action=location_tick change=day=6
[time_engine] action=npc_tick change=day=6
[time_engine] action=end_of_day_log change=day=6
Spawn gate cooldown check: system_id=SYS-004 current_day=6 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=6 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.4175327193955438
[time_engine] action=time_advance_day_completed change=turn=6 hard_stop=None
[time_engine] action=galaxy_tick change=day=7
[time_engine] action=system_tick change=day=7
[time_engine] action=planet_station_tick change=day=7
[time_engine] action=location_tick change=day=7
[time_engine] action=npc_tick change=day=7
[time_engine] action=end_of_day_log change=day=7
Spawn gate cooldown check: system_id=SYS-004 current_day=7 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=7 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.181627670154202
[time_engine] action=time_advance_day_completed change=turn=7 hard_stop=None
[time_engine] action=galaxy_tick change=day=8
[time_engine] action=system_tick change=day=8
[time_engine] action=planet_station_tick change=day=8
[time_engine] action=location_tick change=day=8
[time_engine] action=npc_tick change=day=8
[time_engine] action=end_of_day_log change=day=8
Spawn gate cooldown check: system_id=SYS-004 current_day=8 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=8 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.94895943515755
[time_engine] action=time_advance_day_completed change=turn=8 hard_stop=None
[time_engine] action=galaxy_tick change=day=9
[time_engine] action=system_tick change=day=9
[time_engine] action=planet_station_tick change=day=9
[time_engine] action=location_tick change=day=9
[time_engine] action=npc_tick change=day=9
[time_engine] action=end_of_day_log change=day=9
Spawn gate cooldown check: system_id=SYS-004 current_day=9 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=9 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.5400588772827739
[time_engine] action=time_advance_day_completed change=turn=9 hard_stop=None
[time_engine] action=galaxy_tick change=day=10
[time_engine] action=system_tick change=day=10
[time_engine] action=planet_station_tick change=day=10
[time_engine] action=location_tick change=day=10
[time_engine] action=npc_tick change=day=10
[time_engine] action=end_of_day_log change=day=10
Spawn gate cooldown check: system_id=SYS-004 current_day=10 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=10 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.13832112399136576
[time_engine] action=time_advance_day_completed change=turn=10 hard_stop=None
[time_engine] action=galaxy_tick change=day=11
[time_engine] action=system_tick change=day=11
[time_engine] action=planet_station_tick change=day=11
[time_engine] action=location_tick change=day=11
[time_engine] action=npc_tick change=day=11
[time_engine] action=end_of_day_log change=day=11
Spawn gate cooldown check: system_id=SYS-004 current_day=11 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=11 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.6169624479483845
[time_engine] action=time_advance_day_completed change=turn=11 hard_stop=None
[time_engine] action=galaxy_tick change=day=12
[time_engine] action=system_tick change=day=12
[time_engine] action=planet_station_tick change=day=12
[time_engine] action=location_tick change=day=12
[time_engine] action=npc_tick change=day=12
[time_engine] action=end_of_day_log change=day=12
Spawn gate cooldown check: system_id=SYS-004 current_day=12 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate type+tier selected: system_id=SYS-004 current_day=12 selected_type=situation selected_tier=1 spawn_type_roll=0.4724878695925818 severity_roll=0.19841800834308987
Spawn gate candidate filter: system_id=SYS-004 selected_type=situation selected_tier=1 candidates_found=1
Situation added: cultural_festival system=SYS-004 scope=destination
Spawn gate cooldown set: system_id=SYS-004 current_day=12 cooldown_until=17 generated_any=true reason=spawn_gate_generation
[time_engine] action=time_advance_day_completed change=turn=12 hard_stop=None
[time_engine] action=galaxy_tick change=day=13
[time_engine] action=system_tick change=day=13
[time_engine] action=planet_station_tick change=day=13
[time_engine] action=location_tick change=day=13
[time_engine] action=npc_tick change=day=13
[time_engine] action=end_of_day_log change=day=13
Spawn gate cooldown check: system_id=SYS-004 current_day=13 cooldown_until=17 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=13 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=13 days=10 reason=travel:TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route
[time_engine] action=galaxy_tick change=day=14
[time_engine] action=system_tick change=day=14
[time_engine] action=planet_station_tick change=day=14
[time_engine] action=location_tick change=day=14
[time_engine] action=npc_tick change=day=14
[time_engine] action=end_of_day_log change=day=14
Spawn gate cooldown check: system_id=SYS-004 current_day=14 cooldown_until=17 skipped=true reason=cooldown_active
Situation expired: cultural_festival system=SYS-004
[time_engine] action=time_advance_day_completed change=turn=14 hard_stop=None
[time_engine] action=galaxy_tick change=day=15
[time_engine] action=system_tick change=day=15
[time_engine] action=planet_station_tick change=day=15
[time_engine] action=location_tick change=day=15
[time_engine] action=npc_tick change=day=15
[time_engine] action=end_of_day_log change=day=15
Spawn gate cooldown check: system_id=SYS-004 current_day=15 cooldown_until=17 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=15 hard_stop=None
[time_engine] action=galaxy_tick change=day=16
[time_engine] action=system_tick change=day=16
[time_engine] action=planet_station_tick change=day=16
[time_engine] action=location_tick change=day=16
[time_engine] action=npc_tick change=day=16
[time_engine] action=end_of_day_log change=day=16
Spawn gate cooldown check: system_id=SYS-004 current_day=16 cooldown_until=17 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=16 hard_stop=None
[time_engine] action=galaxy_tick change=day=17
[time_engine] action=system_tick change=day=17
[time_engine] action=planet_station_tick change=day=17
[time_engine] action=location_tick change=day=17
[time_engine] action=npc_tick change=day=17
[time_engine] action=end_of_day_log change=day=17
Spawn gate cooldown check: system_id=SYS-004 current_day=17 cooldown_until=17 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=17 hard_stop=None
[time_engine] action=galaxy_tick change=day=18
[time_engine] action=system_tick change=day=18
[time_engine] action=planet_station_tick change=day=18
[time_engine] action=location_tick change=day=18
[time_engine] action=npc_tick change=day=18
[time_engine] action=end_of_day_log change=day=18
Spawn gate cooldown check: system_id=SYS-004 current_day=18 cooldown_until=17 skipped=false reason=cooldown_clear
Spawn gate type+tier selected: system_id=SYS-004 current_day=18 selected_type=situation selected_tier=3 spawn_type_roll=0.567800404723371 severity_roll=0.7963200999131197
Spawn gate candidate filter: system_id=SYS-004 selected_type=situation selected_tier=3 candidates_found=8
Situation added: resource_shortage system=SYS-004 scope=system_or_destination
Spawn gate cooldown set: system_id=SYS-004 current_day=18 cooldown_until=23 generated_any=true reason=spawn_gate_generation
[time_engine] action=time_advance_day_completed change=turn=18 hard_stop=None
[time_engine] action=galaxy_tick change=day=19
[time_engine] action=system_tick change=day=19
[time_engine] action=planet_station_tick change=day=19
[time_engine] action=location_tick change=day=19
[time_engine] action=npc_tick change=day=19
[time_engine] action=end_of_day_log change=day=19
Spawn gate cooldown check: system_id=SYS-004 current_day=19 cooldown_until=23 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=19 hard_stop=None
[time_engine] action=galaxy_tick change=day=20
[time_engine] action=system_tick change=day=20
[time_engine] action=planet_station_tick change=day=20
[time_engine] action=location_tick change=day=20
[time_engine] action=npc_tick change=day=20
[time_engine] action=end_of_day_log change=day=20
Spawn gate cooldown check: system_id=SYS-004 current_day=20 cooldown_until=23 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=20 hard_stop=None
[time_engine] action=galaxy_tick change=day=21
[time_engine] action=system_tick change=day=21
[time_engine] action=planet_station_tick change=day=21
[time_engine] action=location_tick change=day=21
[time_engine] action=npc_tick change=day=21
[time_engine] action=end_of_day_log change=day=21
Spawn gate cooldown check: system_id=SYS-004 current_day=21 cooldown_until=23 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=21 hard_stop=None
[time_engine] action=galaxy_tick change=day=22
[time_engine] action=system_tick change=day=22
[time_engine] action=planet_station_tick change=day=22
[time_engine] action=location_tick change=day=22
[time_engine] action=npc_tick change=day=22
[time_engine] action=end_of_day_log change=day=22
Spawn gate cooldown check: system_id=SYS-004 current_day=22 cooldown_until=23 skipped=true reason=cooldown_active
Situation expired: resource_shortage system=SYS-004
[time_engine] action=time_advance_day_completed change=turn=22 hard_stop=None
[time_engine] action=galaxy_tick change=day=23
[time_engine] action=system_tick change=day=23
[time_engine] action=planet_station_tick change=day=23
[time_engine] action=location_tick change=day=23
[time_engine] action=npc_tick change=day=23
[time_engine] action=end_of_day_log change=day=23
Spawn gate cooldown check: system_id=SYS-004 current_day=23 cooldown_until=23 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=23 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=23 days=10 reason=travel:TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route
[time_engine] action=galaxy_tick change=day=24
[time_engine] action=system_tick change=day=24
[time_engine] action=planet_station_tick change=day=24
[time_engine] action=location_tick change=day=24
[time_engine] action=npc_tick change=day=24
[time_engine] action=end_of_day_log change=day=24
Spawn gate cooldown check: system_id=SYS-004 current_day=24 cooldown_until=23 skipped=false reason=cooldown_clear
Spawn gate type+tier selected: system_id=SYS-004 current_day=24 selected_type=event selected_tier=1 spawn_type_roll=0.7189681010738505 severity_roll=0.25101156753543064
Spawn gate candidate filter: system_id=SYS-004 selected_type=event selected_tier=1 candidates_found=6
Event added: major_discovery system=SYS-004
Structural detection: origin_system_id=SYS-004 event_id=major_discovery current_day=24 is_structural=False
Situation added: exploration_craze system=SYS-004 scope=system
Situation added: trade_boom system=SYS-004 scope=system
System flag add: system_id=SYS-004 event_id=major_discovery flag=discovery_hype already_present=False
Spawn gate cooldown set: system_id=SYS-004 current_day=24 cooldown_until=29 generated_any=true reason=spawn_gate_generation
Event expired: major_discovery system=SYS-004
[time_engine] action=time_advance_day_completed change=turn=24 hard_stop=None
[time_engine] action=galaxy_tick change=day=25
[time_engine] action=system_tick change=day=25
[time_engine] action=planet_station_tick change=day=25
[time_engine] action=location_tick change=day=25
[time_engine] action=npc_tick change=day=25
[time_engine] action=end_of_day_log change=day=25
Spawn gate cooldown check: system_id=SYS-004 current_day=25 cooldown_until=29 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=25 hard_stop=None
[time_engine] action=galaxy_tick change=day=26
[time_engine] action=system_tick change=day=26
[time_engine] action=planet_station_tick change=day=26
[time_engine] action=location_tick change=day=26
[time_engine] action=npc_tick change=day=26
[time_engine] action=end_of_day_log change=day=26
Spawn gate cooldown check: system_id=SYS-004 current_day=26 cooldown_until=29 skipped=true reason=cooldown_active
Situation expired: exploration_craze system=SYS-004
[time_engine] action=time_advance_day_completed change=turn=26 hard_stop=None
[time_engine] action=galaxy_tick change=day=27
[time_engine] action=system_tick change=day=27
[time_engine] action=planet_station_tick change=day=27
[time_engine] action=location_tick change=day=27
[time_engine] action=npc_tick change=day=27
[time_engine] action=end_of_day_log change=day=27
Spawn gate cooldown check: system_id=SYS-004 current_day=27 cooldown_until=29 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=27 hard_stop=None
[time_engine] action=galaxy_tick change=day=28
[time_engine] action=system_tick change=day=28
[time_engine] action=planet_station_tick change=day=28
[time_engine] action=location_tick change=day=28
[time_engine] action=npc_tick change=day=28
[time_engine] action=end_of_day_log change=day=28
Spawn gate cooldown check: system_id=SYS-004 current_day=28 cooldown_until=29 skipped=true reason=cooldown_active
Situation expired: trade_boom system=SYS-004
[time_engine] action=time_advance_day_completed change=turn=28 hard_stop=None
[time_engine] action=galaxy_tick change=day=29
[time_engine] action=system_tick change=day=29
[time_engine] action=planet_station_tick change=day=29
[time_engine] action=location_tick change=day=29
[time_engine] action=npc_tick change=day=29
[time_engine] action=end_of_day_log change=day=29
Spawn gate cooldown check: system_id=SYS-004 current_day=29 cooldown_until=29 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=29 hard_stop=None
[time_engine] action=galaxy_tick change=day=30
[time_engine] action=system_tick change=day=30
[time_engine] action=planet_station_tick change=day=30
[time_engine] action=location_tick change=day=30
[time_engine] action=npc_tick change=day=30
[time_engine] action=end_of_day_log change=day=30
Spawn gate cooldown check: system_id=SYS-004 current_day=30 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=30 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.997127517456618
[time_engine] action=time_advance_day_completed change=turn=30 hard_stop=None
[time_engine] action=galaxy_tick change=day=31
[time_engine] action=system_tick change=day=31
[time_engine] action=planet_station_tick change=day=31
[time_engine] action=location_tick change=day=31
[time_engine] action=npc_tick change=day=31
[time_engine] action=end_of_day_log change=day=31
Spawn gate cooldown check: system_id=SYS-004 current_day=31 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=31 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.8247573059718782
[time_engine] action=time_advance_day_completed change=turn=31 hard_stop=None
[time_engine] action=galaxy_tick change=day=32
[time_engine] action=system_tick change=day=32
[time_engine] action=planet_station_tick change=day=32
[time_engine] action=location_tick change=day=32
[time_engine] action=npc_tick change=day=32
[time_engine] action=end_of_day_log change=day=32
Spawn gate cooldown check: system_id=SYS-004 current_day=32 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=32 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.7516887695727709
[time_engine] action=time_advance_day_completed change=turn=32 hard_stop=None
[time_engine] action=galaxy_tick change=day=33
[time_engine] action=system_tick change=day=33
[time_engine] action=planet_station_tick change=day=33
[time_engine] action=location_tick change=day=33
[time_engine] action=npc_tick change=day=33
[time_engine] action=end_of_day_log change=day=33
Spawn gate cooldown check: system_id=SYS-004 current_day=33 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=33 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.1245754687168189
[time_engine] action=time_advance_day_completed change=turn=33 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=33 days=10 reason=travel:TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route
[time_engine] action=galaxy_tick change=day=34
[time_engine] action=system_tick change=day=34
[time_engine] action=planet_station_tick change=day=34
[time_engine] action=location_tick change=day=34
[time_engine] action=npc_tick change=day=34
[time_engine] action=end_of_day_log change=day=34
Spawn gate cooldown check: system_id=SYS-004 current_day=34 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=34 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.47205591721654283
[time_engine] action=time_advance_day_completed change=turn=34 hard_stop=None
[time_engine] action=galaxy_tick change=day=35
[time_engine] action=system_tick change=day=35
[time_engine] action=planet_station_tick change=day=35
[time_engine] action=location_tick change=day=35
[time_engine] action=npc_tick change=day=35
[time_engine] action=end_of_day_log change=day=35
Spawn gate cooldown check: system_id=SYS-004 current_day=35 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=35 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.6110802642192759
[time_engine] action=time_advance_day_completed change=turn=35 hard_stop=None
[time_engine] action=galaxy_tick change=day=36
[time_engine] action=system_tick change=day=36
[time_engine] action=planet_station_tick change=day=36
[time_engine] action=location_tick change=day=36
[time_engine] action=npc_tick change=day=36
[time_engine] action=end_of_day_log change=day=36
Spawn gate cooldown check: system_id=SYS-004 current_day=36 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=36 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.7488380601223873
[time_engine] action=time_advance_day_completed change=turn=36 hard_stop=None
[time_engine] action=galaxy_tick change=day=37
[time_engine] action=system_tick change=day=37
[time_engine] action=planet_station_tick change=day=37
[time_engine] action=location_tick change=day=37
[time_engine] action=npc_tick change=day=37
[time_engine] action=end_of_day_log change=day=37
Spawn gate cooldown check: system_id=SYS-004 current_day=37 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=37 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.5078854331094379
[time_engine] action=time_advance_day_completed change=turn=37 hard_stop=None
[time_engine] action=galaxy_tick change=day=38
[time_engine] action=system_tick change=day=38
[time_engine] action=planet_station_tick change=day=38
[time_engine] action=location_tick change=day=38
[time_engine] action=npc_tick change=day=38
[time_engine] action=end_of_day_log change=day=38
Spawn gate cooldown check: system_id=SYS-004 current_day=38 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=38 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.8966927572853776
[time_engine] action=time_advance_day_completed change=turn=38 hard_stop=None
[time_engine] action=galaxy_tick change=day=39
[time_engine] action=system_tick change=day=39
[time_engine] action=planet_station_tick change=day=39
[time_engine] action=location_tick change=day=39
[time_engine] action=npc_tick change=day=39
[time_engine] action=end_of_day_log change=day=39
Spawn gate cooldown check: system_id=SYS-004 current_day=39 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=39 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.3933979004934185
[time_engine] action=time_advance_day_completed change=turn=39 hard_stop=None
[time_engine] action=galaxy_tick change=day=40
[time_engine] action=system_tick change=day=40
[time_engine] action=planet_station_tick change=day=40
[time_engine] action=location_tick change=day=40
[time_engine] action=npc_tick change=day=40
[time_engine] action=end_of_day_log change=day=40
Spawn gate cooldown check: system_id=SYS-004 current_day=40 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate type+tier selected: system_id=SYS-004 current_day=40 selected_type=situation selected_tier=5 spawn_type_roll=0.482967348530709 severity_roll=0.9542004405222188
Spawn gate candidate filter: system_id=SYS-004 selected_type=situation selected_tier=5 candidates_found=0
Spawn gate cooldown not set: system_id=SYS-004 current_day=40 cooldown_until=29 reason=no_generation_created selected_type=situation selected_tier=5 candidates_found=0
[time_engine] action=time_advance_day_completed change=turn=40 hard_stop=None
[time_engine] action=galaxy_tick change=day=41
[time_engine] action=system_tick change=day=41
[time_engine] action=planet_station_tick change=day=41
[time_engine] action=location_tick change=day=41
[time_engine] action=npc_tick change=day=41
[time_engine] action=end_of_day_log change=day=41
Spawn gate cooldown check: system_id=SYS-004 current_day=41 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=41 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.515714392748662
[time_engine] action=time_advance_day_completed change=turn=41 hard_stop=None
[time_engine] action=galaxy_tick change=day=42
[time_engine] action=system_tick change=day=42
[time_engine] action=planet_station_tick change=day=42
[time_engine] action=location_tick change=day=42
[time_engine] action=npc_tick change=day=42
[time_engine] action=end_of_day_log change=day=42
Spawn gate cooldown check: system_id=SYS-004 current_day=42 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=42 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.6866199355548026
[time_engine] action=time_advance_day_completed change=turn=42 hard_stop=None
[time_engine] action=galaxy_tick change=day=43
[time_engine] action=system_tick change=day=43
[time_engine] action=planet_station_tick change=day=43
[time_engine] action=location_tick change=day=43
[time_engine] action=npc_tick change=day=43
[time_engine] action=end_of_day_log change=day=43
Spawn gate cooldown check: system_id=SYS-004 current_day=43 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=43 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.5513954715383288
[time_engine] action=time_advance_day_completed change=turn=43 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=43 days=10 reason=travel:TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route
[time_engine] action=galaxy_tick change=day=44
[time_engine] action=system_tick change=day=44
[time_engine] action=planet_station_tick change=day=44
[time_engine] action=location_tick change=day=44
[time_engine] action=npc_tick change=day=44
[time_engine] action=end_of_day_log change=day=44
Spawn gate cooldown check: system_id=SYS-004 current_day=44 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=44 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.18135946002447856
[time_engine] action=time_advance_day_completed change=turn=44 hard_stop=None
[time_engine] action=galaxy_tick change=day=45
[time_engine] action=system_tick change=day=45
[time_engine] action=planet_station_tick change=day=45
[time_engine] action=location_tick change=day=45
[time_engine] action=npc_tick change=day=45
[time_engine] action=end_of_day_log change=day=45
Spawn gate cooldown check: system_id=SYS-004 current_day=45 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=45 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.12398459320531074
[time_engine] action=time_advance_day_completed change=turn=45 hard_stop=None
[time_engine] action=galaxy_tick change=day=46
[time_engine] action=system_tick change=day=46
[time_engine] action=planet_station_tick change=day=46
[time_engine] action=location_tick change=day=46
[time_engine] action=npc_tick change=day=46
[time_engine] action=end_of_day_log change=day=46
Spawn gate cooldown check: system_id=SYS-004 current_day=46 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=46 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.49757891271576216
[time_engine] action=time_advance_day_completed change=turn=46 hard_stop=None
[time_engine] action=galaxy_tick change=day=47
[time_engine] action=system_tick change=day=47
[time_engine] action=planet_station_tick change=day=47
[time_engine] action=location_tick change=day=47
[time_engine] action=npc_tick change=day=47
[time_engine] action=end_of_day_log change=day=47
Spawn gate cooldown check: system_id=SYS-004 current_day=47 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=47 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.7289634939749933
[time_engine] action=time_advance_day_completed change=turn=47 hard_stop=None
[time_engine] action=galaxy_tick change=day=48
[time_engine] action=system_tick change=day=48
[time_engine] action=planet_station_tick change=day=48
[time_engine] action=location_tick change=day=48
[time_engine] action=npc_tick change=day=48
[time_engine] action=end_of_day_log change=day=48
Spawn gate cooldown check: system_id=SYS-004 current_day=48 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=48 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.6334079620636524
[time_engine] action=time_advance_day_completed change=turn=48 hard_stop=None
[time_engine] action=galaxy_tick change=day=49
[time_engine] action=system_tick change=day=49
[time_engine] action=planet_station_tick change=day=49
[time_engine] action=location_tick change=day=49
[time_engine] action=npc_tick change=day=49
[time_engine] action=end_of_day_log change=day=49
Spawn gate cooldown check: system_id=SYS-004 current_day=49 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=49 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.847665742078646
[time_engine] action=time_advance_day_completed change=turn=49 hard_stop=None
[time_engine] action=galaxy_tick change=day=50
[time_engine] action=system_tick change=day=50
[time_engine] action=planet_station_tick change=day=50
[time_engine] action=location_tick change=day=50
[time_engine] action=npc_tick change=day=50
[time_engine] action=end_of_day_log change=day=50
Spawn gate cooldown check: system_id=SYS-004 current_day=50 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=50 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.5675196323158965
[time_engine] action=time_advance_day_completed change=turn=50 hard_stop=None
[time_engine] action=galaxy_tick change=day=51
[time_engine] action=system_tick change=day=51
[time_engine] action=planet_station_tick change=day=51
[time_engine] action=location_tick change=day=51
[time_engine] action=npc_tick change=day=51
[time_engine] action=end_of_day_log change=day=51
Spawn gate cooldown check: system_id=SYS-004 current_day=51 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=51 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.39877124945863207
[time_engine] action=time_advance_day_completed change=turn=51 hard_stop=None
[time_engine] action=galaxy_tick change=day=52
[time_engine] action=system_tick change=day=52
[time_engine] action=planet_station_tick change=day=52
[time_engine] action=location_tick change=day=52
[time_engine] action=npc_tick change=day=52
[time_engine] action=end_of_day_log change=day=52
Spawn gate cooldown check: system_id=SYS-004 current_day=52 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=52 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.7286833955240793
[time_engine] action=time_advance_day_completed change=turn=52 hard_stop=None
[time_engine] action=galaxy_tick change=day=53
[time_engine] action=system_tick change=day=53
[time_engine] action=planet_station_tick change=day=53
[time_engine] action=location_tick change=day=53
[time_engine] action=npc_tick change=day=53
[time_engine] action=end_of_day_log change=day=53
Spawn gate cooldown check: system_id=SYS-004 current_day=53 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=53 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.3346780127178115
[time_engine] action=time_advance_day_completed change=turn=53 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=53 days=2 reason=travel:TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route
[time_engine] action=galaxy_tick change=day=54
[time_engine] action=system_tick change=day=54
[time_engine] action=planet_station_tick change=day=54
[time_engine] action=location_tick change=day=54
[time_engine] action=npc_tick change=day=54
[time_engine] action=end_of_day_log change=day=54
Spawn gate cooldown check: system_id=SYS-004 current_day=54 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate type+tier selected: system_id=SYS-004 current_day=54 selected_type=situation selected_tier=2 spawn_type_roll=0.021288737529113533 severity_roll=0.34046993635054534
Spawn gate candidate filter: system_id=SYS-004 selected_type=situation selected_tier=2 candidates_found=12
Situation added: trade_boom system=SYS-004 scope=system
Spawn gate cooldown set: system_id=SYS-004 current_day=54 cooldown_until=59 generated_any=true reason=spawn_gate_generation
[time_engine] action=time_advance_day_completed change=turn=54 hard_stop=None
[time_engine] action=galaxy_tick change=day=55
[time_engine] action=system_tick change=day=55
[time_engine] action=planet_station_tick change=day=55
[time_engine] action=location_tick change=day=55
[time_engine] action=npc_tick change=day=55
[time_engine] action=end_of_day_log change=day=55
Spawn gate cooldown check: system_id=SYS-004 current_day=55 cooldown_until=59 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=55 hard_stop=None
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 3, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 51.84375710593287, "distance_ly_ceiled": 52, "inter_system": true, "target_destination_id": "SYS-004-DST-01", "target_system_id": "SYS-004", "travel_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 3, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 3, "fuel_capacity": 55, "fuel_cost": 52, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 3, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 52, "days_requested": 52, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 4, "travel_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route_enc_0", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route_enc_0", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route_enc_0ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route_enc_1", "handler_payload": {"npc_outcome": "attack"}, "next_handler": "combat_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route_enc_1", "resolver_outcome": {"outcome": "max_rounds", "resolver": "combat", "rounds": 3, "winner": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route_enc_3", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route_enc_3", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route_enc_3ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route_enc_3", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route_enc_7", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route_enc_7", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": ["attack_plus_one_high_tr_delta"], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route_enc_7ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [2, 5, 2], "weights_after_notoriety": [2, 5, 2], "weights_after_reputation": [2, 5, 2], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:3:auto_route_enc_7", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 55, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 4040, "destination_id": "SYS-004-DST-01", "location_id": "SYS-004-DST-01", "system_id": "SYS-004"}, "turn_after": 55, "turn_before": 3, "version": "0.11.0"}
You have arrived in Flux.
Intra-system destinations:
  1) SYS-004-DST-01 Flux 1
  2) SYS-004-DST-02 Flux 2
  3) SYS-004-DST-03 Flux 3
  4) SYS-004-DST-04 Flux 4
DESTINATION: Flux 1 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 5
0) Back
1) SYS-004-DST-01-LOC-datanet type=datanet
2) SYS-004-DST-01-LOC-market type=market
3) SYS-004-DST-01-LOC-warehouse type=warehouse
Select location index: 2
Entered location: SYS-004-DST-01-LOC-market
MARKET PROFILE
  System: SYS-004
  Destination: SYS-004-DST-01
  Primary economy: research
  Active situations: ['trade_boom']
  CHEMICALS: produced=[] consumed=['experimental_serums', 'medical_compounds'] neutral=[]
  DATA: produced=['media_packages', 'propaganda_feeds'] consumed=[] neutral=['ai_training_sets', 'encrypted_records']
  ENERGY: produced=['fusion_cores', 'standard_fuel'] consumed=[] neutral=[]
  MEDICINE: produced=['gene_therapy_kits', 'medical_nanites'] consumed=[] neutral=[]
  PARTS: produced=[] consumed=['cybernetic_implants', 'weaponized_autonomous_robots'] neutral=[]
MARKET SKUS
  ai_training_sets | AI Training Sets | buy=304 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_implants | Cybernetic Implants | buy=395 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  encrypted_records | Encrypted Records | buy=202 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_serums | Experimental Serums | buy=319 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fusion_cores | Fusion Cores | buy=344 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=324 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=-- | cargo=10 | legality=-- | risk=--
  media_packages | Media Packages | buy=162 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_compounds | Medical Compounds | buy=273 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=364 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  propaganda_feeds | Propaganda Feeds | buy=164 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=152 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 3
Returned to destination: SYS-004-DST-01
DESTINATION: Flux 1 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 3
Current system: SYS-004 (Flux)
1) Inter-system warp
2) Intra-system destination travel
3) Back
Travel mode: 2
1) SYS-004-DST-01 Flux 1
2) SYS-004-DST-02 Flux 2
3) SYS-004-DST-03 Flux 3
4) SYS-004-DST-04 Flux 4
Select destination index: 2
[time_engine] action=time_advance_requested change=start_turn=55 days=1 reason=travel:TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:55:auto_route
[time_engine] action=galaxy_tick change=day=56
[time_engine] action=system_tick change=day=56
[time_engine] action=planet_station_tick change=day=56
[time_engine] action=location_tick change=day=56
[time_engine] action=npc_tick change=day=56
[time_engine] action=end_of_day_log change=day=56
Spawn gate cooldown check: system_id=SYS-004 current_day=56 cooldown_until=59 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=56 hard_stop=None
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-004-DST-02", "target_system_id": "SYS-004", "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:55:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 3, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:55:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 55, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:55:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 56, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 56, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 3, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:55:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 56, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:55:auto_route_enc_2", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 56, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:55:auto_route_enc_2", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:55:auto_route_enc_2ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 56, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:55:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 56, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:55:auto_route_enc_3", "handler_payload": {"npc_outcome": "pursue"}, "next_handler": "pursuit_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 56, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:55:auto_route_enc_3", "resolver_outcome": {"escaped": false, "outcome": "escape_fail", "resolver": "pursuit", "threshold": 0.55}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 56, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:55:auto_route_enc_3", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 56, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:55:auto_route_enc_6", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 56, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:55:auto_route_enc_6", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:55:auto_route_enc_6ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 56, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:55:auto_route_enc_6", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 56, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 4040, "destination_id": "SYS-004-DST-02", "location_id": "SYS-004-DST-02", "system_id": "SYS-004"}, "turn_after": 56, "turn_before": 55, "version": "0.11.0"}
DESTINATION: Flux 2 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 5
0) Back
1) SYS-004-DST-02-LOC-datanet type=datanet
2) SYS-004-DST-02-LOC-market type=market
3) SYS-004-DST-02-LOC-warehouse type=warehouse
4) SYS-004-DST-02-LOC-shipdock type=shipdock
5) SYS-004-DST-02-LOC-administration type=administration
Select location index: 2
Entered location: SYS-004-DST-02-LOC-market
MARKET PROFILE
  System: SYS-004
  Destination: SYS-004-DST-02
  Primary economy: military
  Active situations: ['trade_boom']
  ENERGY: produced=[] consumed=['experimental_reactors', 'high_density_fuel', 'power_cells', 'standard_fuel'] neutral=[]
  FOOD: produced=[] consumed=['fresh_produce', 'nutrient_paste', 'protein_blocks', 'spice_wine'] neutral=['basic_rations', 'heritage_cuisine']
  MACHINERY: produced=['automated_factories', 'industrial_machinery', 'military_hardware', 'mining_equipment'] consumed=[] neutral=[]
  MEDICINE: produced=[] consumed=['cybernetic_medical_nanites', 'designer_drugs', 'gene_therapy_kits', 'medical_nanites'] neutral=[]
  METAL: produced=['aluminum_alloy', 'decorative_metals', 'steel_ingots', 'titanium_bars'] consumed=['precision_alloys'] neutral=[]
  ORE: produced=['copper_ore', 'nickel_ore', 'radioactive_ore', 'rare_earth_ore'] consumed=[] neutral=[]
  PARTS: produced=[] consumed=['autonomous_robots', 'servitor_units', 'synthetic_intelligences', 'weaponized_autonomous_robots'] neutral=['cybernetic_implants', 'electronic_components', 'mechanical_parts', 'weaponized_synthetic_intelligences']
  WEAPONS: produced=['biological_weapons', 'experimental_weapons', 'heavy_weapons', 'small_arms'] consumed=[] neutral=[]
MARKET SKUS
  aluminum_alloy | Aluminum Alloy | buy=172 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  automated_factories | Automated Factories | buy=364 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  autonomous_robots | Autonomous Robots | buy=380 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_rations | Basic Rations | buy=126 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  biological_weapons | Biological Weapons | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  copper_ore | Copper Ore | buy=132 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_implants | Cybernetic Implants | buy=329 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_medical_nanites | Cybernetic Medical Nanites | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  decorative_metals | Decorative Metals | buy=134 | sell=-- | cargo=0 | legality=RESTRICTED | risk=Severe
  designer_drugs | Designer Drugs | buy=455 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  electronic_components | Electronic Components | buy=228 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_reactors | Experimental Reactors | buy=638 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_weapons | Experimental Weapons | buy=474 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fresh_produce | Fresh Produce | buy=152 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=486 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heavy_weapons | Heavy Weapons | buy=389 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heritage_cuisine | Heritage Cuisine | buy=228 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  high_density_fuel | High-Density Fuel | buy=213 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  industrial_machinery | Industrial Machinery | buy=263 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=91 | cargo=10 | legality=RESTRICTED | risk=Severe
  mechanical_parts | Mechanical Parts | buy=202 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  military_hardware | Military Hardware | buy=510 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  mining_equipment | Mining Equipment | buy=283 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nickel_ore | Nickel Ore | buy=142 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nutrient_paste | Nutrient Paste | buy=139 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  power_cells | Power Cells | buy=273 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  precision_alloys | Precision Alloys | buy=243 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  protein_blocks | Protein Blocks | buy=177 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  radioactive_ore | Radioactive Ore | buy=156 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  rare_earth_ore | Rare Earth Ore | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  servitor_units | Servitor Units | buy=278 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  small_arms | Small Arms | buy=267 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  spice_wine | Spice Wine | buy=202 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=228 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  steel_ingots | Steel Ingots | buy=162 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  synthetic_intelligences | Synthetic Intelligences | buy=531 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  titanium_bars | Titanium Bars | buy=213 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=455 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_synthetic_intelligences | Weaponized Synthetic Intelligences | buy=638 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 1
1) aluminum_alloy Aluminum Alloy price=172 legality=LEGAL risk=Severe
2) automated_factories Automated Factories price=364 legality=LEGAL risk=Severe
3) autonomous_robots Autonomous Robots price=380 legality=LEGAL risk=Severe
4) basic_rations Basic Rations price=126 legality=LEGAL risk=Severe
5) biological_weapons Biological Weapons price=546 legality=LEGAL risk=Severe
6) copper_ore Copper Ore price=132 legality=LEGAL risk=Severe
7) cybernetic_implants Cybernetic Implants price=329 legality=LEGAL risk=Severe
8) cybernetic_medical_nanites Cybernetic Medical Nanites price=546 legality=LEGAL risk=Severe
9) decorative_metals Decorative Metals price=134 legality=RESTRICTED risk=Severe
10) designer_drugs Designer Drugs price=455 legality=LEGAL risk=Severe
11) electronic_components Electronic Components price=228 legality=LEGAL risk=Severe
12) experimental_reactors Experimental Reactors price=638 legality=LEGAL risk=Severe
13) experimental_weapons Experimental Weapons price=474 legality=LEGAL risk=Severe
14) fresh_produce Fresh Produce price=152 legality=LEGAL risk=Severe
15) gene_therapy_kits Gene Therapy Kits price=486 legality=LEGAL risk=Severe
16) heavy_weapons Heavy Weapons price=389 legality=LEGAL risk=Severe
17) heritage_cuisine Heritage Cuisine price=228 legality=LEGAL risk=Severe
18) high_density_fuel High-Density Fuel price=213 legality=LEGAL risk=Severe
19) industrial_machinery Industrial Machinery price=263 legality=LEGAL risk=Severe
20) mechanical_parts Mechanical Parts price=202 legality=LEGAL risk=Severe
21) medical_nanites Medical Nanites price=546 legality=LEGAL risk=Severe
22) military_hardware Military Hardware price=510 legality=LEGAL risk=Severe
23) mining_equipment Mining Equipment price=283 legality=LEGAL risk=Severe
24) nickel_ore Nickel Ore price=142 legality=LEGAL risk=Severe
25) nutrient_paste Nutrient Paste price=139 legality=LEGAL risk=Severe
26) power_cells Power Cells price=273 legality=LEGAL risk=Severe
27) precision_alloys Precision Alloys price=243 legality=LEGAL risk=Severe
28) protein_blocks Protein Blocks price=177 legality=LEGAL risk=Severe
29) radioactive_ore Radioactive Ore price=156 legality=LEGAL risk=Severe
30) rare_earth_ore Rare Earth Ore price=128 legality=LEGAL risk=Severe
31) servitor_units Servitor Units price=278 legality=LEGAL risk=Severe
32) small_arms Small Arms price=267 legality=LEGAL risk=Severe
33) spice_wine Spice Wine price=202 legality=LEGAL risk=Severe
34) standard_fuel Standard Fuel price=228 legality=LEGAL risk=Severe
35) steel_ingots Steel Ingots price=162 legality=LEGAL risk=Severe
36) synthetic_intelligences Synthetic Intelligences price=531 legality=LEGAL risk=Severe
37) titanium_bars Titanium Bars price=213 legality=LEGAL risk=Severe
38) weaponized_autonomous_robots Weaponized Autonomous Robots price=455 legality=LEGAL risk=Severe
39) weaponized_synthetic_intelligences Weaponized Synthetic Intelligences price=638 legality=LEGAL risk=Severe
Select buy sku index: 4
Quantity: 10
{"active_encounter_count": 0, "command_type": "market_buy", "error": null, "events": [{"command_type": "market_buy", "detail": {"command_type": "market_buy"}, "stage": "start", "subsystem": "engine", "turn": 56, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 56, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"action": "buy", "cargo_after": 10, "credits_after": 2780, "credits_before": 4040, "quantity": 10, "sku_id": "basic_rations", "total_cost": 1260, "unit_price": 126}, "stage": "market_trade", "subsystem": "market", "turn": 56, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 2780, "destination_id": "SYS-004-DST-02", "location_id": "SYS-004-DST-02-LOC-market", "system_id": "SYS-004"}, "turn_after": 56, "turn_before": 56, "version": "0.11.0"}
MARKET PROFILE
  System: SYS-004
  Destination: SYS-004-DST-02
  Primary economy: military
  Active situations: ['trade_boom']
  ENERGY: produced=[] consumed=['experimental_reactors', 'high_density_fuel', 'power_cells', 'standard_fuel'] neutral=[]
  FOOD: produced=[] consumed=['fresh_produce', 'nutrient_paste', 'protein_blocks', 'spice_wine'] neutral=['basic_rations', 'heritage_cuisine']
  MACHINERY: produced=['automated_factories', 'industrial_machinery', 'military_hardware', 'mining_equipment'] consumed=[] neutral=[]
  MEDICINE: produced=[] consumed=['cybernetic_medical_nanites', 'designer_drugs', 'gene_therapy_kits', 'medical_nanites'] neutral=[]
  METAL: produced=['aluminum_alloy', 'decorative_metals', 'steel_ingots', 'titanium_bars'] consumed=['precision_alloys'] neutral=[]
  ORE: produced=['copper_ore', 'nickel_ore', 'radioactive_ore', 'rare_earth_ore'] consumed=[] neutral=[]
  PARTS: produced=[] consumed=['autonomous_robots', 'servitor_units', 'synthetic_intelligences', 'weaponized_autonomous_robots'] neutral=['cybernetic_implants', 'electronic_components', 'mechanical_parts', 'weaponized_synthetic_intelligences']
  WEAPONS: produced=['biological_weapons', 'experimental_weapons', 'heavy_weapons', 'small_arms'] consumed=[] neutral=[]
MARKET SKUS
  aluminum_alloy | Aluminum Alloy | buy=172 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  automated_factories | Automated Factories | buy=364 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  autonomous_robots | Autonomous Robots | buy=380 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_rations | Basic Rations | buy=126 | sell=126 | cargo=10 | legality=LEGAL | risk=Severe
  biological_weapons | Biological Weapons | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  copper_ore | Copper Ore | buy=132 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_implants | Cybernetic Implants | buy=329 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_medical_nanites | Cybernetic Medical Nanites | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  decorative_metals | Decorative Metals | buy=134 | sell=-- | cargo=0 | legality=RESTRICTED | risk=Severe
  designer_drugs | Designer Drugs | buy=455 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  electronic_components | Electronic Components | buy=228 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_reactors | Experimental Reactors | buy=638 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_weapons | Experimental Weapons | buy=474 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fresh_produce | Fresh Produce | buy=152 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=486 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heavy_weapons | Heavy Weapons | buy=389 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heritage_cuisine | Heritage Cuisine | buy=228 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  high_density_fuel | High-Density Fuel | buy=213 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  industrial_machinery | Industrial Machinery | buy=263 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=91 | cargo=10 | legality=RESTRICTED | risk=Severe
  mechanical_parts | Mechanical Parts | buy=202 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  military_hardware | Military Hardware | buy=510 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  mining_equipment | Mining Equipment | buy=283 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nickel_ore | Nickel Ore | buy=142 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nutrient_paste | Nutrient Paste | buy=139 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  power_cells | Power Cells | buy=273 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  precision_alloys | Precision Alloys | buy=243 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  protein_blocks | Protein Blocks | buy=177 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  radioactive_ore | Radioactive Ore | buy=156 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  rare_earth_ore | Rare Earth Ore | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  servitor_units | Servitor Units | buy=278 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  small_arms | Small Arms | buy=267 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  spice_wine | Spice Wine | buy=202 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=228 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  steel_ingots | Steel Ingots | buy=162 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  synthetic_intelligences | Synthetic Intelligences | buy=531 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  titanium_bars | Titanium Bars | buy=213 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=455 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_synthetic_intelligences | Weaponized Synthetic Intelligences | buy=638 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 1
1) aluminum_alloy Aluminum Alloy price=172 legality=LEGAL risk=Severe
2) automated_factories Automated Factories price=364 legality=LEGAL risk=Severe
3) autonomous_robots Autonomous Robots price=380 legality=LEGAL risk=Severe
4) basic_rations Basic Rations price=126 legality=LEGAL risk=Severe
5) biological_weapons Biological Weapons price=546 legality=LEGAL risk=Severe
6) copper_ore Copper Ore price=132 legality=LEGAL risk=Severe
7) cybernetic_implants Cybernetic Implants price=329 legality=LEGAL risk=Severe
8) cybernetic_medical_nanites Cybernetic Medical Nanites price=546 legality=LEGAL risk=Severe
9) decorative_metals Decorative Metals price=134 legality=RESTRICTED risk=Severe
10) designer_drugs Designer Drugs price=455 legality=LEGAL risk=Severe
11) electronic_components Electronic Components price=228 legality=LEGAL risk=Severe
12) experimental_reactors Experimental Reactors price=638 legality=LEGAL risk=Severe
13) experimental_weapons Experimental Weapons price=474 legality=LEGAL risk=Severe
14) fresh_produce Fresh Produce price=152 legality=LEGAL risk=Severe
15) gene_therapy_kits Gene Therapy Kits price=486 legality=LEGAL risk=Severe
16) heavy_weapons Heavy Weapons price=389 legality=LEGAL risk=Severe
17) heritage_cuisine Heritage Cuisine price=228 legality=LEGAL risk=Severe
18) high_density_fuel High-Density Fuel price=213 legality=LEGAL risk=Severe
19) industrial_machinery Industrial Machinery price=263 legality=LEGAL risk=Severe
20) mechanical_parts Mechanical Parts price=202 legality=LEGAL risk=Severe
21) medical_nanites Medical Nanites price=546 legality=LEGAL risk=Severe
22) military_hardware Military Hardware price=510 legality=LEGAL risk=Severe
23) mining_equipment Mining Equipment price=283 legality=LEGAL risk=Severe
24) nickel_ore Nickel Ore price=142 legality=LEGAL risk=Severe
25) nutrient_paste Nutrient Paste price=139 legality=LEGAL risk=Severe
26) power_cells Power Cells price=273 legality=LEGAL risk=Severe
27) precision_alloys Precision Alloys price=243 legality=LEGAL risk=Severe
28) protein_blocks Protein Blocks price=177 legality=LEGAL risk=Severe
29) radioactive_ore Radioactive Ore price=156 legality=LEGAL risk=Severe
30) rare_earth_ore Rare Earth Ore price=128 legality=LEGAL risk=Severe
31) servitor_units Servitor Units price=278 legality=LEGAL risk=Severe
32) small_arms Small Arms price=267 legality=LEGAL risk=Severe
33) spice_wine Spice Wine price=202 legality=LEGAL risk=Severe
34) standard_fuel Standard Fuel price=228 legality=LEGAL risk=Severe
35) steel_ingots Steel Ingots price=162 legality=LEGAL risk=Severe
36) synthetic_intelligences Synthetic Intelligences price=531 legality=LEGAL risk=Severe
37) titanium_bars Titanium Bars price=213 legality=LEGAL risk=Severe
38) weaponized_autonomous_robots Weaponized Autonomous Robots price=455 legality=LEGAL risk=Severe
39) weaponized_synthetic_intelligences Weaponized Synthetic Intelligences price=638 legality=LEGAL risk=Severe
Select buy sku index: 14
Quantity: 5
{"active_encounter_count": 0, "command_type": "market_buy", "error": null, "events": [{"command_type": "market_buy", "detail": {"command_type": "market_buy"}, "stage": "start", "subsystem": "engine", "turn": 56, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 56, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"action": "buy", "cargo_after": 5, "credits_after": 2020, "credits_before": 2780, "quantity": 5, "sku_id": "fresh_produce", "total_cost": 760, "unit_price": 152}, "stage": "market_trade", "subsystem": "market", "turn": 56, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 2020, "destination_id": "SYS-004-DST-02", "location_id": "SYS-004-DST-02-LOC-market", "system_id": "SYS-004"}, "turn_after": 56, "turn_before": 56, "version": "0.11.0"}
MARKET PROFILE
  System: SYS-004
  Destination: SYS-004-DST-02
  Primary economy: military
  Active situations: ['trade_boom']
  ENERGY: produced=[] consumed=['experimental_reactors', 'high_density_fuel', 'power_cells', 'standard_fuel'] neutral=[]
  FOOD: produced=[] consumed=['fresh_produce', 'nutrient_paste', 'protein_blocks', 'spice_wine'] neutral=['basic_rations', 'heritage_cuisine']
  MACHINERY: produced=['automated_factories', 'industrial_machinery', 'military_hardware', 'mining_equipment'] consumed=[] neutral=[]
  MEDICINE: produced=[] consumed=['cybernetic_medical_nanites', 'designer_drugs', 'gene_therapy_kits', 'medical_nanites'] neutral=[]
  METAL: produced=['aluminum_alloy', 'decorative_metals', 'steel_ingots', 'titanium_bars'] consumed=['precision_alloys'] neutral=[]
  ORE: produced=['copper_ore', 'nickel_ore', 'radioactive_ore', 'rare_earth_ore'] consumed=[] neutral=[]
  PARTS: produced=[] consumed=['autonomous_robots', 'servitor_units', 'synthetic_intelligences', 'weaponized_autonomous_robots'] neutral=['cybernetic_implants', 'electronic_components', 'mechanical_parts', 'weaponized_synthetic_intelligences']
  WEAPONS: produced=['biological_weapons', 'experimental_weapons', 'heavy_weapons', 'small_arms'] consumed=[] neutral=[]
MARKET SKUS
  aluminum_alloy | Aluminum Alloy | buy=172 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  automated_factories | Automated Factories | buy=364 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  autonomous_robots | Autonomous Robots | buy=380 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_rations | Basic Rations | buy=126 | sell=126 | cargo=10 | legality=LEGAL | risk=Severe
  biological_weapons | Biological Weapons | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  copper_ore | Copper Ore | buy=132 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_implants | Cybernetic Implants | buy=329 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_medical_nanites | Cybernetic Medical Nanites | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  decorative_metals | Decorative Metals | buy=134 | sell=-- | cargo=0 | legality=RESTRICTED | risk=Severe
  designer_drugs | Designer Drugs | buy=455 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  electronic_components | Electronic Components | buy=228 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_reactors | Experimental Reactors | buy=638 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_weapons | Experimental Weapons | buy=474 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fresh_produce | Fresh Produce | buy=152 | sell=152 | cargo=5 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=486 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heavy_weapons | Heavy Weapons | buy=389 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heritage_cuisine | Heritage Cuisine | buy=228 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  high_density_fuel | High-Density Fuel | buy=213 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  industrial_machinery | Industrial Machinery | buy=263 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=91 | cargo=10 | legality=RESTRICTED | risk=Severe
  mechanical_parts | Mechanical Parts | buy=202 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  military_hardware | Military Hardware | buy=510 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  mining_equipment | Mining Equipment | buy=283 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nickel_ore | Nickel Ore | buy=142 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nutrient_paste | Nutrient Paste | buy=139 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  power_cells | Power Cells | buy=273 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  precision_alloys | Precision Alloys | buy=243 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  protein_blocks | Protein Blocks | buy=177 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  radioactive_ore | Radioactive Ore | buy=156 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  rare_earth_ore | Rare Earth Ore | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  servitor_units | Servitor Units | buy=278 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  small_arms | Small Arms | buy=267 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  spice_wine | Spice Wine | buy=202 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=228 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  steel_ingots | Steel Ingots | buy=162 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  synthetic_intelligences | Synthetic Intelligences | buy=531 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  titanium_bars | Titanium Bars | buy=213 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=455 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_synthetic_intelligences | Weaponized Synthetic Intelligences | buy=638 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 1
1) aluminum_alloy Aluminum Alloy price=172 legality=LEGAL risk=Severe
2) automated_factories Automated Factories price=364 legality=LEGAL risk=Severe
3) autonomous_robots Autonomous Robots price=380 legality=LEGAL risk=Severe
4) basic_rations Basic Rations price=126 legality=LEGAL risk=Severe
5) biological_weapons Biological Weapons price=546 legality=LEGAL risk=Severe
6) copper_ore Copper Ore price=132 legality=LEGAL risk=Severe
7) cybernetic_implants Cybernetic Implants price=329 legality=LEGAL risk=Severe
8) cybernetic_medical_nanites Cybernetic Medical Nanites price=546 legality=LEGAL risk=Severe
9) decorative_metals Decorative Metals price=134 legality=RESTRICTED risk=Severe
10) designer_drugs Designer Drugs price=455 legality=LEGAL risk=Severe
11) electronic_components Electronic Components price=228 legality=LEGAL risk=Severe
12) experimental_reactors Experimental Reactors price=638 legality=LEGAL risk=Severe
13) experimental_weapons Experimental Weapons price=474 legality=LEGAL risk=Severe
14) fresh_produce Fresh Produce price=152 legality=LEGAL risk=Severe
15) gene_therapy_kits Gene Therapy Kits price=486 legality=LEGAL risk=Severe
16) heavy_weapons Heavy Weapons price=389 legality=LEGAL risk=Severe
17) heritage_cuisine Heritage Cuisine price=228 legality=LEGAL risk=Severe
18) high_density_fuel High-Density Fuel price=213 legality=LEGAL risk=Severe
19) industrial_machinery Industrial Machinery price=263 legality=LEGAL risk=Severe
20) mechanical_parts Mechanical Parts price=202 legality=LEGAL risk=Severe
21) medical_nanites Medical Nanites price=546 legality=LEGAL risk=Severe
22) military_hardware Military Hardware price=510 legality=LEGAL risk=Severe
23) mining_equipment Mining Equipment price=283 legality=LEGAL risk=Severe
24) nickel_ore Nickel Ore price=142 legality=LEGAL risk=Severe
25) nutrient_paste Nutrient Paste price=139 legality=LEGAL risk=Severe
26) power_cells Power Cells price=273 legality=LEGAL risk=Severe
27) precision_alloys Precision Alloys price=243 legality=LEGAL risk=Severe
28) protein_blocks Protein Blocks price=177 legality=LEGAL risk=Severe
29) radioactive_ore Radioactive Ore price=156 legality=LEGAL risk=Severe
30) rare_earth_ore Rare Earth Ore price=128 legality=LEGAL risk=Severe
31) servitor_units Servitor Units price=278 legality=LEGAL risk=Severe
32) small_arms Small Arms price=267 legality=LEGAL risk=Severe
33) spice_wine Spice Wine price=202 legality=LEGAL risk=Severe
34) standard_fuel Standard Fuel price=228 legality=LEGAL risk=Severe
35) steel_ingots Steel Ingots price=162 legality=LEGAL risk=Severe
36) synthetic_intelligences Synthetic Intelligences price=531 legality=LEGAL risk=Severe
37) titanium_bars Titanium Bars price=213 legality=LEGAL risk=Severe
38) weaponized_autonomous_robots Weaponized Autonomous Robots price=455 legality=LEGAL risk=Severe
39) weaponized_synthetic_intelligences Weaponized Synthetic Intelligences price=638 legality=LEGAL risk=Severe
Select buy sku index: 17
Quantity: 5
{"active_encounter_count": 0, "command_type": "market_buy", "error": null, "events": [{"command_type": "market_buy", "detail": {"command_type": "market_buy"}, "stage": "start", "subsystem": "engine", "turn": 56, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 56, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"action": "buy", "cargo_after": 5, "credits_after": 880, "credits_before": 2020, "quantity": 5, "sku_id": "heritage_cuisine", "total_cost": 1140, "unit_price": 228}, "stage": "market_trade", "subsystem": "market", "turn": 56, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 880, "destination_id": "SYS-004-DST-02", "location_id": "SYS-004-DST-02-LOC-market", "system_id": "SYS-004"}, "turn_after": 56, "turn_before": 56, "version": "0.11.0"}
MARKET PROFILE
  System: SYS-004
  Destination: SYS-004-DST-02
  Primary economy: military
  Active situations: ['trade_boom']
  ENERGY: produced=[] consumed=['experimental_reactors', 'high_density_fuel', 'power_cells', 'standard_fuel'] neutral=[]
  FOOD: produced=[] consumed=['fresh_produce', 'nutrient_paste', 'protein_blocks', 'spice_wine'] neutral=['basic_rations', 'heritage_cuisine']
  MACHINERY: produced=['automated_factories', 'industrial_machinery', 'military_hardware', 'mining_equipment'] consumed=[] neutral=[]
  MEDICINE: produced=[] consumed=['cybernetic_medical_nanites', 'designer_drugs', 'gene_therapy_kits', 'medical_nanites'] neutral=[]
  METAL: produced=['aluminum_alloy', 'decorative_metals', 'steel_ingots', 'titanium_bars'] consumed=['precision_alloys'] neutral=[]
  ORE: produced=['copper_ore', 'nickel_ore', 'radioactive_ore', 'rare_earth_ore'] consumed=[] neutral=[]
  PARTS: produced=[] consumed=['autonomous_robots', 'servitor_units', 'synthetic_intelligences', 'weaponized_autonomous_robots'] neutral=['cybernetic_implants', 'electronic_components', 'mechanical_parts', 'weaponized_synthetic_intelligences']
  WEAPONS: produced=['biological_weapons', 'experimental_weapons', 'heavy_weapons', 'small_arms'] consumed=[] neutral=[]
MARKET SKUS
  aluminum_alloy | Aluminum Alloy | buy=172 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  automated_factories | Automated Factories | buy=364 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  autonomous_robots | Autonomous Robots | buy=380 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_rations | Basic Rations | buy=126 | sell=126 | cargo=10 | legality=LEGAL | risk=Severe
  biological_weapons | Biological Weapons | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  copper_ore | Copper Ore | buy=132 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_implants | Cybernetic Implants | buy=329 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_medical_nanites | Cybernetic Medical Nanites | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  decorative_metals | Decorative Metals | buy=134 | sell=-- | cargo=0 | legality=RESTRICTED | risk=Severe
  designer_drugs | Designer Drugs | buy=455 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  electronic_components | Electronic Components | buy=228 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_reactors | Experimental Reactors | buy=638 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_weapons | Experimental Weapons | buy=474 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fresh_produce | Fresh Produce | buy=152 | sell=152 | cargo=5 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=486 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heavy_weapons | Heavy Weapons | buy=389 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heritage_cuisine | Heritage Cuisine | buy=228 | sell=228 | cargo=5 | legality=LEGAL | risk=Severe
  high_density_fuel | High-Density Fuel | buy=213 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  industrial_machinery | Industrial Machinery | buy=263 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=91 | cargo=10 | legality=RESTRICTED | risk=Severe
  mechanical_parts | Mechanical Parts | buy=202 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  military_hardware | Military Hardware | buy=510 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  mining_equipment | Mining Equipment | buy=283 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nickel_ore | Nickel Ore | buy=142 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nutrient_paste | Nutrient Paste | buy=139 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  power_cells | Power Cells | buy=273 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  precision_alloys | Precision Alloys | buy=243 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  protein_blocks | Protein Blocks | buy=177 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  radioactive_ore | Radioactive Ore | buy=156 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  rare_earth_ore | Rare Earth Ore | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  servitor_units | Servitor Units | buy=278 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  small_arms | Small Arms | buy=267 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  spice_wine | Spice Wine | buy=202 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=228 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  steel_ingots | Steel Ingots | buy=162 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  synthetic_intelligences | Synthetic Intelligences | buy=531 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  titanium_bars | Titanium Bars | buy=213 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=455 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_synthetic_intelligences | Weaponized Synthetic Intelligences | buy=638 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 1
1) aluminum_alloy Aluminum Alloy price=172 legality=LEGAL risk=Severe
2) automated_factories Automated Factories price=364 legality=LEGAL risk=Severe
3) autonomous_robots Autonomous Robots price=380 legality=LEGAL risk=Severe
4) basic_rations Basic Rations price=126 legality=LEGAL risk=Severe
5) biological_weapons Biological Weapons price=546 legality=LEGAL risk=Severe
6) copper_ore Copper Ore price=132 legality=LEGAL risk=Severe
7) cybernetic_implants Cybernetic Implants price=329 legality=LEGAL risk=Severe
8) cybernetic_medical_nanites Cybernetic Medical Nanites price=546 legality=LEGAL risk=Severe
9) decorative_metals Decorative Metals price=134 legality=RESTRICTED risk=Severe
10) designer_drugs Designer Drugs price=455 legality=LEGAL risk=Severe
11) electronic_components Electronic Components price=228 legality=LEGAL risk=Severe
12) experimental_reactors Experimental Reactors price=638 legality=LEGAL risk=Severe
13) experimental_weapons Experimental Weapons price=474 legality=LEGAL risk=Severe
14) fresh_produce Fresh Produce price=152 legality=LEGAL risk=Severe
15) gene_therapy_kits Gene Therapy Kits price=486 legality=LEGAL risk=Severe
16) heavy_weapons Heavy Weapons price=389 legality=LEGAL risk=Severe
17) heritage_cuisine Heritage Cuisine price=228 legality=LEGAL risk=Severe
18) high_density_fuel High-Density Fuel price=213 legality=LEGAL risk=Severe
19) industrial_machinery Industrial Machinery price=263 legality=LEGAL risk=Severe
20) mechanical_parts Mechanical Parts price=202 legality=LEGAL risk=Severe
21) medical_nanites Medical Nanites price=546 legality=LEGAL risk=Severe
22) military_hardware Military Hardware price=510 legality=LEGAL risk=Severe
23) mining_equipment Mining Equipment price=283 legality=LEGAL risk=Severe
24) nickel_ore Nickel Ore price=142 legality=LEGAL risk=Severe
25) nutrient_paste Nutrient Paste price=139 legality=LEGAL risk=Severe
26) power_cells Power Cells price=273 legality=LEGAL risk=Severe
27) precision_alloys Precision Alloys price=243 legality=LEGAL risk=Severe
28) protein_blocks Protein Blocks price=177 legality=LEGAL risk=Severe
29) radioactive_ore Radioactive Ore price=156 legality=LEGAL risk=Severe
30) rare_earth_ore Rare Earth Ore price=128 legality=LEGAL risk=Severe
31) servitor_units Servitor Units price=278 legality=LEGAL risk=Severe
32) small_arms Small Arms price=267 legality=LEGAL risk=Severe
33) spice_wine Spice Wine price=202 legality=LEGAL risk=Severe
34) standard_fuel Standard Fuel price=228 legality=LEGAL risk=Severe
35) steel_ingots Steel Ingots price=162 legality=LEGAL risk=Severe
36) synthetic_intelligences Synthetic Intelligences price=531 legality=LEGAL risk=Severe
37) titanium_bars Titanium Bars price=213 legality=LEGAL risk=Severe
38) weaponized_autonomous_robots Weaponized Autonomous Robots price=455 legality=LEGAL risk=Severe
39) weaponized_synthetic_intelligences Weaponized Synthetic Intelligences price=638 legality=LEGAL risk=Severe
Select buy sku index: 25
Quantity: 5
{"active_encounter_count": 0, "command_type": "market_buy", "error": null, "events": [{"command_type": "market_buy", "detail": {"command_type": "market_buy"}, "stage": "start", "subsystem": "engine", "turn": 56, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 56, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"action": "buy", "cargo_after": 5, "credits_after": 185, "credits_before": 880, "quantity": 5, "sku_id": "nutrient_paste", "total_cost": 695, "unit_price": 139}, "stage": "market_trade", "subsystem": "market", "turn": 56, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 185, "destination_id": "SYS-004-DST-02", "location_id": "SYS-004-DST-02-LOC-market", "system_id": "SYS-004"}, "turn_after": 56, "turn_before": 56, "version": "0.11.0"}
MARKET PROFILE
  System: SYS-004
  Destination: SYS-004-DST-02
  Primary economy: military
  Active situations: ['trade_boom']
  ENERGY: produced=[] consumed=['experimental_reactors', 'high_density_fuel', 'power_cells', 'standard_fuel'] neutral=[]
  FOOD: produced=[] consumed=['fresh_produce', 'nutrient_paste', 'protein_blocks', 'spice_wine'] neutral=['basic_rations', 'heritage_cuisine']
  MACHINERY: produced=['automated_factories', 'industrial_machinery', 'military_hardware', 'mining_equipment'] consumed=[] neutral=[]
  MEDICINE: produced=[] consumed=['cybernetic_medical_nanites', 'designer_drugs', 'gene_therapy_kits', 'medical_nanites'] neutral=[]
  METAL: produced=['aluminum_alloy', 'decorative_metals', 'steel_ingots', 'titanium_bars'] consumed=['precision_alloys'] neutral=[]
  ORE: produced=['copper_ore', 'nickel_ore', 'radioactive_ore', 'rare_earth_ore'] consumed=[] neutral=[]
  PARTS: produced=[] consumed=['autonomous_robots', 'servitor_units', 'synthetic_intelligences', 'weaponized_autonomous_robots'] neutral=['cybernetic_implants', 'electronic_components', 'mechanical_parts', 'weaponized_synthetic_intelligences']
  WEAPONS: produced=['biological_weapons', 'experimental_weapons', 'heavy_weapons', 'small_arms'] consumed=[] neutral=[]
MARKET SKUS
  aluminum_alloy | Aluminum Alloy | buy=172 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  automated_factories | Automated Factories | buy=364 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  autonomous_robots | Autonomous Robots | buy=380 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_rations | Basic Rations | buy=126 | sell=126 | cargo=10 | legality=LEGAL | risk=Severe
  biological_weapons | Biological Weapons | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  copper_ore | Copper Ore | buy=132 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_implants | Cybernetic Implants | buy=329 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_medical_nanites | Cybernetic Medical Nanites | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  decorative_metals | Decorative Metals | buy=134 | sell=-- | cargo=0 | legality=RESTRICTED | risk=Severe
  designer_drugs | Designer Drugs | buy=455 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  electronic_components | Electronic Components | buy=228 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_reactors | Experimental Reactors | buy=638 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_weapons | Experimental Weapons | buy=474 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fresh_produce | Fresh Produce | buy=152 | sell=152 | cargo=5 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=486 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heavy_weapons | Heavy Weapons | buy=389 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heritage_cuisine | Heritage Cuisine | buy=228 | sell=228 | cargo=5 | legality=LEGAL | risk=Severe
  high_density_fuel | High-Density Fuel | buy=213 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  industrial_machinery | Industrial Machinery | buy=263 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=91 | cargo=10 | legality=RESTRICTED | risk=Severe
  mechanical_parts | Mechanical Parts | buy=202 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  military_hardware | Military Hardware | buy=510 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  mining_equipment | Mining Equipment | buy=283 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nickel_ore | Nickel Ore | buy=142 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nutrient_paste | Nutrient Paste | buy=139 | sell=139 | cargo=5 | legality=LEGAL | risk=Severe
  power_cells | Power Cells | buy=273 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  precision_alloys | Precision Alloys | buy=243 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  protein_blocks | Protein Blocks | buy=177 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  radioactive_ore | Radioactive Ore | buy=156 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  rare_earth_ore | Rare Earth Ore | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  servitor_units | Servitor Units | buy=278 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  small_arms | Small Arms | buy=267 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  spice_wine | Spice Wine | buy=202 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=228 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  steel_ingots | Steel Ingots | buy=162 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  synthetic_intelligences | Synthetic Intelligences | buy=531 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  titanium_bars | Titanium Bars | buy=213 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=455 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_synthetic_intelligences | Weaponized Synthetic Intelligences | buy=638 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 1
1) aluminum_alloy Aluminum Alloy price=172 legality=LEGAL risk=Severe
2) automated_factories Automated Factories price=364 legality=LEGAL risk=Severe
3) autonomous_robots Autonomous Robots price=380 legality=LEGAL risk=Severe
4) basic_rations Basic Rations price=126 legality=LEGAL risk=Severe
5) biological_weapons Biological Weapons price=546 legality=LEGAL risk=Severe
6) copper_ore Copper Ore price=132 legality=LEGAL risk=Severe
7) cybernetic_implants Cybernetic Implants price=329 legality=LEGAL risk=Severe
8) cybernetic_medical_nanites Cybernetic Medical Nanites price=546 legality=LEGAL risk=Severe
9) decorative_metals Decorative Metals price=134 legality=RESTRICTED risk=Severe
10) designer_drugs Designer Drugs price=455 legality=LEGAL risk=Severe
11) electronic_components Electronic Components price=228 legality=LEGAL risk=Severe
12) experimental_reactors Experimental Reactors price=638 legality=LEGAL risk=Severe
13) experimental_weapons Experimental Weapons price=474 legality=LEGAL risk=Severe
14) fresh_produce Fresh Produce price=152 legality=LEGAL risk=Severe
15) gene_therapy_kits Gene Therapy Kits price=486 legality=LEGAL risk=Severe
16) heavy_weapons Heavy Weapons price=389 legality=LEGAL risk=Severe
17) heritage_cuisine Heritage Cuisine price=228 legality=LEGAL risk=Severe
18) high_density_fuel High-Density Fuel price=213 legality=LEGAL risk=Severe
19) industrial_machinery Industrial Machinery price=263 legality=LEGAL risk=Severe
20) mechanical_parts Mechanical Parts price=202 legality=LEGAL risk=Severe
21) medical_nanites Medical Nanites price=546 legality=LEGAL risk=Severe
22) military_hardware Military Hardware price=510 legality=LEGAL risk=Severe
23) mining_equipment Mining Equipment price=283 legality=LEGAL risk=Severe
24) nickel_ore Nickel Ore price=142 legality=LEGAL risk=Severe
25) nutrient_paste Nutrient Paste price=139 legality=LEGAL risk=Severe
26) power_cells Power Cells price=273 legality=LEGAL risk=Severe
27) precision_alloys Precision Alloys price=243 legality=LEGAL risk=Severe
28) protein_blocks Protein Blocks price=177 legality=LEGAL risk=Severe
29) radioactive_ore Radioactive Ore price=156 legality=LEGAL risk=Severe
30) rare_earth_ore Rare Earth Ore price=128 legality=LEGAL risk=Severe
31) servitor_units Servitor Units price=278 legality=LEGAL risk=Severe
32) small_arms Small Arms price=267 legality=LEGAL risk=Severe
33) spice_wine Spice Wine price=202 legality=LEGAL risk=Severe
34) standard_fuel Standard Fuel price=228 legality=LEGAL risk=Severe
35) steel_ingots Steel Ingots price=162 legality=LEGAL risk=Severe
36) synthetic_intelligences Synthetic Intelligences price=531 legality=LEGAL risk=Severe
37) titanium_bars Titanium Bars price=213 legality=LEGAL risk=Severe
38) weaponized_autonomous_robots Weaponized Autonomous Robots price=455 legality=LEGAL risk=Severe
39) weaponized_synthetic_intelligences Weaponized Synthetic Intelligences price=638 legality=LEGAL risk=Severe
Select buy sku index: 28
Quantity: 5
{"active_encounter_count": 0, "command_type": "market_buy", "error": "insufficient_credits", "events": [{"command_type": "market_buy", "detail": {"command_type": "market_buy"}, "stage": "start", "subsystem": "engine", "turn": 56, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 56, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": false, "player": {"arrest_state": "free", "credits": 185, "destination_id": "SYS-004-DST-02", "location_id": "SYS-004-DST-02-LOC-market", "system_id": "SYS-004"}, "turn_after": 56, "turn_before": 56, "version": "0.11.0"}
MARKET PROFILE
  System: SYS-004
  Destination: SYS-004-DST-02
  Primary economy: military
  Active situations: ['trade_boom']
  ENERGY: produced=[] consumed=['experimental_reactors', 'high_density_fuel', 'power_cells', 'standard_fuel'] neutral=[]
  FOOD: produced=[] consumed=['fresh_produce', 'nutrient_paste', 'protein_blocks', 'spice_wine'] neutral=['basic_rations', 'heritage_cuisine']
  MACHINERY: produced=['automated_factories', 'industrial_machinery', 'military_hardware', 'mining_equipment'] consumed=[] neutral=[]
  MEDICINE: produced=[] consumed=['cybernetic_medical_nanites', 'designer_drugs', 'gene_therapy_kits', 'medical_nanites'] neutral=[]
  METAL: produced=['aluminum_alloy', 'decorative_metals', 'steel_ingots', 'titanium_bars'] consumed=['precision_alloys'] neutral=[]
  ORE: produced=['copper_ore', 'nickel_ore', 'radioactive_ore', 'rare_earth_ore'] consumed=[] neutral=[]
  PARTS: produced=[] consumed=['autonomous_robots', 'servitor_units', 'synthetic_intelligences', 'weaponized_autonomous_robots'] neutral=['cybernetic_implants', 'electronic_components', 'mechanical_parts', 'weaponized_synthetic_intelligences']
  WEAPONS: produced=['biological_weapons', 'experimental_weapons', 'heavy_weapons', 'small_arms'] consumed=[] neutral=[]
MARKET SKUS
  aluminum_alloy | Aluminum Alloy | buy=172 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  automated_factories | Automated Factories | buy=364 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  autonomous_robots | Autonomous Robots | buy=380 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_rations | Basic Rations | buy=126 | sell=126 | cargo=10 | legality=LEGAL | risk=Severe
  biological_weapons | Biological Weapons | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  copper_ore | Copper Ore | buy=132 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_implants | Cybernetic Implants | buy=329 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_medical_nanites | Cybernetic Medical Nanites | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  decorative_metals | Decorative Metals | buy=134 | sell=-- | cargo=0 | legality=RESTRICTED | risk=Severe
  designer_drugs | Designer Drugs | buy=455 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  electronic_components | Electronic Components | buy=228 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_reactors | Experimental Reactors | buy=638 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_weapons | Experimental Weapons | buy=474 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fresh_produce | Fresh Produce | buy=152 | sell=152 | cargo=5 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=486 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heavy_weapons | Heavy Weapons | buy=389 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heritage_cuisine | Heritage Cuisine | buy=228 | sell=228 | cargo=5 | legality=LEGAL | risk=Severe
  high_density_fuel | High-Density Fuel | buy=213 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  industrial_machinery | Industrial Machinery | buy=263 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=91 | cargo=10 | legality=RESTRICTED | risk=Severe
  mechanical_parts | Mechanical Parts | buy=202 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  military_hardware | Military Hardware | buy=510 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  mining_equipment | Mining Equipment | buy=283 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nickel_ore | Nickel Ore | buy=142 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nutrient_paste | Nutrient Paste | buy=139 | sell=139 | cargo=5 | legality=LEGAL | risk=Severe
  power_cells | Power Cells | buy=273 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  precision_alloys | Precision Alloys | buy=243 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  protein_blocks | Protein Blocks | buy=177 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  radioactive_ore | Radioactive Ore | buy=156 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  rare_earth_ore | Rare Earth Ore | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  servitor_units | Servitor Units | buy=278 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  small_arms | Small Arms | buy=267 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  spice_wine | Spice Wine | buy=202 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=228 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  steel_ingots | Steel Ingots | buy=162 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  synthetic_intelligences | Synthetic Intelligences | buy=531 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  titanium_bars | Titanium Bars | buy=213 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=455 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_synthetic_intelligences | Weaponized Synthetic Intelligences | buy=638 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 1
1) aluminum_alloy Aluminum Alloy price=172 legality=LEGAL risk=Severe
2) automated_factories Automated Factories price=364 legality=LEGAL risk=Severe
3) autonomous_robots Autonomous Robots price=380 legality=LEGAL risk=Severe
4) basic_rations Basic Rations price=126 legality=LEGAL risk=Severe
5) biological_weapons Biological Weapons price=546 legality=LEGAL risk=Severe
6) copper_ore Copper Ore price=132 legality=LEGAL risk=Severe
7) cybernetic_implants Cybernetic Implants price=329 legality=LEGAL risk=Severe
8) cybernetic_medical_nanites Cybernetic Medical Nanites price=546 legality=LEGAL risk=Severe
9) decorative_metals Decorative Metals price=134 legality=RESTRICTED risk=Severe
10) designer_drugs Designer Drugs price=455 legality=LEGAL risk=Severe
11) electronic_components Electronic Components price=228 legality=LEGAL risk=Severe
12) experimental_reactors Experimental Reactors price=638 legality=LEGAL risk=Severe
13) experimental_weapons Experimental Weapons price=474 legality=LEGAL risk=Severe
14) fresh_produce Fresh Produce price=152 legality=LEGAL risk=Severe
15) gene_therapy_kits Gene Therapy Kits price=486 legality=LEGAL risk=Severe
16) heavy_weapons Heavy Weapons price=389 legality=LEGAL risk=Severe
17) heritage_cuisine Heritage Cuisine price=228 legality=LEGAL risk=Severe
18) high_density_fuel High-Density Fuel price=213 legality=LEGAL risk=Severe
19) industrial_machinery Industrial Machinery price=263 legality=LEGAL risk=Severe
20) mechanical_parts Mechanical Parts price=202 legality=LEGAL risk=Severe
21) medical_nanites Medical Nanites price=546 legality=LEGAL risk=Severe
22) military_hardware Military Hardware price=510 legality=LEGAL risk=Severe
23) mining_equipment Mining Equipment price=283 legality=LEGAL risk=Severe
24) nickel_ore Nickel Ore price=142 legality=LEGAL risk=Severe
25) nutrient_paste Nutrient Paste price=139 legality=LEGAL risk=Severe
26) power_cells Power Cells price=273 legality=LEGAL risk=Severe
27) precision_alloys Precision Alloys price=243 legality=LEGAL risk=Severe
28) protein_blocks Protein Blocks price=177 legality=LEGAL risk=Severe
29) radioactive_ore Radioactive Ore price=156 legality=LEGAL risk=Severe
30) rare_earth_ore Rare Earth Ore price=128 legality=LEGAL risk=Severe
31) servitor_units Servitor Units price=278 legality=LEGAL risk=Severe
32) small_arms Small Arms price=267 legality=LEGAL risk=Severe
33) spice_wine Spice Wine price=202 legality=LEGAL risk=Severe
34) standard_fuel Standard Fuel price=228 legality=LEGAL risk=Severe
35) steel_ingots Steel Ingots price=162 legality=LEGAL risk=Severe
36) synthetic_intelligences Synthetic Intelligences price=531 legality=LEGAL risk=Severe
37) titanium_bars Titanium Bars price=213 legality=LEGAL risk=Severe
38) weaponized_autonomous_robots Weaponized Autonomous Robots price=455 legality=LEGAL risk=Severe
39) weaponized_synthetic_intelligences Weaponized Synthetic Intelligences price=638 legality=LEGAL risk=Severe
Select buy sku index: 33
Quantity: 5
{"active_encounter_count": 0, "command_type": "market_buy", "error": "insufficient_credits", "events": [{"command_type": "market_buy", "detail": {"command_type": "market_buy"}, "stage": "start", "subsystem": "engine", "turn": 56, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 56, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": false, "player": {"arrest_state": "free", "credits": 185, "destination_id": "SYS-004-DST-02", "location_id": "SYS-004-DST-02-LOC-market", "system_id": "SYS-004"}, "turn_after": 56, "turn_before": 56, "version": "0.11.0"}
MARKET PROFILE
  System: SYS-004
  Destination: SYS-004-DST-02
  Primary economy: military
  Active situations: ['trade_boom']
  ENERGY: produced=[] consumed=['experimental_reactors', 'high_density_fuel', 'power_cells', 'standard_fuel'] neutral=[]
  FOOD: produced=[] consumed=['fresh_produce', 'nutrient_paste', 'protein_blocks', 'spice_wine'] neutral=['basic_rations', 'heritage_cuisine']
  MACHINERY: produced=['automated_factories', 'industrial_machinery', 'military_hardware', 'mining_equipment'] consumed=[] neutral=[]
  MEDICINE: produced=[] consumed=['cybernetic_medical_nanites', 'designer_drugs', 'gene_therapy_kits', 'medical_nanites'] neutral=[]
  METAL: produced=['aluminum_alloy', 'decorative_metals', 'steel_ingots', 'titanium_bars'] consumed=['precision_alloys'] neutral=[]
  ORE: produced=['copper_ore', 'nickel_ore', 'radioactive_ore', 'rare_earth_ore'] consumed=[] neutral=[]
  PARTS: produced=[] consumed=['autonomous_robots', 'servitor_units', 'synthetic_intelligences', 'weaponized_autonomous_robots'] neutral=['cybernetic_implants', 'electronic_components', 'mechanical_parts', 'weaponized_synthetic_intelligences']
  WEAPONS: produced=['biological_weapons', 'experimental_weapons', 'heavy_weapons', 'small_arms'] consumed=[] neutral=[]
MARKET SKUS
  aluminum_alloy | Aluminum Alloy | buy=172 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  automated_factories | Automated Factories | buy=364 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  autonomous_robots | Autonomous Robots | buy=380 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_rations | Basic Rations | buy=126 | sell=126 | cargo=10 | legality=LEGAL | risk=Severe
  biological_weapons | Biological Weapons | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  copper_ore | Copper Ore | buy=132 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_implants | Cybernetic Implants | buy=329 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_medical_nanites | Cybernetic Medical Nanites | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  decorative_metals | Decorative Metals | buy=134 | sell=-- | cargo=0 | legality=RESTRICTED | risk=Severe
  designer_drugs | Designer Drugs | buy=455 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  electronic_components | Electronic Components | buy=228 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_reactors | Experimental Reactors | buy=638 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_weapons | Experimental Weapons | buy=474 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fresh_produce | Fresh Produce | buy=152 | sell=152 | cargo=5 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=486 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heavy_weapons | Heavy Weapons | buy=389 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heritage_cuisine | Heritage Cuisine | buy=228 | sell=228 | cargo=5 | legality=LEGAL | risk=Severe
  high_density_fuel | High-Density Fuel | buy=213 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  industrial_machinery | Industrial Machinery | buy=263 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=91 | cargo=10 | legality=RESTRICTED | risk=Severe
  mechanical_parts | Mechanical Parts | buy=202 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  military_hardware | Military Hardware | buy=510 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  mining_equipment | Mining Equipment | buy=283 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nickel_ore | Nickel Ore | buy=142 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nutrient_paste | Nutrient Paste | buy=139 | sell=139 | cargo=5 | legality=LEGAL | risk=Severe
  power_cells | Power Cells | buy=273 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  precision_alloys | Precision Alloys | buy=243 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  protein_blocks | Protein Blocks | buy=177 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  radioactive_ore | Radioactive Ore | buy=156 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  rare_earth_ore | Rare Earth Ore | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  servitor_units | Servitor Units | buy=278 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  small_arms | Small Arms | buy=267 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  spice_wine | Spice Wine | buy=202 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=228 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  steel_ingots | Steel Ingots | buy=162 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  synthetic_intelligences | Synthetic Intelligences | buy=531 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  titanium_bars | Titanium Bars | buy=213 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=455 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_synthetic_intelligences | Weaponized Synthetic Intelligences | buy=638 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 2
1) basic_rations Basic Rations units=10 price=126 legality=LEGAL risk=Severe
2) fresh_produce Fresh Produce units=5 price=152 legality=LEGAL risk=Severe
3) heritage_cuisine Heritage Cuisine units=5 price=228 legality=LEGAL risk=Severe
4) luxury_fresh_produce luxury_fresh_produce units=10 price=91 legality=RESTRICTED risk=Severe
5) nutrient_paste Nutrient Paste units=5 price=139 legality=LEGAL risk=Severe
Select sell sku index: 0
Quantity: 0
Invalid sell index.
MARKET PROFILE
  System: SYS-004
  Destination: SYS-004-DST-02
  Primary economy: military
  Active situations: ['trade_boom']
  ENERGY: produced=[] consumed=['experimental_reactors', 'high_density_fuel', 'power_cells', 'standard_fuel'] neutral=[]
  FOOD: produced=[] consumed=['fresh_produce', 'nutrient_paste', 'protein_blocks', 'spice_wine'] neutral=['basic_rations', 'heritage_cuisine']
  MACHINERY: produced=['automated_factories', 'industrial_machinery', 'military_hardware', 'mining_equipment'] consumed=[] neutral=[]
  MEDICINE: produced=[] consumed=['cybernetic_medical_nanites', 'designer_drugs', 'gene_therapy_kits', 'medical_nanites'] neutral=[]
  METAL: produced=['aluminum_alloy', 'decorative_metals', 'steel_ingots', 'titanium_bars'] consumed=['precision_alloys'] neutral=[]
  ORE: produced=['copper_ore', 'nickel_ore', 'radioactive_ore', 'rare_earth_ore'] consumed=[] neutral=[]
  PARTS: produced=[] consumed=['autonomous_robots', 'servitor_units', 'synthetic_intelligences', 'weaponized_autonomous_robots'] neutral=['cybernetic_implants', 'electronic_components', 'mechanical_parts', 'weaponized_synthetic_intelligences']
  WEAPONS: produced=['biological_weapons', 'experimental_weapons', 'heavy_weapons', 'small_arms'] consumed=[] neutral=[]
MARKET SKUS
  aluminum_alloy | Aluminum Alloy | buy=172 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  automated_factories | Automated Factories | buy=364 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  autonomous_robots | Autonomous Robots | buy=380 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_rations | Basic Rations | buy=126 | sell=126 | cargo=10 | legality=LEGAL | risk=Severe
  biological_weapons | Biological Weapons | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  copper_ore | Copper Ore | buy=132 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_implants | Cybernetic Implants | buy=329 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_medical_nanites | Cybernetic Medical Nanites | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  decorative_metals | Decorative Metals | buy=134 | sell=-- | cargo=0 | legality=RESTRICTED | risk=Severe
  designer_drugs | Designer Drugs | buy=455 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  electronic_components | Electronic Components | buy=228 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_reactors | Experimental Reactors | buy=638 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_weapons | Experimental Weapons | buy=474 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fresh_produce | Fresh Produce | buy=152 | sell=152 | cargo=5 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=486 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heavy_weapons | Heavy Weapons | buy=389 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heritage_cuisine | Heritage Cuisine | buy=228 | sell=228 | cargo=5 | legality=LEGAL | risk=Severe
  high_density_fuel | High-Density Fuel | buy=213 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  industrial_machinery | Industrial Machinery | buy=263 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=91 | cargo=10 | legality=RESTRICTED | risk=Severe
  mechanical_parts | Mechanical Parts | buy=202 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=546 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  military_hardware | Military Hardware | buy=510 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  mining_equipment | Mining Equipment | buy=283 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nickel_ore | Nickel Ore | buy=142 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nutrient_paste | Nutrient Paste | buy=139 | sell=139 | cargo=5 | legality=LEGAL | risk=Severe
  power_cells | Power Cells | buy=273 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  precision_alloys | Precision Alloys | buy=243 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  protein_blocks | Protein Blocks | buy=177 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  radioactive_ore | Radioactive Ore | buy=156 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  rare_earth_ore | Rare Earth Ore | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  servitor_units | Servitor Units | buy=278 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  small_arms | Small Arms | buy=267 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  spice_wine | Spice Wine | buy=202 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=228 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  steel_ingots | Steel Ingots | buy=162 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  synthetic_intelligences | Synthetic Intelligences | buy=531 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  titanium_bars | Titanium Bars | buy=213 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=455 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_synthetic_intelligences | Weaponized Synthetic Intelligences | buy=638 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 3
Returned to destination: SYS-004-DST-02
DESTINATION: Flux 2 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 4
1) customs_inspection Customs Inspection
2) refuel Refuel
3) Back
Select destination action index: 2
requested_units: 50
{"active_encounter_count": 0, "command_type": "destination_action", "error": null, "events": [{"command_type": "destination_action", "detail": {"command_type": "destination_action"}, "stage": "start", "subsystem": "engine", "turn": 56, "world_seed": 12345}, {"command_type": "destination_action", "detail": {"action_id": "refuel", "result": {"credits": 185, "ok": false, "reason": "insufficient_credits", "total_cost": 0, "units_purchased": 0}, "result_summary": {"credits_after": 185, "credits_before": 185, "fuel_after": 3, "fuel_before": 3, "reason": "insufficient_credits", "result_ok": false, "total_cost": 0, "unit_price": 0, "units_purchased": 0}}, "stage": "destination_action", "subsystem": "interaction_layer", "turn": 56, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 185, "destination_id": "SYS-004-DST-02", "location_id": "SYS-004-DST-02", "system_id": "SYS-004"}, "turn_after": 56, "turn_before": 56, "version": "0.11.0"}
1) customs_inspection Customs Inspection
2) refuel Refuel
3) Back
Select destination action index: 3
DESTINATION: Flux 2 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 3
Current system: SYS-004 (Flux)
1) Inter-system warp
2) Intra-system destination travel
3) Back
Travel mode: 1
No inter-system targets in range.
Current system: SYS-004 (Flux)
1) Inter-system warp
2) Intra-system destination travel
3) Back
Travel mode: 1
No inter-system targets in range.
Current system: SYS-004 (Flux)
1) Inter-system warp
2) Intra-system destination travel
3) Back
Travel mode: 3
DESTINATION: Flux 2 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 4
1) customs_inspection Customs Inspection
2) refuel Refuel
3) Back
Select destination action index: 2
requested_units: 5
{"active_encounter_count": 0, "command_type": "destination_action", "error": null, "events": [{"command_type": "destination_action", "detail": {"command_type": "destination_action"}, "stage": "start", "subsystem": "engine", "turn": 56, "world_seed": 12345}, {"command_type": "destination_action", "detail": {"action_id": "refuel", "result": {"credits": 160, "current_fuel": 8, "ok": true, "reason": "ok", "total_cost": 25, "units_purchased": 5}, "result_summary": {"credits_after": 160, "credits_before": 185, "fuel_after": 8, "fuel_before": 3, "reason": "ok", "result_ok": true, "total_cost": 25, "unit_price": 5, "units_purchased": 5}}, "stage": "destination_action", "subsystem": "interaction_layer", "turn": 56, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 160, "destination_id": "SYS-004-DST-02", "location_id": "SYS-004-DST-02", "system_id": "SYS-004"}, "turn_after": 56, "turn_before": 56, "version": "0.11.0"}
1) customs_inspection Customs Inspection
2) refuel Refuel
3) Back
Select destination action index: 3
DESTINATION: Flux 2 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 3
Current system: SYS-004 (Flux)
1) Inter-system warp
2) Intra-system destination travel
3) Back
Travel mode: 1
No inter-system targets in range.
Current system: SYS-004 (Flux)
1) Inter-system warp
2) Intra-system destination travel
3) Back
Travel mode: 3
DESTINATION: Flux 2 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 1
PLAYER / SHIP INFO
  Credits: 160
  Fuel: 8/55
  Cargo manifest: {'basic_rations': 10, 'fresh_produce': 5, 'heritage_cuisine': 5, 'luxury_fresh_produce': 10, 'nutrient_paste': 5}
  Reputation: 50 band=0
  Heat: 0
  Notoriety: 0 band=-2
  Arrest state: free
  Warrants: []
  Location: SYS-004 / SYS-004-DST-02 / SYS-004-DST-02
  Turn: 56
  Active crew: []
  Active missions: []
ONGOING COSTS
  Insurance: 0
  Warehouse rental: 0
  Crew wages: 0
  Total recurring cost: 0
WAREHOUSE RENTALS
  none
DESTINATION: Flux 2 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 3
Current system: SYS-004 (Flux)
1) Inter-system warp
2) Intra-system destination travel
3) Back
Travel mode: 2
1) SYS-004-DST-01 Flux 1
2) SYS-004-DST-02 Flux 2
3) SYS-004-DST-03 Flux 3
4) SYS-004-DST-04 Flux 4
Select destination index: 3
[time_engine] action=time_advance_requested change=start_turn=56 days=1 reason=travel:TRAVEL-SYS-004:SYS-004:SYS-004-DST-03:56:auto_route
[time_engine] action=galaxy_tick change=day=57
[time_engine] action=system_tick change=day=57
[time_engine] action=planet_station_tick change=day=57
[time_engine] action=location_tick change=day=57
[time_engine] action=npc_tick change=day=57
[time_engine] action=end_of_day_log change=day=57
Spawn gate cooldown check: system_id=SYS-004 current_day=57 cooldown_until=59 skipped=true reason=cooldown_active
Situation expired: trade_boom system=SYS-004
[time_engine] action=time_advance_day_completed change=turn=57 hard_stop=None
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 56, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-004-DST-03", "target_system_id": "SYS-004", "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-03:56:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 56, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 8, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-03:56:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 56, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-03:56:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 57, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"outcome": {"arrested": false, "dead": false, "detention_tier": null, "escaped": false, "fines_added": 0, "heat_delta": 5, "market_access_denied": false, "rep_delta": 0, "ship_lost": false, "warrant_issued": false}, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 57, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 3, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-03:56:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 57, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-03:56:auto_route_enc_0", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 57, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-03:56:auto_route_enc_0", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 4, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-004:SYS-004-DST-03:56:auto_route_enc_0ignore0", "selected_outcome": "hail", "tr_delta": 3, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 57, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-03:56:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 57, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-03:56:auto_route_enc_1", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 57, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-03:56:auto_route_enc_1", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-004:SYS-004-DST-03:56:auto_route_enc_1ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [2, 5, 1], "weights_after_notoriety": [2, 5, 1], "weights_after_reputation": [2, 5, 1], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 57, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-03:56:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 57, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-03:56:auto_route_enc_3", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 57, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-03:56:auto_route_enc_3", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 4, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-004:SYS-004-DST-03:56:auto_route_enc_3ignore0", "selected_outcome": "hail", "tr_delta": 3, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 57, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-03:56:auto_route_enc_3", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 57, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 160, "destination_id": "SYS-004-DST-03", "location_id": "SYS-004-DST-03", "system_id": "SYS-004"}, "turn_after": 57, "turn_before": 56, "version": "0.11.0"}
DESTINATION: Flux 3 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 5
0) Back
1) SYS-004-DST-03-LOC-datanet type=datanet
2) SYS-004-DST-03-LOC-market type=market
3) SYS-004-DST-03-LOC-warehouse type=warehouse
4) SYS-004-DST-03-LOC-shipdock type=shipdock
5) SYS-004-DST-03-LOC-administration type=administration
Select location index: 2
Entered location: SYS-004-DST-03-LOC-market
MARKET PROFILE
  System: SYS-004
  Destination: SYS-004-DST-03
  Primary economy: military
  Active situations: none
  ENERGY: produced=[] consumed=['high_density_fuel', 'power_cells', 'standard_fuel'] neutral=[]
  FOOD: produced=[] consumed=[] neutral=['fresh_produce', 'heritage_cuisine', 'spice_wine']
  MACHINERY: produced=['automated_factories', 'military_hardware', 'mining_equipment'] consumed=[] neutral=[]
  MEDICINE: produced=[] consumed=[] neutral=['advanced_pharmaceuticals', 'basic_medkits', 'gene_therapy_kits']
  METAL: produced=[] consumed=['aluminum_alloy', 'precision_alloys', 'titanium_bars'] neutral=[]
  PARTS: produced=[] consumed=['autonomous_robots', 'cybernetic_implants', 'mechanical_parts'] neutral=[]
  WEAPONS: produced=['experimental_weapons', 'heavy_weapons', 'small_arms'] consumed=[] neutral=[]
MARKET SKUS
  advanced_pharmaceuticals | Advanced Pharmaceuticals | buy=220 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  aluminum_alloy | Aluminum Alloy | buy=204 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  automated_factories | Automated Factories | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  autonomous_robots | Autonomous Robots | buy=360 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_medkits | Basic Medkits | buy=180 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_rations | Basic Rations | buy=-- | sell=58 | cargo=10 | legality=LEGAL | risk=Severe
  cybernetic_implants | Cybernetic Implants | buy=312 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_weapons | Experimental Weapons | buy=374 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fresh_produce | Fresh Produce | buy=120 | sell=120 | cargo=5 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=320 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heavy_weapons | Heavy Weapons | buy=307 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heritage_cuisine | Heritage Cuisine | buy=180 | sell=180 | cargo=5 | legality=LEGAL | risk=Severe
  high_density_fuel | High-Density Fuel | buy=168 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=72 | cargo=10 | legality=RESTRICTED | risk=Severe
  mechanical_parts | Mechanical Parts | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  military_hardware | Military Hardware | buy=403 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  mining_equipment | Mining Equipment | buy=224 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nutrient_paste | Nutrient Paste | buy=-- | sell=53 | cargo=5 | legality=LEGAL | risk=Severe
  power_cells | Power Cells | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  precision_alloys | Precision Alloys | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  small_arms | Small Arms | buy=211 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  spice_wine | Spice Wine | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=180 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  titanium_bars | Titanium Bars | buy=252 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 2
1) basic_rations Basic Rations units=10 price=58 legality=LEGAL risk=Severe
2) fresh_produce Fresh Produce units=5 price=120 legality=LEGAL risk=Severe
3) heritage_cuisine Heritage Cuisine units=5 price=180 legality=LEGAL risk=Severe
4) luxury_fresh_produce luxury_fresh_produce units=10 price=72 legality=RESTRICTED risk=Severe
5) nutrient_paste Nutrient Paste units=5 price=53 legality=LEGAL risk=Severe
Select sell sku index: 2
Quantity: 5
{"active_encounter_count": 0, "command_type": "market_sell", "error": null, "events": [{"command_type": "market_sell", "detail": {"command_type": "market_sell"}, "stage": "start", "subsystem": "engine", "turn": 57, "world_seed": 12345}, {"command_type": "market_sell", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 57, "world_seed": 12345}, {"command_type": "market_sell", "detail": {"action": "sell", "cargo_after": 0, "credits_after": 760, "credits_before": 160, "quantity": 5, "sku_id": "fresh_produce", "total_gain": 600, "unit_price": 120}, "stage": "market_trade", "subsystem": "market", "turn": 57, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 760, "destination_id": "SYS-004-DST-03", "location_id": "SYS-004-DST-03-LOC-market", "system_id": "SYS-004"}, "turn_after": 57, "turn_before": 57, "version": "0.11.0"}
MARKET PROFILE
  System: SYS-004
  Destination: SYS-004-DST-03
  Primary economy: military
  Active situations: none
  ENERGY: produced=[] consumed=['high_density_fuel', 'power_cells', 'standard_fuel'] neutral=[]
  FOOD: produced=[] consumed=[] neutral=['fresh_produce', 'heritage_cuisine', 'spice_wine']
  MACHINERY: produced=['automated_factories', 'military_hardware', 'mining_equipment'] consumed=[] neutral=[]
  MEDICINE: produced=[] consumed=[] neutral=['advanced_pharmaceuticals', 'basic_medkits', 'gene_therapy_kits']
  METAL: produced=[] consumed=['aluminum_alloy', 'precision_alloys', 'titanium_bars'] neutral=[]
  PARTS: produced=[] consumed=['autonomous_robots', 'cybernetic_implants', 'mechanical_parts'] neutral=[]
  WEAPONS: produced=['experimental_weapons', 'heavy_weapons', 'small_arms'] consumed=[] neutral=[]
MARKET SKUS
  advanced_pharmaceuticals | Advanced Pharmaceuticals | buy=220 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  aluminum_alloy | Aluminum Alloy | buy=204 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  automated_factories | Automated Factories | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  autonomous_robots | Autonomous Robots | buy=360 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_medkits | Basic Medkits | buy=180 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_rations | Basic Rations | buy=-- | sell=58 | cargo=10 | legality=LEGAL | risk=Severe
  cybernetic_implants | Cybernetic Implants | buy=312 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_weapons | Experimental Weapons | buy=374 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fresh_produce | Fresh Produce | buy=120 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=320 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heavy_weapons | Heavy Weapons | buy=307 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heritage_cuisine | Heritage Cuisine | buy=180 | sell=180 | cargo=5 | legality=LEGAL | risk=Severe
  high_density_fuel | High-Density Fuel | buy=168 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=72 | cargo=10 | legality=RESTRICTED | risk=Severe
  mechanical_parts | Mechanical Parts | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  military_hardware | Military Hardware | buy=403 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  mining_equipment | Mining Equipment | buy=224 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nutrient_paste | Nutrient Paste | buy=-- | sell=53 | cargo=5 | legality=LEGAL | risk=Severe
  power_cells | Power Cells | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  precision_alloys | Precision Alloys | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  small_arms | Small Arms | buy=211 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  spice_wine | Spice Wine | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=180 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  titanium_bars | Titanium Bars | buy=252 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 3
Returned to destination: SYS-004-DST-03
DESTINATION: Flux 3 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 3
Current system: SYS-004 (Flux)
1) Inter-system warp
2) Intra-system destination travel
3) Back
Travel mode: 2
1) SYS-004-DST-01 Flux 1
2) SYS-004-DST-02 Flux 2
3) SYS-004-DST-03 Flux 3
4) SYS-004-DST-04 Flux 4
Select destination index: 4
[time_engine] action=time_advance_requested change=start_turn=57 days=1 reason=travel:TRAVEL-SYS-004:SYS-004:SYS-004-DST-04:57:auto_route
[time_engine] action=galaxy_tick change=day=58
[time_engine] action=system_tick change=day=58
[time_engine] action=planet_station_tick change=day=58
[time_engine] action=location_tick change=day=58
[time_engine] action=npc_tick change=day=58
[time_engine] action=end_of_day_log change=day=58
Spawn gate cooldown check: system_id=SYS-004 current_day=58 cooldown_until=59 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=58 hard_stop=None
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 57, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-004-DST-04", "target_system_id": "SYS-004", "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-04:57:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 57, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 8, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-04:57:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 57, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-04:57:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 58, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"outcome": {"arrested": false, "dead": false, "detention_tier": null, "escaped": false, "fines_added": 0, "heat_delta": 5, "market_access_denied": false, "rep_delta": 0, "ship_lost": false, "warrant_issued": false}, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 58, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 2, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-04:57:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 58, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-04:57:auto_route_enc_2", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 58, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-04:57:auto_route_enc_2", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 58, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-04:57:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 58, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-04:57:auto_route_enc_5", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 58, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-04:57:auto_route_enc_5", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": ["attack_plus_one_high_tr_delta"], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-004:SYS-004-DST-04:57:auto_route_enc_5ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [2, 5, 2], "weights_after_notoriety": [2, 5, 2], "weights_after_reputation": [2, 5, 2], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 58, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-04:57:auto_route_enc_5", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 58, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 760, "destination_id": "SYS-004-DST-04", "location_id": "SYS-004-DST-04", "system_id": "SYS-004"}, "turn_after": 58, "turn_before": 57, "version": "0.11.0"}
DESTINATION: Flux 4 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 5
No locations available.
DESTINATION: Flux 4 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 4
1) customs_inspection Customs Inspection
2) Back
Select destination action index: 2
DESTINATION: Flux 4 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 3
Current system: SYS-004 (Flux)
1) Inter-system warp
2) Intra-system destination travel
3) Back
Travel mode: 2
1) SYS-004-DST-01 Flux 1
2) SYS-004-DST-02 Flux 2
3) SYS-004-DST-03 Flux 3
4) SYS-004-DST-04 Flux 4
Select destination index: 1
[time_engine] action=time_advance_requested change=start_turn=58 days=1 reason=travel:TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route
[time_engine] action=galaxy_tick change=day=59
[time_engine] action=system_tick change=day=59
[time_engine] action=planet_station_tick change=day=59
[time_engine] action=location_tick change=day=59
[time_engine] action=npc_tick change=day=59
[time_engine] action=end_of_day_log change=day=59
Spawn gate cooldown check: system_id=SYS-004 current_day=59 cooldown_until=59 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=59 hard_stop=None
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 58, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-004-DST-01", "target_system_id": "SYS-004", "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 58, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 8, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 58, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 59, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"outcome": {"arrested": false, "dead": false, "detention_tier": null, "escaped": false, "fines_added": 0, "heat_delta": 5, "market_access_denied": false, "rep_delta": 0, "ship_lost": false, "warrant_issued": false}, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 59, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 5, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 59, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route_enc_0", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 59, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route_enc_0", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": ["attack_plus_one_high_tr_delta"], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route_enc_0ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [2, 5, 2], "weights_after_notoriety": [2, 5, 2], "weights_after_reputation": [2, 5, 2], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 59, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 59, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route_enc_1", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 59, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route_enc_1", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route_enc_1ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 59, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 59, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route_enc_2", "handler_payload": {"npc_outcome": "attack"}, "next_handler": "combat_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 59, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route_enc_2", "resolver_outcome": {"outcome": "destroyed", "resolver": "combat", "rounds": 2, "winner": "enemy"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 59, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 59, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route_enc_4", "handler_payload": {"npc_outcome": "attack"}, "next_handler": "combat_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 59, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route_enc_4", "resolver_outcome": {"outcome": "destroyed", "resolver": "combat", "rounds": 2, "winner": "enemy"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 59, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route_enc_4", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 59, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route_enc_5", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 59, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route_enc_5", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 59, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:58:auto_route_enc_5", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 59, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 760, "destination_id": "SYS-004-DST-01", "location_id": "SYS-004-DST-01", "system_id": "SYS-004"}, "turn_after": 59, "turn_before": 58, "version": "0.11.0"}
DESTINATION: Flux 1 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 1
PLAYER / SHIP INFO
  Credits: 760
  Fuel: 8/55
  Cargo manifest: {'basic_rations': 10, 'heritage_cuisine': 5, 'luxury_fresh_produce': 10, 'nutrient_paste': 5}
  Reputation: 50 band=0
  Heat: 20
  Notoriety: 0 band=-2
  Arrest state: free
  Warrants: []
  Location: SYS-004 / SYS-004-DST-01 / SYS-004-DST-01
  Turn: 59
  Active crew: []
  Active missions: []
ONGOING COSTS
  Insurance: 0
  Warehouse rental: 0
  Crew wages: 0
  Total recurring cost: 0
WAREHOUSE RENTALS
  none
DESTINATION: Flux 1 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 5
0) Back
1) SYS-004-DST-01-LOC-datanet type=datanet
2) SYS-004-DST-01-LOC-market type=market
3) SYS-004-DST-01-LOC-warehouse type=warehouse
Select location index: 2
Entered location: SYS-004-DST-01-LOC-market
MARKET PROFILE
  System: SYS-004
  Destination: SYS-004-DST-01
  Primary economy: research
  Active situations: none
  CHEMICALS: produced=[] consumed=['experimental_serums', 'medical_compounds'] neutral=[]
  DATA: produced=['media_packages', 'propaganda_feeds'] consumed=[] neutral=['ai_training_sets', 'encrypted_records']
  ENERGY: produced=['fusion_cores', 'standard_fuel'] consumed=[] neutral=[]
  MEDICINE: produced=['gene_therapy_kits', 'medical_nanites'] consumed=[] neutral=[]
  PARTS: produced=[] consumed=['cybernetic_implants', 'weaponized_autonomous_robots'] neutral=[]
MARKET SKUS
  ai_training_sets | AI Training Sets | buy=240 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_rations | basic_rations | buy=-- | sell=-- | cargo=10 | legality=-- | risk=--
  cybernetic_implants | Cybernetic Implants | buy=312 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  encrypted_records | Encrypted Records | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_serums | Experimental Serums | buy=252 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fusion_cores | Fusion Cores | buy=272 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=256 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heritage_cuisine | heritage_cuisine | buy=-- | sell=-- | cargo=5 | legality=-- | risk=--
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=-- | cargo=10 | legality=-- | risk=--
  media_packages | Media Packages | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_compounds | Medical Compounds | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nutrient_paste | nutrient_paste | buy=-- | sell=-- | cargo=5 | legality=-- | risk=--
  propaganda_feeds | Propaganda Feeds | buy=130 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=120 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=432 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 2
No market sell offers.
MARKET PROFILE
  System: SYS-004
  Destination: SYS-004-DST-01
  Primary economy: research
  Active situations: none
  CHEMICALS: produced=[] consumed=['experimental_serums', 'medical_compounds'] neutral=[]
  DATA: produced=['media_packages', 'propaganda_feeds'] consumed=[] neutral=['ai_training_sets', 'encrypted_records']
  ENERGY: produced=['fusion_cores', 'standard_fuel'] consumed=[] neutral=[]
  MEDICINE: produced=['gene_therapy_kits', 'medical_nanites'] consumed=[] neutral=[]
  PARTS: produced=[] consumed=['cybernetic_implants', 'weaponized_autonomous_robots'] neutral=[]
MARKET SKUS
  ai_training_sets | AI Training Sets | buy=240 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_rations | basic_rations | buy=-- | sell=-- | cargo=10 | legality=-- | risk=--
  cybernetic_implants | Cybernetic Implants | buy=312 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  encrypted_records | Encrypted Records | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_serums | Experimental Serums | buy=252 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fusion_cores | Fusion Cores | buy=272 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=256 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heritage_cuisine | heritage_cuisine | buy=-- | sell=-- | cargo=5 | legality=-- | risk=--
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=-- | cargo=10 | legality=-- | risk=--
  media_packages | Media Packages | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_compounds | Medical Compounds | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nutrient_paste | nutrient_paste | buy=-- | sell=-- | cargo=5 | legality=-- | risk=--
  propaganda_feeds | Propaganda Feeds | buy=130 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=120 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=432 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 2
No market sell offers.
MARKET PROFILE
  System: SYS-004
  Destination: SYS-004-DST-01
  Primary economy: research
  Active situations: none
  CHEMICALS: produced=[] consumed=['experimental_serums', 'medical_compounds'] neutral=[]
  DATA: produced=['media_packages', 'propaganda_feeds'] consumed=[] neutral=['ai_training_sets', 'encrypted_records']
  ENERGY: produced=['fusion_cores', 'standard_fuel'] consumed=[] neutral=[]
  MEDICINE: produced=['gene_therapy_kits', 'medical_nanites'] consumed=[] neutral=[]
  PARTS: produced=[] consumed=['cybernetic_implants', 'weaponized_autonomous_robots'] neutral=[]
MARKET SKUS
  ai_training_sets | AI Training Sets | buy=240 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_rations | basic_rations | buy=-- | sell=-- | cargo=10 | legality=-- | risk=--
  cybernetic_implants | Cybernetic Implants | buy=312 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  encrypted_records | Encrypted Records | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_serums | Experimental Serums | buy=252 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fusion_cores | Fusion Cores | buy=272 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=256 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heritage_cuisine | heritage_cuisine | buy=-- | sell=-- | cargo=5 | legality=-- | risk=--
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=-- | cargo=10 | legality=-- | risk=--
  media_packages | Media Packages | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_compounds | Medical Compounds | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nutrient_paste | nutrient_paste | buy=-- | sell=-- | cargo=5 | legality=-- | risk=--
  propaganda_feeds | Propaganda Feeds | buy=130 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=120 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=432 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 2
No market sell offers.
MARKET PROFILE
  System: SYS-004
  Destination: SYS-004-DST-01
  Primary economy: research
  Active situations: none
  CHEMICALS: produced=[] consumed=['experimental_serums', 'medical_compounds'] neutral=[]
  DATA: produced=['media_packages', 'propaganda_feeds'] consumed=[] neutral=['ai_training_sets', 'encrypted_records']
  ENERGY: produced=['fusion_cores', 'standard_fuel'] consumed=[] neutral=[]
  MEDICINE: produced=['gene_therapy_kits', 'medical_nanites'] consumed=[] neutral=[]
  PARTS: produced=[] consumed=['cybernetic_implants', 'weaponized_autonomous_robots'] neutral=[]
MARKET SKUS
  ai_training_sets | AI Training Sets | buy=240 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_rations | basic_rations | buy=-- | sell=-- | cargo=10 | legality=-- | risk=--
  cybernetic_implants | Cybernetic Implants | buy=312 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  encrypted_records | Encrypted Records | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_serums | Experimental Serums | buy=252 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fusion_cores | Fusion Cores | buy=272 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=256 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heritage_cuisine | heritage_cuisine | buy=-- | sell=-- | cargo=5 | legality=-- | risk=--
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=-- | cargo=10 | legality=-- | risk=--
  media_packages | Media Packages | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_compounds | Medical Compounds | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nutrient_paste | nutrient_paste | buy=-- | sell=-- | cargo=5 | legality=-- | risk=--
  propaganda_feeds | Propaganda Feeds | buy=130 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=120 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=432 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 3
Returned to destination: SYS-004-DST-01
DESTINATION: Flux 1 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 2
SYSTEM INFO
  Name: Flux
  ID: SYS-004
  Government: fascist
  Population: 4
  Coordinates: (-59.411901373532054, -48.98768474984742)
  Active situations: []
  Destinations: ['Flux 1', 'Flux 2', 'Flux 3', 'Flux 4']
  Active flags: ['discovery_hype']
  Reachable systems:
    SYS-001 Ion distance_ly=51.844 in_range=False
    SYS-002 Haven distance_ly=127.562 in_range=False
    SYS-003 Drift distance_ly=114.841 in_range=False
    SYS-005 Beacon distance_ly=99.303 in_range=False
DESTINATION: Flux 1 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 3
Current system: SYS-004 (Flux)
1) Inter-system warp
2) Intra-system destination travel
3) Back
Travel mode: 2
1) SYS-004-DST-01 Flux 1
2) SYS-004-DST-02 Flux 2
3) SYS-004-DST-03 Flux 3
4) SYS-004-DST-04 Flux 4
Select destination index: 2
[time_engine] action=time_advance_requested change=start_turn=59 days=1 reason=travel:TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route
[time_engine] action=galaxy_tick change=day=60
[time_engine] action=system_tick change=day=60
[time_engine] action=planet_station_tick change=day=60
[time_engine] action=location_tick change=day=60
[time_engine] action=npc_tick change=day=60
[time_engine] action=end_of_day_log change=day=60
Spawn gate cooldown check: system_id=SYS-004 current_day=60 cooldown_until=59 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=60 cooldown_until=59 reason=spawn_gate_roll_failed spawn_gate_roll=0.2507952931351969
[time_engine] action=time_advance_day_completed change=turn=60 hard_stop=None
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 59, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-004-DST-02", "target_system_id": "SYS-004", "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 59, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 8, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 59, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 60, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"outcome": null, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 60, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 5, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 60, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route_enc_0", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 60, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route_enc_0", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 60, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 60, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route_enc_1", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 60, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route_enc_1", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route_enc_1ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [2, 5, 1], "weights_after_notoriety": [2, 5, 1], "weights_after_reputation": [2, 5, 1], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 60, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 60, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route_enc_2", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 60, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route_enc_2", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": ["attack_plus_one_high_tr_delta"], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route_enc_2ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [2, 5, 2], "weights_after_notoriety": [2, 5, 2], "weights_after_reputation": [2, 5, 2], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 60, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 60, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route_enc_3", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 60, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route_enc_3", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 60, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route_enc_3", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 60, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route_enc_4", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 60, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route_enc_4", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route_enc_4ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 60, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:59:auto_route_enc_4", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 60, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 760, "destination_id": "SYS-004-DST-02", "location_id": "SYS-004-DST-02", "system_id": "SYS-004"}, "turn_after": 60, "turn_before": 59, "version": "0.11.0"}
DESTINATION: Flux 2 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 5
0) Back
1) SYS-004-DST-02-LOC-datanet type=datanet
2) SYS-004-DST-02-LOC-market type=market
3) SYS-004-DST-02-LOC-warehouse type=warehouse
4) SYS-004-DST-02-LOC-shipdock type=shipdock
5) SYS-004-DST-02-LOC-administration type=administration
Select location index: 2
Entered location: SYS-004-DST-02-LOC-market
MARKET PROFILE
  System: SYS-004
  Destination: SYS-004-DST-02
  Primary economy: military
  Active situations: none
  ENERGY: produced=[] consumed=['experimental_reactors', 'high_density_fuel', 'power_cells', 'standard_fuel'] neutral=[]
  FOOD: produced=[] consumed=['fresh_produce', 'nutrient_paste', 'protein_blocks', 'spice_wine'] neutral=['basic_rations', 'heritage_cuisine']
  MACHINERY: produced=['automated_factories', 'industrial_machinery', 'military_hardware', 'mining_equipment'] consumed=[] neutral=[]
  MEDICINE: produced=[] consumed=['cybernetic_medical_nanites', 'designer_drugs', 'gene_therapy_kits', 'medical_nanites'] neutral=[]
  METAL: produced=['aluminum_alloy', 'decorative_metals', 'steel_ingots', 'titanium_bars'] consumed=['precision_alloys'] neutral=[]
  ORE: produced=['copper_ore', 'nickel_ore', 'radioactive_ore', 'rare_earth_ore'] consumed=[] neutral=[]
  PARTS: produced=[] consumed=['autonomous_robots', 'servitor_units', 'synthetic_intelligences', 'weaponized_autonomous_robots'] neutral=['cybernetic_implants', 'electronic_components', 'mechanical_parts', 'weaponized_synthetic_intelligences']
  WEAPONS: produced=['biological_weapons', 'experimental_weapons', 'heavy_weapons', 'small_arms'] consumed=[] neutral=[]
MARKET SKUS
  aluminum_alloy | Aluminum Alloy | buy=136 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  automated_factories | Automated Factories | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  autonomous_robots | Autonomous Robots | buy=300 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_rations | Basic Rations | buy=100 | sell=100 | cargo=10 | legality=LEGAL | risk=Severe
  biological_weapons | Biological Weapons | buy=432 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  copper_ore | Copper Ore | buy=104 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_implants | Cybernetic Implants | buy=260 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_medical_nanites | Cybernetic Medical Nanites | buy=432 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  decorative_metals | Decorative Metals | buy=106 | sell=-- | cargo=0 | legality=RESTRICTED | risk=Severe
  designer_drugs | Designer Drugs | buy=360 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  electronic_components | Electronic Components | buy=180 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_reactors | Experimental Reactors | buy=504 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_weapons | Experimental Weapons | buy=374 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fresh_produce | Fresh Produce | buy=120 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=384 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heavy_weapons | Heavy Weapons | buy=307 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heritage_cuisine | Heritage Cuisine | buy=180 | sell=180 | cargo=5 | legality=LEGAL | risk=Severe
  high_density_fuel | High-Density Fuel | buy=168 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  industrial_machinery | Industrial Machinery | buy=208 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=72 | cargo=10 | legality=RESTRICTED | risk=Severe
  mechanical_parts | Mechanical Parts | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=432 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  military_hardware | Military Hardware | buy=403 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  mining_equipment | Mining Equipment | buy=224 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nickel_ore | Nickel Ore | buy=112 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nutrient_paste | Nutrient Paste | buy=110 | sell=110 | cargo=5 | legality=LEGAL | risk=Severe
  power_cells | Power Cells | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  precision_alloys | Precision Alloys | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  protein_blocks | Protein Blocks | buy=140 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  radioactive_ore | Radioactive Ore | buy=123 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  rare_earth_ore | Rare Earth Ore | buy=101 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  servitor_units | Servitor Units | buy=220 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  small_arms | Small Arms | buy=211 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  spice_wine | Spice Wine | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=180 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  steel_ingots | Steel Ingots | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  synthetic_intelligences | Synthetic Intelligences | buy=420 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  titanium_bars | Titanium Bars | buy=168 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=360 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_synthetic_intelligences | Weaponized Synthetic Intelligences | buy=504 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 2
1) basic_rations Basic Rations units=10 price=100 legality=LEGAL risk=Severe
2) heritage_cuisine Heritage Cuisine units=5 price=180 legality=LEGAL risk=Severe
3) luxury_fresh_produce luxury_fresh_produce units=10 price=72 legality=RESTRICTED risk=Severe
4) nutrient_paste Nutrient Paste units=5 price=110 legality=LEGAL risk=Severe
Select sell sku index: 1
Quantity: 10
{"active_encounter_count": 0, "command_type": "market_sell", "error": null, "events": [{"command_type": "market_sell", "detail": {"command_type": "market_sell"}, "stage": "start", "subsystem": "engine", "turn": 60, "world_seed": 12345}, {"command_type": "market_sell", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 60, "world_seed": 12345}, {"command_type": "market_sell", "detail": {"action": "sell", "cargo_after": 0, "credits_after": 1760, "credits_before": 760, "quantity": 10, "sku_id": "basic_rations", "total_gain": 1000, "unit_price": 100}, "stage": "market_trade", "subsystem": "market", "turn": 60, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 1760, "destination_id": "SYS-004-DST-02", "location_id": "SYS-004-DST-02-LOC-market", "system_id": "SYS-004"}, "turn_after": 60, "turn_before": 60, "version": "0.11.0"}
MARKET PROFILE
  System: SYS-004
  Destination: SYS-004-DST-02
  Primary economy: military
  Active situations: none
  ENERGY: produced=[] consumed=['experimental_reactors', 'high_density_fuel', 'power_cells', 'standard_fuel'] neutral=[]
  FOOD: produced=[] consumed=['fresh_produce', 'nutrient_paste', 'protein_blocks', 'spice_wine'] neutral=['basic_rations', 'heritage_cuisine']
  MACHINERY: produced=['automated_factories', 'industrial_machinery', 'military_hardware', 'mining_equipment'] consumed=[] neutral=[]
  MEDICINE: produced=[] consumed=['cybernetic_medical_nanites', 'designer_drugs', 'gene_therapy_kits', 'medical_nanites'] neutral=[]
  METAL: produced=['aluminum_alloy', 'decorative_metals', 'steel_ingots', 'titanium_bars'] consumed=['precision_alloys'] neutral=[]
  ORE: produced=['copper_ore', 'nickel_ore', 'radioactive_ore', 'rare_earth_ore'] consumed=[] neutral=[]
  PARTS: produced=[] consumed=['autonomous_robots', 'servitor_units', 'synthetic_intelligences', 'weaponized_autonomous_robots'] neutral=['cybernetic_implants', 'electronic_components', 'mechanical_parts', 'weaponized_synthetic_intelligences']
  WEAPONS: produced=['biological_weapons', 'experimental_weapons', 'heavy_weapons', 'small_arms'] consumed=[] neutral=[]
MARKET SKUS
  aluminum_alloy | Aluminum Alloy | buy=136 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  automated_factories | Automated Factories | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  autonomous_robots | Autonomous Robots | buy=300 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_rations | Basic Rations | buy=100 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  biological_weapons | Biological Weapons | buy=432 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  copper_ore | Copper Ore | buy=104 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_implants | Cybernetic Implants | buy=260 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_medical_nanites | Cybernetic Medical Nanites | buy=432 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  decorative_metals | Decorative Metals | buy=106 | sell=-- | cargo=0 | legality=RESTRICTED | risk=Severe
  designer_drugs | Designer Drugs | buy=360 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  electronic_components | Electronic Components | buy=180 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_reactors | Experimental Reactors | buy=504 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_weapons | Experimental Weapons | buy=374 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fresh_produce | Fresh Produce | buy=120 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=384 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heavy_weapons | Heavy Weapons | buy=307 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heritage_cuisine | Heritage Cuisine | buy=180 | sell=180 | cargo=5 | legality=LEGAL | risk=Severe
  high_density_fuel | High-Density Fuel | buy=168 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  industrial_machinery | Industrial Machinery | buy=208 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=72 | cargo=10 | legality=RESTRICTED | risk=Severe
  mechanical_parts | Mechanical Parts | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=432 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  military_hardware | Military Hardware | buy=403 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  mining_equipment | Mining Equipment | buy=224 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nickel_ore | Nickel Ore | buy=112 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nutrient_paste | Nutrient Paste | buy=110 | sell=110 | cargo=5 | legality=LEGAL | risk=Severe
  power_cells | Power Cells | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  precision_alloys | Precision Alloys | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  protein_blocks | Protein Blocks | buy=140 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  radioactive_ore | Radioactive Ore | buy=123 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  rare_earth_ore | Rare Earth Ore | buy=101 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  servitor_units | Servitor Units | buy=220 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  small_arms | Small Arms | buy=211 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  spice_wine | Spice Wine | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=180 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  steel_ingots | Steel Ingots | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  synthetic_intelligences | Synthetic Intelligences | buy=420 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  titanium_bars | Titanium Bars | buy=168 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=360 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_synthetic_intelligences | Weaponized Synthetic Intelligences | buy=504 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 2
1) heritage_cuisine Heritage Cuisine units=5 price=180 legality=LEGAL risk=Severe
2) luxury_fresh_produce luxury_fresh_produce units=10 price=72 legality=RESTRICTED risk=Severe
3) nutrient_paste Nutrient Paste units=5 price=110 legality=LEGAL risk=Severe
Select sell sku index: 3
Quantity: 5
{"active_encounter_count": 0, "command_type": "market_sell", "error": null, "events": [{"command_type": "market_sell", "detail": {"command_type": "market_sell"}, "stage": "start", "subsystem": "engine", "turn": 60, "world_seed": 12345}, {"command_type": "market_sell", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 60, "world_seed": 12345}, {"command_type": "market_sell", "detail": {"action": "sell", "cargo_after": 0, "credits_after": 2310, "credits_before": 1760, "quantity": 5, "sku_id": "nutrient_paste", "total_gain": 550, "unit_price": 110}, "stage": "market_trade", "subsystem": "market", "turn": 60, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 2310, "destination_id": "SYS-004-DST-02", "location_id": "SYS-004-DST-02-LOC-market", "system_id": "SYS-004"}, "turn_after": 60, "turn_before": 60, "version": "0.11.0"}
MARKET PROFILE
  System: SYS-004
  Destination: SYS-004-DST-02
  Primary economy: military
  Active situations: none
  ENERGY: produced=[] consumed=['experimental_reactors', 'high_density_fuel', 'power_cells', 'standard_fuel'] neutral=[]
  FOOD: produced=[] consumed=['fresh_produce', 'nutrient_paste', 'protein_blocks', 'spice_wine'] neutral=['basic_rations', 'heritage_cuisine']
  MACHINERY: produced=['automated_factories', 'industrial_machinery', 'military_hardware', 'mining_equipment'] consumed=[] neutral=[]
  MEDICINE: produced=[] consumed=['cybernetic_medical_nanites', 'designer_drugs', 'gene_therapy_kits', 'medical_nanites'] neutral=[]
  METAL: produced=['aluminum_alloy', 'decorative_metals', 'steel_ingots', 'titanium_bars'] consumed=['precision_alloys'] neutral=[]
  ORE: produced=['copper_ore', 'nickel_ore', 'radioactive_ore', 'rare_earth_ore'] consumed=[] neutral=[]
  PARTS: produced=[] consumed=['autonomous_robots', 'servitor_units', 'synthetic_intelligences', 'weaponized_autonomous_robots'] neutral=['cybernetic_implants', 'electronic_components', 'mechanical_parts', 'weaponized_synthetic_intelligences']
  WEAPONS: produced=['biological_weapons', 'experimental_weapons', 'heavy_weapons', 'small_arms'] consumed=[] neutral=[]
MARKET SKUS
  aluminum_alloy | Aluminum Alloy | buy=136 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  automated_factories | Automated Factories | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  autonomous_robots | Autonomous Robots | buy=300 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_rations | Basic Rations | buy=100 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  biological_weapons | Biological Weapons | buy=432 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  copper_ore | Copper Ore | buy=104 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_implants | Cybernetic Implants | buy=260 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_medical_nanites | Cybernetic Medical Nanites | buy=432 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  decorative_metals | Decorative Metals | buy=106 | sell=-- | cargo=0 | legality=RESTRICTED | risk=Severe
  designer_drugs | Designer Drugs | buy=360 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  electronic_components | Electronic Components | buy=180 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_reactors | Experimental Reactors | buy=504 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_weapons | Experimental Weapons | buy=374 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fresh_produce | Fresh Produce | buy=120 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=384 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heavy_weapons | Heavy Weapons | buy=307 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heritage_cuisine | Heritage Cuisine | buy=180 | sell=180 | cargo=5 | legality=LEGAL | risk=Severe
  high_density_fuel | High-Density Fuel | buy=168 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  industrial_machinery | Industrial Machinery | buy=208 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=72 | cargo=10 | legality=RESTRICTED | risk=Severe
  mechanical_parts | Mechanical Parts | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=432 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  military_hardware | Military Hardware | buy=403 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  mining_equipment | Mining Equipment | buy=224 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nickel_ore | Nickel Ore | buy=112 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nutrient_paste | Nutrient Paste | buy=110 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  power_cells | Power Cells | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  precision_alloys | Precision Alloys | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  protein_blocks | Protein Blocks | buy=140 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  radioactive_ore | Radioactive Ore | buy=123 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  rare_earth_ore | Rare Earth Ore | buy=101 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  servitor_units | Servitor Units | buy=220 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  small_arms | Small Arms | buy=211 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  spice_wine | Spice Wine | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=180 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  steel_ingots | Steel Ingots | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  synthetic_intelligences | Synthetic Intelligences | buy=420 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  titanium_bars | Titanium Bars | buy=168 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=360 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_synthetic_intelligences | Weaponized Synthetic Intelligences | buy=504 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 3
Returned to destination: SYS-004-DST-02
DESTINATION: Flux 2 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 4
1) customs_inspection Customs Inspection
2) refuel Refuel
3) Back
Select destination action index: 2
requested_units: 55
{"active_encounter_count": 0, "command_type": "destination_action", "error": null, "events": [{"command_type": "destination_action", "detail": {"command_type": "destination_action"}, "stage": "start", "subsystem": "engine", "turn": 60, "world_seed": 12345}, {"command_type": "destination_action", "detail": {"action_id": "refuel", "result": {"credits": 2075, "current_fuel": 55, "ok": true, "reason": "ok", "total_cost": 235, "units_purchased": 47}, "result_summary": {"credits_after": 2075, "credits_before": 2310, "fuel_after": 55, "fuel_before": 8, "reason": "ok", "result_ok": true, "total_cost": 235, "unit_price": 5, "units_purchased": 47}}, "stage": "destination_action", "subsystem": "interaction_layer", "turn": 60, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 2075, "destination_id": "SYS-004-DST-02", "location_id": "SYS-004-DST-02", "system_id": "SYS-004"}, "turn_after": 60, "turn_before": 60, "version": "0.11.0"}
1) customs_inspection Customs Inspection
2) refuel Refuel
3) Back
Select destination action index: 3
DESTINATION: Flux 2 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 1
PLAYER / SHIP INFO
  Credits: 2075
  Fuel: 55/55
  Cargo manifest: {'heritage_cuisine': 5, 'luxury_fresh_produce': 10}
  Reputation: 50 band=0
  Heat: 25
  Notoriety: 0 band=-2
  Arrest state: free
  Warrants: []
  Location: SYS-004 / SYS-004-DST-02 / SYS-004-DST-02
  Turn: 60
  Active crew: []
  Active missions: []
ONGOING COSTS
  Insurance: 0
  Warehouse rental: 0
  Crew wages: 0
  Total recurring cost: 0
WAREHOUSE RENTALS
  none
DESTINATION: Flux 2 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 3
Current system: SYS-004 (Flux)
1) Inter-system warp
2) Intra-system destination travel
3) Back
Travel mode: 1
1) SYS-001 Ion distance_ly=51.844 government=democracy population=3 destinations=4 active_situations=[]
Select target system index: 1
[time_engine] action=time_advance_requested change=start_turn=60 days=10 reason=travel:TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route
[time_engine] action=galaxy_tick change=day=61
[time_engine] action=system_tick change=day=61
[time_engine] action=planet_station_tick change=day=61
[time_engine] action=location_tick change=day=61
[time_engine] action=npc_tick change=day=61
[time_engine] action=end_of_day_log change=day=61
Spawn gate cooldown check: system_id=SYS-001 current_day=61 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=61 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.642729847120708
[time_engine] action=time_advance_day_completed change=turn=61 hard_stop=None
[time_engine] action=galaxy_tick change=day=62
[time_engine] action=system_tick change=day=62
[time_engine] action=planet_station_tick change=day=62
[time_engine] action=location_tick change=day=62
[time_engine] action=npc_tick change=day=62
[time_engine] action=end_of_day_log change=day=62
Spawn gate cooldown check: system_id=SYS-001 current_day=62 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=62 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.9372648185368946
[time_engine] action=time_advance_day_completed change=turn=62 hard_stop=None
[time_engine] action=galaxy_tick change=day=63
[time_engine] action=system_tick change=day=63
[time_engine] action=planet_station_tick change=day=63
[time_engine] action=location_tick change=day=63
[time_engine] action=npc_tick change=day=63
[time_engine] action=end_of_day_log change=day=63
Spawn gate cooldown check: system_id=SYS-001 current_day=63 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=63 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.9430298617264846
[time_engine] action=time_advance_day_completed change=turn=63 hard_stop=None
[time_engine] action=galaxy_tick change=day=64
[time_engine] action=system_tick change=day=64
[time_engine] action=planet_station_tick change=day=64
[time_engine] action=location_tick change=day=64
[time_engine] action=npc_tick change=day=64
[time_engine] action=end_of_day_log change=day=64
Spawn gate cooldown check: system_id=SYS-001 current_day=64 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=64 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.5765253689907425
[time_engine] action=time_advance_day_completed change=turn=64 hard_stop=None
[time_engine] action=galaxy_tick change=day=65
[time_engine] action=system_tick change=day=65
[time_engine] action=planet_station_tick change=day=65
[time_engine] action=location_tick change=day=65
[time_engine] action=npc_tick change=day=65
[time_engine] action=end_of_day_log change=day=65
Spawn gate cooldown check: system_id=SYS-001 current_day=65 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=65 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.5149949674910665
[time_engine] action=time_advance_day_completed change=turn=65 hard_stop=None
[time_engine] action=galaxy_tick change=day=66
[time_engine] action=system_tick change=day=66
[time_engine] action=planet_station_tick change=day=66
[time_engine] action=location_tick change=day=66
[time_engine] action=npc_tick change=day=66
[time_engine] action=end_of_day_log change=day=66
Spawn gate cooldown check: system_id=SYS-001 current_day=66 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=66 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.9923995220309269
[time_engine] action=time_advance_day_completed change=turn=66 hard_stop=None
[time_engine] action=galaxy_tick change=day=67
[time_engine] action=system_tick change=day=67
[time_engine] action=planet_station_tick change=day=67
[time_engine] action=location_tick change=day=67
[time_engine] action=npc_tick change=day=67
[time_engine] action=end_of_day_log change=day=67
Spawn gate cooldown check: system_id=SYS-001 current_day=67 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=67 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.10425135157321797
[time_engine] action=time_advance_day_completed change=turn=67 hard_stop=None
[time_engine] action=galaxy_tick change=day=68
[time_engine] action=system_tick change=day=68
[time_engine] action=planet_station_tick change=day=68
[time_engine] action=location_tick change=day=68
[time_engine] action=npc_tick change=day=68
[time_engine] action=end_of_day_log change=day=68
Spawn gate cooldown check: system_id=SYS-001 current_day=68 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=68 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.5349441580292263
[time_engine] action=time_advance_day_completed change=turn=68 hard_stop=None
[time_engine] action=galaxy_tick change=day=69
[time_engine] action=system_tick change=day=69
[time_engine] action=planet_station_tick change=day=69
[time_engine] action=location_tick change=day=69
[time_engine] action=npc_tick change=day=69
[time_engine] action=end_of_day_log change=day=69
Spawn gate cooldown check: system_id=SYS-001 current_day=69 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=69 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.44483274231249437
[time_engine] action=time_advance_day_completed change=turn=69 hard_stop=None
[time_engine] action=galaxy_tick change=day=70
[time_engine] action=system_tick change=day=70
[time_engine] action=planet_station_tick change=day=70
[time_engine] action=location_tick change=day=70
[time_engine] action=npc_tick change=day=70
[time_engine] action=end_of_day_log change=day=70
Spawn gate cooldown check: system_id=SYS-001 current_day=70 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=70 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.8171737477200718
[time_engine] action=time_advance_day_completed change=turn=70 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=70 days=10 reason=travel:TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route
[time_engine] action=galaxy_tick change=day=71
[time_engine] action=system_tick change=day=71
[time_engine] action=planet_station_tick change=day=71
[time_engine] action=location_tick change=day=71
[time_engine] action=npc_tick change=day=71
[time_engine] action=end_of_day_log change=day=71
Spawn gate cooldown check: system_id=SYS-001 current_day=71 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=71 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.9892110745854691
[time_engine] action=time_advance_day_completed change=turn=71 hard_stop=None
[time_engine] action=galaxy_tick change=day=72
[time_engine] action=system_tick change=day=72
[time_engine] action=planet_station_tick change=day=72
[time_engine] action=location_tick change=day=72
[time_engine] action=npc_tick change=day=72
[time_engine] action=end_of_day_log change=day=72
Spawn gate cooldown check: system_id=SYS-001 current_day=72 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate type+tier selected: system_id=SYS-001 current_day=72 selected_type=situation selected_tier=3 spawn_type_roll=0.6984162700221205 severity_roll=0.7214226001157366
Spawn gate candidate filter: system_id=SYS-001 selected_type=situation selected_tier=3 candidates_found=8
Situation added: economic_recession system=SYS-001 scope=system
Spawn gate cooldown set: system_id=SYS-001 current_day=72 cooldown_until=77 generated_any=true reason=spawn_gate_generation
[time_engine] action=time_advance_day_completed change=turn=72 hard_stop=None
[time_engine] action=galaxy_tick change=day=73
[time_engine] action=system_tick change=day=73
[time_engine] action=planet_station_tick change=day=73
[time_engine] action=location_tick change=day=73
[time_engine] action=npc_tick change=day=73
[time_engine] action=end_of_day_log change=day=73
Spawn gate cooldown check: system_id=SYS-001 current_day=73 cooldown_until=77 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=73 hard_stop=None
[time_engine] action=galaxy_tick change=day=74
[time_engine] action=system_tick change=day=74
[time_engine] action=planet_station_tick change=day=74
[time_engine] action=location_tick change=day=74
[time_engine] action=npc_tick change=day=74
[time_engine] action=end_of_day_log change=day=74
Spawn gate cooldown check: system_id=SYS-001 current_day=74 cooldown_until=77 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=74 hard_stop=None
[time_engine] action=galaxy_tick change=day=75
[time_engine] action=system_tick change=day=75
[time_engine] action=planet_station_tick change=day=75
[time_engine] action=location_tick change=day=75
[time_engine] action=npc_tick change=day=75
[time_engine] action=end_of_day_log change=day=75
Spawn gate cooldown check: system_id=SYS-001 current_day=75 cooldown_until=77 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=75 hard_stop=None
[time_engine] action=galaxy_tick change=day=76
[time_engine] action=system_tick change=day=76
[time_engine] action=planet_station_tick change=day=76
[time_engine] action=location_tick change=day=76
[time_engine] action=npc_tick change=day=76
[time_engine] action=end_of_day_log change=day=76
Spawn gate cooldown check: system_id=SYS-001 current_day=76 cooldown_until=77 skipped=true reason=cooldown_active
Situation expired: economic_recession system=SYS-001
[time_engine] action=time_advance_day_completed change=turn=76 hard_stop=None
[time_engine] action=galaxy_tick change=day=77
[time_engine] action=system_tick change=day=77
[time_engine] action=planet_station_tick change=day=77
[time_engine] action=location_tick change=day=77
[time_engine] action=npc_tick change=day=77
[time_engine] action=end_of_day_log change=day=77
Spawn gate cooldown check: system_id=SYS-001 current_day=77 cooldown_until=77 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=77 hard_stop=None
[time_engine] action=galaxy_tick change=day=78
[time_engine] action=system_tick change=day=78
[time_engine] action=planet_station_tick change=day=78
[time_engine] action=location_tick change=day=78
[time_engine] action=npc_tick change=day=78
[time_engine] action=end_of_day_log change=day=78
Spawn gate cooldown check: system_id=SYS-001 current_day=78 cooldown_until=77 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=78 cooldown_until=77 reason=spawn_gate_roll_failed spawn_gate_roll=0.18574705385623624
[time_engine] action=time_advance_day_completed change=turn=78 hard_stop=None
[time_engine] action=galaxy_tick change=day=79
[time_engine] action=system_tick change=day=79
[time_engine] action=planet_station_tick change=day=79
[time_engine] action=location_tick change=day=79
[time_engine] action=npc_tick change=day=79
[time_engine] action=end_of_day_log change=day=79
Spawn gate cooldown check: system_id=SYS-001 current_day=79 cooldown_until=77 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=79 cooldown_until=77 reason=spawn_gate_roll_failed spawn_gate_roll=0.6479826520626323
[time_engine] action=time_advance_day_completed change=turn=79 hard_stop=None
[time_engine] action=galaxy_tick change=day=80
[time_engine] action=system_tick change=day=80
[time_engine] action=planet_station_tick change=day=80
[time_engine] action=location_tick change=day=80
[time_engine] action=npc_tick change=day=80
[time_engine] action=end_of_day_log change=day=80
Spawn gate cooldown check: system_id=SYS-001 current_day=80 cooldown_until=77 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=80 cooldown_until=77 reason=spawn_gate_roll_failed spawn_gate_roll=0.6472685014427421
[time_engine] action=time_advance_day_completed change=turn=80 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=80 days=10 reason=travel:TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route
[time_engine] action=galaxy_tick change=day=81
[time_engine] action=system_tick change=day=81
[time_engine] action=planet_station_tick change=day=81
[time_engine] action=location_tick change=day=81
[time_engine] action=npc_tick change=day=81
[time_engine] action=end_of_day_log change=day=81
Spawn gate cooldown check: system_id=SYS-001 current_day=81 cooldown_until=77 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=81 cooldown_until=77 reason=spawn_gate_roll_failed spawn_gate_roll=0.967059779872699
[time_engine] action=time_advance_day_completed change=turn=81 hard_stop=None
[time_engine] action=galaxy_tick change=day=82
[time_engine] action=system_tick change=day=82
[time_engine] action=planet_station_tick change=day=82
[time_engine] action=location_tick change=day=82
[time_engine] action=npc_tick change=day=82
[time_engine] action=end_of_day_log change=day=82
Spawn gate cooldown check: system_id=SYS-001 current_day=82 cooldown_until=77 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=82 cooldown_until=77 reason=spawn_gate_roll_failed spawn_gate_roll=0.6491333637709701
[time_engine] action=time_advance_day_completed change=turn=82 hard_stop=None
[time_engine] action=galaxy_tick change=day=83
[time_engine] action=system_tick change=day=83
[time_engine] action=planet_station_tick change=day=83
[time_engine] action=location_tick change=day=83
[time_engine] action=npc_tick change=day=83
[time_engine] action=end_of_day_log change=day=83
Spawn gate cooldown check: system_id=SYS-001 current_day=83 cooldown_until=77 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=83 cooldown_until=77 reason=spawn_gate_roll_failed spawn_gate_roll=0.10034173399589175
[time_engine] action=time_advance_day_completed change=turn=83 hard_stop=None
[time_engine] action=galaxy_tick change=day=84
[time_engine] action=system_tick change=day=84
[time_engine] action=planet_station_tick change=day=84
[time_engine] action=location_tick change=day=84
[time_engine] action=npc_tick change=day=84
[time_engine] action=end_of_day_log change=day=84
Spawn gate cooldown check: system_id=SYS-001 current_day=84 cooldown_until=77 skipped=false reason=cooldown_clear
Spawn gate type+tier selected: system_id=SYS-001 current_day=84 selected_type=situation selected_tier=4 spawn_type_roll=0.14993482262257163 severity_roll=0.9251110268090194
Spawn gate candidate filter: system_id=SYS-001 selected_type=situation selected_tier=4 candidates_found=0
Spawn gate cooldown not set: system_id=SYS-001 current_day=84 cooldown_until=77 reason=no_generation_created selected_type=situation selected_tier=4 candidates_found=0
[time_engine] action=time_advance_day_completed change=turn=84 hard_stop=None
[time_engine] action=galaxy_tick change=day=85
[time_engine] action=system_tick change=day=85
[time_engine] action=planet_station_tick change=day=85
[time_engine] action=location_tick change=day=85
[time_engine] action=npc_tick change=day=85
[time_engine] action=end_of_day_log change=day=85
Spawn gate cooldown check: system_id=SYS-001 current_day=85 cooldown_until=77 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=85 cooldown_until=77 reason=spawn_gate_roll_failed spawn_gate_roll=0.5202316714283028
[time_engine] action=time_advance_day_completed change=turn=85 hard_stop=None
[time_engine] action=galaxy_tick change=day=86
[time_engine] action=system_tick change=day=86
[time_engine] action=planet_station_tick change=day=86
[time_engine] action=location_tick change=day=86
[time_engine] action=npc_tick change=day=86
[time_engine] action=end_of_day_log change=day=86
Spawn gate cooldown check: system_id=SYS-001 current_day=86 cooldown_until=77 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=86 cooldown_until=77 reason=spawn_gate_roll_failed spawn_gate_roll=0.5189365139434534
[time_engine] action=time_advance_day_completed change=turn=86 hard_stop=None
[time_engine] action=galaxy_tick change=day=87
[time_engine] action=system_tick change=day=87
[time_engine] action=planet_station_tick change=day=87
[time_engine] action=location_tick change=day=87
[time_engine] action=npc_tick change=day=87
[time_engine] action=end_of_day_log change=day=87
Spawn gate cooldown check: system_id=SYS-001 current_day=87 cooldown_until=77 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=87 cooldown_until=77 reason=spawn_gate_roll_failed spawn_gate_roll=0.4039960274141239
[time_engine] action=time_advance_day_completed change=turn=87 hard_stop=None
[time_engine] action=galaxy_tick change=day=88
[time_engine] action=system_tick change=day=88
[time_engine] action=planet_station_tick change=day=88
[time_engine] action=location_tick change=day=88
[time_engine] action=npc_tick change=day=88
[time_engine] action=end_of_day_log change=day=88
Spawn gate cooldown check: system_id=SYS-001 current_day=88 cooldown_until=77 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=88 cooldown_until=77 reason=spawn_gate_roll_failed spawn_gate_roll=0.12814632696230976
[time_engine] action=time_advance_day_completed change=turn=88 hard_stop=None
[time_engine] action=galaxy_tick change=day=89
[time_engine] action=system_tick change=day=89
[time_engine] action=planet_station_tick change=day=89
[time_engine] action=location_tick change=day=89
[time_engine] action=npc_tick change=day=89
[time_engine] action=end_of_day_log change=day=89
Spawn gate cooldown check: system_id=SYS-001 current_day=89 cooldown_until=77 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=89 cooldown_until=77 reason=spawn_gate_roll_failed spawn_gate_roll=0.657757353195506
[time_engine] action=time_advance_day_completed change=turn=89 hard_stop=None
[time_engine] action=galaxy_tick change=day=90
[time_engine] action=system_tick change=day=90
[time_engine] action=planet_station_tick change=day=90
[time_engine] action=location_tick change=day=90
[time_engine] action=npc_tick change=day=90
[time_engine] action=end_of_day_log change=day=90
Spawn gate cooldown check: system_id=SYS-001 current_day=90 cooldown_until=77 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=90 cooldown_until=77 reason=spawn_gate_roll_failed spawn_gate_roll=0.8789145274877052
[time_engine] action=time_advance_day_completed change=turn=90 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=90 days=10 reason=travel:TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route
[time_engine] action=galaxy_tick change=day=91
[time_engine] action=system_tick change=day=91
[time_engine] action=planet_station_tick change=day=91
[time_engine] action=location_tick change=day=91
[time_engine] action=npc_tick change=day=91
[time_engine] action=end_of_day_log change=day=91
Spawn gate cooldown check: system_id=SYS-001 current_day=91 cooldown_until=77 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=91 cooldown_until=77 reason=spawn_gate_roll_failed spawn_gate_roll=0.7126504068542738
[time_engine] action=time_advance_day_completed change=turn=91 hard_stop=None
[time_engine] action=galaxy_tick change=day=92
[time_engine] action=system_tick change=day=92
[time_engine] action=planet_station_tick change=day=92
[time_engine] action=location_tick change=day=92
[time_engine] action=npc_tick change=day=92
[time_engine] action=end_of_day_log change=day=92
Spawn gate cooldown check: system_id=SYS-001 current_day=92 cooldown_until=77 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=92 cooldown_until=77 reason=spawn_gate_roll_failed spawn_gate_roll=0.1177366275454852
[time_engine] action=time_advance_day_completed change=turn=92 hard_stop=None
[time_engine] action=galaxy_tick change=day=93
[time_engine] action=system_tick change=day=93
[time_engine] action=planet_station_tick change=day=93
[time_engine] action=location_tick change=day=93
[time_engine] action=npc_tick change=day=93
[time_engine] action=end_of_day_log change=day=93
Spawn gate cooldown check: system_id=SYS-001 current_day=93 cooldown_until=77 skipped=false reason=cooldown_clear
Spawn gate type+tier selected: system_id=SYS-001 current_day=93 selected_type=situation selected_tier=1 spawn_type_roll=0.1161497576128745 severity_roll=0.0200163030517031
Spawn gate candidate filter: system_id=SYS-001 selected_type=situation selected_tier=1 candidates_found=1
Situation added: cultural_festival system=SYS-001 scope=destination
Spawn gate cooldown set: system_id=SYS-001 current_day=93 cooldown_until=98 generated_any=true reason=spawn_gate_generation
[time_engine] action=time_advance_day_completed change=turn=93 hard_stop=None
[time_engine] action=galaxy_tick change=day=94
[time_engine] action=system_tick change=day=94
[time_engine] action=planet_station_tick change=day=94
[time_engine] action=location_tick change=day=94
[time_engine] action=npc_tick change=day=94
[time_engine] action=end_of_day_log change=day=94
Spawn gate cooldown check: system_id=SYS-001 current_day=94 cooldown_until=98 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=94 hard_stop=None
[time_engine] action=galaxy_tick change=day=95
[time_engine] action=system_tick change=day=95
[time_engine] action=planet_station_tick change=day=95
[time_engine] action=location_tick change=day=95
[time_engine] action=npc_tick change=day=95
[time_engine] action=end_of_day_log change=day=95
Spawn gate cooldown check: system_id=SYS-001 current_day=95 cooldown_until=98 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=95 hard_stop=None
[time_engine] action=galaxy_tick change=day=96
[time_engine] action=system_tick change=day=96
[time_engine] action=planet_station_tick change=day=96
[time_engine] action=location_tick change=day=96
[time_engine] action=npc_tick change=day=96
[time_engine] action=end_of_day_log change=day=96
Spawn gate cooldown check: system_id=SYS-001 current_day=96 cooldown_until=98 skipped=true reason=cooldown_active
Situation expired: cultural_festival system=SYS-001
[time_engine] action=time_advance_day_completed change=turn=96 hard_stop=None
[time_engine] action=galaxy_tick change=day=97
[time_engine] action=system_tick change=day=97
[time_engine] action=planet_station_tick change=day=97
[time_engine] action=location_tick change=day=97
[time_engine] action=npc_tick change=day=97
[time_engine] action=end_of_day_log change=day=97
Spawn gate cooldown check: system_id=SYS-001 current_day=97 cooldown_until=98 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=97 hard_stop=None
[time_engine] action=galaxy_tick change=day=98
[time_engine] action=system_tick change=day=98
[time_engine] action=planet_station_tick change=day=98
[time_engine] action=location_tick change=day=98
[time_engine] action=npc_tick change=day=98
[time_engine] action=end_of_day_log change=day=98
Spawn gate cooldown check: system_id=SYS-001 current_day=98 cooldown_until=98 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=98 hard_stop=None
[time_engine] action=galaxy_tick change=day=99
[time_engine] action=system_tick change=day=99
[time_engine] action=planet_station_tick change=day=99
[time_engine] action=location_tick change=day=99
[time_engine] action=npc_tick change=day=99
[time_engine] action=end_of_day_log change=day=99
Spawn gate cooldown check: system_id=SYS-001 current_day=99 cooldown_until=98 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=99 cooldown_until=98 reason=spawn_gate_roll_failed spawn_gate_roll=0.23423094612445028
[time_engine] action=time_advance_day_completed change=turn=99 hard_stop=None
[time_engine] action=galaxy_tick change=day=100
[time_engine] action=system_tick change=day=100
[time_engine] action=planet_station_tick change=day=100
[time_engine] action=location_tick change=day=100
[time_engine] action=npc_tick change=day=100
[time_engine] action=end_of_day_log change=day=100
Spawn gate cooldown check: system_id=SYS-001 current_day=100 cooldown_until=98 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=100 cooldown_until=98 reason=spawn_gate_roll_failed spawn_gate_roll=0.5385479192146897
[time_engine] action=time_advance_day_completed change=turn=100 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=100 days=10 reason=travel:TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route
[time_engine] action=galaxy_tick change=day=101
[time_engine] action=system_tick change=day=101
[time_engine] action=planet_station_tick change=day=101
[time_engine] action=location_tick change=day=101
[time_engine] action=npc_tick change=day=101
[time_engine] action=end_of_day_log change=day=101
Spawn gate cooldown check: system_id=SYS-001 current_day=101 cooldown_until=98 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=101 cooldown_until=98 reason=spawn_gate_roll_failed spawn_gate_roll=0.6761869050522236
[time_engine] action=time_advance_day_completed change=turn=101 hard_stop=None
[time_engine] action=galaxy_tick change=day=102
[time_engine] action=system_tick change=day=102
[time_engine] action=planet_station_tick change=day=102
[time_engine] action=location_tick change=day=102
[time_engine] action=npc_tick change=day=102
[time_engine] action=end_of_day_log change=day=102
Spawn gate cooldown check: system_id=SYS-001 current_day=102 cooldown_until=98 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=102 cooldown_until=98 reason=spawn_gate_roll_failed spawn_gate_roll=0.25883271953144893
[time_engine] action=time_advance_day_completed change=turn=102 hard_stop=None
[time_engine] action=galaxy_tick change=day=103
[time_engine] action=system_tick change=day=103
[time_engine] action=planet_station_tick change=day=103
[time_engine] action=location_tick change=day=103
[time_engine] action=npc_tick change=day=103
[time_engine] action=end_of_day_log change=day=103
Spawn gate cooldown check: system_id=SYS-001 current_day=103 cooldown_until=98 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=103 cooldown_until=98 reason=spawn_gate_roll_failed spawn_gate_roll=0.8853791051412484
[time_engine] action=time_advance_day_completed change=turn=103 hard_stop=None
[time_engine] action=galaxy_tick change=day=104
[time_engine] action=system_tick change=day=104
[time_engine] action=planet_station_tick change=day=104
[time_engine] action=location_tick change=day=104
[time_engine] action=npc_tick change=day=104
[time_engine] action=end_of_day_log change=day=104
Spawn gate cooldown check: system_id=SYS-001 current_day=104 cooldown_until=98 skipped=false reason=cooldown_clear
Spawn gate type+tier selected: system_id=SYS-001 current_day=104 selected_type=situation selected_tier=3 spawn_type_roll=0.4689757391673611 severity_roll=0.7588484583887429
Spawn gate candidate filter: system_id=SYS-001 selected_type=situation selected_tier=3 candidates_found=8
Situation added: civil_unrest system=SYS-001 scope=system
Spawn gate cooldown set: system_id=SYS-001 current_day=104 cooldown_until=109 generated_any=true reason=spawn_gate_generation
[time_engine] action=time_advance_day_completed change=turn=104 hard_stop=None
[time_engine] action=galaxy_tick change=day=105
[time_engine] action=system_tick change=day=105
[time_engine] action=planet_station_tick change=day=105
[time_engine] action=location_tick change=day=105
[time_engine] action=npc_tick change=day=105
[time_engine] action=end_of_day_log change=day=105
Spawn gate cooldown check: system_id=SYS-001 current_day=105 cooldown_until=109 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=105 hard_stop=None
[time_engine] action=galaxy_tick change=day=106
[time_engine] action=system_tick change=day=106
[time_engine] action=planet_station_tick change=day=106
[time_engine] action=location_tick change=day=106
[time_engine] action=npc_tick change=day=106
[time_engine] action=end_of_day_log change=day=106
Spawn gate cooldown check: system_id=SYS-001 current_day=106 cooldown_until=109 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=106 hard_stop=None
[time_engine] action=galaxy_tick change=day=107
[time_engine] action=system_tick change=day=107
[time_engine] action=planet_station_tick change=day=107
[time_engine] action=location_tick change=day=107
[time_engine] action=npc_tick change=day=107
[time_engine] action=end_of_day_log change=day=107
Spawn gate cooldown check: system_id=SYS-001 current_day=107 cooldown_until=109 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=107 hard_stop=None
[time_engine] action=galaxy_tick change=day=108
[time_engine] action=system_tick change=day=108
[time_engine] action=planet_station_tick change=day=108
[time_engine] action=location_tick change=day=108
[time_engine] action=npc_tick change=day=108
[time_engine] action=end_of_day_log change=day=108
Spawn gate cooldown check: system_id=SYS-001 current_day=108 cooldown_until=109 skipped=true reason=cooldown_active
Situation expired: civil_unrest system=SYS-001
[time_engine] action=time_advance_day_completed change=turn=108 hard_stop=None
[time_engine] action=galaxy_tick change=day=109
[time_engine] action=system_tick change=day=109
[time_engine] action=planet_station_tick change=day=109
[time_engine] action=location_tick change=day=109
[time_engine] action=npc_tick change=day=109
[time_engine] action=end_of_day_log change=day=109
Spawn gate cooldown check: system_id=SYS-001 current_day=109 cooldown_until=109 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=109 hard_stop=None
[time_engine] action=galaxy_tick change=day=110
[time_engine] action=system_tick change=day=110
[time_engine] action=planet_station_tick change=day=110
[time_engine] action=location_tick change=day=110
[time_engine] action=npc_tick change=day=110
[time_engine] action=end_of_day_log change=day=110
Spawn gate cooldown check: system_id=SYS-001 current_day=110 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=110 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.5605620214611486
[time_engine] action=time_advance_day_completed change=turn=110 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=110 days=2 reason=travel:TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route
[time_engine] action=galaxy_tick change=day=111
[time_engine] action=system_tick change=day=111
[time_engine] action=planet_station_tick change=day=111
[time_engine] action=location_tick change=day=111
[time_engine] action=npc_tick change=day=111
[time_engine] action=end_of_day_log change=day=111
Spawn gate cooldown check: system_id=SYS-001 current_day=111 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=111 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.3884663497232661
[time_engine] action=time_advance_day_completed change=turn=111 hard_stop=None
[time_engine] action=galaxy_tick change=day=112
[time_engine] action=system_tick change=day=112
[time_engine] action=planet_station_tick change=day=112
[time_engine] action=location_tick change=day=112
[time_engine] action=npc_tick change=day=112
[time_engine] action=end_of_day_log change=day=112
Spawn gate cooldown check: system_id=SYS-001 current_day=112 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=112 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.28810424493568276
[time_engine] action=time_advance_day_completed change=turn=112 hard_stop=None
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 60, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 51.84375710593287, "distance_ly_ceiled": 52, "inter_system": true, "target_destination_id": "SYS-001-DST-01", "target_system_id": "SYS-001", "travel_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 60, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 3, "fuel_capacity": 55, "fuel_cost": 52, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 60, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 52, "days_requested": 52, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 6, "travel_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route_enc_0", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route_enc_0", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route_enc_1", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route_enc_1", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route_enc_2", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route_enc_2", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route_enc_2ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route_enc_3", "handler_payload": {"npc_outcome": "attack"}, "next_handler": "combat_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route_enc_3", "resolver_outcome": {"outcome": "destroyed", "resolver": "combat", "rounds": 2, "winner": "enemy"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route_enc_3", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route_enc_4", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route_enc_4", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": ["attack_plus_one_high_tr_delta"], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route_enc_4ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [2, 5, 2], "weights_after_notoriety": [2, 5, 2], "weights_after_reputation": [2, 5, 2], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route_enc_4", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route_enc_5", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route_enc_5", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:60:auto_route_enc_5", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 112, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 2075, "destination_id": "SYS-001-DST-01", "location_id": "SYS-001-DST-01", "system_id": "SYS-001"}, "turn_after": 112, "turn_before": 60, "version": "0.11.0"}
You have arrived in Ion.
Intra-system destinations:
  1) SYS-001-DST-01 Ion 1
  2) SYS-001-DST-02 Ion 2
  3) SYS-001-DST-03 Ion 3
  4) SYS-001-DST-04 Ion 4
DESTINATION: Ion 1 (SYS-001)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 4
1) customs_inspection Customs Inspection
2) refuel Refuel
3) Back
Select destination action index: 2
requested_units: 55
{"active_encounter_count": 0, "command_type": "destination_action", "error": null, "events": [{"command_type": "destination_action", "detail": {"command_type": "destination_action"}, "stage": "start", "subsystem": "engine", "turn": 112, "world_seed": 12345}, {"command_type": "destination_action", "detail": {"action_id": "refuel", "result": {"credits": 1815, "current_fuel": 55, "ok": true, "reason": "ok", "total_cost": 260, "units_purchased": 52}, "result_summary": {"credits_after": 1815, "credits_before": 2075, "fuel_after": 55, "fuel_before": 3, "reason": "ok", "result_ok": true, "total_cost": 260, "unit_price": 5, "units_purchased": 52}}, "stage": "destination_action", "subsystem": "interaction_layer", "turn": 112, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 1815, "destination_id": "SYS-001-DST-01", "location_id": "SYS-001-DST-01", "system_id": "SYS-001"}, "turn_after": 112, "turn_before": 112, "version": "0.11.0"}
1) customs_inspection Customs Inspection
2) refuel Refuel
3) Back
Select destination action index: 3
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
Travel mode: 1
1) SYS-004 Flux distance_ly=51.844 government=fascist population=4 destinations=4 active_situations=[]
2) SYS-005 Beacon distance_ly=50.078
Select target system index: 2
[time_engine] action=time_advance_requested change=start_turn=112 days=10 reason=travel:TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route
[time_engine] action=galaxy_tick change=day=113
[time_engine] action=system_tick change=day=113
[time_engine] action=planet_station_tick change=day=113
[time_engine] action=location_tick change=day=113
[time_engine] action=npc_tick change=day=113
[time_engine] action=end_of_day_log change=day=113
Spawn gate cooldown check: system_id=SYS-005 current_day=113 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=113 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.8897025965378514
[time_engine] action=time_advance_day_completed change=turn=113 hard_stop=None
[time_engine] action=galaxy_tick change=day=114
[time_engine] action=system_tick change=day=114
[time_engine] action=planet_station_tick change=day=114
[time_engine] action=location_tick change=day=114
[time_engine] action=npc_tick change=day=114
[time_engine] action=end_of_day_log change=day=114
Spawn gate cooldown check: system_id=SYS-005 current_day=114 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=114 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.8259032284990114
[time_engine] action=time_advance_day_completed change=turn=114 hard_stop=None
[time_engine] action=galaxy_tick change=day=115
[time_engine] action=system_tick change=day=115
[time_engine] action=planet_station_tick change=day=115
[time_engine] action=location_tick change=day=115
[time_engine] action=npc_tick change=day=115
[time_engine] action=end_of_day_log change=day=115
Spawn gate cooldown check: system_id=SYS-005 current_day=115 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=115 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.09353580350266955
[time_engine] action=time_advance_day_completed change=turn=115 hard_stop=None
[time_engine] action=galaxy_tick change=day=116
[time_engine] action=system_tick change=day=116
[time_engine] action=planet_station_tick change=day=116
[time_engine] action=location_tick change=day=116
[time_engine] action=npc_tick change=day=116
[time_engine] action=end_of_day_log change=day=116
Spawn gate cooldown check: system_id=SYS-005 current_day=116 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=116 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.6087291161252619
[time_engine] action=time_advance_day_completed change=turn=116 hard_stop=None
[time_engine] action=galaxy_tick change=day=117
[time_engine] action=system_tick change=day=117
[time_engine] action=planet_station_tick change=day=117
[time_engine] action=location_tick change=day=117
[time_engine] action=npc_tick change=day=117
[time_engine] action=end_of_day_log change=day=117
Spawn gate cooldown check: system_id=SYS-005 current_day=117 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=117 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.9444732309794275
[time_engine] action=time_advance_day_completed change=turn=117 hard_stop=None
[time_engine] action=galaxy_tick change=day=118
[time_engine] action=system_tick change=day=118
[time_engine] action=planet_station_tick change=day=118
[time_engine] action=location_tick change=day=118
[time_engine] action=npc_tick change=day=118
[time_engine] action=end_of_day_log change=day=118
Spawn gate cooldown check: system_id=SYS-005 current_day=118 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=118 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.858216521618301
[time_engine] action=time_advance_day_completed change=turn=118 hard_stop=None
[time_engine] action=galaxy_tick change=day=119
[time_engine] action=system_tick change=day=119
[time_engine] action=planet_station_tick change=day=119
[time_engine] action=location_tick change=day=119
[time_engine] action=npc_tick change=day=119
[time_engine] action=end_of_day_log change=day=119
Spawn gate cooldown check: system_id=SYS-005 current_day=119 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=119 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.5141510705573987
[time_engine] action=time_advance_day_completed change=turn=119 hard_stop=None
[time_engine] action=galaxy_tick change=day=120
[time_engine] action=system_tick change=day=120
[time_engine] action=planet_station_tick change=day=120
[time_engine] action=location_tick change=day=120
[time_engine] action=npc_tick change=day=120
[time_engine] action=end_of_day_log change=day=120
Spawn gate cooldown check: system_id=SYS-005 current_day=120 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=120 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.26094745987901447
[time_engine] action=time_advance_day_completed change=turn=120 hard_stop=None
[time_engine] action=galaxy_tick change=day=121
[time_engine] action=system_tick change=day=121
[time_engine] action=planet_station_tick change=day=121
[time_engine] action=location_tick change=day=121
[time_engine] action=npc_tick change=day=121
[time_engine] action=end_of_day_log change=day=121
Spawn gate cooldown check: system_id=SYS-005 current_day=121 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=121 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.3366087079988723
[time_engine] action=time_advance_day_completed change=turn=121 hard_stop=None
[time_engine] action=galaxy_tick change=day=122
[time_engine] action=system_tick change=day=122
[time_engine] action=planet_station_tick change=day=122
[time_engine] action=location_tick change=day=122
[time_engine] action=npc_tick change=day=122
[time_engine] action=end_of_day_log change=day=122
Spawn gate cooldown check: system_id=SYS-005 current_day=122 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=122 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.8729426441008747
[time_engine] action=time_advance_day_completed change=turn=122 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=122 days=10 reason=travel:TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route
[time_engine] action=galaxy_tick change=day=123
[time_engine] action=system_tick change=day=123
[time_engine] action=planet_station_tick change=day=123
[time_engine] action=location_tick change=day=123
[time_engine] action=npc_tick change=day=123
[time_engine] action=end_of_day_log change=day=123
Spawn gate cooldown check: system_id=SYS-005 current_day=123 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=123 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.4732388058602699
[time_engine] action=time_advance_day_completed change=turn=123 hard_stop=None
[time_engine] action=galaxy_tick change=day=124
[time_engine] action=system_tick change=day=124
[time_engine] action=planet_station_tick change=day=124
[time_engine] action=location_tick change=day=124
[time_engine] action=npc_tick change=day=124
[time_engine] action=end_of_day_log change=day=124
Spawn gate cooldown check: system_id=SYS-005 current_day=124 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=124 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.8869967068226452
[time_engine] action=time_advance_day_completed change=turn=124 hard_stop=None
[time_engine] action=galaxy_tick change=day=125
[time_engine] action=system_tick change=day=125
[time_engine] action=planet_station_tick change=day=125
[time_engine] action=location_tick change=day=125
[time_engine] action=npc_tick change=day=125
[time_engine] action=end_of_day_log change=day=125
Spawn gate cooldown check: system_id=SYS-005 current_day=125 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=125 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.80472138092516
[time_engine] action=time_advance_day_completed change=turn=125 hard_stop=None
[time_engine] action=galaxy_tick change=day=126
[time_engine] action=system_tick change=day=126
[time_engine] action=planet_station_tick change=day=126
[time_engine] action=location_tick change=day=126
[time_engine] action=npc_tick change=day=126
[time_engine] action=end_of_day_log change=day=126
Spawn gate cooldown check: system_id=SYS-005 current_day=126 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=126 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.6545240863266324
[time_engine] action=time_advance_day_completed change=turn=126 hard_stop=None
[time_engine] action=galaxy_tick change=day=127
[time_engine] action=system_tick change=day=127
[time_engine] action=planet_station_tick change=day=127
[time_engine] action=location_tick change=day=127
[time_engine] action=npc_tick change=day=127
[time_engine] action=end_of_day_log change=day=127
Spawn gate cooldown check: system_id=SYS-005 current_day=127 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate type+tier selected: system_id=SYS-005 current_day=127 selected_type=situation selected_tier=2 spawn_type_roll=0.3462767081463737 severity_roll=0.4534059704893757
Spawn gate candidate filter: system_id=SYS-005 selected_type=situation selected_tier=2 candidates_found=12
Situation added: trade_boom system=SYS-005 scope=system
Spawn gate cooldown set: system_id=SYS-005 current_day=127 cooldown_until=132 generated_any=true reason=spawn_gate_generation
[time_engine] action=time_advance_day_completed change=turn=127 hard_stop=None
[time_engine] action=galaxy_tick change=day=128
[time_engine] action=system_tick change=day=128
[time_engine] action=planet_station_tick change=day=128
[time_engine] action=location_tick change=day=128
[time_engine] action=npc_tick change=day=128
[time_engine] action=end_of_day_log change=day=128
Spawn gate cooldown check: system_id=SYS-005 current_day=128 cooldown_until=132 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=128 hard_stop=None
[time_engine] action=galaxy_tick change=day=129
[time_engine] action=system_tick change=day=129
[time_engine] action=planet_station_tick change=day=129
[time_engine] action=location_tick change=day=129
[time_engine] action=npc_tick change=day=129
[time_engine] action=end_of_day_log change=day=129
Spawn gate cooldown check: system_id=SYS-005 current_day=129 cooldown_until=132 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=129 hard_stop=None
[time_engine] action=galaxy_tick change=day=130
[time_engine] action=system_tick change=day=130
[time_engine] action=planet_station_tick change=day=130
[time_engine] action=location_tick change=day=130
[time_engine] action=npc_tick change=day=130
[time_engine] action=end_of_day_log change=day=130
Spawn gate cooldown check: system_id=SYS-005 current_day=130 cooldown_until=132 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=130 hard_stop=None
[time_engine] action=galaxy_tick change=day=131
[time_engine] action=system_tick change=day=131
[time_engine] action=planet_station_tick change=day=131
[time_engine] action=location_tick change=day=131
[time_engine] action=npc_tick change=day=131
[time_engine] action=end_of_day_log change=day=131
Spawn gate cooldown check: system_id=SYS-005 current_day=131 cooldown_until=132 skipped=true reason=cooldown_active
Situation expired: trade_boom system=SYS-005
[time_engine] action=time_advance_day_completed change=turn=131 hard_stop=None
[time_engine] action=galaxy_tick change=day=132
[time_engine] action=system_tick change=day=132
[time_engine] action=planet_station_tick change=day=132
[time_engine] action=location_tick change=day=132
[time_engine] action=npc_tick change=day=132
[time_engine] action=end_of_day_log change=day=132
Spawn gate cooldown check: system_id=SYS-005 current_day=132 cooldown_until=132 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=132 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=132 days=10 reason=travel:TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route
[time_engine] action=galaxy_tick change=day=133
[time_engine] action=system_tick change=day=133
[time_engine] action=planet_station_tick change=day=133
[time_engine] action=location_tick change=day=133
[time_engine] action=npc_tick change=day=133
[time_engine] action=end_of_day_log change=day=133
Spawn gate cooldown check: system_id=SYS-005 current_day=133 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=133 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.9581881274178746
[time_engine] action=time_advance_day_completed change=turn=133 hard_stop=None
[time_engine] action=galaxy_tick change=day=134
[time_engine] action=system_tick change=day=134
[time_engine] action=planet_station_tick change=day=134
[time_engine] action=location_tick change=day=134
[time_engine] action=npc_tick change=day=134
[time_engine] action=end_of_day_log change=day=134
Spawn gate cooldown check: system_id=SYS-005 current_day=134 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=134 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.4436965409863054
[time_engine] action=time_advance_day_completed change=turn=134 hard_stop=None
[time_engine] action=galaxy_tick change=day=135
[time_engine] action=system_tick change=day=135
[time_engine] action=planet_station_tick change=day=135
[time_engine] action=location_tick change=day=135
[time_engine] action=npc_tick change=day=135
[time_engine] action=end_of_day_log change=day=135
Spawn gate cooldown check: system_id=SYS-005 current_day=135 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=135 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.570575943317606
[time_engine] action=time_advance_day_completed change=turn=135 hard_stop=None
[time_engine] action=galaxy_tick change=day=136
[time_engine] action=system_tick change=day=136
[time_engine] action=planet_station_tick change=day=136
[time_engine] action=location_tick change=day=136
[time_engine] action=npc_tick change=day=136
[time_engine] action=end_of_day_log change=day=136
Spawn gate cooldown check: system_id=SYS-005 current_day=136 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=136 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.18554805224120352
[time_engine] action=time_advance_day_completed change=turn=136 hard_stop=None
[time_engine] action=galaxy_tick change=day=137
[time_engine] action=system_tick change=day=137
[time_engine] action=planet_station_tick change=day=137
[time_engine] action=location_tick change=day=137
[time_engine] action=npc_tick change=day=137
[time_engine] action=end_of_day_log change=day=137
Spawn gate cooldown check: system_id=SYS-005 current_day=137 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=137 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.9107281027697172
[time_engine] action=time_advance_day_completed change=turn=137 hard_stop=None
[time_engine] action=galaxy_tick change=day=138
[time_engine] action=system_tick change=day=138
[time_engine] action=planet_station_tick change=day=138
[time_engine] action=location_tick change=day=138
[time_engine] action=npc_tick change=day=138
[time_engine] action=end_of_day_log change=day=138
Spawn gate cooldown check: system_id=SYS-005 current_day=138 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=138 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.19303488505696076
[time_engine] action=time_advance_day_completed change=turn=138 hard_stop=None
[time_engine] action=galaxy_tick change=day=139
[time_engine] action=system_tick change=day=139
[time_engine] action=planet_station_tick change=day=139
[time_engine] action=location_tick change=day=139
[time_engine] action=npc_tick change=day=139
[time_engine] action=end_of_day_log change=day=139
Spawn gate cooldown check: system_id=SYS-005 current_day=139 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=139 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.7026004907590709
[time_engine] action=time_advance_day_completed change=turn=139 hard_stop=None
[time_engine] action=galaxy_tick change=day=140
[time_engine] action=system_tick change=day=140
[time_engine] action=planet_station_tick change=day=140
[time_engine] action=location_tick change=day=140
[time_engine] action=npc_tick change=day=140
[time_engine] action=end_of_day_log change=day=140
Spawn gate cooldown check: system_id=SYS-005 current_day=140 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=140 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.45662446347848573
[time_engine] action=time_advance_day_completed change=turn=140 hard_stop=None
[time_engine] action=galaxy_tick change=day=141
[time_engine] action=system_tick change=day=141
[time_engine] action=planet_station_tick change=day=141
[time_engine] action=location_tick change=day=141
[time_engine] action=npc_tick change=day=141
[time_engine] action=end_of_day_log change=day=141
Spawn gate cooldown check: system_id=SYS-005 current_day=141 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=141 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.5609568983543964
[time_engine] action=time_advance_day_completed change=turn=141 hard_stop=None
[time_engine] action=galaxy_tick change=day=142
[time_engine] action=system_tick change=day=142
[time_engine] action=planet_station_tick change=day=142
[time_engine] action=location_tick change=day=142
[time_engine] action=npc_tick change=day=142
[time_engine] action=end_of_day_log change=day=142
Spawn gate cooldown check: system_id=SYS-005 current_day=142 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=142 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.46075764859855295
[time_engine] action=time_advance_day_completed change=turn=142 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=142 days=10 reason=travel:TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route
[time_engine] action=galaxy_tick change=day=143
[time_engine] action=system_tick change=day=143
[time_engine] action=planet_station_tick change=day=143
[time_engine] action=location_tick change=day=143
[time_engine] action=npc_tick change=day=143
[time_engine] action=end_of_day_log change=day=143
Spawn gate cooldown check: system_id=SYS-005 current_day=143 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=143 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.544456181462437
[time_engine] action=time_advance_day_completed change=turn=143 hard_stop=None
[time_engine] action=galaxy_tick change=day=144
[time_engine] action=system_tick change=day=144
[time_engine] action=planet_station_tick change=day=144
[time_engine] action=location_tick change=day=144
[time_engine] action=npc_tick change=day=144
[time_engine] action=end_of_day_log change=day=144
Spawn gate cooldown check: system_id=SYS-005 current_day=144 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=144 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.3325252115786519
[time_engine] action=time_advance_day_completed change=turn=144 hard_stop=None
[time_engine] action=galaxy_tick change=day=145
[time_engine] action=system_tick change=day=145
[time_engine] action=planet_station_tick change=day=145
[time_engine] action=location_tick change=day=145
[time_engine] action=npc_tick change=day=145
[time_engine] action=end_of_day_log change=day=145
Spawn gate cooldown check: system_id=SYS-005 current_day=145 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=145 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.9005042318644789
[time_engine] action=time_advance_day_completed change=turn=145 hard_stop=None
[time_engine] action=galaxy_tick change=day=146
[time_engine] action=system_tick change=day=146
[time_engine] action=planet_station_tick change=day=146
[time_engine] action=location_tick change=day=146
[time_engine] action=npc_tick change=day=146
[time_engine] action=end_of_day_log change=day=146
Spawn gate cooldown check: system_id=SYS-005 current_day=146 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=146 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.5447532821227778
[time_engine] action=time_advance_day_completed change=turn=146 hard_stop=None
[time_engine] action=galaxy_tick change=day=147
[time_engine] action=system_tick change=day=147
[time_engine] action=planet_station_tick change=day=147
[time_engine] action=location_tick change=day=147
[time_engine] action=npc_tick change=day=147
[time_engine] action=end_of_day_log change=day=147
Spawn gate cooldown check: system_id=SYS-005 current_day=147 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=147 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.7220336993360837
[time_engine] action=time_advance_day_completed change=turn=147 hard_stop=None
[time_engine] action=galaxy_tick change=day=148
[time_engine] action=system_tick change=day=148
[time_engine] action=planet_station_tick change=day=148
[time_engine] action=location_tick change=day=148
[time_engine] action=npc_tick change=day=148
[time_engine] action=end_of_day_log change=day=148
Spawn gate cooldown check: system_id=SYS-005 current_day=148 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=148 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.9451219938387383
[time_engine] action=time_advance_day_completed change=turn=148 hard_stop=None
[time_engine] action=galaxy_tick change=day=149
[time_engine] action=system_tick change=day=149
[time_engine] action=planet_station_tick change=day=149
[time_engine] action=location_tick change=day=149
[time_engine] action=npc_tick change=day=149
[time_engine] action=end_of_day_log change=day=149
Spawn gate cooldown check: system_id=SYS-005 current_day=149 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=149 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.5836290831847629
[time_engine] action=time_advance_day_completed change=turn=149 hard_stop=None
[time_engine] action=galaxy_tick change=day=150
[time_engine] action=system_tick change=day=150
[time_engine] action=planet_station_tick change=day=150
[time_engine] action=location_tick change=day=150
[time_engine] action=npc_tick change=day=150
[time_engine] action=end_of_day_log change=day=150
Spawn gate cooldown check: system_id=SYS-005 current_day=150 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=150 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.19673281097544992
[time_engine] action=time_advance_day_completed change=turn=150 hard_stop=None
[time_engine] action=galaxy_tick change=day=151
[time_engine] action=system_tick change=day=151
[time_engine] action=planet_station_tick change=day=151
[time_engine] action=location_tick change=day=151
[time_engine] action=npc_tick change=day=151
[time_engine] action=end_of_day_log change=day=151
Spawn gate cooldown check: system_id=SYS-005 current_day=151 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=151 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.29609554117049364
[time_engine] action=time_advance_day_completed change=turn=151 hard_stop=None
[time_engine] action=galaxy_tick change=day=152
[time_engine] action=system_tick change=day=152
[time_engine] action=planet_station_tick change=day=152
[time_engine] action=location_tick change=day=152
[time_engine] action=npc_tick change=day=152
[time_engine] action=end_of_day_log change=day=152
Spawn gate cooldown check: system_id=SYS-005 current_day=152 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=152 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.35996342724282104
[time_engine] action=time_advance_day_completed change=turn=152 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=152 days=10 reason=travel:TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route
[time_engine] action=galaxy_tick change=day=153
[time_engine] action=system_tick change=day=153
[time_engine] action=planet_station_tick change=day=153
[time_engine] action=location_tick change=day=153
[time_engine] action=npc_tick change=day=153
[time_engine] action=end_of_day_log change=day=153
Spawn gate cooldown check: system_id=SYS-005 current_day=153 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=153 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.2682338064772911
[time_engine] action=time_advance_day_completed change=turn=153 hard_stop=None
[time_engine] action=galaxy_tick change=day=154
[time_engine] action=system_tick change=day=154
[time_engine] action=planet_station_tick change=day=154
[time_engine] action=location_tick change=day=154
[time_engine] action=npc_tick change=day=154
[time_engine] action=end_of_day_log change=day=154
Spawn gate cooldown check: system_id=SYS-005 current_day=154 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=154 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.4712126848121201
[time_engine] action=time_advance_day_completed change=turn=154 hard_stop=None
[time_engine] action=galaxy_tick change=day=155
[time_engine] action=system_tick change=day=155
[time_engine] action=planet_station_tick change=day=155
[time_engine] action=location_tick change=day=155
[time_engine] action=npc_tick change=day=155
[time_engine] action=end_of_day_log change=day=155
Spawn gate cooldown check: system_id=SYS-005 current_day=155 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=155 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.31589114981090904
[time_engine] action=time_advance_day_completed change=turn=155 hard_stop=None
[time_engine] action=galaxy_tick change=day=156
[time_engine] action=system_tick change=day=156
[time_engine] action=planet_station_tick change=day=156
[time_engine] action=location_tick change=day=156
[time_engine] action=npc_tick change=day=156
[time_engine] action=end_of_day_log change=day=156
Spawn gate cooldown check: system_id=SYS-005 current_day=156 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=156 cooldown_until=132 reason=spawn_gate_roll_failed spawn_gate_roll=0.995614456960936
[time_engine] action=time_advance_day_completed change=turn=156 hard_stop=None
[time_engine] action=galaxy_tick change=day=157
[time_engine] action=system_tick change=day=157
[time_engine] action=planet_station_tick change=day=157
[time_engine] action=location_tick change=day=157
[time_engine] action=npc_tick change=day=157
[time_engine] action=end_of_day_log change=day=157
Spawn gate cooldown check: system_id=SYS-005 current_day=157 cooldown_until=132 skipped=false reason=cooldown_clear
Spawn gate type+tier selected: system_id=SYS-005 current_day=157 selected_type=situation selected_tier=3 spawn_type_roll=0.4150401740218289 severity_roll=0.6978604940524044
Spawn gate candidate filter: system_id=SYS-005 selected_type=situation selected_tier=3 candidates_found=8
Situation added: economic_recession system=SYS-005 scope=system
Spawn gate cooldown set: system_id=SYS-005 current_day=157 cooldown_until=162 generated_any=true reason=spawn_gate_generation
[time_engine] action=time_advance_day_completed change=turn=157 hard_stop=None
[time_engine] action=galaxy_tick change=day=158
[time_engine] action=system_tick change=day=158
[time_engine] action=planet_station_tick change=day=158
[time_engine] action=location_tick change=day=158
[time_engine] action=npc_tick change=day=158
[time_engine] action=end_of_day_log change=day=158
Spawn gate cooldown check: system_id=SYS-005 current_day=158 cooldown_until=162 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=158 hard_stop=None
[time_engine] action=galaxy_tick change=day=159
[time_engine] action=system_tick change=day=159
[time_engine] action=planet_station_tick change=day=159
[time_engine] action=location_tick change=day=159
[time_engine] action=npc_tick change=day=159
[time_engine] action=end_of_day_log change=day=159
Spawn gate cooldown check: system_id=SYS-005 current_day=159 cooldown_until=162 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=159 hard_stop=None
[time_engine] action=galaxy_tick change=day=160
[time_engine] action=system_tick change=day=160
[time_engine] action=planet_station_tick change=day=160
[time_engine] action=location_tick change=day=160
[time_engine] action=npc_tick change=day=160
[time_engine] action=end_of_day_log change=day=160
Spawn gate cooldown check: system_id=SYS-005 current_day=160 cooldown_until=162 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=160 hard_stop=None
[time_engine] action=galaxy_tick change=day=161
[time_engine] action=system_tick change=day=161
[time_engine] action=planet_station_tick change=day=161
[time_engine] action=location_tick change=day=161
[time_engine] action=npc_tick change=day=161
[time_engine] action=end_of_day_log change=day=161
Spawn gate cooldown check: system_id=SYS-005 current_day=161 cooldown_until=162 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=161 hard_stop=None
[time_engine] action=galaxy_tick change=day=162
[time_engine] action=system_tick change=day=162
[time_engine] action=planet_station_tick change=day=162
[time_engine] action=location_tick change=day=162
[time_engine] action=npc_tick change=day=162
[time_engine] action=end_of_day_log change=day=162
Spawn gate cooldown check: system_id=SYS-005 current_day=162 cooldown_until=162 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=162 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=162 days=1 reason=travel:TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route
[time_engine] action=galaxy_tick change=day=163
[time_engine] action=system_tick change=day=163
[time_engine] action=planet_station_tick change=day=163
[time_engine] action=location_tick change=day=163
[time_engine] action=npc_tick change=day=163
[time_engine] action=end_of_day_log change=day=163
Spawn gate cooldown check: system_id=SYS-005 current_day=163 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=163 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.30575050965631534
Situation expired: economic_recession system=SYS-005
[time_engine] action=time_advance_day_completed change=turn=163 hard_stop=None
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 50.07785749565051, "distance_ly_ceiled": 51, "inter_system": true, "target_destination_id": "SYS-005-DST-01", "target_system_id": "SYS-005", "travel_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 4, "fuel_capacity": 55, "fuel_cost": 51, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 112, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 51, "days_requested": 51, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 163, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 163, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 4, "travel_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 163, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route_enc_0", "handler_payload": {"npc_outcome": "pursue"}, "next_handler": "pursuit_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 163, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route_enc_0", "resolver_outcome": {"escaped": true, "outcome": "escape_success", "resolver": "pursuit", "threshold": 0.55}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 163, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route_enc_0", "qualifies": true}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 163, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"applied": {"cargo": null, "context": "game_engine", "credits": 1031, "quantity": 0}, "encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route_enc_0", "reward_profile_id": "bounty_credit"}, "stage": "conditional_rewards", "subsystem": "reward_applicator", "turn": 163, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route_enc_1", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 163, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route_enc_1", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 163, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 163, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route_enc_2", "handler_payload": {"npc_outcome": "attack"}, "next_handler": "combat_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 163, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route_enc_2", "resolver_outcome": {"outcome": "max_rounds", "resolver": "combat", "rounds": 3, "winner": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 163, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 163, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route_enc_4", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 163, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route_enc_4", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 163, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:112:auto_route_enc_4", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 163, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 2846, "destination_id": "SYS-005-DST-01", "location_id": "SYS-005-DST-01", "system_id": "SYS-005"}, "turn_after": 163, "turn_before": 112, "version": "0.11.0"}
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
Select location index: 2
Entered location: SYS-005-DST-01-LOC-market
MARKET PROFILE
  System: SYS-005
  Destination: SYS-005-DST-01
  Primary economy: cultural
  Active situations: none
  DATA: produced=['encrypted_records', 'media_packages'] consumed=[] neutral=[]
  ENERGY: produced=[] consumed=['fusion_cores', 'power_cells'] neutral=[]
  FOOD: produced=[] consumed=['fresh_produce', 'spice_wine'] neutral=[]
  LUXURY: produced=['designer_goods', 'prestige_technology'] consumed=[] neutral=[]
  MACHINERY: produced=['automated_factories', 'military_hardware'] consumed=[] neutral=[]
  METAL: produced=[] consumed=['decorative_metals', 'titanium_bars'] neutral=[]
  PARTS: produced=[] consumed=['cybernetic_implants', 'mechanical_parts'] neutral=[]
  WEAPONS: produced=['ship_weapons', 'small_arms'] consumed=[] neutral=[]
MARKET SKUS
  automated_factories | Automated Factories | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  cybernetic_implants | Cybernetic Implants | buy=312 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  decorative_metals | Decorative Metals | buy=317 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  designer_goods | Designer Goods | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  encrypted_records | Encrypted Records | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  fresh_produce | Fresh Produce | buy=144 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  fusion_cores | Fusion Cores | buy=408 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  heritage_cuisine | Heritage Cuisine | buy=-- | sell=85 | cargo=5 | legality=LEGAL | risk=Medium
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=173 | cargo=10 | legality=LEGAL | risk=Medium
  mechanical_parts | Mechanical Parts | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  media_packages | Media Packages | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  military_hardware | Military Hardware | buy=336 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  power_cells | Power Cells | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  prestige_technology | Prestige Technology | buy=403 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  ship_weapons | Ship Weapons | buy=320 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  small_arms | Small Arms | buy=176 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  spice_wine | Spice Wine | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  titanium_bars | Titanium Bars | buy=252 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 3
Returned to destination: SYS-005-DST-01
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
Select location index: 2
Entered location: SYS-005-DST-01-LOC-market
MARKET PROFILE
  System: SYS-005
  Destination: SYS-005-DST-01
  Primary economy: cultural
  Active situations: none
  DATA: produced=['encrypted_records', 'media_packages'] consumed=[] neutral=[]
  ENERGY: produced=[] consumed=['fusion_cores', 'power_cells'] neutral=[]
  FOOD: produced=[] consumed=['fresh_produce', 'spice_wine'] neutral=[]
  LUXURY: produced=['designer_goods', 'prestige_technology'] consumed=[] neutral=[]
  MACHINERY: produced=['automated_factories', 'military_hardware'] consumed=[] neutral=[]
  METAL: produced=[] consumed=['decorative_metals', 'titanium_bars'] neutral=[]
  PARTS: produced=[] consumed=['cybernetic_implants', 'mechanical_parts'] neutral=[]
  WEAPONS: produced=['ship_weapons', 'small_arms'] consumed=[] neutral=[]
MARKET SKUS
  automated_factories | Automated Factories | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  cybernetic_implants | Cybernetic Implants | buy=312 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  decorative_metals | Decorative Metals | buy=317 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  designer_goods | Designer Goods | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  encrypted_records | Encrypted Records | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  fresh_produce | Fresh Produce | buy=144 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  fusion_cores | Fusion Cores | buy=408 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  heritage_cuisine | Heritage Cuisine | buy=-- | sell=85 | cargo=5 | legality=LEGAL | risk=Medium
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=173 | cargo=10 | legality=LEGAL | risk=Medium
  mechanical_parts | Mechanical Parts | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  media_packages | Media Packages | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  military_hardware | Military Hardware | buy=336 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  power_cells | Power Cells | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  prestige_technology | Prestige Technology | buy=403 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  ship_weapons | Ship Weapons | buy=320 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  small_arms | Small Arms | buy=176 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  spice_wine | Spice Wine | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  titanium_bars | Titanium Bars | buy=252 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 2
1) heritage_cuisine Heritage Cuisine units=5 price=85 legality=LEGAL risk=Medium
2) luxury_fresh_produce luxury_fresh_produce units=10 price=173 legality=LEGAL risk=Medium
Select sell sku index: 2
Quantity: 10
{"active_encounter_count": 0, "command_type": "market_sell", "error": null, "events": [{"command_type": "market_sell", "detail": {"command_type": "market_sell"}, "stage": "start", "subsystem": "engine", "turn": 163, "world_seed": 12345}, {"command_type": "market_sell", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 163, "world_seed": 12345}, {"command_type": "market_sell", "detail": {"action": "sell", "cargo_after": 0, "credits_after": 4576, "credits_before": 2846, "quantity": 10, "sku_id": "luxury_fresh_produce", "total_gain": 1730, "unit_price": 173}, "stage": "market_trade", "subsystem": "market", "turn": 163, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 4576, "destination_id": "SYS-005-DST-01", "location_id": "SYS-005-DST-01-LOC-market", "system_id": "SYS-005"}, "turn_after": 163, "turn_before": 163, "version": "0.11.0"}
MARKET PROFILE
  System: SYS-005
  Destination: SYS-005-DST-01
  Primary economy: cultural
  Active situations: none
  DATA: produced=['encrypted_records', 'media_packages'] consumed=[] neutral=[]
  ENERGY: produced=[] consumed=['fusion_cores', 'power_cells'] neutral=[]
  FOOD: produced=[] consumed=['fresh_produce', 'spice_wine'] neutral=[]
  LUXURY: produced=['designer_goods', 'prestige_technology'] consumed=[] neutral=[]
  MACHINERY: produced=['automated_factories', 'military_hardware'] consumed=[] neutral=[]
  METAL: produced=[] consumed=['decorative_metals', 'titanium_bars'] neutral=[]
  PARTS: produced=[] consumed=['cybernetic_implants', 'mechanical_parts'] neutral=[]
  WEAPONS: produced=['ship_weapons', 'small_arms'] consumed=[] neutral=[]
MARKET SKUS
  automated_factories | Automated Factories | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  cybernetic_implants | Cybernetic Implants | buy=312 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  decorative_metals | Decorative Metals | buy=317 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  designer_goods | Designer Goods | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  encrypted_records | Encrypted Records | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  fresh_produce | Fresh Produce | buy=144 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  fusion_cores | Fusion Cores | buy=408 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  heritage_cuisine | Heritage Cuisine | buy=-- | sell=85 | cargo=5 | legality=LEGAL | risk=Medium
  mechanical_parts | Mechanical Parts | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  media_packages | Media Packages | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  military_hardware | Military Hardware | buy=336 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  power_cells | Power Cells | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  prestige_technology | Prestige Technology | buy=403 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  ship_weapons | Ship Weapons | buy=320 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  small_arms | Small Arms | buy=176 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  spice_wine | Spice Wine | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  titanium_bars | Titanium Bars | buy=252 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 3
Returned to destination: SYS-005-DST-01
DESTINATION: Beacon 1 (SYS-005)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 1
PLAYER / SHIP INFO
  Credits: 4576
  Fuel: 4/55
  Cargo manifest: {'heritage_cuisine': 5}
  Reputation: 50 band=0
  Heat: 0
  Notoriety: 0 band=-2
  Arrest state: free
  Warrants: []
  Location: SYS-005 / SYS-005-DST-01 / SYS-005-DST-01
  Turn: 163
  Active crew: []
  Active missions: []
ONGOING COSTS
  Insurance: 0
  Warehouse rental: 0
  Crew wages: 0
  Total recurring cost: 0
WAREHOUSE RENTALS
  none
DESTINATION: Beacon 1 (SYS-005)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 4
1) customs_inspection Customs Inspection
2) refuel Refuel
3) Back
Select destination action index: 2
requested_units: 55
{"active_encounter_count": 0, "command_type": "destination_action", "error": null, "events": [{"command_type": "destination_action", "detail": {"command_type": "destination_action"}, "stage": "start", "subsystem": "engine", "turn": 163, "world_seed": 12345}, {"command_type": "destination_action", "detail": {"action_id": "refuel", "result": {"credits": 4321, "current_fuel": 55, "ok": true, "reason": "ok", "total_cost": 255, "units_purchased": 51}, "result_summary": {"credits_after": 4321, "credits_before": 4576, "fuel_after": 55, "fuel_before": 4, "reason": "ok", "result_ok": true, "total_cost": 255, "unit_price": 5, "units_purchased": 51}}, "stage": "destination_action", "subsystem": "interaction_layer", "turn": 163, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 4321, "destination_id": "SYS-005-DST-01", "location_id": "SYS-005-DST-01", "system_id": "SYS-005"}, "turn_after": 163, "turn_before": 163, "version": "0.11.0"}
1) customs_inspection Customs Inspection
2) refuel Refuel
3) Back
Select destination action index: 3
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
Travel mode: 1
1) SYS-001 Ion distance_ly=50.078 government=democracy population=3 destinations=4 active_situations=[]
Select target system index: 1
[time_engine] action=time_advance_requested change=start_turn=163 days=10 reason=travel:TRAVEL-SYS-005:SYS-001:SYS-001-DST-01:163:auto_route
[time_engine] action=galaxy_tick change=day=164
[time_engine] action=system_tick change=day=164
[time_engine] action=planet_station_tick change=day=164
[time_engine] action=location_tick change=day=164
[time_engine] action=npc_tick change=day=164
[time_engine] action=end_of_day_log change=day=164
Spawn gate cooldown check: system_id=SYS-001 current_day=164 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=164 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.49302338472202556
[time_engine] action=time_advance_day_completed change=turn=164 hard_stop=None
[time_engine] action=galaxy_tick change=day=165
[time_engine] action=system_tick change=day=165
[time_engine] action=planet_station_tick change=day=165
[time_engine] action=location_tick change=day=165
[time_engine] action=npc_tick change=day=165
[time_engine] action=end_of_day_log change=day=165
Spawn gate cooldown check: system_id=SYS-001 current_day=165 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=165 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.9806158957924993
[time_engine] action=time_advance_day_completed change=turn=165 hard_stop=None
[time_engine] action=galaxy_tick change=day=166
[time_engine] action=system_tick change=day=166
[time_engine] action=planet_station_tick change=day=166
[time_engine] action=location_tick change=day=166
[time_engine] action=npc_tick change=day=166
[time_engine] action=end_of_day_log change=day=166
Spawn gate cooldown check: system_id=SYS-001 current_day=166 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=166 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.9394692262400146
[time_engine] action=time_advance_day_completed change=turn=166 hard_stop=None
[time_engine] action=galaxy_tick change=day=167
[time_engine] action=system_tick change=day=167
[time_engine] action=planet_station_tick change=day=167
[time_engine] action=location_tick change=day=167
[time_engine] action=npc_tick change=day=167
[time_engine] action=end_of_day_log change=day=167
Spawn gate cooldown check: system_id=SYS-001 current_day=167 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=167 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.20848319708320218
[time_engine] action=time_advance_day_completed change=turn=167 hard_stop=None
[time_engine] action=galaxy_tick change=day=168
[time_engine] action=system_tick change=day=168
[time_engine] action=planet_station_tick change=day=168
[time_engine] action=location_tick change=day=168
[time_engine] action=npc_tick change=day=168
[time_engine] action=end_of_day_log change=day=168
Spawn gate cooldown check: system_id=SYS-001 current_day=168 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=168 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.12864148802076758
[time_engine] action=time_advance_day_completed change=turn=168 hard_stop=None
[time_engine] action=galaxy_tick change=day=169
[time_engine] action=system_tick change=day=169
[time_engine] action=planet_station_tick change=day=169
[time_engine] action=location_tick change=day=169
[time_engine] action=npc_tick change=day=169
[time_engine] action=end_of_day_log change=day=169
Spawn gate cooldown check: system_id=SYS-001 current_day=169 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=169 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.5833640389182948
[time_engine] action=time_advance_day_completed change=turn=169 hard_stop=None
[time_engine] action=galaxy_tick change=day=170
[time_engine] action=system_tick change=day=170
[time_engine] action=planet_station_tick change=day=170
[time_engine] action=location_tick change=day=170
[time_engine] action=npc_tick change=day=170
[time_engine] action=end_of_day_log change=day=170
Spawn gate cooldown check: system_id=SYS-001 current_day=170 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=170 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.5828607458055759
[time_engine] action=time_advance_day_completed change=turn=170 hard_stop=None
[time_engine] action=galaxy_tick change=day=171
[time_engine] action=system_tick change=day=171
[time_engine] action=planet_station_tick change=day=171
[time_engine] action=location_tick change=day=171
[time_engine] action=npc_tick change=day=171
[time_engine] action=end_of_day_log change=day=171
Spawn gate cooldown check: system_id=SYS-001 current_day=171 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=171 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.08515830551527792
[time_engine] action=time_advance_day_completed change=turn=171 hard_stop=None
[time_engine] action=galaxy_tick change=day=172
[time_engine] action=system_tick change=day=172
[time_engine] action=planet_station_tick change=day=172
[time_engine] action=location_tick change=day=172
[time_engine] action=npc_tick change=day=172
[time_engine] action=end_of_day_log change=day=172
Spawn gate cooldown check: system_id=SYS-001 current_day=172 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=172 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.5019911574782002
[time_engine] action=time_advance_day_completed change=turn=172 hard_stop=None
[time_engine] action=galaxy_tick change=day=173
[time_engine] action=system_tick change=day=173
[time_engine] action=planet_station_tick change=day=173
[time_engine] action=location_tick change=day=173
[time_engine] action=npc_tick change=day=173
[time_engine] action=end_of_day_log change=day=173
Spawn gate cooldown check: system_id=SYS-001 current_day=173 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=173 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.5963226215812163
[time_engine] action=time_advance_day_completed change=turn=173 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=173 days=10 reason=travel:TRAVEL-SYS-005:SYS-001:SYS-001-DST-01:163:auto_route
[time_engine] action=galaxy_tick change=day=174
[time_engine] action=system_tick change=day=174
[time_engine] action=planet_station_tick change=day=174
[time_engine] action=location_tick change=day=174
[time_engine] action=npc_tick change=day=174
[time_engine] action=end_of_day_log change=day=174
Spawn gate cooldown check: system_id=SYS-001 current_day=174 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=174 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.4405123718102766
[time_engine] action=time_advance_day_completed change=turn=174 hard_stop=None
[time_engine] action=galaxy_tick change=day=175
[time_engine] action=system_tick change=day=175
[time_engine] action=planet_station_tick change=day=175
[time_engine] action=location_tick change=day=175
[time_engine] action=npc_tick change=day=175
[time_engine] action=end_of_day_log change=day=175
Spawn gate cooldown check: system_id=SYS-001 current_day=175 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=175 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.5835001838752794
[time_engine] action=time_advance_day_completed change=turn=175 hard_stop=None
[time_engine] action=galaxy_tick change=day=176
[time_engine] action=system_tick change=day=176
[time_engine] action=planet_station_tick change=day=176
[time_engine] action=location_tick change=day=176
[time_engine] action=npc_tick change=day=176
[time_engine] action=end_of_day_log change=day=176
Spawn gate cooldown check: system_id=SYS-001 current_day=176 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=176 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.15753380440721065
[time_engine] action=time_advance_day_completed change=turn=176 hard_stop=None
[time_engine] action=galaxy_tick change=day=177
[time_engine] action=system_tick change=day=177
[time_engine] action=planet_station_tick change=day=177
[time_engine] action=location_tick change=day=177
[time_engine] action=npc_tick change=day=177
[time_engine] action=end_of_day_log change=day=177
Spawn gate cooldown check: system_id=SYS-001 current_day=177 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=177 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.8613309964693995
[time_engine] action=time_advance_day_completed change=turn=177 hard_stop=None
[time_engine] action=galaxy_tick change=day=178
[time_engine] action=system_tick change=day=178
[time_engine] action=planet_station_tick change=day=178
[time_engine] action=location_tick change=day=178
[time_engine] action=npc_tick change=day=178
[time_engine] action=end_of_day_log change=day=178
Spawn gate cooldown check: system_id=SYS-001 current_day=178 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=178 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.27300961938486323
[time_engine] action=time_advance_day_completed change=turn=178 hard_stop=None
[time_engine] action=galaxy_tick change=day=179
[time_engine] action=system_tick change=day=179
[time_engine] action=planet_station_tick change=day=179
[time_engine] action=location_tick change=day=179
[time_engine] action=npc_tick change=day=179
[time_engine] action=end_of_day_log change=day=179
Spawn gate cooldown check: system_id=SYS-001 current_day=179 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=179 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.5698792620707714
[time_engine] action=time_advance_day_completed change=turn=179 hard_stop=None
[time_engine] action=galaxy_tick change=day=180
[time_engine] action=system_tick change=day=180
[time_engine] action=planet_station_tick change=day=180
[time_engine] action=location_tick change=day=180
[time_engine] action=npc_tick change=day=180
[time_engine] action=end_of_day_log change=day=180
Spawn gate cooldown check: system_id=SYS-001 current_day=180 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=180 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.23730434135679712
[time_engine] action=time_advance_day_completed change=turn=180 hard_stop=None
[time_engine] action=galaxy_tick change=day=181
[time_engine] action=system_tick change=day=181
[time_engine] action=planet_station_tick change=day=181
[time_engine] action=location_tick change=day=181
[time_engine] action=npc_tick change=day=181
[time_engine] action=end_of_day_log change=day=181
Spawn gate cooldown check: system_id=SYS-001 current_day=181 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=181 cooldown_until=109 reason=spawn_gate_roll_failed spawn_gate_roll=0.17432224090468973
[time_engine] action=time_advance_day_completed change=turn=181 hard_stop=None
[time_engine] action=galaxy_tick change=day=182
[time_engine] action=system_tick change=day=182
[time_engine] action=planet_station_tick change=day=182
[time_engine] action=location_tick change=day=182
[time_engine] action=npc_tick change=day=182
[time_engine] action=end_of_day_log change=day=182
Spawn gate cooldown check: system_id=SYS-001 current_day=182 cooldown_until=109 skipped=false reason=cooldown_clear
Spawn gate type+tier selected: system_id=SYS-001 current_day=182 selected_type=situation selected_tier=3 spawn_type_roll=0.5644738940713688 severity_roll=0.7863101245655613
Spawn gate candidate filter: system_id=SYS-001 selected_type=situation selected_tier=3 candidates_found=8
Situation added: civil_unrest system=SYS-001 scope=system
Spawn gate cooldown set: system_id=SYS-001 current_day=182 cooldown_until=187 generated_any=true reason=spawn_gate_generation
[time_engine] action=time_advance_day_completed change=turn=182 hard_stop=None
[time_engine] action=galaxy_tick change=day=183
[time_engine] action=system_tick change=day=183
[time_engine] action=planet_station_tick change=day=183
[time_engine] action=location_tick change=day=183
[time_engine] action=npc_tick change=day=183
[time_engine] action=end_of_day_log change=day=183
Spawn gate cooldown check: system_id=SYS-001 current_day=183 cooldown_until=187 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=183 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=183 days=10 reason=travel:TRAVEL-SYS-005:SYS-001:SYS-001-DST-01:163:auto_route
[time_engine] action=galaxy_tick change=day=184
[time_engine] action=system_tick change=day=184
[time_engine] action=planet_station_tick change=day=184
[time_engine] action=location_tick change=day=184
[time_engine] action=npc_tick change=day=184
[time_engine] action=end_of_day_log change=day=184
Spawn gate cooldown check: system_id=SYS-001 current_day=184 cooldown_until=187 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=184 hard_stop=None
[time_engine] action=galaxy_tick change=day=185
[time_engine] action=system_tick change=day=185
[time_engine] action=planet_station_tick change=day=185
[time_engine] action=location_tick change=day=185
[time_engine] action=npc_tick change=day=185
[time_engine] action=end_of_day_log change=day=185
Spawn gate cooldown check: system_id=SYS-001 current_day=185 cooldown_until=187 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=185 hard_stop=None
[time_engine] action=galaxy_tick change=day=186
[time_engine] action=system_tick change=day=186
[time_engine] action=planet_station_tick change=day=186
[time_engine] action=location_tick change=day=186
[time_engine] action=npc_tick change=day=186
[time_engine] action=end_of_day_log change=day=186
Spawn gate cooldown check: system_id=SYS-001 current_day=186 cooldown_until=187 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=186 hard_stop=None
[time_engine] action=galaxy_tick change=day=187
[time_engine] action=system_tick change=day=187
[time_engine] action=planet_station_tick change=day=187
[time_engine] action=location_tick change=day=187
[time_engine] action=npc_tick change=day=187
[time_engine] action=end_of_day_log change=day=187
Spawn gate cooldown check: system_id=SYS-001 current_day=187 cooldown_until=187 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=187 hard_stop=None
[time_engine] action=galaxy_tick change=day=188
[time_engine] action=system_tick change=day=188
[time_engine] action=planet_station_tick change=day=188
[time_engine] action=location_tick change=day=188
[time_engine] action=npc_tick change=day=188
[time_engine] action=end_of_day_log change=day=188
Spawn gate cooldown check: system_id=SYS-001 current_day=188 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=188 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.7756220786251127
[time_engine] action=time_advance_day_completed change=turn=188 hard_stop=None
[time_engine] action=galaxy_tick change=day=189
[time_engine] action=system_tick change=day=189
[time_engine] action=planet_station_tick change=day=189
[time_engine] action=location_tick change=day=189
[time_engine] action=npc_tick change=day=189
[time_engine] action=end_of_day_log change=day=189
Spawn gate cooldown check: system_id=SYS-001 current_day=189 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=189 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.3495375390484289
Situation expired: civil_unrest system=SYS-001
[time_engine] action=time_advance_day_completed change=turn=189 hard_stop=None
[time_engine] action=galaxy_tick change=day=190
[time_engine] action=system_tick change=day=190
[time_engine] action=planet_station_tick change=day=190
[time_engine] action=location_tick change=day=190
[time_engine] action=npc_tick change=day=190
[time_engine] action=end_of_day_log change=day=190
Spawn gate cooldown check: system_id=SYS-001 current_day=190 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=190 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.3296823929652113
[time_engine] action=time_advance_day_completed change=turn=190 hard_stop=None
[time_engine] action=galaxy_tick change=day=191
[time_engine] action=system_tick change=day=191
[time_engine] action=planet_station_tick change=day=191
[time_engine] action=location_tick change=day=191
[time_engine] action=npc_tick change=day=191
[time_engine] action=end_of_day_log change=day=191
Spawn gate cooldown check: system_id=SYS-001 current_day=191 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=191 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.900255780517158
[time_engine] action=time_advance_day_completed change=turn=191 hard_stop=None
[time_engine] action=galaxy_tick change=day=192
[time_engine] action=system_tick change=day=192
[time_engine] action=planet_station_tick change=day=192
[time_engine] action=location_tick change=day=192
[time_engine] action=npc_tick change=day=192
[time_engine] action=end_of_day_log change=day=192
Spawn gate cooldown check: system_id=SYS-001 current_day=192 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=192 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.5454436277923816
[time_engine] action=time_advance_day_completed change=turn=192 hard_stop=None
[time_engine] action=galaxy_tick change=day=193
[time_engine] action=system_tick change=day=193
[time_engine] action=planet_station_tick change=day=193
[time_engine] action=location_tick change=day=193
[time_engine] action=npc_tick change=day=193
[time_engine] action=end_of_day_log change=day=193
Spawn gate cooldown check: system_id=SYS-001 current_day=193 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=193 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.6563575723401261
[time_engine] action=time_advance_day_completed change=turn=193 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=193 days=10 reason=travel:TRAVEL-SYS-005:SYS-001:SYS-001-DST-01:163:auto_route
[time_engine] action=galaxy_tick change=day=194
[time_engine] action=system_tick change=day=194
[time_engine] action=planet_station_tick change=day=194
[time_engine] action=location_tick change=day=194
[time_engine] action=npc_tick change=day=194
[time_engine] action=end_of_day_log change=day=194
Spawn gate cooldown check: system_id=SYS-001 current_day=194 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=194 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.9640470181922373
[time_engine] action=time_advance_day_completed change=turn=194 hard_stop=None
[time_engine] action=galaxy_tick change=day=195
[time_engine] action=system_tick change=day=195
[time_engine] action=planet_station_tick change=day=195
[time_engine] action=location_tick change=day=195
[time_engine] action=npc_tick change=day=195
[time_engine] action=end_of_day_log change=day=195
Spawn gate cooldown check: system_id=SYS-001 current_day=195 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=195 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.9564198151864848
[time_engine] action=time_advance_day_completed change=turn=195 hard_stop=None
[time_engine] action=galaxy_tick change=day=196
[time_engine] action=system_tick change=day=196
[time_engine] action=planet_station_tick change=day=196
[time_engine] action=location_tick change=day=196
[time_engine] action=npc_tick change=day=196
[time_engine] action=end_of_day_log change=day=196
Spawn gate cooldown check: system_id=SYS-001 current_day=196 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=196 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.6645075161831902
[time_engine] action=time_advance_day_completed change=turn=196 hard_stop=None
[time_engine] action=galaxy_tick change=day=197
[time_engine] action=system_tick change=day=197
[time_engine] action=planet_station_tick change=day=197
[time_engine] action=location_tick change=day=197
[time_engine] action=npc_tick change=day=197
[time_engine] action=end_of_day_log change=day=197
Spawn gate cooldown check: system_id=SYS-001 current_day=197 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=197 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.27091165910212045
[time_engine] action=time_advance_day_completed change=turn=197 hard_stop=None
[time_engine] action=galaxy_tick change=day=198
[time_engine] action=system_tick change=day=198
[time_engine] action=planet_station_tick change=day=198
[time_engine] action=location_tick change=day=198
[time_engine] action=npc_tick change=day=198
[time_engine] action=end_of_day_log change=day=198
Spawn gate cooldown check: system_id=SYS-001 current_day=198 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=198 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.8826768747427184
[time_engine] action=time_advance_day_completed change=turn=198 hard_stop=None
[time_engine] action=galaxy_tick change=day=199
[time_engine] action=system_tick change=day=199
[time_engine] action=planet_station_tick change=day=199
[time_engine] action=location_tick change=day=199
[time_engine] action=npc_tick change=day=199
[time_engine] action=end_of_day_log change=day=199
Spawn gate cooldown check: system_id=SYS-001 current_day=199 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=199 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.2086746989784256
[time_engine] action=time_advance_day_completed change=turn=199 hard_stop=None
[time_engine] action=galaxy_tick change=day=200
[time_engine] action=system_tick change=day=200
[time_engine] action=planet_station_tick change=day=200
[time_engine] action=location_tick change=day=200
[time_engine] action=npc_tick change=day=200
[time_engine] action=end_of_day_log change=day=200
Spawn gate cooldown check: system_id=SYS-001 current_day=200 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=200 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.5767852115268307
[time_engine] action=time_advance_day_completed change=turn=200 hard_stop=None
[time_engine] action=galaxy_tick change=day=201
[time_engine] action=system_tick change=day=201
[time_engine] action=planet_station_tick change=day=201
[time_engine] action=location_tick change=day=201
[time_engine] action=npc_tick change=day=201
[time_engine] action=end_of_day_log change=day=201
Spawn gate cooldown check: system_id=SYS-001 current_day=201 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=201 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.7535262277044796
[time_engine] action=time_advance_day_completed change=turn=201 hard_stop=None
[time_engine] action=galaxy_tick change=day=202
[time_engine] action=system_tick change=day=202
[time_engine] action=planet_station_tick change=day=202
[time_engine] action=location_tick change=day=202
[time_engine] action=npc_tick change=day=202
[time_engine] action=end_of_day_log change=day=202
Spawn gate cooldown check: system_id=SYS-001 current_day=202 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=202 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.7100239863769856
[time_engine] action=time_advance_day_completed change=turn=202 hard_stop=None
[time_engine] action=galaxy_tick change=day=203
[time_engine] action=system_tick change=day=203
[time_engine] action=planet_station_tick change=day=203
[time_engine] action=location_tick change=day=203
[time_engine] action=npc_tick change=day=203
[time_engine] action=end_of_day_log change=day=203
Spawn gate cooldown check: system_id=SYS-001 current_day=203 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=203 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.6287302718892415
[time_engine] action=time_advance_day_completed change=turn=203 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=203 days=10 reason=travel:TRAVEL-SYS-005:SYS-001:SYS-001-DST-01:163:auto_route
[time_engine] action=galaxy_tick change=day=204
[time_engine] action=system_tick change=day=204
[time_engine] action=planet_station_tick change=day=204
[time_engine] action=location_tick change=day=204
[time_engine] action=npc_tick change=day=204
[time_engine] action=end_of_day_log change=day=204
Spawn gate cooldown check: system_id=SYS-001 current_day=204 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=204 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.37420017345758183
[time_engine] action=time_advance_day_completed change=turn=204 hard_stop=None
[time_engine] action=galaxy_tick change=day=205
[time_engine] action=system_tick change=day=205
[time_engine] action=planet_station_tick change=day=205
[time_engine] action=location_tick change=day=205
[time_engine] action=npc_tick change=day=205
[time_engine] action=end_of_day_log change=day=205
Spawn gate cooldown check: system_id=SYS-001 current_day=205 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=205 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.14310141549885613
[time_engine] action=time_advance_day_completed change=turn=205 hard_stop=None
[time_engine] action=galaxy_tick change=day=206
[time_engine] action=system_tick change=day=206
[time_engine] action=planet_station_tick change=day=206
[time_engine] action=location_tick change=day=206
[time_engine] action=npc_tick change=day=206
[time_engine] action=end_of_day_log change=day=206
Spawn gate cooldown check: system_id=SYS-001 current_day=206 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=206 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.6094786463404689
[time_engine] action=time_advance_day_completed change=turn=206 hard_stop=None
[time_engine] action=galaxy_tick change=day=207
[time_engine] action=system_tick change=day=207
[time_engine] action=planet_station_tick change=day=207
[time_engine] action=location_tick change=day=207
[time_engine] action=npc_tick change=day=207
[time_engine] action=end_of_day_log change=day=207
Spawn gate cooldown check: system_id=SYS-001 current_day=207 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=207 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.4108912394078128
[time_engine] action=time_advance_day_completed change=turn=207 hard_stop=None
[time_engine] action=galaxy_tick change=day=208
[time_engine] action=system_tick change=day=208
[time_engine] action=planet_station_tick change=day=208
[time_engine] action=location_tick change=day=208
[time_engine] action=npc_tick change=day=208
[time_engine] action=end_of_day_log change=day=208
Spawn gate cooldown check: system_id=SYS-001 current_day=208 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=208 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.28813360749160466
[time_engine] action=time_advance_day_completed change=turn=208 hard_stop=None
[time_engine] action=galaxy_tick change=day=209
[time_engine] action=system_tick change=day=209
[time_engine] action=planet_station_tick change=day=209
[time_engine] action=location_tick change=day=209
[time_engine] action=npc_tick change=day=209
[time_engine] action=end_of_day_log change=day=209
Spawn gate cooldown check: system_id=SYS-001 current_day=209 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=209 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.4588660967374044
[time_engine] action=time_advance_day_completed change=turn=209 hard_stop=None
[time_engine] action=galaxy_tick change=day=210
[time_engine] action=system_tick change=day=210
[time_engine] action=planet_station_tick change=day=210
[time_engine] action=location_tick change=day=210
[time_engine] action=npc_tick change=day=210
[time_engine] action=end_of_day_log change=day=210
Spawn gate cooldown check: system_id=SYS-001 current_day=210 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=210 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.2503556864205718
[time_engine] action=time_advance_day_completed change=turn=210 hard_stop=None
[time_engine] action=galaxy_tick change=day=211
[time_engine] action=system_tick change=day=211
[time_engine] action=planet_station_tick change=day=211
[time_engine] action=location_tick change=day=211
[time_engine] action=npc_tick change=day=211
[time_engine] action=end_of_day_log change=day=211
Spawn gate cooldown check: system_id=SYS-001 current_day=211 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=211 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.1799818408640833
[time_engine] action=time_advance_day_completed change=turn=211 hard_stop=None
[time_engine] action=galaxy_tick change=day=212
[time_engine] action=system_tick change=day=212
[time_engine] action=planet_station_tick change=day=212
[time_engine] action=location_tick change=day=212
[time_engine] action=npc_tick change=day=212
[time_engine] action=end_of_day_log change=day=212
Spawn gate cooldown check: system_id=SYS-001 current_day=212 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=212 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.2471935132424954
[time_engine] action=time_advance_day_completed change=turn=212 hard_stop=None
[time_engine] action=galaxy_tick change=day=213
[time_engine] action=system_tick change=day=213
[time_engine] action=planet_station_tick change=day=213
[time_engine] action=location_tick change=day=213
[time_engine] action=npc_tick change=day=213
[time_engine] action=end_of_day_log change=day=213
Spawn gate cooldown check: system_id=SYS-001 current_day=213 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=213 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.10520872403149129
[time_engine] action=time_advance_day_completed change=turn=213 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=213 days=1 reason=travel:TRAVEL-SYS-005:SYS-001:SYS-001-DST-01:163:auto_route
[time_engine] action=galaxy_tick change=day=214
[time_engine] action=system_tick change=day=214
[time_engine] action=planet_station_tick change=day=214
[time_engine] action=location_tick change=day=214
[time_engine] action=npc_tick change=day=214
[time_engine] action=end_of_day_log change=day=214
Spawn gate cooldown check: system_id=SYS-001 current_day=214 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=214 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.53759444700266
[time_engine] action=time_advance_day_completed change=turn=214 hard_stop=None
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 163, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 50.07785749565051, "distance_ly_ceiled": 51, "inter_system": true, "target_destination_id": "SYS-001-DST-01", "target_system_id": "SYS-001", "travel_id": "TRAVEL-SYS-005:SYS-001:SYS-001-DST-01:163:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 163, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 4, "fuel_capacity": 55, "fuel_cost": 51, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-005:SYS-001:SYS-001-DST-01:163:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 163, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 51, "days_requested": 51, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-005:SYS-001:SYS-001-DST-01:163:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 214, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 214, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 1, "travel_id": "TRAVEL-SYS-005:SYS-001:SYS-001-DST-01:163:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 214, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-005:SYS-001:SYS-001-DST-01:163:auto_route_enc_0", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 214, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-001:SYS-001-DST-01:163:auto_route_enc_0", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": ["attack_plus_one_high_tr_delta"], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-005:SYS-001:SYS-001-DST-01:163:auto_route_enc_0ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [2, 5, 2], "weights_after_notoriety": [2, 5, 2], "weights_after_reputation": [2, 5, 2], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 214, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-005:SYS-001:SYS-001-DST-01:163:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 214, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 4321, "destination_id": "SYS-001-DST-01", "location_id": "SYS-001-DST-01", "system_id": "SYS-001"}, "turn_after": 214, "turn_before": 163, "version": "0.11.0"}
You have arrived in Ion.
Intra-system destinations:
  1) SYS-001-DST-01 Ion 1
  2) SYS-001-DST-02 Ion 2
  3) SYS-001-DST-03 Ion 3
  4) SYS-001-DST-04 Ion 4
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
Select location index: 2
Entered location: SYS-001-DST-01-LOC-market
MARKET PROFILE
  System: SYS-001
  Destination: SYS-001-DST-01
  Primary economy: industrial
  Active situations: none
  ENERGY: produced=['high_density_fuel', 'power_cells'] consumed=[] neutral=[]
  MACHINERY: produced=['automated_factories', 'military_hardware'] consumed=[] neutral=[]
  MEDICINE: produced=[] consumed=[] neutral=['designer_drugs', 'field_stimulants']
  METAL: produced=[] consumed=['decorative_metals', 'precision_alloys'] neutral=[]
  ORE: produced=[] consumed=['copper_ore', 'rare_earth_ore'] neutral=[]
  PARTS: produced=['electronic_components', 'mechanical_parts'] consumed=[] neutral=[]
MARKET SKUS
  automated_factories | Automated Factories | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  copper_ore | Copper Ore | buy=156 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  decorative_metals | Decorative Metals | buy=264 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  designer_drugs | Designer Drugs | buy=300 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  electronic_components | Electronic Components | buy=144 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  field_stimulants | Field Stimulants | buy=240 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  heritage_cuisine | heritage_cuisine | buy=-- | sell=-- | cargo=5 | legality=-- | risk=--
  high_density_fuel | High-Density Fuel | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  mechanical_parts | Mechanical Parts | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  military_hardware | Military Hardware | buy=269 | sell=-- | cargo=0 | legality=LEGAL | risk=High
  power_cells | Power Cells | buy=144 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  precision_alloys | Precision Alloys | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  rare_earth_ore | Rare Earth Ore | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 3
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
[time_engine] action=time_advance_requested change=start_turn=214 days=1 reason=travel:TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:214:auto_route
[time_engine] action=galaxy_tick change=day=215
[time_engine] action=system_tick change=day=215
[time_engine] action=planet_station_tick change=day=215
[time_engine] action=location_tick change=day=215
[time_engine] action=npc_tick change=day=215
[time_engine] action=end_of_day_log change=day=215
Spawn gate cooldown check: system_id=SYS-001 current_day=215 cooldown_until=187 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=215 cooldown_until=187 reason=spawn_gate_roll_failed spawn_gate_roll=0.9081706205049256
[time_engine] action=time_advance_day_completed change=turn=215 hard_stop=None
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 214, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-001-DST-02", "target_system_id": "SYS-001", "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:214:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 214, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 4, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:214:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 214, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:214:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 215, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 215, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 3, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:214:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 215, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:214:auto_route_enc_1", "handler_payload": {"npc_outcome": "attack"}, "next_handler": "combat_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 215, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:214:auto_route_enc_1", "resolver_outcome": {"outcome": "max_rounds", "resolver": "combat", "rounds": 3, "winner": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 215, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:214:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 215, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:214:auto_route_enc_2", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 215, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:214:auto_route_enc_2", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": ["attack_plus_one_high_tr_delta"], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:214:auto_route_enc_2ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [2, 5, 2], "weights_after_notoriety": [2, 5, 2], "weights_after_reputation": [2, 5, 2], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 215, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:214:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 215, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:214:auto_route_enc_3", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 215, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:214:auto_route_enc_3", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:214:auto_route_enc_3ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 215, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-02:214:auto_route_enc_3", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 215, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 4321, "destination_id": "SYS-001-DST-02", "location_id": "SYS-001-DST-02", "system_id": "SYS-001"}, "turn_after": 215, "turn_before": 214, "version": "0.11.0"}
DESTINATION: Ion 2 (SYS-001)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 4
1) customs_inspection Customs Inspection
2) refuel Refuel
3) Back
Select destination action index: 2
requested_units: 55
{"active_encounter_count": 0, "command_type": "destination_action", "error": null, "events": [{"command_type": "destination_action", "detail": {"command_type": "destination_action"}, "stage": "start", "subsystem": "engine", "turn": 215, "world_seed": 12345}, {"command_type": "destination_action", "detail": {"action_id": "refuel", "result": {"credits": 4066, "current_fuel": 55, "ok": true, "reason": "ok", "total_cost": 255, "units_purchased": 51}, "result_summary": {"credits_after": 4066, "credits_before": 4321, "fuel_after": 55, "fuel_before": 4, "reason": "ok", "result_ok": true, "total_cost": 255, "unit_price": 5, "units_purchased": 51}}, "stage": "destination_action", "subsystem": "interaction_layer", "turn": 215, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 4066, "destination_id": "SYS-001-DST-02", "location_id": "SYS-001-DST-02", "system_id": "SYS-001"}, "turn_after": 215, "turn_before": 215, "version": "0.11.0"}
1) customs_inspection Customs Inspection
2) refuel Refuel
3) Back
Select destination action index: 3
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
Select location index: 2
Entered location: SYS-001-DST-02-LOC-market
MARKET PROFILE
  System: SYS-001
  Destination: SYS-001-DST-02
  Primary economy: agricultural
  Active situations: none
  CHEMICALS: produced=['industrial_chemicals'] consumed=[] neutral=[]
  ENERGY: produced=[] consumed=['experimental_reactors'] neutral=[]
  FOOD: produced=['luxury_fresh_produce'] consumed=[] neutral=[]
  METAL: produced=[] consumed=['precision_alloys'] neutral=[]
  PARTS: produced=[] consumed=['mechanical_parts'] neutral=[]
MARKET SKUS
  experimental_reactors | Experimental Reactors | buy=504 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  heritage_cuisine | Heritage Cuisine | buy=-- | sell=91 | cargo=5 | legality=LEGAL | risk=Medium
  industrial_chemicals | Industrial Chemicals | buy=120 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  luxury_fresh_produce | Luxury Fresh Produce | buy=96 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  mechanical_parts | Mechanical Parts | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  precision_alloys | Precision Alloys | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 1
1) experimental_reactors Experimental Reactors price=504 legality=LEGAL risk=Medium
2) industrial_chemicals Industrial Chemicals price=120 legality=LEGAL risk=Medium
3) luxury_fresh_produce Luxury Fresh Produce price=96 legality=LEGAL risk=Medium
4) mechanical_parts Mechanical Parts price=192 legality=LEGAL risk=Medium
5) precision_alloys Precision Alloys price=288 legality=LEGAL risk=Medium
Select buy sku index: 3
Quantity: 30
{"active_encounter_count": 0, "command_type": "market_buy", "error": null, "events": [{"command_type": "market_buy", "detail": {"command_type": "market_buy"}, "stage": "start", "subsystem": "engine", "turn": 215, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 215, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"action": "buy", "cargo_after": 30, "credits_after": 1186, "credits_before": 4066, "quantity": 30, "sku_id": "luxury_fresh_produce", "total_cost": 2880, "unit_price": 96}, "stage": "market_trade", "subsystem": "market", "turn": 215, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 1186, "destination_id": "SYS-001-DST-02", "location_id": "SYS-001-DST-02-LOC-market", "system_id": "SYS-001"}, "turn_after": 215, "turn_before": 215, "version": "0.11.0"}
MARKET PROFILE
  System: SYS-001
  Destination: SYS-001-DST-02
  Primary economy: agricultural
  Active situations: none
  CHEMICALS: produced=['industrial_chemicals'] consumed=[] neutral=[]
  ENERGY: produced=[] consumed=['experimental_reactors'] neutral=[]
  FOOD: produced=['luxury_fresh_produce'] consumed=[] neutral=[]
  METAL: produced=[] consumed=['precision_alloys'] neutral=[]
  PARTS: produced=[] consumed=['mechanical_parts'] neutral=[]
MARKET SKUS
  experimental_reactors | Experimental Reactors | buy=504 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  heritage_cuisine | Heritage Cuisine | buy=-- | sell=91 | cargo=5 | legality=LEGAL | risk=Medium
  industrial_chemicals | Industrial Chemicals | buy=120 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  luxury_fresh_produce | Luxury Fresh Produce | buy=96 | sell=96 | cargo=30 | legality=LEGAL | risk=Medium
  mechanical_parts | Mechanical Parts | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  precision_alloys | Precision Alloys | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 3
Returned to destination: SYS-001-DST-02
DESTINATION: Ion 2 (SYS-001)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 1
PLAYER / SHIP INFO
  Credits: 1186
  Fuel: 55/55
  Cargo manifest: {'heritage_cuisine': 5, 'luxury_fresh_produce': 30}
  Reputation: 50 band=0
  Heat: 0
  Notoriety: 0 band=-2
  Arrest state: free
  Warrants: []
  Location: SYS-001 / SYS-001-DST-02 / SYS-001-DST-02
  Turn: 215
  Active crew: []
  Active missions: []
ONGOING COSTS
  Insurance: 0
  Warehouse rental: 0
  Crew wages: 0
  Total recurring cost: 0
WAREHOUSE RENTALS
  none
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
Select location index: 2
Entered location: SYS-001-DST-02-LOC-market
MARKET PROFILE
  System: SYS-001
  Destination: SYS-001-DST-02
  Primary economy: agricultural
  Active situations: none
  CHEMICALS: produced=['industrial_chemicals'] consumed=[] neutral=[]
  ENERGY: produced=[] consumed=['experimental_reactors'] neutral=[]
  FOOD: produced=['luxury_fresh_produce'] consumed=[] neutral=[]
  METAL: produced=[] consumed=['precision_alloys'] neutral=[]
  PARTS: produced=[] consumed=['mechanical_parts'] neutral=[]
MARKET SKUS
  experimental_reactors | Experimental Reactors | buy=504 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  heritage_cuisine | Heritage Cuisine | buy=-- | sell=91 | cargo=5 | legality=LEGAL | risk=Medium
  industrial_chemicals | Industrial Chemicals | buy=120 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  luxury_fresh_produce | Luxury Fresh Produce | buy=96 | sell=96 | cargo=30 | legality=LEGAL | risk=Medium
  mechanical_parts | Mechanical Parts | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  precision_alloys | Precision Alloys | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 1
1) experimental_reactors Experimental Reactors price=504 legality=LEGAL risk=Medium
2) industrial_chemicals Industrial Chemicals price=120 legality=LEGAL risk=Medium
3) luxury_fresh_produce Luxury Fresh Produce price=96 legality=LEGAL risk=Medium
4) mechanical_parts Mechanical Parts price=192 legality=LEGAL risk=Medium
5) precision_alloys Precision Alloys price=288 legality=LEGAL risk=Medium
Select buy sku index: 3
Quantity: 10
{"active_encounter_count": 0, "command_type": "market_buy", "error": null, "events": [{"command_type": "market_buy", "detail": {"command_type": "market_buy"}, "stage": "start", "subsystem": "engine", "turn": 215, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 215, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"action": "buy", "cargo_after": 40, "credits_after": 226, "credits_before": 1186, "quantity": 10, "sku_id": "luxury_fresh_produce", "total_cost": 960, "unit_price": 96}, "stage": "market_trade", "subsystem": "market", "turn": 215, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 226, "destination_id": "SYS-001-DST-02", "location_id": "SYS-001-DST-02-LOC-market", "system_id": "SYS-001"}, "turn_after": 215, "turn_before": 215, "version": "0.11.0"}
MARKET PROFILE
  System: SYS-001
  Destination: SYS-001-DST-02
  Primary economy: agricultural
  Active situations: none
  CHEMICALS: produced=['industrial_chemicals'] consumed=[] neutral=[]
  ENERGY: produced=[] consumed=['experimental_reactors'] neutral=[]
  FOOD: produced=['luxury_fresh_produce'] consumed=[] neutral=[]
  METAL: produced=[] consumed=['precision_alloys'] neutral=[]
  PARTS: produced=[] consumed=['mechanical_parts'] neutral=[]
MARKET SKUS
  experimental_reactors | Experimental Reactors | buy=504 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  heritage_cuisine | Heritage Cuisine | buy=-- | sell=91 | cargo=5 | legality=LEGAL | risk=Medium
  industrial_chemicals | Industrial Chemicals | buy=120 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  luxury_fresh_produce | Luxury Fresh Produce | buy=96 | sell=96 | cargo=40 | legality=LEGAL | risk=Medium
  mechanical_parts | Mechanical Parts | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  precision_alloys | Precision Alloys | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 3
Returned to destination: SYS-001-DST-02
DESTINATION: Ion 2 (SYS-001)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 1
PLAYER / SHIP INFO
  Credits: 226
  Fuel: 55/55
  Cargo manifest: {'heritage_cuisine': 5, 'luxury_fresh_produce': 40}
  Reputation: 50 band=0
  Heat: 0
  Notoriety: 0 band=-2
  Arrest state: free
  Warrants: []
  Location: SYS-001 / SYS-001-DST-02 / SYS-001-DST-02
  Turn: 215
  Active crew: []
  Active missions: []
ONGOING COSTS
  Insurance: 0
  Warehouse rental: 0
  Crew wages: 0
  Total recurring cost: 0
WAREHOUSE RENTALS
  none
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
Travel mode: 1
1) SYS-004 Flux distance_ly=51.844 government=fascist population=4 destinations=4 active_situations=[]
2) SYS-005 Beacon distance_ly=50.078 government=corporate_authority population=3 destinations=4 active_situations=[]
Select target system index: 2
[time_engine] action=time_advance_requested change=start_turn=215 days=10 reason=travel:TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:215:auto_route
[time_engine] action=galaxy_tick change=day=216
[time_engine] action=system_tick change=day=216
[time_engine] action=planet_station_tick change=day=216
[time_engine] action=location_tick change=day=216
[time_engine] action=npc_tick change=day=216
[time_engine] action=end_of_day_log change=day=216
Spawn gate cooldown check: system_id=SYS-005 current_day=216 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=216 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.737350484217202
[time_engine] action=time_advance_day_completed change=turn=216 hard_stop=None
[time_engine] action=galaxy_tick change=day=217
[time_engine] action=system_tick change=day=217
[time_engine] action=planet_station_tick change=day=217
[time_engine] action=location_tick change=day=217
[time_engine] action=npc_tick change=day=217
[time_engine] action=end_of_day_log change=day=217
Spawn gate cooldown check: system_id=SYS-005 current_day=217 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=217 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.6637141691412191
[time_engine] action=time_advance_day_completed change=turn=217 hard_stop=None
[time_engine] action=galaxy_tick change=day=218
[time_engine] action=system_tick change=day=218
[time_engine] action=planet_station_tick change=day=218
[time_engine] action=location_tick change=day=218
[time_engine] action=npc_tick change=day=218
[time_engine] action=end_of_day_log change=day=218
Spawn gate cooldown check: system_id=SYS-005 current_day=218 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=218 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.13725197054737792
[time_engine] action=time_advance_day_completed change=turn=218 hard_stop=None
[time_engine] action=galaxy_tick change=day=219
[time_engine] action=system_tick change=day=219
[time_engine] action=planet_station_tick change=day=219
[time_engine] action=location_tick change=day=219
[time_engine] action=npc_tick change=day=219
[time_engine] action=end_of_day_log change=day=219
Spawn gate cooldown check: system_id=SYS-005 current_day=219 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=219 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.26598102119194633
[time_engine] action=time_advance_day_completed change=turn=219 hard_stop=None
[time_engine] action=galaxy_tick change=day=220
[time_engine] action=system_tick change=day=220
[time_engine] action=planet_station_tick change=day=220
[time_engine] action=location_tick change=day=220
[time_engine] action=npc_tick change=day=220
[time_engine] action=end_of_day_log change=day=220
Spawn gate cooldown check: system_id=SYS-005 current_day=220 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=220 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.7664385828726249
[time_engine] action=time_advance_day_completed change=turn=220 hard_stop=None
[time_engine] action=galaxy_tick change=day=221
[time_engine] action=system_tick change=day=221
[time_engine] action=planet_station_tick change=day=221
[time_engine] action=location_tick change=day=221
[time_engine] action=npc_tick change=day=221
[time_engine] action=end_of_day_log change=day=221
Spawn gate cooldown check: system_id=SYS-005 current_day=221 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=221 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.32322452107593425
[time_engine] action=time_advance_day_completed change=turn=221 hard_stop=None
[time_engine] action=galaxy_tick change=day=222
[time_engine] action=system_tick change=day=222
[time_engine] action=planet_station_tick change=day=222
[time_engine] action=location_tick change=day=222
[time_engine] action=npc_tick change=day=222
[time_engine] action=end_of_day_log change=day=222
Spawn gate cooldown check: system_id=SYS-005 current_day=222 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=222 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.8329416671040059
[time_engine] action=time_advance_day_completed change=turn=222 hard_stop=None
[time_engine] action=galaxy_tick change=day=223
[time_engine] action=system_tick change=day=223
[time_engine] action=planet_station_tick change=day=223
[time_engine] action=location_tick change=day=223
[time_engine] action=npc_tick change=day=223
[time_engine] action=end_of_day_log change=day=223
Spawn gate cooldown check: system_id=SYS-005 current_day=223 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=223 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.175971568248096
[time_engine] action=time_advance_day_completed change=turn=223 hard_stop=None
[time_engine] action=galaxy_tick change=day=224
[time_engine] action=system_tick change=day=224
[time_engine] action=planet_station_tick change=day=224
[time_engine] action=location_tick change=day=224
[time_engine] action=npc_tick change=day=224
[time_engine] action=end_of_day_log change=day=224
Spawn gate cooldown check: system_id=SYS-005 current_day=224 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=224 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.49087397913801933
[time_engine] action=time_advance_day_completed change=turn=224 hard_stop=None
[time_engine] action=galaxy_tick change=day=225
[time_engine] action=system_tick change=day=225
[time_engine] action=planet_station_tick change=day=225
[time_engine] action=location_tick change=day=225
[time_engine] action=npc_tick change=day=225
[time_engine] action=end_of_day_log change=day=225
Spawn gate cooldown check: system_id=SYS-005 current_day=225 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=225 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.2627165452916018
[time_engine] action=time_advance_day_completed change=turn=225 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=225 days=10 reason=travel:TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:215:auto_route
[time_engine] action=galaxy_tick change=day=226
[time_engine] action=system_tick change=day=226
[time_engine] action=planet_station_tick change=day=226
[time_engine] action=location_tick change=day=226
[time_engine] action=npc_tick change=day=226
[time_engine] action=end_of_day_log change=day=226
Spawn gate cooldown check: system_id=SYS-005 current_day=226 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=226 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.44217787467170244
[time_engine] action=time_advance_day_completed change=turn=226 hard_stop=None
[time_engine] action=galaxy_tick change=day=227
[time_engine] action=system_tick change=day=227
[time_engine] action=planet_station_tick change=day=227
[time_engine] action=location_tick change=day=227
[time_engine] action=npc_tick change=day=227
[time_engine] action=end_of_day_log change=day=227
Spawn gate cooldown check: system_id=SYS-005 current_day=227 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=227 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.6202847079045786
[time_engine] action=time_advance_day_completed change=turn=227 hard_stop=None
[time_engine] action=galaxy_tick change=day=228
[time_engine] action=system_tick change=day=228
[time_engine] action=planet_station_tick change=day=228
[time_engine] action=location_tick change=day=228
[time_engine] action=npc_tick change=day=228
[time_engine] action=end_of_day_log change=day=228
Spawn gate cooldown check: system_id=SYS-005 current_day=228 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=228 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.3674958730135899
[time_engine] action=time_advance_day_completed change=turn=228 hard_stop=None
[time_engine] action=galaxy_tick change=day=229
[time_engine] action=system_tick change=day=229
[time_engine] action=planet_station_tick change=day=229
[time_engine] action=location_tick change=day=229
[time_engine] action=npc_tick change=day=229
[time_engine] action=end_of_day_log change=day=229
Spawn gate cooldown check: system_id=SYS-005 current_day=229 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=229 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.6921033158755601
[time_engine] action=time_advance_day_completed change=turn=229 hard_stop=None
[time_engine] action=galaxy_tick change=day=230
[time_engine] action=system_tick change=day=230
[time_engine] action=planet_station_tick change=day=230
[time_engine] action=location_tick change=day=230
[time_engine] action=npc_tick change=day=230
[time_engine] action=end_of_day_log change=day=230
Spawn gate cooldown check: system_id=SYS-005 current_day=230 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=230 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.3101707619568518
[time_engine] action=time_advance_day_completed change=turn=230 hard_stop=None
[time_engine] action=galaxy_tick change=day=231
[time_engine] action=system_tick change=day=231
[time_engine] action=planet_station_tick change=day=231
[time_engine] action=location_tick change=day=231
[time_engine] action=npc_tick change=day=231
[time_engine] action=end_of_day_log change=day=231
Spawn gate cooldown check: system_id=SYS-005 current_day=231 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=231 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.3436747979763266
[time_engine] action=time_advance_day_completed change=turn=231 hard_stop=None
[time_engine] action=galaxy_tick change=day=232
[time_engine] action=system_tick change=day=232
[time_engine] action=planet_station_tick change=day=232
[time_engine] action=location_tick change=day=232
[time_engine] action=npc_tick change=day=232
[time_engine] action=end_of_day_log change=day=232
Spawn gate cooldown check: system_id=SYS-005 current_day=232 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=232 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.6195337016265478
[time_engine] action=time_advance_day_completed change=turn=232 hard_stop=None
[time_engine] action=galaxy_tick change=day=233
[time_engine] action=system_tick change=day=233
[time_engine] action=planet_station_tick change=day=233
[time_engine] action=location_tick change=day=233
[time_engine] action=npc_tick change=day=233
[time_engine] action=end_of_day_log change=day=233
Spawn gate cooldown check: system_id=SYS-005 current_day=233 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=233 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.3615928339775121
[time_engine] action=time_advance_day_completed change=turn=233 hard_stop=None
[time_engine] action=galaxy_tick change=day=234
[time_engine] action=system_tick change=day=234
[time_engine] action=planet_station_tick change=day=234
[time_engine] action=location_tick change=day=234
[time_engine] action=npc_tick change=day=234
[time_engine] action=end_of_day_log change=day=234
Spawn gate cooldown check: system_id=SYS-005 current_day=234 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=234 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.801838835554821
[time_engine] action=time_advance_day_completed change=turn=234 hard_stop=None
[time_engine] action=galaxy_tick change=day=235
[time_engine] action=system_tick change=day=235
[time_engine] action=planet_station_tick change=day=235
[time_engine] action=location_tick change=day=235
[time_engine] action=npc_tick change=day=235
[time_engine] action=end_of_day_log change=day=235
Spawn gate cooldown check: system_id=SYS-005 current_day=235 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=235 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.4027934936580997
[time_engine] action=time_advance_day_completed change=turn=235 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=235 days=10 reason=travel:TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:215:auto_route
[time_engine] action=galaxy_tick change=day=236
[time_engine] action=system_tick change=day=236
[time_engine] action=planet_station_tick change=day=236
[time_engine] action=location_tick change=day=236
[time_engine] action=npc_tick change=day=236
[time_engine] action=end_of_day_log change=day=236
Spawn gate cooldown check: system_id=SYS-005 current_day=236 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=236 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.17829383928794296
[time_engine] action=time_advance_day_completed change=turn=236 hard_stop=None
[time_engine] action=galaxy_tick change=day=237
[time_engine] action=system_tick change=day=237
[time_engine] action=planet_station_tick change=day=237
[time_engine] action=location_tick change=day=237
[time_engine] action=npc_tick change=day=237
[time_engine] action=end_of_day_log change=day=237
Spawn gate cooldown check: system_id=SYS-005 current_day=237 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=237 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.12882707386045789
[time_engine] action=time_advance_day_completed change=turn=237 hard_stop=None
[time_engine] action=galaxy_tick change=day=238
[time_engine] action=system_tick change=day=238
[time_engine] action=planet_station_tick change=day=238
[time_engine] action=location_tick change=day=238
[time_engine] action=npc_tick change=day=238
[time_engine] action=end_of_day_log change=day=238
Spawn gate cooldown check: system_id=SYS-005 current_day=238 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=238 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.39515220243548266
[time_engine] action=time_advance_day_completed change=turn=238 hard_stop=None
[time_engine] action=galaxy_tick change=day=239
[time_engine] action=system_tick change=day=239
[time_engine] action=planet_station_tick change=day=239
[time_engine] action=location_tick change=day=239
[time_engine] action=npc_tick change=day=239
[time_engine] action=end_of_day_log change=day=239
Spawn gate cooldown check: system_id=SYS-005 current_day=239 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=239 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.3783414495469474
[time_engine] action=time_advance_day_completed change=turn=239 hard_stop=None
[time_engine] action=galaxy_tick change=day=240
[time_engine] action=system_tick change=day=240
[time_engine] action=planet_station_tick change=day=240
[time_engine] action=location_tick change=day=240
[time_engine] action=npc_tick change=day=240
[time_engine] action=end_of_day_log change=day=240
Spawn gate cooldown check: system_id=SYS-005 current_day=240 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=240 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.7886066734438988
[time_engine] action=time_advance_day_completed change=turn=240 hard_stop=None
[time_engine] action=galaxy_tick change=day=241
[time_engine] action=system_tick change=day=241
[time_engine] action=planet_station_tick change=day=241
[time_engine] action=location_tick change=day=241
[time_engine] action=npc_tick change=day=241
[time_engine] action=end_of_day_log change=day=241
Spawn gate cooldown check: system_id=SYS-005 current_day=241 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=241 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.5870763098715139
[time_engine] action=time_advance_day_completed change=turn=241 hard_stop=None
[time_engine] action=galaxy_tick change=day=242
[time_engine] action=system_tick change=day=242
[time_engine] action=planet_station_tick change=day=242
[time_engine] action=location_tick change=day=242
[time_engine] action=npc_tick change=day=242
[time_engine] action=end_of_day_log change=day=242
Spawn gate cooldown check: system_id=SYS-005 current_day=242 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=242 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.4292110450799198
[time_engine] action=time_advance_day_completed change=turn=242 hard_stop=None
[time_engine] action=galaxy_tick change=day=243
[time_engine] action=system_tick change=day=243
[time_engine] action=planet_station_tick change=day=243
[time_engine] action=location_tick change=day=243
[time_engine] action=npc_tick change=day=243
[time_engine] action=end_of_day_log change=day=243
Spawn gate cooldown check: system_id=SYS-005 current_day=243 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=243 cooldown_until=162 reason=spawn_gate_roll_failed spawn_gate_roll=0.2533433600506382
[time_engine] action=time_advance_day_completed change=turn=243 hard_stop=None
[time_engine] action=galaxy_tick change=day=244
[time_engine] action=system_tick change=day=244
[time_engine] action=planet_station_tick change=day=244
[time_engine] action=location_tick change=day=244
[time_engine] action=npc_tick change=day=244
[time_engine] action=end_of_day_log change=day=244
Spawn gate cooldown check: system_id=SYS-005 current_day=244 cooldown_until=162 skipped=false reason=cooldown_clear
Spawn gate type+tier selected: system_id=SYS-005 current_day=244 selected_type=situation selected_tier=2 spawn_type_roll=0.14819958344248185 severity_roll=0.4733845693925144
Spawn gate candidate filter: system_id=SYS-005 selected_type=situation selected_tier=2 candidates_found=12
Situation added: religious_revival system=SYS-005 scope=system
Spawn gate cooldown set: system_id=SYS-005 current_day=244 cooldown_until=249 generated_any=true reason=spawn_gate_generation
[time_engine] action=time_advance_day_completed change=turn=244 hard_stop=None
[time_engine] action=galaxy_tick change=day=245
[time_engine] action=system_tick change=day=245
[time_engine] action=planet_station_tick change=day=245
[time_engine] action=location_tick change=day=245
[time_engine] action=npc_tick change=day=245
[time_engine] action=end_of_day_log change=day=245
Spawn gate cooldown check: system_id=SYS-005 current_day=245 cooldown_until=249 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=245 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=245 days=10 reason=travel:TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:215:auto_route
[time_engine] action=galaxy_tick change=day=246
[time_engine] action=system_tick change=day=246
[time_engine] action=planet_station_tick change=day=246
[time_engine] action=location_tick change=day=246
[time_engine] action=npc_tick change=day=246
[time_engine] action=end_of_day_log change=day=246
Spawn gate cooldown check: system_id=SYS-005 current_day=246 cooldown_until=249 skipped=true reason=cooldown_active
Situation expired: religious_revival system=SYS-005
[time_engine] action=time_advance_day_completed change=turn=246 hard_stop=None
[time_engine] action=galaxy_tick change=day=247
[time_engine] action=system_tick change=day=247
[time_engine] action=planet_station_tick change=day=247
[time_engine] action=location_tick change=day=247
[time_engine] action=npc_tick change=day=247
[time_engine] action=end_of_day_log change=day=247
Spawn gate cooldown check: system_id=SYS-005 current_day=247 cooldown_until=249 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=247 hard_stop=None
[time_engine] action=galaxy_tick change=day=248
[time_engine] action=system_tick change=day=248
[time_engine] action=planet_station_tick change=day=248
[time_engine] action=location_tick change=day=248
[time_engine] action=npc_tick change=day=248
[time_engine] action=end_of_day_log change=day=248
Spawn gate cooldown check: system_id=SYS-005 current_day=248 cooldown_until=249 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=248 hard_stop=None
[time_engine] action=galaxy_tick change=day=249
[time_engine] action=system_tick change=day=249
[time_engine] action=planet_station_tick change=day=249
[time_engine] action=location_tick change=day=249
[time_engine] action=npc_tick change=day=249
[time_engine] action=end_of_day_log change=day=249
Spawn gate cooldown check: system_id=SYS-005 current_day=249 cooldown_until=249 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=249 hard_stop=None
[time_engine] action=galaxy_tick change=day=250
[time_engine] action=system_tick change=day=250
[time_engine] action=planet_station_tick change=day=250
[time_engine] action=location_tick change=day=250
[time_engine] action=npc_tick change=day=250
[time_engine] action=end_of_day_log change=day=250
Spawn gate cooldown check: system_id=SYS-005 current_day=250 cooldown_until=249 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=250 cooldown_until=249 reason=spawn_gate_roll_failed spawn_gate_roll=0.5545973526208674
[time_engine] action=time_advance_day_completed change=turn=250 hard_stop=None
[time_engine] action=galaxy_tick change=day=251
[time_engine] action=system_tick change=day=251
[time_engine] action=planet_station_tick change=day=251
[time_engine] action=location_tick change=day=251
[time_engine] action=npc_tick change=day=251
[time_engine] action=end_of_day_log change=day=251
Spawn gate cooldown check: system_id=SYS-005 current_day=251 cooldown_until=249 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=251 cooldown_until=249 reason=spawn_gate_roll_failed spawn_gate_roll=0.7207150327990303
[time_engine] action=time_advance_day_completed change=turn=251 hard_stop=None
[time_engine] action=galaxy_tick change=day=252
[time_engine] action=system_tick change=day=252
[time_engine] action=planet_station_tick change=day=252
[time_engine] action=location_tick change=day=252
[time_engine] action=npc_tick change=day=252
[time_engine] action=end_of_day_log change=day=252
Spawn gate cooldown check: system_id=SYS-005 current_day=252 cooldown_until=249 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=252 cooldown_until=249 reason=spawn_gate_roll_failed spawn_gate_roll=0.4713163314868347
[time_engine] action=time_advance_day_completed change=turn=252 hard_stop=None
[time_engine] action=galaxy_tick change=day=253
[time_engine] action=system_tick change=day=253
[time_engine] action=planet_station_tick change=day=253
[time_engine] action=location_tick change=day=253
[time_engine] action=npc_tick change=day=253
[time_engine] action=end_of_day_log change=day=253
Spawn gate cooldown check: system_id=SYS-005 current_day=253 cooldown_until=249 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=253 cooldown_until=249 reason=spawn_gate_roll_failed spawn_gate_roll=0.7242791235646957
[time_engine] action=time_advance_day_completed change=turn=253 hard_stop=None
[time_engine] action=galaxy_tick change=day=254
[time_engine] action=system_tick change=day=254
[time_engine] action=planet_station_tick change=day=254
[time_engine] action=location_tick change=day=254
[time_engine] action=npc_tick change=day=254
[time_engine] action=end_of_day_log change=day=254
Spawn gate cooldown check: system_id=SYS-005 current_day=254 cooldown_until=249 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=254 cooldown_until=249 reason=spawn_gate_roll_failed spawn_gate_roll=0.23141239799066482
[time_engine] action=time_advance_day_completed change=turn=254 hard_stop=None
[time_engine] action=galaxy_tick change=day=255
[time_engine] action=system_tick change=day=255
[time_engine] action=planet_station_tick change=day=255
[time_engine] action=location_tick change=day=255
[time_engine] action=npc_tick change=day=255
[time_engine] action=end_of_day_log change=day=255
Spawn gate cooldown check: system_id=SYS-005 current_day=255 cooldown_until=249 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=255 cooldown_until=249 reason=spawn_gate_roll_failed spawn_gate_roll=0.29740490281876975
[time_engine] action=time_advance_day_completed change=turn=255 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=255 days=10 reason=travel:TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:215:auto_route
[time_engine] action=galaxy_tick change=day=256
[time_engine] action=system_tick change=day=256
[time_engine] action=planet_station_tick change=day=256
[time_engine] action=location_tick change=day=256
[time_engine] action=npc_tick change=day=256
[time_engine] action=end_of_day_log change=day=256
Spawn gate cooldown check: system_id=SYS-005 current_day=256 cooldown_until=249 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=256 cooldown_until=249 reason=spawn_gate_roll_failed spawn_gate_roll=0.126116833627257
[time_engine] action=time_advance_day_completed change=turn=256 hard_stop=None
[time_engine] action=galaxy_tick change=day=257
[time_engine] action=system_tick change=day=257
[time_engine] action=planet_station_tick change=day=257
[time_engine] action=location_tick change=day=257
[time_engine] action=npc_tick change=day=257
[time_engine] action=end_of_day_log change=day=257
Spawn gate cooldown check: system_id=SYS-005 current_day=257 cooldown_until=249 skipped=false reason=cooldown_clear
Spawn gate type+tier selected: system_id=SYS-005 current_day=257 selected_type=event selected_tier=3 spawn_type_roll=0.8976769579275737 severity_roll=0.8192214753337846
Spawn gate candidate filter: system_id=SYS-005 selected_type=event selected_tier=3 candidates_found=9
Event added: alien_science_defector system=SYS-005
Structural detection: origin_system_id=SYS-005 event_id=alien_science_defector current_day=257 is_structural=False
Situation added: exploration_craze system=SYS-005 scope=system
System flag add: system_id=SYS-005 event_id=alien_science_defector flag=alien_defector already_present=False
Spawn gate cooldown set: system_id=SYS-005 current_day=257 cooldown_until=262 generated_any=true reason=spawn_gate_generation
Event expired: alien_science_defector system=SYS-005
[time_engine] action=time_advance_day_completed change=turn=257 hard_stop=None
[time_engine] action=galaxy_tick change=day=258
[time_engine] action=system_tick change=day=258
[time_engine] action=planet_station_tick change=day=258
[time_engine] action=location_tick change=day=258
[time_engine] action=npc_tick change=day=258
[time_engine] action=end_of_day_log change=day=258
Spawn gate cooldown check: system_id=SYS-005 current_day=258 cooldown_until=262 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=258 hard_stop=None
[time_engine] action=galaxy_tick change=day=259
[time_engine] action=system_tick change=day=259
[time_engine] action=planet_station_tick change=day=259
[time_engine] action=location_tick change=day=259
[time_engine] action=npc_tick change=day=259
[time_engine] action=end_of_day_log change=day=259
Spawn gate cooldown check: system_id=SYS-005 current_day=259 cooldown_until=262 skipped=true reason=cooldown_active
Situation expired: exploration_craze system=SYS-005
[time_engine] action=time_advance_day_completed change=turn=259 hard_stop=None
[time_engine] action=galaxy_tick change=day=260
[time_engine] action=system_tick change=day=260
[time_engine] action=planet_station_tick change=day=260
[time_engine] action=location_tick change=day=260
[time_engine] action=npc_tick change=day=260
[time_engine] action=end_of_day_log change=day=260
Spawn gate cooldown check: system_id=SYS-005 current_day=260 cooldown_until=262 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=260 hard_stop=None
[time_engine] action=galaxy_tick change=day=261
[time_engine] action=system_tick change=day=261
[time_engine] action=planet_station_tick change=day=261
[time_engine] action=location_tick change=day=261
[time_engine] action=npc_tick change=day=261
[time_engine] action=end_of_day_log change=day=261
Spawn gate cooldown check: system_id=SYS-005 current_day=261 cooldown_until=262 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=261 hard_stop=None
[time_engine] action=galaxy_tick change=day=262
[time_engine] action=system_tick change=day=262
[time_engine] action=planet_station_tick change=day=262
[time_engine] action=location_tick change=day=262
[time_engine] action=npc_tick change=day=262
[time_engine] action=end_of_day_log change=day=262
Spawn gate cooldown check: system_id=SYS-005 current_day=262 cooldown_until=262 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=262 hard_stop=None
[time_engine] action=galaxy_tick change=day=263
[time_engine] action=system_tick change=day=263
[time_engine] action=planet_station_tick change=day=263
[time_engine] action=location_tick change=day=263
[time_engine] action=npc_tick change=day=263
[time_engine] action=end_of_day_log change=day=263
Spawn gate cooldown check: system_id=SYS-005 current_day=263 cooldown_until=262 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=263 cooldown_until=262 reason=spawn_gate_roll_failed spawn_gate_roll=0.45642115798338667
[time_engine] action=time_advance_day_completed change=turn=263 hard_stop=None
[time_engine] action=galaxy_tick change=day=264
[time_engine] action=system_tick change=day=264
[time_engine] action=planet_station_tick change=day=264
[time_engine] action=location_tick change=day=264
[time_engine] action=npc_tick change=day=264
[time_engine] action=end_of_day_log change=day=264
Spawn gate cooldown check: system_id=SYS-005 current_day=264 cooldown_until=262 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=264 cooldown_until=262 reason=spawn_gate_roll_failed spawn_gate_roll=0.7255825094221491
[time_engine] action=time_advance_day_completed change=turn=264 hard_stop=None
[time_engine] action=galaxy_tick change=day=265
[time_engine] action=system_tick change=day=265
[time_engine] action=planet_station_tick change=day=265
[time_engine] action=location_tick change=day=265
[time_engine] action=npc_tick change=day=265
[time_engine] action=end_of_day_log change=day=265
Spawn gate cooldown check: system_id=SYS-005 current_day=265 cooldown_until=262 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=265 cooldown_until=262 reason=spawn_gate_roll_failed spawn_gate_roll=0.1432860770469766
[time_engine] action=time_advance_day_completed change=turn=265 hard_stop=None
[time_engine] action=time_advance_requested change=start_turn=265 days=1 reason=travel:TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:215:auto_route
[time_engine] action=galaxy_tick change=day=266
[time_engine] action=system_tick change=day=266
[time_engine] action=planet_station_tick change=day=266
[time_engine] action=location_tick change=day=266
[time_engine] action=npc_tick change=day=266
[time_engine] action=end_of_day_log change=day=266
Spawn gate cooldown check: system_id=SYS-005 current_day=266 cooldown_until=262 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-005 current_day=266 cooldown_until=262 reason=spawn_gate_roll_failed spawn_gate_roll=0.11151645474817296
[time_engine] action=time_advance_day_completed change=turn=266 hard_stop=None
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 215, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 50.07785749565051, "distance_ly_ceiled": 51, "inter_system": true, "target_destination_id": "SYS-005-DST-01", "target_system_id": "SYS-005", "travel_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:215:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 215, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 4, "fuel_capacity": 55, "fuel_cost": 51, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:215:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 215, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 51, "days_requested": 51, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:215:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 266, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 266, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 2, "travel_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:215:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 266, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:215:auto_route_enc_0", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 266, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:215:auto_route_enc_0", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 266, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:215:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 266, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:215:auto_route_enc_4", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 266, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:215:auto_route_enc_4", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:215:auto_route_enc_4ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [2, 5, 1], "weights_after_notoriety": [2, 5, 1], "weights_after_reputation": [2, 5, 1], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 266, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-005:SYS-005-DST-01:215:auto_route_enc_4", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 266, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 226, "destination_id": "SYS-005-DST-01", "location_id": "SYS-005-DST-01", "system_id": "SYS-005"}, "turn_after": 266, "turn_before": 215, "version": "0.11.0"}
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
Select location index: 2
Entered location: SYS-005-DST-01-LOC-market
MARKET PROFILE
  System: SYS-005
  Destination: SYS-005-DST-01
  Primary economy: cultural
  Active situations: none
  DATA: produced=['encrypted_records', 'media_packages'] consumed=[] neutral=[]
  ENERGY: produced=[] consumed=['fusion_cores', 'power_cells'] neutral=[]
  FOOD: produced=[] consumed=['fresh_produce', 'spice_wine'] neutral=[]
  LUXURY: produced=['designer_goods', 'prestige_technology'] consumed=[] neutral=[]
  MACHINERY: produced=['automated_factories', 'military_hardware'] consumed=[] neutral=[]
  METAL: produced=[] consumed=['decorative_metals', 'titanium_bars'] neutral=[]
  PARTS: produced=[] consumed=['cybernetic_implants', 'mechanical_parts'] neutral=[]
  WEAPONS: produced=['ship_weapons', 'small_arms'] consumed=[] neutral=[]
MARKET SKUS
  automated_factories | Automated Factories | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  cybernetic_implants | Cybernetic Implants | buy=312 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  decorative_metals | Decorative Metals | buy=317 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  designer_goods | Designer Goods | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  encrypted_records | Encrypted Records | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  fresh_produce | Fresh Produce | buy=144 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  fusion_cores | Fusion Cores | buy=408 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  heritage_cuisine | Heritage Cuisine | buy=-- | sell=85 | cargo=5 | legality=LEGAL | risk=Medium
  luxury_fresh_produce | luxury_fresh_produce | buy=-- | sell=173 | cargo=40 | legality=LEGAL | risk=Medium
  mechanical_parts | Mechanical Parts | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  media_packages | Media Packages | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  military_hardware | Military Hardware | buy=336 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  power_cells | Power Cells | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  prestige_technology | Prestige Technology | buy=403 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  ship_weapons | Ship Weapons | buy=320 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  small_arms | Small Arms | buy=176 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  spice_wine | Spice Wine | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  titanium_bars | Titanium Bars | buy=252 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 2
1) heritage_cuisine Heritage Cuisine units=5 price=85 legality=LEGAL risk=Medium
2) luxury_fresh_produce luxury_fresh_produce units=40 price=173 legality=LEGAL risk=Medium
Select sell sku index: 2
Quantity: 40
{"active_encounter_count": 0, "command_type": "market_sell", "error": null, "events": [{"command_type": "market_sell", "detail": {"command_type": "market_sell"}, "stage": "start", "subsystem": "engine", "turn": 266, "world_seed": 12345}, {"command_type": "market_sell", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 266, "world_seed": 12345}, {"command_type": "market_sell", "detail": {"action": "sell", "cargo_after": 0, "credits_after": 7146, "credits_before": 226, "quantity": 40, "sku_id": "luxury_fresh_produce", "total_gain": 6920, "unit_price": 173}, "stage": "market_trade", "subsystem": "market", "turn": 266, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 7146, "destination_id": "SYS-005-DST-01", "location_id": "SYS-005-DST-01-LOC-market", "system_id": "SYS-005"}, "turn_after": 266, "turn_before": 266, "version": "0.11.0"}
MARKET PROFILE
  System: SYS-005
  Destination: SYS-005-DST-01
  Primary economy: cultural
  Active situations: none
  DATA: produced=['encrypted_records', 'media_packages'] consumed=[] neutral=[]
  ENERGY: produced=[] consumed=['fusion_cores', 'power_cells'] neutral=[]
  FOOD: produced=[] consumed=['fresh_produce', 'spice_wine'] neutral=[]
  LUXURY: produced=['designer_goods', 'prestige_technology'] consumed=[] neutral=[]
  MACHINERY: produced=['automated_factories', 'military_hardware'] consumed=[] neutral=[]
  METAL: produced=[] consumed=['decorative_metals', 'titanium_bars'] neutral=[]
  PARTS: produced=[] consumed=['cybernetic_implants', 'mechanical_parts'] neutral=[]
  WEAPONS: produced=['ship_weapons', 'small_arms'] consumed=[] neutral=[]
MARKET SKUS
  automated_factories | Automated Factories | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  cybernetic_implants | Cybernetic Implants | buy=312 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  decorative_metals | Decorative Metals | buy=317 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  designer_goods | Designer Goods | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  encrypted_records | Encrypted Records | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  fresh_produce | Fresh Produce | buy=144 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  fusion_cores | Fusion Cores | buy=408 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  heritage_cuisine | Heritage Cuisine | buy=-- | sell=85 | cargo=5 | legality=LEGAL | risk=Medium
  mechanical_parts | Mechanical Parts | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  media_packages | Media Packages | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  military_hardware | Military Hardware | buy=336 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  power_cells | Power Cells | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  prestige_technology | Prestige Technology | buy=403 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  ship_weapons | Ship Weapons | buy=320 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  small_arms | Small Arms | buy=176 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  spice_wine | Spice Wine | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  titanium_bars | Titanium Bars | buy=252 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 2
1) heritage_cuisine Heritage Cuisine units=5 price=85 legality=LEGAL risk=Medium
Select sell sku index: 1
Quantity: 5
{"active_encounter_count": 0, "command_type": "market_sell", "error": null, "events": [{"command_type": "market_sell", "detail": {"command_type": "market_sell"}, "stage": "start", "subsystem": "engine", "turn": 266, "world_seed": 12345}, {"command_type": "market_sell", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 266, "world_seed": 12345}, {"command_type": "market_sell", "detail": {"action": "sell", "cargo_after": 0, "credits_after": 7571, "credits_before": 7146, "quantity": 5, "sku_id": "heritage_cuisine", "total_gain": 425, "unit_price": 85}, "stage": "market_trade", "subsystem": "market", "turn": 266, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 7571, "destination_id": "SYS-005-DST-01", "location_id": "SYS-005-DST-01-LOC-market", "system_id": "SYS-005"}, "turn_after": 266, "turn_before": 266, "version": "0.11.0"}
MARKET PROFILE
  System: SYS-005
  Destination: SYS-005-DST-01
  Primary economy: cultural
  Active situations: none
  DATA: produced=['encrypted_records', 'media_packages'] consumed=[] neutral=[]
  ENERGY: produced=[] consumed=['fusion_cores', 'power_cells'] neutral=[]
  FOOD: produced=[] consumed=['fresh_produce', 'spice_wine'] neutral=[]
  LUXURY: produced=['designer_goods', 'prestige_technology'] consumed=[] neutral=[]
  MACHINERY: produced=['automated_factories', 'military_hardware'] consumed=[] neutral=[]
  METAL: produced=[] consumed=['decorative_metals', 'titanium_bars'] neutral=[]
  PARTS: produced=[] consumed=['cybernetic_implants', 'mechanical_parts'] neutral=[]
  WEAPONS: produced=['ship_weapons', 'small_arms'] consumed=[] neutral=[]
MARKET SKUS
  automated_factories | Automated Factories | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  cybernetic_implants | Cybernetic Implants | buy=312 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  decorative_metals | Decorative Metals | buy=317 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  designer_goods | Designer Goods | buy=288 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  encrypted_records | Encrypted Records | buy=160 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  fresh_produce | Fresh Produce | buy=144 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  fusion_cores | Fusion Cores | buy=408 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  mechanical_parts | Mechanical Parts | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  media_packages | Media Packages | buy=128 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  military_hardware | Military Hardware | buy=336 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  power_cells | Power Cells | buy=216 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  prestige_technology | Prestige Technology | buy=403 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  ship_weapons | Ship Weapons | buy=320 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  small_arms | Small Arms | buy=176 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  spice_wine | Spice Wine | buy=192 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  titanium_bars | Titanium Bars | buy=252 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 3
Returned to destination: SYS-005-DST-01
DESTINATION: Beacon 1 (SYS-005)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 1
PLAYER / SHIP INFO
  Credits: 7571
  Fuel: 4/55
  Cargo manifest: {}
  Reputation: 50 band=0
  Heat: 0
  Notoriety: 0 band=-2
  Arrest state: free
  Warrants: []
  Location: SYS-005 / SYS-005-DST-01 / SYS-005-DST-01
  Turn: 266
  Active crew: []
  Active missions: []
ONGOING COSTS
  Insurance: 0
  Warehouse rental: 0
  Crew wages: 0
  Total recurring cost: 0
WAREHOUSE RENTALS
  none
DESTINATION: Beacon 1 (SYS-005)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 6
{"active_encounter_count": 0, "command_type": "quit", "error": null, "events": [{"command_type": "quit", "detail": {"command_type": "quit"}, "stage": "start", "subsystem": "engine", "turn": 266, "world_seed": 12345}, {"command_type": "quit", "detail": {"quit": true}, "stage": "command", "subsystem": "engine", "turn": 266, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 7571, "destination_id": "SYS-005-DST-01", "location_id": "SYS-005-DST-01", "system_id": "SYS-005"}, "turn_after": 266, "turn_before": 266, "version": "0.11.0"}
PS D:\GitHub\EmojiSpace>