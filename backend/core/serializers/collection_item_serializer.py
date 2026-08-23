from rest_framework import serializers

from core.models import CollectionItem


class CollectionItemCreateSerializer(serializers.Serializer):
    registry_id = serializers.IntegerField()
    order = serializers.IntegerField(required=False)


class CollectionItemUpdateSerializer(serializers.Serializer):
    order = serializers.IntegerField()


class CollectionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionItem
        fields = ['id', 'collection_id', 'registry_id', 'order']
