from django.db import models


class CatalogoExamen(models.Model):
    nombre = models.CharField(max_length=100)
    area = models.CharField(max_length=50, blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name = 'Catálogo de Examen'
        verbose_name_plural = 'Catálogos de Exámenes'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

