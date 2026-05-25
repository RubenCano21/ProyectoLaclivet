from django.contrib import admin
from .models import Especie, Raza, HistorialClinico, Paciente


@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre']
    search_fields = ['nombre']


@admin.register(Raza)
class RazaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'especie']
    search_fields = ['nombre']
    list_filter = ['especie']


@admin.register(HistorialClinico)
class HistorialClinicoAdmin(admin.ModelAdmin):
    list_display = ['id', 'fecha_creacion', 'usuario']
    list_filter = ['fecha_creacion']


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'sexo', 'tamanio', 'color', 'raza', 'propietario']
    search_fields = ['nombre']
    list_filter = ['sexo', 'tamanio', 'raza__especie']
