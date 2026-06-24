# backend/apps/usuarios/management/commands/crear_superusuario.py
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from apps.usuarios.models import Usuario, Rol
import os


class Command(BaseCommand):
    help = "Crea un superusuario con rol de Administrador"

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email del superusuario')
        parser.add_argument('--username', type=str, help='Nombre de usuario')
        parser.add_argument('--password', type=str, help='Contraseña del superusuario')
        parser.add_argument('--first-name', type=str, help='Nombre')
        parser.add_argument('--last-name', type=str, help='Apellido')
        parser.add_argument('--force', action='store_true', help='Forzar creación aunque ya exista un superusuario')

    def handle(self, *args, **options):
        # Priorizar: argumentos de línea de comandos > variables de entorno > valores por defecto
        username = options.get('username') or os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = options.get('email') or os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@laclivet.com')
        password = options.get('password') or os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')
        first_name = options.get('first_name') or os.getenv('DJANGO_SUPERUSER_FIRST_NAME', 'Admin')
        last_name = options.get('last_name') or os.getenv('DJANGO_SUPERUSER_LAST_NAME', 'Sistema')
        force = options.get('force', False)

        # Verificar si ya existe un superusuario
        existing_superuser = Usuario.objects.filter(is_superuser=True).exists()

        if existing_superuser and not force:
            self.stdout.write(
                self.style.WARNING("⚠️ Ya existe un superusuario en el sistema.")
            )
            self.stdout.write(self.style.WARNING("Usa --force para forzar la creación de otro superusuario"))
            return

        # Verificar si el usuario específico ya existe
        if Usuario.objects.filter(username=username).exists() and not force:
            self.stdout.write(
                self.style.WARNING(f"⚠️ El usuario '{username}' ya existe.")
            )
            self.stdout.write(self.style.WARNING("Usa --force para forzar la creación"))
            return

        self.stdout.write("🔧 Creando superusuario...")

        try:
            # Obtener o crear el rol de Administrador
            rol_admin, created = Rol.objects.get_or_create(
                nombre='Administrador',
                defaults={'descripcion': 'Acceso total al sistema'}
            )

            if created:
                self.stdout.write(self.style.SUCCESS("✅ Rol 'Administrador' creado"))
            else:
                self.stdout.write("ℹ️ Rol 'Administrador' ya existente")

            # Verificar si el usuario ya existe para actualizar o crear
            usuario, created = Usuario.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'rol': rol_admin,
                    'is_superuser': True,
                    'is_staff': True,
                    'is_active': True,
                }
            )

            if created:
                # Establecer la contraseña
                usuario.set_password(password)
                usuario.save()
                self.stdout.write(self.style.SUCCESS("✅ Superusuario creado exitosamente!"))
            else:
                # Actualizar usuario existente si se forza
                if force:
                    usuario.email = email
                    usuario.first_name = first_name
                    usuario.last_name = last_name
                    usuario.rol = rol_admin
                    usuario.is_superuser = True
                    usuario.is_staff = True
                    usuario.is_active = True
                    usuario.set_password(password)
                    usuario.save()
                    self.stdout.write(self.style.SUCCESS("✅ Superusuario actualizado exitosamente!"))
                else:
                    self.stdout.write(self.style.WARNING(f"ℹ️ El usuario '{username}' ya existe y no se actualizó"))

            # Mostrar información del usuario
            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("📋 Información del usuario:"))
            self.stdout.write(f"   👤 Username: {usuario.username}")
            self.stdout.write(f"   📧 Email: {usuario.email}")
            self.stdout.write(f"   👔 Nombre: {usuario.get_full_name()}")
            self.stdout.write(f"   🎯 Rol: {usuario.rol.nombre if usuario.rol else 'Sin rol'}")
            self.stdout.write(f"   ⭐ Superusuario: {usuario.is_superuser}")
            self.stdout.write("")

        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f"❌ Error de integridad: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error inesperado: {str(e)}"))