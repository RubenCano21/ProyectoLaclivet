"""Tests para la generación de PDF de resultados (regresión del bug
corregido: campos de la plantilla desalineados con los modelos reales).
"""
import shutil
import tempfile
from decimal import Decimal

from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework import status

from apps.usuarios.models import Usuario, Rol
from apps.paciente.models import Especie, Raza, Paciente
from apps.catalogo.models import (
    CatalogoExamen, Examen, Parametro, ValorReferencia,
    OrdenTrabajo, OrdenExamen, ResultadoParametro,
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class GenerarPdfResultadoTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        rol_admin = Rol.objects.create(nombre='Administrador')
        self.staff = Usuario.objects.create(
            username='admin', email='admin@example.com',
            first_name='Admin', last_name='Sistema', rol=rol_admin,
        )
        self.staff.set_password('x')
        self.staff.save()

        especie = Especie.objects.create(nombre='Canino')
        raza = Raza.objects.create(nombre='Labrador', especie=especie)
        paciente = Paciente.objects.create(nombre='Firulais', sexo='macho', raza=raza)

        catalogo = CatalogoExamen.objects.create(nombre='Hematologia', precio=Decimal('150.00'))
        examen = Examen.objects.create(nombre_examen='Hemograma', catalogo=catalogo)
        parametro = Parametro.objects.create(
            nombre_parametro='Hemoglobina', unidad_medida='g/dl',
            examen=examen, grupo='Eritrograma', orden=1,
        )
        ValorReferencia.objects.create(
            valor_min=Decimal('12.00'), valor_max=Decimal('18.00'),
            especie='Canino', sexo='A', parametro=parametro,
        )

        orden_trabajo = OrdenTrabajo.objects.create(paciente=paciente)
        self.orden_examen = OrdenExamen.objects.create(
            orden=orden_trabajo, examen=examen, estado='completado',
            veterinario_responsable=self.staff,
        )
        ResultadoParametro.objects.create(
            orden_examen=self.orden_examen, parametro=parametro,
            valor_numerico=Decimal('15.00'), interpretacion='NORMAL',
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.staff)

    def test_generar_pdf_no_lanza_excepcion_y_guarda_archivo(self):
        """Reproduce el flujo completo: la plantilla debe poder renderizar
        todos los campos (paciente.raza.especie, parametro.nombre_parametro,
        examen.nombre_examen, etc.) sin lanzar AttributeError/TemplateError."""
        response = self.client.post(
            f'/api/catalogos/orden-examenes/{self.orden_examen.id}/generar-pdf/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertTrue(response.data['pdf_url'])

        self.orden_examen.refresh_from_db()
        self.assertTrue(bool(self.orden_examen.archivo_pdf))

    def test_no_permite_generar_pdf_de_examen_no_completado(self):
        self.orden_examen.estado = 'pendiente'
        self.orden_examen.save(update_fields=['estado'])

        response = self.client.post(
            f'/api/catalogos/orden-examenes/{self.orden_examen.id}/generar-pdf/'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

