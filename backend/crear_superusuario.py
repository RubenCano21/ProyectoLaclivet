"""
Script para crear un superusuario automáticamente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.usuarios.models import Usuario, Rol

def crear_superusuario():
    """Crear un superusuario con rol de Administrador"""

    # Verificar si ya existe un superusuario
    if Usuario.objects.filter(is_superuser=True).exists():
        print("⚠️  Ya existe un superusuario en el sistema.")
        return

    print("🔧 Creando superusuario...\n")

    # Obtener o crear rol de Administrador
    rol_admin, _ = Rol.objects.get_or_create(
        nombre='Administrador',
        defaults={'descripcion': 'Acceso total al sistema'}
    )

    # Crear superusuario
    usuario = Usuario.objects.create_superuser(
        username='admin',
        email='admin@laclivet.com',
        password='admin123',  # Cambiar en producción!
        first_name='Admin',
        last_name='Sistema',
        rol=rol_admin
    )

    print("✅ Superusuario creado exitosamente!")
    print(f"\n📋 Credenciales:")
    print(f"   Usuario: {usuario.username}")
    print(f"   Email: {usuario.email}")
    print(f"   Password: admin123")
    print(f"   Rol: {usuario.rol.nombre if usuario.rol else 'Sin rol'}")
    print(f"\n🌐 Panel de administración: http://localhost:8000/admin/")
    print(f"\n⚠️  IMPORTANTE: Cambia la contraseña en producción!")

if __name__ == '__main__':
    crear_superusuario()

