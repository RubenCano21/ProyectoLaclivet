import re
from django.core.exceptions import ValidationError


def validar_formato_ci(value):
    """Valida que el CI solo contenga números (5 a 10 dígitos)."""
    if value and not re.match(r'^\d{5,10}$', value):
        raise ValidationError("El CI solo puede contener números (5 a 10 dígitos).")


def validar_ci_unico_global(value,
                            exclude_usuario_pk=None,
                            exclude_propietario_pk=None,
                            exclude_medico_pk=None):
    """Valida que el CI no esté registrado en ningún modelo del sistema."""
    if not value:
        return

    from apps.usuarios.models import Usuario
    from apps.propietario.models import Propietario
    from apps.medico.models import MedicoVeterinario

    qs_usuario = Usuario.objects.filter(ci=value)
    if exclude_usuario_pk:
        qs_usuario = qs_usuario.exclude(pk=exclude_usuario_pk)
    if qs_usuario.exists():
        raise ValidationError("Este CI ya está registrado como usuario del sistema.")

    qs_propietario = Propietario.objects.filter(ci=value)
    if exclude_propietario_pk:
        qs_propietario = qs_propietario.exclude(pk=exclude_propietario_pk)
    if qs_propietario.exists():
        raise ValidationError("Este CI ya está registrado como propietario.")

    qs_medico = MedicoVeterinario.objects.filter(ci=value)  # ← nuevo
    if exclude_medico_pk:
        qs_medico = qs_medico.exclude(pk=exclude_medico_pk)
    if qs_medico.exists():
        raise ValidationError("Este CI ya está registrado como médico veterinario.")