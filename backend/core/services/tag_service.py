from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.repositories.tag_repository import TagRepository

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from core.models import Tag


class TagService:
    def __init__(self) -> None:
        self._repository = TagRepository()

    def create(self, name: str) -> Tag:
        return self._repository.create(name=name)

    def get_by_id(self, tag_id: int) -> Tag:
        return self._repository.get_by_id(tag_id=tag_id)

    def list_all(self) -> QuerySet[Tag]:
        return self._repository.list_all()

    def update(self, tag_id: int, **kwargs: Any) -> Tag:
        return self._repository.update(tag_id=tag_id, **kwargs)

    def delete(self, tag_id: int) -> None:
        self._repository.delete(tag_id=tag_id)
