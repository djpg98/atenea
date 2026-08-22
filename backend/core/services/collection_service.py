from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.repositories.collection_repository import CollectionRepository

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from core.models import Collection


class CollectionService:
    def __init__(self) -> None:
        self._repository = CollectionRepository()

    def create(self, name: str, **kwargs: Any) -> Collection:
        return self._repository.create(name=name, **kwargs)

    def get_by_id(self, collection_id: int) -> Collection:
        return self._repository.get_by_id(collection_id=collection_id)

    def list_all(self) -> QuerySet[Collection]:
        return self._repository.list_all()

    def update(self, collection_id: int, **kwargs: Any) -> Collection:
        return self._repository.update(collection_id=collection_id, **kwargs)

    def delete(self, collection_id: int) -> None:
        self._repository.delete(collection_id=collection_id)
