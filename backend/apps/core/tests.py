"""Tests unitarios para las clases de permisos compartidas.

Cubren la corrección de `EsPropietario.has_object_permission`, que antes
comparaba `Propietario == Usuario` (siempre False) en vez de
`Propietario.usuario == Usuario`.
"""
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.core.permissions import EsPropietario, es_propietario_de, tiene_rol
from apps.usuarios.models import Usuario, Rol
from apps.propietario.models import Propietario
from apps.paciente.models import Especie, Raza, Paciente


class EsPropietarioObjectPermissionTests(TestCase):
    def setUp(self):
        rol = Rol.objects.create(nombre='Propietario')
        self.usuario = Usuario.objects.create(
            username='ana', email='ana@example.com', first_name='Ana', last_name='Perez', rol=rol,
        )
        self.propietario = Propietario.objects.create(usuario=self.usuario)

        otro_usuario = Usuario.objects.create(
            username='beto', email='beto@example.com', first_name='Beto', last_name='B', rol=rol,
        )
        self.otro_propietario = Propietario.objects.create(usuario=otro_usuario)

        especie = Especie.objects.create(nombre='Canino')
        raza = Raza.objects.create(nombre='Labrador', especie=especie)
        self.paciente_propio = Paciente.objects.create(nombre='Firulais', propietario=self.propietario, raza=raza)
        self.paciente_ajeno = Paciente.objects.create(nombre='Toby', propietario=self.otro_propietario, raza=raza)

        self.factory = APIRequestFactory()

    def _request(self, user):
        req = self.factory.get('/fake/')
        req.user = user
        return req

    def test_permite_acceso_a_objeto_propio(self):
        permiso = EsPropietario()
        request = self._request(self.usuario)
        self.assertTrue(permiso.has_object_permission(request, None, self.paciente_propio))

    def test_deniega_acceso_a_objeto_ajeno(self):
        permiso = EsPropietario()
        request = self._request(self.usuario)
        self.assertFalse(permiso.has_object_permission(request, None, self.paciente_ajeno))

    def test_helper_es_propietario_de(self):
        self.assertTrue(es_propietario_de(self.usuario, self.paciente_propio))
        self.assertFalse(es_propietario_de(self.usuario, self.paciente_ajeno))

    def test_helper_tiene_rol(self):
        self.assertTrue(tiene_rol(self.usuario, 'Propietario'))
        self.assertFalse(tiene_rol(self.usuario, 'Administrador'))

