from django.contrib import admin
from .models import CatalogoExamen, Examen


@admin.register(CatalogoExamen)
class CatalogoExamenAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'area', 'precio']
    search_fields = ['nombre', 'area']
    list_filter = ['area']


@admin.register(Examen)
class ExamenAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre_examen', 'categoria', 'catalogo']
    search_fields = ['nombre_examen', 'categoria']
    list_filter = ['catalogo', 'categoria']
