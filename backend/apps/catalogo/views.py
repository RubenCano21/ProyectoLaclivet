from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from config.pagination import StandardPagination
from .models import CatalogoExamen, Examen, Parametro, ValorReferencia
from .serializers import (
    CatalogoExamenSerializer, CatalogoExamenCreateSerializer, CatalogoExamenUpdateSerializer,
    ExamenSerializer, ExamenCreateSerializer, ExamenUpdateSerializer,
    ParametroSerializer, ParametroCreateSerializer, ParametroUpdateSerializer,
    ValorReferenciaSerializer, ValorReferenciaCreateSerializer, ValorReferenciaUpdateSerializer,
)


# ── CatalogoExamen ────────────────────────────────────────
class CatalogoExamenListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = CatalogoExamen.objects.all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(CatalogoExamenSerializer(pagina, many=True).data)

    def post(self, request):
        s = CatalogoExamenCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(CatalogoExamenSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class CatalogoExamenDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return CatalogoExamen.objects.get(pk=pk)
        except CatalogoExamen.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Catálogo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CatalogoExamenSerializer(obj).data)

    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Catálogo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = CatalogoExamenUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(CatalogoExamenSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Catálogo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = CatalogoExamenUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(CatalogoExamenSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Catálogo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Catálogo eliminado exitosamente'}, status=status.HTTP_200_OK)


# ── Examen ────────────────────────────────────────────────
class ExamenListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Examen.objects.select_related('catalogo').all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(ExamenSerializer(pagina, many=True).data)

    def post(self, request):
        s = ExamenCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(ExamenSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class ExamenDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Examen.objects.select_related('catalogo').get(pk=pk)
        except Examen.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Examen no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ExamenSerializer(obj).data)

    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Examen no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = ExamenUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(ExamenSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Examen no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = ExamenUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(ExamenSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Examen no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Examen eliminado exitosamente'}, status=status.HTTP_200_OK)


# ── Parametro ─────────────────────────────────────────────
class ParametroListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Parametro.objects.select_related('examen').all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(ParametroSerializer(pagina, many=True).data)

    def post(self, request):
        s = ParametroCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(ParametroSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class ParametroDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Parametro.objects.select_related('examen').get(pk=pk)
        except Parametro.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Parámetro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ParametroSerializer(obj).data)

    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Parámetro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = ParametroUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(ParametroSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Parámetro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = ParametroUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(ParametroSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Parámetro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Parámetro eliminado exitosamente'}, status=status.HTTP_200_OK)


# ── ValorReferencia ───────────────────────────────────────
class ValorReferenciaListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = ValorReferencia.objects.select_related('parametro').all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(ValorReferenciaSerializer(pagina, many=True).data)

    def post(self, request):
        s = ValorReferenciaCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(ValorReferenciaSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class ValorReferenciaDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return ValorReferencia.objects.select_related('parametro').get(pk=pk)
        except ValorReferencia.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Valor de referencia no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ValorReferenciaSerializer(obj).data)

    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Valor de referencia no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = ValorReferenciaUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(ValorReferenciaSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Valor de referencia no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = ValorReferenciaUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(ValorReferenciaSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Valor de referencia no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Valor de referencia eliminado exitosamente'}, status=status.HTTP_200_OK)
