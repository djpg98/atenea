from django.db import models


class Collection(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=500, blank=True, null=True)
    featured = models.BooleanField(default=False)

    class Meta:
        db_table = 'collection'

    def __str__(self) -> str:
        return self.name
