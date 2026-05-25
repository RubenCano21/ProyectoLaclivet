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


class Examen(models.Model):
    nombre_examen = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    catalogo = models.ForeignKey(CatalogoExamen, on_delete=models.CASCADE, related_name='examenes')

    class Meta:
        verbose_name = 'Examen'
        verbose_name_plural = 'Examenes'
        ordering = ['nombre_examen']

    def __str__(self):
        return f"{self.nombre_examen} ({self.catalogo.nombre})"


class Parametro(models.Model):
    nombre_parametro = models.CharField(max_length=100)
    unidad_medida = models.CharField(max_length=20, blank=True, null=True)
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE, related_name='parametros')

    class Meta:
        verbose_name = 'Parámetro'
        verbose_name_plural = 'Parámetros'
        ordering = ['nombre_parametro']

    def __str__(self):
        return f"{self.nombre_parametro} ({self.examen.nombre_examen})"


class ValorReferencia(models.Model):
    valor_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valor_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    especie = models.CharField(max_length=50, blank=True, null=True)
    parametro = models.ForeignKey(Parametro, on_delete=models.CASCADE, related_name='valores_referencia')

    class Meta:
        verbose_name = 'Valor de Referencia'
        verbose_name_plural = 'Valores de Referencia'
        ordering = ['parametro']

    def __str__(self):
        return f"{self.parametro.nombre_parametro} [{self.valor_min} - {self.valor_max}] ({self.especie})"
