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
        """Solo puede acceder a sus propias mascotas/expedientes.

        OJO: `obj.propietario` es una instancia de `Propietario`, no de
        `Usuario` — se debe comparar contra `propietario.usuario`.
        """
        propietario = getattr(obj, 'propietario', None)
        if propietario is not None:
            return getattr(propietario, 'usuario', None) == request.user

        mascota = getattr(obj, 'mascota', None)
        if mascota is not None:
            propietario_mascota = getattr(mascota, 'propietario', None)
            if propietario_mascota is not None:
                return getattr(propietario_mascota, 'usuario', None) == request.user
        return False


def es_propietario_de(usuario, paciente):
    """Verifica si `usuario` es el dueño (vía Propietario.usuario) del `paciente`."""
    if not usuario or not getattr(usuario, 'is_authenticated', False):
        return False
    if not paciente or not paciente.propietario:
        return False
    return paciente.propietario.usuario_id == usuario.id


def tiene_rol(usuario, *nombres_rol):
    return bool(
        usuario and usuario.is_authenticated and
        usuario.rol and usuario.rol.nombre in nombres_rol
    )

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