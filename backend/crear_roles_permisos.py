"""
Script para crear datos iniciales: roles y permisos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.usuarios.models import Rol, Permiso, RolPermiso


def crear_roles_y_permisos():
    """Crear roles y permisos iniciales del sistema"""

    print("🔧 Creando roles y permisos iniciales...\n")

    # Crear roles
    roles_data = [
        {'nombre': 'Administrador', 'descripcion': 'Acceso total al sistema'},
        {'nombre': 'Veterinario', 'descripcion': 'Gestión de consultas y tratamientos'},
        {'nombre': 'Recepcionista', 'descripcion': 'Gestión de citas y clientes'},
        {'nombre': 'Cliente', 'descripcion': 'Usuario cliente de la clínica'},
    ]

    roles = {}
    for rol_data in roles_data:
        rol, created = Rol.objects.get_or_create(
            nombre=rol_data['nombre'],
            defaults={'descripcion': rol_data['descripcion']}
        )
        roles[rol_data['nombre']] = rol
        status = "✓ Creado" if created else "○ Ya existe"
        print(f"{status}: Rol '{rol.nombre}'")

    print()

    # Crear permisos
    permisos_data = [
        # Usuarios
        {'nombre': 'Crear Usuario', 'codigo': 'crear_usuario', 'descripcion': 'Crear nuevos usuarios'},
        {'nombre': 'Editar Usuario', 'codigo': 'editar_usuario', 'descripcion': 'Editar usuarios existentes'},
        {'nombre': 'Eliminar Usuario', 'codigo': 'eliminar_usuario', 'descripcion': 'Eliminar usuarios'},
        {'nombre': 'Ver Usuarios', 'codigo': 'ver_usuarios', 'descripcion': 'Ver lista de usuarios'},

        # Mascotas
        {'nombre': 'Crear Mascota', 'codigo': 'crear_mascota', 'descripcion': 'Registrar nuevas mascotas'},
        {'nombre': 'Editar Mascota', 'codigo': 'editar_mascota', 'descripcion': 'Editar datos de mascotas'},
        {'nombre': 'Eliminar Mascota', 'codigo': 'eliminar_mascota', 'descripcion': 'Eliminar mascotas'},
        {'nombre': 'Ver Mascotas', 'codigo': 'ver_mascotas', 'descripcion': 'Ver lista de mascotas'},

        # Citas
        {'nombre': 'Crear Cita', 'codigo': 'crear_cita', 'descripcion': 'Programar nuevas citas'},
        {'nombre': 'Editar Cita', 'codigo': 'editar_cita', 'descripcion': 'Modificar citas'},
        {'nombre': 'Cancelar Cita', 'codigo': 'cancelar_cita', 'descripcion': 'Cancelar citas'},
        {'nombre': 'Ver Citas', 'codigo': 'ver_citas', 'descripcion': 'Ver citas programadas'},

        # Consultas
        {'nombre': 'Crear Consulta', 'codigo': 'crear_consulta', 'descripcion': 'Registrar consultas médicas'},
        {'nombre': 'Ver Consultas', 'codigo': 'ver_consultas', 'descripcion': 'Ver historial de consultas'},

        # Reportes
        {'nombre': 'Ver Reportes', 'codigo': 'ver_reportes', 'descripcion': 'Acceso a reportes del sistema'},
    ]

    permisos = {}
    for permiso_data in permisos_data:
        permiso, created = Permiso.objects.get_or_create(
            codigo=permiso_data['codigo'],
            defaults={
                'nombre': permiso_data['nombre'],
                'descripcion': permiso_data['descripcion']
            }
        )
        permisos[permiso_data['codigo']] = permiso
        status = "✓ Creado" if created else "○ Ya existe"
        print(f"{status}: Permiso '{permiso.nombre}' ({permiso.codigo})")

    print()

    # Asignar permisos a roles
    print("🔗 Asignando permisos a roles...\n")

    # Administrador: todos los permisos
    for permiso in permisos.values():
        RolPermiso.objects.get_or_create(
            rol=roles['Administrador'],
            permiso=permiso
        )
    print(f"✓ Administrador: {len(permisos)} permisos asignados")

    # Veterinario: permisos relacionados con mascotas, consultas y citas
    permisos_veterinario = [
        'ver_usuarios', 'ver_mascotas', 'editar_mascota',
        'crear_cita', 'editar_cita', 'ver_citas',
        'crear_consulta', 'ver_consultas', 'ver_reportes'
    ]
    for codigo in permisos_veterinario:
        RolPermiso.objects.get_or_create(
            rol=roles['Veterinario'],
            permiso=permisos[codigo]
        )
    print(f"✓ Veterinario: {len(permisos_veterinario)} permisos asignados")

    # Recepcionista: permisos de gestión de citas y clientes
    permisos_recepcionista = [
        'ver_usuarios', 'crear_mascota', 'editar_mascota', 'ver_mascotas',
        'crear_cita', 'editar_cita', 'cancelar_cita', 'ver_citas'
    ]
    for codigo in permisos_recepcionista:
        RolPermiso.objects.get_or_create(
            rol=roles['Recepcionista'],
            permiso=permisos[codigo]
        )
    print(f"✓ Recepcionista: {len(permisos_recepcionista)} permisos asignados")

    # Cliente: permisos básicos
    permisos_cliente = [
        'ver_mascotas', 'crear_cita', 'ver_citas', 'ver_consultas'
    ]
    for codigo in permisos_cliente:
        RolPermiso.objects.get_or_create(
            rol=roles['Cliente'],
            permiso=permisos[codigo]
        )
    print(f"✓ Cliente: {len(permisos_cliente)} permisos asignados")

    print("\n✅ Roles y permisos creados exitosamente!")


if __name__ == '__main__':
    crear_roles_y_permisos()

