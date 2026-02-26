from pathlib import Path
from typing import List

from data_catalog import load_data_catalog
from government_registry import GovernmentRegistry
from datanet_entry import DataNetEntry
from datanet_feed import assemble_datanet_feed
from mission_factory import create_mission
from npc_placement import resolve_npcs_for_location
from npc_registry import NPCRegistry
from world_generator import WorldGenerator


def _prompt_seed() -> int:
    raw = input("Seed (blank for default 12345): ").strip()
    if not raw:
        return 12345
    return int(raw)


def _print_system_summary(system, government_name: str) -> None:
    print(
        f"[System] {system.system_id} {system.name} | pop={system.population} "
        f"| gov={government_name} ({system.government_id}) | destinations={len(system.destinations)}"
    )


def _print_destination_summary(destination, npc_registry: NPCRegistry, system) -> None:
    print(
        f"[Destination] {destination.destination_id} | type={destination.destination_type} "
        f"| pop={destination.population} | primary={destination.primary_economy_id} "
        f"| secondary={destination.secondary_economy_ids}"
    )
    if destination.locations:
        location_types = [location.location_type for location in destination.locations]
        print(f"  Locations: {', '.join(location_types)}")
    else:
        print("  Locations: none")
    if destination.market is not None:
        _print_market_summary(destination.market)
    else:
        print("  Market: none")
    _print_destination_npcs(destination, npc_registry, system.system_id)
    _print_destination_missions(destination)
    _print_datanet_feed_for_destination(system, destination)


def _print_market_summary(market) -> None:
    category_count = len(market.categories)
    produced_total = sum(len(category.produced) for category in market.categories.values())
    consumed_total = sum(len(category.consumed) for category in market.categories.values())
    neutral_total = sum(len(category.neutral) for category in market.categories.values())
    print(
        f"  Market: categories={category_count} "
        f"produced={produced_total} consumed={consumed_total} neutral={neutral_total}"
    )


def _print_market_details(market) -> None:
    if not market.categories:
        print("  Market details: no categories")
        return
    print("  Market details:")
    for category_id, category in market.categories.items():
        produced = [good.sku for good in category.produced]
        consumed = [good.sku for good in category.consumed]
        neutral = [good.sku for good in category.neutral]
        print(f"    Category {category_id}:")
        print(f"      produced={produced}")
        print(f"      consumed={consumed}")
        print(f"      neutral={neutral}")


def _print_destination_npcs(destination, npc_registry: NPCRegistry, system_id: str) -> None:
    npcs: List[str] = []
    for location in destination.locations:
        if location.location_type not in {"bar", "administration"}:
            continue
        resolved = resolve_npcs_for_location(
            location_id=destination.destination_id + f":{location.location_type}",
            location_type=location.location_type,
            system_id=system_id,
            registry=npc_registry,
        )
        npcs.extend([npc.display_name or npc.npc_id for npc in resolved])
    if npcs:
        print(f"  NPCs: {npcs}")
    else:
        print("  NPCs: none")


def _print_destination_missions(destination) -> None:
    mission = create_mission(
        source_type="bar",
        source_id=destination.destination_id,
        system_id=destination.system_id,
        destination_id=destination.destination_id,
        mission_type="delivery",
        mission_tier=1,
        payout_policy="auto",
        claim_scope="none",
    )
    print(f"  Missions: {[mission.mission_id]}")


def _build_datanet_entries(system, destinations) -> List[DataNetEntry]:
    entries: List[DataNetEntry] = []
    for destination in destinations:
        entries.append(
            DataNetEntry(
                datanet_id=f"DN-{destination.destination_id}",
                datanet_type="news",
                source_type="system",
                scope="destination",
                truth_band="accurate",
                censorship_level="none",
                related_ids=[destination.destination_id],
                prose_text="A routine update moves through the channel.",
                persistence="ephemeral",
                is_red_herring=False,
            )
        )
    entries.append(
        DataNetEntry(
            datanet_id=f"DN-{system.system_id}-R",
            datanet_type="rumor",
            source_type="anonymous",
            scope="system",
            truth_band="vague",
            censorship_level="soft",
            related_ids=[system.system_id],
            prose_text="A drifting rumor circles without focus.",
            persistence="ephemeral",
            is_red_herring=True,
        )
    )
    return entries


def _print_datanet_feed_for_destination(system, destination) -> None:
    entries = _build_datanet_entries(system, system.destinations)
    feed = assemble_datanet_feed(
        entries=entries,
        context_id=destination.destination_id,
        scope="destination",
    )
    if not feed:
        print("  DataNet: none")
        return
    print("  DataNet:")
    for entry in feed:
        print(f"    {entry.datanet_type} {entry.datanet_id} red_herring={entry.is_red_herring}")


def _select_index(prompt: str, max_index: int) -> int | None:
    raw = input(prompt).strip()
    if raw.lower() in {"q", "quit", "exit"}:
        return None
    if raw.lower() in {"b", "back"}:
        return -2
    if not raw.isdigit():
        return -1
    idx = int(raw)
    if idx < 1 or idx > max_index:
        return -1
    return idx - 1


def _locations_for_destination(destination) -> List[str]:
    return [location.location_type for location in destination.locations]


def main() -> None:
    try:
        seed = _prompt_seed()
    except ValueError:
        print("Invalid seed.")
        return

    catalog = load_data_catalog()
    government_registry = GovernmentRegistry.from_file(
        Path(__file__).resolve().parents[1] / "data" / "governments.json"
    )

    npc_registry = NPCRegistry()
    generator = WorldGenerator(
        seed=seed,
        system_count=5,
        government_ids=government_registry.government_ids(),
        catalog=catalog,
        logger=None,
    )
    galaxy = generator.generate()

    while True:
        print("")
        print(f"Galaxy seed={seed} systems={len(galaxy.systems)}")
        for idx, system in enumerate(galaxy.systems, start=1):
            government = government_registry.get_government(system.government_id)
            print(f"{idx}) {system.system_id} {system.name} (pop={system.population}, gov={government.name})")
        selection = _select_index("Select system (q to quit): ", len(galaxy.systems))
        if selection is None:
            return
        if selection < 0:
            print("Invalid selection.")
            continue
        system = galaxy.systems[selection]
        government = government_registry.get_government(system.government_id)
        _print_system_summary(system, government.name)

        while True:
            print("")
            for idx, destination in enumerate(system.destinations, start=1):
                print(f"{idx}) {destination.destination_id} ({destination.destination_type})")
            dest_selection = _select_index("Select destination (b to go back, q to quit): ", len(system.destinations))
            if dest_selection is None:
                return
            if dest_selection == -2:
                break
            if dest_selection == -1:
                print("Invalid selection.")
                continue
            destination = system.destinations[dest_selection]
            _print_destination_summary(destination, npc_registry, system)
            location_types = _locations_for_destination(destination)
            if not location_types:
                continue
            while True:
                print("")
                for idx, location_type in enumerate(location_types, start=1):
                    print(f"{idx}) {location_type}")
                loc_selection = _select_index("Select location (b to go back, q to quit): ", len(location_types))
                if loc_selection is None:
                    return
                if loc_selection == -2:
                    break
                if loc_selection == -1:
                    print("Invalid selection.")
                    continue
                location_type = location_types[loc_selection]
                print(f"[Location] {location_type}")
                if location_type in {"bar", "administration"}:
                    npcs = resolve_npcs_for_location(
                        location_id=destination.destination_id + f":{location_type}",
                        location_type=location_type,
                        system_id=system.system_id,
                        registry=npc_registry,
                    )
                    if npcs:
                        names = [npc.display_name or npc.npc_id for npc in npcs]
                        print(f"  NPCs: {names}")
                        mission_ids: List[str] = []
                        for npc in npcs:
                            mission = create_mission(
                                source_type="bar",
                                source_id=npc.npc_id,
                                system_id=system.system_id,
                                destination_id=destination.destination_id,
                                mission_type="delivery",
                                mission_tier=1,
                                payout_policy="auto",
                                claim_scope="none",
                            )
                            mission_ids.append(mission.mission_id)
                        print(f"  NPC Missions: {mission_ids}")
                    else:
                        print("  NPCs: none")
                if location_type == "market":
                    if destination.market is None:
                        print("  Market: none")
                    else:
                        _print_market_summary(destination.market)
                        _print_market_details(destination.market)
                elif location_type == "warehouse":
                    print("  Warehouse: storage only (details not loaded)")
                else:
                    print("  Details: none")


if __name__ == "__main__":
    print("Deprecated harness entry point. Use src/cli_run.py.")
