from django.db import models


class ResourceNote(models.Model):
    registry = models.ForeignKey("core.ResourceRegistry", on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'resource_note'
