from django.contrib import admin
from .models import MedicoVeterinario


@admin.register(MedicoVeterinario)
class MedicoVeterinarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_nombre', 'get_apellido', 'especialidad', 'clinica_procedencia', 'get_correo', 'get_telefono']
    search_fields = ['usuario__first_name', 'usuario__last_name', 'usuario__email', 'especialidad']
    list_filter = ['especialidad']

    def get_nombre(self, obj):
        return obj.usuario.first_name if obj.usuario else '-'
    get_nombre.short_description = 'Nombre'

    def get_apellido(self, obj):
        return obj.usuario.last_name if obj.usuario else '-'
    get_apellido.short_description = 'Apellido'

    def get_correo(self, obj):
        return obj.usuario.email if obj.usuario else '-'
    get_correo.short_description = 'Correo'

    def get_telefono(self, obj):
        return obj.usuario.telefono if obj.usuario else '-'
    get_telefono.short_description = 'Teléfono'
