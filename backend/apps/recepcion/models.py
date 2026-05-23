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

