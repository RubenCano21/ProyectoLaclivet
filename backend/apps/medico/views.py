from apps.core.permissions import EsStaffInterno, EsMedicoExterno
from rest_framework import status
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
        medicos = MedicoVeterinario.objects.select_related('usuario').all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(medicos, request)
        return paginator.get_paginated_response(MedicoVeterinarioSerializer(pagina, many=True).data)

    @swagger_auto_schema(operation_summary="Crear médico veterinario", request_body=MedicoVeterinarioCreateSerializer)
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
            return MedicoVeterinario.objects.select_related('usuario').get(pk=pk)
        except MedicoVeterinario.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Obtener médico veterinario", responses={200: MedicoVeterinarioSerializer})
    def get(self, request, pk):
        medico = self.get_object(pk)
        if medico is None:
            return Response({'error': 'Médico no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(MedicoVeterinarioSerializer(medico).data)

    @swagger_auto_schema(operation_summary="Actualizar médico veterinario", request_body=MedicoVeterinarioUpdateSerializer)
    def put(self, request, pk):
        medico = self.get_object(pk)
        if medico is None:
            return Response({'error': 'Médico no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MedicoVeterinarioUpdateSerializer(medico, data=request.data)
        if serializer.is_valid():
            return Response(MedicoVeterinarioSerializer(serializer.save()).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente médico", request_body=MedicoVeterinarioUpdateSerializer)
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
        # Eliminar también el usuario vinculado
        usuario = medico.usuario
        medico.delete()
        if usuario:
            usuario.delete()
        return Response({'mensaje': 'Médico eliminado exitosamente'}, status=status.HTTP_200_OK)


class ResultadosMedicoVeterinarioView(APIView):
    permission_classes = [EsMedicoExterno]

    def get(self, request):
        # El médico autenticado ve solo sus propios resultados
        try:
            medico = request.user.medico_perfil
        except MedicoVeterinario.DoesNotExist:
            return Response({'error': 'No tiene perfil de médico'}, status=status.HTTP_404_NOT_FOUND)

        from apps.muestra.models import Resultado
        from apps.muestra.serializers import ResultadoSerializer
        resultados = Resultado.objects.filter(
            detalle_solicitud__solicitud__medico_veterinario=medico
        ).select_related(
            'detalle_solicitud__solicitud',
            'detalle_solicitud__examen',
            'muestra',
        )
        return Response(ResultadoSerializer(resultados, many=True).data)