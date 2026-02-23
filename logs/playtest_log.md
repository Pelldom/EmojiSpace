
PS D:\GitHub\EmojiSpace> python .\src\run_game_engine_cli.py
Seed [12345]:
[v0.11.0][turn 0] action=engine:initialization change={"detail": {"starting_destination_marked_visited": true, "starting_system_marked_visited": true}, "stage": "initialization", "subsystem": "engine"}
[v0.11.0][turn 0] action=engine:logging change={"command_type": "set_logging", "detail": {"enabled": true, "log_path": "D:\\GitHub\\EmojiSpace\\logs\\gameplay_seed_12345.log", "truncate": true}, "stage": "logging", "subsystem": "engine", "turn": 0, "world_seed": 12345}
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
[v0.11.0][turn 0] action=engine:start change={"command_type": "enter_location", "detail": {"command_type": "enter_location"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=npc_registry change=add npc_id=NPC-952663a0
[v0.11.0][turn 0] action=npc_placement change=created location_id=SYS-001-DST-01-LOC-bar npc_id=NPC-952663a0
[v0.11.0][turn 0] action=engine:location_navigation change={"command_type": "enter_location", "detail": {"action": "enter_location", "location_id": "SYS-001-DST-01-LOC-bar", "location_type": "bar", "resolved_npc_ids": ["NPC-952663a0"]}, "stage": "location_navigation", "subsystem": "engine", "turn": 0, "world_seed": 12345}
Entered location: SYS-001-DST-01-LOC-bar
[v0.11.0][turn 0] action=engine:start change={"command_type": "list_location_npcs", "detail": {"command_type": "list_location_npcs"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=engine:location_npcs change={"command_type": "list_location_npcs", "detail": {"location_id": "SYS-001-DST-01-LOC-bar", "npcs": [{"display_name": "Bartender", "npc_id": "NPC-952663a0", "persistence_tier": 3, "role": "bartender"}]}, "stage": "location_npcs", "subsystem": "engine", "turn": 0, "world_seed": 12345}
LOCATION: SYS-001-DST-01-LOC-bar
1) Bartender (bartender)
0) Return to destination
Select NPC index: 1
[v0.11.0][turn 0] action=engine:start change={"command_type": "list_npc_interactions", "detail": {"command_type": "list_npc_interactions"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=interaction_layer:npc_interactions change={"command_type": "list_npc_interactions", "detail": {"interactions": [{"action_id": "npc_talk", "description": "Have a short conversation.", "display_name": "Talk", "parameters": []}, {"action_id": "bartender_rumors", "description": "Request a local rumor.", "display_name": "Ask for rumors", "parameters": []}], "npc_id": "NPC-952663a0", "role": "bartender"}, "stage": "npc_interactions", "subsystem": "interaction_layer", "turn": 0, "world_seed": 12345}
NPC: NPC-952663a0
1) Talk
2) Ask for rumors
0) Back
Select interaction index: 2
[v0.11.0][turn 0] action=engine:start change={"command_type": "npc_interact", "detail": {"command_type": "npc_interact"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=interaction_layer:npc_interaction change={"command_type": "npc_interact", "detail": {"interaction_id": "bartender_rumors", "npc_id": "NPC-952663a0", "result": {"ok": true, "rumor_text": "Long-haulers say every port keeps a story no map can hold.", "rumor_type": "lore"}}, "stage": "npc_interaction", "subsystem": "interaction_layer", "turn": 0, "world_seed": 12345}
Rumor type: lore
Rumor: Long-haulers say every port keeps a story no map can hold.
[v0.11.0][turn 0] action=engine:start change={"command_type": "list_npc_interactions", "detail": {"command_type": "list_npc_interactions"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=interaction_layer:npc_interactions change={"command_type": "list_npc_interactions", "detail": {"interactions": [{"action_id": "npc_talk", "description": "Have a short conversation.", "display_name": "Talk", "parameters": []}, {"action_id": "bartender_rumors", "description": "Request a local rumor.", "display_name": "Ask for rumors", "parameters": []}], "npc_id": "NPC-952663a0", "role": "bartender"}, "stage": "npc_interactions", "subsystem": "interaction_layer", "turn": 0, "world_seed": 12345}
NPC: NPC-952663a0
1) Talk
2) Ask for rumors
0) Back
Select interaction index: 1
[v0.11.0][turn 0] action=engine:start change={"command_type": "npc_interact", "detail": {"command_type": "npc_interact"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=interaction_layer:npc_interaction change={"command_type": "npc_interact", "detail": {"interaction_id": "npc_talk", "npc_id": "NPC-952663a0", "result": {"ok": true, "text": "Bartender polishes a glass and nods."}}, "stage": "npc_interaction", "subsystem": "interaction_layer", "turn": 0, "world_seed": 12345}
Bartender polishes a glass and nods.
[v0.11.0][turn 0] action=engine:start change={"command_type": "list_npc_interactions", "detail": {"command_type": "list_npc_interactions"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=interaction_layer:npc_interactions change={"command_type": "list_npc_interactions", "detail": {"interactions": [{"action_id": "npc_talk", "description": "Have a short conversation.", "display_name": "Talk", "parameters": []}, {"action_id": "bartender_rumors", "description": "Request a local rumor.", "display_name": "Ask for rumors", "parameters": []}], "npc_id": "NPC-952663a0", "role": "bartender"}, "stage": "npc_interactions", "subsystem": "interaction_layer", "turn": 0, "world_seed": 12345}
NPC: NPC-952663a0
1) Talk
2) Ask for rumors
0) Back
Select interaction index: 0
[v0.11.0][turn 0] action=engine:start change={"command_type": "list_location_npcs", "detail": {"command_type": "list_location_npcs"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=engine:location_npcs change={"command_type": "list_location_npcs", "detail": {"location_id": "SYS-001-DST-01-LOC-bar", "npcs": [{"display_name": "Bartender", "npc_id": "NPC-952663a0", "persistence_tier": 3, "role": "bartender"}]}, "stage": "location_npcs", "subsystem": "engine", "turn": 0, "world_seed": 12345}
LOCATION: SYS-001-DST-01-LOC-bar
1) Bartender (bartender)
0) Return to destination
Select NPC index: 0
[v0.11.0][turn 0] action=engine:start change={"command_type": "return_to_destination", "detail": {"command_type": "return_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=engine:location_navigation change={"command_type": "return_to_destination", "detail": {"action": "return_to_destination", "destination_id": "SYS-001-DST-01"}, "stage": "location_navigation", "subsystem": "engine", "turn": 0, "world_seed": 12345}
Returned to destination: SYS-001-DST-01
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
[v0.11.0][turn 0] action=engine:start change={"command_type": "enter_location", "detail": {"command_type": "enter_location"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=law_enforcement:law_checkpoint change={"command_type": "enter_location", "detail": {"skipped": true, "trigger_type": "CUSTOMS"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=engine:location_navigation change={"command_type": "enter_location", "detail": {"action": "enter_location", "location_id": "SYS-001-DST-01-LOC-market", "location_type": "market", "resolved_npc_ids": []}, "stage": "location_navigation", "subsystem": "engine", "turn": 0, "world_seed": 12345}
Entered location: SYS-001-DST-01-LOC-market
[v0.11.0][turn 0] action=engine:start change={"command_type": "get_market_profile", "detail": {"command_type": "get_market_profile"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=market:market_profile change={"command_type": "get_market_profile", "detail": {"active_situations": [], "categories": {"ENERGY": {"consumed": [], "neutral": [], "produced": ["high_density_fuel", "power_cells"]}, "MACHINERY": {"consumed": [], "neutral": [], "produced": ["automated_factories", "military_hardware"]}, "MEDICINE": {"consumed": [], "neutral": ["designer_drugs", "field_stimulants"], "produced": []}, "METAL": {"consumed": ["decorative_metals", "precision_alloys"], "neutral": [], "produced": []}, "ORE": {"consumed": ["copper_ore", "rare_earth_ore"], "neutral": [], "produced": []}, "PARTS": {"consumed": [], "neutral": [], "produced": ["electronic_components", "mechanical_parts"]}}, "destination_id": "SYS-001-DST-01", "primary_economy_id": "industrial", "secondary_economy_ids": [], "system_id": "SYS-001"}, "stage": "market_profile", "subsystem": "market", "turn": 0, "world_seed": 12345}
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
[v0.11.0][turn 0] action=engine:start change={"command_type": "market_buy_list", "detail": {"command_type": "market_buy_list"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=market:market_buy_list change={"command_type": "market_buy_list", "detail": {"destination_id": "SYS-001-DST-01", "rows": [{"available_units": null, "display_name": "Automated Factories", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "automated_factories", "unit_price": 284}, {"available_units": null, "display_name": "Copper Ore", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "copper_ore", "unit_price": 154}, {"available_units": null, "display_name": "Decorative Metals", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "decorative_metals", "unit_price": 338}, {"available_units": null, "display_name": "Designer Drugs", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "designer_drugs", "unit_price": 296}, {"available_units": null, "display_name": "Electronic Components", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "electronic_components", "unit_price": 142}, {"available_units": null, "display_name": "Field Stimulants", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "field_stimulants", "unit_price": 237}, {"available_units": null, "display_name": "High-Density Fuel", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "high_density_fuel", "unit_price": 158}, {"available_units": null, "display_name": "Mechanical Parts", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "mechanical_parts", "unit_price": 126}, {"available_units": null, "display_name": "Military Hardware", "legality": "LEGAL", "risk_tier": "High", "sku_id": "military_hardware", "unit_price": 497}, {"available_units": null, "display_name": "Power Cells", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "power_cells", "unit_price": 142}, {"available_units": null, "display_name": "Precision Alloys", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "precision_alloys", "unit_price": 284}, {"available_units": null, "display_name": "Rare Earth Ore", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "rare_earth_ore", "unit_price": 213}]}, "stage": "market_buy_list", "subsystem": "market", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=engine:start change={"command_type": "market_sell_list", "detail": {"command_type": "market_sell_list"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=market:market_sell_list change={"command_type": "market_sell_list", "detail": {"destination_id": "SYS-001-DST-01", "rows": []}, "stage": "market_sell_list", "subsystem": "market", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {}, "credits": 5000, "crew_wages_per_turn": 0, "destination_id": "SYS-001-DST-01", "fuel_capacity": 55, "fuel_current": 55, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-001-DST-01-LOC-market", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-001", "total_recurring_cost_per_turn": 0, "turn": 0, "warehouse_cost_per_turn": 0, "warehouses": [], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 0, "world_seed": 12345}
MARKET SKUS
  automated_factories | Automated Factories | buy=284 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  copper_ore | Copper Ore | buy=154 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  decorative_metals | Decorative Metals | buy=338 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  designer_drugs | Designer Drugs | buy=296 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  electronic_components | Electronic Components | buy=142 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  field_stimulants | Field Stimulants | buy=237 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  high_density_fuel | High-Density Fuel | buy=158 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  mechanical_parts | Mechanical Parts | buy=126 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  military_hardware | Military Hardware | buy=497 | sell=-- | cargo=0 | legality=LEGAL | risk=High
  power_cells | Power Cells | buy=142 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  precision_alloys | Precision Alloys | buy=284 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  rare_earth_ore | Rare Earth Ore | buy=213 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 1
[v0.11.0][turn 0] action=engine:start change={"command_type": "market_buy_list", "detail": {"command_type": "market_buy_list"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=market:market_buy_list change={"command_type": "market_buy_list", "detail": {"destination_id": "SYS-001-DST-01", "rows": [{"available_units": null, "display_name": "Automated Factories", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "automated_factories", "unit_price": 284}, {"available_units": null, "display_name": "Copper Ore", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "copper_ore", "unit_price": 154}, {"available_units": null, "display_name": "Decorative Metals", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "decorative_metals", "unit_price": 338}, {"available_units": null, "display_name": "Designer Drugs", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "designer_drugs", "unit_price": 296}, {"available_units": null, "display_name": "Electronic Components", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "electronic_components", "unit_price": 142}, {"available_units": null, "display_name": "Field Stimulants", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "field_stimulants", "unit_price": 237}, {"available_units": null, "display_name": "High-Density Fuel", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "high_density_fuel", "unit_price": 158}, {"available_units": null, "display_name": "Mechanical Parts", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "mechanical_parts", "unit_price": 126}, {"available_units": null, "display_name": "Military Hardware", "legality": "LEGAL", "risk_tier": "High", "sku_id": "military_hardware", "unit_price": 497}, {"available_units": null, "display_name": "Power Cells", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "power_cells", "unit_price": 142}, {"available_units": null, "display_name": "Precision Alloys", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "precision_alloys", "unit_price": 284}, {"available_units": null, "display_name": "Rare Earth Ore", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "rare_earth_ore", "unit_price": 213}]}, "stage": "market_buy_list", "subsystem": "market", "turn": 0, "world_seed": 12345}
1) automated_factories Automated Factories price=284 legality=LEGAL risk=Medium
2) copper_ore Copper Ore price=154 legality=LEGAL risk=Medium
3) decorative_metals Decorative Metals price=338 legality=LEGAL risk=Medium
4) designer_drugs Designer Drugs price=296 legality=LEGAL risk=Medium
5) electronic_components Electronic Components price=142 legality=LEGAL risk=Medium
6) field_stimulants Field Stimulants price=237 legality=LEGAL risk=Medium
7) high_density_fuel High-Density Fuel price=158 legality=LEGAL risk=Medium
8) mechanical_parts Mechanical Parts price=126 legality=LEGAL risk=Medium
9) military_hardware Military Hardware price=497 legality=LEGAL risk=High
10) power_cells Power Cells price=142 legality=LEGAL risk=Medium
11) precision_alloys Precision Alloys price=284 legality=LEGAL risk=Medium
12) rare_earth_ore Rare Earth Ore price=213 legality=LEGAL risk=Medium
Select buy sku index: 9
Quantity: 10
[v0.11.0][turn 0] action=engine:start change={"command_type": "market_buy", "detail": {"command_type": "market_buy"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=law_enforcement:customs_guard change={"command_type": "market_buy", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=market:market_trade change={"command_type": "market_buy", "detail": {"action": "buy", "cargo_after": 10, "credits_after": 30, "credits_before": 5000, "quantity": 10, "sku_id": "military_hardware", "total_cost": 4970, "unit_price": 497}, "stage": "market_trade", "subsystem": "market", "turn": 0, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "market_buy", "error": null, "events": [{"command_type": "market_buy", "detail": {"command_type": "market_buy"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 0, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"action": "buy", "cargo_after": 10, "credits_after": 30, "credits_before": 5000, "quantity": 10, "sku_id": "military_hardware", "total_cost": 4970, "unit_price": 497}, "stage": "market_trade", "subsystem": "market", "turn": 0, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 30, "destination_id": "SYS-001-DST-01", "location_id": "SYS-001-DST-01-LOC-market", "system_id": "SYS-001"}, "turn_after": 0, "turn_before": 0, "version": "0.11.0"}
[v0.11.0][turn 0] action=engine:start change={"command_type": "get_market_profile", "detail": {"command_type": "get_market_profile"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=market:market_profile change={"command_type": "get_market_profile", "detail": {"active_situations": [], "categories": {"ENERGY": {"consumed": [], "neutral": [], "produced": ["high_density_fuel", "power_cells"]}, "MACHINERY": {"consumed": [], "neutral": [], "produced": ["automated_factories", "military_hardware"]}, "MEDICINE": {"consumed": [], "neutral": ["designer_drugs", "field_stimulants"], "produced": []}, "METAL": {"consumed": ["decorative_metals", "precision_alloys"], "neutral": [], "produced": []}, "ORE": {"consumed": ["copper_ore", "rare_earth_ore"], "neutral": [], "produced": []}, "PARTS": {"consumed": [], "neutral": [], "produced": ["electronic_components", "mechanical_parts"]}}, "destination_id": "SYS-001-DST-01", "primary_economy_id": "industrial", "secondary_economy_ids": [], "system_id": "SYS-001"}, "stage": "market_profile", "subsystem": "market", "turn": 0, "world_seed": 12345}
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
[v0.11.0][turn 0] action=engine:start change={"command_type": "market_buy_list", "detail": {"command_type": "market_buy_list"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=market:market_buy_list change={"command_type": "market_buy_list", "detail": {"destination_id": "SYS-001-DST-01", "rows": [{"available_units": null, "display_name": "Automated Factories", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "automated_factories", "unit_price": 284}, {"available_units": null, "display_name": "Copper Ore", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "copper_ore", "unit_price": 154}, {"available_units": null, "display_name": "Decorative Metals", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "decorative_metals", "unit_price": 338}, {"available_units": null, "display_name": "Designer Drugs", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "designer_drugs", "unit_price": 296}, {"available_units": null, "display_name": "Electronic Components", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "electronic_components", "unit_price": 142}, {"available_units": null, "display_name": "Field Stimulants", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "field_stimulants", "unit_price": 237}, {"available_units": null, "display_name": "High-Density Fuel", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "high_density_fuel", "unit_price": 158}, {"available_units": null, "display_name": "Mechanical Parts", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "mechanical_parts", "unit_price": 126}, {"available_units": null, "display_name": "Military Hardware", "legality": "LEGAL", "risk_tier": "High", "sku_id": "military_hardware", "unit_price": 497}, {"available_units": null, "display_name": "Power Cells", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "power_cells", "unit_price": 142}, {"available_units": null, "display_name": "Precision Alloys", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "precision_alloys", "unit_price": 284}, {"available_units": null, "display_name": "Rare Earth Ore", "legality": "LEGAL", "risk_tier": "Medium", "sku_id": "rare_earth_ore", "unit_price": 213}]}, "stage": "market_buy_list", "subsystem": "market", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=engine:start change={"command_type": "market_sell_list", "detail": {"command_type": "market_sell_list"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=market:market_sell_list change={"command_type": "market_sell_list", "detail": {"destination_id": "SYS-001-DST-01", "rows": [{"available_units": null, "display_name": "Military Hardware", "legality": "LEGAL", "player_has_units": 10, "risk_tier": "High", "sku_id": "military_hardware", "unit_price": 497}]}, "stage": "market_sell_list", "subsystem": "market", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {"military_hardware": 10}, "credits": 30, "crew_wages_per_turn": 0, "destination_id": "SYS-001-DST-01", "fuel_capacity": 55, "fuel_current": 55, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-001-DST-01-LOC-market", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-001", "total_recurring_cost_per_turn": 0, "turn": 0, "warehouse_cost_per_turn": 0, "warehouses": [], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 0, "world_seed": 12345}
MARKET SKUS
  automated_factories | Automated Factories | buy=284 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  copper_ore | Copper Ore | buy=154 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  decorative_metals | Decorative Metals | buy=338 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  designer_drugs | Designer Drugs | buy=296 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  electronic_components | Electronic Components | buy=142 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  field_stimulants | Field Stimulants | buy=237 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  high_density_fuel | High-Density Fuel | buy=158 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  mechanical_parts | Mechanical Parts | buy=126 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  military_hardware | Military Hardware | buy=497 | sell=497 | cargo=10 | legality=LEGAL | risk=High
  power_cells | Power Cells | buy=142 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  precision_alloys | Precision Alloys | buy=284 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
  rare_earth_ore | Rare Earth Ore | buy=213 | sell=-- | cargo=0 | legality=LEGAL | risk=Medium
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 3
[v0.11.0][turn 0] action=engine:start change={"command_type": "return_to_destination", "detail": {"command_type": "return_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=engine:location_navigation change={"command_type": "return_to_destination", "detail": {"action": "return_to_destination", "destination_id": "SYS-001-DST-01"}, "stage": "location_navigation", "subsystem": "engine", "turn": 0, "world_seed": 12345}
Returned to destination: SYS-001-DST-01
DESTINATION: Ion 1 (SYS-001)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 1
[v0.11.0][turn 0] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {"military_hardware": 10}, "credits": 30, "crew_wages_per_turn": 0, "destination_id": "SYS-001-DST-01", "fuel_capacity": 55, "fuel_current": 55, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-001-DST-01", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-001", "total_recurring_cost_per_turn": 0, "turn": 0, "warehouse_cost_per_turn": 0, "warehouses": [], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=engine:start change={"command_type": "get_destination_profile", "detail": {"command_type": "get_destination_profile"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=engine:destination_profile change={"command_type": "get_destination_profile", "detail": {"active_crew": [], "active_destination_situations": [], "active_missions": [], "destination_id": "SYS-001-DST-01", "locations": [{"location_id": "SYS-001-DST-01-LOC-bar", "location_type": "bar"}, {"location_id": "SYS-001-DST-01-LOC-datanet", "location_type": "datanet"}, {"location_id": "SYS-001-DST-01-LOC-market", "location_type": "market"}, {"location_id": "SYS-001-DST-01-LOC-warehouse", "location_type": "warehouse"}], "market_attached": true, "name": "Ion 1", "population": 2, "primary_economy": "industrial"}, "stage": "destination_profile", "subsystem": "engine", "turn": 0, "world_seed": 12345}
PLAYER / SHIP INFO
  Credits: 30
  Fuel: 55/55
  Cargo manifest: {'military_hardware': 10}
  Reputation: 50 band=0
  Heat: 0
  Notoriety: 0 band=-2
  Arrest state: free
  Warrants: []
  Location: SYS-001 / SYS-001-DST-01 / SYS-001-DST-01
  Turn: 0
  Active crew: []
  Active missions: []
ONGOING COSTS
  Insurance: 0
  Warehouse rental: 0
  Crew wages: 0
  Total recurring cost: 0
WAREHOUSE RENTALS
  none
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
1) SYS-004 Flux distance_ly=51.844
2) SYS-005 Beacon distance_ly=50.078
Select target system index: 1
[v0.11.0][turn 0] action=engine:start change={"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"distance_ly": 51.84375710593287, "distance_ly_ceiled": 52, "inter_system": true, "target_destination_id": "SYS-004-DST-01", "target_system_id": "SYS-004", "travel_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 0, "world_seed": 12345}
[v0.11.0][turn 0] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"current_fuel": 3, "fuel_capacity": 55, "fuel_cost": 52, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 0, "world_seed": 12345}
[time_engine] action=time_advance_requested change=start_turn=0 days=10 reason=travel:TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route
[time_engine] action=galaxy_tick change=day=1
[time_engine] action=system_tick change=day=1
[time_engine] action=planet_station_tick change=day=1
[time_engine] action=location_tick change=day=1
[time_engine] action=npc_tick change=day=1
[time_engine] action=end_of_day_log change=day=1
Spawn gate cooldown check: system_id=SYS-004 current_day=1 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=1 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.8852235956883219
[time_engine] action=time_advance_day_completed change=turn=1 hard_stop=None
[time_engine] action=galaxy_tick change=day=2
[time_engine] action=system_tick change=day=2
[time_engine] action=planet_station_tick change=day=2
[time_engine] action=location_tick change=day=2
[time_engine] action=npc_tick change=day=2
[time_engine] action=end_of_day_log change=day=2
Spawn gate cooldown check: system_id=SYS-004 current_day=2 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=2 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.21472905845803036
[time_engine] action=time_advance_day_completed change=turn=2 hard_stop=None
[time_engine] action=galaxy_tick change=day=3
[time_engine] action=system_tick change=day=3
[time_engine] action=planet_station_tick change=day=3
[time_engine] action=location_tick change=day=3
[time_engine] action=npc_tick change=day=3
[time_engine] action=end_of_day_log change=day=3
Spawn gate cooldown check: system_id=SYS-004 current_day=3 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=3 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.8644109961367317
[time_engine] action=time_advance_day_completed change=turn=3 hard_stop=None
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
[time_engine] action=time_advance_requested change=start_turn=10 days=10 reason=travel:TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route
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
[time_engine] action=time_advance_requested change=start_turn=20 days=10 reason=travel:TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route
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
[time_engine] action=time_advance_requested change=start_turn=30 days=10 reason=travel:TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route
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
[time_engine] action=time_advance_requested change=start_turn=40 days=10 reason=travel:TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route
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
[time_engine] action=time_advance_requested change=start_turn=50 days=2 reason=travel:TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route
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
[v0.11.0][turn 52] action=time_engine:time_advance change={"command_type": "travel_to_destination", "detail": {"days_completed": 52, "days_requested": 52, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 52, "world_seed": 12345}
[v0.11.0][turn 52] action=law_enforcement:law_checkpoint change={"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 52, "world_seed": 12345}
[v0.11.0][turn 52] action=encounter_generator:encounter_gen change={"command_type": "travel_to_destination", "detail": {"encounter_count": 2, "travel_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 52, "world_seed": 12345}
[v0.11.0][turn 52] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route_enc_3", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 52, "world_seed": 12345}
[v0.11.0][turn 52] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route_enc_3", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": ["attack_plus_one_high_tr_delta"], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route_enc_3ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [2, 5, 2], "weights_after_notoriety": [2, 5, 2], "weights_after_reputation": [2, 5, 2], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 52, "world_seed": 12345}
[v0.11.0][turn 52] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route_enc_3", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 52, "world_seed": 12345}
[v0.11.0][turn 52] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route_enc_6", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 52, "world_seed": 12345}
[v0.11.0][turn 52] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route_enc_6", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route_enc_6ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [2, 5, 1], "weights_after_notoriety": [2, 5, 1], "weights_after_reputation": [2, 5, 1], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 52, "world_seed": 12345}
[v0.11.0][turn 52] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route_enc_6", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 52, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 0, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 51.84375710593287, "distance_ly_ceiled": 52, "inter_system": true, "target_destination_id": "SYS-004-DST-01", "target_system_id": "SYS-004", "travel_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 0, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 3, "fuel_capacity": 55, "fuel_cost": 52, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 0, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 52, "days_requested": 52, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 52, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 52, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 2, "travel_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 52, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route_enc_3", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 52, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route_enc_3", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": ["attack_plus_one_high_tr_delta"], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route_enc_3ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [2, 5, 2], "weights_after_notoriety": [2, 5, 2], "weights_after_reputation": [2, 5, 2], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 52, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route_enc_3", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 52, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route_enc_6", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 52, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route_enc_6", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route_enc_6ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [2, 5, 1], "weights_after_notoriety": [2, 5, 1], "weights_after_reputation": [2, 5, 1], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 52, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-004:SYS-004-DST-01:0:auto_route_enc_6", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 52, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 30, "destination_id": "SYS-004-DST-01", "location_id": "SYS-004-DST-01", "system_id": "SYS-004"}, "turn_after": 52, "turn_before": 0, "version": "0.11.0"}
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
[v0.11.0][turn 52] action=engine:start change={"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 52, "world_seed": 12345}
[v0.11.0][turn 52] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-004-DST-02", "target_system_id": "SYS-004", "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:52:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 52, "world_seed": 12345}
[v0.11.0][turn 52] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"current_fuel": 3, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:52:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 52, "world_seed": 12345}
[time_engine] action=time_advance_requested change=start_turn=52 days=1 reason=travel:TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:52:auto_route
[time_engine] action=galaxy_tick change=day=53
[time_engine] action=system_tick change=day=53
[time_engine] action=planet_station_tick change=day=53
[time_engine] action=location_tick change=day=53
[time_engine] action=npc_tick change=day=53
[time_engine] action=end_of_day_log change=day=53
Spawn gate cooldown check: system_id=SYS-004 current_day=53 cooldown_until=29 skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-004 current_day=53 cooldown_until=29 reason=spawn_gate_roll_failed spawn_gate_roll=0.3346780127178115
[time_engine] action=time_advance_day_completed change=turn=53 hard_stop=None
[v0.11.0][turn 53] action=time_engine:time_advance change={"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:52:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=law_enforcement:law_checkpoint change={"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=encounter_generator:encounter_gen change={"command_type": "travel_to_destination", "detail": {"encounter_count": 1, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:52:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:52:auto_route_enc_2", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:52:auto_route_enc_2", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:52:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 53, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 52, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-004-DST-02", "target_system_id": "SYS-004", "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:52:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 52, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 3, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:52:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 52, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:52:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 1, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:52:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:52:auto_route_enc_2", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:52:auto_route_enc_2", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-02:52:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 53, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 30, "destination_id": "SYS-004-DST-02", "location_id": "SYS-004-DST-02", "system_id": "SYS-004"}, "turn_after": 53, "turn_before": 52, "version": "0.11.0"}
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
Select location index: 5
[v0.11.0][turn 53] action=engine:start change={"command_type": "enter_location", "detail": {"command_type": "enter_location"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=npc_registry change=add npc_id=NPC-19fd77a4
[v0.11.0][turn 53] action=npc_placement change=created location_id=SYS-004-DST-02-LOC-administration npc_id=NPC-19fd77a4
[v0.11.0][turn 53] action=engine:location_navigation change={"command_type": "enter_location", "detail": {"action": "enter_location", "location_id": "SYS-004-DST-02-LOC-administration", "location_type": "administration", "resolved_npc_ids": ["NPC-19fd77a4"]}, "stage": "location_navigation", "subsystem": "engine", "turn": 53, "world_seed": 12345}
Entered location: SYS-004-DST-02-LOC-administration
[v0.11.0][turn 53] action=engine:start change={"command_type": "list_location_npcs", "detail": {"command_type": "list_location_npcs"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=engine:location_npcs change={"command_type": "list_location_npcs", "detail": {"location_id": "SYS-004-DST-02-LOC-administration", "npcs": [{"display_name": "Administrator", "npc_id": "NPC-19fd77a4", "persistence_tier": 3, "role": "administrator"}]}, "stage": "location_npcs", "subsystem": "engine", "turn": 53, "world_seed": 12345}
LOCATION: SYS-004-DST-02-LOC-administration
1) Administrator (administrator)
0) Return to destination
Select NPC index: 1
[v0.11.0][turn 53] action=engine:start change={"command_type": "list_npc_interactions", "detail": {"command_type": "list_npc_interactions"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=interaction_layer:npc_interactions change={"command_type": "list_npc_interactions", "detail": {"interactions": [{"action_id": "npc_talk", "description": "Have a short conversation.", "display_name": "Talk", "parameters": []}, {"action_id": "admin_pay_fines", "description": "Pay outstanding fines in this system.", "display_name": "Pay fines", "parameters": []}], "npc_id": "NPC-19fd77a4", "role": "administrator"}, "stage": "npc_interactions", "subsystem": "interaction_layer", "turn": 53, "world_seed": 12345}
NPC: NPC-19fd77a4
1) Talk
2) Pay fines
0) Back
Select interaction index: 1
[v0.11.0][turn 53] action=engine:start change={"command_type": "npc_interact", "detail": {"command_type": "npc_interact"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=interaction_layer:npc_interaction change={"command_type": "npc_interact", "detail": {"interaction_id": "npc_talk", "npc_id": "NPC-19fd77a4", "result": {"ok": true, "text": "Administrator reviews your record and waits."}}, "stage": "npc_interaction", "subsystem": "interaction_layer", "turn": 53, "world_seed": 12345}
Administrator reviews your record and waits.
[v0.11.0][turn 53] action=engine:start change={"command_type": "list_npc_interactions", "detail": {"command_type": "list_npc_interactions"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=interaction_layer:npc_interactions change={"command_type": "list_npc_interactions", "detail": {"interactions": [{"action_id": "npc_talk", "description": "Have a short conversation.", "display_name": "Talk", "parameters": []}, {"action_id": "admin_pay_fines", "description": "Pay outstanding fines in this system.", "display_name": "Pay fines", "parameters": []}], "npc_id": "NPC-19fd77a4", "role": "administrator"}, "stage": "npc_interactions", "subsystem": "interaction_layer", "turn": 53, "world_seed": 12345}
NPC: NPC-19fd77a4
1) Talk
2) Pay fines
0) Back
Select interaction index: 2
[v0.11.0][turn 53] action=engine:start change={"command_type": "npc_interact", "detail": {"command_type": "npc_interact"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=interaction_layer:npc_interaction change={"command_type": "npc_interact", "detail": {"interaction_id": "admin_pay_fines", "npc_id": "NPC-19fd77a4", "result": {"ok": true, "paid": 0, "reason": "no_fines_due"}}, "stage": "npc_interaction", "subsystem": "interaction_layer", "turn": 53, "world_seed": 12345}
{"ok": true, "paid": 0, "reason": "no_fines_due"}
[v0.11.0][turn 53] action=engine:start change={"command_type": "list_npc_interactions", "detail": {"command_type": "list_npc_interactions"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=interaction_layer:npc_interactions change={"command_type": "list_npc_interactions", "detail": {"interactions": [{"action_id": "npc_talk", "description": "Have a short conversation.", "display_name": "Talk", "parameters": []}, {"action_id": "admin_pay_fines", "description": "Pay outstanding fines in this system.", "display_name": "Pay fines", "parameters": []}], "npc_id": "NPC-19fd77a4", "role": "administrator"}, "stage": "npc_interactions", "subsystem": "interaction_layer", "turn": 53, "world_seed": 12345}
NPC: NPC-19fd77a4
1) Talk
2) Pay fines
0) Back
Select interaction index: 0
[v0.11.0][turn 53] action=engine:start change={"command_type": "list_location_npcs", "detail": {"command_type": "list_location_npcs"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=engine:location_npcs change={"command_type": "list_location_npcs", "detail": {"location_id": "SYS-004-DST-02-LOC-administration", "npcs": [{"display_name": "Administrator", "npc_id": "NPC-19fd77a4", "persistence_tier": 3, "role": "administrator"}]}, "stage": "location_npcs", "subsystem": "engine", "turn": 53, "world_seed": 12345}
LOCATION: SYS-004-DST-02-LOC-administration
1) Administrator (administrator)
0) Return to destination
Select NPC index: 0
[v0.11.0][turn 53] action=engine:start change={"command_type": "return_to_destination", "detail": {"command_type": "return_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=engine:location_navigation change={"command_type": "return_to_destination", "detail": {"action": "return_to_destination", "destination_id": "SYS-004-DST-02"}, "stage": "location_navigation", "subsystem": "engine", "turn": 53, "world_seed": 12345}
Returned to destination: SYS-004-DST-02
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
[v0.11.0][turn 53] action=engine:start change={"command_type": "enter_location", "detail": {"command_type": "enter_location"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=law_enforcement:law_checkpoint change={"command_type": "enter_location", "detail": {"skipped": true, "trigger_type": "CUSTOMS"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=engine:location_navigation change={"command_type": "enter_location", "detail": {"action": "enter_location", "location_id": "SYS-004-DST-02-LOC-market", "location_type": "market", "resolved_npc_ids": []}, "stage": "location_navigation", "subsystem": "engine", "turn": 53, "world_seed": 12345}
Entered location: SYS-004-DST-02-LOC-market
[v0.11.0][turn 53] action=engine:start change={"command_type": "get_market_profile", "detail": {"command_type": "get_market_profile"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=market:market_profile change={"command_type": "get_market_profile", "detail": {"active_situations": [], "categories": {"ENERGY": {"consumed": ["experimental_reactors", "high_density_fuel", "power_cells", "standard_fuel"], "neutral": [], "produced": []}, "FOOD": {"consumed": ["fresh_produce", "nutrient_paste", "protein_blocks", "spice_wine"], "neutral": ["basic_rations", "heritage_cuisine"], "produced": []}, "MACHINERY": {"consumed": [], "neutral": [], "produced": ["automated_factories", "industrial_machinery", "military_hardware", "mining_equipment"]}, "MEDICINE": {"consumed": ["cybernetic_medical_nanites", "designer_drugs", "gene_therapy_kits", "medical_nanites"], "neutral": [], "produced": []}, "METAL": {"consumed": ["precision_alloys"], "neutral": [], "produced": ["aluminum_alloy", "decorative_metals", "steel_ingots", "titanium_bars"]}, "ORE": {"consumed": [], "neutral": [], "produced": ["copper_ore", "nickel_ore", "radioactive_ore", "rare_earth_ore"]}, "PARTS": {"consumed": ["autonomous_robots", "servitor_units", "synthetic_intelligences", "weaponized_autonomous_robots"], "neutral": ["cybernetic_implants", "electronic_components", "mechanical_parts", "weaponized_synthetic_intelligences"], "produced": []}, "WEAPONS": {"consumed": [], "neutral": [], "produced": ["biological_weapons", "experimental_weapons", "heavy_weapons", "small_arms"]}}, "destination_id": "SYS-004-DST-02", "primary_economy_id": "military", "secondary_economy_ids": ["mining"], "system_id": "SYS-004"}, "stage": "market_profile", "subsystem": "market", "turn": 53, "world_seed": 12345}
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
[v0.11.0][turn 53] action=engine:start change={"command_type": "market_buy_list", "detail": {"command_type": "market_buy_list"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=market:market_buy_list change={"command_type": "market_buy_list", "detail": {"destination_id": "SYS-004-DST-02", "rows": [{"available_units": null, "display_name": "Aluminum Alloy", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "aluminum_alloy", "unit_price": 142}, {"available_units": null, "display_name": "Automated Factories", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "automated_factories", "unit_price": 300}, {"available_units": null, "display_name": "Autonomous Robots", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "autonomous_robots", "unit_price": 312}, {"available_units": null, "display_name": "Basic Rations", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "basic_rations", "unit_price": 104}, {"available_units": null, "display_name": "Biological Weapons", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "biological_weapons", "unit_price": 750}, {"available_units": null, "display_name": "Copper Ore", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "copper_ore", "unit_price": 108}, {"available_units": null, "display_name": "Cybernetic Implants", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "cybernetic_implants", "unit_price": 271}, {"available_units": null, "display_name": "Cybernetic Medical Nanites", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "cybernetic_medical_nanites", "unit_price": 450}, {"available_units": null, "display_name": "Decorative Metals", "legality": "RESTRICTED", "risk_tier": "Severe", "sku_id": "decorative_metals", "unit_price": 238}, {"available_units": null, "display_name": "Designer Drugs", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "designer_drugs", "unit_price": 375}, {"available_units": null, "display_name": "Electronic Components", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "electronic_components", "unit_price": 187}, {"available_units": null, "display_name": "Experimental Reactors", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "experimental_reactors", "unit_price": 525}, {"available_units": null, "display_name": "Experimental Weapons", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "experimental_weapons", "unit_price": 650}, {"available_units": null, "display_name": "Fresh Produce", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "fresh_produce", "unit_price": 125}, {"available_units": null, "display_name": "Gene Therapy Kits", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "gene_therapy_kits", "unit_price": 400}, {"available_units": null, "display_name": "Heavy Weapons", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "heavy_weapons", "unit_price": 400}, {"available_units": null, "display_name": "Heritage Cuisine", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "heritage_cuisine", "unit_price": 187}, {"available_units": null, "display_name": "High-Density Fuel", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "high_density_fuel", "unit_price": 250}, {"available_units": null, "display_name": "Industrial Machinery", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "industrial_machinery", "unit_price": 217}, {"available_units": null, "display_name": "Mechanical Parts", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "mechanical_parts", "unit_price": 167}, {"available_units": null, "display_name": "Medical Nanites", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "medical_nanites", "unit_price": 450}, {"available_units": null, "display_name": "Military Hardware", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "military_hardware", "unit_price": 525}, {"available_units": null, "display_name": "Mining Equipment", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "mining_equipment", "unit_price": 233}, {"available_units": null, "display_name": "Nickel Ore", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "nickel_ore", "unit_price": 117}, {"available_units": null, "display_name": "Nutrient Paste", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "nutrient_paste", "unit_price": 115}, {"available_units": null, "display_name": "Power Cells", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "power_cells", "unit_price": 225}, {"available_units": null, "display_name": "Precision Alloys", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "precision_alloys", "unit_price": 200}, {"available_units": null, "display_name": "Protein Blocks", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "protein_blocks", "unit_price": 146}, {"available_units": null, "display_name": "Radioactive Ore", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "radioactive_ore", "unit_price": 183}, {"available_units": null, "display_name": "Rare Earth Ore", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "rare_earth_ore", "unit_price": 150}, {"available_units": null, "display_name": "Servitor Units", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "servitor_units", "unit_price": 229}, {"available_units": null, "display_name": "Small Arms", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "small_arms", "unit_price": 275}, {"available_units": null, "display_name": "Spice Wine", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "spice_wine", "unit_price": 167}, {"available_units": null, "display_name": "Standard Fuel", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "standard_fuel", "unit_price": 187}, {"available_units": null, "display_name": "Steel Ingots", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "steel_ingots", "unit_price": 133}, {"available_units": null, "display_name": "Synthetic Intelligences", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "synthetic_intelligences", "unit_price": 437}, {"available_units": null, "display_name": "Titanium Bars", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "titanium_bars", "unit_price": 175}, {"available_units": null, "display_name": "Weaponized Autonomous Robots", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "weaponized_autonomous_robots", "unit_price": 469}, {"available_units": null, "display_name": "Weaponized Synthetic Intelligences", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "weaponized_synthetic_intelligences", "unit_price": 656}]}, "stage": "market_buy_list", "subsystem": "market", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=engine:start change={"command_type": "market_sell_list", "detail": {"command_type": "market_sell_list"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=market:market_sell_list change={"command_type": "market_sell_list", "detail": {"destination_id": "SYS-004-DST-02", "rows": [{"available_units": null, "display_name": "Military Hardware", "legality": "LEGAL", "player_has_units": 10, "risk_tier": "Severe", "sku_id": "military_hardware", "unit_price": 525}]}, "stage": "market_sell_list", "subsystem": "market", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {"military_hardware": 10}, "credits": 30, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-02", "fuel_capacity": 55, "fuel_current": 3, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-02-LOC-market", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 0, "turn": 53, "warehouse_cost_per_turn": 0, "warehouses": [], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 53, "world_seed": 12345}
MARKET SKUS
  aluminum_alloy | Aluminum Alloy | buy=142 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  automated_factories | Automated Factories | buy=300 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  autonomous_robots | Autonomous Robots | buy=312 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_rations | Basic Rations | buy=104 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  biological_weapons | Biological Weapons | buy=750 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  copper_ore | Copper Ore | buy=108 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_implants | Cybernetic Implants | buy=271 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_medical_nanites | Cybernetic Medical Nanites | buy=450 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  decorative_metals | Decorative Metals | buy=238 | sell=-- | cargo=0 | legality=RESTRICTED | risk=Severe
  designer_drugs | Designer Drugs | buy=375 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  electronic_components | Electronic Components | buy=187 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_reactors | Experimental Reactors | buy=525 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_weapons | Experimental Weapons | buy=650 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fresh_produce | Fresh Produce | buy=125 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=400 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heavy_weapons | Heavy Weapons | buy=400 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heritage_cuisine | Heritage Cuisine | buy=187 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  high_density_fuel | High-Density Fuel | buy=250 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  industrial_machinery | Industrial Machinery | buy=217 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  mechanical_parts | Mechanical Parts | buy=167 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=450 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  military_hardware | Military Hardware | buy=525 | sell=525 | cargo=10 | legality=LEGAL | risk=Severe
  mining_equipment | Mining Equipment | buy=233 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nickel_ore | Nickel Ore | buy=117 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nutrient_paste | Nutrient Paste | buy=115 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  power_cells | Power Cells | buy=225 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  precision_alloys | Precision Alloys | buy=200 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  protein_blocks | Protein Blocks | buy=146 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  radioactive_ore | Radioactive Ore | buy=183 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  rare_earth_ore | Rare Earth Ore | buy=150 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  servitor_units | Servitor Units | buy=229 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  small_arms | Small Arms | buy=275 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  spice_wine | Spice Wine | buy=167 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=187 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  steel_ingots | Steel Ingots | buy=133 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  synthetic_intelligences | Synthetic Intelligences | buy=437 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  titanium_bars | Titanium Bars | buy=175 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=469 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_synthetic_intelligences | Weaponized Synthetic Intelligences | buy=656 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 2
[v0.11.0][turn 53] action=engine:start change={"command_type": "market_sell_list", "detail": {"command_type": "market_sell_list"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=market:market_sell_list change={"command_type": "market_sell_list", "detail": {"destination_id": "SYS-004-DST-02", "rows": [{"available_units": null, "display_name": "Military Hardware", "legality": "LEGAL", "player_has_units": 10, "risk_tier": "Severe", "sku_id": "military_hardware", "unit_price": 525}]}, "stage": "market_sell_list", "subsystem": "market", "turn": 53, "world_seed": 12345}
1) military_hardware Military Hardware units=10 price=525 legality=LEGAL risk=Severe
Select sell sku index: 0
Quantity: 0
Invalid sell index.
[v0.11.0][turn 53] action=engine:start change={"command_type": "get_market_profile", "detail": {"command_type": "get_market_profile"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=market:market_profile change={"command_type": "get_market_profile", "detail": {"active_situations": [], "categories": {"ENERGY": {"consumed": ["experimental_reactors", "high_density_fuel", "power_cells", "standard_fuel"], "neutral": [], "produced": []}, "FOOD": {"consumed": ["fresh_produce", "nutrient_paste", "protein_blocks", "spice_wine"], "neutral": ["basic_rations", "heritage_cuisine"], "produced": []}, "MACHINERY": {"consumed": [], "neutral": [], "produced": ["automated_factories", "industrial_machinery", "military_hardware", "mining_equipment"]}, "MEDICINE": {"consumed": ["cybernetic_medical_nanites", "designer_drugs", "gene_therapy_kits", "medical_nanites"], "neutral": [], "produced": []}, "METAL": {"consumed": ["precision_alloys"], "neutral": [], "produced": ["aluminum_alloy", "decorative_metals", "steel_ingots", "titanium_bars"]}, "ORE": {"consumed": [], "neutral": [], "produced": ["copper_ore", "nickel_ore", "radioactive_ore", "rare_earth_ore"]}, "PARTS": {"consumed": ["autonomous_robots", "servitor_units", "synthetic_intelligences", "weaponized_autonomous_robots"], "neutral": ["cybernetic_implants", "electronic_components", "mechanical_parts", "weaponized_synthetic_intelligences"], "produced": []}, "WEAPONS": {"consumed": [], "neutral": [], "produced": ["biological_weapons", "experimental_weapons", "heavy_weapons", "small_arms"]}}, "destination_id": "SYS-004-DST-02", "primary_economy_id": "military", "secondary_economy_ids": ["mining"], "system_id": "SYS-004"}, "stage": "market_profile", "subsystem": "market", "turn": 53, "world_seed": 12345}
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
[v0.11.0][turn 53] action=engine:start change={"command_type": "market_buy_list", "detail": {"command_type": "market_buy_list"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=market:market_buy_list change={"command_type": "market_buy_list", "detail": {"destination_id": "SYS-004-DST-02", "rows": [{"available_units": null, "display_name": "Aluminum Alloy", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "aluminum_alloy", "unit_price": 142}, {"available_units": null, "display_name": "Automated Factories", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "automated_factories", "unit_price": 300}, {"available_units": null, "display_name": "Autonomous Robots", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "autonomous_robots", "unit_price": 312}, {"available_units": null, "display_name": "Basic Rations", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "basic_rations", "unit_price": 104}, {"available_units": null, "display_name": "Biological Weapons", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "biological_weapons", "unit_price": 750}, {"available_units": null, "display_name": "Copper Ore", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "copper_ore", "unit_price": 108}, {"available_units": null, "display_name": "Cybernetic Implants", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "cybernetic_implants", "unit_price": 271}, {"available_units": null, "display_name": "Cybernetic Medical Nanites", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "cybernetic_medical_nanites", "unit_price": 450}, {"available_units": null, "display_name": "Decorative Metals", "legality": "RESTRICTED", "risk_tier": "Severe", "sku_id": "decorative_metals", "unit_price": 238}, {"available_units": null, "display_name": "Designer Drugs", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "designer_drugs", "unit_price": 375}, {"available_units": null, "display_name": "Electronic Components", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "electronic_components", "unit_price": 187}, {"available_units": null, "display_name": "Experimental Reactors", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "experimental_reactors", "unit_price": 525}, {"available_units": null, "display_name": "Experimental Weapons", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "experimental_weapons", "unit_price": 650}, {"available_units": null, "display_name": "Fresh Produce", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "fresh_produce", "unit_price": 125}, {"available_units": null, "display_name": "Gene Therapy Kits", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "gene_therapy_kits", "unit_price": 400}, {"available_units": null, "display_name": "Heavy Weapons", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "heavy_weapons", "unit_price": 400}, {"available_units": null, "display_name": "Heritage Cuisine", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "heritage_cuisine", "unit_price": 187}, {"available_units": null, "display_name": "High-Density Fuel", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "high_density_fuel", "unit_price": 250}, {"available_units": null, "display_name": "Industrial Machinery", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "industrial_machinery", "unit_price": 217}, {"available_units": null, "display_name": "Mechanical Parts", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "mechanical_parts", "unit_price": 167}, {"available_units": null, "display_name": "Medical Nanites", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "medical_nanites", "unit_price": 450}, {"available_units": null, "display_name": "Military Hardware", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "military_hardware", "unit_price": 525}, {"available_units": null, "display_name": "Mining Equipment", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "mining_equipment", "unit_price": 233}, {"available_units": null, "display_name": "Nickel Ore", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "nickel_ore", "unit_price": 117}, {"available_units": null, "display_name": "Nutrient Paste", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "nutrient_paste", "unit_price": 115}, {"available_units": null, "display_name": "Power Cells", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "power_cells", "unit_price": 225}, {"available_units": null, "display_name": "Precision Alloys", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "precision_alloys", "unit_price": 200}, {"available_units": null, "display_name": "Protein Blocks", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "protein_blocks", "unit_price": 146}, {"available_units": null, "display_name": "Radioactive Ore", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "radioactive_ore", "unit_price": 183}, {"available_units": null, "display_name": "Rare Earth Ore", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "rare_earth_ore", "unit_price": 150}, {"available_units": null, "display_name": "Servitor Units", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "servitor_units", "unit_price": 229}, {"available_units": null, "display_name": "Small Arms", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "small_arms", "unit_price": 275}, {"available_units": null, "display_name": "Spice Wine", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "spice_wine", "unit_price": 167}, {"available_units": null, "display_name": "Standard Fuel", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "standard_fuel", "unit_price": 187}, {"available_units": null, "display_name": "Steel Ingots", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "steel_ingots", "unit_price": 133}, {"available_units": null, "display_name": "Synthetic Intelligences", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "synthetic_intelligences", "unit_price": 437}, {"available_units": null, "display_name": "Titanium Bars", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "titanium_bars", "unit_price": 175}, {"available_units": null, "display_name": "Weaponized Autonomous Robots", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "weaponized_autonomous_robots", "unit_price": 469}, {"available_units": null, "display_name": "Weaponized Synthetic Intelligences", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "weaponized_synthetic_intelligences", "unit_price": 656}]}, "stage": "market_buy_list", "subsystem": "market", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=engine:start change={"command_type": "market_sell_list", "detail": {"command_type": "market_sell_list"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=market:market_sell_list change={"command_type": "market_sell_list", "detail": {"destination_id": "SYS-004-DST-02", "rows": [{"available_units": null, "display_name": "Military Hardware", "legality": "LEGAL", "player_has_units": 10, "risk_tier": "Severe", "sku_id": "military_hardware", "unit_price": 525}]}, "stage": "market_sell_list", "subsystem": "market", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {"military_hardware": 10}, "credits": 30, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-02", "fuel_capacity": 55, "fuel_current": 3, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-02-LOC-market", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 0, "turn": 53, "warehouse_cost_per_turn": 0, "warehouses": [], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 53, "world_seed": 12345}
MARKET SKUS
  aluminum_alloy | Aluminum Alloy | buy=142 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  automated_factories | Automated Factories | buy=300 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  autonomous_robots | Autonomous Robots | buy=312 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  basic_rations | Basic Rations | buy=104 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  biological_weapons | Biological Weapons | buy=750 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  copper_ore | Copper Ore | buy=108 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_implants | Cybernetic Implants | buy=271 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_medical_nanites | Cybernetic Medical Nanites | buy=450 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  decorative_metals | Decorative Metals | buy=238 | sell=-- | cargo=0 | legality=RESTRICTED | risk=Severe
  designer_drugs | Designer Drugs | buy=375 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  electronic_components | Electronic Components | buy=187 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_reactors | Experimental Reactors | buy=525 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_weapons | Experimental Weapons | buy=650 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fresh_produce | Fresh Produce | buy=125 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=400 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heavy_weapons | Heavy Weapons | buy=400 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  heritage_cuisine | Heritage Cuisine | buy=187 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  high_density_fuel | High-Density Fuel | buy=250 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  industrial_machinery | Industrial Machinery | buy=217 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  mechanical_parts | Mechanical Parts | buy=167 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=450 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  military_hardware | Military Hardware | buy=525 | sell=525 | cargo=10 | legality=LEGAL | risk=Severe
  mining_equipment | Mining Equipment | buy=233 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nickel_ore | Nickel Ore | buy=117 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  nutrient_paste | Nutrient Paste | buy=115 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  power_cells | Power Cells | buy=225 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  precision_alloys | Precision Alloys | buy=200 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  protein_blocks | Protein Blocks | buy=146 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  radioactive_ore | Radioactive Ore | buy=183 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  rare_earth_ore | Rare Earth Ore | buy=150 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  servitor_units | Servitor Units | buy=229 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  small_arms | Small Arms | buy=275 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  spice_wine | Spice Wine | buy=167 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=187 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  steel_ingots | Steel Ingots | buy=133 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  synthetic_intelligences | Synthetic Intelligences | buy=437 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  titanium_bars | Titanium Bars | buy=175 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=469 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_synthetic_intelligences | Weaponized Synthetic Intelligences | buy=656 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 3
[v0.11.0][turn 53] action=engine:start change={"command_type": "return_to_destination", "detail": {"command_type": "return_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=engine:location_navigation change={"command_type": "return_to_destination", "detail": {"action": "return_to_destination", "destination_id": "SYS-004-DST-02"}, "stage": "location_navigation", "subsystem": "engine", "turn": 53, "world_seed": 12345}
Returned to destination: SYS-004-DST-02
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
[v0.11.0][turn 53] action=engine:start change={"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-004-DST-01", "target_system_id": "SYS-004", "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 53, "world_seed": 12345}
[v0.11.0][turn 53] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"current_fuel": 3, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 53, "world_seed": 12345}
[time_engine] action=time_advance_requested change=start_turn=53 days=1 reason=travel:TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route
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
[v0.11.0][turn 54] action=time_engine:time_advance change={"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=law_enforcement:law_checkpoint change={"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=encounter_generator:encounter_gen change={"command_type": "travel_to_destination", "detail": {"encounter_count": 6, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_0", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_0", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": ["attack_plus_one_high_tr_delta"], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_0ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [2, 5, 2], "weights_after_notoriety": [2, 5, 2], "weights_after_reputation": [2, 5, 2], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_1", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_1", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_1ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_2", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_2", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": ["attack_plus_one_high_tr_delta"], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_2ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [2, 5, 2], "weights_after_notoriety": [2, 5, 2], "weights_after_reputation": [2, 5, 2], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_3", "handler_payload": {"npc_outcome": "pursue"}, "next_handler": "pursuit_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_3", "resolver_outcome": {"escaped": true, "outcome": "escape_success", "resolver": "pursuit", "threshold": 0.55}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_3", "qualifies": true}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=reward_applicator:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"applied": {"cargo": null, "context": "game_engine", "credits": 1496, "quantity": 0}, "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_3", "reward_profile_id": "bounty_credit"}, "stage": "conditional_rewards", "subsystem": "reward_applicator", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_4", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_4", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_4", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_5", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_5", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_5", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-004-DST-01", "target_system_id": "SYS-004", "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 3, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 53, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 6, "travel_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_0", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_0", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": ["attack_plus_one_high_tr_delta"], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_0ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [2, 5, 2], "weights_after_notoriety": [2, 5, 2], "weights_after_reputation": [2, 5, 2], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_1", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_1", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_1ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_2", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_2", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": ["attack_plus_one_high_tr_delta"], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_2ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [2, 5, 2], "weights_after_notoriety": [2, 5, 2], "weights_after_reputation": [2, 5, 2], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_3", "handler_payload": {"npc_outcome": "pursue"}, "next_handler": "pursuit_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_3", "resolver_outcome": {"escaped": true, "outcome": "escape_success", "resolver": "pursuit", "threshold": 0.55}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_3", "qualifies": true}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"applied": {"cargo": null, "context": "game_engine", "credits": 1496, "quantity": 0}, "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_3", "reward_profile_id": "bounty_credit"}, "stage": "conditional_rewards", "subsystem": "reward_applicator", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_4", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_4", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_4", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_5", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_5", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-004:SYS-004-DST-01:53:auto_route_enc_5", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 54, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 1526, "destination_id": "SYS-004-DST-01", "location_id": "SYS-004-DST-01", "system_id": "SYS-004"}, "turn_after": 54, "turn_before": 53, "version": "0.11.0"}
DESTINATION: Flux 1 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 4
[v0.11.0][turn 54] action=engine:start change={"command_type": "list_destination_actions", "detail": {"command_type": "list_destination_actions"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=interaction_layer:destination_actions change={"command_type": "list_destination_actions", "detail": {"actions": [{"action_id": "customs_inspection", "description": "Run a voluntary customs inspection at destination level.", "display_name": "Customs Inspection", "fuel_cost": 0, "parameters": [], "requires_confirm": false, "time_cost_days": 0}, {"action_id": "refuel", "description": "Purchase fuel units up to ship fuel capacity.", "display_name": "Refuel", "fuel_cost": 0, "parameters": ["requested_units"], "requires_confirm": false, "time_cost_days": 0}], "destination_id": "SYS-004-DST-01"}, "stage": "destination_actions", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
1) customs_inspection Customs Inspection
2) refuel Refuel
3) Back
Select destination action index: 2
requested_units: 3
[v0.11.0][turn 54] action=engine:start change={"command_type": "destination_action", "detail": {"command_type": "destination_action"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=interaction_layer:destination_action change={"command_type": "destination_action", "detail": {"action_id": "refuel", "result": {"credits": 1511, "current_fuel": 6, "ok": true, "reason": "ok", "total_cost": 15, "units_purchased": 3}, "result_summary": {"credits_after": 1511, "credits_before": 1526, "fuel_after": 6, "fuel_before": 3, "reason": "ok", "result_ok": true, "total_cost": 15, "unit_price": 5, "units_purchased": 3}}, "stage": "destination_action", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "destination_action", "error": null, "events": [{"command_type": "destination_action", "detail": {"command_type": "destination_action"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}, {"command_type": "destination_action", "detail": {"action_id": "refuel", "result": {"credits": 1511, "current_fuel": 6, "ok": true, "reason": "ok", "total_cost": 15, "units_purchased": 3}, "result_summary": {"credits_after": 1511, "credits_before": 1526, "fuel_after": 6, "fuel_before": 3, "reason": "ok", "result_ok": true, "total_cost": 15, "unit_price": 5, "units_purchased": 3}}, "stage": "destination_action", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 1511, "destination_id": "SYS-004-DST-01", "location_id": "SYS-004-DST-01", "system_id": "SYS-004"}, "turn_after": 54, "turn_before": 54, "version": "0.11.0"}
[v0.11.0][turn 54] action=engine:start change={"command_type": "list_destination_actions", "detail": {"command_type": "list_destination_actions"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=interaction_layer:destination_actions change={"command_type": "list_destination_actions", "detail": {"actions": [{"action_id": "customs_inspection", "description": "Run a voluntary customs inspection at destination level.", "display_name": "Customs Inspection", "fuel_cost": 0, "parameters": [], "requires_confirm": false, "time_cost_days": 0}, {"action_id": "refuel", "description": "Purchase fuel units up to ship fuel capacity.", "display_name": "Refuel", "fuel_cost": 0, "parameters": ["requested_units"], "requires_confirm": false, "time_cost_days": 0}], "destination_id": "SYS-004-DST-01"}, "stage": "destination_actions", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
1) customs_inspection Customs Inspection
2) refuel Refuel
3) Back
Select destination action index: 3
DESTINATION: Flux 1 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 1
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {"military_hardware": 10}, "credits": 1511, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-01", "fuel_capacity": 55, "fuel_current": 6, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-01", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 0, "turn": 54, "warehouse_cost_per_turn": 0, "warehouses": [], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_destination_profile", "detail": {"command_type": "get_destination_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:destination_profile change={"command_type": "get_destination_profile", "detail": {"active_crew": [], "active_destination_situations": [], "active_missions": [], "destination_id": "SYS-004-DST-01", "locations": [{"location_id": "SYS-004-DST-01-LOC-datanet", "location_type": "datanet"}, {"location_id": "SYS-004-DST-01-LOC-market", "location_type": "market"}, {"location_id": "SYS-004-DST-01-LOC-warehouse", "location_type": "warehouse"}], "market_attached": true, "name": "Flux 1", "population": 2, "primary_economy": "research"}, "stage": "destination_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
PLAYER / SHIP INFO
  Credits: 1511
  Fuel: 6/55
  Cargo manifest: {'military_hardware': 10}
  Reputation: 50 band=0
  Heat: 0
  Notoriety: 0 band=-2
  Arrest state: free
  Warrants: []
  Location: SYS-004 / SYS-004-DST-01 / SYS-004-DST-01
  Turn: 54
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
Select location index: 3
[v0.11.0][turn 54] action=engine:start change={"command_type": "enter_location", "detail": {"command_type": "enter_location"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:location_navigation change={"command_type": "enter_location", "detail": {"action": "enter_location", "location_id": "SYS-004-DST-01-LOC-warehouse", "location_type": "warehouse", "resolved_npc_ids": []}, "stage": "location_navigation", "subsystem": "engine", "turn": 54, "world_seed": 12345}
Entered location: SYS-004-DST-01-LOC-warehouse
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {"military_hardware": 10}, "credits": 1511, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-01", "fuel_capacity": 55, "fuel_current": 6, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-01-LOC-warehouse", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 0, "turn": 54, "warehouse_cost_per_turn": 0, "warehouses": [], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
WAREHOUSE PROFILE
  Rented capacity: 0
  Used storage: 0
  Available storage: 0
  Rental cost per turn: 0
  Stored goods list:
    none
LOCATION: warehouse
1) Rent space
2) Deposit cargo
3) Withdraw cargo
4) Return to Destination
Select action index: 1
Units to rent: 10
[v0.11.0][turn 54] action=engine:start change={"command_type": "location_action", "detail": {"command_type": "location_action"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=interaction_layer:location_action change={"command_type": "location_action", "detail": {"action_id": "warehouse_rent", "result": {"ok": true, "reason": "ok"}, "result_summary": {"capacity_after": 10, "capacity_before": 0, "cost_per_turn_per_capacity": 2, "destination_id": "SYS-004-DST-01", "result_ok": true, "units_rented": 10}}, "stage": "location_action", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "location_action", "error": null, "events": [{"command_type": "location_action", "detail": {"command_type": "location_action"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}, {"command_type": "location_action", "detail": {"action_id": "warehouse_rent", "result": {"ok": true, "reason": "ok"}, "result_summary": {"capacity_after": 10, "capacity_before": 0, "cost_per_turn_per_capacity": 2, "destination_id": "SYS-004-DST-01", "result_ok": true, "units_rented": 10}}, "stage": "location_action", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 1511, "destination_id": "SYS-004-DST-01", "location_id": "SYS-004-DST-01-LOC-warehouse", "system_id": "SYS-004"}, "turn_after": 54, "turn_before": 54, "version": "0.11.0"}
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {"military_hardware": 10}, "credits": 1511, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-01", "fuel_capacity": 55, "fuel_current": 6, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-01-LOC-warehouse", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 20, "turn": 54, "warehouse_cost_per_turn": 20, "warehouses": [{"available": 10, "capacity": 10, "cost_per_turn": 20, "destination_id": "SYS-004-DST-01", "goods": {}, "used": 0}], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
WAREHOUSE PROFILE
  Rented capacity: 10
  Used storage: 0
  Available storage: 10
  Rental cost per turn: 20
  Stored goods list:
    none
LOCATION: warehouse
1) Rent space
2) Deposit cargo
3) Withdraw cargo
4) Return to Destination
Select action index: 2
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {"military_hardware": 10}, "credits": 1511, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-01", "fuel_capacity": 55, "fuel_current": 6, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-01-LOC-warehouse", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 20, "turn": 54, "warehouse_cost_per_turn": 20, "warehouses": [{"available": 10, "capacity": 10, "cost_per_turn": 20, "destination_id": "SYS-004-DST-01", "goods": {}, "used": 0}], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
1) military_hardware units=10
Select cargo SKU index: 1
Quantity: 10
[v0.11.0][turn 54] action=engine:start change={"command_type": "location_action", "detail": {"command_type": "location_action"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=interaction_layer:location_action change={"command_type": "location_action", "detail": {"action_id": "warehouse_deposit", "result": {"ok": true, "reason": "ok"}, "result_summary": {"destination_id": "SYS-004-DST-01", "quantity": 10, "sku_id": "military_hardware", "warehouse_available_after": 0, "warehouse_used_after": 10}}, "stage": "location_action", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "location_action", "error": null, "events": [{"command_type": "location_action", "detail": {"command_type": "location_action"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}, {"command_type": "location_action", "detail": {"action_id": "warehouse_deposit", "result": {"ok": true, "reason": "ok"}, "result_summary": {"destination_id": "SYS-004-DST-01", "quantity": 10, "sku_id": "military_hardware", "warehouse_available_after": 0, "warehouse_used_after": 10}}, "stage": "location_action", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 1511, "destination_id": "SYS-004-DST-01", "location_id": "SYS-004-DST-01-LOC-warehouse", "system_id": "SYS-004"}, "turn_after": 54, "turn_before": 54, "version": "0.11.0"}
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {}, "credits": 1511, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-01", "fuel_capacity": 55, "fuel_current": 6, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-01-LOC-warehouse", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 20, "turn": 54, "warehouse_cost_per_turn": 20, "warehouses": [{"available": 0, "capacity": 10, "cost_per_turn": 20, "destination_id": "SYS-004-DST-01", "goods": {"military_hardware": 10}, "used": 10}], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
WAREHOUSE PROFILE
  Rented capacity: 10
  Used storage: 10
  Available storage: 0
  Rental cost per turn: 20
  Stored goods list:
    military_hardware: 10
LOCATION: warehouse
1) Rent space
2) Deposit cargo
3) Withdraw cargo
4) Return to Destination
Select action index: 1
Units to rent: 10
[v0.11.0][turn 54] action=engine:start change={"command_type": "location_action", "detail": {"command_type": "location_action"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=interaction_layer:location_action change={"command_type": "location_action", "detail": {"action_id": "warehouse_rent", "result": {"ok": true, "reason": "ok"}, "result_summary": {"capacity_after": 20, "capacity_before": 10, "cost_per_turn_per_capacity": 2, "destination_id": "SYS-004-DST-01", "result_ok": true, "units_rented": 10}}, "stage": "location_action", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "location_action", "error": null, "events": [{"command_type": "location_action", "detail": {"command_type": "location_action"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}, {"command_type": "location_action", "detail": {"action_id": "warehouse_rent", "result": {"ok": true, "reason": "ok"}, "result_summary": {"capacity_after": 20, "capacity_before": 10, "cost_per_turn_per_capacity": 2, "destination_id": "SYS-004-DST-01", "result_ok": true, "units_rented": 10}}, "stage": "location_action", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 1511, "destination_id": "SYS-004-DST-01", "location_id": "SYS-004-DST-01-LOC-warehouse", "system_id": "SYS-004"}, "turn_after": 54, "turn_before": 54, "version": "0.11.0"}
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {}, "credits": 1511, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-01", "fuel_capacity": 55, "fuel_current": 6, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-01-LOC-warehouse", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 40, "turn": 54, "warehouse_cost_per_turn": 40, "warehouses": [{"available": 10, "capacity": 20, "cost_per_turn": 40, "destination_id": "SYS-004-DST-01", "goods": {"military_hardware": 10}, "used": 10}], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
WAREHOUSE PROFILE
  Rented capacity: 20
  Used storage: 10
  Available storage: 10
  Rental cost per turn: 40
  Stored goods list:
    military_hardware: 10
LOCATION: warehouse
1) Rent space
2) Deposit cargo
3) Withdraw cargo
4) Return to Destination
Select action index: 2
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {}, "credits": 1511, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-01", "fuel_capacity": 55, "fuel_current": 6, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-01-LOC-warehouse", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 40, "turn": 54, "warehouse_cost_per_turn": 40, "warehouses": [{"available": 10, "capacity": 20, "cost_per_turn": 40, "destination_id": "SYS-004-DST-01", "goods": {"military_hardware": 10}, "used": 10}], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
No cargo available to deposit.
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {}, "credits": 1511, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-01", "fuel_capacity": 55, "fuel_current": 6, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-01-LOC-warehouse", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 40, "turn": 54, "warehouse_cost_per_turn": 40, "warehouses": [{"available": 10, "capacity": 20, "cost_per_turn": 40, "destination_id": "SYS-004-DST-01", "goods": {"military_hardware": 10}, "used": 10}], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
WAREHOUSE PROFILE
  Rented capacity: 20
  Used storage: 10
  Available storage: 10
  Rental cost per turn: 40
  Stored goods list:
    military_hardware: 10
LOCATION: warehouse
1) Rent space
2) Deposit cargo
3) Withdraw cargo
4) Return to Destination
Select action index: 4
[v0.11.0][turn 54] action=engine:start change={"command_type": "return_to_destination", "detail": {"command_type": "return_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:location_navigation change={"command_type": "return_to_destination", "detail": {"action": "return_to_destination", "destination_id": "SYS-004-DST-01"}, "stage": "location_navigation", "subsystem": "engine", "turn": 54, "world_seed": 12345}
Returned to destination: SYS-004-DST-01
DESTINATION: Flux 1 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 1
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {}, "credits": 1511, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-01", "fuel_capacity": 55, "fuel_current": 6, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-01", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 40, "turn": 54, "warehouse_cost_per_turn": 40, "warehouses": [{"available": 10, "capacity": 20, "cost_per_turn": 40, "destination_id": "SYS-004-DST-01", "goods": {"military_hardware": 10}, "used": 10}], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_destination_profile", "detail": {"command_type": "get_destination_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:destination_profile change={"command_type": "get_destination_profile", "detail": {"active_crew": [], "active_destination_situations": [], "active_missions": [], "destination_id": "SYS-004-DST-01", "locations": [{"location_id": "SYS-004-DST-01-LOC-datanet", "location_type": "datanet"}, {"location_id": "SYS-004-DST-01-LOC-market", "location_type": "market"}, {"location_id": "SYS-004-DST-01-LOC-warehouse", "location_type": "warehouse"}], "market_attached": true, "name": "Flux 1", "population": 2, "primary_economy": "research"}, "stage": "destination_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
PLAYER / SHIP INFO
  Credits: 1511
  Fuel: 6/55
  Cargo manifest: {}
  Reputation: 50 band=0
  Heat: 0
  Notoriety: 0 band=-2
  Arrest state: free
  Warrants: []
  Location: SYS-004 / SYS-004-DST-01 / SYS-004-DST-01
  Turn: 54
  Active crew: []
  Active missions: []
ONGOING COSTS
  Insurance: 0
  Warehouse rental: 40
  Crew wages: 0
  Total recurring cost: 40
WAREHOUSE RENTALS
  1) destination=SYS-004-DST-01 capacity=20 used=10 available=10 cost/turn=40 goods={'military_hardware': 10}
Cancel warehouse rental index [0 skip]: 0
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
[v0.11.0][turn 54] action=engine:start change={"command_type": "enter_location", "detail": {"command_type": "enter_location"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=law_enforcement:law_checkpoint change={"command_type": "enter_location", "detail": {"skipped": true, "trigger_type": "CUSTOMS"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:location_navigation change={"command_type": "enter_location", "detail": {"action": "enter_location", "location_id": "SYS-004-DST-01-LOC-market", "location_type": "market", "resolved_npc_ids": []}, "stage": "location_navigation", "subsystem": "engine", "turn": 54, "world_seed": 12345}
Entered location: SYS-004-DST-01-LOC-market
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_market_profile", "detail": {"command_type": "get_market_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=market:market_profile change={"command_type": "get_market_profile", "detail": {"active_situations": ["trade_boom"], "categories": {"CHEMICALS": {"consumed": ["experimental_serums", "medical_compounds"], "neutral": [], "produced": []}, "DATA": {"consumed": [], "neutral": ["ai_training_sets", "encrypted_records"], "produced": ["media_packages", "propaganda_feeds"]}, "ENERGY": {"consumed": [], "neutral": [], "produced": ["fusion_cores", "standard_fuel"]}, "MEDICINE": {"consumed": [], "neutral": [], "produced": ["gene_therapy_kits", "medical_nanites"]}, "PARTS": {"consumed": ["cybernetic_implants", "weaponized_autonomous_robots"], "neutral": [], "produced": []}}, "destination_id": "SYS-004-DST-01", "primary_economy_id": "research", "secondary_economy_ids": [], "system_id": "SYS-004"}, "stage": "market_profile", "subsystem": "market", "turn": 54, "world_seed": 12345}
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
[v0.11.0][turn 54] action=engine:start change={"command_type": "market_buy_list", "detail": {"command_type": "market_buy_list"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=market:market_buy_list change={"command_type": "market_buy_list", "detail": {"destination_id": "SYS-004-DST-01", "rows": [{"available_units": null, "display_name": "AI Training Sets", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "ai_training_sets", "unit_price": 302}, {"available_units": null, "display_name": "Cybernetic Implants", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "cybernetic_implants", "unit_price": 392}, {"available_units": null, "display_name": "Encrypted Records", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "encrypted_records", "unit_price": 201}, {"available_units": null, "display_name": "Experimental Serums", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "experimental_serums", "unit_price": 453}, {"available_units": null, "display_name": "Fusion Cores", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "fusion_cores", "unit_price": 342}, {"available_units": null, "display_name": "Gene Therapy Kits", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "gene_therapy_kits", "unit_price": 322}, {"available_units": null, "display_name": "Media Packages", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "media_packages", "unit_price": 161}, {"available_units": null, "display_name": "Medical Compounds", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "medical_compounds", "unit_price": 272}, {"available_units": null, "display_name": "Medical Nanites", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "medical_nanites", "unit_price": 362}, {"available_units": null, "display_name": "Propaganda Feeds", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "propaganda_feeds", "unit_price": 181}, {"available_units": null, "display_name": "Standard Fuel", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "standard_fuel", "unit_price": 151}, {"available_units": null, "display_name": "Weaponized Autonomous Robots", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "weaponized_autonomous_robots", "unit_price": 679}]}, "stage": "market_buy_list", "subsystem": "market", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:start change={"command_type": "market_sell_list", "detail": {"command_type": "market_sell_list"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=market:market_sell_list change={"command_type": "market_sell_list", "detail": {"destination_id": "SYS-004-DST-01", "rows": []}, "stage": "market_sell_list", "subsystem": "market", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {}, "credits": 1511, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-01", "fuel_capacity": 55, "fuel_current": 6, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-01-LOC-market", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 40, "turn": 54, "warehouse_cost_per_turn": 40, "warehouses": [{"available": 10, "capacity": 20, "cost_per_turn": 40, "destination_id": "SYS-004-DST-01", "goods": {"military_hardware": 10}, "used": 10}], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
MARKET SKUS
  ai_training_sets | AI Training Sets | buy=302 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_implants | Cybernetic Implants | buy=392 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  encrypted_records | Encrypted Records | buy=201 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_serums | Experimental Serums | buy=453 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fusion_cores | Fusion Cores | buy=342 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=322 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  media_packages | Media Packages | buy=161 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_compounds | Medical Compounds | buy=272 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=362 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  propaganda_feeds | Propaganda Feeds | buy=181 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=151 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=679 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 1
[v0.11.0][turn 54] action=engine:start change={"command_type": "market_buy_list", "detail": {"command_type": "market_buy_list"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=market:market_buy_list change={"command_type": "market_buy_list", "detail": {"destination_id": "SYS-004-DST-01", "rows": [{"available_units": null, "display_name": "AI Training Sets", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "ai_training_sets", "unit_price": 302}, {"available_units": null, "display_name": "Cybernetic Implants", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "cybernetic_implants", "unit_price": 392}, {"available_units": null, "display_name": "Encrypted Records", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "encrypted_records", "unit_price": 201}, {"available_units": null, "display_name": "Experimental Serums", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "experimental_serums", "unit_price": 453}, {"available_units": null, "display_name": "Fusion Cores", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "fusion_cores", "unit_price": 342}, {"available_units": null, "display_name": "Gene Therapy Kits", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "gene_therapy_kits", "unit_price": 322}, {"available_units": null, "display_name": "Media Packages", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "media_packages", "unit_price": 161}, {"available_units": null, "display_name": "Medical Compounds", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "medical_compounds", "unit_price": 272}, {"available_units": null, "display_name": "Medical Nanites", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "medical_nanites", "unit_price": 362}, {"available_units": null, "display_name": "Propaganda Feeds", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "propaganda_feeds", "unit_price": 181}, {"available_units": null, "display_name": "Standard Fuel", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "standard_fuel", "unit_price": 151}, {"available_units": null, "display_name": "Weaponized Autonomous Robots", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "weaponized_autonomous_robots", "unit_price": 679}]}, "stage": "market_buy_list", "subsystem": "market", "turn": 54, "world_seed": 12345}
1) ai_training_sets AI Training Sets price=302 legality=LEGAL risk=Severe
2) cybernetic_implants Cybernetic Implants price=392 legality=LEGAL risk=Severe
3) encrypted_records Encrypted Records price=201 legality=LEGAL risk=Severe
4) experimental_serums Experimental Serums price=453 legality=LEGAL risk=Severe
5) fusion_cores Fusion Cores price=342 legality=LEGAL risk=Severe
6) gene_therapy_kits Gene Therapy Kits price=322 legality=LEGAL risk=Severe
7) media_packages Media Packages price=161 legality=LEGAL risk=Severe
8) medical_compounds Medical Compounds price=272 legality=LEGAL risk=Severe
9) medical_nanites Medical Nanites price=362 legality=LEGAL risk=Severe
10) propaganda_feeds Propaganda Feeds price=181 legality=LEGAL risk=Severe
11) standard_fuel Standard Fuel price=151 legality=LEGAL risk=Severe
12) weaponized_autonomous_robots Weaponized Autonomous Robots price=679 legality=LEGAL risk=Severe
Select buy sku index: 7
Quantity: 10
[v0.11.0][turn 54] action=engine:start change={"command_type": "market_buy", "detail": {"command_type": "market_buy"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=law_enforcement:customs_guard change={"command_type": "market_buy", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 54, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "market_buy", "error": "insufficient_credits", "events": [{"command_type": "market_buy", "detail": {"command_type": "market_buy"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 54, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": false, "player": {"arrest_state": "free", "credits": 1511, "destination_id": "SYS-004-DST-01", "location_id": "SYS-004-DST-01-LOC-market", "system_id": "SYS-004"}, "turn_after": 54, "turn_before": 54, "version": "0.11.0"}
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_market_profile", "detail": {"command_type": "get_market_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=market:market_profile change={"command_type": "get_market_profile", "detail": {"active_situations": ["trade_boom"], "categories": {"CHEMICALS": {"consumed": ["experimental_serums", "medical_compounds"], "neutral": [], "produced": []}, "DATA": {"consumed": [], "neutral": ["ai_training_sets", "encrypted_records"], "produced": ["media_packages", "propaganda_feeds"]}, "ENERGY": {"consumed": [], "neutral": [], "produced": ["fusion_cores", "standard_fuel"]}, "MEDICINE": {"consumed": [], "neutral": [], "produced": ["gene_therapy_kits", "medical_nanites"]}, "PARTS": {"consumed": ["cybernetic_implants", "weaponized_autonomous_robots"], "neutral": [], "produced": []}}, "destination_id": "SYS-004-DST-01", "primary_economy_id": "research", "secondary_economy_ids": [], "system_id": "SYS-004"}, "stage": "market_profile", "subsystem": "market", "turn": 54, "world_seed": 12345}
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
[v0.11.0][turn 54] action=engine:start change={"command_type": "market_buy_list", "detail": {"command_type": "market_buy_list"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=market:market_buy_list change={"command_type": "market_buy_list", "detail": {"destination_id": "SYS-004-DST-01", "rows": [{"available_units": null, "display_name": "AI Training Sets", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "ai_training_sets", "unit_price": 302}, {"available_units": null, "display_name": "Cybernetic Implants", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "cybernetic_implants", "unit_price": 392}, {"available_units": null, "display_name": "Encrypted Records", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "encrypted_records", "unit_price": 201}, {"available_units": null, "display_name": "Experimental Serums", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "experimental_serums", "unit_price": 453}, {"available_units": null, "display_name": "Fusion Cores", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "fusion_cores", "unit_price": 342}, {"available_units": null, "display_name": "Gene Therapy Kits", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "gene_therapy_kits", "unit_price": 322}, {"available_units": null, "display_name": "Media Packages", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "media_packages", "unit_price": 161}, {"available_units": null, "display_name": "Medical Compounds", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "medical_compounds", "unit_price": 272}, {"available_units": null, "display_name": "Medical Nanites", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "medical_nanites", "unit_price": 362}, {"available_units": null, "display_name": "Propaganda Feeds", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "propaganda_feeds", "unit_price": 181}, {"available_units": null, "display_name": "Standard Fuel", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "standard_fuel", "unit_price": 151}, {"available_units": null, "display_name": "Weaponized Autonomous Robots", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "weaponized_autonomous_robots", "unit_price": 679}]}, "stage": "market_buy_list", "subsystem": "market", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:start change={"command_type": "market_sell_list", "detail": {"command_type": "market_sell_list"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=market:market_sell_list change={"command_type": "market_sell_list", "detail": {"destination_id": "SYS-004-DST-01", "rows": []}, "stage": "market_sell_list", "subsystem": "market", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {}, "credits": 1511, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-01", "fuel_capacity": 55, "fuel_current": 6, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-01-LOC-market", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 40, "turn": 54, "warehouse_cost_per_turn": 40, "warehouses": [{"available": 10, "capacity": 20, "cost_per_turn": 40, "destination_id": "SYS-004-DST-01", "goods": {"military_hardware": 10}, "used": 10}], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
MARKET SKUS
  ai_training_sets | AI Training Sets | buy=302 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_implants | Cybernetic Implants | buy=392 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  encrypted_records | Encrypted Records | buy=201 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_serums | Experimental Serums | buy=453 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fusion_cores | Fusion Cores | buy=342 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=322 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  media_packages | Media Packages | buy=161 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_compounds | Medical Compounds | buy=272 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=362 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  propaganda_feeds | Propaganda Feeds | buy=181 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=151 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=679 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 1
[v0.11.0][turn 54] action=engine:start change={"command_type": "market_buy_list", "detail": {"command_type": "market_buy_list"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=market:market_buy_list change={"command_type": "market_buy_list", "detail": {"destination_id": "SYS-004-DST-01", "rows": [{"available_units": null, "display_name": "AI Training Sets", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "ai_training_sets", "unit_price": 302}, {"available_units": null, "display_name": "Cybernetic Implants", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "cybernetic_implants", "unit_price": 392}, {"available_units": null, "display_name": "Encrypted Records", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "encrypted_records", "unit_price": 201}, {"available_units": null, "display_name": "Experimental Serums", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "experimental_serums", "unit_price": 453}, {"available_units": null, "display_name": "Fusion Cores", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "fusion_cores", "unit_price": 342}, {"available_units": null, "display_name": "Gene Therapy Kits", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "gene_therapy_kits", "unit_price": 322}, {"available_units": null, "display_name": "Media Packages", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "media_packages", "unit_price": 161}, {"available_units": null, "display_name": "Medical Compounds", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "medical_compounds", "unit_price": 272}, {"available_units": null, "display_name": "Medical Nanites", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "medical_nanites", "unit_price": 362}, {"available_units": null, "display_name": "Propaganda Feeds", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "propaganda_feeds", "unit_price": 181}, {"available_units": null, "display_name": "Standard Fuel", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "standard_fuel", "unit_price": 151}, {"available_units": null, "display_name": "Weaponized Autonomous Robots", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "weaponized_autonomous_robots", "unit_price": 679}]}, "stage": "market_buy_list", "subsystem": "market", "turn": 54, "world_seed": 12345}
1) ai_training_sets AI Training Sets price=302 legality=LEGAL risk=Severe
2) cybernetic_implants Cybernetic Implants price=392 legality=LEGAL risk=Severe
3) encrypted_records Encrypted Records price=201 legality=LEGAL risk=Severe
4) experimental_serums Experimental Serums price=453 legality=LEGAL risk=Severe
5) fusion_cores Fusion Cores price=342 legality=LEGAL risk=Severe
6) gene_therapy_kits Gene Therapy Kits price=322 legality=LEGAL risk=Severe
7) media_packages Media Packages price=161 legality=LEGAL risk=Severe
8) medical_compounds Medical Compounds price=272 legality=LEGAL risk=Severe
9) medical_nanites Medical Nanites price=362 legality=LEGAL risk=Severe
10) propaganda_feeds Propaganda Feeds price=181 legality=LEGAL risk=Severe
11) standard_fuel Standard Fuel price=151 legality=LEGAL risk=Severe
12) weaponized_autonomous_robots Weaponized Autonomous Robots price=679 legality=LEGAL risk=Severe
Select buy sku index: 7
Quantity: 7
[v0.11.0][turn 54] action=engine:start change={"command_type": "market_buy", "detail": {"command_type": "market_buy"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=law_enforcement:customs_guard change={"command_type": "market_buy", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=market:market_trade change={"command_type": "market_buy", "detail": {"action": "buy", "cargo_after": 7, "credits_after": 384, "credits_before": 1511, "quantity": 7, "sku_id": "media_packages", "total_cost": 1127, "unit_price": 161}, "stage": "market_trade", "subsystem": "market", "turn": 54, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "market_buy", "error": null, "events": [{"command_type": "market_buy", "detail": {"command_type": "market_buy"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"blocked": true, "last_kind": "auto_market_entry", "reason": "customs_already_processed_this_turn"}, "stage": "customs_guard", "subsystem": "law_enforcement", "turn": 54, "world_seed": 12345}, {"command_type": "market_buy", "detail": {"action": "buy", "cargo_after": 7, "credits_after": 384, "credits_before": 1511, "quantity": 7, "sku_id": "media_packages", "total_cost": 1127, "unit_price": 161}, "stage": "market_trade", "subsystem": "market", "turn": 54, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 384, "destination_id": "SYS-004-DST-01", "location_id": "SYS-004-DST-01-LOC-market", "system_id": "SYS-004"}, "turn_after": 54, "turn_before": 54, "version": "0.11.0"}
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_market_profile", "detail": {"command_type": "get_market_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=market:market_profile change={"command_type": "get_market_profile", "detail": {"active_situations": ["trade_boom"], "categories": {"CHEMICALS": {"consumed": ["experimental_serums", "medical_compounds"], "neutral": [], "produced": []}, "DATA": {"consumed": [], "neutral": ["ai_training_sets", "encrypted_records"], "produced": ["media_packages", "propaganda_feeds"]}, "ENERGY": {"consumed": [], "neutral": [], "produced": ["fusion_cores", "standard_fuel"]}, "MEDICINE": {"consumed": [], "neutral": [], "produced": ["gene_therapy_kits", "medical_nanites"]}, "PARTS": {"consumed": ["cybernetic_implants", "weaponized_autonomous_robots"], "neutral": [], "produced": []}}, "destination_id": "SYS-004-DST-01", "primary_economy_id": "research", "secondary_economy_ids": [], "system_id": "SYS-004"}, "stage": "market_profile", "subsystem": "market", "turn": 54, "world_seed": 12345}
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
[v0.11.0][turn 54] action=engine:start change={"command_type": "market_buy_list", "detail": {"command_type": "market_buy_list"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=market:market_buy_list change={"command_type": "market_buy_list", "detail": {"destination_id": "SYS-004-DST-01", "rows": [{"available_units": null, "display_name": "AI Training Sets", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "ai_training_sets", "unit_price": 302}, {"available_units": null, "display_name": "Cybernetic Implants", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "cybernetic_implants", "unit_price": 392}, {"available_units": null, "display_name": "Encrypted Records", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "encrypted_records", "unit_price": 201}, {"available_units": null, "display_name": "Experimental Serums", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "experimental_serums", "unit_price": 453}, {"available_units": null, "display_name": "Fusion Cores", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "fusion_cores", "unit_price": 342}, {"available_units": null, "display_name": "Gene Therapy Kits", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "gene_therapy_kits", "unit_price": 322}, {"available_units": null, "display_name": "Media Packages", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "media_packages", "unit_price": 161}, {"available_units": null, "display_name": "Medical Compounds", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "medical_compounds", "unit_price": 272}, {"available_units": null, "display_name": "Medical Nanites", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "medical_nanites", "unit_price": 362}, {"available_units": null, "display_name": "Propaganda Feeds", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "propaganda_feeds", "unit_price": 181}, {"available_units": null, "display_name": "Standard Fuel", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "standard_fuel", "unit_price": 151}, {"available_units": null, "display_name": "Weaponized Autonomous Robots", "legality": "LEGAL", "risk_tier": "Severe", "sku_id": "weaponized_autonomous_robots", "unit_price": 679}]}, "stage": "market_buy_list", "subsystem": "market", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:start change={"command_type": "market_sell_list", "detail": {"command_type": "market_sell_list"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=market:market_sell_list change={"command_type": "market_sell_list", "detail": {"destination_id": "SYS-004-DST-01", "rows": [{"available_units": null, "display_name": "Media Packages", "legality": "LEGAL", "player_has_units": 7, "risk_tier": "Severe", "sku_id": "media_packages", "unit_price": 161}]}, "stage": "market_sell_list", "subsystem": "market", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {"media_packages": 7}, "credits": 384, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-01", "fuel_capacity": 55, "fuel_current": 6, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-01-LOC-market", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 40, "turn": 54, "warehouse_cost_per_turn": 40, "warehouses": [{"available": 10, "capacity": 20, "cost_per_turn": 40, "destination_id": "SYS-004-DST-01", "goods": {"military_hardware": 10}, "used": 10}], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
MARKET SKUS
  ai_training_sets | AI Training Sets | buy=302 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  cybernetic_implants | Cybernetic Implants | buy=392 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  encrypted_records | Encrypted Records | buy=201 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  experimental_serums | Experimental Serums | buy=453 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  fusion_cores | Fusion Cores | buy=342 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  gene_therapy_kits | Gene Therapy Kits | buy=322 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  media_packages | Media Packages | buy=161 | sell=161 | cargo=7 | legality=LEGAL | risk=Severe
  medical_compounds | Medical Compounds | buy=272 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  medical_nanites | Medical Nanites | buy=362 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  propaganda_feeds | Propaganda Feeds | buy=181 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  standard_fuel | Standard Fuel | buy=151 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
  weaponized_autonomous_robots | Weaponized Autonomous Robots | buy=679 | sell=-- | cargo=0 | legality=LEGAL | risk=Severe
LOCATION: market
1) Buy
2) Sell
3) Return to Destination
Select action index: 3
[v0.11.0][turn 54] action=engine:start change={"command_type": "return_to_destination", "detail": {"command_type": "return_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:location_navigation change={"command_type": "return_to_destination", "detail": {"action": "return_to_destination", "destination_id": "SYS-004-DST-01"}, "stage": "location_navigation", "subsystem": "engine", "turn": 54, "world_seed": 12345}
Returned to destination: SYS-004-DST-01
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
Select location index: 3
[v0.11.0][turn 54] action=engine:start change={"command_type": "enter_location", "detail": {"command_type": "enter_location"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:location_navigation change={"command_type": "enter_location", "detail": {"action": "enter_location", "location_id": "SYS-004-DST-01-LOC-warehouse", "location_type": "warehouse", "resolved_npc_ids": []}, "stage": "location_navigation", "subsystem": "engine", "turn": 54, "world_seed": 12345}
Entered location: SYS-004-DST-01-LOC-warehouse
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {"media_packages": 7}, "credits": 384, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-01", "fuel_capacity": 55, "fuel_current": 6, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-01-LOC-warehouse", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 40, "turn": 54, "warehouse_cost_per_turn": 40, "warehouses": [{"available": 10, "capacity": 20, "cost_per_turn": 40, "destination_id": "SYS-004-DST-01", "goods": {"military_hardware": 10}, "used": 10}], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
WAREHOUSE PROFILE
  Rented capacity: 20
  Used storage: 10
  Available storage: 10
  Rental cost per turn: 40
  Stored goods list:
    military_hardware: 10
LOCATION: warehouse
1) Rent space
2) Deposit cargo
3) Withdraw cargo
4) Return to Destination
Select action index: 2
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {"media_packages": 7}, "credits": 384, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-01", "fuel_capacity": 55, "fuel_current": 6, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-01-LOC-warehouse", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 40, "turn": 54, "warehouse_cost_per_turn": 40, "warehouses": [{"available": 10, "capacity": 20, "cost_per_turn": 40, "destination_id": "SYS-004-DST-01", "goods": {"military_hardware": 10}, "used": 10}], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
1) media_packages units=7
Select cargo SKU index: 1
Quantity: 7
[v0.11.0][turn 54] action=engine:start change={"command_type": "location_action", "detail": {"command_type": "location_action"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=interaction_layer:location_action change={"command_type": "location_action", "detail": {"action_id": "warehouse_deposit", "result": {"ok": true, "reason": "ok"}, "result_summary": {"destination_id": "SYS-004-DST-01", "quantity": 7, "sku_id": "media_packages", "warehouse_available_after": 3, "warehouse_used_after": 17}}, "stage": "location_action", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "location_action", "error": null, "events": [{"command_type": "location_action", "detail": {"command_type": "location_action"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}, {"command_type": "location_action", "detail": {"action_id": "warehouse_deposit", "result": {"ok": true, "reason": "ok"}, "result_summary": {"destination_id": "SYS-004-DST-01", "quantity": 7, "sku_id": "media_packages", "warehouse_available_after": 3, "warehouse_used_after": 17}}, "stage": "location_action", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 384, "destination_id": "SYS-004-DST-01", "location_id": "SYS-004-DST-01-LOC-warehouse", "system_id": "SYS-004"}, "turn_after": 54, "turn_before": 54, "version": "0.11.0"}
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {}, "credits": 384, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-01", "fuel_capacity": 55, "fuel_current": 6, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-01-LOC-warehouse", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 40, "turn": 54, "warehouse_cost_per_turn": 40, "warehouses": [{"available": 3, "capacity": 20, "cost_per_turn": 40, "destination_id": "SYS-004-DST-01", "goods": {"media_packages": 7, "military_hardware": 10}, "used": 17}], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
WAREHOUSE PROFILE
  Rented capacity: 20
  Used storage: 17
  Available storage: 3
  Rental cost per turn: 40
  Stored goods list:
    media_packages: 7
    military_hardware: 10
LOCATION: warehouse
1) Rent space
2) Deposit cargo
3) Withdraw cargo
4) Return to Destination
Select action index: 4
[v0.11.0][turn 54] action=engine:start change={"command_type": "return_to_destination", "detail": {"command_type": "return_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:location_navigation change={"command_type": "return_to_destination", "detail": {"action": "return_to_destination", "destination_id": "SYS-004-DST-01"}, "stage": "location_navigation", "subsystem": "engine", "turn": 54, "world_seed": 12345}
Returned to destination: SYS-004-DST-01
DESTINATION: Flux 1 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 1
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {}, "credits": 384, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-01", "fuel_capacity": 55, "fuel_current": 6, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-01", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 40, "turn": 54, "warehouse_cost_per_turn": 40, "warehouses": [{"available": 3, "capacity": 20, "cost_per_turn": 40, "destination_id": "SYS-004-DST-01", "goods": {"media_packages": 7, "military_hardware": 10}, "used": 17}], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_destination_profile", "detail": {"command_type": "get_destination_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:destination_profile change={"command_type": "get_destination_profile", "detail": {"active_crew": [], "active_destination_situations": [], "active_missions": [], "destination_id": "SYS-004-DST-01", "locations": [{"location_id": "SYS-004-DST-01-LOC-datanet", "location_type": "datanet"}, {"location_id": "SYS-004-DST-01-LOC-market", "location_type": "market"}, {"location_id": "SYS-004-DST-01-LOC-warehouse", "location_type": "warehouse"}], "market_attached": true, "name": "Flux 1", "population": 2, "primary_economy": "research"}, "stage": "destination_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
PLAYER / SHIP INFO
  Credits: 384
  Fuel: 6/55
  Cargo manifest: {}
  Reputation: 50 band=0
  Heat: 0
  Notoriety: 0 band=-2
  Arrest state: free
  Warrants: []
  Location: SYS-004 / SYS-004-DST-01 / SYS-004-DST-01
  Turn: 54
  Active crew: []
  Active missions: []
ONGOING COSTS
  Insurance: 0
  Warehouse rental: 40
  Crew wages: 0
  Total recurring cost: 40
WAREHOUSE RENTALS
  1) destination=SYS-004-DST-01 capacity=20 used=17 available=3 cost/turn=40 goods={'military_hardware': 10, 'media_packages': 7}
Cancel warehouse rental index [0 skip]: 0
DESTINATION: Flux 1 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 4
[v0.11.0][turn 54] action=engine:start change={"command_type": "list_destination_actions", "detail": {"command_type": "list_destination_actions"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=interaction_layer:destination_actions change={"command_type": "list_destination_actions", "detail": {"actions": [{"action_id": "customs_inspection", "description": "Run a voluntary customs inspection at destination level.", "display_name": "Customs Inspection", "fuel_cost": 0, "parameters": [], "requires_confirm": false, "time_cost_days": 0}, {"action_id": "refuel", "description": "Purchase fuel units up to ship fuel capacity.", "display_name": "Refuel", "fuel_cost": 0, "parameters": ["requested_units"], "requires_confirm": false, "time_cost_days": 0}], "destination_id": "SYS-004-DST-01"}, "stage": "destination_actions", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
1) customs_inspection Customs Inspection
2) refuel Refuel
3) Back
Select destination action index: 2
requested_units: 55
[v0.11.0][turn 54] action=engine:start change={"command_type": "destination_action", "detail": {"command_type": "destination_action"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=interaction_layer:destination_action change={"command_type": "destination_action", "detail": {"action_id": "refuel", "result": {"credits": 139, "current_fuel": 55, "ok": true, "reason": "ok", "total_cost": 245, "units_purchased": 49}, "result_summary": {"credits_after": 139, "credits_before": 384, "fuel_after": 55, "fuel_before": 6, "reason": "ok", "result_ok": true, "total_cost": 245, "unit_price": 5, "units_purchased": 49}}, "stage": "destination_action", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "destination_action", "error": null, "events": [{"command_type": "destination_action", "detail": {"command_type": "destination_action"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}, {"command_type": "destination_action", "detail": {"action_id": "refuel", "result": {"credits": 139, "current_fuel": 55, "ok": true, "reason": "ok", "total_cost": 245, "units_purchased": 49}, "result_summary": {"credits_after": 139, "credits_before": 384, "fuel_after": 55, "fuel_before": 6, "reason": "ok", "result_ok": true, "total_cost": 245, "unit_price": 5, "units_purchased": 49}}, "stage": "destination_action", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 139, "destination_id": "SYS-004-DST-01", "location_id": "SYS-004-DST-01", "system_id": "SYS-004"}, "turn_after": 54, "turn_before": 54, "version": "0.11.0"}
[v0.11.0][turn 54] action=engine:start change={"command_type": "list_destination_actions", "detail": {"command_type": "list_destination_actions"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=interaction_layer:destination_actions change={"command_type": "list_destination_actions", "detail": {"actions": [{"action_id": "customs_inspection", "description": "Run a voluntary customs inspection at destination level.", "display_name": "Customs Inspection", "fuel_cost": 0, "parameters": [], "requires_confirm": false, "time_cost_days": 0}, {"action_id": "refuel", "description": "Purchase fuel units up to ship fuel capacity.", "display_name": "Refuel", "fuel_cost": 0, "parameters": ["requested_units"], "requires_confirm": false, "time_cost_days": 0}], "destination_id": "SYS-004-DST-01"}, "stage": "destination_actions", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
1) customs_inspection Customs Inspection
2) refuel Refuel
3) Back
Select destination action index: 3
DESTINATION: Flux 1 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 1
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {}, "credits": 139, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-01", "fuel_capacity": 55, "fuel_current": 55, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-01", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 40, "turn": 54, "warehouse_cost_per_turn": 40, "warehouses": [{"available": 3, "capacity": 20, "cost_per_turn": 40, "destination_id": "SYS-004-DST-01", "goods": {"media_packages": 7, "military_hardware": 10}, "used": 17}], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_destination_profile", "detail": {"command_type": "get_destination_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:destination_profile change={"command_type": "get_destination_profile", "detail": {"active_crew": [], "active_destination_situations": [], "active_missions": [], "destination_id": "SYS-004-DST-01", "locations": [{"location_id": "SYS-004-DST-01-LOC-datanet", "location_type": "datanet"}, {"location_id": "SYS-004-DST-01-LOC-market", "location_type": "market"}, {"location_id": "SYS-004-DST-01-LOC-warehouse", "location_type": "warehouse"}], "market_attached": true, "name": "Flux 1", "population": 2, "primary_economy": "research"}, "stage": "destination_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
PLAYER / SHIP INFO
  Credits: 139
  Fuel: 55/55
  Cargo manifest: {}
  Reputation: 50 band=0
  Heat: 0
  Notoriety: 0 band=-2
  Arrest state: free
  Warrants: []
  Location: SYS-004 / SYS-004-DST-01 / SYS-004-DST-01
  Turn: 54
  Active crew: []
  Active missions: []
ONGOING COSTS
  Insurance: 0
  Warehouse rental: 40
  Crew wages: 0
  Total recurring cost: 40
WAREHOUSE RENTALS
  1) destination=SYS-004-DST-01 capacity=20 used=17 available=3 cost/turn=40 goods={'military_hardware': 10, 'media_packages': 7}
Cancel warehouse rental index [0 skip]: 0
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
Select location index: 3
[v0.11.0][turn 54] action=engine:start change={"command_type": "enter_location", "detail": {"command_type": "enter_location"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:location_navigation change={"command_type": "enter_location", "detail": {"action": "enter_location", "location_id": "SYS-004-DST-01-LOC-warehouse", "location_type": "warehouse", "resolved_npc_ids": []}, "stage": "location_navigation", "subsystem": "engine", "turn": 54, "world_seed": 12345}
Entered location: SYS-004-DST-01-LOC-warehouse
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {}, "credits": 139, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-01", "fuel_capacity": 55, "fuel_current": 55, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-01-LOC-warehouse", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 40, "turn": 54, "warehouse_cost_per_turn": 40, "warehouses": [{"available": 3, "capacity": 20, "cost_per_turn": 40, "destination_id": "SYS-004-DST-01", "goods": {"media_packages": 7, "military_hardware": 10}, "used": 17}], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
WAREHOUSE PROFILE
  Rented capacity: 20
  Used storage: 17
  Available storage: 3
  Rental cost per turn: 40
  Stored goods list:
    media_packages: 7
    military_hardware: 10
LOCATION: warehouse
1) Rent space
2) Deposit cargo
3) Withdraw cargo
4) Return to Destination
Select action index: 1
Units to rent: 40
[v0.11.0][turn 54] action=engine:start change={"command_type": "location_action", "detail": {"command_type": "location_action"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=interaction_layer:location_action change={"command_type": "location_action", "detail": {"action_id": "warehouse_rent", "result": {"ok": true, "reason": "ok"}, "result_summary": {"capacity_after": 60, "capacity_before": 20, "cost_per_turn_per_capacity": 2, "destination_id": "SYS-004-DST-01", "result_ok": true, "units_rented": 40}}, "stage": "location_action", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "location_action", "error": null, "events": [{"command_type": "location_action", "detail": {"command_type": "location_action"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}, {"command_type": "location_action", "detail": {"action_id": "warehouse_rent", "result": {"ok": true, "reason": "ok"}, "result_summary": {"capacity_after": 60, "capacity_before": 20, "cost_per_turn_per_capacity": 2, "destination_id": "SYS-004-DST-01", "result_ok": true, "units_rented": 40}}, "stage": "location_action", "subsystem": "interaction_layer", "turn": 54, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 139, "destination_id": "SYS-004-DST-01", "location_id": "SYS-004-DST-01-LOC-warehouse", "system_id": "SYS-004"}, "turn_after": 54, "turn_before": 54, "version": "0.11.0"}
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {}, "credits": 139, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-01", "fuel_capacity": 55, "fuel_current": 55, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-01-LOC-warehouse", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 120, "turn": 54, "warehouse_cost_per_turn": 120, "warehouses": [{"available": 43, "capacity": 60, "cost_per_turn": 120, "destination_id": "SYS-004-DST-01", "goods": {"media_packages": 7, "military_hardware": 10}, "used": 17}], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
WAREHOUSE PROFILE
  Rented capacity: 60
  Used storage: 17
  Available storage: 43
  Rental cost per turn: 120
  Stored goods list:
    media_packages: 7
    military_hardware: 10
LOCATION: warehouse
1) Rent space
2) Deposit cargo
3) Withdraw cargo
4) Return to Destination
Select action index: 4
[v0.11.0][turn 54] action=engine:start change={"command_type": "return_to_destination", "detail": {"command_type": "return_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:location_navigation change={"command_type": "return_to_destination", "detail": {"action": "return_to_destination", "destination_id": "SYS-004-DST-01"}, "stage": "location_navigation", "subsystem": "engine", "turn": 54, "world_seed": 12345}
Returned to destination: SYS-004-DST-01
DESTINATION: Flux 1 (SYS-004)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 1
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {}, "credits": 139, "crew_wages_per_turn": 0, "destination_id": "SYS-004-DST-01", "fuel_capacity": 55, "fuel_current": 55, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-004-DST-01", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-004", "total_recurring_cost_per_turn": 120, "turn": 54, "warehouse_cost_per_turn": 120, "warehouses": [{"available": 43, "capacity": 60, "cost_per_turn": 120, "destination_id": "SYS-004-DST-01", "goods": {"media_packages": 7, "military_hardware": 10}, "used": 17}], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:start change={"command_type": "get_destination_profile", "detail": {"command_type": "get_destination_profile"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=engine:destination_profile change={"command_type": "get_destination_profile", "detail": {"active_crew": [], "active_destination_situations": [], "active_missions": [], "destination_id": "SYS-004-DST-01", "locations": [{"location_id": "SYS-004-DST-01-LOC-datanet", "location_type": "datanet"}, {"location_id": "SYS-004-DST-01-LOC-market", "location_type": "market"}, {"location_id": "SYS-004-DST-01-LOC-warehouse", "location_type": "warehouse"}], "market_attached": true, "name": "Flux 1", "population": 2, "primary_economy": "research"}, "stage": "destination_profile", "subsystem": "engine", "turn": 54, "world_seed": 12345}
PLAYER / SHIP INFO
  Credits: 139
  Fuel: 55/55
  Cargo manifest: {}
  Reputation: 50 band=0
  Heat: 0
  Notoriety: 0 band=-2
  Arrest state: free
  Warrants: []
  Location: SYS-004 / SYS-004-DST-01 / SYS-004-DST-01
  Turn: 54
  Active crew: []
  Active missions: []
ONGOING COSTS
  Insurance: 0
  Warehouse rental: 120
  Crew wages: 0
  Total recurring cost: 120
WAREHOUSE RENTALS
  1) destination=SYS-004-DST-01 capacity=60 used=17 available=43 cost/turn=120 goods={'military_hardware': 10, 'media_packages': 7}
Cancel warehouse rental index [0 skip]: 0
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
Travel mode: 1
1) SYS-001 Ion distance_ly=51.844 government=democracy population=3 destinations=4 active_situations=[]
Select target system index: 1
[v0.11.0][turn 54] action=engine:start change={"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"distance_ly": 51.84375710593287, "distance_ly_ceiled": 52, "inter_system": true, "target_destination_id": "SYS-001-DST-01", "target_system_id": "SYS-001", "travel_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 54, "world_seed": 12345}
[v0.11.0][turn 54] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"current_fuel": 3, "fuel_capacity": 55, "fuel_cost": 52, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 54, "world_seed": 12345}
[time_engine] action=time_advance_requested change=start_turn=54 days=10 reason=travel:TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route
[time_engine] action=galaxy_tick change=day=55
[time_engine] action=system_tick change=day=55
[time_engine] action=planet_station_tick change=day=55
[time_engine] action=location_tick change=day=55
[time_engine] action=npc_tick change=day=55
[time_engine] action=end_of_day_log change=day=55
Spawn gate cooldown check: system_id=SYS-001 current_day=55 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=55 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.6672324483101936
[time_engine] action=time_advance_day_completed change=turn=55 hard_stop=None
[time_engine] action=galaxy_tick change=day=56
[time_engine] action=system_tick change=day=56
[time_engine] action=planet_station_tick change=day=56
[time_engine] action=location_tick change=day=56
[time_engine] action=npc_tick change=day=56
[time_engine] action=end_of_day_log change=day=56
Spawn gate cooldown check: system_id=SYS-001 current_day=56 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=56 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.9988135659666256
[time_engine] action=time_advance_day_completed change=turn=56 hard_stop=None
[time_engine] action=galaxy_tick change=day=57
[time_engine] action=system_tick change=day=57
[time_engine] action=planet_station_tick change=day=57
[time_engine] action=location_tick change=day=57
[time_engine] action=npc_tick change=day=57
[time_engine] action=end_of_day_log change=day=57
Spawn gate cooldown check: system_id=SYS-001 current_day=57 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=57 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.6034290160390922
Situation expired: trade_boom system=SYS-004
[time_engine] action=time_advance_day_completed change=turn=57 hard_stop=None
[time_engine] action=galaxy_tick change=day=58
[time_engine] action=system_tick change=day=58
[time_engine] action=planet_station_tick change=day=58
[time_engine] action=location_tick change=day=58
[time_engine] action=npc_tick change=day=58
[time_engine] action=end_of_day_log change=day=58
Spawn gate cooldown check: system_id=SYS-001 current_day=58 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=58 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.8713070810572678
[time_engine] action=time_advance_day_completed change=turn=58 hard_stop=None
[time_engine] action=galaxy_tick change=day=59
[time_engine] action=system_tick change=day=59
[time_engine] action=planet_station_tick change=day=59
[time_engine] action=location_tick change=day=59
[time_engine] action=npc_tick change=day=59
[time_engine] action=end_of_day_log change=day=59
Spawn gate cooldown check: system_id=SYS-001 current_day=59 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=59 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.7196129073999837
[time_engine] action=time_advance_day_completed change=turn=59 hard_stop=None
[time_engine] action=galaxy_tick change=day=60
[time_engine] action=system_tick change=day=60
[time_engine] action=planet_station_tick change=day=60
[time_engine] action=location_tick change=day=60
[time_engine] action=npc_tick change=day=60
[time_engine] action=end_of_day_log change=day=60
Spawn gate cooldown check: system_id=SYS-001 current_day=60 cooldown_until=None skipped=false reason=cooldown_clear
Spawn gate cooldown not set: system_id=SYS-001 current_day=60 cooldown_until=None reason=spawn_gate_roll_failed spawn_gate_roll=0.7646553312460135
[time_engine] action=time_advance_day_completed change=turn=60 hard_stop=None
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
[time_engine] action=time_advance_requested change=start_turn=64 days=10 reason=travel:TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route
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
[time_engine] action=time_advance_requested change=start_turn=74 days=10 reason=travel:TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route
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
[time_engine] action=time_advance_requested change=start_turn=84 days=10 reason=travel:TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route
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
[time_engine] action=time_advance_requested change=start_turn=94 days=10 reason=travel:TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route
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
[time_engine] action=time_advance_requested change=start_turn=104 days=2 reason=travel:TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route
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
[v0.11.0][turn 106] action=time_engine:time_advance change={"command_type": "travel_to_destination", "detail": {"days_completed": 52, "days_requested": 52, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 106, "world_seed": 12345}
[v0.11.0][turn 106] action=law_enforcement:law_checkpoint change={"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 106, "world_seed": 12345}
[v0.11.0][turn 106] action=encounter_generator:encounter_gen change={"command_type": "travel_to_destination", "detail": {"encounter_count": 3, "travel_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 106, "world_seed": 12345}
[v0.11.0][turn 106] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_1", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 106, "world_seed": 12345}
[v0.11.0][turn 106] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_1", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_1ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 106, "world_seed": 12345}
[v0.11.0][turn 106] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 106, "world_seed": 12345}
[v0.11.0][turn 106] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_2", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 106, "world_seed": 12345}
[v0.11.0][turn 106] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_2", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_2ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 106, "world_seed": 12345}
[v0.11.0][turn 106] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 106, "world_seed": 12345}
[v0.11.0][turn 106] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_3", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 106, "world_seed": 12345}
[v0.11.0][turn 106] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_3", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_3ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 106, "world_seed": 12345}
[v0.11.0][turn 106] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_3", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 106, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 51.84375710593287, "distance_ly_ceiled": 52, "inter_system": true, "target_destination_id": "SYS-001-DST-01", "target_system_id": "SYS-001", "travel_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 3, "fuel_capacity": 55, "fuel_cost": 52, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 54, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 52, "days_requested": 52, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 106, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 106, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 3, "travel_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 106, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_1", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 106, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_1", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_1ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 106, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 106, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_2", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 106, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_2", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_2ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 106, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 106, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_3", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 106, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_3", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_3ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 106, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-004:SYS-001:SYS-001-DST-01:54:auto_route_enc_3", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 106, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 0, "destination_id": "SYS-001-DST-01", "location_id": "SYS-001-DST-01", "system_id": "SYS-001"}, "turn_after": 106, "turn_before": 54, "version": "0.11.0"}
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
Select: 1
[v0.11.0][turn 106] action=engine:start change={"command_type": "get_player_profile", "detail": {"command_type": "get_player_profile"}, "stage": "start", "subsystem": "engine", "turn": 106, "world_seed": 12345}
[v0.11.0][turn 106] action=engine:player_profile change={"command_type": "get_player_profile", "detail": {"arrest_state": "free", "cargo_manifest": {}, "credits": 0, "crew_wages_per_turn": 0, "destination_id": "SYS-001-DST-01", "fuel_capacity": 55, "fuel_current": 3, "heat": 0, "insurance_cost_per_turn": 0, "location_id": "SYS-001-DST-01", "notoriety_band": -2, "notoriety_score": 0, "reputation_band": 0, "reputation_score": 50, "system_id": "SYS-001", "total_recurring_cost_per_turn": 120, "turn": 106, "warehouse_cost_per_turn": 120, "warehouses": [{"available": 43, "capacity": 60, "cost_per_turn": 120, "destination_id": "SYS-004-DST-01", "goods": {"media_packages": 7, "military_hardware": 10}, "used": 17}], "warrants": []}, "stage": "player_profile", "subsystem": "engine", "turn": 106, "world_seed": 12345}
[v0.11.0][turn 106] action=engine:start change={"command_type": "get_destination_profile", "detail": {"command_type": "get_destination_profile"}, "stage": "start", "subsystem": "engine", "turn": 106, "world_seed": 12345}
[v0.11.0][turn 106] action=engine:destination_profile change={"command_type": "get_destination_profile", "detail": {"active_crew": [], "active_destination_situations": [], "active_missions": [], "destination_id": "SYS-001-DST-01", "locations": [{"location_id": "SYS-001-DST-01-LOC-bar", "location_type": "bar"}, {"location_id": "SYS-001-DST-01-LOC-datanet", "location_type": "datanet"}, {"location_id": "SYS-001-DST-01-LOC-market", "location_type": "market"}, {"location_id": "SYS-001-DST-01-LOC-warehouse", "location_type": "warehouse"}], "market_attached": true, "name": "Ion 1", "population": 2, "primary_economy": "industrial"}, "stage": "destination_profile", "subsystem": "engine", "turn": 106, "world_seed": 12345}
PLAYER / SHIP INFO
  Credits: 0
  Fuel: 3/55
  Cargo manifest: {}
  Reputation: 50 band=0
  Heat: 0
  Notoriety: 0 band=-2
  Arrest state: free
  Warrants: []
  Location: SYS-001 / SYS-001-DST-01 / SYS-001-DST-01
  Turn: 106
  Active crew: []
  Active missions: []
ONGOING COSTS
  Insurance: 0
  Warehouse rental: 120
  Crew wages: 0
  Total recurring cost: 120
WAREHOUSE RENTALS
  1) destination=SYS-004-DST-01 capacity=60 used=17 available=43 cost/turn=120 goods={'military_hardware': 10, 'media_packages': 7}
Cancel warehouse rental index [0 skip]: 0
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
Select destination index: 3
[v0.11.0][turn 106] action=engine:start change={"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 106, "world_seed": 12345}
[v0.11.0][turn 106] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-001-DST-03", "target_system_id": "SYS-001", "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 106, "world_seed": 12345}
[v0.11.0][turn 106] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"current_fuel": 3, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 106, "world_seed": 12345}
[time_engine] action=time_advance_requested change=start_turn=106 days=1 reason=travel:TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route
[time_engine] action=galaxy_tick change=day=107
[time_engine] action=system_tick change=day=107
[time_engine] action=planet_station_tick change=day=107
[time_engine] action=location_tick change=day=107
[time_engine] action=npc_tick change=day=107
[time_engine] action=end_of_day_log change=day=107
Spawn gate cooldown check: system_id=SYS-001 current_day=107 cooldown_until=109 skipped=true reason=cooldown_active
[time_engine] action=time_advance_day_completed change=turn=107 hard_stop=None
[v0.11.0][turn 107] action=time_engine:time_advance change={"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 107, "world_seed": 12345}
[v0.11.0][turn 107] action=law_enforcement:law_checkpoint change={"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 107, "world_seed": 12345}
[v0.11.0][turn 107] action=encounter_generator:encounter_gen change={"command_type": "travel_to_destination", "detail": {"encounter_count": 5, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 107, "world_seed": 12345}
[v0.11.0][turn 107] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_0", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 107, "world_seed": 12345}
[v0.11.0][turn 107] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_0", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_0ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 107, "world_seed": 12345}
[v0.11.0][turn 107] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 107, "world_seed": 12345}
[v0.11.0][turn 107] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_1", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 107, "world_seed": 12345}
[v0.11.0][turn 107] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_1", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 107, "world_seed": 12345}
[v0.11.0][turn 107] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 107, "world_seed": 12345}
[v0.11.0][turn 107] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_2", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 107, "world_seed": 12345}
[v0.11.0][turn 107] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_2", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_2ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 107, "world_seed": 12345}
[v0.11.0][turn 107] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 107, "world_seed": 12345}
[v0.11.0][turn 107] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_4", "handler_payload": {"npc_outcome": "pursue"}, "next_handler": "pursuit_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 107, "world_seed": 12345}
[v0.11.0][turn 107] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_4", "resolver_outcome": {"escaped": true, "outcome": "escape_success", "resolver": "pursuit", "threshold": 0.5}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 107, "world_seed": 12345}
[v0.11.0][turn 107] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_4", "qualifies": true}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 107, "world_seed": 12345}
[v0.11.0][turn 107] action=reward_applicator:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"applied": {"cargo": null, "context": "game_engine", "credits": 1176, "quantity": 0}, "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_4", "reward_profile_id": "bounty_credit"}, "stage": "conditional_rewards", "subsystem": "reward_applicator", "turn": 107, "world_seed": 12345}
[v0.11.0][turn 107] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_5", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 107, "world_seed": 12345}
[v0.11.0][turn 107] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_5", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_5ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [2, 5, 1], "weights_after_notoriety": [2, 5, 1], "weights_after_reputation": [2, 5, 1], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 107, "world_seed": 12345}
[v0.11.0][turn 107] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_5", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 107, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 106, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-001-DST-03", "target_system_id": "SYS-001", "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 106, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 3, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 106, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 5, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_0", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_0", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_0ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_0", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_1", "handler_payload": {"npc_outcome": "ignore"}, "next_handler": "end"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_1", "resolver_outcome": {"outcome": null, "resolver": "none"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_1", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_2", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_2", "resolver_outcome": {"log": {"baseline_weights": {"hail": 5, "pursue": 3}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["hail", "pursue"], "effective_weights": [5, 3], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_2ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [5, 3], "weights_after_notoriety": [5, 3], "weights_after_reputation": [5, 3], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_2", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_4", "handler_payload": {"npc_outcome": "pursue"}, "next_handler": "pursuit_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_4", "resolver_outcome": {"escaped": true, "outcome": "escape_success", "resolver": "pursuit", "threshold": 0.5}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_4", "qualifies": true}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"applied": {"cargo": null, "context": "game_engine", "credits": 1176, "quantity": 0}, "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_4", "reward_profile_id": "bounty_credit"}, "stage": "conditional_rewards", "subsystem": "reward_applicator", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_5", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_5", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": [], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 2, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_5ignore0", "selected_outcome": "hail", "tr_delta": 1, "weights_after_modifiers": [2, 5, 1], "weights_after_notoriety": [2, 5, 1], "weights_after_reputation": [2, 5, 1], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-03:106:auto_route_enc_5", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 107, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 1176, "destination_id": "SYS-001-DST-03", "location_id": "SYS-001-DST-03", "system_id": "SYS-001"}, "turn_after": 107, "turn_before": 106, "version": "0.11.0"}
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
Select destination index: 1
[v0.11.0][turn 107] action=engine:start change={"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 107, "world_seed": 12345}
[v0.11.0][turn 107] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-001-DST-01", "target_system_id": "SYS-001", "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 107, "world_seed": 12345}
[v0.11.0][turn 107] action=travel_resolution:travel change={"command_type": "travel_to_destination", "detail": {"current_fuel": 3, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 107, "world_seed": 12345}
[time_engine] action=time_advance_requested change=start_turn=107 days=1 reason=travel:TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route
[time_engine] action=galaxy_tick change=day=108
[time_engine] action=system_tick change=day=108
[time_engine] action=planet_station_tick change=day=108
[time_engine] action=location_tick change=day=108
[time_engine] action=npc_tick change=day=108
[time_engine] action=end_of_day_log change=day=108
Spawn gate cooldown check: system_id=SYS-001 current_day=108 cooldown_until=109 skipped=true reason=cooldown_active
Situation expired: civil_unrest system=SYS-001
[time_engine] action=time_advance_day_completed change=turn=108 hard_stop=None
[v0.11.0][turn 108] action=time_engine:time_advance change={"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 108, "world_seed": 12345}
[v0.11.0][turn 108] action=law_enforcement:law_checkpoint change={"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 108, "world_seed": 12345}
[v0.11.0][turn 108] action=encounter_generator:encounter_gen change={"command_type": "travel_to_destination", "detail": {"encounter_count": 2, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 108, "world_seed": 12345}
[v0.11.0][turn 108] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route_enc_3", "handler_payload": {"npc_outcome": "pursue"}, "next_handler": "pursuit_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 108, "world_seed": 12345}
[v0.11.0][turn 108] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route_enc_3", "resolver_outcome": {"escaped": true, "outcome": "escape_success", "resolver": "pursuit", "threshold": 0.5}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 108, "world_seed": 12345}
[v0.11.0][turn 108] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route_enc_3", "qualifies": true}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 108, "world_seed": 12345}
[v0.11.0][turn 108] action=reward_applicator:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"applied": {"cargo": null, "context": "game_engine", "credits": 1830, "quantity": 0}, "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route_enc_3", "reward_profile_id": "bounty_credit"}, "stage": "conditional_rewards", "subsystem": "reward_applicator", "turn": 108, "world_seed": 12345}
[v0.11.0][turn 108] action=interaction_layer:interaction_dispatch change={"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route_enc_4", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 108, "world_seed": 12345}
[v0.11.0][turn 108] action=resolver_router:resolver change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route_enc_4", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": ["attack_plus_one_high_tr_delta"], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route_enc_4ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [2, 5, 2], "weights_after_notoriety": [2, 5, 2], "weights_after_reputation": [2, 5, 2], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 108, "world_seed": 12345}
[v0.11.0][turn 108] action=reward_gate:conditional_rewards change={"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route_enc_4", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 108, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "travel_to_destination", "error": null, "events": [{"command_type": "travel_to_destination", "detail": {"command_type": "travel_to_destination"}, "stage": "start", "subsystem": "engine", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"distance_ly": 0.0, "distance_ly_ceiled": 0, "inter_system": false, "target_destination_id": "SYS-001-DST-01", "target_system_id": "SYS-001", "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"current_fuel": 3, "fuel_capacity": 55, "fuel_cost": 0, "reason": "ok", "success": true, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route"}, "stage": "travel", "subsystem": "travel_resolution", "turn": 107, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"days_completed": 1, "days_requested": 1, "hard_stop_reason": null, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route"}, "stage": "time_advance", "subsystem": "time_engine", "turn": 108, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"skipped": true, "trigger_type": "BORDER"}, "stage": "law_checkpoint", "subsystem": "law_enforcement", "turn": 108, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_count": 2, "travel_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route"}, "stage": "encounter_gen", "subsystem": "encounter_generator", "turn": 108, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route_enc_3", "handler_payload": {"npc_outcome": "pursue"}, "next_handler": "pursuit_stub"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 108, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route_enc_3", "resolver_outcome": {"escaped": true, "outcome": "escape_success", "resolver": "pursuit", "threshold": 0.5}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 108, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route_enc_3", "qualifies": true}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 108, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"applied": {"cargo": null, "context": "game_engine", "credits": 1830, "quantity": 0}, "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route_enc_3", "reward_profile_id": "bounty_credit"}, "stage": "conditional_rewards", "subsystem": "reward_applicator", "turn": 108, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"action_id": "ignore", "encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route_enc_4", "handler_payload": {"npc_outcome": "hail"}, "next_handler": "reaction"}, "stage": "interaction_dispatch", "subsystem": "interaction_layer", "turn": 108, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route_enc_4", "resolver_outcome": {"log": {"baseline_weights": {"attack": 1, "hail": 5, "ignore": 2}, "block_used": "on_ignore", "derived_player_tr": 1, "effective_outcomes": ["ignore", "hail", "attack"], "effective_weights": [2, 5, 1], "ignore_escalation_applied": false, "law_score": null, "modifiers_applied": ["attack_plus_one_high_tr_delta"], "notoriety_band": 1, "notoriety_score": 0, "npc_tr": 3, "outlaw_score": null, "player_action": "ignore", "player_tr": 1, "reputation_band": 3, "reputation_score": 50, "seed": "12345TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route_enc_4ignore0", "selected_outcome": "hail", "tr_delta": 2, "weights_after_modifiers": [2, 5, 2], "weights_after_notoriety": [2, 5, 2], "weights_after_reputation": [2, 5, 2], "zero_after_modifiers": false}, "outcome": "hail", "resolver": "reaction"}}, "stage": "resolver", "subsystem": "resolver_router", "turn": 108, "world_seed": 12345}, {"command_type": "travel_to_destination", "detail": {"encounter_id": "TRAVEL-SYS-001:SYS-001:SYS-001-DST-01:107:auto_route_enc_4", "qualifies": false}, "stage": "conditional_rewards", "subsystem": "reward_gate", "turn": 108, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 2886, "destination_id": "SYS-001-DST-01", "location_id": "SYS-001-DST-01", "system_id": "SYS-001"}, "turn_after": 108, "turn_before": 107, "version": "0.11.0"}
DESTINATION: Ion 1 (SYS-001)
1) Player / Ship Info
2) System Info
3) Travel
4) Destination Actions
5) Locations
6) Quit
Select: 6
[v0.11.0][turn 108] action=engine:start change={"command_type": "quit", "detail": {"command_type": "quit"}, "stage": "start", "subsystem": "engine", "turn": 108, "world_seed": 12345}
[v0.11.0][turn 108] action=engine:command change={"command_type": "quit", "detail": {"quit": true}, "stage": "command", "subsystem": "engine", "turn": 108, "world_seed": 12345}
{"active_encounter_count": 0, "command_type": "quit", "error": null, "events": [{"command_type": "quit", "detail": {"command_type": "quit"}, "stage": "start", "subsystem": "engine", "turn": 108, "world_seed": 12345}, {"command_type": "quit", "detail": {"quit": true}, "stage": "command", "subsystem": "engine", "turn": 108, "world_seed": 12345}], "hard_stop": false, "hard_stop_reason": null, "ok": true, "player": {"arrest_state": "free", "credits": 2886, "destination_id": "SYS-001-DST-01", "location_id": "SYS-001-DST-01", "system_id": "SYS-001"}, "turn_after": 108, "turn_before": 108, "version": "0.11.0"}
PS D:\GitHub\EmojiSpace>