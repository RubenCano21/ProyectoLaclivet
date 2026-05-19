from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    RegistroView,
    LoginView,
    LogoutView,
    PerfilUsuarioView,
    CambiarPasswordView,
    ListaUsuariosView,
    DetalleUsuarioView,
    verificar_token,
    ListaRolesView,
    ListaPermisosView,
    ActualizarRolPermisosView,
    AsignarRolUsuarioView,
)

app_name = 'usuarios'

urlpatterns = [
    # Autenticación con JWT
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/login/alternativo/', LoginView.as_view(), name='login_alternativo'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/verificar/', verificar_token, name='verificar_token'),

    # Registro y perfil
    path('auth/registro/', RegistroView.as_view(), name='registro'),
    path('perfil/', PerfilUsuarioView.as_view(), name='perfil'),
    path('cambiar-password/', CambiarPasswordView.as_view(), name='cambiar_password'),

    # Gestión de usuarios (admin)
    path('', ListaUsuariosView.as_view(), name='lista_usuarios'),
    path('<int:pk>/', DetalleUsuarioView.as_view(), name='detalle_usuario'),
    path('<int:pk>/asignar-rol/', AsignarRolUsuarioView.as_view(), name='asignar_rol'),

    # Roles y permisos
    path('roles/', ListaRolesView.as_view(), name='lista_roles'),
    path('permisos/', ListaPermisosView.as_view(), name='lista_permisos'),
    path('roles/<int:pk>/permisos/', ActualizarRolPermisosView.as_view(), name='actualizar_rol_permisos'),
]

