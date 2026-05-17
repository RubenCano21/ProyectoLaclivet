from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Propietario
from .serializers import (
    PropietarioSerializer,
    PropietarioCreateSerializer,
    PropietarioUpdateSerializer,
)


class PropietarioListCreateView(APIView):
    """Lista todos los propietarios o crea uno nuevo"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        propietarios = Propietario.objects.all().order_by('apellido', 'nombre')
        serializer = PropietarioSerializer(propietarios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Propietario.objects.get(pk=pk)
        except Propietario.DoesNotExist:
            return None

    def get(self, request, pk):
        propietario = self.get_object(pk)
        if propietario is None:
            return Response(
                {'error': 'Propietario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = PropietarioSerializer(propietario)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

