from typing import Any

from rest_framework import serializers

from core.models import CollectionItem


class CollectionItemCreateSerializer(serializers.Serializer):
    registry_id = serializers.IntegerField()
    order = serializers.IntegerField(required=False)


class CollectionItemUpdateSerializer(serializers.Serializer):
    order = serializers.IntegerField()


class CollectionItemSerializer(serializers.ModelSerializer):
    resource_type_area = serializers.SerializerMethodField()
    resource = serializers.SerializerMethodField()

    class Meta:
        model = CollectionItem
        fields = ['id', 'collection_id', 'registry_id', 'order', 'resource_type_area', 'resource']

    def get_resource_type_area(self, obj: CollectionItem) -> str:
        return obj.registry.resource_type.area

    def get_resource(self, obj: CollectionItem) -> dict[str, Any] | None:
        return getattr(obj, 'resource', None)
