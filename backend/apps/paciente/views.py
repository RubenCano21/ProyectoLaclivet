from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from config.pagination import StandardPagination
from .models import Especie, Raza, HistorialClinico
from .serializers import (
    EspecieSerializer, EspecieCreateSerializer, EspecieUpdateSerializer,
    RazaSerializer, RazaCreateSerializer, RazaUpdateSerializer,
    HistorialClinicoSerializer, HistorialClinicoCreateSerializer, HistorialClinicoUpdateSerializer,
)


# ── Especie ──────────────────────────────────────────────
class EspecieListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        especies = Especie.objects.all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(especies, request)
        return paginator.get_paginated_response(EspecieSerializer(pagina, many=True).data)

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
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Especie no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        return Response(EspecieSerializer(obj).data)

    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Especie no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EspecieUpdateSerializer(obj, data=request.data)
        if serializer.is_valid():
            return Response(EspecieSerializer(serializer.save()).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Especie no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EspecieUpdateSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            return Response(EspecieSerializer(serializer.save()).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Especie no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Especie eliminada exitosamente'}, status=status.HTTP_200_OK)


# ── Raza ─────────────────────────────────────────────────
class RazaListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        razas = Raza.objects.select_related('especie').all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(razas, request)
        return paginator.get_paginated_response(RazaSerializer(pagina, many=True).data)

    def post(self, request):
        serializer = RazaCreateSerializer(data=request.data)
        if serializer.is_valid():
            raza = serializer.save()
            return Response(RazaSerializer(raza).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RazaDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Raza.objects.select_related('especie').get(pk=pk)
        except Raza.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Raza no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        return Response(RazaSerializer(obj).data)

    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Raza no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        serializer = RazaUpdateSerializer(obj, data=request.data)
        if serializer.is_valid():
            return Response(RazaSerializer(serializer.save()).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Raza no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        serializer = RazaUpdateSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            return Response(RazaSerializer(serializer.save()).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Raza no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Raza eliminada exitosamente'}, status=status.HTTP_200_OK)


# ── HistorialClinico ──────────────────────────────────────
class HistorialClinicoListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        historiales = HistorialClinico.objects.all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(historiales, request)
        return paginator.get_paginated_response(HistorialClinicoSerializer(pagina, many=True).data)

    def post(self, request):
        serializer = HistorialClinicoCreateSerializer(data=request.data)
        if serializer.is_valid():
            historial = serializer.save()
            return Response(HistorialClinicoSerializer(historial).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HistorialClinicoDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return HistorialClinico.objects.get(pk=pk)
        except HistorialClinico.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Historial clínico no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(HistorialClinicoSerializer(obj).data)

    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Historial clínico no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = HistorialClinicoUpdateSerializer(obj, data=request.data)
        if serializer.is_valid():
            return Response(HistorialClinicoSerializer(serializer.save()).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Historial clínico no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = HistorialClinicoUpdateSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            return Response(HistorialClinicoSerializer(serializer.save()).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Historial clínico no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Historial clínico eliminado exitosamente'}, status=status.HTTP_200_OK)

