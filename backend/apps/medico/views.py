from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from config.pagination import StandardPagination
from .models import MedicoVeterinario
from .serializers import (
    MedicoVeterinarioSerializer,
    MedicoVeterinarioCreateSerializer,
    MedicoVeterinarioUpdateSerializer,
)


class MedicoVeterinarioListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        medicos = MedicoVeterinario.objects.all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(medicos, request)
        serializer = MedicoVeterinarioSerializer(pagina, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = MedicoVeterinarioCreateSerializer(data=request.data)
        if serializer.is_valid():
            medico = serializer.save()
            return Response(
                MedicoVeterinarioSerializer(medico).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MedicoVeterinarioDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return MedicoVeterinario.objects.get(pk=pk)
        except MedicoVeterinario.DoesNotExist:
            return None

    def get(self, request, pk):
        medico = self.get_object(pk)
        if medico is None:
            return Response({'error': 'Médico no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(MedicoVeterinarioSerializer(medico).data)

    def put(self, request, pk):
        medico = self.get_object(pk)
        if medico is None:
            return Response({'error': 'Médico no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MedicoVeterinarioUpdateSerializer(medico, data=request.data)
        if serializer.is_valid():
            medico = serializer.save()
            return Response(MedicoVeterinarioSerializer(medico).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        medico = self.get_object(pk)
        if medico is None:
            return Response({'error': 'Médico no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MedicoVeterinarioUpdateSerializer(medico, data=request.data, partial=True)
        if serializer.is_valid():
            medico = serializer.save()
            return Response(MedicoVeterinarioSerializer(medico).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        medico = self.get_object(pk)
        if medico is None:
            return Response({'error': 'Médico no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        medico.delete()
        return Response({'mensaje': 'Médico eliminado exitosamente'}, status=status.HTTP_200_OK)

