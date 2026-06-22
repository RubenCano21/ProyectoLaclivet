from django.core.management.base import BaseCommand
from apps.usuarios.models import Rol, Permiso, RolPermiso


class Command(BaseCommand):
    help = "Crea los roles y permisos iniciales del sistema"

    def handle(self, *args, **options):
        self.stdout.write("Creando roles y permisos iniciales...\n")

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
            status = "Creado" if created else "Ya existe"
            self.stdout.write(f"{status}: Rol '{rol.nombre}'")

        permisos_data = [
            {'nombre': 'Crear Usuario', 'codigo': 'crear_usuario', 'descripcion': 'Crear nuevos usuarios'},
            {'nombre': 'Editar Usuario', 'codigo': 'editar_usuario', 'descripcion': 'Editar usuarios existentes'},
            {'nombre': 'Eliminar Usuario', 'codigo': 'eliminar_usuario', 'descripcion': 'Eliminar usuarios'},
            {'nombre': 'Ver Usuarios', 'codigo': 'ver_usuarios', 'descripcion': 'Ver lista de usuarios'},
            {'nombre': 'Crear Mascota', 'codigo': 'crear_mascota', 'descripcion': 'Registrar nuevas mascotas'},
            {'nombre': 'Editar Mascota', 'codigo': 'editar_mascota', 'descripcion': 'Editar datos de mascotas'},
            {'nombre': 'Eliminar Mascota', 'codigo': 'eliminar_mascota', 'descripcion': 'Eliminar mascotas'},
            {'nombre': 'Ver Mascotas', 'codigo': 'ver_mascotas', 'descripcion': 'Ver lista de mascotas'},
            {'nombre': 'Crear Cita', 'codigo': 'crear_cita', 'descripcion': 'Programar nuevas citas'},
            {'nombre': 'Editar Cita', 'codigo': 'editar_cita', 'descripcion': 'Modificar citas'},
            {'nombre': 'Cancelar Cita', 'codigo': 'cancelar_cita', 'descripcion': 'Cancelar citas'},
            {'nombre': 'Ver Citas', 'codigo': 'ver_citas', 'descripcion': 'Ver citas programadas'},
            {'nombre': 'Crear Consulta', 'codigo': 'crear_consulta', 'descripcion': 'Registrar consultas médicas'},
            {'nombre': 'Ver Consultas', 'codigo': 'ver_consultas', 'descripcion': 'Ver historial de consultas'},
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
            status = "Creado" if created else "Ya existe"
            self.stdout.write(f"{status}: Permiso '{permiso.nombre}' ({permiso.codigo})")

        self.stdout.write("\nAsignando permisos a roles...\n")

        for permiso in permisos.values():
            RolPermiso.objects.get_or_create(rol=roles['Administrador'], permiso=permiso)
        self.stdout.write(f"Administrador: {len(permisos)} permisos asignados")

        permisos_veterinario = [
            'ver_usuarios', 'ver_mascotas', 'editar_mascota',
            'crear_cita', 'editar_cita', 'ver_citas',
            'crear_consulta', 'ver_consultas', 'ver_reportes'
        ]
        for codigo in permisos_veterinario:
            RolPermiso.objects.get_or_create(rol=roles['Veterinario'], permiso=permisos[codigo])
        self.stdout.write(f"Veterinario: {len(permisos_veterinario)} permisos asignados")

        permisos_recepcionista = [
            'ver_usuarios', 'crear_mascota', 'editar_mascota', 'ver_mascotas',
            'crear_cita', 'editar_cita', 'cancelar_cita', 'ver_citas'
        ]
        for codigo in permisos_recepcionista:
            RolPermiso.objects.get_or_create(rol=roles['Recepcionista'], permiso=permisos[codigo])
        self.stdout.write(f"Recepcionista: {len(permisos_recepcionista)} permisos asignados")

        permisos_cliente = ['ver_mascotas', 'crear_cita', 'ver_citas', 'ver_consultas']
        for codigo in permisos_cliente:
            RolPermiso.objects.get_or_create(rol=roles['Cliente'], permiso=permisos[codigo])
        self.stdout.write(f"Cliente: {len(permisos_cliente)} permisos asignados")

        self.stdout.write(self.style.SUCCESS("\nRoles y permisos creados exitosamente!"))