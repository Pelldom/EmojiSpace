from typing import Iterable, List

from datanet_entry import DataNetEntry


def assemble_datanet_feed(
    *,
    entries: Iterable[DataNetEntry],
    context_id: str,
    scope: str,
    logger=None,
    turn: int = 0,
) -> List[DataNetEntry]:
    scoped = [entry for entry in entries if entry.scope == scope and context_id in entry.related_ids]
    filtered = [entry for entry in scoped if _passes_censorship(entry)]
    ordered = sorted(filtered, key=lambda entry: entry.datanet_id)
    red_herring_count = len([entry for entry in ordered if entry.is_red_herring])
    _log_feed(logger, turn, context_id, scope, len(scoped), len(ordered), red_herring_count)
    return ordered


def _passes_censorship(entry: DataNetEntry) -> bool:
    if entry.censorship_level == "none":
        return True
    if entry.censorship_level == "soft":
        return entry.truth_band in {"accurate", "vague"}
    if entry.censorship_level == "heavy":
        return entry.truth_band == "accurate"
    return True


def _log_feed(
    logger,
    turn: int,
    context_id: str,
    scope: str,
    scoped_count: int,
    returned_count: int,
    red_herring_count: int,
) -> None:
    if logger is None:
        return
    logger.log(
        turn=turn,
        action="datanet_feed",
        state_change=(
            f"context_id={context_id} scope={scope} "
            f"entries_scoped={scoped_count} entries_returned={returned_count} "
            f"red_herring={red_herring_count}"
        ),
    )
