from django.db import models


class MedicoVeterinario(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    ci = models.CharField(max_length=10, blank=True, null=True, unique=True)
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    genero = models.CharField(max_length=20, choices=GENERO_CHOICES, blank=True, null=True)
    correo = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = 'Médico Veterinario'
        verbose_name_plural = 'Médicos Veterinarios'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"Dr(a). {self.nombre} {self.apellido}"

