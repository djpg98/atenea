from typing import Any

from django.db.models import QuerySet

from core.models import Artist
from core.exceptions import ArtistNotFound


class ArtistRepository:
    def create(self, name: str, **kwargs: Any) -> Artist:
        return Artist.objects.create(name=name, **kwargs)

    def get_by_id(self, artist_id: int) -> Artist:
        try:
            return Artist.objects.get(id=artist_id)
        except Artist.DoesNotExist:
            raise ArtistNotFound(f"Artist {artist_id} not found")

    def list_all(self) -> QuerySet[Artist]:
        return Artist.objects.all()

    def update(self, artist_id: int, **kwargs: Any) -> Artist:
        try:
            artist = Artist.objects.get(id=artist_id)
        except Artist.DoesNotExist:
            raise ArtistNotFound(f"Artist {artist_id} not found")

        for field, value in kwargs.items():
            setattr(artist, field, value)
        artist.save()
        return artist

    def delete(self, artist_id: int) -> None:
        Artist.objects.filter(id=artist_id).delete()
