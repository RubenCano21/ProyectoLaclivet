from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from config.pagination import StandardPagination
from .models import Especie
from .serializers import (
    EspecieSerializer,
    EspecieCreateSerializer,
    EspecieUpdateSerializer,
)


class EspecieListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        especies = Especie.objects.all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(especies, request)
        serializer = EspecieSerializer(pagina, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = EspecieCreateSerializer(data=request.data)
        if serializer.is_valid():
            especie = serializer.save()
            return Response(EspecieSerializer(especie).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EspecieDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Especie.objects.get(pk=pk)
        except Especie.DoesNotExist:
            return None

    def get(self, request, pk):
        especie = self.get_object(pk)
        if especie is None:
            return Response({'error': 'Especie no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        return Response(EspecieSerializer(especie).data)

    def put(self, request, pk):
        especie = self.get_object(pk)
        if especie is None:
            return Response({'error': 'Especie no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EspecieUpdateSerializer(especie, data=request.data)
        if serializer.is_valid():
            especie = serializer.save()
            return Response(EspecieSerializer(especie).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        especie = self.get_object(pk)
        if especie is None:
            return Response({'error': 'Especie no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EspecieUpdateSerializer(especie, data=request.data, partial=True)
        if serializer.is_valid():
            especie = serializer.save()
            return Response(EspecieSerializer(especie).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        especie = self.get_object(pk)
        if especie is None:
            return Response({'error': 'Especie no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        especie.delete()
        return Response({'mensaje': 'Especie eliminada exitosamente'}, status=status.HTTP_200_OK)

