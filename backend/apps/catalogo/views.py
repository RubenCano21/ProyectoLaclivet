from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from config.pagination import StandardPagination
from .models import CatalogoExamen, Examen
from .serializers import (
    CatalogoExamenSerializer,
    CatalogoExamenCreateSerializer,
    CatalogoExamenUpdateSerializer,
    ExamenSerializer,
    ExamenCreateSerializer,
    ExamenUpdateSerializer,
)


class CatalogoExamenListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        catalogos = CatalogoExamen.objects.all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(catalogos, request)
        return paginator.get_paginated_response(CatalogoExamenSerializer(pagina, many=True).data)

    def post(self, request):
        serializer = CatalogoExamenCreateSerializer(data=request.data)
        if serializer.is_valid():
            catalogo = serializer.save()
            return Response(CatalogoExamenSerializer(catalogo).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CatalogoExamenDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return CatalogoExamen.objects.get(pk=pk)
        except CatalogoExamen.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Catálogo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CatalogoExamenSerializer(obj).data)

    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Catálogo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CatalogoExamenUpdateSerializer(obj, data=request.data)
        if serializer.is_valid():
            return Response(CatalogoExamenSerializer(serializer.save()).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Catálogo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CatalogoExamenUpdateSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            return Response(CatalogoExamenSerializer(serializer.save()).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Catálogo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Catálogo eliminado exitosamente'}, status=status.HTTP_200_OK)


# ── Examen ────────────────────────────────────────────────
class ExamenListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        examenes = Examen.objects.select_related('catalogo').all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(examenes, request)
        return paginator.get_paginated_response(ExamenSerializer(pagina, many=True).data)

    def post(self, request):
        serializer = ExamenCreateSerializer(data=request.data)
        if serializer.is_valid():
            examen = serializer.save()
            return Response(ExamenSerializer(examen).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExamenDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Examen.objects.select_related('catalogo').get(pk=pk)
        except Examen.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Examen no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ExamenSerializer(obj).data)

    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Examen no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ExamenUpdateSerializer(obj, data=request.data)
        if serializer.is_valid():
            return Response(ExamenSerializer(serializer.save()).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Examen no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ExamenUpdateSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            return Response(ExamenSerializer(serializer.save()).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Examen no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Examen eliminado exitosamente'}, status=status.HTTP_200_OK)
