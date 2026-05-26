from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from config.pagination import StandardPagination
from .models import Cobro, SolicitudExamen, DetalleSolicitud
from .serializers import (
    CobroSerializer, CobroCreateSerializer, CobroUpdateSerializer,
    SolicitudExamenSerializer, SolicitudExamenCreateSerializer, SolicitudExamenUpdateSerializer,
    DetalleSolicitudSerializer, DetalleSolicitudCreateSerializer, DetalleSolicitudUpdateSerializer,
)

_del_response = openapi.Response('Eliminado exitosamente')


# ── Cobro ─────────────────────────────────────────────────
class CobroListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_summary="Listar cobros", responses={200: CobroSerializer(many=True)})
    def get(self, request):
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(Cobro.objects.all(), request)
        return paginator.get_paginated_response(CobroSerializer(pagina, many=True).data)

    @swagger_auto_schema(operation_summary="Crear cobro", request_body=CobroCreateSerializer, responses={201: CobroSerializer})
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

    @swagger_auto_schema(operation_summary="Obtener cobro", responses={200: CobroSerializer})
    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Cobro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CobroSerializer(obj).data)

    @swagger_auto_schema(operation_summary="Actualizar cobro", request_body=CobroUpdateSerializer, responses={200: CobroSerializer})
    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Cobro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = CobroUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(CobroSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente cobro", request_body=CobroUpdateSerializer, responses={200: CobroSerializer})
    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Cobro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = CobroUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(CobroSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Eliminar cobro", responses={200: _del_response})
    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Cobro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Cobro eliminado exitosamente'}, status=status.HTTP_200_OK)


# ── SolicitudExamen ───────────────────────────────────────
class SolicitudExamenListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_summary="Listar solicitudes de examen", responses={200: SolicitudExamenSerializer(many=True)})
    def get(self, request):
        qs = SolicitudExamen.objects.select_related('cobro', 'paciente', 'medico_veterinario').all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(SolicitudExamenSerializer(pagina, many=True).data)

    @swagger_auto_schema(operation_summary="Crear solicitud de examen", request_body=SolicitudExamenCreateSerializer, responses={201: SolicitudExamenSerializer})
    def post(self, request):
        s = SolicitudExamenCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(SolicitudExamenSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class SolicitudExamenDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return SolicitudExamen.objects.select_related('cobro', 'paciente', 'medico_veterinario').get(pk=pk)
        except SolicitudExamen.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Obtener solicitud de examen", responses={200: SolicitudExamenSerializer})
    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Solicitud no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        return Response(SolicitudExamenSerializer(obj).data)

    @swagger_auto_schema(operation_summary="Actualizar solicitud de examen", request_body=SolicitudExamenUpdateSerializer, responses={200: SolicitudExamenSerializer})
    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Solicitud no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        s = SolicitudExamenUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(SolicitudExamenSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente solicitud", request_body=SolicitudExamenUpdateSerializer, responses={200: SolicitudExamenSerializer})
    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Solicitud no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        s = SolicitudExamenUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(SolicitudExamenSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Eliminar solicitud de examen", responses={200: _del_response})
    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Solicitud no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Solicitud eliminada exitosamente'}, status=status.HTTP_200_OK)


# ── DetalleSolicitud ──────────────────────────────────────
class DetalleSolicitudListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_summary="Listar detalles de solicitud", responses={200: DetalleSolicitudSerializer(many=True)})
    def get(self, request):
        qs = DetalleSolicitud.objects.select_related('solicitud', 'examen').all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(DetalleSolicitudSerializer(pagina, many=True).data)

    @swagger_auto_schema(operation_summary="Crear detalle de solicitud", request_body=DetalleSolicitudCreateSerializer, responses={201: DetalleSolicitudSerializer})
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

    @swagger_auto_schema(operation_summary="Obtener detalle de solicitud", responses={200: DetalleSolicitudSerializer})
    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Detalle no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(DetalleSolicitudSerializer(obj).data)

    @swagger_auto_schema(operation_summary="Actualizar detalle de solicitud", request_body=DetalleSolicitudUpdateSerializer, responses={200: DetalleSolicitudSerializer})
    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Detalle no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = DetalleSolicitudUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(DetalleSolicitudSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente detalle", request_body=DetalleSolicitudUpdateSerializer, responses={200: DetalleSolicitudSerializer})
    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Detalle no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = DetalleSolicitudUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(DetalleSolicitudSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Eliminar detalle de solicitud", responses={200: _del_response})
    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Detalle no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Detalle eliminado exitosamente'}, status=status.HTTP_200_OK)
