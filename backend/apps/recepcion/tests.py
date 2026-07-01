"""Tests de seguridad para el módulo Recepción.

Cubren las correcciones:
- El monto de un Cobro vinculado a una solicitud se calcula en el
  servidor (no se confía en el valor enviado por el cliente).
- Los endpoints de recepción (cobros, solicitudes) son exclusivos de
  staff interno (Administrador/Veterinario/Recepcionista).
"""
from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.usuarios.models import Usuario, Rol
from apps.propietario.models import Propietario
from apps.paciente.models import Especie, Raza, Paciente
from apps.catalogo.models import CatalogoExamen, Examen
from apps.recepcion.models import SolicitudExamen, DetalleSolicitud


class CobroMontoSeguroTests(TestCase):
    def setUp(self):
        self.rol_admin = Rol.objects.create(nombre='Administrador')
        self.staff = Usuario.objects.create(
            username='admin', email='admin@example.com',
            first_name='Admin', last_name='Sistema', rol=self.rol_admin,
        )
        self.staff.set_password('x')
        self.staff.save()

        especie = Especie.objects.create(nombre='Canino')
        raza = Raza.objects.create(nombre='Labrador', especie=especie)
        paciente = Paciente.objects.create(nombre='Firulais', raza=raza)

        self.solicitud = SolicitudExamen.objects.create(codigo='SOL-TEST01', paciente=paciente)
        catalogo = CatalogoExamen.objects.create(nombre='Hematologia', precio=Decimal('150.00'))
        examen1 = Examen.objects.create(nombre_examen='Hemograma', catalogo=catalogo)
        examen2 = Examen.objects.create(nombre_examen='Bioquimica', catalogo=catalogo)

        # Precio real acordado: 100 + 80 = 180
        DetalleSolicitud.objects.create(solicitud=self.solicitud, examen=examen1, precio_aplicado=Decimal('100.00'))
        DetalleSolicitud.objects.create(solicitud=self.solicitud, examen=examen2, precio_aplicado=Decimal('80.00'))

        self.client = APIClient()
        self.client.force_authenticate(user=self.staff)

    def test_monto_total_se_calcula_del_servidor_no_del_cliente(self):
        """Aunque el cliente envíe un monto manipulado (1 Bs.), el servidor
        debe ignorarlo y calcular el total real de la solicitud (180 Bs.)."""
        response = self.client.post('/api/recepcion/cobros/', {
            'monto_total': '1.00',  # intento de manipulación
            'metodo_pago': 'efectivo',
            'fecha': '2026-06-30T10:00:00Z',
            'solicitud': self.solicitud.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(str(response.data['monto_total'])), Decimal('180.00'))

        self.solicitud.refresh_from_db()
        self.assertIsNotNone(self.solicitud.cobro_id)

    def test_monto_manual_permitido_sin_solicitud(self):
        """Sin `solicitud`, se admite un monto manual (cargos misceláneos)."""
        response = self.client.post('/api/recepcion/cobros/', {
            'monto_total': '50.00',
            'metodo_pago': 'efectivo',
            'fecha': '2026-06-30T10:00:00Z',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(str(response.data['monto_total'])), Decimal('50.00'))


class RecepcionAccesoRestringidoTests(TestCase):
    def setUp(self):
        rol_propietario = Rol.objects.create(nombre='Propietario')
        self.propietario_user = Usuario.objects.create(
            username='duenio', email='duenio@example.com',
            first_name='Ana', last_name='Perez', rol=rol_propietario,
        )
        self.propietario_user.set_password('x')
        self.propietario_user.save()
        # La señal post_save de Usuario ya crea el Propietario automáticamente.

        self.client = APIClient()

    def test_propietario_no_puede_crear_cobros(self):
        self.client.force_authenticate(user=self.propietario_user)
        response = self.client.post('/api/recepcion/cobros/', {
            'monto_total': '999999.00',
            'metodo_pago': 'efectivo',
            'fecha': '2026-06-30T10:00:00Z',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_propietario_no_puede_listar_solicitudes(self):
        self.client.force_authenticate(user=self.propietario_user)
        response = self.client.get('/api/recepcion/solicitudes/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonimo_no_puede_acceder(self):
        response = self.client.get('/api/recepcion/cobros/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

