from django.contrib import admin
from .models import Propietario


@admin.register(Propietario)
class PropietarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_ci', 'get_nombre', 'get_apellido', 'get_correo', 'get_telefono']
    search_fields = ['usuario__first_name', 'usuario__last_name', 'usuario__email', 'usuario__ci']
    ordering = ['usuario__last_name', 'usuario__first_name']

    def get_ci(self, obj):
        return obj.usuario.ci if obj.usuario else '-'
    get_ci.short_description = 'CI'

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
