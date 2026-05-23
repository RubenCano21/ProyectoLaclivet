from rest_framework import serializers
from .models import MedicoVeterinario


class MedicoVeterinarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicoVeterinario
        fields = ['id', 'nombre', 'apellido', 'especialidad', 'genero', 'correo', 'telefono', 'direccion']


class MedicoVeterinarioCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicoVeterinario
        fields = ['nombre', 'apellido', 'especialidad', 'genero', 'correo', 'telefono', 'direccion']
        extra_kwargs = {
            'nombre': {'required': True},
            'apellido': {'required': True},
        }

    def validate_correo(self, value):
        if value and MedicoVeterinario.objects.filter(correo=value).exists():
            raise serializers.ValidationError("Ya existe un médico registrado con este correo.")
        return value


class MedicoVeterinarioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicoVeterinario
        fields = ['nombre', 'apellido', 'especialidad', 'genero', 'correo', 'telefono', 'direccion']

    def validate_correo(self, value):
        if value and MedicoVeterinario.objects.exclude(pk=self.instance.pk).filter(correo=value).exists():
            raise serializers.ValidationError("Ya existe un médico registrado con este correo.")
        return value

