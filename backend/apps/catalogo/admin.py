from django.contrib import admin
from .models import CatalogoExamen, Examen, Parametro, ValorReferencia


@admin.register(CatalogoExamen)
class CatalogoExamenAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'area', 'precio']
    search_fields = ['nombre', 'area']


@admin.register(Examen)
class ExamenAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre_examen', 'categoria', 'catalogo']
    search_fields = ['nombre_examen', 'categoria']
    list_filter = ['catalogo', 'categoria']


@admin.register(Parametro)
class ParametroAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre_parametro', 'unidad_medida', 'examen']
    search_fields = ['nombre_parametro']
    list_filter = ['examen']


@admin.register(ValorReferencia)
class ValorReferenciaAdmin(admin.ModelAdmin):
    list_display = ['id', 'parametro', 'especie', 'valor_min', 'valor_max']
    search_fields = ['especie']
    list_filter = ['parametro', 'especie']
