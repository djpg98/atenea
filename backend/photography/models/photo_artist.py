from django.db import models


class PhotoArtist(models.Model):
    photo = models.ForeignKey("photography.Photo", on_delete=models.CASCADE)
    artist = models.ForeignKey("core.Artist", on_delete=models.CASCADE)

    class Meta:
        db_table = 'photo_artist'
        unique_together = [('photo', 'artist')]
