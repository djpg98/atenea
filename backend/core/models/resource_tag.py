from django.db import models


class ResourceTag(models.Model):
    registry = models.ForeignKey("core.ResourceRegistry", on_delete=models.CASCADE)
    tag = models.ForeignKey("core.Tag", on_delete=models.CASCADE)

    class Meta:
        db_table = 'resource_tag'
        unique_together = [('registry', 'tag')]
