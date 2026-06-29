from django.db import models


class Muestra(models.Model):
    ESTADO_CHOICES = [
        ('pendiente',  'Pendiente'),
        ('en_proceso', 'En proceso'),
        ('completada', 'Completada'),
        ('rechazada',  'Rechazada'),
    ]

    codigo = models.CharField(max_length=50, unique=True)
    tipo_muestra = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='pendiente')
    fecha_recepcion = models.DateField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    paciente = models.ForeignKey(
        'paciente.Paciente', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='muestras'
    )
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

class Resultado(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En proceso'),
        ('completado', 'Completado'),
        ('validado', 'Validado'),
    ]

    detalle_solicitud = models.OneToOneField(
        'recepcion.DetalleSolicitud',
        on_delete=models.CASCADE,
        related_name='resultado'
    )
    muestra = models.ForeignKey(
        Muestra,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='resultados'
    )
    veterinario_responsable = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='resultados_emitidos'
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    valores_obtenidos = models.JSONField(
        blank=True, null=True,
        help_text="Valores del examen en formato JSON. Ej: {'glucosa': '95 mg/dL'}"
    )
    observaciones = models.TextField(blank=True, null=True)
    fecha_emision = models.DateTimeField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    archivo_pdf = models.FileField(
        upload_to='resultados/',
        blank=True, null=True,
        help_text="PDF del resultado generado"
    )

    class Meta:
        verbose_name = 'Resultado'
        verbose_name_plural = 'Resultados'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Resultado #{self.pk} - {self.detalle_solicitud.solicitud.codigo}"

    @property
    def paciente(self):
        return self.detalle_solicitud.solicitud.paciente

    @property
    def medico_solicitante(self):
        return self.detalle_solicitud.solicitud.medico_veterinario

    @property
    def examen(self):
        return self.detalle_solicitud.examen