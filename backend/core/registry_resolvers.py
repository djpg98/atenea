from __future__ import annotations

from typing import Any, Callable

Resolver = Callable[[list[int]], dict[int, dict[str, Any]]]

_resolvers: dict[str, Resolver] = {}


def register_resolver(area: str, resolver: Resolver) -> None:
    _resolvers[area] = resolver


def resolve_registry_ids(area: str, registry_ids: list[int]) -> dict[int, dict[str, Any]]:
    resolver = _resolvers.get(area)
    if resolver is None:
        return {}
    return resolver(registry_ids)
