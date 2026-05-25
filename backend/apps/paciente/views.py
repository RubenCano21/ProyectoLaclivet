from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from config.pagination import StandardPagination
from .models import Especie, Raza, HistorialClinico, Paciente
from .serializers import (
    EspecieSerializer, EspecieCreateSerializer, EspecieUpdateSerializer,
    RazaSerializer, RazaCreateSerializer, RazaUpdateSerializer,
    HistorialClinicoSerializer, HistorialClinicoCreateSerializer, HistorialClinicoUpdateSerializer,
    PacienteSerializer, PacienteCreateSerializer, PacienteUpdateSerializer,
)


def _crud_view(Model, ReadSerializer, WriteSerializer, UpdateSerializer, not_found_msg):
    """Helper para reducir boilerplate en vistas detalle"""
    pass


# ── Especie ──────────────────────────────────────────────
class EspecieListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(Especie.objects.all(), request)
        return paginator.get_paginated_response(EspecieSerializer(pagina, many=True).data)

    def post(self, request):
        s = EspecieCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(EspecieSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


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
        s = EspecieUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(EspecieSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Especie no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        s = EspecieUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(EspecieSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

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
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(Raza.objects.select_related('especie').all(), request)
        return paginator.get_paginated_response(RazaSerializer(pagina, many=True).data)

    def post(self, request):
        s = RazaCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(RazaSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


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
        s = RazaUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(RazaSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Raza no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        s = RazaUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(RazaSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

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
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(HistorialClinico.objects.all(), request)
        return paginator.get_paginated_response(HistorialClinicoSerializer(pagina, many=True).data)

    def post(self, request):
        s = HistorialClinicoCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(HistorialClinicoSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


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
        s = HistorialClinicoUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(HistorialClinicoSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Historial clínico no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = HistorialClinicoUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(HistorialClinicoSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Historial clínico no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Historial clínico eliminado exitosamente'}, status=status.HTTP_200_OK)


# ── Paciente ──────────────────────────────────────────────
class PacienteListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Paciente.objects.select_related('raza__especie', 'propietario', 'historial_clinico').all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(PacienteSerializer(pagina, many=True).data)

    def post(self, request):
        s = PacienteCreateSerializer(data=request.data)
        if s.is_valid():
            paciente = s.save()
            return Response(PacienteSerializer(paciente).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class PacienteDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Paciente.objects.select_related('raza__especie', 'propietario', 'historial_clinico').get(pk=pk)
        except Paciente.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Paciente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PacienteSerializer(obj).data)

    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Paciente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = PacienteUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(PacienteSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Paciente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = PacienteUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(PacienteSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Paciente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Paciente eliminado exitosamente'}, status=status.HTTP_200_OK)
