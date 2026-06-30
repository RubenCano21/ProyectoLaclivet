from rest_framework import serializers
from .models import Muestra, IncidenciaMuestra


# ── Muestra ───────────────────────────────────────────────
class MuestraSerializer(serializers.ModelSerializer):
    solicitud_codigo = serializers.CharField(source='solicitud.codigo', read_only=True)

    class Meta:
        model = Muestra
        fields = ['id', 'codigo', 'tipo_muestra', 'estado', 'solicitud', 'solicitud_codigo']


class MuestraCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Muestra
        fields = ['codigo', 'tipo_muestra', 'estado', 'solicitud']
        extra_kwargs = {'codigo': {'required': True}}

    def validate_codigo(self, value):
        if Muestra.objects.filter(codigo=value).exists():
            raise serializers.ValidationError("Ya existe una muestra con este código.")
        return value


class MuestraUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Muestra
        fields = ['tipo_muestra', 'estado', 'solicitud']


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