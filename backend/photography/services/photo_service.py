from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.db import transaction

from core.services.resource_registry_service import ResourceRegistryService
from photography.repositories.photo_repository import PhotoRepository

if TYPE_CHECKING:
    from photography.models import Photo


class PhotoService:
    def __init__(self) -> None:
        self._photo_repository = PhotoRepository()
        self._registry_service = ResourceRegistryService()

    def create(self, resource_type_id: int, reference: str, reference_type: str, **kwargs: Any) -> Photo:
        with transaction.atomic():
            registry = self._registry_service.create(resource_type_id=resource_type_id)
            return self._photo_repository.create(
                registry_id=registry.id,
                reference=reference,
                reference_type=reference_type,
                **kwargs
            )

    def get_by_id(self, photo_id: int) -> Photo:
        return self._photo_repository.get_by_id(photo_id=photo_id)

    def update(self, photo_id: int, **kwargs: Any) -> Photo:
        return self._photo_repository.update(photo_id=photo_id, **kwargs)

    def delete(self, photo_id: int) -> None:
        registry_id = self._photo_repository.get_registry_id(photo_id=photo_id)
        self._registry_service.delete(registry_id=registry_id)
