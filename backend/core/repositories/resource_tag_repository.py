from core.models import ResourceTag


class ResourceTagRepository:
    def bulk_create(self, registry_id: int, tag_ids: list[int]) -> list[ResourceTag]:
        links = [ResourceTag(registry_id=registry_id, tag_id=tag_id) for tag_id in tag_ids]
        return ResourceTag.objects.bulk_create(links)

    def bulk_delete(self, registry_id: int, tag_ids: list[int]) -> None:
        ResourceTag.objects.filter(registry_id=registry_id, tag_id__in=tag_ids).delete()

    def list_tag_ids_by_registry(self, registry_id: int) -> list[int]:
        return list(ResourceTag.objects.filter(registry_id=registry_id).values_list('tag_id', flat=True))
