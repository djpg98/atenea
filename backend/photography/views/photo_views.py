from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from photography.services.photo_service import PhotoService
from photography.serializers.photo_serializer import PhotoCreateSerializer, PhotoSerializer
from photography.exceptions import PhotoNotFound


class PhotoListCreateView(APIView):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._service = PhotoService()

    def post(self, request: Request) -> Response:
        serializer = PhotoCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        resource_type_id = data.pop('resource_type_id')
        reference = data.pop('reference')
        reference_type = data.pop('reference_type')

        photo = self._service.create(
            resource_type_id=resource_type_id,
            reference=reference,
            reference_type=reference_type,
            **data
        )
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
