from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from photography.services.photo_service import PhotoService
from photography.serializers.photo_serializer import PhotoCreateSerializer, PhotoUpdateSerializer, PhotoSerializer
from photography.exceptions import PhotoNotFound
from core.exceptions import ArtistNotFound, TagNotFound


class PhotoListCreateView(APIView):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._service = PhotoService()

    def get(self, request: Request) -> Response:
        photos = self._service.list_all()
        return Response(PhotoSerializer(photos, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = PhotoCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        resource_type_id = data.pop('resource_type_id')
        reference = data.pop('reference')
        reference_type = data.pop('reference_type')
        artist_ids = data.pop('artist_ids', None)
        tag_ids = data.pop('tag_ids', None)

        try:
            photo = self._service.create(
                resource_type_id=resource_type_id,
                reference=reference,
                reference_type=reference_type,
                artist_ids=artist_ids,
                tag_ids=tag_ids,
                **data
            )
        except ArtistNotFound:
            return Response({'error': 'One or more artists not found'}, status=status.HTTP_404_NOT_FOUND)
        except TagNotFound:
            return Response({'error': 'One or more tags not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(PhotoSerializer(photo).data, status=status.HTTP_201_CREATED)


class PhotoDetailView(APIView):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._service = PhotoService()

    def get(self, request: Request, photo_id: int) -> Response:
        try:
            photo = self._service.get_by_id(photo_id=photo_id)
        except PhotoNotFound:
            return Response({'error': 'Photo not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(PhotoSerializer(photo).data)

    def patch(self, request: Request, photo_id: int) -> Response:
        serializer = PhotoUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        artist_ids = data.pop('artist_ids', None)
        tag_ids = data.pop('tag_ids', None)

        try:
            photo = self._service.update(photo_id=photo_id, artist_ids=artist_ids, tag_ids=tag_ids, **data)
        except PhotoNotFound:
            return Response({'error': 'Photo not found'}, status=status.HTTP_404_NOT_FOUND)
        except ArtistNotFound:
            return Response({'error': 'One or more artists not found'}, status=status.HTTP_404_NOT_FOUND)
        except TagNotFound:
            return Response({'error': 'One or more tags not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(PhotoSerializer(photo).data)

    def delete(self, request: Request, photo_id: int) -> Response:
        try:
            self._service.delete(photo_id=photo_id)
        except PhotoNotFound:
            return Response({'error': 'Photo not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_200_OK)
