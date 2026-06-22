from django.conf import settings
from django.db import models


class MedicoVeterinario(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medico_perfil',
        null=True, blank=True  # null hasta que se le asigne usuario
    )
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    clinica_procedencia = models.CharField(max_length=200, blank=True, null=True)
    genero = models.CharField(max_length=20, choices=GENERO_CHOICES, blank=True, null=True)

    # Eliminar: nombre, apellido, ci, telefono, correo, direccion
    # → esos datos van en Usuario

    class Meta:
        verbose_name = 'Médico Veterinario'
        verbose_name_plural = 'Médicos Veterinarios'

    def __str__(self):
        if self.usuario:
            return f"Dr(a). {self.usuario.first_name} {self.usuario.last_name}"
        return "Médico sin usuario"

