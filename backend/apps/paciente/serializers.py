from rest_framework import serializers
from .models import Especie, Raza, Paciente, AntecedentePaciente


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
        extra_kwargs = {'nombre': {'required': True}, 'especie': {'required': True}}

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


# ── Paciente ──────────────────────────────────────────────
class PacienteSerializer(serializers.ModelSerializer):
    raza_nombre = serializers.CharField(source='raza.nombre', read_only=True)
    especie_nombre = serializers.CharField(source='raza.especie.nombre', read_only=True)
    propietario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Paciente
        fields = [
            'id', 'nombre', 'sexo', 'tamanio', 'color', 'fecha_nacimiento',
            'propietario', 'propietario_nombre',
            'raza', 'raza_nombre', 'especie_nombre',
        ]

    def get_propietario_nombre(self, obj):
        # ← corregido: los datos personales ahora viven en usuario
        if obj.propietario and obj.propietario.usuario:
            u = obj.propietario.usuario
            return f"{u.first_name} {u.last_name}"
        return None


class PacienteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = ['nombre', 'sexo', 'tamanio', 'color', 'fecha_nacimiento', 'propietario', 'raza']
        extra_kwargs = {'nombre': {'required': True}}


class PacienteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = ['nombre', 'sexo', 'tamanio', 'color', 'fecha_nacimiento', 'propietario', 'raza']


# ── AntecedentePaciente ───────────────────────────────────
class AntecedentePacienteSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    registrado_por_email = serializers.CharField(source='registrado_por.email', read_only=True)

    class Meta:
        model = AntecedentePaciente
        fields = ['id', 'paciente', 'tipo', 'tipo_display', 'descripcion',
                  'fecha_registro', 'registrado_por', 'registrado_por_email']


class AntecedentePacienteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AntecedentePaciente
        fields = ['paciente', 'tipo', 'descripcion', 'registrado_por']
        extra_kwargs = {
            'paciente': {'required': True},
            'descripcion': {'required': True},
        }


class AntecedentePacienteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AntecedentePaciente
        fields = ['tipo', 'descripcion']


# ── Historial Dinámico ────────────────────────────────────
class HistorialSolicitudSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    codigo = serializers.CharField()
    fecha_solicitud = serializers.DateTimeField()
    estado = serializers.CharField()
    observaciones = serializers.CharField()
    medico_veterinario = serializers.SerializerMethodField()
    examenes = serializers.SerializerMethodField()

    def get_medico_veterinario(self, obj):
        # ← corregido: los datos personales ahora viven en usuario
        if obj.medico_veterinario and obj.medico_veterinario.usuario:
            u = obj.medico_veterinario.usuario
            return f"{u.first_name} {u.last_name}"
        return None

    def get_examenes(self, obj):
        return [
            {
                'examen': d.examen.nombre_examen if d.examen else None,
                'precio_aplicado': d.precio_aplicado,
            }
            for d in obj.detalles.select_related('examen').all()
        ]