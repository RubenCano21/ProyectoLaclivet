from apps.core.permissions import EsStaffInterno, EsPropietario
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from config.pagination import StandardPagination
from .models import Propietario
from .serializers import (
    PropietarioSerializer,
    PropietarioCreateSerializer,
    PropietarioUpdateSerializer,
)


class PropietarioListCreateView(APIView):
    permission_classes = [EsStaffInterno]

    @swagger_auto_schema(operation_summary="Listar propietarios", responses={200: PropietarioSerializer(many=True)})
    def get(self, request):
        propietarios = Propietario.objects.select_related('usuario').order_by(
            'usuario__last_name', 'usuario__first_name'
        )
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(propietarios, request)
        return paginator.get_paginated_response(PropietarioSerializer(pagina, many=True).data)

    @swagger_auto_schema(operation_summary="Crear propietario", request_body=PropietarioCreateSerializer)
    def post(self, request):
        serializer = PropietarioCreateSerializer(data=request.data)
        if serializer.is_valid():
            propietario = serializer.save()
            return Response(PropietarioSerializer(propietario).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PropietarioDetailView(APIView):
    permission_classes = [EsStaffInterno]

    def get_object(self, pk):
        try:
            return Propietario.objects.select_related('usuario').get(pk=pk)
        except Propietario.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Obtener propietario", responses={200: PropietarioSerializer})
    def get(self, request, pk):
        propietario = self.get_object(pk)
        if propietario is None:
            return Response({'error': 'Propietario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PropietarioSerializer(propietario).data)

    @swagger_auto_schema(operation_summary="Actualizar propietario", request_body=PropietarioUpdateSerializer)
    def put(self, request, pk):
        propietario = self.get_object(pk)
        if propietario is None:
            return Response({'error': 'Propietario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PropietarioUpdateSerializer(propietario, data=request.data)
        if serializer.is_valid():
            return Response(PropietarioSerializer(serializer.save()).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente propietario", request_body=PropietarioUpdateSerializer)
    def patch(self, request, pk):
        propietario = self.get_object(pk)
        if propietario is None:
            return Response({'error': 'Propietario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PropietarioUpdateSerializer(propietario, data=request.data, partial=True)
        if serializer.is_valid():
            return Response(PropietarioSerializer(serializer.save()).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Eliminar propietario", responses={200: openapi.Response('Eliminado')})
    def delete(self, request, pk):
        propietario = self.get_object(pk)
        if propietario is None:
            return Response({'error': 'Propietario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        # Eliminar también el usuario vinculado
        usuario = propietario.usuario
        propietario.delete()
        if usuario:
            usuario.delete()
        return Response({'mensaje': 'Propietario eliminado exitosamente'}, status=status.HTTP_200_OK)


class ResultadosPropietarioView(APIView):
    permission_classes = [EsPropietario]

    def get(self, request):
        try:
            propietario = request.user.propietario_perfil
        except Propietario.DoesNotExist:
            return Response({'error': 'No tiene perfil de propietario'}, status=status.HTTP_404_NOT_FOUND)

        from apps.muestra.models import Resultado
        from apps.muestra.serializers import ResultadoSerializer
        resultados = Resultado.objects.filter(
            detalle_solicitud__solicitud__paciente__propietario=propietario
        ).select_related(
            'detalle_solicitud__solicitud__paciente',
            'detalle_solicitud__examen',
            'muestra',
        )
        return Response(ResultadoSerializer(resultados, many=True).data)