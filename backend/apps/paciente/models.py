from django.db import models


class Especie(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Especie'
        verbose_name_plural = 'Especies'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

