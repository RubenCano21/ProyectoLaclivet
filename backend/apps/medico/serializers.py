from rest_framework import serializers
from .models import MedicoVeterinario
from apps.core.validators import validar_formato_ci, validar_ci_unico_global


class MedicoVeterinarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicoVeterinario
        fields = ['id', 'nombre', 'apellido', 'ci', 'especialidad', 'genero', 'correo', 'telefono', 'direccion']  # ← ci


class MedicoVeterinarioCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicoVeterinario
        fields = ['nombre', 'apellido', 'ci', 'especialidad', 'genero', 'correo', 'telefono', 'direccion']  # ← ci
        extra_kwargs = {
            'nombre': {'required': True},
            'apellido': {'required': True},
        }

    def validate_ci(self, value):
        validar_formato_ci(value)
        validar_ci_unico_global(value)
        return value

    def validate_correo(self, value):
        if value and MedicoVeterinario.objects.filter(correo=value).exists():
            raise serializers.ValidationError("Ya existe un médico registrado con este correo.")
        return value

    def validate_nombre(self, value):
        import re
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', value):
            raise serializers.ValidationError("El nombre solo puede contener letras.")
        return value.strip()

    def validate_apellido(self, value):
        import re
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', value):
            raise serializers.ValidationError("El apellido solo puede contener letras.")
        return value.strip()

    def validate_telefono(self, value):
        import re
        if value and not re.match(r'^\d{7,8}$', value):
            raise serializers.ValidationError("El teléfono debe contener solo números (7 u 8 dígitos).")
        return value


class MedicoVeterinarioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicoVeterinario
        fields = ['nombre', 'apellido', 'ci', 'especialidad', 'genero', 'correo', 'telefono', 'direccion']  # ← ci

    def validate_ci(self, value):
        validar_formato_ci(value)
        validar_ci_unico_global(value, exclude_medico_pk=self.instance.pk)  # ← excluye el actual
        return value

    def validate_correo(self, value):
        if value and MedicoVeterinario.objects.exclude(pk=self.instance.pk).filter(correo=value).exists():
            raise serializers.ValidationError("Ya existe un médico registrado con este correo.")
        return value

    def validate_nombre(self, value):
        import re
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', value):
            raise serializers.ValidationError("El nombre solo puede contener letras.")
        return value.strip()

    def validate_apellido(self, value):
        import re
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', value):
            raise serializers.ValidationError("El apellido solo puede contener letras.")
        return value.strip()

    def validate_telefono(self, value):
        import re
        if value and not re.match(r'^\d{7,8}$', value):
            raise serializers.ValidationError("El teléfono debe contener solo números (7 u 8 dígitos).")
        return value