from rest_framework import serializers
from .models import Especie


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

