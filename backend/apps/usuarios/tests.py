"""Tests de seguridad para el flujo de autenticación/registro.

Cubren específicamente las correcciones aplicadas:
- El auto-registro público NO debe permitir elegir rol (evita escalada
  de privilegios).
- Las contraseñas generadas automáticamente deben ser aleatorias (no
  predecibles a partir de apellido+CI) y forzar cambio en el próximo login.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.usuarios.models import Usuario, Rol
from apps.core.validators import generar_password_default


class RegistroPublicoSeguridadTests(TestCase):
    """POST /api/usuarios/auth/registro/ (AllowAny)."""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/usuarios/auth/registro/'
        self.admin_rol = Rol.objects.create(nombre='Administrador', descripcion='Full access')

    def test_no_permite_escalar_privilegios_via_rol_id(self):
        """Un usuario anónimo NO debe poder auto-asignarse el rol Administrador."""
        payload = {
            'email': 'nuevo@example.com',
            'first_name': 'Ana',
            'last_name': 'Perez',
            'ci': '1234567',
            'rol_id': self.admin_rol.id,  # intento de escalada
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        usuario = Usuario.objects.get(email='nuevo@example.com')
        self.assertIsNotNone(usuario.rol)
        self.assertEqual(usuario.rol.nombre, 'Propietario')
        self.assertNotEqual(usuario.rol_id, self.admin_rol.id)

    def test_password_generada_no_es_predecible(self):
        """Si no se envía password, se genera una aleatoria y se exige cambiarla."""
        payload = {
            'email': 'sinpass@example.com',
            'first_name': 'Luis',
            'last_name': 'Gomez',
            'ci': '7654321',
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        usuario = Usuario.objects.get(email='sinpass@example.com')
        # La contraseña predecible legacy era "gomez.7654321"
        self.assertFalse(usuario.check_password('gomez.7654321'))
        self.assertTrue(usuario.debe_cambiar_password)

    def test_generar_password_default_es_aleatoria(self):
        """Dos llamadas con los mismos datos NO deben producir la misma contraseña."""
        p1 = generar_password_default('Perez', '1234567')
        p2 = generar_password_default('Perez', '1234567')
        self.assertNotEqual(p1, p2)
        self.assertGreaterEqual(len(p1), 10)


class CambiarPasswordTests(TestCase):
    def setUp(self):
        self.rol = Rol.objects.create(nombre='Propietario')
        self.usuario = Usuario.objects.create(
            username='juan', email='juan@example.com',
            first_name='Juan', last_name='Lopez',
            rol=self.rol, debe_cambiar_password=True,
        )
        self.usuario.set_password('temporal123')
        self.usuario.save()

        self.client = APIClient()
        self.client.force_authenticate(user=self.usuario)

    def test_cambiar_password_limpia_flag(self):
        response = self.client.post('/api/usuarios/cambiar-password/', {
            'password_actual': 'temporal123',
            'password_nuevo': 'NuevaClaveSegura123',
            'password_nuevo2': 'NuevaClaveSegura123',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.usuario.refresh_from_db()
        self.assertFalse(self.usuario.debe_cambiar_password)

