from django.contrib import admin
from .models import Muestra, IncidenciaMuestra

@admin.register(Muestra)
class MuestraAdmin(admin.ModelAdmin):
    list_display = ['id', 'codigo', 'tipo_muestra', 'estado', 'solicitud']
    search_fields = ['codigo']
    list_filter = ['estado']

@admin.register(IncidenciaMuestra)
class IncidenciaMuestraAdmin(admin.ModelAdmin):
    list_display = ['id', 'muestra', 'fecha_registro']
    list_filter = ['fecha_registro']
    readonly_fields = ['fecha_registro']
