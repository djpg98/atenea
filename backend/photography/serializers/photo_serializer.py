from rest_framework import serializers

from photography.models import Photo, PhotoArtist
from core.models import ResourceTag


class PhotoCreateSerializer(serializers.ModelSerializer):
    resource_type_id = serializers.IntegerField()
    artist_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    tag_ids = serializers.ListField(child=serializers.IntegerField(), required=False)

    class Meta:
        model = Photo
        fields = [
            'resource_type_id', 'artist_ids', 'tag_ids', 'reference', 'reference_type', 'title', 'year', 'iso',
            'lens', 'camera'
        ]


class PhotoUpdateSerializer(serializers.ModelSerializer):
    artist_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    tag_ids = serializers.ListField(child=serializers.IntegerField(), required=False)

    class Meta:
        model = Photo
        fields = ['artist_ids', 'tag_ids', 'reference', 'reference_type', 'title', 'year', 'iso', 'lens', 'camera']


class PhotoSerializer(serializers.ModelSerializer):
    artist_ids = serializers.SerializerMethodField()
    tag_ids = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = [
            'id', 'registry_id', 'reference', 'reference_type', 'title', 'year', 'iso', 'lens', 'camera',
            'artist_ids', 'tag_ids'
        ]

    def get_artist_ids(self, obj: Photo) -> list[int]:
        return list(PhotoArtist.objects.filter(photo_id=obj.id).values_list('artist_id', flat=True))

    def get_tag_ids(self, obj: Photo) -> list[int]:
        return list(ResourceTag.objects.filter(registry_id=obj.registry_id).values_list('tag_id', flat=True))
