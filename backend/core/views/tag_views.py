from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.services.tag_service import TagService
from core.serializers.tag_serializer import TagSerializer
from core.exceptions import TagNotFound


class TagListCreateView(APIView):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._service = TagService()

    def get(self, request: Request) -> Response:
        tags = self._service.list_all()
        return Response(TagSerializer(tags, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = TagSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        tag = self._service.create(**serializer.validated_data)
        return Response(TagSerializer(tag).data, status=status.HTTP_201_CREATED)


class TagDetailView(APIView):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._service = TagService()

    def get(self, request: Request, tag_id: int) -> Response:
        try:
            tag = self._service.get_by_id(tag_id=tag_id)
        except TagNotFound:
            return Response({'error': 'Tag not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(TagSerializer(tag).data)

    def patch(self, request: Request, tag_id: int) -> Response:
        serializer = TagSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            tag = self._service.update(tag_id=tag_id, **serializer.validated_data)
        except TagNotFound:
            return Response({'error': 'Tag not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(TagSerializer(tag).data)

    def delete(self, request: Request, tag_id: int) -> Response:
        self._service.delete(tag_id=tag_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
