from django.contrib.auth.models import AbstractUser
from django.db import models


class Rol(models.Model):
    """Modelo para los roles del sistema"""
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre


class Permiso(models.Model):
    """Modelo para los permisos del sistema"""
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=50, unique=True)  # Ej: 'crear_usuario', 'editar_mascota'
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'

    def __str__(self):
        return self.nombre


class RolPermiso(models.Model):
    """Relación entre roles y permisos"""
    id = models.AutoField(primary_key=True)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='permisos_rol')
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE, related_name='roles_permiso')

    class Meta:
        verbose_name = 'Rol-Permiso'
        verbose_name_plural = 'Roles-Permisos'
        unique_together = ['rol', 'permiso']

    def __str__(self):
        return f"{self.rol.nombre} - {self.permiso.nombre}"


class Usuario(AbstractUser):
    """Modelo de usuario personalizado que extiende AbstractUser"""
    # AbstractUser ya incluye: username, password, email, first_name, last_name, etc.

    # Sobrescribir el campo email para hacerlo único y requerido
    email = models.EmailField(
        'email address',
        unique=True,
        error_messages={
            'unique': 'Ya existe un usuario con este email.',
        }
    )

    # Campos adicionales
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)

    # Relación con rol
    rol = models.ForeignKey(
        Rol,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios'
    )

    # Campos de auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    # Configurar el campo de autenticación principal
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.email

    def get_permisos(self):
        """Obtiene todos los permisos del usuario basados en su rol"""
        if self.rol:
            return Permiso.objects.filter(
                roles_permiso__rol=self.rol
            ).distinct()
        return Permiso.objects.none()

    def tiene_permiso(self, codigo_permiso):
        """Verifica si el usuario tiene un permiso específico"""
        return self.get_permisos().filter(codigo=codigo_permiso).exists()
