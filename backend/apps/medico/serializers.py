import re
from rest_framework import serializers
from django.db import transaction
from .models import MedicoVeterinario
from apps.usuarios.models import Usuario, Rol
from apps.core.validators import validar_formato_ci, validar_ci_unico_global, generar_password_default, generar_username


class UsuarioMedicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'first_name', 'last_name', 'ci', 'email', 'telefono', 'direccion']


class MedicoVeterinarioSerializer(serializers.ModelSerializer):
    usuario = UsuarioMedicoSerializer(read_only=True)

    class Meta:
        model = MedicoVeterinario
        fields = ['id', 'usuario', 'especialidad', 'clinica_procedencia', 'genero']


class MedicoVeterinarioCreateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True, max_length=100)
    last_name = serializers.CharField(required=True, max_length=100)
    ci = serializers.CharField(required=True, max_length=10)
    email = serializers.EmailField(required=True)
    telefono = serializers.CharField(required=False, allow_blank=True, max_length=8)
    direccion = serializers.CharField(required=False, allow_blank=True)
    especialidad = serializers.CharField(required=False, allow_blank=True, max_length=100)
    clinica_procedencia = serializers.CharField(required=False, allow_blank=True, max_length=200)
    genero = serializers.ChoiceField(
        choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')],
        required=False, allow_null=True
    )

    def validate_ci(self, value):
        validar_formato_ci(value)
        validar_ci_unico_global(value)
        return value

    def validate_first_name(self, value):
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', value):
            raise serializers.ValidationError("El nombre solo puede contener letras.")
        return value.strip()

    def validate_last_name(self, value):
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', value):
            raise serializers.ValidationError("El apellido solo puede contener letras.")
        return value.strip()

    def validate_telefono(self, value):
        if value and not re.match(r'^\d{7,8}$', value):
            raise serializers.ValidationError("El teléfono debe contener solo números (7 u 8 dígitos).")
        return value

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        rol_medico, _ = Rol.objects.get_or_create(
            nombre='Medico Externo',
            defaults={'descripcion': 'Solo resultados de sus solicitudes'}
        )
        password = generar_password_default()
        username = generar_username(validated_data['email'])

        usuario = Usuario.objects.create(
            username=username,
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            ci=validated_data['ci'],
            telefono=validated_data.get('telefono', ''),
            direccion=validated_data.get('direccion', ''),
            rol=rol_medico,
            debe_cambiar_password=True,
        )
        usuario.set_password(password)
        usuario.save()

        medico = MedicoVeterinario.objects.create(
            usuario=usuario,
            especialidad=validated_data.get('especialidad', ''),
            clinica_procedencia=validated_data.get('clinica_procedencia', ''),
            genero=validated_data.get('genero'),
        )
        return medico


class MedicoVeterinarioUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, max_length=100)
    last_name = serializers.CharField(required=False, max_length=100)
    ci = serializers.CharField(required=False, max_length=10)
    email = serializers.EmailField(required=False)
    telefono = serializers.CharField(required=False, allow_blank=True, max_length=8)
    direccion = serializers.CharField(required=False, allow_blank=True)
    especialidad = serializers.CharField(required=False, allow_blank=True, max_length=100)
    clinica_procedencia = serializers.CharField(required=False, allow_blank=True, max_length=200)
    genero = serializers.ChoiceField(
        choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')],
        required=False, allow_null=True
    )

    def validate_ci(self, value):
        validar_formato_ci(value)
        instance = self.instance
        validar_ci_unico_global(
            value,
            exclude_usuario_pk=instance.usuario.pk if instance and instance.usuario else None,
        )
        return value

    def validate_email(self, value):
        instance = self.instance
        usuario_pk = instance.usuario.pk if instance and instance.usuario else None
        if Usuario.objects.exclude(pk=usuario_pk).filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado por otro usuario.")
        return value

    def validate_first_name(self, value):
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', value):
            raise serializers.ValidationError("El nombre solo puede contener letras.")
        return value.strip()

    def validate_last_name(self, value):
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', value):
            raise serializers.ValidationError("El apellido solo puede contener letras.")
        return value.strip()

    def validate_telefono(self, value):
        if value and not re.match(r'^\d{7,8}$', value):
            raise serializers.ValidationError("El teléfono debe contener solo números (7 u 8 dígitos).")
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        usuario = instance.usuario

        # Si no tiene usuario vinculado, crear uno nuevo
        if usuario is None:
            rol_medico, _ = Rol.objects.get_or_create(
                nombre='Medico Externo',
                defaults={'descripcion': 'Solo resultados de sus solicitudes'}
            )
            base_email = validated_data.get('email', f'medico{instance.pk}@laclivet.com')
            username = generar_username(base_email)
            password = generar_password_default()

            usuario = Usuario.objects.create(
                username=username,
                email=base_email,
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
                ci=validated_data.get('ci'),
                telefono=validated_data.get('telefono', ''),
                direccion=validated_data.get('direccion', ''),
                rol=rol_medico,
                debe_cambiar_password=True,
            )
            usuario.set_password(password)
            usuario.save()
            instance.usuario = usuario
            instance.save()
        else:
            # Actualizar usuario existente
            campos_usuario = ['first_name', 'last_name', 'ci', 'email', 'telefono', 'direccion']
            for campo in campos_usuario:
                if campo in validated_data:
                    setattr(usuario, campo, validated_data[campo])
            usuario.save()

        # Actualizar campos del médico
        campos_medico = ['especialidad', 'clinica_procedencia', 'genero']
        for campo in campos_medico:
            if campo in validated_data:
                setattr(instance, campo, validated_data[campo])
        instance.save()

        return instance