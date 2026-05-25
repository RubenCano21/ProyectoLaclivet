from django.db import models
from django.conf import settings


class Especie(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Especie'
        verbose_name_plural = 'Especies'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Raza(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    especie = models.ForeignKey(Especie, on_delete=models.CASCADE, related_name='razas')

    class Meta:
        verbose_name = 'Raza'
        verbose_name_plural = 'Razas'
        ordering = ['nombre']
        unique_together = ['nombre', 'especie']

    def __str__(self):
        return f"{self.nombre} ({self.especie.nombre})"


class HistorialClinico(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    antecedentes = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historiales'
    )

    class Meta:
        verbose_name = 'Historial Clínico'
        verbose_name_plural = 'Historiales Clínicos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Historial #{self.pk} - {self.fecha_creacion.strftime('%d/%m/%Y')}"


class Paciente(models.Model):
    SEXO_CHOICES = [
        ('macho', 'Macho'),
        ('hembra', 'Hembra'),
        ('desconocido', 'Desconocido'),
    ]
    TAMANIO_CHOICES = [
        ('pequeño', 'Pequeño'),
        ('mediano', 'Mediano'),
        ('grande', 'Grande'),
    ]

    nombre = models.CharField(max_length=100)
    sexo = models.CharField(max_length=20, choices=SEXO_CHOICES, blank=True, null=True)
    tamanio = models.CharField(max_length=20, choices=TAMANIO_CHOICES, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    historial_clinico = models.OneToOneField(
        HistorialClinico, on_delete=models.CASCADE, related_name='paciente'
    )
    propietario = models.ForeignKey(
        'propietario.Propietario', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='pacientes'
    )
    raza = models.ForeignKey(
        Raza, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='pacientes'
    )

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.raza})"
