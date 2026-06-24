from apps.core.permissions import EsStaffInterno
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from config.pagination import StandardPagination
from .models import CatalogoExamen, Examen, Parametro, ValorReferencia
from .serializers import (
    CatalogoExamenSerializer, CatalogoExamenCreateSerializer, CatalogoExamenUpdateSerializer,
    ExamenSerializer, ExamenCreateSerializer, ExamenUpdateSerializer,
    ParametroSerializer, ParametroCreateSerializer, ParametroUpdateSerializer,
    ValorReferenciaSerializer, ValorReferenciaCreateSerializer, ValorReferenciaUpdateSerializer,
)

_del_response = openapi.Response('Eliminado exitosamente')


def _permisos_lectura_o_staff(request):
    """
    GET/HEAD/OPTIONS: cualquier usuario autenticado puede ver.
    POST/PUT/PATCH/DELETE: solo staff interno (Administrador, Veterinario, Recepcionista)
    puede gestionar.
    """
    if request.method in permissions.SAFE_METHODS:
        return permissions.IsAuthenticated().has_permission(request, None)
    return EsStaffInterno().has_permission(request, None)


class _CatalogoBasePermissionMixin:
    """
    Mixin que aplica la regla: lectura abierta a cualquier autenticado,
    escritura restringida a EsStaffInterno. No declarar permission_classes
    en las subclases que usen este mixin (se deja IsAuthenticated solo
    como base para que DRF no bloquee antes de tiempo).
    """

    def check_permissions(self, request):
        super().check_permissions(request)
        if not _permisos_lectura_o_staff(request):
            self.permission_denied(
                request,
                message="No tiene permiso para realizar esta acción.",
            )


# ── CatalogoExamen ────────────────────────────────────────
class CatalogoExamenListCreateView(_CatalogoBasePermissionMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_summary="Listar catálogos de examen", responses={200: CatalogoExamenSerializer(many=True)})
    def get(self, request):
        qs = CatalogoExamen.objects.all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(CatalogoExamenSerializer(pagina, many=True).data)

    @swagger_auto_schema(operation_summary="Crear catálogo de examen", request_body=CatalogoExamenCreateSerializer, responses={201: CatalogoExamenSerializer})
    def post(self, request):
        s = CatalogoExamenCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(CatalogoExamenSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class CatalogoExamenDetailView(_CatalogoBasePermissionMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return CatalogoExamen.objects.get(pk=pk)
        except CatalogoExamen.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Obtener catálogo de examen", responses={200: CatalogoExamenSerializer})
    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Catálogo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CatalogoExamenSerializer(obj).data)

    @swagger_auto_schema(operation_summary="Actualizar catálogo de examen", request_body=CatalogoExamenUpdateSerializer, responses={200: CatalogoExamenSerializer})
    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Catálogo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = CatalogoExamenUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(CatalogoExamenSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente catálogo", request_body=CatalogoExamenUpdateSerializer, responses={200: CatalogoExamenSerializer})
    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Catálogo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = CatalogoExamenUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(CatalogoExamenSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Eliminar catálogo de examen", responses={200: _del_response})
    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Catálogo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Catálogo eliminado exitosamente'}, status=status.HTTP_200_OK)


# ── Examen ────────────────────────────────────────────────
class ExamenListCreateView(_CatalogoBasePermissionMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_summary="Listar exámenes", responses={200: ExamenSerializer(many=True)})
    def get(self, request):
        qs = Examen.objects.select_related('catalogo').all()
        catalogo_id = request.query_params.get('catalogo')
        if catalogo_id:
            qs = qs.filter(catalogo_id=catalogo_id)
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(ExamenSerializer(pagina, many=True).data)

    @swagger_auto_schema(operation_summary="Crear examen", request_body=ExamenCreateSerializer, responses={201: ExamenSerializer})
    def post(self, request):
        s = ExamenCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(ExamenSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class ExamenDetailView(_CatalogoBasePermissionMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Examen.objects.select_related('catalogo').get(pk=pk)
        except Examen.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Obtener examen", responses={200: ExamenSerializer})
    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Examen no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ExamenSerializer(obj).data)

    @swagger_auto_schema(operation_summary="Actualizar examen", request_body=ExamenUpdateSerializer, responses={200: ExamenSerializer})
    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Examen no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = ExamenUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(ExamenSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente examen", request_body=ExamenUpdateSerializer, responses={200: ExamenSerializer})
    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Examen no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = ExamenUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(ExamenSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Eliminar examen", responses={200: _del_response})
    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Examen no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Examen eliminado exitosamente'}, status=status.HTTP_200_OK)


# ── Parametro ─────────────────────────────────────────────
class ParametroListCreateView(_CatalogoBasePermissionMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_summary="Listar parámetros", responses={200: ParametroSerializer(many=True)})
    def get(self, request):
        qs = Parametro.objects.select_related('examen').all()
        examen_id = request.query_params.get('examen')
        if examen_id:
            qs = qs.filter(examen_id=examen_id)
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(ParametroSerializer(pagina, many=True).data)

    @swagger_auto_schema(operation_summary="Crear parámetro", request_body=ParametroCreateSerializer, responses={201: ParametroSerializer})
    def post(self, request):
        s = ParametroCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(ParametroSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class ParametroDetailView(_CatalogoBasePermissionMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Parametro.objects.select_related('examen').get(pk=pk)
        except Parametro.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Obtener parámetro", responses={200: ParametroSerializer})
    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Parámetro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ParametroSerializer(obj).data)

    @swagger_auto_schema(operation_summary="Actualizar parámetro", request_body=ParametroUpdateSerializer, responses={200: ParametroSerializer})
    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Parámetro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = ParametroUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(ParametroSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente parámetro", request_body=ParametroUpdateSerializer, responses={200: ParametroSerializer})
    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Parámetro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = ParametroUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(ParametroSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Eliminar parámetro", responses={200: _del_response})
    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Parámetro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Parámetro eliminado exitosamente'}, status=status.HTTP_200_OK)


# ── ValorReferencia ───────────────────────────────────────
class ValorReferenciaListCreateView(_CatalogoBasePermissionMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_summary="Listar valores de referencia", responses={200: ValorReferenciaSerializer(many=True)})
    def get(self, request):
        qs = ValorReferencia.objects.select_related('parametro').all()
        parametro_id = request.query_params.get('parametro')
        if parametro_id:
            qs = qs.filter(parametro_id=parametro_id)
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(ValorReferenciaSerializer(pagina, many=True).data)

    @swagger_auto_schema(operation_summary="Crear valor de referencia", request_body=ValorReferenciaCreateSerializer, responses={201: ValorReferenciaSerializer})
    def post(self, request):
        s = ValorReferenciaCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(ValorReferenciaSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class ValorReferenciaDetailView(_CatalogoBasePermissionMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return ValorReferencia.objects.select_related('parametro').get(pk=pk)
        except ValorReferencia.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Obtener valor de referencia", responses={200: ValorReferenciaSerializer})
    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Valor de referencia no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ValorReferenciaSerializer(obj).data)

    @swagger_auto_schema(operation_summary="Actualizar valor de referencia", request_body=ValorReferenciaUpdateSerializer, responses={200: ValorReferenciaSerializer})
    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Valor de referencia no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = ValorReferenciaUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(ValorReferenciaSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente valor de referencia", request_body=ValorReferenciaUpdateSerializer, responses={200: ValorReferenciaSerializer})
    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Valor de referencia no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = ValorReferenciaUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(ValorReferenciaSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Eliminar valor de referencia", responses={200: _del_response})
    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Valor de referencia no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Valor de referencia eliminado exitosamente'}, status=status.HTTP_200_OK)