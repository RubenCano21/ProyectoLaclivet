from rest_framework import serializers
from .models import CatalogoExamen


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

