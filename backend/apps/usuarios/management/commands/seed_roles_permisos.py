from django.core.management.base import BaseCommand
from apps.usuarios.models import Rol, Permiso, RolPermiso


class Command(BaseCommand):
    help = "Crea los roles y permisos del sistema LACLIVET"

    def handle(self, *args, **options):
        self.stdout.write("Creando roles y permisos...\n")

        roles_data = [
            {'nombre': 'Administrador',  'descripcion': 'Acceso total al sistema'},
            {'nombre': 'Veterinario',    'descripcion': 'Gestión de resultados y consultas'},
            {'nombre': 'Recepcionista',  'descripcion': 'Recepción de muestras y solicitudes'},
            {'nombre': 'Medico Externo', 'descripcion': 'Acceso de solo lectura a resultados'},
            {'nombre': 'Propietario',    'descripcion': 'Propietario de pacientes (portal propio)'},
        ]

        roles = {}
        for rol_data in roles_data:
            rol, created = Rol.objects.get_or_create(
                nombre=rol_data['nombre'],
                defaults={'descripcion': rol_data['descripcion']}
            )
            roles[rol_data['nombre']] = rol
            self.stdout.write(f"{'Creado' if created else 'Existe'}: Rol '{rol.nombre}'")

        permisos_data = [
            # ── Usuarios ──────────────────────────────────────────────────────
            {'nombre': 'Ver Usuarios',         'codigo': 'ver_usuarios',         'descripcion': 'Ver lista de usuarios del sistema'},
            {'nombre': 'Crear Usuario',         'codigo': 'crear_usuario',        'descripcion': 'Crear nuevos usuarios'},
            {'nombre': 'Editar Usuario',        'codigo': 'editar_usuario',       'descripcion': 'Editar usuarios existentes'},
            {'nombre': 'Eliminar Usuario',      'codigo': 'eliminar_usuario',     'descripcion': 'Eliminar usuarios'},
            {'nombre': 'Ver Auditoría',         'codigo': 'ver_auditoria',        'descripcion': 'Ver bitácora de auditoría'},
            # ── Pacientes / Propietarios ──────────────────────────────────────
            {'nombre': 'Ver Pacientes',         'codigo': 'ver_pacientes',        'descripcion': 'Ver lista de pacientes'},
            {'nombre': 'Crear Paciente',        'codigo': 'crear_paciente',       'descripcion': 'Registrar nuevos pacientes'},
            {'nombre': 'Editar Paciente',       'codigo': 'editar_paciente',      'descripcion': 'Editar datos de pacientes'},
            {'nombre': 'Eliminar Paciente',     'codigo': 'eliminar_paciente',    'descripcion': 'Eliminar pacientes'},
            # ── Catálogo & Solicitudes ────────────────────────────────────────
            {'nombre': 'Ver Catálogo',          'codigo': 'ver_catalogo',         'descripcion': 'Ver catálogo de exámenes'},
            {'nombre': 'Gestionar Catálogo',    'codigo': 'gestionar_catalogo',   'descripcion': 'Crear, editar y eliminar exámenes del catálogo'},
            {'nombre': 'Ver Solicitudes',       'codigo': 'ver_solicitudes',      'descripcion': 'Ver solicitudes de exámenes'},
            {'nombre': 'Gestionar Solicitudes', 'codigo': 'gestionar_solicitudes','descripcion': 'Crear y editar solicitudes'},
            # ── Muestras ──────────────────────────────────────────────────────
            {'nombre': 'Ver Muestras',          'codigo': 'ver_muestras',         'descripcion': 'Ver muestras e incidencias'},
            {'nombre': 'Gestionar Muestras',    'codigo': 'gestionar_muestras',   'descripcion': 'Crear, editar y eliminar muestras'},
            # ── Resultados ────────────────────────────────────────────────────
            {'nombre': 'Ver Resultados',        'codigo': 'ver_resultados',       'descripcion': 'Ver resultados de exámenes'},
            {'nombre': 'Registrar Resultados',  'codigo': 'registrar_resultados', 'descripcion': 'Capturar valores de resultados'},
            {'nombre': 'Validar Resultados',    'codigo': 'validar_resultados',   'descripcion': 'Validar y aprobar resultados'},
            # ── Reportes ──────────────────────────────────────────────────────
            {'nombre': 'Ver Reportes',          'codigo': 'ver_reportes',         'descripcion': 'Acceso al módulo de Business Intelligence'},
        ]

        permisos = {}
        for p in permisos_data:
            obj, created = Permiso.objects.get_or_create(
                codigo=p['codigo'],
                defaults={'nombre': p['nombre'], 'descripcion': p['descripcion']}
            )
            permisos[p['codigo']] = obj
            self.stdout.write(f"{'Creado' if created else 'Existe'}: Permiso '{obj.nombre}' ({obj.codigo})")

        self.stdout.write("\nAsignando permisos a roles...\n")

        # Administrador: todos
        for permiso in permisos.values():
            RolPermiso.objects.get_or_create(rol=roles['Administrador'], permiso=permiso)
        self.stdout.write(f"Administrador: {len(permisos)} permisos")

        # Veterinario
        permisos_veterinario = [
            'ver_pacientes', 'editar_paciente',
            'ver_catalogo',
            'ver_solicitudes', 'gestionar_solicitudes',
            'ver_muestras', 'gestionar_muestras',
            'ver_resultados', 'registrar_resultados', 'validar_resultados',
            'ver_reportes',
        ]
        for cod in permisos_veterinario:
            RolPermiso.objects.get_or_create(rol=roles['Veterinario'], permiso=permisos[cod])
        self.stdout.write(f"Veterinario: {len(permisos_veterinario)} permisos")

        # Recepcionista
        permisos_recepcionista = [
            'ver_pacientes', 'crear_paciente', 'editar_paciente',
            'ver_catalogo',
            'ver_solicitudes', 'gestionar_solicitudes',
            'ver_muestras', 'gestionar_muestras',
            'ver_resultados',
        ]
        for cod in permisos_recepcionista:
            RolPermiso.objects.get_or_create(rol=roles['Recepcionista'], permiso=permisos[cod])
        self.stdout.write(f"Recepcionista: {len(permisos_recepcionista)} permisos")

        # Medico Externo (solo lectura)
        permisos_medico_externo = [
            'ver_pacientes',
            'ver_catalogo',
            'ver_solicitudes',
            'ver_muestras',
            'ver_resultados',
        ]
        for cod in permisos_medico_externo:
            RolPermiso.objects.get_or_create(rol=roles['Medico Externo'], permiso=permisos[cod])
        self.stdout.write(f"Medico Externo: {len(permisos_medico_externo)} permisos")

        # Propietario (portal propio — sin acceso al panel interno)
        permisos_propietario = ['ver_pacientes']
        for cod in permisos_propietario:
            RolPermiso.objects.get_or_create(rol=roles['Propietario'], permiso=permisos[cod])
        self.stdout.write(f"Propietario: {len(permisos_propietario)} permisos")

        self.stdout.write(self.style.SUCCESS("\n¡Roles y permisos creados exitosamente!"))