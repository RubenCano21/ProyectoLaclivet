"""
Uso:
    python manage.py seed_hemograma

Crea CatalogoExamen "Hematología" -> Examen "Hemograma Completo" ->
Parametros (con su grupo visual) -> ValorReferencia para Bovino,
replicando exactamente la hoja de resultados de ejemplo.
"""
from django.core.management.base import BaseCommand
from apps.catalogo.models import CatalogoExamen, Examen, Parametro, ValorReferencia, TipoDato


class Command(BaseCommand):
    help = "Crea el catálogo del examen Hemograma con sus parámetros y referencias"

    def handle(self, *args, **options):
        catalogo, _ = CatalogoExamen.objects.get_or_create(
            nombre="Hematología", defaults={"area": "Laboratorio Clínico", "precio": 80}
        )
        examen, _ = Examen.objects.get_or_create(
            nombre_examen="Hemograma Completo",
            catalogo=catalogo,
            defaults={"categoria": "Hematología"},
        )

        ESPECIE = "Bovino"

        # nombre_parametro, grupo, unidad, tipo_dato, orden, (min, max) | texto_referencia
        PARAMETROS = [
            ("Eritrocitos", "Eritrograma", "mill/ul", TipoDato.NUMERICO, 1, (5, 9)),
            ("Hematocrito", "Eritrograma", "%", TipoDato.NUMERICO, 2, (24, 38)),
            ("Hemoglobina", "Eritrograma", "g/dl", TipoDato.NUMERICO, 3, (8.5, 13)),
            ("VCM", "Eritrograma", "fl", TipoDato.NUMERICO, 4, (40, 60)),
            ("CHCM", "Eritrograma", "dl", TipoDato.NUMERICO, 5, (30, 37)),
            ("E. Nucleados", "Eritrograma", "/100 Leuc", TipoDato.NUMERICO, 6, (0, 0)),
            ("Anisocitosis", "Eritrograma", "", TipoDato.SELECT, 7, None, "-a +"),
            ("Policromacia", "Eritrograma", "", TipoDato.SELECT, 8, None, "- a +"),
            ("Corp. Howell Jolly", "Eritrograma", "", TipoDato.SELECT, 9, None, "- a +"),
            ("Plaquetas", "Plaquetas y Proteínas", "mil/ul", TipoDato.NUMERICO, 10, (100, 800)),
            ("Proteinas", "Plaquetas y Proteínas", "g/l", TipoDato.NUMERICO, 11, (60, 80)),

            ("Monocitos %", "Leucograma %", "%", TipoDato.NUMERICO, 13, (2, 5)),
            ("Linfocitos %", "Leucograma %", "%", TipoDato.NUMERICO, 14, (35, 45)),
            ("Neutrofilos %", "Leucograma %", "%", TipoDato.NUMERICO, 15, (42, 56)),
            ("En Banda %", "Leucograma %", "%", TipoDato.NUMERICO, 16, (2, 6)),
            ("Juvenil %", "Leucograma %", "%", TipoDato.NUMERICO, 17, (0, 0)),
            ("Mielocitos %", "Leucograma %", "%", TipoDato.NUMERICO, 18, (0, 0)),
            ("Eosinofilos %", "Leucograma %", "%", TipoDato.NUMERICO, 19, (1, 3)),
            ("Basofilos %", "Leucograma %", "%", TipoDato.NUMERICO, 20, (0, 0)),

            ("Leucocitos", "Leucograma absoluto", "/ul", TipoDato.NUMERICO, 21, (4500, 12000)),
            ("Monocitos abs.", "Leucograma absoluto", "/ul", TipoDato.NUMERICO, 22, (200, 960)),
            ("Linfocitos abs.", "Leucograma absoluto", "/ul", TipoDato.NUMERICO, 23, (2000, 7200)),
            ("Neutrofilos abs.", "Leucograma absoluto", "/ul", TipoDato.NUMERICO, 24, (1150, 4400)),
            ("En Banda abs.", "Leucograma absoluto", "/ul", TipoDato.NUMERICO, 25, (0, 330)),
            ("Eosinofilos abs.", "Leucograma absoluto", "/ul", TipoDato.NUMERICO, 26, (180, 1100)),
            ("Basofilos abs.", "Leucograma absoluto", "/ul", TipoDato.NUMERICO, 27, (0, 0)),
            ("Parasitemia", "Leucograma absoluto", "", TipoDato.TEXTO, 28, None),
        ]

        for item in PARAMETROS:
            nombre, grupo, unidad, tipo, orden, rango, *resto = item
            texto_ref = resto[0] if resto else ""

            parametro, _ = Parametro.objects.get_or_create(
                examen=examen, nombre_parametro=nombre,
                defaults={
                    "grupo": grupo, "unidad_medida": unidad,
                    "tipo_dato": tipo, "orden": orden,
                },
            )

            if rango is not None:
                ValorReferencia.objects.get_or_create(
                    parametro=parametro, especie=ESPECIE, sexo="A",
                    defaults={"valor_min": rango[0], "valor_max": rango[1]},
                )
            elif texto_ref:
                ValorReferencia.objects.get_or_create(
                    parametro=parametro, especie=ESPECIE, sexo="A",
                    defaults={"texto_referencia": texto_ref},
                )

        self.stdout.write(self.style.SUCCESS(f"Hemograma sembrado con {len(PARAMETROS)} parámetros."))