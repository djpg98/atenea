from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.services.artist_service import ArtistService
from core.serializers.artist_serializer import ArtistSerializer
from core.exceptions import ArtistNotFound


class ArtistListCreateView(APIView):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._service = ArtistService()

    def get(self, request: Request) -> Response:
        artists = self._service.list_all()
        return Response(ArtistSerializer(artists, many=True).data)

    @extend_schema(request=ArtistSerializer)
    def post(self, request: Request) -> Response:
        serializer = ArtistSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        artist = self._service.create(**serializer.validated_data)
        return Response(ArtistSerializer(artist).data, status=status.HTTP_201_CREATED)


class ArtistDetailView(APIView):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._service = ArtistService()

    def get(self, request: Request, artist_id: int) -> Response:
        try:
            artist = self._service.get_by_id(artist_id=artist_id)
        except ArtistNotFound:
            return Response({'error': 'Artist not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(ArtistSerializer(artist).data)

    @extend_schema(request=ArtistSerializer)
    def patch(self, request: Request, artist_id: int) -> Response:
        serializer = ArtistSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            artist = self._service.update(artist_id=artist_id, **serializer.validated_data)
        except ArtistNotFound:
            return Response({'error': 'Artist not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(ArtistSerializer(artist).data)

    def delete(self, request: Request, artist_id: int) -> Response:
        self._service.delete(artist_id=artist_id)
        return Response(status=status.HTTP_200_OK)
