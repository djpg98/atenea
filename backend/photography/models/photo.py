from django.db import models


class Photo(models.Model):
    class ReferenceType(models.TextChoices):
        URL = 'url', 'URL'
        FILESYSTEM = 'filesystem', 'Filesystem'

    registry = models.OneToOneField("core.ResourceRegistry", on_delete=models.CASCADE)
    reference = models.CharField(max_length=1000)
    reference_type = models.CharField(max_length=20, choices=ReferenceType.choices)
    title = models.CharField(max_length=255, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    iso = models.IntegerField(blank=True, null=True)
    lens = models.CharField(max_length=255, blank=True, null=True)
    camera = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'photo'

    def __str__(self) -> str:
        return self.title or f"Photo {self.id}"
