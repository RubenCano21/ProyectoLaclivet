from django.db import models


class Muestra(models.Model):
    ESTADO_CHOICES = [
        ('recibida', 'Recibida'),
        ('en_proceso', 'En proceso'),
        ('procesada', 'Procesada'),
        ('descartada', 'Descartada'),
    ]

    codigo = models.CharField(max_length=50, unique=True)
    tipo_muestra = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='recibida')
    solicitud = models.ForeignKey(
        'recepcion.SolicitudExamen', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='muestras'
    )

    class Meta:
        verbose_name = 'Muestra'
        verbose_name_plural = 'Muestras'
        ordering = ['codigo']

    def __str__(self):
        return f"Muestra {self.codigo} - {self.estado}"


class IncidenciaMuestra(models.Model):
    fecha_registro = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)
    muestra = models.ForeignKey(
        Muestra, on_delete=models.CASCADE, related_name='incidencias'
    )

    class Meta:
        verbose_name = 'Incidencia de Muestra'
        verbose_name_plural = 'Incidencias de Muestras'
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"Incidencia #{self.pk} - {self.muestra.codigo}"
