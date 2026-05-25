from rest_framework import serializers
from .models import CatalogoExamen, Examen, Parametro, ValorReferencia


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
        fields = ['id', 'nombre_parametro', 'unidad_medida', 'examen', 'examen_nombre']


class ParametroCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parametro
        fields = ['nombre_parametro', 'unidad_medida', 'examen']
        extra_kwargs = {
            'nombre_parametro': {'required': True},
            'examen': {'required': True},
        }


class ParametroUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parametro
        fields = ['nombre_parametro', 'unidad_medida', 'examen']


# ── ValorReferencia ───────────────────────────────────────
class ValorReferenciaSerializer(serializers.ModelSerializer):
    parametro_nombre = serializers.CharField(source='parametro.nombre_parametro', read_only=True)

    class Meta:
        model = ValorReferencia
        fields = ['id', 'valor_min', 'valor_max', 'especie', 'parametro', 'parametro_nombre']


class ValorReferenciaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValorReferencia
        fields = ['valor_min', 'valor_max', 'especie', 'parametro']
        extra_kwargs = {
            'parametro': {'required': True},
        }


class ValorReferenciaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValorReferencia
        fields = ['valor_min', 'valor_max', 'especie', 'parametro']

