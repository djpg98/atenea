from typing import Any

from django.db.models import QuerySet

from core.models import Tag
from core.exceptions import TagNotFound


class TagRepository:
    def create(self, name: str) -> Tag:
        return Tag.objects.create(name=name)

    def get_by_id(self, tag_id: int) -> Tag:
        try:
            return Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            raise TagNotFound(f"Tag {tag_id} not found")

    def list_all(self) -> QuerySet[Tag]:
        return Tag.objects.all()

    def update(self, tag_id: int, **kwargs: Any) -> Tag:
        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            raise TagNotFound(f"Tag {tag_id} not found")

        for field, value in kwargs.items():
            setattr(tag, field, value)
        tag.save()
        return tag

    def delete(self, tag_id: int) -> None:
        Tag.objects.filter(id=tag_id).delete()
