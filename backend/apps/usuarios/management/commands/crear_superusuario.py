from django.core.management.base import BaseCommand
from apps.usuarios.models import Usuario, Rol


class Command(BaseCommand):
    help = "Crea un superusuario con rol de Administrador"

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, default='admin@laclivet.com')
        parser.add_argument('--username', type=str, default='admin')
        parser.add_argument('--password', type=str, default='admin123')
        parser.add_argument('--first-name', type=str, default='Admin')
        parser.add_argument('--last-name', type=str, default='Sistema')

    def handle(self, *args, **options):
        if Usuario.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.WARNING("Ya existe un superusuario en el sistema."))
            return

        self.stdout.write("Creando superusuario...\n")

        rol_admin, _ = Rol.objects.get_or_create(
            nombre='Administrador',
            defaults={'descripcion': 'Acceso total al sistema'}
        )

        usuario = Usuario.objects.create_superuser(
            username=options['username'],
            email=options['email'],
            password=options['password'],
            first_name=options['first_name'],
            last_name=options['last_name'],
            rol=rol_admin
        )

        self.stdout.write(self.style.SUCCESS("Superusuario creado exitosamente!"))
        self.stdout.write(f"Usuario: {usuario.username}")
        self.stdout.write(f"Email: {usuario.email}")
        self.stdout.write(f"Rol: {usuario.rol.nombre if usuario.rol else 'Sin rol'}")
