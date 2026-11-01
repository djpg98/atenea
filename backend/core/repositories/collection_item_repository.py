from typing import Any

from django.db import IntegrityError, transaction
from django.db.models import Count, F, QuerySet

from core.models import CollectionItem
from core.exceptions import CollectionItemNotFound, CollectionItemAlreadyExists


class CollectionItemRepository:
    def create(self, collection_id: int, registry_id: int, order: int) -> CollectionItem:
        try:
            with transaction.atomic():
                return CollectionItem.objects.create(
                    collection_id=collection_id,
                    registry_id=registry_id,
                    order=order,
                )
        except IntegrityError:
            raise CollectionItemAlreadyExists(
                f"Registry {registry_id} is already in collection {collection_id}"
            )

    def get_by_id(self, collection_id: int, item_id: int) -> CollectionItem:
        try:
            return CollectionItem.objects.get(id=item_id, collection_id=collection_id)
        except CollectionItem.DoesNotExist:
            raise CollectionItemNotFound(f"CollectionItem {item_id} not found in collection {collection_id}")

    def list_by_collection(self, collection_id: int) -> QuerySet[CollectionItem]:
        return CollectionItem.objects.filter(
            collection_id=collection_id
        ).select_related('registry__resource_type').order_by('order')

    def get_next_order(self, collection_id: int) -> int:
        last_item = CollectionItem.objects.filter(collection_id=collection_id).order_by('-order').first()
        return (last_item.order + 1) if last_item else 0

    def update(self, collection_id: int, item_id: int, **kwargs: Any) -> CollectionItem:
        item = self.get_by_id(collection_id=collection_id, item_id=item_id)
        for field, value in kwargs.items():
            setattr(item, field, value)
        item.save()
        return item

    def delete(self, collection_id: int, item_id: int) -> None:
        CollectionItem.objects.filter(id=item_id, collection_id=collection_id).delete()

    def count_by_collection_and_area(self) -> list[dict[str, Any]]:
        return list(
            CollectionItem.objects
            .values('collection_id', area=F('registry__resource_type__area'))
            .annotate(count=Count('id'))
        )
