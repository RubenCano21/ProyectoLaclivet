from django.contrib import admin
from .models import MedicoVeterinario


@admin.register(MedicoVeterinario)
class MedicoVeterinarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'apellido', 'especialidad', 'genero', 'correo', 'telefono']
    search_fields = ['nombre', 'apellido', 'especialidad', 'correo']
    list_filter = ['especialidad', 'genero']

