from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.services.resource_type_service import ResourceTypeService
from core.serializers.resource_type_serializer import ResourceTypeSerializer
from core.exceptions import ResourceTypeNotFound


class ResourceTypeListCreateView(APIView):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._service = ResourceTypeService()

    def get(self, request: Request) -> Response:
        resource_types = self._service.list_all()
        return Response(ResourceTypeSerializer(resource_types, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = ResourceTypeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        resource_type = self._service.create(**serializer.validated_data)
        return Response(ResourceTypeSerializer(resource_type).data, status=status.HTTP_201_CREATED)


class ResourceTypeDetailView(APIView):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._service = ResourceTypeService()

    def get(self, request: Request, resource_type_id: int) -> Response:
        try:
            resource_type = self._service.get_by_id(resource_type_id=resource_type_id)
        except ResourceTypeNotFound:
            return Response({'error': 'ResourceType not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(ResourceTypeSerializer(resource_type).data)

    def patch(self, request: Request, resource_type_id: int) -> Response:
        serializer = ResourceTypeSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            resource_type = self._service.update(resource_type_id=resource_type_id, **serializer.validated_data)
        except ResourceTypeNotFound:
            return Response({'error': 'ResourceType not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(ResourceTypeSerializer(resource_type).data)

    def delete(self, request: Request, resource_type_id: int) -> Response:
        self._service.delete(resource_type_id=resource_type_id)
        return Response(status=status.HTTP_200_OK)
