from rest_framework import serializers
from .models import CatalogoExamen, Examen


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

