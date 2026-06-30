from rest_framework import serializers
from .models import Cobro, SolicitudExamen, DetalleSolicitud
from apps.catalogo.models import Examen
from apps.muestra.models import Muestra


class CobroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cobro
        fields = ['id', 'monto_total', 'metodo_pago', 'fecha']


class CobroCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cobro
        fields = ['monto_total', 'metodo_pago', 'fecha']
        extra_kwargs = {
            'monto_total': {'required': True},
            'metodo_pago': {'required': True},
            'fecha': {'required': True},
        }

    def validate_monto_total(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("El monto total debe ser mayor a 0.")
        return value


class CobroUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cobro
        fields = ['monto_total', 'metodo_pago', 'fecha']

    def validate_monto_total(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("El monto total debe ser mayor a 0.")
        return value


# ── SolicitudExamen ───────────────────────────────────────
class SolicitudExamenSerializer(serializers.ModelSerializer):
    medico_nombre = serializers.SerializerMethodField()
    paciente_nombre = serializers.SerializerMethodField()
    propietario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = SolicitudExamen
        fields = [
            'id', 'codigo', 'fecha_solicitud', 'observaciones', 'estado',
            'cobro', 'paciente', 'medico_veterinario',
            'medico_nombre', 'paciente_nombre', 'propietario_nombre',
        ]

    def get_medico_nombre(self, obj):
        if obj.medico_veterinario:
            return f"{obj.medico_veterinario.usuario.first_name} {obj.medico_veterinario.usuario.last_name}"
        return None

    def get_paciente_nombre(self, obj):
        if obj.paciente:
            return obj.paciente.nombre
        return None

    def get_propietario_nombre(self, obj):
        if obj.paciente and obj.paciente.propietario:
            p = obj.paciente.propietario
            return f"{p.usuario.first_name} {p.usuario.last_name}"
        return None


class SolicitudExamenCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudExamen
        fields = ['codigo', 'observaciones', 'estado', 'cobro', 'paciente', 'medico_veterinario']
        extra_kwargs = {'codigo': {'required': True}}

    def validate_codigo(self, value):
        if SolicitudExamen.objects.filter(codigo=value).exists():
            raise serializers.ValidationError("Ya existe una solicitud con este código.")
        return value


class SolicitudExamenUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudExamen
        fields = ['observaciones', 'estado', 'cobro', 'paciente', 'medico_veterinario']


# ── DetalleSolicitud ──────────────────────────────────────
class DetalleSolicitudSerializer(serializers.ModelSerializer):
    examen_nombre = serializers.CharField(source='examen.nombre_examen', read_only=True)
    solicitud_codigo = serializers.CharField(source='solicitud.codigo', read_only=True)

    class Meta:
        model = DetalleSolicitud
        fields = ['id', 'precio_aplicado', 'solicitud', 'solicitud_codigo', 'examen', 'examen_nombre']


class DetalleSolicitudCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleSolicitud
        fields = ['precio_aplicado', 'solicitud', 'examen']
        extra_kwargs = {'solicitud': {'required': True}}


class DetalleSolicitudUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleSolicitud
        fields = ['precio_aplicado', 'solicitud', 'examen']


class MuestraMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Muestra
        fields = ['id', 'codigo', 'tipo_muestra', 'estado']


class DetalleSolicitudConMuestraSerializer(serializers.ModelSerializer):
    """Variante de DetalleSolicitudSerializer con info de muestra y resultado.
    La muestra se obtiene vía OrdenExamen.muestra (no hay FK directa Muestra->DetalleSolicitud)."""
    examen_nombre = serializers.CharField(source='examen.nombre_examen', read_only=True)
    requiere_muestra = serializers.BooleanField(source='examen.requiere_muestra', read_only=True)
    muestra = serializers.SerializerMethodField()
    tiene_resultado = serializers.SerializerMethodField()
    estado_resultado = serializers.SerializerMethodField()

    class Meta:
        model = DetalleSolicitud
        fields = [
            'id', 'precio_aplicado', 'examen', 'examen_nombre',
            'requiere_muestra', 'muestra', 'tiene_resultado', 'estado_resultado',
        ]

    def get_muestra(self, obj):
        orden_examen = getattr(obj, 'orden_examen', None)
        if orden_examen and orden_examen.muestra:
            return MuestraMiniSerializer(orden_examen.muestra).data
        return None

    def get_tiene_resultado(self, obj):
        orden_examen = getattr(obj, 'orden_examen', None)
        return bool(orden_examen and orden_examen.resultados.exists())

    def get_estado_resultado(self, obj):
        orden_examen = getattr(obj, 'orden_examen', None)
        return orden_examen.estado if orden_examen else None


class SolicitudExamenFullDetailSerializer(serializers.ModelSerializer):
    """Detalle completo de una solicitud, con sus DetalleSolicitud + muestras + estado de resultado.
    Se usa para la vista de detalle/lista que ve Recepción/Veterinario."""
    detalles = DetalleSolicitudConMuestraSerializer(many=True, read_only=True)
    paciente_nombre = serializers.CharField(source='paciente.nombre', read_only=True)
    medico_nombre = serializers.SerializerMethodField()

    class Meta:
        model = SolicitudExamen
        fields = [
            'id', 'codigo', 'fecha_solicitud', 'observaciones', 'estado',
            'cobro', 'paciente', 'paciente_nombre', 'medico_veterinario',
            'medico_nombre', 'detalles',
        ]

    def get_medico_nombre(self, obj):
        if obj.medico_veterinario and obj.medico_veterinario.usuario:
            u = obj.medico_veterinario.usuario
            return f"{u.first_name} {u.last_name}"
        return None


class CrearSolicitudConExamenesSerializer(serializers.Serializer):
    """Input para crear una solicitud junto con sus exámenes en un solo paso,
    delegando a services.crear_solicitud_con_muestras (verifica muestras)."""
    paciente = serializers.IntegerField()
    medico_veterinario = serializers.IntegerField(required=False, allow_null=True)
    examenes_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    observaciones = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_examenes_ids(self, value):
        existentes = set(Examen.objects.filter(id__in=value).values_list('id', flat=True))
        faltantes = set(value) - existentes
        if faltantes:
            raise serializers.ValidationError(f"Exámenes no encontrados: {faltantes}")
        return value


class CambiarEstadoSolicitudSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=SolicitudExamen.ESTADO_CHOICES)
