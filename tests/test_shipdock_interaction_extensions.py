import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from interaction_layer import (  # noqa: E402
    destination_actions,
    execute_buy_hull,
    execute_buy_module,
    execute_repair_ship,
    execute_sell_hull,
    execute_sell_module,
)
from player_state import PlayerState  # noqa: E402
from ship_entity import ShipEntity  # noqa: E402


def _shipdock_destination(destination_id: str = "DST-1") -> dict:
    return {"destination_id": destination_id, "locations": [{"location_type": "shipdock"}]}


def test_shipdock_actions_are_destination_gated() -> None:
    shipdock_actions = destination_actions(_shipdock_destination(), base_actions=["ignore"])
    assert "buy_hull" in shipdock_actions
    assert "sell_hull" in shipdock_actions
    assert "buy_module" in shipdock_actions
    assert "sell_module" in shipdock_actions
    assert "repair_ship" in shipdock_actions

    non_shipdock = {"destination_id": "DST-2", "locations": [{"location_type": "market"}]}
    non_shipdock_actions = destination_actions(non_shipdock, base_actions=["ignore"])
    assert "buy_hull" not in non_shipdock_actions


def test_buy_hull_creates_inactive_ship_at_location() -> None:
    destination = _shipdock_destination()
    player = PlayerState(player_id="player", credits=5000, owned_ship_ids=[])
    fleet: dict[str, ShipEntity] = {}
    inventory = {"hulls": [{"hull_id": "civ_t1_midge", "base_price_credits": 1650}], "modules": []}

    result = execute_buy_hull(
        destination=destination,
        player=player,
        fleet_by_id=fleet,
        inventory=inventory,
        hull_id="civ_t1_midge",
        ship_id="SHIP-NEW-1",
    )
    assert result["ok"] is True
    assert player.credits == 3350
    ship = fleet["SHIP-NEW-1"]
    assert ship.model_id == "civ_t1_midge"
    assert ship.location_id == "DST-1"
    assert ship.activity_state == "inactive"
    assert ship.persistent_state["active_flag"] is False
    assert ship.current_fuel == ship.fuel_capacity


def test_sell_active_hull_requires_and_promotes_replacement() -> None:
    destination = _shipdock_destination()
    player = PlayerState(player_id="player", credits=1000, active_ship_id="SHIP-A", owned_ship_ids=["SHIP-A", "SHIP-B"])
    ship_a = ShipEntity(ship_id="SHIP-A", model_id="civ_t1_midge", location_id="DST-1", activity_state="active")
    ship_b = ShipEntity(ship_id="SHIP-B", model_id="civ_t1_gnat", location_id="DST-1", activity_state="inactive")
    ship_a.persistent_state["active_flag"] = True
    ship_b.persistent_state["active_flag"] = False
    fleet = {"SHIP-A": ship_a, "SHIP-B": ship_b}

    result = execute_sell_hull(destination=destination, player=player, fleet_by_id=fleet, ship_id="SHIP-A")
    assert result["ok"] is True
    assert "SHIP-A" not in fleet
    assert player.active_ship_id == "SHIP-B"
    assert fleet["SHIP-B"].activity_state == "active"
    assert player.credits > 1000


def test_buy_module_validates_slot_constraints_and_presence() -> None:
    destination = _shipdock_destination()
    player = PlayerState(player_id="player", credits=10000, owned_ship_ids=["SHIP-1"])
    ship = ShipEntity(ship_id="SHIP-1", model_id="civ_t1_midge", location_id="DST-1")
    ship.persistent_state["module_instances"] = [{"module_id": "weapon_energy_mk1", "secondary_tags": []}]
    ship.persistent_state["degradation_state"] = {"weapon": 0, "defense": 0, "engine": 0}
    fleet = {"SHIP-1": ship}
    inventory = {"hulls": [], "modules": [{"module_id": "weapon_energy_mk1", "base_price_credits": 1800}]}

    fail = execute_buy_module(
        destination=destination,
        player=player,
        fleet_by_id=fleet,
        inventory=inventory,
        ship_id="SHIP-1",
        module_id="weapon_energy_mk1",
    )
    assert fail["ok"] is False
    assert fail["reason"] == "slot_constraints_failed"
    assert len(ship.persistent_state["module_instances"]) == 1

    ship.location_id = "DST-OTHER"
    not_present = execute_buy_module(
        destination=destination,
        player=player,
        fleet_by_id=fleet,
        inventory=inventory,
        ship_id="SHIP-1",
        module_id="weapon_energy_mk1",
    )
    assert not_present["ok"] is False
    assert not_present["reason"] == "ship_not_present"


def test_sell_module_and_repair_ship_apply_contract_math() -> None:
    destination = _shipdock_destination()
    player = PlayerState(player_id="player", credits=0, owned_ship_ids=["SHIP-1"])
    ship = ShipEntity(ship_id="SHIP-1", model_id="civ_t1_midge", location_id="DST-1", fuel_capacity=10, current_fuel=3)
    ship.persistent_state["module_instances"] = [{"module_id": "combat_utility_engine_boost_mk1", "secondary_tags": []}]
    ship.persistent_state["degradation_state"] = {"weapon": 1, "defense": 2, "engine": 0}
    ship.persistent_state["max_hull_integrity"] = 10
    ship.persistent_state["current_hull_integrity"] = 7
    fleet = {"SHIP-1": ship}

    sold = execute_sell_module(
        destination=destination,
        player=player,
        fleet_by_id=fleet,
        ship_id="SHIP-1",
        module_id="combat_utility_engine_boost_mk1",
    )
    assert sold["ok"] is True
    assert sold["final_price"] > 0
    assert ship.current_fuel <= ship.fuel_capacity

    credits_before = player.credits
    repaired = execute_repair_ship(
        destination=destination,
        player=player,
        fleet_by_id=fleet,
        ship_id="SHIP-1",
        system_population=3,
    )
    # hull_damage=3 => 30, subsystem_damage=3 => 75, total=105 at pop3 modifier 1.0
    assert repaired["ok"] is True
    assert repaired["final_cost"] == 105
    assert player.credits == credits_before - 105
    assert ship.persistent_state["current_hull_integrity"] == 10
    assert ship.persistent_state["degradation_state"] == {"weapon": 0, "defense": 0, "engine": 0}


def test_sell_module_secondary_resale_multipliers() -> None:
    destination = _shipdock_destination()
    player = PlayerState(player_id="player", credits=0, owned_ship_ids=["SHIP-1"])
    ship = ShipEntity(ship_id="SHIP-1", model_id="civ_t1_midge", location_id="DST-1")
    ship.persistent_state["degradation_state"] = {"weapon": 0, "defense": 0, "engine": 0}
    fleet = {"SHIP-1": ship}

    ship.persistent_state["module_instances"] = [
        {"module_id": "combat_utility_engine_boost_mk1", "secondary_tags": ["secondary:prototype"]}
    ]
    sold_proto = execute_sell_module(
        destination=destination,
        player=player,
        fleet_by_id=fleet,
        ship_id="SHIP-1",
        module_id="combat_utility_engine_boost_mk1",
    )
    assert sold_proto["ok"] is True
    assert sold_proto["final_price"] == 1050  # 1400 * 0.5 * 1.5

    ship.persistent_state["module_instances"] = [
        {"module_id": "combat_utility_engine_boost_mk1", "secondary_tags": ["secondary:alien"]}
    ]
    sold_alien = execute_sell_module(
        destination=destination,
        player=player,
        fleet_by_id=fleet,
        ship_id="SHIP-1",
        module_id="combat_utility_engine_boost_mk1",
    )
    assert sold_alien["ok"] is True
    assert sold_alien["final_price"] == 1400  # 1400 * 0.5 * 2.0

    ship.persistent_state["module_instances"] = [
        {
            "module_id": "combat_utility_engine_boost_mk1",
            "secondary_tags": ["secondary:prototype", "secondary:alien"],
        }
    ]
    sold_stacked = execute_sell_module(
        destination=destination,
        player=player,
        fleet_by_id=fleet,
        ship_id="SHIP-1",
        module_id="combat_utility_engine_boost_mk1",
    )
    assert sold_stacked["ok"] is True
    assert sold_stacked["final_price"] == 2100  # 1400 * 0.5 * 1.5 * 2.0
