"""Utilidades para registrar eventos en la bit\u00e1cora."""
from .models import Bitacora


def _client_ip(request):
    if request is None:
        return None
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def registrar_evento(request, modulo, accion, usuario=None):
    """Crea un registro en la bit\u00e1cora. Nunca lanza excepciones."""
    try:
        if usuario is None and request is not None:
            u = getattr(request, 'user', None)
            if u is not None and getattr(u, 'is_authenticated', False):
                usuario = u
        Bitacora.objects.create(
            modulo=modulo,
            accion_realizada=accion,
            direccion_ip=_client_ip(request),
            usuario=usuario,
        )
    except Exception:
        pass
