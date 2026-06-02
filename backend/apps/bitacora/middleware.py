"""Middleware para registrar autom\u00e1ticamente eventos en la bit\u00e1cora."""
import re

from .utils import registrar_evento


# Mapa de prefijo de URL -> nombre del m\u00f3dulo
MODULE_MAP = [
    ('/api/usuarios/auth/login',     'auth'),
    ('/api/usuarios/auth/logout',    'auth'),
    ('/api/usuarios/auth/registro',  'usuarios'),
    ('/api/usuarios/auth',           'auth'),
    ('/api/usuarios/cambiar-password', 'auth'),
    ('/api/usuarios/perfil',         'usuarios'),
    ('/api/usuarios',                'usuarios'),
    ('/api/propietarios',            'propietarios'),
    ('/api/catalogos',               'catalogos'),
    ('/api/medicos',                 'medicos'),
    ('/api/pacientes',               'pacientes'),
    ('/api/recepcion',               'recepcion'),
    ('/api/muestras',                'muestras'),
    ('/api/bitacora',                'bitacora'),
]

METHOD_VERB = {
    'POST': 'Cre\u00f3',
    'PUT': 'Actualiz\u00f3',
    'PATCH': 'Actualiz\u00f3',
    'DELETE': 'Elimin\u00f3',
    'GET': 'Consult\u00f3',
}

# Slugs human-readable por m\u00f3dulo y m\u00e9todo
ENTITY_LABEL = {
    'usuarios': 'usuario',
    'propietarios': 'propietario',
    'catalogos': 'cat\u00e1logo',
    'medicos': 'm\u00e9dico',
    'pacientes': 'paciente',
    'recepcion': 'recepci\u00f3n',
    'muestras': 'muestra',
    'bitacora': 'registro de bit\u00e1cora',
    'auth': 'sesi\u00f3n',
}


def _detect_module(path: str):
    for prefix, mod in MODULE_MAP:
        if path.startswith(prefix):
            return mod
    return None


def _is_listing(path: str) -> bool:
    # GET /api/foo/ \u2192 listado.  GET /api/foo/<id>/ \u2192 detalle.
    tail = path.rstrip('/').split('/')[-1]
    return not tail.isdigit()


class BitacoraMiddleware:
    """Registra cada request que modifica datos en la bit\u00e1cora.

    - Solo se registran requests bajo /api/.
    - GET solo se registra si es a un detalle/listado de m\u00f3dulo conocido
      y el usuario est\u00e1 autenticado (para no inundar la tabla).
    - El login/logout/registro se registran aunque la request no traiga usuario.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        try:
            path = request.path or ''
            if not path.startswith('/api/'):
                return response

            method = request.method
            modulo = _detect_module(path)
            if modulo is None:
                return response

            # No registrar errores de cliente (4xx/5xx) excepto login fallido
            status = getattr(response, 'status_code', 200)
            is_auth_event = modulo == 'auth'
            if status >= 400 and not is_auth_event:
                return response

            user = getattr(request, 'user', None)
            authenticated = bool(user and getattr(user, 'is_authenticated', False))

            # Filtrar GETs ruidosos
            if method == 'GET' and not authenticated:
                return response
            if method == 'GET' and modulo == 'bitacora':
                # No registrar la consulta de la propia bit\u00e1cora
                return response

            verbo = METHOD_VERB.get(method, method)
            entidad = ENTITY_LABEL.get(modulo, modulo)

            if is_auth_event and 'login' in path:
                accion = 'Inicio de sesi\u00f3n exitoso' if status < 400 else 'Intento de inicio de sesi\u00f3n fallido'
            elif is_auth_event and 'logout' in path:
                accion = 'Cierre de sesi\u00f3n'
            elif method == 'GET':
                accion = f'Consult\u00f3 {"listado de" if _is_listing(path) else "detalle de"} {entidad}'
            else:
                accion = f'{verbo} {entidad} ({method} {path})'

            registrar_evento(request, modulo, accion, usuario=user if authenticated else None)
        except Exception:
            # Nunca romper la respuesta por un fallo de auditor\u00eda
            pass

        return response
