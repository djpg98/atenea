from typing import Any

from django.db.models import QuerySet

from core.models import ResourceType
from core.exceptions import ResourceTypeNotFound


class ResourceTypeRepository:
    def create(self, name: str, area: str) -> ResourceType:
        return ResourceType.objects.create(name=name, area=area)

    def get_by_id(self, resource_type_id: int) -> ResourceType:
        try:
            return ResourceType.objects.get(id=resource_type_id)
        except ResourceType.DoesNotExist:
            raise ResourceTypeNotFound(f"ResourceType {resource_type_id} not found")

    def list_all(self) -> QuerySet[ResourceType]:
        return ResourceType.objects.all()

    def update(self, resource_type_id: int, **kwargs: Any) -> ResourceType:
        try:
            resource_type = ResourceType.objects.get(id=resource_type_id)
        except ResourceType.DoesNotExist:
            raise ResourceTypeNotFound(f"ResourceType {resource_type_id} not found")

        for field, value in kwargs.items():
            setattr(resource_type, field, value)
        resource_type.save()
        return resource_type

    def delete(self, resource_type_id: int) -> None:
        ResourceType.objects.filter(id=resource_type_id).delete()
