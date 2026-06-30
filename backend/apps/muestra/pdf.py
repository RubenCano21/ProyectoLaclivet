from io import BytesIO
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from xhtml2pdf import pisa


def _link_callback(uri, rel):
    """Necesario para xhtml2pdf: resuelve rutas de archivos estáticos/media."""
    return uri


def generar_pdf_orden_examen(orden_examen):
    resultados = orden_examen.resultados.select_related('parametro').order_by(
        'parametro__orden', 'parametro__grupo'
    )

    grupos = {}
    for rp in resultados:
        grupo = rp.parametro.grupo or 'General'
        grupos.setdefault(grupo, []).append(rp)

    contexto = {
        'orden_examen': orden_examen,
        'paciente': orden_examen.paciente,
        'examen': orden_examen.examen,
        'medico_solicitante': orden_examen.medico_solicitante,
        'veterinario': orden_examen.veterinario_responsable,
        'grupos': grupos,
        'fecha_emision': orden_examen.fecha_resultado,
    }

    html_string = render_to_string('pdf/resultado_examen.html', contexto)

    pdf_buffer = BytesIO()
    resultado_pisa = pisa.CreatePDF(
        html_string,
        dest=pdf_buffer,
        link_callback=_link_callback,
        encoding='utf-8',
    )

    if resultado_pisa.err:
        raise RuntimeError(f"Error generando PDF: {resultado_pisa.err}")

    pdf_buffer.seek(0)
    nombre_archivo = f"resultado_OE{orden_examen.id}.pdf"
    orden_examen.archivo_pdf.save(nombre_archivo, ContentFile(pdf_buffer.read()), save=True)
    return orden_examen