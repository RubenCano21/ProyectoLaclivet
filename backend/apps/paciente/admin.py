from django.contrib import admin
from .models import Especie, Raza, HistorialClinico


@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre']
    search_fields = ['nombre']


@admin.register(Raza)
class RazaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'especie', 'descripcion']
    search_fields = ['nombre']
    list_filter = ['especie']


@admin.register(HistorialClinico)
class HistorialClinicoAdmin(admin.ModelAdmin):
    list_display = ['id', 'fecha_creacion', 'usuario']
    search_fields = ['antecedentes', 'observaciones']
    list_filter = ['fecha_creacion']
