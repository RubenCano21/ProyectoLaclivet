from django.contrib import admin
from .models import Especie, Raza, Paciente, AntecedentePaciente


@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre']
    search_fields = ['nombre']


@admin.register(Raza)
class RazaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'especie']
    search_fields = ['nombre']
    list_filter = ['especie']


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'sexo', 'tamanio', 'color', 'fecha_nacimiento', 'raza', 'propietario']
    search_fields = ['nombre']
    list_filter = ['sexo', 'tamanio', 'raza__especie']


@admin.register(AntecedentePaciente)
class AntecedentePacienteAdmin(admin.ModelAdmin):
    list_display = ['id', 'paciente', 'tipo', 'fecha_registro', 'registrado_por']
    list_filter = ['tipo', 'fecha_registro']
    search_fields = ['paciente__nombre', 'descripcion']
