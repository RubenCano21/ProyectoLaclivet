"""Utilidades para registrar eventos en la bit\u00e1cora."""
import ipaddress

from .models import Bitacora


def _to_ipv4(ip_str: str) -> str:
    """Devuelve la representación IPv4 de una IP.
    Si es una IPv6 mapeada a IPv4 (::ffff:x.x.x.x), extrae la parte IPv4.
    De lo contrario retorna la IP tal cual.
    """
    try:
        addr = ipaddress.ip_address(ip_str)
        if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped:
            return str(addr.ipv4_mapped)
    except ValueError:
        pass
    return ip_str


def _client_ip(request):
    if request is None:
        return None
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    raw = xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')
    return _to_ipv4(raw) if raw else None


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
