from typing import Any

from photography.models import Photo
from photography.exceptions import PhotoNotFound


class PhotoRepository:
    def create(self, registry_id: int, reference: str, reference_type: str, **kwargs: Any) -> Photo:
        return Photo.objects.create(
            registry_id=registry_id,
            reference=reference,
            reference_type=reference_type,
            **kwargs
        )

    def get_by_id(self, photo_id: int) -> Photo:
        try:
            return Photo.objects.get(id=photo_id)
        except Photo.DoesNotExist:
            raise PhotoNotFound(f"Photo {photo_id} not found")

    def update(self, photo_id: int, **kwargs: Any) -> Photo:
        try:
            photo = Photo.objects.get(id=photo_id)
        except Photo.DoesNotExist:
            raise PhotoNotFound(f"Photo {photo_id} not found")

        for field, value in kwargs.items():
            setattr(photo, field, value)
        photo.save()
        return photo

    def get_registry_id(self, photo_id: int) -> int:
        try:
            return Photo.objects.values_list('registry_id', flat=True).get(id=photo_id)
        except Photo.DoesNotExist:
            raise PhotoNotFound(f"Photo {photo_id} not found")
