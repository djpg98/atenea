from __future__ import annotations


def reconcile_ids(current_ids: list[int], target_ids: list[int]) -> tuple[set[int], set[int]]:
    current = set(current_ids)
    target = set(target_ids)
    to_add = target - current
    to_remove = current - target
    return to_add, to_remove
