from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.services.collection_service import CollectionService
from core.serializers.collection_serializer import CollectionSerializer
from core.exceptions import CollectionNotFound


class CollectionListCreateView(APIView):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._service = CollectionService()

    def get(self, request: Request) -> Response:
        collections = self._service.list_all()
        return Response(CollectionSerializer(collections, many=True).data)

    @extend_schema(request=CollectionSerializer)
    def post(self, request: Request) -> Response:
        serializer = CollectionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        collection = self._service.create(**serializer.validated_data)
        return Response(CollectionSerializer(collection).data, status=status.HTTP_201_CREATED)


class CollectionDetailView(APIView):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._service = CollectionService()

    def get(self, request: Request, collection_id: int) -> Response:
        try:
            collection = self._service.get_by_id(collection_id=collection_id)
        except CollectionNotFound:
            return Response({'error': 'Collection not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(CollectionSerializer(collection).data)

    @extend_schema(request=CollectionSerializer)
    def patch(self, request: Request, collection_id: int) -> Response:
        serializer = CollectionSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            collection = self._service.update(collection_id=collection_id, **serializer.validated_data)
        except CollectionNotFound:
            return Response({'error': 'Collection not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(CollectionSerializer(collection).data)

    def delete(self, request: Request, collection_id: int) -> Response:
        self._service.delete(collection_id=collection_id)
        return Response(status=status.HTTP_200_OK)
