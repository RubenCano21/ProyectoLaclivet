from rest_framework import serializers
from .models import Muestra, IncidenciaMuestra, Resultado


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


# ── Serializadores de soporte ──────────────────────────────────────────────

class ValorReferenciaSerializer(serializers.Serializer):
    especie = serializers.CharField()
    valor_min = serializers.DecimalField(max_digits=10, decimal_places=2)
    valor_max = serializers.DecimalField(max_digits=10, decimal_places=2)


class ParametroResultadoSerializer(serializers.Serializer):
    """Parámetro del examen con su valor obtenido y referencia"""
    id = serializers.IntegerField()
    nombre_parametro = serializers.CharField()
    unidad_medida = serializers.CharField()
    valor_obtenido = serializers.SerializerMethodField()
    valores_referencia = serializers.SerializerMethodField()

    def get_valor_obtenido(self, parametro):
        """Busca el valor obtenido en el JSON del resultado"""
        valores = self.context.get('valores_obtenidos') or {}
        return valores.get(str(parametro.id)) or valores.get(parametro.nombre_parametro)

    def get_valores_referencia(self, parametro):
        refs = parametro.valores_referencia.all()
        return ValorReferenciaSerializer(refs, many=True).data


class ExamenResultadoSerializer(serializers.Serializer):
    """Examen con sus parámetros y valores obtenidos"""
    id = serializers.IntegerField()
    nombre_examen = serializers.CharField()
    categoria = serializers.CharField()
    parametros = serializers.SerializerMethodField()

    def get_parametros(self, examen):
        parametros = examen.parametros.prefetch_related('valores_referencia').all()
        return ParametroResultadoSerializer(
            parametros,
            many=True,
            context=self.context
        ).data


class MuestraResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Muestra
        fields = ['id', 'codigo', 'tipo_muestra', 'estado']


class PacienteResumenSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    sexo = serializers.CharField()
    especie = serializers.SerializerMethodField()
    raza = serializers.SerializerMethodField()

    def get_especie(self, paciente):
        return paciente.raza.especie.nombre if paciente.raza else None

    def get_raza(self, paciente):
        return paciente.raza.nombre if paciente.raza else None


class PropietarioResumenSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre_completo = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    telefono = serializers.SerializerMethodField()

    def get_nombre_completo(self, propietario):
        if propietario.usuario:
            return f"{propietario.usuario.first_name} {propietario.usuario.last_name}"
        return None

    def get_email(self, propietario):
        return propietario.usuario.email if propietario.usuario else None

    def get_telefono(self, propietario):
        return propietario.usuario.telefono if propietario.usuario else None


class MedicoResumenSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre_completo = serializers.SerializerMethodField()
    especialidad = serializers.CharField()
    clinica_procedencia = serializers.CharField()

    def get_nombre_completo(self, medico):
        if medico.usuario:
            return f"Dr(a). {medico.usuario.first_name} {medico.usuario.last_name}"
        return None


class VeterinarioResumenSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre_completo = serializers.SerializerMethodField()

    def get_nombre_completo(self, usuario):
        return f"{usuario.first_name} {usuario.last_name}"


# ── Serializer principal de Resultado ─────────────────────────────────────

class ResultadoSerializer(serializers.ModelSerializer):
    # Datos del examen con parámetros y valores
    examen = serializers.SerializerMethodField()

    # Datos de la solicitud
    solicitud_codigo = serializers.SerializerMethodField()
    fecha_solicitud = serializers.SerializerMethodField()

    # Datos del paciente
    paciente = serializers.SerializerMethodField()

    # Datos del propietario
    propietario = serializers.SerializerMethodField()

    # Datos del médico solicitante
    medico_solicitante = serializers.SerializerMethodField()

    # Datos del veterinario responsable del resultado
    veterinario_responsable = serializers.SerializerMethodField()

    # Muestra analizada
    muestra = MuestraResumenSerializer(read_only=True)

    class Meta:
        model = Resultado
        fields = [
            'id',
            'estado',
            'solicitud_codigo',
            'fecha_solicitud',
            'paciente',
            'propietario',
            'medico_solicitante',
            'veterinario_responsable',
            'muestra',
            'examen',
            'observaciones',
            'fecha_emision',
            'fecha_creacion',
            'fecha_actualizacion',
            'archivo_pdf',
        ]

    def get_examen(self, obj):
        examen = obj.examen
        if not examen:
            return None
        return ExamenResultadoSerializer(
            examen,
            context={'valores_obtenidos': obj.valores_obtenidos}
        ).data

    def get_solicitud_codigo(self, obj):
        return obj.detalle_solicitud.solicitud.codigo

    def get_fecha_solicitud(self, obj):
        return obj.detalle_solicitud.solicitud.fecha_solicitud

    def get_paciente(self, obj):
        paciente = obj.paciente
        return PacienteResumenSerializer(paciente).data if paciente else None

    def get_propietario(self, obj):
        paciente = obj.paciente
        if paciente and paciente.propietario:
            return PropietarioResumenSerializer(paciente.propietario).data
        return None

    def get_medico_solicitante(self, obj):
        medico = obj.medico_solicitante
        return MedicoResumenSerializer(medico).data if medico else None

    def get_veterinario_responsable(self, obj):
        vet = obj.veterinario_responsable
        return VeterinarioResumenSerializer(vet).data if vet else None


class ResultadoCreateSerializer(serializers.ModelSerializer):
    """Para crear o actualizar un resultado"""

    class Meta:
        model = Resultado
        fields = [
            'detalle_solicitud',
            'muestra',
            'veterinario_responsable',
            'estado',
            'valores_obtenidos',
            'observaciones',
            'fecha_emision',
            'archivo_pdf',
        ]

    def validate_detalle_solicitud(self, value):
        # No permitir duplicar resultado para el mismo detalle
        if Resultado.objects.filter(detalle_solicitud=value).exclude(
            pk=self.instance.pk if self.instance else None
        ).exists():
            raise serializers.ValidationError(
                "Ya existe un resultado para este detalle de solicitud."
            )
        return value