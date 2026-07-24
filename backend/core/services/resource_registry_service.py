from core.repositories.resource_registry_repository import ResourceRegistryRepository


class ResourceRegistryService:
    def __init__(self):
        self._repository = ResourceRegistryRepository()

    def create(self, resource_type_id):
        return self._repository.create(resource_type_id=resource_type_id)

    def get_by_id(self, registry_id):
        return self._repository.get_by_id(registry_id=registry_id)

    def delete(self, registry_id):
        self._repository.delete(registry_id=registry_id)
