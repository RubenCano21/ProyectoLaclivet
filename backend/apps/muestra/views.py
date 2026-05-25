from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from config.pagination import StandardPagination
from .models import Muestra, IncidenciaMuestra
from .serializers import (
    MuestraSerializer, MuestraCreateSerializer, MuestraUpdateSerializer,
    IncidenciaMuestraSerializer, IncidenciaMuestraCreateSerializer, IncidenciaMuestraUpdateSerializer,
)


class MuestraListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Muestra.objects.select_related('solicitud').all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(MuestraSerializer(pagina, many=True).data)

    def post(self, request):
        s = MuestraCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(MuestraSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class MuestraDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Muestra.objects.select_related('solicitud').get(pk=pk)
        except Muestra.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Muestra no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        return Response(MuestraSerializer(obj).data)

    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Muestra no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        s = MuestraUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(MuestraSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Muestra no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        s = MuestraUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(MuestraSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Muestra no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Muestra eliminada exitosamente'}, status=status.HTTP_200_OK)


# ── IncidenciaMuestra ─────────────────────────────────────
class IncidenciaMuestraListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = IncidenciaMuestra.objects.select_related('muestra').all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(IncidenciaMuestraSerializer(pagina, many=True).data)

    def post(self, request):
        s = IncidenciaMuestraCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(IncidenciaMuestraSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class IncidenciaMuestraDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return IncidenciaMuestra.objects.select_related('muestra').get(pk=pk)
        except IncidenciaMuestra.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Incidencia no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        return Response(IncidenciaMuestraSerializer(obj).data)

    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Incidencia no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        s = IncidenciaMuestraUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(IncidenciaMuestraSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Incidencia no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        s = IncidenciaMuestraUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(IncidenciaMuestraSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Incidencia no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Incidencia eliminada exitosamente'}, status=status.HTTP_200_OK)
