from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.repositories.collection_item_repository import CollectionItemRepository
from core.services.collection_service import CollectionService
from core.services.resource_registry_service import ResourceRegistryService

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from core.models import CollectionItem


class CollectionItemService:
    def __init__(self) -> None:
        self._repository = CollectionItemRepository()
        self._collection_service = CollectionService()
        self._registry_service = ResourceRegistryService()

    def add_item(self, collection_id: int, registry_id: int, order: int | None = None) -> CollectionItem:
        self._collection_service.get_by_id(collection_id=collection_id)
        self._registry_service.get_by_id(registry_id=registry_id)

        if order is None:
            order = self._repository.get_next_order(collection_id=collection_id)

        return self._repository.create(collection_id=collection_id, registry_id=registry_id, order=order)

    def list_by_collection(self, collection_id: int) -> QuerySet[CollectionItem]:
        self._collection_service.get_by_id(collection_id=collection_id)
        return self._repository.list_by_collection(collection_id=collection_id)

    def update(self, collection_id: int, item_id: int, **kwargs: Any) -> CollectionItem:
        return self._repository.update(collection_id=collection_id, item_id=item_id, **kwargs)

    def delete(self, collection_id: int, item_id: int) -> None:
        self._repository.delete(collection_id=collection_id, item_id=item_id)
