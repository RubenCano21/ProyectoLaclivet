from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from config.pagination import StandardPagination
from .models import CatalogoExamen
from .serializers import (
    CatalogoExamenSerializer,
    CatalogoExamenCreateSerializer,
    CatalogoExamenUpdateSerializer,
)


class CatalogoExamenListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        catalogos = CatalogoExamen.objects.all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(catalogos, request)
        serializer = CatalogoExamenSerializer(pagina, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = CatalogoExamenCreateSerializer(data=request.data)
        if serializer.is_valid():
            catalogo = serializer.save()
            return Response(
                CatalogoExamenSerializer(catalogo).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CatalogoExamenDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return CatalogoExamen.objects.get(pk=pk)
        except CatalogoExamen.DoesNotExist:
            return None

    def get(self, request, pk):
        catalogo = self.get_object(pk)
        if catalogo is None:
            return Response({'error': 'Catálogo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CatalogoExamenSerializer(catalogo).data)

    def put(self, request, pk):
        catalogo = self.get_object(pk)
        if catalogo is None:
            return Response({'error': 'Catálogo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CatalogoExamenUpdateSerializer(catalogo, data=request.data)
        if serializer.is_valid():
            catalogo = serializer.save()
            return Response(CatalogoExamenSerializer(catalogo).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        catalogo = self.get_object(pk)
        if catalogo is None:
            return Response({'error': 'Catálogo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CatalogoExamenUpdateSerializer(catalogo, data=request.data, partial=True)
        if serializer.is_valid():
            catalogo = serializer.save()
            return Response(CatalogoExamenSerializer(catalogo).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        catalogo = self.get_object(pk)
        if catalogo is None:
            return Response({'error': 'Catálogo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        catalogo.delete()
        return Response({'mensaje': 'Catálogo eliminado exitosamente'}, status=status.HTTP_200_OK)

