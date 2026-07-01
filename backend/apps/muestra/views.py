from apps.core.permissions import EsStaffInterno
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from config.pagination import StandardPagination
from .models import Muestra, IncidenciaMuestra
from .serializers import (
    MuestraSerializer, MuestraCreateSerializer, MuestraUpdateSerializer,
    IncidenciaMuestraSerializer, IncidenciaMuestraCreateSerializer, IncidenciaMuestraUpdateSerializer
)

_del_response = openapi.Response('Eliminado exitosamente')


class MuestraListCreateView(APIView):
    permission_classes = [EsStaffInterno]

    @swagger_auto_schema(operation_summary="Listar muestras", responses={200: MuestraSerializer(many=True)})
    def get(self, request):
        qs = Muestra.objects.select_related('solicitud', 'paciente').all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(MuestraSerializer(pagina, many=True).data)

    @swagger_auto_schema(operation_summary="Crear muestra", request_body=MuestraCreateSerializer, responses={201: MuestraSerializer})
    def post(self, request):
        s = MuestraCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(MuestraSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class MuestraDetailView(APIView):
    permission_classes = [EsStaffInterno]

    def get_object(self, pk):
        try:
            return Muestra.objects.select_related('solicitud', 'paciente').get(pk=pk)
        except Muestra.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Obtener muestra", responses={200: MuestraSerializer})
    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Muestra no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        return Response(MuestraSerializer(obj).data)

    @swagger_auto_schema(operation_summary="Actualizar muestra", request_body=MuestraUpdateSerializer, responses={200: MuestraSerializer})
    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Muestra no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        s = MuestraUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(MuestraSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente muestra", request_body=MuestraUpdateSerializer, responses={200: MuestraSerializer})
    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Muestra no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        s = MuestraUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(MuestraSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Eliminar muestra", responses={200: _del_response})
    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Muestra no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Muestra eliminada exitosamente'}, status=status.HTTP_200_OK)


# ── IncidenciaMuestra ─────────────────────────────────────
class IncidenciaMuestraListCreateView(APIView):
    permission_classes = [EsStaffInterno]

    @swagger_auto_schema(operation_summary="Listar incidencias de muestra", responses={200: IncidenciaMuestraSerializer(many=True)})
    def get(self, request):
        qs = IncidenciaMuestra.objects.select_related('muestra').all()
        muestra_id = request.query_params.get('muestra')
        if muestra_id:
            qs = qs.filter(muestra_id=muestra_id)
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(IncidenciaMuestraSerializer(pagina, many=True).data)

    @swagger_auto_schema(operation_summary="Crear incidencia de muestra", request_body=IncidenciaMuestraCreateSerializer, responses={201: IncidenciaMuestraSerializer})
    def post(self, request):
        s = IncidenciaMuestraCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(IncidenciaMuestraSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class IncidenciaMuestraDetailView(APIView):
    permission_classes = [EsStaffInterno]

    def get_object(self, pk):
        try:
            return IncidenciaMuestra.objects.select_related('muestra').get(pk=pk)
        except IncidenciaMuestra.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Obtener incidencia de muestra", responses={200: IncidenciaMuestraSerializer})
    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Incidencia no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        return Response(IncidenciaMuestraSerializer(obj).data)

    @swagger_auto_schema(operation_summary="Actualizar incidencia", request_body=IncidenciaMuestraUpdateSerializer, responses={200: IncidenciaMuestraSerializer})
    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Incidencia no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        s = IncidenciaMuestraUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(IncidenciaMuestraSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente incidencia", request_body=IncidenciaMuestraUpdateSerializer, responses={200: IncidenciaMuestraSerializer})
    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Incidencia no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        s = IncidenciaMuestraUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(IncidenciaMuestraSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Eliminar incidencia", responses={200: _del_response})
    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Incidencia no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Incidencia eliminada exitosamente'}, status=status.HTTP_200_OK)

