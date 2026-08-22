from typing import Any

from django.db.models import QuerySet

from core.models import Collection
from core.exceptions import CollectionNotFound


class CollectionRepository:
    def create(self, name: str, **kwargs: Any) -> Collection:
        return Collection.objects.create(name=name, **kwargs)

    def get_by_id(self, collection_id: int) -> Collection:
        try:
            return Collection.objects.get(id=collection_id)
        except Collection.DoesNotExist:
            raise CollectionNotFound(f"Collection {collection_id} not found")

    def list_all(self) -> QuerySet[Collection]:
        return Collection.objects.all()

    def update(self, collection_id: int, **kwargs: Any) -> Collection:
        try:
            collection = Collection.objects.get(id=collection_id)
        except Collection.DoesNotExist:
            raise CollectionNotFound(f"Collection {collection_id} not found")

        for field, value in kwargs.items():
            setattr(collection, field, value)
        collection.save()
        return collection

    def delete(self, collection_id: int) -> None:
        Collection.objects.filter(id=collection_id).delete()
