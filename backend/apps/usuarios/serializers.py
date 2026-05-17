from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import Usuario, Rol, Permiso, RolPermiso


class RolSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Rol"""

    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion']


class PermisoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Permiso"""

    class Meta:
        model = Permiso
        fields = ['id', 'nombre', 'codigo', 'descripcion']


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Usuario (lectura)"""
    rol = RolSerializer(read_only=True)
    permisos = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'telefono', 'direccion', 'fecha_nacimiento', 'rol', 'permisos',
            'fecha_creacion', 'fecha_actualizacion', 'is_active', 'is_staff'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

    def get_permisos(self, obj):
        """Obtiene los permisos del usuario"""
        permisos = obj.get_permisos()
        return PermisoSerializer(permisos, many=True).data


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    """Serializer para el registro de nuevos usuarios"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='Confirmar contraseña'
    )

    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password', 'password2',
            'first_name', 'last_name', 'telefono',
            'direccion', 'fecha_nacimiento'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        """Validar que las contraseñas coincidan"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Las contraseñas no coinciden."
            })
        return attrs

    def validate_email(self, value):
        """Validar que el email no esté registrado"""
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value

    def validate_username(self, value):
        """Validar que el username no esté registrado"""
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está registrado.")
        return value

    def create(self, validated_data):
        """Crear un nuevo usuario"""
        validated_data.pop('password2')
        password = validated_data.pop('password')

        usuario = Usuario.objects.create(**validated_data)
        usuario.set_password(password)
        usuario.save()

        return usuario


class LoginSerializer(serializers.Serializer):
    """Serializer para el login de usuarios con email"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """Validar las credenciales del usuario"""
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            usuario = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )

            if not usuario:
                raise serializers.ValidationError(
                    'No se pudo iniciar sesión con las credenciales proporcionadas.',
                    code='authorization'
                )

            if not usuario.is_active:
                raise serializers.ValidationError(
                    'Esta cuenta está desactivada.',
                    code='authorization'
                )

            attrs['usuario'] = usuario
            return attrs
        else:
            raise serializers.ValidationError(
                'Debe incluir "email" y "password".',
                code='authorization'
            )


class CambiarPasswordSerializer(serializers.Serializer):
    """Serializer para cambiar la contraseña"""
    password_actual = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    password_nuevo = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_nuevo2 = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """Validar que las contraseñas nuevas coincidan"""
        if attrs['password_nuevo'] != attrs['password_nuevo2']:
            raise serializers.ValidationError({
                "password_nuevo": "Las contraseñas no coinciden."
            })
        return attrs

    def validate_password_actual(self, value):
        """Validar que la contraseña actual sea correcta"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual es incorrecta.")
        return value

    def save(self):
        """Cambiar la contraseña del usuario"""
        user = self.context['request'].user
        user.set_password(self.validated_data['password_nuevo'])
        user.save()
        return user


class ActualizarUsuarioSerializer(serializers.ModelSerializer):
    """Serializer para actualizar información del usuario"""

    class Meta:
        model = Usuario
        fields = [
            'first_name', 'last_name', 'email', 'telefono',
            'direccion', 'fecha_nacimiento'
        ]
        extra_kwargs = {
            'email': {'required': True}
        }

    def validate_email(self, value):
        """Validar que el email no esté registrado por otro usuario"""
        usuario = self.context['request'].user
        if Usuario.objects.exclude(pk=usuario.pk).filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado por otro usuario.")
        return value

