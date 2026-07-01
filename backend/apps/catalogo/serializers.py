from itertools import groupby

from apps.muestra.models import Muestra
from rest_framework import serializers
from apps.catalogo.models import (
    CatalogoExamen, Examen, Parametro, ValorReferencia,
    OrdenTrabajo, OrdenExamen, ResultadoParametro,
)


# ── CatalogoExamen ────────────────────────────────────────
class CatalogoExamenSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogoExamen
        fields = ['id', 'nombre', 'area', 'precio']


class CatalogoExamenCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogoExamen
        fields = ['nombre', 'area', 'precio']
        extra_kwargs = {
            'nombre': {'required': True},
        }

    def validate_nombre(self, value):
        if CatalogoExamen.objects.filter(nombre__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un catálogo con este nombre.")
        return value


class CatalogoExamenUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogoExamen
        fields = ['nombre', 'area', 'precio']

    def validate_nombre(self, value):
        if CatalogoExamen.objects.exclude(pk=self.instance.pk).filter(nombre__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un catálogo con este nombre.")
        return value


# ── Examen ────────────────────────────────────────────────
class ExamenSerializer(serializers.ModelSerializer):
    catalogo_nombre = serializers.CharField(source='catalogo.nombre', read_only=True)

    class Meta:
        model = Examen
        fields = ['id', 'nombre_examen', 'categoria', 'descripcion', 'catalogo', 'catalogo_nombre']


class ExamenCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Examen
        fields = ['nombre_examen', 'categoria', 'descripcion', 'catalogo']
        extra_kwargs = {
            'nombre_examen': {'required': True},
            'catalogo': {'required': True},
        }


class ExamenUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Examen
        fields = ['nombre_examen', 'categoria', 'descripcion', 'catalogo']


# ── Parametro ─────────────────────────────────────────────
class ParametroSerializer(serializers.ModelSerializer):
    examen_nombre = serializers.CharField(source='examen.nombre_examen', read_only=True)

    class Meta:
        model = Parametro
        fields = [
            'id', 'nombre_parametro', 'unidad_medida', 'examen', 'examen_nombre',
            'grupo', 'tipo_dato', 'opciones', 'orden',
        ]


class ParametroCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parametro
        fields = ['nombre_parametro', 'unidad_medida', 'examen', 'grupo', 'tipo_dato', 'opciones', 'orden']
        extra_kwargs = {
            'nombre_parametro': {'required': True},
            'examen': {'required': True},
        }

    def validate_opciones(self, value):
        tipo_dato = self.initial_data.get('tipo_dato')
        if tipo_dato == 'SEL' and not value:
            raise serializers.ValidationError("Debes indicar las opciones cuando el tipo de dato es Selección.")
        return value


class ParametroUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parametro
        fields = ['nombre_parametro', 'unidad_medida', 'examen', 'grupo', 'tipo_dato', 'opciones', 'orden']


# ── ValorReferencia ───────────────────────────────────────
class ValorReferenciaSerializer(serializers.ModelSerializer):
    parametro_nombre = serializers.CharField(source='parametro.nombre_parametro', read_only=True)

    class Meta:
        model = ValorReferencia
        fields = [
            'id', 'valor_min', 'valor_max', 'especie', 'sexo',
            'texto_referencia', 'parametro', 'parametro_nombre',
        ]


class ValorReferenciaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValorReferencia
        fields = ['valor_min', 'valor_max', 'especie', 'sexo', 'texto_referencia', 'parametro']
        extra_kwargs = {
            'parametro': {'required': True},
        }

    def validate(self, attrs):
        tiene_rango = attrs.get('valor_min') is not None or attrs.get('valor_max') is not None
        tiene_texto = bool(attrs.get('texto_referencia'))
        if not tiene_rango and not tiene_texto:
            raise serializers.ValidationError(
                "Debes indicar un rango (valor_min/valor_max) o un texto_referencia."
            )
        return attrs


class ValorReferenciaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValorReferencia
        fields = ['valor_min', 'valor_max', 'especie', 'sexo', 'texto_referencia', 'parametro']


# ── Plantilla agrupada (consumo del front para pintar el formulario) ──────
class ParametroPlantillaSerializer(serializers.ModelSerializer):
    """Variante de ParametroSerializer con sus valores_referencia anidados.
    Solo se usa de lectura, dentro de ExamenDetalleSerializer."""
    valores_referencia = ValorReferenciaSerializer(many=True, read_only=True)

    class Meta:
        model = Parametro
        fields = [
            'id', 'nombre_parametro', 'unidad_medida', 'grupo',
            'tipo_dato', 'opciones', 'orden', 'valores_referencia',
        ]


class ExamenDetalleSerializer(serializers.ModelSerializer):
    """Plantilla completa del examen para el formulario de captura de resultados:
    agrupa los parámetros por 'grupo' (Eritrograma, Leucograma, etc.)."""
    grupos = serializers.SerializerMethodField()

    class Meta:
        model = Examen
        fields = ['id', 'nombre_examen', 'categoria', 'descripcion', 'catalogo', 'grupos']

    def get_grupos(self, obj):
        parametros = sorted(obj.parametros.all(), key=lambda p: (p.grupo or '', p.orden))
        grupos = []
        for nombre_grupo, items in groupby(parametros, key=lambda p: p.grupo or 'General'):
            grupos.append({
                'nombre': nombre_grupo,
                'parametros': ParametroPlantillaSerializer(list(items), many=True).data,
            })
        return grupos


# ── Resultados (OrdenTrabajo / OrdenExamen / ResultadoParametro) ─────────
class OrdenTrabajoSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.CharField(source='paciente.nombre', read_only=True)

    class Meta:
        model = OrdenTrabajo
        fields = [
            'id', 'paciente', 'paciente_nombre', 'veterinario_solicitante',
            'fecha_creacion', 'estado', 'observaciones_generales',
        ]


class OrdenTrabajoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdenTrabajo
        fields = ['paciente', 'veterinario_solicitante', 'observaciones_generales']
        extra_kwargs = {
            'paciente': {'required': True},
        }


class ResultadoParametroSerializer(serializers.ModelSerializer):
    parametro_nombre = serializers.CharField(source='parametro.nombre_parametro', read_only=True)

    class Meta:
        model = ResultadoParametro
        fields = ['id', 'parametro', 'parametro_nombre', 'valor_numerico', 'valor_texto', 'interpretacion']
        read_only_fields = ['interpretacion']


class ResultadoParametroInputSerializer(serializers.Serializer):
    """Usado solo dentro de OrdenExamenSerializer al escribir; no toca 'interpretacion',
    eso lo calcula el backend."""
    parametro = serializers.PrimaryKeyRelatedField(queryset=Parametro.objects.all())
    valor_numerico = serializers.DecimalField(max_digits=10, decimal_places=3, required=False, allow_null=True)
    valor_texto = serializers.CharField(required=False, allow_blank=True)


class OrdenExamenSerializer(serializers.ModelSerializer):
    resultados = ResultadoParametroSerializer(many=True, read_only=True)
    examen_nombre = serializers.CharField(source='examen.nombre_examen', read_only=True)

    class Meta:
        model = OrdenExamen
        fields = [
            'id', 'orden', 'examen', 'examen_nombre', 'muestra',
            'realizado_por', 'validado_por', 'fecha_resultado',
            'observaciones', 'alteraciones', 'diagnostico', 'pronostico',
            'resultados',
        ]


class OrdenExamenResultadosUpdateSerializer(serializers.Serializer):
    """Serializer de escritura para el endpoint de guardado de resultados
    (acción separada, ej. POST /orden-examenes/<id>/resultados/), siguiendo
    tu mismo criterio de separar lectura de escritura."""
    observaciones = serializers.CharField(required=False, allow_blank=True)
    alteraciones = serializers.CharField(required=False, allow_blank=True)
    diagnostico = serializers.CharField(required=False, allow_blank=True)
    pronostico = serializers.CharField(required=False, allow_blank=True)
    realizado_por = serializers.CharField(required=False, allow_blank=True)
    resultados = ResultadoParametroInputSerializer(many=True)

    def update(self, instance, validated_data):
        resultados_data = validated_data.pop('resultados', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        paciente = instance.orden.paciente
        especie_nombre = paciente.raza.especie.nombre if paciente.raza_id else None

        instance.resultados.all().delete()
        for r in resultados_data:
            parametro = r['parametro']
            ref = None
            if especie_nombre:
                ref = parametro.valores_referencia.filter(especie__iexact=especie_nombre).first()
            interpretacion = ''
            if ref and r.get('valor_numerico') is not None:
                interpretacion = ref.evaluar(r['valor_numerico']) or ''
            ResultadoParametro.objects.create(
                orden_examen=instance,
                parametro=parametro,
                valor_numerico=r.get('valor_numerico'),
                valor_texto=r.get('valor_texto', ''),
                interpretacion=interpretacion,
            )
        return instance

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


class OrdenExamenFullDetailSerializer(serializers.ModelSerializer):
    """Reemplaza al antiguo ResultadoSerializer (JSON). Misma forma de salida,
    pero los datos vienen de ResultadoParametro real, no de un JSON suelto."""
    examen_nombre = serializers.CharField(source='examen.nombre_examen', read_only=True)
    solicitud_codigo = serializers.SerializerMethodField()
    fecha_solicitud = serializers.SerializerMethodField()
    paciente = serializers.SerializerMethodField()
    propietario = serializers.SerializerMethodField()
    medico_solicitante = serializers.SerializerMethodField()
    veterinario_nombre = serializers.SerializerMethodField()
    muestra = MuestraResumenSerializer(read_only=True)
    resultados = ResultadoParametroSerializer(many=True, read_only=True)

    class Meta:
        model = OrdenExamen
        fields = [
            'id', 'estado', 'examen', 'examen_nombre', 'solicitud_codigo', 'fecha_solicitud',
            'paciente', 'propietario', 'medico_solicitante', 'veterinario_responsable',
            'veterinario_nombre', 'muestra', 'resultados',
            'observaciones', 'alteraciones', 'diagnostico', 'pronostico',
            'fecha_resultado', 'archivo_pdf',
        ]

    def get_solicitud_codigo(self, obj):
        return obj.detalle_solicitud.solicitud.codigo if obj.detalle_solicitud else None

    def get_fecha_solicitud(self, obj):
        return obj.detalle_solicitud.solicitud.fecha_solicitud if obj.detalle_solicitud else None

    def get_paciente(self, obj):
        return PacienteResumenSerializer(obj.paciente).data if obj.paciente else None

    def get_propietario(self, obj):
        if obj.paciente and getattr(obj.paciente, 'propietario', None):
            return PropietarioResumenSerializer(obj.paciente.propietario).data
        return None

    def get_medico_solicitante(self, obj):
        medico = obj.medico_solicitante
        return MedicoResumenSerializer(medico).data if medico else None

    def get_veterinario_nombre(self, obj):
        if obj.veterinario_responsable:
            return VeterinarioResumenSerializer(obj.veterinario_responsable).data
        return None


class RegistrarResultadoOrdenExamenSerializer(serializers.Serializer):
    """Usado por el Veterinario para registrar resultados + cambiar estado a completado."""
    observaciones = serializers.CharField(required=False, allow_blank=True)
    alteraciones = serializers.CharField(required=False, allow_blank=True)
    diagnostico = serializers.CharField(required=False, allow_blank=True)
    pronostico = serializers.CharField(required=False, allow_blank=True)
    resultados = ResultadoParametroInputSerializer(many=True)

    def update(self, instance, validated_data):
        from django.utils import timezone
        resultados_data = validated_data.pop('resultados', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        paciente = instance.orden.paciente
        especie_nombre = paciente.raza.especie.nombre if paciente.raza_id else None
        sexo_codigo = "M" if getattr(paciente, 'sexo', '').lower().startswith('m') else "H"

        instance.resultados.all().delete()
        for r in resultados_data:
            parametro = r['parametro']
            qs_ref = parametro.valores_referencia.all()
            ref = None
            if especie_nombre:
                ref = qs_ref.filter(especie__iexact=especie_nombre, sexo=sexo_codigo).first() \
                      or qs_ref.filter(especie__iexact=especie_nombre, sexo='A').first()
            interpretacion = ''
            if ref and r.get('valor_numerico') is not None:
                interpretacion = ref.evaluar(r['valor_numerico']) or ''
            ResultadoParametro.objects.create(
                orden_examen=instance,
                parametro=parametro,
                valor_numerico=r.get('valor_numerico'),
                valor_texto=r.get('valor_texto', ''),
                interpretacion=interpretacion,
            )

        instance.estado = 'completado'
        instance.fecha_resultado = timezone.now()
        instance.veterinario_responsable = self.context['request'].user
        instance.save()

        # Si todos los OrdenExamen de la orden están completados, marcar la SolicitudExamen
        orden = instance.orden
        if all(oe.estado in ('completado', 'validado') for oe in orden.examenes.all()):
            if orden.solicitud:
                orden.solicitud.estado = 'completado'
                orden.solicitud.save(update_fields=['estado'])

        return instance