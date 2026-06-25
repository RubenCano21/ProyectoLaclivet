from rest_framework import serializers
from apps.propietario.models import Propietario
from apps.usuarios.models import Usuario, Rol
from apps.core.validators import validar_formato_ci, validar_ci_unico_global, generar_username, generar_password_default
from django.db import transaction


class UsuarioPropietarioSerializer(serializers.ModelSerializer):
    """Serializer de lectura para el usuario vinculado al propietario"""
    class Meta:
        model = Usuario
        fields = ['id', 'first_name', 'last_name', 'ci', 'email', 'telefono', 'direccion', 'fecha_nacimiento']


class PropietarioSerializer(serializers.ModelSerializer):
    """Serializer de lectura"""
    usuario = UsuarioPropietarioSerializer(read_only=True)

    class Meta:
        model = Propietario
        fields = ['id', 'usuario']


class PropietarioCreateSerializer(serializers.Serializer):
    """Serializer para crear propietario + usuario vinculado"""
    # Datos del usuario
    first_name = serializers.CharField(required=True, max_length=50)
    last_name = serializers.CharField(required=True, max_length=50)
    ci = serializers.CharField(required=True, max_length=10)
    email = serializers.EmailField(required=True)
    telefono = serializers.CharField(required=False, allow_blank=True, max_length=8)
    direccion = serializers.CharField(required=False, allow_blank=True)
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)


    def validate_ci(self, value):
        validar_formato_ci(value)
        validar_ci_unico_global(value)
        return value

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value

    def _generar_username(self, email):
        base = (email or '').split('@')[0][:140] or 'user'
        username = base
        i = 1
        while Usuario.objects.filter(username=username).exists():
            i += 1
            username = f"{base}{i}"[:150]
        return username

    def _generar_password_default(self, data):
        last_name = data.get('last_name', '').strip().lower()
        primer_apellido = last_name.split()[0] if last_name else 'usuario'
        ci = data.get('ci', '').strip()
        return f"{primer_apellido}.{ci}" if ci else primer_apellido

    @transaction.atomic
    def create(self, validated_data):
        # Obtener o crear el rol Propietario
        rol_propietario, _ = Rol.objects.get_or_create(
            nombre='Propietario',
            defaults={'descripcion': 'Solo resultados de sus mascotas'}
        )

        password = generar_password_default(validated_data.get('last_name', ''), validated_data.get('ci', ''))
        username = generar_username(validated_data['email'])

        usuario = Usuario.objects.create(
            username=username,
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            ci=validated_data['ci'],
            telefono=validated_data.get('telefono', ''),
            direccion=validated_data.get('direccion', ''),
            fecha_nacimiento=validated_data.get('fecha_nacimiento'),
            rol=rol_propietario,
        )
        usuario.set_password(password)
        usuario.save()

        propietario = Propietario.objects.create(usuario=usuario)
        return propietario


class PropietarioUpdateSerializer(serializers.Serializer):
    """Serializer para actualizar propietario — actualiza el usuario vinculado"""
    first_name = serializers.CharField(required=False, max_length=50)
    last_name = serializers.CharField(required=False, max_length=50)
    ci = serializers.CharField(required=False, max_length=10)
    email = serializers.EmailField(required=False)
    telefono = serializers.CharField(required=False, allow_blank=True, max_length=8)
    direccion = serializers.CharField(required=False, allow_blank=True)
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)

    def validate_ci(self, value):
        validar_formato_ci(value)
        instance = self.instance  # instancia de Propietario
        validar_ci_unico_global(
            value,
            exclude_usuario_pk=instance.usuario.pk if instance and instance.usuario else None,
            exclude_propietario_pk=instance.pk if instance else None,
        )
        return value

    def validate_email(self, value):
        instance = self.instance
        usuario_pk = instance.usuario.pk if instance and instance.usuario else None
        if Usuario.objects.exclude(pk=usuario_pk).filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado por otro usuario.")
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        usuario = instance.usuario

        # Si no tiene usuario vinculado, crear uno nuevo
        if usuario is None:
            rol_propietario, _ = Rol.objects.get_or_create(
                nombre='Propietario',
                defaults={'descripcion': 'Solo resultados de sus mascotas'}
            )
            password = generar_password_default(validated_data.get('last_name', ''), validated_data.get('ci', ''))
            username = generar_username(validated_data.get('email', ''))

            usuario = Usuario.objects.create(
                username=username,
                email=validated_data.get('email', ''),
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
                ci=validated_data.get('ci'),
                telefono=validated_data.get('telefono', ''),
                direccion=validated_data.get('direccion', ''),
                fecha_nacimiento=validated_data.get('fecha_nacimiento'),
                rol=rol_propietario,
            )
            usuario.set_password(password)
            usuario.save()
            instance.usuario = usuario
            instance.save()
        else:
            # Actualizar usuario existente
            for attr, val in validated_data.items():
                setattr(usuario, attr, val)
            usuario.save()

        return instance