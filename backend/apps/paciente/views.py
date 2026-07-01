from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.core.permissions import EsStaffInterno, tiene_rol
from config.pagination import StandardPagination
from .models import Especie, Raza, Paciente, AntecedentePaciente
from .serializers import (
    EspecieSerializer, EspecieCreateSerializer, EspecieUpdateSerializer,
    RazaSerializer, RazaCreateSerializer, RazaUpdateSerializer,
    PacienteSerializer, PacienteCreateSerializer, PacienteUpdateSerializer,
    AntecedentePacienteSerializer, AntecedentePacienteCreateSerializer, AntecedentePacienteUpdateSerializer,
    HistorialSolicitudSerializer,
)

_del_response = openapi.Response('Eliminado exitosamente')


class _ReferenciaBasePermissionMixin:
    """Especie/Raza son catálogos de referencia compartidos.
    Lectura: cualquier usuario autenticado. Escritura: solo staff interno."""

    def check_permissions(self, request):
        super().check_permissions(request)
        if request.method not in permissions.SAFE_METHODS:
            if not EsStaffInterno().has_permission(request, self):
                self.permission_denied(
                    request, message="Solo el personal interno puede modificar el catálogo."
                )


def _es_dueno(request, paciente):
    """True si el paciente pertenece al Propietario autenticado (o si el
    usuario no tiene rol Propietario, en cuyo caso no aplica esta restricción)."""
    if not tiene_rol(request.user, 'Propietario'):
        return True
    return bool(paciente and paciente.propietario and paciente.propietario.usuario_id == request.user.id)


# ── Especie ──────────────────────────────────────────────
class EspecieListCreateView(_ReferenciaBasePermissionMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_summary="Listar especies",
                         responses={200: EspecieSerializer(many=True)})
    def get(self, request):
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(Especie.objects.all(), request)
        return paginator.get_paginated_response(EspecieSerializer(pagina, many=True).data)

    @swagger_auto_schema(operation_summary="Crear especie",
                         request_body=EspecieCreateSerializer,
                         responses={201: EspecieSerializer})
    def post(self, request):
        s = EspecieCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(EspecieSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class EspecieDetailView(_ReferenciaBasePermissionMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Especie.objects.get(pk=pk)
        except Especie.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Obtener especie",
                         responses={200: EspecieSerializer})
    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Especie no encontrada'},
                            status=status.HTTP_404_NOT_FOUND)
        return Response(EspecieSerializer(obj).data)

    @swagger_auto_schema(operation_summary="Actualizar especie",
                         request_body=EspecieUpdateSerializer,
                         responses={200: EspecieSerializer})
    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Especie no encontrada'},
                            status=status.HTTP_404_NOT_FOUND)
        s = EspecieUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(EspecieSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente especie",
                         request_body=EspecieUpdateSerializer,
                         responses={200: EspecieSerializer})
    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Especie no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        s = EspecieUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(EspecieSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Eliminar especie", responses={200: _del_response})
    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Especie no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Especie eliminada exitosamente'}, status=status.HTTP_200_OK)


# ── Raza ─────────────────────────────────────────────────
class RazaListCreateView(_ReferenciaBasePermissionMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_summary="Listar razas", responses={200: RazaSerializer(many=True)})
    def get(self, request):
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(Raza.objects.select_related('especie').all(), request)
        return paginator.get_paginated_response(RazaSerializer(pagina, many=True).data)

    @swagger_auto_schema(operation_summary="Crear raza",
                         request_body=RazaCreateSerializer,
                         responses={201: RazaSerializer})
    def post(self, request):
        s = RazaCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(RazaSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class RazaDetailView(_ReferenciaBasePermissionMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Raza.objects.select_related('especie').get(pk=pk)
        except Raza.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Obtener raza", responses={200: RazaSerializer})
    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Raza no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        return Response(RazaSerializer(obj).data)

    @swagger_auto_schema(operation_summary="Actualizar raza",
                         request_body=RazaUpdateSerializer,
                         responses={200: RazaSerializer})
    def put(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Raza no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        s = RazaUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(RazaSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente raza",
                         request_body=RazaUpdateSerializer,
                         responses={200: RazaSerializer})
    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Raza no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        s = RazaUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(RazaSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Eliminar raza", responses={200: _del_response})
    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Raza no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Raza eliminada exitosamente'}, status=status.HTTP_200_OK)


# ── Paciente ──────────────────────────────────────────────
class PacienteListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_summary="Listar pacientes", responses={200: PacienteSerializer(many=True)})
    def get(self, request):
        qs = Paciente.objects.select_related('raza__especie', 'propietario__usuario').all()
        # Un Propietario solo puede ver sus propias mascotas (evita IDOR).
        if tiene_rol(request.user, 'Propietario'):
            qs = qs.filter(propietario__usuario=request.user)
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(PacienteSerializer(pagina, many=True).data)

    @swagger_auto_schema(operation_summary="Crear paciente",
                         request_body=PacienteCreateSerializer,
                         responses={201: PacienteSerializer})
    def post(self, request):
        # Registrar pacientes es una operación de recepción/veterinario, no del propietario.
        if not EsStaffInterno().has_permission(request, self):
            return Response(
                {'error': 'Solo el personal interno puede registrar pacientes.'},
                status=status.HTTP_403_FORBIDDEN
            )
        s = PacienteCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(PacienteSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class PacienteDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Paciente.objects.select_related('raza__especie', 'propietario__usuario').get(pk=pk)
        except Paciente.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Obtener paciente",
                         responses={200: PacienteSerializer})
    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Paciente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        if not _es_dueno(request, obj):
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        return Response(PacienteSerializer(obj).data)

    @swagger_auto_schema(operation_summary="Actualizar paciente",
                         request_body=PacienteUpdateSerializer,
                         responses={200: PacienteSerializer})
    def put(self, request, pk):
        if not EsStaffInterno().has_permission(request, self):
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Paciente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = PacienteUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(PacienteSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente paciente",
                         request_body=PacienteUpdateSerializer,
                         responses={200: PacienteSerializer})
    def patch(self, request, pk):
        if not EsStaffInterno().has_permission(request, self):
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Paciente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = PacienteUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(PacienteSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Eliminar paciente", responses={200: _del_response})
    def delete(self, request, pk):
        if not EsStaffInterno().has_permission(request, self):
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Paciente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Paciente eliminado exitosamente'}, status=status.HTTP_200_OK)


# ── Historial Dinámico (CU16) ─────────────────────────────
class PacienteHistorialView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Consultar historial clínico-laboratorial del paciente (CU16)",
        operation_description=(
            "Retorna el historial dinámico: datos del paciente, antecedentes persistentes "
            "y todas las solicitudes de examen vinculadas cronológicamente."
        ),
        responses={200: openapi.Response('Historial del paciente')}
    )
    def get(self, request, pk):
        try:
            paciente = Paciente.objects.select_related('raza__especie', 'propietario__usuario').get(pk=pk)
        except Paciente.DoesNotExist:
            return Response({'error': 'Paciente no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if not _es_dueno(request, paciente):
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)

        # Antecedentes persistentes
        antecedentes = paciente.antecedentes.select_related('registrado_por').all()

        # Historial dinámico: todas las solicitudes del paciente
        from apps.recepcion.models import SolicitudExamen
        solicitudes = SolicitudExamen.objects.filter(paciente=paciente).select_related(
            'medico_veterinario', 'cobro'
        ).prefetch_related('detalles__examen').order_by('-fecha_solicitud')

        return Response({
            'paciente': PacienteSerializer(paciente).data,
            'antecedentes': AntecedentePacienteSerializer(antecedentes, many=True).data,
            'total_visitas': solicitudes.count(),
            'solicitudes': HistorialSolicitudSerializer(solicitudes, many=True).data,
        })


# ── AntecedentePaciente ───────────────────────────────────
class AntecedentePacienteListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_summary="Listar antecedentes de pacientes",
                         responses={200: AntecedentePacienteSerializer(many=True)})
    def get(self, request):
        qs = AntecedentePaciente.objects.select_related('paciente__propietario__usuario', 'registrado_por').all()
        # Un Propietario solo ve antecedentes de sus propias mascotas.
        if tiene_rol(request.user, 'Propietario'):
            qs = qs.filter(paciente__propietario__usuario=request.user)
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(AntecedentePacienteSerializer(pagina, many=True).data)

    @swagger_auto_schema(operation_summary="Registrar antecedente de paciente",
                         request_body=AntecedentePacienteCreateSerializer,
                         responses={201: AntecedentePacienteSerializer})
    def post(self, request):
        if not EsStaffInterno().has_permission(request, self):
            return Response(
                {'error': 'Solo el personal interno puede registrar antecedentes.'},
                status=status.HTTP_403_FORBIDDEN
            )
        s = AntecedentePacienteCreateSerializer(data=request.data)
        if s.is_valid():
            return Response(AntecedentePacienteSerializer(s.save()).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class AntecedentePacienteDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return AntecedentePaciente.objects.select_related(
                'paciente__propietario__usuario', 'registrado_por'
            ).get(pk=pk)
        except AntecedentePaciente.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Obtener antecedente",
                         responses={200: AntecedentePacienteSerializer})
    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Antecedente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        if not _es_dueno(request, obj.paciente):
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        return Response(AntecedentePacienteSerializer(obj).data)

    @swagger_auto_schema(operation_summary="Actualizar antecedente",
                         request_body=AntecedentePacienteUpdateSerializer,
                         responses={200: AntecedentePacienteSerializer})
    def put(self, request, pk):
        if not EsStaffInterno().has_permission(request, self):
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Antecedente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = AntecedentePacienteUpdateSerializer(obj, data=request.data)
        if s.is_valid():
            return Response(AntecedentePacienteSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Actualizar parcialmente antecedente",
                         request_body=AntecedentePacienteUpdateSerializer,
                         responses={200: AntecedentePacienteSerializer})
    def patch(self, request, pk):
        if not EsStaffInterno().has_permission(request, self):
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Antecedente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        s = AntecedentePacienteUpdateSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            return Response(AntecedentePacienteSerializer(s.save()).data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Eliminar antecedente", responses={200: _del_response})
    def delete(self, request, pk):
        if not EsStaffInterno().has_permission(request, self):
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Antecedente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Antecedente eliminado exitosamente'}, status=status.HTTP_200_OK)
