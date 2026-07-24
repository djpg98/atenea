from core.models import ResourceRegistry
from core.exceptions import ResourceRegistryNotFound


class ResourceRegistryRepository:
    def create(self, resource_type_id: int) -> ResourceRegistry:
        return ResourceRegistry.objects.create(resource_type_id=resource_type_id)

    def get_by_id(self, registry_id: int) -> ResourceRegistry:
        try:
            return ResourceRegistry.objects.get(id=registry_id)
        except ResourceRegistry.DoesNotExist:
            raise ResourceRegistryNotFound(f"ResourceRegistry {registry_id} not found")

    def delete(self, registry_id: int) -> None:
        ResourceRegistry.objects.filter(id=registry_id).delete()
