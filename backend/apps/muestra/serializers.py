from rest_framework import serializers
from .models import Muestra, IncidenciaMuestra


# ── Muestra ───────────────────────────────────────────────
class MuestraSerializer(serializers.ModelSerializer):
    solicitud_codigo = serializers.CharField(source='solicitud.codigo', read_only=True)
    paciente_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Muestra
        fields = [
            'id', 'codigo', 'tipo_muestra', 'estado',
            'fecha_recepcion', 'observaciones',
            'paciente', 'paciente_nombre',
            'solicitud', 'solicitud_codigo',
        ]

    def get_paciente_nombre(self, obj):
        if obj.paciente:
            return obj.paciente.nombre
        return None


class MuestraCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Muestra
        fields = ['codigo', 'tipo_muestra', 'estado', 'solicitud', 'paciente', 'fecha_recepcion', 'observaciones']
        extra_kwargs = {'codigo': {'required': False}}

    def validate_codigo(self, value):
        if Muestra.objects.filter(codigo=value).exists():
            raise serializers.ValidationError("Ya existe una muestra con este código.")
        return value


class MuestraUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Muestra
        fields = ['tipo_muestra', 'estado', 'solicitud', 'paciente', 'fecha_recepcion', 'observaciones']


# ── IncidenciaMuestra ─────────────────────────────────────
class IncidenciaMuestraSerializer(serializers.ModelSerializer):
    muestra_codigo = serializers.CharField(source='muestra.codigo', read_only=True)

    class Meta:
        model = IncidenciaMuestra
        fields = ['id', 'fecha_registro', 'descripcion', 'muestra', 'muestra_codigo']


class IncidenciaMuestraCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidenciaMuestra
        fields = ['descripcion', 'muestra']
        extra_kwargs = {'muestra': {'required': True}}


class IncidenciaMuestraUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidenciaMuestra
        fields = ['descripcion', 'muestra']