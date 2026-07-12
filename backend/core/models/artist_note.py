from django.db import models


class ArtistNote(models.Model):
    artist = models.ForeignKey("core.Artist", on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'artist_note'
