from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from config.pagination import StandardPagination
from .models import Cobro, SolicitudExamen, DetalleSolicitud
from .serializers import (
    CobroSerializer, CobroCreateSerializer, CobroUpdateSerializer,
    SolicitudExamenSerializer, SolicitudExamenCreateSerializer, SolicitudExamenUpdateSerializer,
    DetalleSolicitudSerializer, DetalleSolicitudCreateSerializer, DetalleSolicitudUpdateSerializer,
)


# ── Cobro ─────────────────────────────────────────────────
class CobroListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(Cobro.objects.all(), request)
        return paginator.get_paginated_response(CobroSerializer(pagina, many=True).data)

    def post(self, request):
        s = CobroCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(CobroSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class CobroDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Cobro.objects.get(pk=pk)
        except Cobro.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Cobro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CobroSerializer(obj).data)

    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Cobro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = CobroUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(CobroSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Cobro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = CobroUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(CobroSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Cobro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Cobro eliminado exitosamente'}, status=status.HTTP_200_OK)


# ── SolicitudExamen ───────────────────────────────────────
class SolicitudExamenListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = SolicitudExamen.objects.select_related(
            'cobro', 'historial_clinico', 'medico_veterinario'
        ).all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(SolicitudExamenSerializer(pagina, many=True).data)

    def post(self, request):
        s = SolicitudExamenCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(SolicitudExamenSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class SolicitudExamenDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return SolicitudExamen.objects.select_related(
                'cobro', 'historial_clinico', 'medico_veterinario'
            ).get(pk=pk)
        except SolicitudExamen.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Solicitud no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        return Response(SolicitudExamenSerializer(obj).data)

    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Solicitud no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        s = SolicitudExamenUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(SolicitudExamenSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Solicitud no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        s = SolicitudExamenUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(SolicitudExamenSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Solicitud no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Solicitud eliminada exitosamente'}, status=status.HTTP_200_OK)


# ── DetalleSolicitud ──────────────────────────────────────
class DetalleSolicitudListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = DetalleSolicitud.objects.select_related('solicitud', 'examen').all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(DetalleSolicitudSerializer(pagina, many=True).data)

    def post(self, request):
        s = DetalleSolicitudCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(DetalleSolicitudSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class DetalleSolicitudDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return DetalleSolicitud.objects.select_related('solicitud', 'examen').get(pk=pk)
        except DetalleSolicitud.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Detalle no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(DetalleSolicitudSerializer(obj).data)

    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Detalle no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = DetalleSolicitudUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(DetalleSolicitudSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Detalle no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = DetalleSolicitudUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(DetalleSolicitudSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Detalle no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Detalle eliminado exitosamente'}, status=status.HTTP_200_OK)

