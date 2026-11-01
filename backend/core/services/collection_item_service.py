from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.db import transaction

from core.registry_resolvers import resolve_registry_ids
from core.repositories.collection_item_repository import CollectionItemRepository
from core.services.collection_service import CollectionService
from core.services.resource_registry_service import ResourceRegistryService
from core.utils.collection_metadata_manager import CollectionMetadataManager

if TYPE_CHECKING:
    from core.models import CollectionItem


class CollectionItemService:
    def __init__(self) -> None:
        self._repository = CollectionItemRepository()
        self._collection_service = CollectionService()
        self._registry_service = ResourceRegistryService()

    def add_item(self, collection_id: int, registry_id: int, order: int | None = None) -> CollectionItem:
        collection = self._collection_service.get_by_id(collection_id=collection_id)
        registry = self._registry_service.get_by_id(registry_id=registry_id)

        if order is None:
            order = self._repository.get_next_order(collection_id=collection_id)

        with transaction.atomic():
            item = self._repository.create(collection_id=collection_id, registry_id=registry_id, order=order)

            manager = CollectionMetadataManager(collection.metadata)
            updated_metadata = manager.increment(registry.resource_type.area)
            self._collection_service.update(collection_id=collection_id, metadata=updated_metadata)

        return item

    def list_by_collection(self, collection_id: int) -> list[CollectionItem]:
        self._collection_service.get_by_id(collection_id=collection_id)
        items = list(self._repository.list_by_collection(collection_id=collection_id))

        ids_by_area: dict[str, list[int]] = {}
        for item in items:
            area = item.registry.resource_type.area
            ids_by_area.setdefault(area, []).append(item.registry_id)

        resolved: dict[int, dict] = {}
        for area, registry_ids in ids_by_area.items():
            resolved.update(resolve_registry_ids(area=area, registry_ids=registry_ids))

        for item in items:
            item.resource = resolved.get(item.registry_id)

        return items

    def update(self, collection_id: int, item_id: int, **kwargs: Any) -> CollectionItem:
        return self._repository.update(collection_id=collection_id, item_id=item_id, **kwargs)

    def delete(self, collection_id: int, item_id: int) -> None:
        item = self._repository.get_by_id(collection_id=collection_id, item_id=item_id)
        registry = self._registry_service.get_by_id(registry_id=item.registry_id)
        collection = self._collection_service.get_by_id(collection_id=collection_id)

        with transaction.atomic():
            self._repository.delete(collection_id=collection_id, item_id=item_id)

            manager = CollectionMetadataManager(collection.metadata)
            updated_metadata = manager.decrement(registry.resource_type.area)
            self._collection_service.update(collection_id=collection_id, metadata=updated_metadata)
