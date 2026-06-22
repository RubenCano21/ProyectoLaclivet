from apps.core.permissions import EsStaffInterno, EsMedicoExterno
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from config.pagination import StandardPagination
from .models import MedicoVeterinario
from .serializers import (
    MedicoVeterinarioSerializer,
    MedicoVeterinarioCreateSerializer,
    MedicoVeterinarioUpdateSerializer,
)


class MedicoVeterinarioListCreateView(APIView):
    permission_classes = [EsStaffInterno]

    @swagger_auto_schema(operation_summary="Listar médicos veterinarios", responses={200: MedicoVeterinarioSerializer(many=True)})
    def get(self, request):
        medicos = MedicoVeterinario.objects.all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(medicos, request)
        return paginator.get_paginated_response(MedicoVeterinarioSerializer(pagina, many=True).data)

    @swagger_auto_schema(operation_summary="Crear médico veterinario", request_body=MedicoVeterinarioCreateSerializer, responses={201: MedicoVeterinarioSerializer})
    def post(self, request):
        serializer = MedicoVeterinarioCreateSerializer(data=request.data)
        if serializer.is_valid():
            medico = serializer.save()
            return Response(MedicoVeterinarioSerializer(medico).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MedicoVeterinarioDetailView(APIView):
    permission_classes = [EsStaffInterno]

    def get_object(self, pk):
        try:
            return MedicoVeterinario.objects.get(pk=pk)
        except MedicoVeterinario.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Obtener médico veterinario", responses={200: MedicoVeterinarioSerializer})
    def get(self, request, pk):
        medico = self.get_object(pk)
        if medico is None:
            return Response({'error': 'Médico no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(MedicoVeterinarioSerializer(medico).data)

    @swagger_auto_schema(operation_summary="Actualizar médico veterinario", request_body=MedicoVeterinarioUpdateSerializer, responses={200: MedicoVeterinarioSerializer})
    def put(self, request, pk):
        medico = self.get_object(pk)
        if medico is None:
            return Response({'error': 'Médico no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MedicoVeterinarioUpdateSerializer(medico, data=request.data)
        if serializer.is_valid():
            return Response(MedicoVeterinarioSerializer(serializer.save()).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente médico", request_body=MedicoVeterinarioUpdateSerializer, responses={200: MedicoVeterinarioSerializer})
    def patch(self, request, pk):
        medico = self.get_object(pk)
        if medico is None:
            return Response({'error': 'Médico no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MedicoVeterinarioUpdateSerializer(medico, data=request.data, partial=True)
        if serializer.is_valid():
            return Response(MedicoVeterinarioSerializer(serializer.save()).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Eliminar médico veterinario", responses={200: openapi.Response('Eliminado')})
    def delete(self, request, pk):
        medico = self.get_object(pk)
        if medico is None:
            return Response({'error': 'Médico no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        medico.delete()
        return Response({'mensaje': 'Médico eliminado exitosamente'}, status=status.HTTP_200_OK)

class ResultadosMedicoVeterinarioView(APIView):
    permission_classes = [EsMedicoExterno]  # médico externo ve sus resultados
    def get(self, request, pk):
        medico = MedicoVeterinario.objects.get(pk=pk)
        resultados = medico.resultados.filter(solicitud__medico=medico)
        return Response(MedicoVeterinarioSerializer(medico, context={'resultados': resultados}).data)