from django.db import models


class CollectionItem(models.Model):
    collection = models.ForeignKey("core.Collection", on_delete=models.CASCADE)
    registry = models.ForeignKey("core.ResourceRegistry", on_delete=models.CASCADE)
    order = models.IntegerField()

    class Meta:
        db_table = 'collection_item'
        unique_together = [('collection', 'registry')]
