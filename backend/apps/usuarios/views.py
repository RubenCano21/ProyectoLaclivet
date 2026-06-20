from django.shortcuts import get_object_or_404
from rest_framework import status, generics, permissions, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import logout
from django.contrib.auth import authenticate

from config.pagination import StandardPagination
from .models import Usuario, Rol, Permiso, RolPermiso
from .serializers import (
    UsuarioSerializer,
    RegistroUsuarioSerializer,
    LoginSerializer,
    CambiarPasswordSerializer,
    ActualizarUsuarioSerializer,
    AdminActualizarUsuarioSerializer,
    RolSerializer,
    PermisoSerializer,
    RolConPermisosSerializer,
)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer personalizado para incluir datos del usuario en el token"""

    # Cambiar el campo username por email
    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Agregar datos personalizados al token
        token['username'] = user.username
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name

        if user.rol:
            token['rol'] = user.rol.nombre

        return token

    def validate(self, attrs):
        # Obtener email en lugar de username
        email = attrs.get(self.username_field)
        password = attrs.get('password')


        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if user is None:
            raise serializers.ValidationError(
                'No se encontró una cuenta activa con las credenciales proporcionadas',
                code='authorization'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'Esta cuenta está desactivada',
                code='authorization'
            )

        # Generar tokens
        refresh = self.get_token(user)

        data = {'refresh': str(refresh), 'access': str(refresh.access_token), 'usuario': UsuarioSerializer(user).data}

        # Agregar información del usuario a la respuesta

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vista personalizada para obtener el token JWT"""
    serializer_class = CustomTokenObtainPairSerializer


class RegistroView(generics.CreateAPIView):
    """Vista para registrar nuevos usuarios"""
    queryset = Usuario.objects.all()
    serializer_class = RegistroUsuarioSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()

        # Generar tokens para el usuario registrado
        refresh = RefreshToken.for_user(usuario)

        return Response({
            'mensaje': 'Usuario registrado exitosamente',
            'usuario': UsuarioSerializer(usuario).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Vista para el login de usuarios (alternativa a JWT token)"""
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            usuario = serializer.validated_data['usuario']

            # Generar tokens JWT
            refresh = RefreshToken.for_user(usuario)

            return Response({
                'mensaje': 'Login exitoso',
                'usuario': UsuarioSerializer(usuario).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """Vista para cerrar sesión (blacklist del refresh token)"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')

            if not refresh_token:
                return Response({
                    'error': 'Se requiere el refresh token'
                }, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            logout(request)

            return Response({
                'mensaje': 'Logout exitoso'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Token inválido o ya expirado'
            }, status=status.HTTP_400_BAD_REQUEST)


class PerfilUsuarioView(APIView):
    """Vista para obtener y actualizar el perfil del usuario autenticado"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Obtener perfil del usuario"""
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        """Actualizar perfil del usuario"""
        serializer = ActualizarUsuarioSerializer(
            request.user,
            data=request.data,
            context={'request': request},
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                'mensaje': 'Perfil actualizado exitosamente',
                'usuario': UsuarioSerializer(request.user).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CambiarPasswordView(APIView):
    """Vista para cambiar la contraseña del usuario autenticado"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CambiarPasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                'mensaje': 'Contraseña cambiada exitosamente'
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListaUsuariosView(generics.ListAPIView):
    """Vista para listar todos los usuarios (solo para administradores)"""
    queryset = Usuario.objects.all().order_by('id')
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    pagination_class = StandardPagination


class DetalleUsuarioView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Usuario.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return AdminActualizarUsuarioSerializer
        return UsuarioSerializer

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True  # siempre parcial para no exigir todos los campos
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UsuarioSerializer(instance).data)

    def perform_destroy(self, instance):
        """ En lugar de eliminar fisicamente, marcamos como inactivo"""
        instance.is_active = False
        instance.save()

    def destroy(self, request, *args, **kwargs):
        """
        Sobrescribimos el destroy para devolver un mensaje claro y
        el código de estado 200 (OK) en lugar de 204 (No Content).
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'mensaje': 'Usuario desactivado exitosamente (eliminación lógica)'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def verificar_token(request):
    """Vista para verificar si el token es válido"""
    return Response({
        'mensaje': 'Token válido',
        'usuario': UsuarioSerializer(request.user).data
    })


class ListaRolesView(generics.ListAPIView):
    """Lista todos los roles del sistema"""
    queryset = Rol.objects.all().order_by('id')
    serializer_class = RolConPermisosSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination


class ListaPermisosView(generics.ListAPIView):
    """Lista todos los permisos del sistema"""
    queryset = Permiso.objects.all().order_by('id')
    serializer_class = PermisoSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination


class ActualizarRolPermisosView(APIView):
    """Actualiza los permisos asignados a un rol (solo administradores)"""
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def put(self, request, pk):
        try:
            rol = Rol.objects.get(pk=pk)
        except Rol.DoesNotExist:
            return Response({'error': 'Rol no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        permiso_ids = request.data.get('permisos', [])
        if not isinstance(permiso_ids, list):
            return Response({'error': 'Se esperaba una lista de IDs'}, status=status.HTTP_400_BAD_REQUEST)

        permisos_validos = Permiso.objects.filter(id__in=permiso_ids)
        RolPermiso.objects.filter(rol=rol).delete()
        RolPermiso.objects.bulk_create([
            RolPermiso(rol=rol, permiso=p) for p in permisos_validos
        ])
        return Response(RolConPermisosSerializer(rol).data)


class AsignarRolUsuarioView(APIView):
    """Asigna un rol a un usuario (solo administradores)"""
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def patch(self, request, pk):

        usuario = get_object_or_404(Usuario, pk=pk)

        rol_id = request.data.get('rol_id')
        if rol_id is None:
            usuario.rol = None
        else:
            try:
                usuario.rol = Rol.objects.get(pk=rol_id)
            except Rol.DoesNotExist:
                return Response({'error': 'Rol no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        usuario.save()
        return Response(UsuarioSerializer(usuario).data)

