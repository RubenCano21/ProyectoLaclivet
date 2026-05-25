from rest_framework import serializers
from .models import Cobro, SolicitudExamen, DetalleSolicitud


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

    class Meta:
        model = SolicitudExamen
        fields = [
            'id', 'codigo', 'fecha_solicitud', 'observaciones', 'estado',
            'cobro', 'historial_clinico', 'medico_veterinario',
            'medico_nombre', 'paciente_nombre',
        ]

    def get_medico_nombre(self, obj):
        if obj.medico_veterinario:
            return f"{obj.medico_veterinario.nombre} {obj.medico_veterinario.apellido}"
        return None

    def get_paciente_nombre(self, obj):
        if obj.historial_clinico and hasattr(obj.historial_clinico, 'paciente'):
            return obj.historial_clinico.paciente.nombre
        return None


class SolicitudExamenCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudExamen
        fields = ['codigo', 'observaciones', 'estado', 'cobro', 'historial_clinico', 'medico_veterinario']
        extra_kwargs = {'codigo': {'required': True}}

    def validate_codigo(self, value):
        if SolicitudExamen.objects.filter(codigo=value).exists():
            raise serializers.ValidationError("Ya existe una solicitud con este código.")
        return value


class SolicitudExamenUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudExamen
        fields = ['observaciones', 'estado', 'cobro', 'historial_clinico', 'medico_veterinario']


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
