from django.contrib import admin
from .models import Cobro, SolicitudExamen, DetalleSolicitud


@admin.register(Cobro)
class CobroAdmin(admin.ModelAdmin):
    list_display = ['id', 'monto_total', 'metodo_pago', 'fecha']
    list_filter = ['metodo_pago']


@admin.register(SolicitudExamen)
class SolicitudExamenAdmin(admin.ModelAdmin):
    list_display = ['id', 'codigo', 'estado', 'fecha_solicitud', 'paciente', 'medico_veterinario']
    search_fields = ['codigo']
    list_filter = ['estado']


@admin.register(DetalleSolicitud)
class DetalleSolicitudAdmin(admin.ModelAdmin):
    list_display = ['id', 'solicitud', 'examen', 'precio_aplicado']
    list_filter = ['solicitud']
