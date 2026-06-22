from rest_framework.permissions import BasePermission

class EsStaffInterno(BasePermission):
    """Solo Administrador, Veterinario, Recepcionista"""
    ROLES_INTERNOS = {'Administrador', 'Veterinario', 'Recepcionista'}

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.rol and
            request.user.rol.nombre in self.ROLES_INTERNOS
        )

class EsMedicoExterno(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.rol and
            request.user.rol.nombre == 'Medico Externo'
        )

class EsPropietario(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.rol and
            request.user.rol.nombre == 'Propietario'
        )