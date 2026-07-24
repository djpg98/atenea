from core.models import ResourceRegistry
from core.exceptions import ResourceRegistryNotFound


class ResourceRegistryRepository:
    def create(self, resource_type_id):
        return ResourceRegistry.objects.create(resource_type_id=resource_type_id)

    def get_by_id(self, registry_id):
        try:
            return ResourceRegistry.objects.get(id=registry_id)
        except ResourceRegistry.DoesNotExist:
            raise ResourceRegistryNotFound(f"ResourceRegistry {registry_id} not found")

    def delete(self, registry_id):
        ResourceRegistry.objects.filter(id=registry_id).delete()
