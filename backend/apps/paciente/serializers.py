from rest_framework import serializers
from .models import Especie, Raza, HistorialClinico, Paciente


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


# ── Paciente ──────────────────────────────────────────────
class PacienteSerializer(serializers.ModelSerializer):
    raza_nombre = serializers.CharField(source='raza.nombre', read_only=True)
    especie_nombre = serializers.CharField(source='raza.especie.nombre', read_only=True)
    propietario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Paciente
        fields = [
            'id', 'nombre', 'sexo', 'tamanio', 'color',
            'historial_clinico', 'propietario', 'propietario_nombre',
            'raza', 'raza_nombre', 'especie_nombre',
        ]

    def get_propietario_nombre(self, obj):
        if obj.propietario:
            return f"{obj.propietario.nombre} {obj.propietario.apellido}"
        return None


class PacienteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = ['nombre', 'sexo', 'tamanio', 'color', 'historial_clinico', 'propietario', 'raza']
        extra_kwargs = {
            'nombre': {'required': True},
            'historial_clinico': {'required': True},
        }

    def validate_historial_clinico(self, value):
        if Paciente.objects.filter(historial_clinico=value).exists():
            raise serializers.ValidationError("Ya existe un paciente con este historial clínico.")
        return value


class PacienteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = ['nombre', 'sexo', 'tamanio', 'color', 'propietario', 'raza']

