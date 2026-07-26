from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.repositories.resource_type_repository import ResourceTypeRepository

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from core.models import ResourceType


class ResourceTypeService:
    def __init__(self) -> None:
        self._repository = ResourceTypeRepository()

    def create(self, name: str, area: str) -> ResourceType:
        return self._repository.create(name=name, area=area)

    def get_by_id(self, resource_type_id: int) -> ResourceType:
        return self._repository.get_by_id(resource_type_id=resource_type_id)

    def list_all(self) -> QuerySet[ResourceType]:
        return self._repository.list_all()

    def update(self, resource_type_id: int, **kwargs: Any) -> ResourceType:
        return self._repository.update(resource_type_id=resource_type_id, **kwargs)

    def delete(self, resource_type_id: int) -> None:
        self._repository.delete(resource_type_id=resource_type_id)
