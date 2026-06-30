from apps.core.permissions import EsStaffInterno
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from config.pagination import StandardPagination
from .models import CatalogoExamen, Examen, Parametro, ValorReferencia, OrdenExamen, OrdenTrabajo
from .serializers import (
    CatalogoExamenSerializer, CatalogoExamenCreateSerializer, CatalogoExamenUpdateSerializer,
    ExamenSerializer, ExamenCreateSerializer, ExamenUpdateSerializer,
    ParametroSerializer, ParametroCreateSerializer, ParametroUpdateSerializer,
    ValorReferenciaSerializer, ValorReferenciaCreateSerializer, ValorReferenciaUpdateSerializer,
    OrdenExamenResultadosUpdateSerializer, OrdenExamenSerializer, OrdenTrabajoCreateSerializer,
    OrdenTrabajoSerializer, ExamenDetalleSerializer,
    OrdenExamenFullDetailSerializer, RegistrarResultadoOrdenExamenSerializer,
)

_del_response = openapi.Response('Eliminado exitosamente')


def _permisos_lectura_o_staff(request):
    if request.method in permissions.SAFE_METHODS:
        return permissions.IsAuthenticated().has_permission(request, None)
    return EsStaffInterno().has_permission(request, None)


class _CatalogoBasePermissionMixin:

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

    @swagger_auto_schema(operation_summary="Listar catálogos de examen",
                         responses={200: CatalogoExamenSerializer(many=True)})
    def get(self, request):
        qs = CatalogoExamen.objects.all()
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(CatalogoExamenSerializer(pagina, many=True).data)

    @swagger_auto_schema(operation_summary="Crear catálogo de examen", request_body=CatalogoExamenCreateSerializer,
                         responses={201: CatalogoExamenSerializer})
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

    @swagger_auto_schema(operation_summary="Obtener catálogo de examen",
                         responses={200: CatalogoExamenSerializer})
    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Catálogo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CatalogoExamenSerializer(obj).data)

    @swagger_auto_schema(operation_summary="Actualizar catálogo de examen",
                         request_body=CatalogoExamenUpdateSerializer,
                         responses={200: CatalogoExamenSerializer})
    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Catálogo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = CatalogoExamenUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(CatalogoExamenSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente catálogo",
                         request_body=CatalogoExamenUpdateSerializer,
                         responses={200: CatalogoExamenSerializer})
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

    @swagger_auto_schema(operation_summary="Crear examen", request_body=ExamenCreateSerializer,
                         responses={201: ExamenSerializer})
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

    @swagger_auto_schema(operation_summary="Actualizar examen", request_body=ExamenUpdateSerializer,
                         responses={200: ExamenSerializer})
    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Examen no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = ExamenUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(ExamenSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente examen", request_body=ExamenUpdateSerializer,
                         responses={200: ExamenSerializer})
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

    @swagger_auto_schema(operation_summary="Crear parámetro", request_body=ParametroCreateSerializer,
                         responses={201: ParametroSerializer})
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

    @swagger_auto_schema(operation_summary="Actualizar parámetro", request_body=ParametroUpdateSerializer,
                         responses={200: ParametroSerializer})
    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Parámetro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = ParametroUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(ParametroSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente parámetro", request_body=ParametroUpdateSerializer,
                         responses={200: ParametroSerializer})
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

    @swagger_auto_schema(operation_summary="Listar valores de referencia",
                         responses={200: ValorReferenciaSerializer(many=True)})
    def get(self, request):
        qs = ValorReferencia.objects.select_related('parametro').all()
        parametro_id = request.query_params.get('parametro')
        if parametro_id:
            qs = qs.filter(parametro_id=parametro_id)
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(ValorReferenciaSerializer(pagina, many=True).data)

    @swagger_auto_schema(operation_summary="Crear valor de referencia",
                         request_body=ValorReferenciaCreateSerializer, responses={201: ValorReferenciaSerializer})
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


# ── Examen: plantilla agrupada (solo lectura) ────────────────────────────
class ExamenPlantillaView(_CatalogoBasePermissionMixin, APIView):
    """GET /examenes/<pk>/plantilla/
    Devuelve el examen con sus parámetros agrupados por 'grupo' y sus
    valores de referencia anidados. Es lo que consume el formulario de
    captura de resultados (hemograma, etc.) en el front."""
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Examen.objects.prefetch_related(
                'parametros__valores_referencia'
            ).select_related('catalogo').get(pk=pk)
        except Examen.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Plantilla agrupada del examen (parámetros + V. Ref.)",
                         responses={200: ExamenDetalleSerializer})
    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Examen no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ExamenDetalleSerializer(obj).data)


# ── OrdenTrabajo ──────────────────────────────────────────
class OrdenTrabajoListCreateView(_CatalogoBasePermissionMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_summary="Listar órdenes de trabajo",
                         responses={200: OrdenTrabajoSerializer(many=True)})
    def get(self, request):
        qs = OrdenTrabajo.objects.select_related('paciente').all()
        paciente_id = request.query_params.get('paciente')
        estado = request.query_params.get('estado')
        if paciente_id:
            qs = qs.filter(paciente_id=paciente_id)
        if estado:
            qs = qs.filter(estado=estado)
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(OrdenTrabajoSerializer(pagina, many=True).data)

    @swagger_auto_schema(operation_summary="Crear orden de trabajo", request_body=OrdenTrabajoCreateSerializer,
                         responses={201: OrdenTrabajoSerializer})
    def post(self, request):
        s = OrdenTrabajoCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(OrdenTrabajoSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class OrdenTrabajoDetailView(_CatalogoBasePermissionMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return OrdenTrabajo.objects.select_related('paciente').get(pk=pk)
        except OrdenTrabajo.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Obtener orden de trabajo", responses={200: OrdenTrabajoSerializer})
    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Orden de trabajo no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrdenTrabajoSerializer(obj).data)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente orden de trabajo",
                         request_body=OrdenTrabajoCreateSerializer, responses={200: OrdenTrabajoSerializer})
    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Orden de trabajo no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        s = OrdenTrabajoCreateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(OrdenTrabajoSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Eliminar orden de trabajo", responses={200: _del_response})
    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Orden de trabajo no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Orden de trabajo eliminada exitosamente'}, status=status.HTTP_200_OK)


# ── OrdenExamen (examen agregado a una orden) ────────────
class OrdenExamenListCreateView(_CatalogoBasePermissionMixin, APIView):
    """Asocia un Examen del catálogo (y opcionalmente una Muestra) a una OrdenTrabajo.
    El cuerpo de creación es minimal; los resultados se cargan después con
    OrdenExamenResultadosView."""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Listar exámenes de una orden",
        manual_parameters=[openapi.Parameter('orden', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                             description="Filtrar por orden de trabajo")],
        responses={200: OrdenExamenSerializer(many=True)},
    )
    def get(self, request):
        qs = OrdenExamen.objects.select_related('examen', 'orden', 'muestra').prefetch_related('resultados')
        orden_id = request.query_params.get('orden')
        if orden_id:
            qs = qs.filter(orden_id=orden_id)
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(OrdenExamenSerializer(pagina, many=True).data)

    @swagger_auto_schema(
        operation_summary="Agregar examen a una orden",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['orden', 'examen'],
            properties={
                'orden': openapi.Schema(type=openapi.TYPE_INTEGER),
                'examen': openapi.Schema(type=openapi.TYPE_INTEGER),
                'muestra': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
        responses={201: OrdenExamenSerializer},
    )
    def post(self, request):
        orden_id = request.data.get('orden')
        examen_id = request.data.get('examen')
        if not orden_id or not examen_id:
            return Response({'error': 'orden y examen son obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            orden = OrdenTrabajo.objects.get(pk=orden_id)
            examen = Examen.objects.get(pk=examen_id)
        except (OrdenTrabajo.DoesNotExist, Examen.DoesNotExist):
            return Response({'error': 'Orden o examen no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if OrdenExamen.objects.filter(orden=orden, examen=examen).exists():
            return Response({'error': 'Este examen ya fue agregado a la orden'}, status=status.HTTP_400_BAD_REQUEST)

        obj = OrdenExamen.objects.create(orden=orden, examen=examen, muestra_id=request.data.get('muestra'))
        return Response(OrdenExamenSerializer(obj).data, status=status.HTTP_201_CREATED)


class OrdenExamenDetailView(_CatalogoBasePermissionMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return OrdenExamen.objects.select_related('examen', 'orden__paciente__raza__especie',
                                                      'muestra').prefetch_related('resultados').get(pk=pk)
        except OrdenExamen.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Obtener examen de orden (con resultados)",
                         responses={200: OrdenExamenSerializer})
    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Registro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrdenExamenSerializer(obj).data)

    @swagger_auto_schema(operation_summary="Eliminar examen de orden", responses={200: _del_response})
    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Registro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Examen eliminado de la orden'}, status=status.HTTP_200_OK)


class OrdenExamenResultadosView(_CatalogoBasePermissionMixin, APIView):
    """PATCH /orden-examenes/<pk>/resultados/
    Endpoint dedicado para guardar/actualizar los resultados de un examen
    (parámetros + observaciones/alteraciones/diagnóstico/pronóstico).
    Calcula automáticamente BAJO/NORMAL/ALTO según la especie del paciente."""
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return OrdenExamen.objects.select_related('orden__paciente__raza__especie').get(pk=pk)
        except OrdenExamen.DoesNotExist:
            return None

    @swagger_auto_schema(
        operation_summary="Guardar resultados de un examen",
        request_body=OrdenExamenResultadosUpdateSerializer,
        responses={200: OrdenExamenSerializer},
    )
    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Registro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = OrdenExamenResultadosUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            actualizado = s.save()
            return Response(OrdenExamenSerializer(actualizado).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

class OrdenExamenFullDetailView(APIView):
    """Reemplaza al antiguo ResultadoDetailView (muestra). Misma lógica de permisos:
    staff interno ve todo, médico externo solo lo suyo, propietario solo de sus mascotas."""
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return OrdenExamen.objects.select_related(
                'examen', 'orden__paciente__raza__especie', 'muestra',
                'detalle_solicitud__solicitud__medico_veterinario__usuario',
                'veterinario_responsable',
            ).prefetch_related('resultados__parametro').get(pk=pk)
        except OrdenExamen.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Detalle completo del resultado (con permisos)",
                         responses={200: OrdenExamenFullDetailSerializer})
    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Registro no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if hasattr(user, 'rol') and user.rol and user.rol.nombre in ('Administrador', 'Veterinario', 'Recepcionista'):
            return Response(OrdenExamenFullDetailSerializer(obj).data)

        if hasattr(user, 'medico_perfil'):
            if obj.medico_solicitante != user.medico_perfil:
                return Response({'error': 'No autorizado'}, status=403)
            return Response(OrdenExamenFullDetailSerializer(obj).data)

        if hasattr(user, 'propietario_perfil'):
            if not obj.paciente or obj.paciente.propietario != user.propietario_perfil:
                return Response({'error': 'No autorizado'}, status=403)
            return Response(OrdenExamenFullDetailSerializer(obj).data)

        return Response({'error': 'No autorizado'}, status=403)


class RegistrarResultadoOrdenExamenView(APIView):
    """Solo Veterinario interno registra resultados (RF8: captura de resultados)."""
    permission_classes = [IsAuthenticated, EsStaffInterno]  # ajustar a EsVeterinario si quieres restringir más

    def get_object(self, pk):
        try:
            return OrdenExamen.objects.select_related('orden__paciente__raza__especie').get(pk=pk)
        except OrdenExamen.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Registrar resultados (Veterinario)",
                         request_body=RegistrarResultadoOrdenExamenSerializer,
                         responses={200: OrdenExamenFullDetailSerializer})
    def post(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Registro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = RegistrarResultadoOrdenExamenSerializer(obj, data=request.data, context={'request': request})
        if s.is_valid():
            actualizado = s.save()
            return Response(OrdenExamenFullDetailSerializer(actualizado).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class OrdenExamenGenerarPdfView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return OrdenExamen.objects.select_related(
                'examen', 'orden__paciente__raza__especie',
                'detalle_solicitud__solicitud__medico_veterinario__usuario',
                'veterinario_responsable',
            ).prefetch_related('resultados__parametro').get(pk=pk)
        except OrdenExamen.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Generar PDF del resultado", responses={200: OrdenExamenFullDetailSerializer})
    def post(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Registro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        if obj.estado not in ('completado', 'validado'):
            return Response(
                {'error': 'El examen debe estar completado antes de generar el PDF.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Import lazy: solo se carga cuando realmente se usa el endpoint
        from apps.muestra.pdf import generar_pdf_orden_examen
        obj = generar_pdf_orden_examen(obj)
        return Response(OrdenExamenFullDetailSerializer(obj).data)