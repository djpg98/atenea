from __future__ import annotations

from core.repositories.resource_tag_repository import ResourceTagRepository
from core.services.tag_service import TagService
from core.utils.reconciliation import reconcile_ids


class ResourceTagService:
    def __init__(self) -> None:
        self._repository = ResourceTagRepository()
        self._tag_service = TagService()

    def add_tags(self, registry_id: int, tag_ids: list[int]) -> None:
        unique_tag_ids = list(dict.fromkeys(tag_ids))
        for tag_id in unique_tag_ids:
            self._tag_service.get_by_id(tag_id=tag_id)
        self._repository.bulk_create(registry_id=registry_id, tag_ids=unique_tag_ids)

    def reconcile_tags(self, registry_id: int, tag_ids: list[int]) -> None:
        current_tag_ids = self._repository.list_tag_ids_by_registry(registry_id=registry_id)
        to_add, to_remove = reconcile_ids(current_tag_ids, tag_ids)

        for tag_id in to_add:
            self._tag_service.get_by_id(tag_id=tag_id)

        if to_add:
            self._repository.bulk_create(registry_id=registry_id, tag_ids=list(to_add))
        if to_remove:
            self._repository.bulk_delete(registry_id=registry_id, tag_ids=list(to_remove))

    def list_tag_ids(self, registry_id: int) -> list[int]:
        return self._repository.list_tag_ids_by_registry(registry_id=registry_id)
