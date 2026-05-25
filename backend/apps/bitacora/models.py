from django.db import models
from django.conf import settings


class Bitacora(models.Model):
    modulo = models.CharField(max_length=50, blank=True, null=True)
    accion_realizada = models.CharField(max_length=255, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    direccion_ip = models.GenericIPAddressField(blank=True, null=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bitacoras'
    )

    class Meta:
        verbose_name = 'Bitácora'
        verbose_name_plural = 'Bitácoras'
        ordering = ['-fecha']

    def __str__(self):
        return f"[{self.fecha.strftime('%d/%m/%Y %H:%M')}] {self.modulo} - {self.accion_realizada}"
