from django.db import models


class ResourceType(models.Model):
    class Area(models.TextChoices):
        PHOTOGRAPHY = 'photography', 'Photography'
        CINEMA = 'cinema', 'Cinema'
        MUSIC = 'music', 'Music'
        COMPUTER_SCIENCE = 'computer_science', 'Computer Science'
        COMICS = 'comics', 'Comics'
        GENERAL = 'general', 'General'

    name = models.CharField(max_length=100)
    area = models.CharField(max_length=50, choices=Area.choices)

    class Meta:
        db_table = 'resource_type'

    def __str__(self) -> str:
        return f"{self.name} ({self.area})"
