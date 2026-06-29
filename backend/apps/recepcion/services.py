from django.db import transaction
from django.utils.crypto import get_random_string

from apps.muestra.models import Muestra
from .models import SolicitudExamen, DetalleSolicitud


def _generar_codigo_solicitud():
    return f"SOL-{get_random_string(8).upper()}"


def _generar_codigo_muestra():
    return f"MUE-{get_random_string(8).upper()}"


@transaction.atomic
def crear_solicitud_con_muestras(paciente, medico_veterinario, examenes_ids, observaciones=""):
    """
    Crea SolicitudExamen + DetalleSolicitud por cada examen.
    Verifica Examen.requiere_muestra y genera Muestra si aplica.
    Además crea la OrdenTrabajo + OrdenExamen correspondiente en 'catalogo',
    que es donde el Veterinario registrará los resultados.
    """
    from apps.catalogo.models import Examen, OrdenTrabajo, OrdenExamen

    solicitud = SolicitudExamen.objects.create(
        codigo=_generar_codigo_solicitud(),
        paciente=paciente,
        medico_veterinario=medico_veterinario,
        observaciones=observaciones,
        estado='pendiente',
    )

    orden_trabajo = OrdenTrabajo.objects.create(
        paciente=paciente,
        veterinario_solicitante=(
            f"{medico_veterinario.usuario.first_name} {medico_veterinario.usuario.last_name}"
            if medico_veterinario and medico_veterinario.usuario else ""
        ),
        observaciones_generales=observaciones,
        solicitud=solicitud,
    )

    examenes = Examen.objects.filter(id__in=examenes_ids).select_related('catalogo')
    muestras_generadas = []

    for examen in examenes:
        detalle = DetalleSolicitud.objects.create(
            solicitud=solicitud,
            examen=examen,
            precio_aplicado=examen.catalogo.precio,
        )

        muestra = None
        if examen.requiere_muestra:
            muestra = Muestra.objects.create(
                codigo=_generar_codigo_muestra(),
                tipo_muestra=examen.tipo_muestra_sugerida or "Sin especificar",
                estado='pendiente',
                paciente=paciente,
                solicitud=solicitud,
            )
            muestras_generadas.append(muestra)

        OrdenExamen.objects.create(
            orden=orden_trabajo,
            examen=examen,
            muestra=muestra,
            detalle_solicitud=detalle,
        )

    return solicitud, muestras_generadas


def cambiar_estado_solicitud(solicitud: SolicitudExamen, nuevo_estado: str):
    solicitud.estado = nuevo_estado
    solicitud.save(update_fields=['estado'])
    return solicitud