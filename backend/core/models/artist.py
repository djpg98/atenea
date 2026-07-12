from django.db import models


class Artist(models.Model):
    name = models.CharField(max_length=255)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'artist'

    def __str__(self):
        return self.name
