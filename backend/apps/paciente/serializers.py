from rest_framework import serializers
from .models import Especie, Raza, HistorialClinico


# ── Especie ──────────────────────────────────────────────
class EspecieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especie
        fields = ['id', 'nombre']


class EspecieCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especie
        fields = ['nombre']
        extra_kwargs = {'nombre': {'required': True}}

    def validate_nombre(self, value):
        if Especie.objects.filter(nombre__iexact=value).exists():
            raise serializers.ValidationError("Ya existe una especie con este nombre.")
        return value


class EspecieUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especie
        fields = ['nombre']

    def validate_nombre(self, value):
        if Especie.objects.exclude(pk=self.instance.pk).filter(nombre__iexact=value).exists():
            raise serializers.ValidationError("Ya existe una especie con este nombre.")
        return value


# ── Raza ─────────────────────────────────────────────────
class RazaSerializer(serializers.ModelSerializer):
    especie_nombre = serializers.CharField(source='especie.nombre', read_only=True)

    class Meta:
        model = Raza
        fields = ['id', 'nombre', 'descripcion', 'especie', 'especie_nombre']


class RazaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Raza
        fields = ['nombre', 'descripcion', 'especie']
        extra_kwargs = {
            'nombre': {'required': True},
            'especie': {'required': True},
        }

    def validate(self, attrs):
        if Raza.objects.filter(nombre__iexact=attrs['nombre'], especie=attrs['especie']).exists():
            raise serializers.ValidationError("Ya existe una raza con este nombre para esta especie.")
        return attrs


class RazaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Raza
        fields = ['nombre', 'descripcion', 'especie']

    def validate(self, attrs):
        nombre = attrs.get('nombre', self.instance.nombre)
        especie = attrs.get('especie', self.instance.especie)
        if Raza.objects.exclude(pk=self.instance.pk).filter(nombre__iexact=nombre, especie=especie).exists():
            raise serializers.ValidationError("Ya existe una raza con este nombre para esta especie.")
        return attrs


# ── HistorialClinico ──────────────────────────────────────
class HistorialClinicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialClinico
        fields = ['id', 'fecha_creacion', 'antecedentes', 'observaciones', 'usuario']


class HistorialClinicoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialClinico
        fields = ['antecedentes', 'observaciones', 'usuario']


class HistorialClinicoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialClinico
        fields = ['antecedentes', 'observaciones', 'usuario']
