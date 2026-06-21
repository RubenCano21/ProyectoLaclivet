from django.core.management.base import BaseCommand
from apps.usuarios.models import Usuario, Rol


class Command(BaseCommand):
    help = "Asigna el rol de Administrador a un superusuario existente"

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email del usuario')

    def handle(self, *args, **options):
        email = options['email']

        rol_admin, _ = Rol.objects.get_or_create(
            nombre='Administrador',
            defaults={'descripcion': 'Acceso total al sistema'}
        )

        try:
            usuario = Usuario.objects.get(email=email)
            usuario.rol = rol_admin
            usuario.save()
            self.stdout.write(self.style.SUCCESS(
                f"Rol '{rol_admin.nombre}' asignado a {usuario.email}"
            ))
        except Usuario.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"No existe usuario con email {email}"))
