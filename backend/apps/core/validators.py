# apps/core/validators.py
import re
from django.core.exceptions import ValidationError


def validar_formato_ci(value):
    if value and not re.match(r'^\d{5,10}$', value):
        raise ValidationError("El CI solo puede contener números (5 a 10 dígitos).")


def validar_ci_unico_global(
    value,
    exclude_usuario_pk=None,
    exclude_propietario_pk=None,
    exclude_medico_pk=None
):
    if not value:
        return

    from apps.usuarios.models import Usuario
    from apps.propietario.models import Propietario
    from apps.medico.models import MedicoVeterinario

    # Verificar en Usuario
    qs_usuario = Usuario.objects.filter(ci=value)
    if exclude_usuario_pk:
        qs_usuario = qs_usuario.exclude(pk=exclude_usuario_pk)
    if qs_usuario.exists():
        raise ValidationError("Este CI ya está registrado como usuario del sistema.")

    # Propietario ya no tiene ci propio — el ci vive en su usuario
    # Se excluye el usuario del propietario para no generar falso positivo al actualizar
    if exclude_propietario_pk:
        try:
            propietario = Propietario.objects.get(pk=exclude_propietario_pk)
            if propietario.usuario:
                qs_usuario = qs_usuario.exclude(pk=propietario.usuario.pk)
        except Propietario.DoesNotExist:
            pass

    # Verificar en MedicoVeterinario — el ci también vive en su usuario
    if exclude_medico_pk:
        try:
            medico = MedicoVeterinario.objects.get(pk=exclude_medico_pk)
            if medico.usuario:
                qs_usuario = qs_usuario.exclude(pk=medico.usuario.pk)
        except MedicoVeterinario.DoesNotExist:
            pass

def generar_username(email: str) -> str:
    from apps.usuarios.models import Usuario
    base = (email or '').split('@')[0][:140] or 'user'
    username = base
    i = 1
    while Usuario.objects.filter(username=username).exists():
        i += 1
        username = f"{base}{i}"[:150]
    return username

def generar_password_default(last_name: str, ci: str) -> str:
    primer_apellido = last_name.strip().lower().split()[0] if last_name.strip() else 'usuario'
    return f"{primer_apellido}.{ci}" if ci else primer_apellido