from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.services.collection_item_service import CollectionItemService
from core.serializers.collection_item_serializer import (
    CollectionItemCreateSerializer,
    CollectionItemUpdateSerializer,
    CollectionItemSerializer,
)
from core.exceptions import (
    CollectionNotFound,
    ResourceRegistryNotFound,
    CollectionItemNotFound,
    CollectionItemAlreadyExists,
)


class CollectionItemListCreateView(APIView):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._service = CollectionItemService()

    def get(self, request: Request, collection_id: int) -> Response:
        try:
            items = self._service.list_by_collection(collection_id=collection_id)
        except CollectionNotFound:
            return Response({'error': 'Collection not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(CollectionItemSerializer(items, many=True).data)

    @extend_schema(request=CollectionItemCreateSerializer)
    def post(self, request: Request, collection_id: int) -> Response:
        serializer = CollectionItemCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = self._service.add_item(collection_id=collection_id, **serializer.validated_data)
        except CollectionNotFound:
            return Response({'error': 'Collection not found'}, status=status.HTTP_404_NOT_FOUND)
        except ResourceRegistryNotFound:
            return Response({'error': 'Resource not found'}, status=status.HTTP_404_NOT_FOUND)
        except CollectionItemAlreadyExists:
            return Response({'error': 'Resource already in collection'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(CollectionItemSerializer(item).data, status=status.HTTP_201_CREATED)


class CollectionItemDetailView(APIView):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._service = CollectionItemService()

    @extend_schema(request=CollectionItemUpdateSerializer)
    def patch(self, request: Request, collection_id: int, item_id: int) -> Response:
        serializer = CollectionItemUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = self._service.update(collection_id=collection_id, item_id=item_id, **serializer.validated_data)
        except CollectionItemNotFound:
            return Response({'error': 'CollectionItem not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(CollectionItemSerializer(item).data)

    def delete(self, request: Request, collection_id: int, item_id: int) -> Response:
        self._service.delete(collection_id=collection_id, item_id=item_id)
        return Response(status=status.HTTP_200_OK)
