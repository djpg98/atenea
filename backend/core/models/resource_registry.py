from django.db import models


class ResourceRegistry(models.Model):
    resource_type = models.ForeignKey("core.ResourceType", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'resource_registry'

    def __str__(self):
        return f"Resource {self.id} ({self.resource_type})"
