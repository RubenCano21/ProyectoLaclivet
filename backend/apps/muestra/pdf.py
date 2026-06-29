from io import BytesIO
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from weasyprint import HTML

from .models import Resultado


def generar_pdf_resultado(resultado: Resultado) -> Resultado:
    detalle = resultado.detalle_solicitud
    solicitud = detalle.solicitud
    paciente = solicitud.paciente
    propietario = getattr(paciente, 'propietario', None)
    examen = detalle.examen

    parametros_resultado = (
        resultado.resultados_parametro
        .select_related('parametro')
        .order_by('parametro__orden', 'parametro__grupo')
    )

    grupos = {}
    for rp in parametros_resultado:
        grupo = rp.parametro.grupo or 'General'
        grupos.setdefault(grupo, []).append(rp)

    veterinario = resultado.veterinario_responsable
    medico_solicitante = solicitud.medico_veterinario

    contexto = {
        'resultado': resultado,
        'solicitud': solicitud,
        'paciente': paciente,
        'propietario': propietario,
        'examen': examen,
        'grupos': grupos,
        'veterinario': veterinario,
        'medico_solicitante': medico_solicitante,
        'fecha_emision': resultado.fecha_emision,
    }

    html_string = render_to_string('pdf/resultado_examen.html', contexto)
    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(pdf_file)
    pdf_file.seek(0)

    nombre_archivo = f"resultado_{solicitud.codigo}_{examen.id}.pdf"
    resultado.archivo_pdf.save(nombre_archivo, ContentFile(pdf_file.read()), save=True)
    return resultado