from rest_framework import serializers

from photography.models import Photo


class PhotoCreateSerializer(serializers.ModelSerializer):
    resource_type_id = serializers.IntegerField()

    class Meta:
        model = Photo
        fields = ['resource_type_id', 'reference', 'reference_type', 'title', 'year', 'iso', 'lens', 'camera']


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'registry_id', 'reference', 'reference_type', 'title', 'year', 'iso', 'lens', 'camera']
