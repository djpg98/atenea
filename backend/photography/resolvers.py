from __future__ import annotations

from typing import Any

from photography.services.photo_service import PhotoService
from photography.serializers.photo_serializer import PhotoSerializer


def resolve_photos_by_registry_ids(registry_ids: list[int]) -> dict[int, dict[str, Any]]:
    photos = PhotoService().list_by_registry_ids(registry_ids=registry_ids)
    return {photo.registry_id: PhotoSerializer(photo).data for photo in photos}
