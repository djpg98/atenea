from rest_framework import serializers

from core.models import ResourceType


class ResourceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceType
        fields = ['id', 'name', 'area']
