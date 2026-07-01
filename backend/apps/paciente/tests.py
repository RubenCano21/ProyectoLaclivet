"""Tests de control de acceso (IDOR) para el módulo Paciente.

Cubren la corrección: un usuario con rol Propietario solo debe poder ver/
editar sus propias mascotas, nunca las de otro propietario, y no debe poder
crear/editar/eliminar pacientes (operación reservada a staff interno).
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.usuarios.models import Usuario, Rol
from apps.propietario.models import Propietario
from apps.paciente.models import Especie, Raza, Paciente


class PacienteIDORTests(TestCase):
    def setUp(self):
        self.rol_propietario = Rol.objects.create(nombre='Propietario')
        self.rol_admin = Rol.objects.create(nombre='Administrador')

        # Propietario A y su mascota
        self.usuario_a = Usuario.objects.create(
            username='duenio_a', email='duenio_a@example.com',
            first_name='Ana', last_name='A', rol=self.rol_propietario,
        )
        self.usuario_a.set_password('x')
        self.usuario_a.save()
        self.propietario_a = Propietario.objects.create(usuario=self.usuario_a)

        # Propietario B y su mascota (la que A NO debería poder ver/editar)
        self.usuario_b = Usuario.objects.create(
            username='duenio_b', email='duenio_b@example.com',
            first_name='Beto', last_name='B', rol=self.rol_propietario,
        )
        self.usuario_b.set_password('x')
        self.usuario_b.save()
        self.propietario_b = Propietario.objects.create(usuario=self.usuario_b)

        self.especie = Especie.objects.create(nombre='Canino')
        self.raza = Raza.objects.create(nombre='Labrador', especie=self.especie)

        self.paciente_a = Paciente.objects.create(
            nombre='Firulais', propietario=self.propietario_a, raza=self.raza
        )
        self.paciente_b = Paciente.objects.create(
            nombre='Toby', propietario=self.propietario_b, raza=self.raza
        )

        # Staff interno
        self.staff = Usuario.objects.create(
            username='admin', email='admin@example.com',
            first_name='Admin', last_name='Sistema', rol=self.rol_admin,
        )
        self.staff.set_password('x')
        self.staff.save()

        self.client = APIClient()

    def test_propietario_no_ve_paciente_de_otro_en_el_listado(self):
        self.client.force_authenticate(user=self.usuario_a)
        response = self.client.get('/api/pacientes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [p['id'] for p in response.data['resultados']]
        self.assertIn(self.paciente_a.id, ids)
        self.assertNotIn(self.paciente_b.id, ids)

    def test_propietario_no_puede_ver_detalle_de_paciente_ajeno(self):
        self.client.force_authenticate(user=self.usuario_a)
        response = self.client.get(f'/api/pacientes/{self.paciente_b.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_propietario_si_puede_ver_su_propio_paciente(self):
        self.client.force_authenticate(user=self.usuario_a)
        response = self.client.get(f'/api/pacientes/{self.paciente_a.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_propietario_no_puede_crear_pacientes(self):
        self.client.force_authenticate(user=self.usuario_a)
        response = self.client.post('/api/pacientes/', {
            'nombre': 'Nuevo', 'propietario': self.propietario_a.id, 'raza': self.raza.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_propietario_no_puede_editar_ni_eliminar_pacientes(self):
        self.client.force_authenticate(user=self.usuario_a)
        response = self.client.patch(
            f'/api/pacientes/{self.paciente_a.id}/', {'nombre': 'Hackeado'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(f'/api/pacientes/{self.paciente_a.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_si_puede_crear_y_ver_todos_los_pacientes(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.get('/api/pacientes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [p['id'] for p in response.data['resultados']]
        self.assertIn(self.paciente_a.id, ids)
        self.assertIn(self.paciente_b.id, ids)

        response = self.client.post('/api/pacientes/', {
            'nombre': 'Rex', 'propietario': self.propietario_a.id, 'raza': self.raza.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

