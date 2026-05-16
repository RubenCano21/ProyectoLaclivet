from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Rol, Permiso, RolPermiso


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'descripcion']
    search_fields = ['nombre']
    ordering = ['nombre']


@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'codigo', 'descripcion']
    search_fields = ['nombre', 'codigo']
    ordering = ['nombre']


@admin.register(RolPermiso)
class RolPermisoAdmin(admin.ModelAdmin):
    list_display = ['id', 'rol', 'permiso']
    list_filter = ['rol']
    search_fields = ['rol__nombre', 'permiso__nombre']
    ordering = ['rol', 'permiso']


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'rol', 'is_active', 'fecha_creacion']
    list_filter = ['is_active', 'is_staff', 'rol', 'fecha_creacion']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-fecha_creacion']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('username', 'first_name', 'last_name', 'telefono', 'direccion', 'fecha_nacimiento')}),
        ('Permisos y Rol', {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined', 'fecha_creacion', 'fecha_actualizacion')}),
    )

    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'last_login', 'date_joined']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'first_name', 'last_name', 'rol'),
        }),
    )

