from io import BytesIO
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from xhtml2pdf import pisa


def _link_callback(uri, rel):
    """Necesario para xhtml2pdf: resuelve rutas de archivos estáticos/media."""
    return uri


def generar_pdf_orden_examen(orden_examen):
    # Obtener resultados con todas las relaciones necesarias
    resultados = orden_examen.resultados.select_related(
        'parametro'
    ).prefetch_related(
        'parametro__valores_referencia'
    ).order_by('parametro__orden', 'parametro__grupo')

    # Agrupar y enriquecer cada resultado con los valores pre-calculados
    grupos = {}
    for rp in resultados:
        grupo = rp.parametro.grupo or 'General'

        # Valor a mostrar: numérico o texto
        if rp.valor_numerico is not None:
            rp.valor_display = str(rp.valor_numerico).rstrip('0').rstrip('.')
        elif rp.valor_texto:
            rp.valor_display = rp.valor_texto
        else:
            rp.valor_display = '—'

        # fuera_de_rango basado en interpretacion del modelo
        rp.fuera_de_rango = rp.interpretacion in ('BAJO', 'ALTO')
        rp.interpretacion_display = rp.interpretacion or 'Normal'

        # Rango de referencia desde ValorReferencia
        vr = rp.parametro.valores_referencia.first()
        if vr:
            if vr.valor_min is not None or vr.valor_max is not None:
                rp.referencia_display = f"{vr.valor_min or '—'} - {vr.valor_max or '—'}"
            elif vr.texto_referencia:
                rp.referencia_display = vr.texto_referencia
            else:
                rp.referencia_display = '-'
        else:
            rp.referencia_display = '-'

        grupos.setdefault(grupo, []).append(rp)

    # Resolución segura del paciente y sus relaciones
    paciente = orden_examen.paciente  # property: orden.paciente

    # Resolución segura de la solicitud
    solicitud = None
    if orden_examen.detalle_solicitud:
        solicitud = orden_examen.detalle_solicitud.solicitud

    contexto = {
        'orden_examen': orden_examen,
        'paciente': paciente,
        'solicitud': solicitud,
        'muestra': orden_examen.muestra,
        'medico_solicitante': orden_examen.medico_solicitante,   # property en OrdenExamen
        'veterinario_responsable': orden_examen.veterinario_responsable,  # FK a Usuario
        'grupos_parametros': grupos,
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
    nombre_archivo = f"resultado_LACLIVET_OE{orden_examen.id}.pdf"
    orden_examen.archivo_pdf.save(nombre_archivo, ContentFile(pdf_buffer.read()), save=True)

    return orden_examen