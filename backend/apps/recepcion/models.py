from django.db import models


class Cobro(models.Model):
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('qr', 'QR'),
    ]

    monto_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    metodo_pago = models.CharField(max_length=50, choices=METODO_PAGO_CHOICES, blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Cobro'
        verbose_name_plural = 'Cobros'
        ordering = ['-fecha']

    def __str__(self):
        return f"Cobro #{self.id} - Bs. {self.monto_total}"


class SolicitudExamen(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En proceso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]

    codigo = models.CharField(max_length=50, unique=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='pendiente')
    cobro = models.OneToOneField(
        Cobro, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='solicitud'
    )
    historial_clinico = models.ForeignKey(
        'paciente.HistorialClinico', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='solicitudes'
    )
    medico_veterinario = models.ForeignKey(
        'medico.MedicoVeterinario', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='solicitudes'
    )

    class Meta:
        verbose_name = 'Solicitud de Examen'
        verbose_name_plural = 'Solicitudes de Examen'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"Solicitud {self.codigo} - {self.estado}"


class DetalleSolicitud(models.Model):
    precio_aplicado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    solicitud = models.ForeignKey(
        SolicitudExamen, on_delete=models.CASCADE, related_name='detalles'
    )
    examen = models.ForeignKey(
        'catalogo.Examen', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='detalles_solicitud'
    )

    class Meta:
        verbose_name = 'Detalle de Solicitud'
        verbose_name_plural = 'Detalles de Solicitud'

    def __str__(self):
        return f"Detalle #{self.pk} - {self.solicitud.codigo}"
