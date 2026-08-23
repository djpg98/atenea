from __future__ import annotations


def reconcile_artist_ids(current_artist_ids: list[int], target_artist_ids: list[int]) -> tuple[set[int], set[int]]:
    current = set(current_artist_ids)
    target = set(target_artist_ids)
    to_add = target - current
    to_remove = current - target
    return to_add, to_remove
