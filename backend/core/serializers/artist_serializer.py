from rest_framework import serializers

from core.models import Artist


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['id', 'name', 'nationality', 'birth_date']
