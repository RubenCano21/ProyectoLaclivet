from django.conf import settings
from django.db import models

class Propietario(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='propietario_perfil',
        null=True, blank=True
    )
    # Eliminar: nombre, apellido, ci, telefono, correo, direccion
    # → esos datos van en Usuario

    class Meta:
        verbose_name = 'Propietario'
        verbose_name_plural = 'Propietarios'

    def __str__(self):
        if self.usuario:
            return f"{self.usuario.first_name} {self.usuario.last_name}"
        return "Propietario sin usuario"
