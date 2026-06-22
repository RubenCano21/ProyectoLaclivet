from apps.core.permissions import EsStaffInterno, EsPropietario
from apps.muestra.models import Resultado
from apps.muestra.serializers import ResultadoSerializer
from rest_framework import status, permissions
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
    """Lista todos los propietarios o crea uno nuevo"""
    permission_classes = [EsStaffInterno]

    @swagger_auto_schema(
        operation_summary="Listar propietarios",
        responses={200: PropietarioSerializer(many=True)}
    )
    def get(self, request):
        propietarios = Propietario.objects.all().order_by('apellido', 'nombre')
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(propietarios, request)
        serializer = PropietarioSerializer(pagina, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Crear propietario",
        request_body=PropietarioCreateSerializer,
        responses={201: PropietarioSerializer}
    )
    def post(self, request):
        serializer = PropietarioCreateSerializer(data=request.data)
        if serializer.is_valid():
            propietario = serializer.save()
            return Response(
                PropietarioSerializer(propietario).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PropietarioDetailView(APIView):
    """Obtiene, actualiza o elimina un propietario por ID"""
    permission_classes = [EsStaffInterno]

    def get_object(self, pk):
        try:
            return Propietario.objects.get(pk=pk)
        except Propietario.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Obtener propietario", responses={200: PropietarioSerializer})
    def get(self, request, pk):
        propietario = self.get_object(pk)
        if propietario is None:
            return Response(
                {'error': 'Propietario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = PropietarioSerializer(propietario)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_summary="Actualizar propietario", request_body=PropietarioUpdateSerializer, responses={200: PropietarioSerializer})
    def put(self, request, pk):
        propietario = self.get_object(pk)
        if propietario is None:
            return Response(
                {'error': 'Propietario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = PropietarioUpdateSerializer(propietario, data=request.data)
        if serializer.is_valid():
            propietario = serializer.save()
            return Response(PropietarioSerializer(propietario).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente propietario", request_body=PropietarioUpdateSerializer, responses={200: PropietarioSerializer})
    def patch(self, request, pk):
        propietario = self.get_object(pk)
        if propietario is None:
            return Response(
                {'error': 'Propietario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = PropietarioUpdateSerializer(propietario, data=request.data, partial=True)
        if serializer.is_valid():
            propietario = serializer.save()
            return Response(PropietarioSerializer(propietario).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Eliminar propietario", responses={200: openapi.Response('Eliminado')})
    def delete(self, request, pk):
        propietario = self.get_object(pk)
        if propietario is None:
            return Response(
                {'error': 'Propietario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        propietario.delete()
        return Response(
            {'mensaje': 'Propietario eliminado exitosamente'},
            status=status.HTTP_200_OK
        )

class ResultadosPropietarioView(APIView):
    permission_classes = [EsPropietario]  # propietario ve resultados de sus mascotas
    def get(self, request):
        propietario = request.user.propietario_perfil
        resultados = Resultado.objects.filter(solicitud__paciente__propietario=propietario)
        return Response(ResultadoSerializer(resultados, many=True).data)
