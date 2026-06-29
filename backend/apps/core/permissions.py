from apps.core.constants import Rol
from rest_framework.permissions import BasePermission, SAFE_METHODS


class EsStaffInterno(BasePermission):
    """Solo Administrador, Veterinario, Recepcionista"""
    ROLES_INTERNOS = {Rol.ADMINISTRADOR, Rol.VETERINARIO, Rol.RECEPCIONISTA}

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.rol and
            request.user.rol.nombre in self.ROLES_INTERNOS
        )

class EsMedicoExternoReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not (request.user.is_authenticated and
                request.user.rol and
                request.user.rol.nombre == Rol.MEDICO_EXTERNO):
            return False
        # Solo lectura
        return request.method in SAFE_METHODS

class EsPropietario(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.rol and
            request.user.rol.nombre == 'Propietario'
        )

    def has_object_permission(self, request, view, obj):
        # solo puede acceder a sus mascotas/ expedientes
        if hasattr(obj, 'propietario'):
            return obj.propietario == request.user
        if hasattr(obj, 'mascota'):
            return obj.mascota.propietario == request.user
        return False

class EsVeterinario(BasePermission):
    """Permite acceso solo a usuarios con rol 'Veterinario' (interno)."""
    message = "Solo un usuario con rol Veterinario puede realizar esta acción."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and
            user.rol and user.rol.nombre == 'Veterinario'
        )


class EsRecepcionOAdmin(BasePermission):
    message = "Solo Recepción o Administrador pueden realizar esta acción."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and
            user.rol and user.rol.nombre in ('Recepcionista', 'Administrador')
        )

def _usuario_tiene_permiso(usuario, codigo_permiso):
    if not usuario or not usuario.is_authenticated:
        return False
    if usuario.is_superuser:
        return True
    if not usuario.rol:
        return False
    return usuario.rol.permisos_rol.filter(permiso__codigo=codigo_permiso).exists()


def TienePermisoPorMetodo(ver, escribir):
    """
    Factory: exige `ver` para GET/HEAD/OPTIONS y `escribir` para
    POST/PUT/PATCH/DELETE. Útil para vistas donde Cliente solo lee
    y Administrador gestiona.
    """

    class _TienePermisoPorMetodo(BasePermission):
        def has_permission(self, request, view):
            codigo = ver if request.method in ('GET', 'HEAD', 'OPTIONS') else escribir
            return _usuario_tiene_permiso(request.user, codigo)

        def has_object_permission(self, request, view, obj):
            codigo = ver if request.method in ('GET', 'HEAD', 'OPTIONS') else escribir
            return _usuario_tiene_permiso(request.user, codigo)

    return _TienePermisoPorMetodo