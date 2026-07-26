from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.repositories.artist_repository import ArtistRepository

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from core.models import Artist


class ArtistService:
    def __init__(self) -> None:
        self._repository = ArtistRepository()

    def create(self, name: str, **kwargs: Any) -> Artist:
        return self._repository.create(name=name, **kwargs)

    def get_by_id(self, artist_id: int) -> Artist:
        return self._repository.get_by_id(artist_id=artist_id)

    def list_all(self) -> QuerySet[Artist]:
        return self._repository.list_all()

    def update(self, artist_id: int, **kwargs: Any) -> Artist:
        return self._repository.update(artist_id=artist_id, **kwargs)

    def delete(self, artist_id: int) -> None:
        self._repository.delete(artist_id=artist_id)
