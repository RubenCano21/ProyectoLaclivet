from apps.propietario.models import Propietario
from rest_framework import serializers
from apps.core.validators import validar_formato_ci, validar_ci_unico_global


class PropietarioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Propietario
        fields = ['id', 'ci', 'nombre', 'apellido', 'correo', 'telefono', 'direccion']


class PropietarioCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Propietario
        fields = ['nombre', 'apellido', 'ci', 'correo', 'telefono', 'direccion']
        extra_kwargs = {
            'ci': {'required': True},
            'telefono': {'required': True},
        }

    def validate_ci(self, value):
        validar_formato_ci(value)
        instance = getattr(self, 'instance', None)
        validar_ci_unico_global(
            value,
            exclude_propietario_pk=instance.pk if instance else None
        )
        return value

    def validate_correo(self, value):
        if Propietario.objects.filter(correo=value).exists():
            raise serializers.ValidationError("Ya existe un propietario con este correo.")
        return value

    def create(self, validated_data):
        return Propietario.objects.create(**validated_data)


class PropietarioUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Propietario
        fields = ['nombre', 'apellido', 'ci', 'correo', 'telefono', 'direccion']

    def validate_ci(self, value):
        propietario = self.instance
        if Propietario.objects.exclude(pk=propietario.pk).filter(ci=value).exists():
            raise serializers.ValidationError("Ya existe un propietario con este CI.")
        return value

    def validate_correo(self, value):
        propietario = self.instance
        if Propietario.objects.exclude(pk=propietario.pk).filter(correo=value).exists():
            raise serializers.ValidationError("Ya existe un propietario con este correo.")
        return value
