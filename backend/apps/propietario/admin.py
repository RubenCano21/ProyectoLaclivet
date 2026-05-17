from django.contrib import admin
from .models import Propietario


@admin.register(Propietario)
class PropietarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'ci', 'nombre', 'apellido', 'correo', 'telefono']
    search_fields = ['ci', 'nombre', 'apellido', 'correo']
    ordering = ['apellido', 'nombre']

