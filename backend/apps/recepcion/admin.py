from django.contrib import admin
from .models import Cobro


@admin.register(Cobro)
class CobroAdmin(admin.ModelAdmin):
    list_display = ['id', 'monto_total', 'metodo_pago', 'fecha']
    list_filter = ['metodo_pago']
    search_fields = ['metodo_pago']

