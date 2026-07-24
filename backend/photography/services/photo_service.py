from django.db import transaction

from core.services.resource_registry_service import ResourceRegistryService
from photography.repositories.photo_repository import PhotoRepository


class PhotoService:
    def __init__(self):
        self._photo_repository = PhotoRepository()
        self._registry_service = ResourceRegistryService()

    def create(self, resource_type_id, reference, reference_type, **kwargs):
        with transaction.atomic():
            registry = self._registry_service.create(resource_type_id=resource_type_id)
            return self._photo_repository.create(
                registry_id=registry.id,
                reference=reference,
                reference_type=reference_type,
                **kwargs
            )

    def get_by_id(self, photo_id):
        return self._photo_repository.get_by_id(photo_id=photo_id)

    def update(self, photo_id, **kwargs):
        return self._photo_repository.update(photo_id=photo_id, **kwargs)

    def delete(self, photo_id):
        registry_id = self._photo_repository.get_registry_id(photo_id=photo_id)
        self._registry_service.delete(registry_id=registry_id)
