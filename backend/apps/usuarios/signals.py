from django.db.models.signals import post_save
from django.dispatch import receiver

ROLES_MEDICO = {'Veterinario', 'Medico Externo'}


@receiver(post_save, sender='usuarios.Usuario')
def sincronizar_propietario(sender, instance, **kwargs):
    """
    Cuando un Usuario es guardado con rol 'Propietario', crea el registro
    Propietario vinculado si todavía no existe.
    Si el rol cambia a otro diferente, elimina el registro Propietario
    para mantener consistencia.
    """
    from apps.propietario.models import Propietario

    es_propietario = instance.rol and instance.rol.nombre == 'Propietario'

    if es_propietario:
        Propietario.objects.get_or_create(usuario=instance)
    else:
        Propietario.objects.filter(usuario=instance).delete()


@receiver(post_save, sender='usuarios.Usuario')
def sincronizar_medico(sender, instance, **kwargs):
    """
    Cuando un Usuario es guardado con rol 'Veterinario' o 'Medico Externo',
    crea el registro MedicoVeterinario vinculado si todavía no existe.
    Si el rol cambia a otro, elimina el registro para mantener consistencia.
    """
    from apps.medico.models import MedicoVeterinario

    es_medico = instance.rol and instance.rol.nombre in ROLES_MEDICO

    if es_medico:
        MedicoVeterinario.objects.get_or_create(usuario=instance)
    else:
        MedicoVeterinario.objects.filter(usuario=instance).delete()
