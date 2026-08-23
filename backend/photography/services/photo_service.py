from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.db import transaction

from core.services.resource_registry_service import ResourceRegistryService
from core.services.artist_service import ArtistService
from photography.repositories.photo_repository import PhotoRepository
from photography.repositories.photo_artist_repository import PhotoArtistRepository

if TYPE_CHECKING:
    from photography.models import Photo


class PhotoService:
    def __init__(self) -> None:
        self._photo_repository = PhotoRepository()
        self._photo_artist_repository = PhotoArtistRepository()
        self._registry_service = ResourceRegistryService()
        self._artist_service = ArtistService()

    def create(
        self,
        resource_type_id: int,
        reference: str,
        reference_type: str,
        artist_ids: list[int] | None = None,
        **kwargs: Any,
    ) -> Photo:
        with transaction.atomic():
            registry = self._registry_service.create(resource_type_id=resource_type_id)
            photo = self._photo_repository.create(
                registry_id=registry.id,
                reference=reference,
                reference_type=reference_type,
                **kwargs
            )
            if artist_ids:
                unique_artist_ids = list(dict.fromkeys(artist_ids))
                for artist_id in unique_artist_ids:
                    self._artist_service.get_by_id(artist_id=artist_id)
                self._photo_artist_repository.bulk_create(photo_id=photo.id, artist_ids=unique_artist_ids)
            return photo

    def get_by_id(self, photo_id: int) -> Photo:
        return self._photo_repository.get_by_id(photo_id=photo_id)

    def update(self, photo_id: int, **kwargs: Any) -> Photo:
        return self._photo_repository.update(photo_id=photo_id, **kwargs)

    def delete(self, photo_id: int) -> None:
        registry_id = self._photo_repository.get_registry_id(photo_id=photo_id)
        self._registry_service.delete(registry_id=registry_id)
