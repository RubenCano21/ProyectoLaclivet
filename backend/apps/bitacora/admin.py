from django.contrib import admin
from .models import Bitacora

@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = ['id', 'modulo', 'accion_realizada', 'fecha', 'direccion_ip', 'usuario']
    search_fields = ['modulo', 'accion_realizada']
    list_filter = ['modulo', 'fecha']
    readonly_fields = ['fecha']
