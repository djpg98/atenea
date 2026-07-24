from __future__ import annotations

from typing import TYPE_CHECKING

from core.repositories.resource_registry_repository import ResourceRegistryRepository

if TYPE_CHECKING:
    from core.models import ResourceRegistry


class ResourceRegistryService:
    def __init__(self) -> None:
        self._repository = ResourceRegistryRepository()

    def create(self, resource_type_id: int) -> ResourceRegistry:
        return self._repository.create(resource_type_id=resource_type_id)

    def get_by_id(self, registry_id: int) -> ResourceRegistry:
        return self._repository.get_by_id(registry_id=registry_id)

    def delete(self, registry_id: int) -> None:
        self._repository.delete(registry_id=registry_id)
