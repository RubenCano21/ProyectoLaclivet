from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from config.pagination import StandardPagination
from .models import Cobro
from .serializers import (
    CobroSerializer,
    CobroCreateSerializer,
    CobroUpdateSerializer,
)


class CobroListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cobros = Cobro.objects.all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(cobros, request)
        serializer = CobroSerializer(pagina, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = CobroCreateSerializer(data=request.data)
        if serializer.is_valid():
            cobro = serializer.save()
            return Response(CobroSerializer(cobro).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CobroDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Cobro.objects.get(pk=pk)
        except Cobro.DoesNotExist:
            return None

    def get(self, request, pk):
        cobro = self.get_object(pk)
        if cobro is None:
            return Response({'error': 'Cobro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CobroSerializer(cobro).data)

    def put(self, request, pk):
        cobro = self.get_object(pk)
        if cobro is None:
            return Response({'error': 'Cobro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CobroUpdateSerializer(cobro, data=request.data)
        if serializer.is_valid():
            cobro = serializer.save()
            return Response(CobroSerializer(cobro).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        cobro = self.get_object(pk)
        if cobro is None:
            return Response({'error': 'Cobro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CobroUpdateSerializer(cobro, data=request.data, partial=True)
        if serializer.is_valid():
            cobro = serializer.save()
            return Response(CobroSerializer(cobro).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        cobro = self.get_object(pk)
        if cobro is None:
            return Response({'error': 'Cobro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        cobro.delete()
        return Response({'mensaje': 'Cobro eliminado exitosamente'}, status=status.HTTP_200_OK)

