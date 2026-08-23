from photography.models import PhotoArtist


class PhotoArtistRepository:
    def bulk_create(self, photo_id: int, artist_ids: list[int]) -> list[PhotoArtist]:
        links = [PhotoArtist(photo_id=photo_id, artist_id=artist_id) for artist_id in artist_ids]
        return PhotoArtist.objects.bulk_create(links)

    def list_artist_ids_by_photo(self, photo_id: int) -> list[int]:
        return list(PhotoArtist.objects.filter(photo_id=photo_id).values_list('artist_id', flat=True))

    def bulk_delete(self, photo_id: int, artist_ids: list[int]) -> None:
        PhotoArtist.objects.filter(photo_id=photo_id, artist_id__in=artist_ids).delete()
