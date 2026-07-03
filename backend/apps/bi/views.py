import csv
import os
import logging
from io import BytesIO
from datetime import timedelta, date

from django.conf import settings
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from xhtml2pdf import pisa

from apps.core.permissions import EsStaffInterno

logger = logging.getLogger(__name__)
from apps.muestra.models import Muestra
from apps.recepcion.models import SolicitudExamen, Cobro
from apps.paciente.models import Paciente
from apps.catalogo.models import OrdenExamen, ResultadoParametro


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _ultimos_meses(n=6):
    hoy = date.today()
    meses = []
    for i in range(n - 1, -1, -1):
        d = date(hoy.year, hoy.month, 1) - timedelta(days=i * 30)
        meses.append(f"{d.year}-{d.month:02d}")
    return meses


def _parse_meses(request, default=6) -> int:
    try:
        n = int(request.query_params.get('meses', default))
        return max(1, min(n, 24))
    except (ValueError, TypeError):
        return default


def _parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _render_pdf(template_name, context, filename):
    html = render_to_string(template_name, context)
    buffer = BytesIO()
    result = pisa.CreatePDF(html, dest=buffer, encoding='utf-8')
    if result.err:
        return HttpResponse('Error generando PDF', status=500)
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD — KPIs EXISTENTES (ampliados)
# ─────────────────────────────────────────────────────────────────────────────

class BiResumenView(APIView):
    """KPIs generales del laboratorio — ampliado con nuevas métricas."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        total_muestras       = Muestra.objects.count()
        total_solicitudes    = SolicitudExamen.objects.count()
        total_pacientes      = Paciente.objects.count()
        total_ingresos       = Cobro.objects.aggregate(total=Sum('monto_total'))['total'] or 0
        solicitudes_pendientes = SolicitudExamen.objects.filter(estado='pendiente').count()
        muestras_pendientes  = Muestra.objects.filter(estado='pendiente').count()
        muestras_rechazadas  = Muestra.objects.filter(estado='rechazada').count()
        parametros_fuera_rango = ResultadoParametro.objects.filter(
            interpretacion__in=['ALTO', 'BAJO']
        ).count()

        hoy = date.today()
        inicio_mes_actual   = date(hoy.year, hoy.month, 1)
        inicio_mes_anterior = (inicio_mes_actual - timedelta(days=1)).replace(day=1)

        muestras_mes     = Muestra.objects.filter(fecha_recepcion__gte=inicio_mes_actual).count()
        muestras_mes_ant = Muestra.objects.filter(
            fecha_recepcion__gte=inicio_mes_anterior,
            fecha_recepcion__lt=inicio_mes_actual
        ).count()
        sol_mes     = SolicitudExamen.objects.filter(fecha_solicitud__date__gte=inicio_mes_actual).count()
        sol_mes_ant = SolicitudExamen.objects.filter(
            fecha_solicitud__date__gte=inicio_mes_anterior,
            fecha_solicitud__date__lt=inicio_mes_actual
        ).count()
        ingresos_mes     = Cobro.objects.filter(fecha__date__gte=inicio_mes_actual).aggregate(total=Sum('monto_total'))['total'] or 0
        ingresos_mes_ant = Cobro.objects.filter(
            fecha__date__gte=inicio_mes_anterior,
            fecha__date__lt=inicio_mes_actual
        ).aggregate(total=Sum('monto_total'))['total'] or 0

        tasa_rechazo = round(muestras_rechazadas / total_muestras * 100, 1) if total_muestras else 0

        return Response({
            'total_muestras':           total_muestras,
            'total_solicitudes':        total_solicitudes,
            'total_pacientes':          total_pacientes,
            'total_ingresos':           float(total_ingresos),
            'solicitudes_pendientes':   solicitudes_pendientes,
            'muestras_pendientes':      muestras_pendientes,
            'muestras_rechazadas':      muestras_rechazadas,
            'tasa_rechazo':             tasa_rechazo,
            'parametros_fuera_rango':   parametros_fuera_rango,
            'muestras_este_mes':        muestras_mes,
            'muestras_mes_anterior':    muestras_mes_ant,
            'solicitudes_este_mes':     sol_mes,
            'solicitudes_mes_anterior': sol_mes_ant,
            'ingresos_este_mes':        float(ingresos_mes),
            'ingresos_mes_anterior':    float(ingresos_mes_ant),
        })


class BiMuestrasPorMesView(APIView):
    """Tendencia de muestras — soporta ?meses=N (default 6, máx 24)."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        n = _parse_meses(request)
        meses = _ultimos_meses(n)
        inicio = date.today().replace(day=1) - timedelta(days=n * 30)
        qs = (
            Muestra.objects
            .filter(fecha_recepcion__gte=inicio)
            .annotate(mes=TruncMonth('fecha_recepcion'))
            .values('mes').annotate(total=Count('id')).order_by('mes')
        )
        por_mes = {m['mes'].strftime('%Y-%m'): m['total'] for m in qs if m['mes']}
        return Response({'labels': meses, 'datos': [por_mes.get(m, 0) for m in meses]})


class BiSolicitudesPorMesView(APIView):
    """Tendencia de solicitudes — soporta ?meses=N."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        n = _parse_meses(request)
        meses = _ultimos_meses(n)
        inicio = timezone.now() - timedelta(days=n * 30)
        qs = (
            SolicitudExamen.objects
            .filter(fecha_solicitud__gte=inicio)
            .annotate(mes=TruncMonth('fecha_solicitud'))
            .values('mes').annotate(total=Count('id')).order_by('mes')
        )
        por_mes = {m['mes'].strftime('%Y-%m'): m['total'] for m in qs}
        return Response({'labels': meses, 'datos': [por_mes.get(m, 0) for m in meses]})


class BiIngresosPorMesView(APIView):
    """Ingresos totales por mes — soporta ?meses=N."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        n = _parse_meses(request)
        meses = _ultimos_meses(n)
        inicio = timezone.now() - timedelta(days=n * 30)
        qs = (
            Cobro.objects
            .filter(fecha__gte=inicio)
            .annotate(mes=TruncMonth('fecha'))
            .values('mes').annotate(total=Sum('monto_total')).order_by('mes')
        )
        por_mes = {m['mes'].strftime('%Y-%m'): float(m['total'] or 0) for m in qs}
        return Response({'labels': meses, 'datos': [por_mes.get(m, 0.0) for m in meses]})


class BiSolicitudesPorEstadoView(APIView):
    permission_classes = [EsStaffInterno]

    def get(self, request):
        qs = SolicitudExamen.objects.values('estado').annotate(total=Count('id')).order_by('-total')
        return Response({'labels': [i['estado'].replace('_', ' ').capitalize() for i in qs], 'datos': [i['total'] for i in qs]})


class BiTiposMuestraView(APIView):
    permission_classes = [EsStaffInterno]

    def get(self, request):
        qs = Muestra.objects.values('tipo_muestra').annotate(total=Count('id')).order_by('-total')
        return Response({'labels': [i['tipo_muestra'] or 'Sin tipo' for i in qs], 'datos': [i['total'] for i in qs]})


class BiMuestrasPorEstadoView(APIView):
    permission_classes = [EsStaffInterno]

    def get(self, request):
        qs = Muestra.objects.values('estado').annotate(total=Count('id')).order_by('-total')
        return Response({'labels': [i['estado'].replace('_', ' ').capitalize() for i in qs], 'datos': [i['total'] for i in qs]})


class BiEspeciesView(APIView):
    permission_classes = [EsStaffInterno]

    def get(self, request):
        qs = (
            Paciente.objects.exclude(raza__isnull=True)
            .values('raza__especie__nombre').annotate(total=Count('id')).order_by('-total')
        )
        labels = [i['raza__especie__nombre'] or 'Desconocida' for i in qs]
        datos  = [i['total'] for i in qs]
        sin = Paciente.objects.filter(raza__isnull=True).count()
        if sin:
            labels.append('Sin especie'); datos.append(sin)
        return Response({'labels': labels, 'datos': datos})


class BiExamenesTopView(APIView):
    permission_classes = [EsStaffInterno]

    def get(self, request):
        qs = OrdenExamen.objects.values('examen__nombre_examen').annotate(total=Count('id')).order_by('-total')[:8]
        return Response({'labels': [i['examen__nombre_examen'] for i in qs], 'datos': [i['total'] for i in qs]})


# ─────────────────────────────────────────────────────────────────────────────
# NUEVOS ENDPOINTS ANALÍTICOS
# ─────────────────────────────────────────────────────────────────────────────

class BiIngresosPorMetodoPagoView(APIView):
    """Distribución de ingresos por método de pago."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        qs = (
            Cobro.objects.exclude(metodo_pago__isnull=True)
            .values('metodo_pago').annotate(total=Sum('monto_total')).order_by('-total')
        )
        return Response({
            'labels': [i['metodo_pago'].capitalize() for i in qs],
            'datos':  [float(i['total'] or 0) for i in qs],
        })


class BiRendimientoVeterinariosView(APIView):
    """Exámenes completados/validados por veterinario (top 10)."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        qs = (
            OrdenExamen.objects
            .filter(veterinario_responsable__isnull=False, estado__in=['completado', 'validado'])
            .values('veterinario_responsable__first_name', 'veterinario_responsable__last_name', 'veterinario_responsable__email')
            .annotate(total=Count('id')).order_by('-total')[:10]
        )
        labels = []
        for item in qs:
            nombre = f"{item['veterinario_responsable__first_name']} {item['veterinario_responsable__last_name']}".strip()
            labels.append(nombre or item['veterinario_responsable__email'])
        return Response({'labels': labels, 'datos': [i['total'] for i in qs]})


class BiAlertasParametrosView(APIView):
    """Parámetros fuera de rango (ALTO/BAJO) con mayor frecuencia."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        qs = (
            ResultadoParametro.objects
            .filter(interpretacion__in=['ALTO', 'BAJO'])
            .values('parametro__nombre_parametro', 'interpretacion')
            .annotate(total=Count('id')).order_by('-total')[:12]
        )
        resultados = [
            {'parametro': i['parametro__nombre_parametro'], 'interpretacion': i['interpretacion'], 'total': i['total']}
            for i in qs
        ]
        return Response({
            'resultados':  resultados,
            'total_alto':  sum(r['total'] for r in resultados if r['interpretacion'] == 'ALTO'),
            'total_bajo':  sum(r['total'] for r in resultados if r['interpretacion'] == 'BAJO'),
            'labels': [r['parametro'] for r in resultados],
            'datos':  [r['total'] for r in resultados],
        })


class BiPacientesMasActivosView(APIView):
    """Top 8 pacientes con más solicitudes de examen."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        qs = (
            Paciente.objects
            .annotate(total_solicitudes=Count('solicitudes'))
            .filter(total_solicitudes__gt=0)
            .order_by('-total_solicitudes')
            .values('nombre', 'total_solicitudes', 'raza__especie__nombre')[:8]
        )
        return Response({
            'labels':   [i['nombre'] for i in qs],
            'datos':    [i['total_solicitudes'] for i in qs],
            'especies': [i['raza__especie__nombre'] or '?' for i in qs],
        })


class BiInsightsView(APIView):
    """Insights automáticos basados en reglas de negocio del laboratorio."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        insights = []
        hoy = date.today()
        inicio_mes = date(hoy.year, hoy.month, 1)

        total_muestras      = Muestra.objects.count()
        muestras_rechazadas = Muestra.objects.filter(estado='rechazada').count()
        muestras_pendientes = Muestra.objects.filter(estado='pendiente').count()
        sol_pendientes      = SolicitudExamen.objects.filter(estado='pendiente').count()
        fuera_rango         = ResultadoParametro.objects.filter(interpretacion__in=['ALTO', 'BAJO']).count()
        ingresos_mes        = float(Cobro.objects.filter(fecha__date__gte=inicio_mes).aggregate(t=Sum('monto_total'))['t'] or 0)

        if total_muestras > 0:
            tasa = muestras_rechazadas / total_muestras
            if tasa > 0.10:
                insights.append({'tipo': 'alerta', 'titulo': 'Alta tasa de rechazo de muestras', 'mensaje': f'El {tasa:.1%} de las muestras fueron rechazadas (umbral crítico: 10%).'})
            elif tasa > 0.05:
                insights.append({'tipo': 'advertencia', 'titulo': 'Tasa de rechazo moderada', 'mensaje': f'El {tasa:.1%} de las muestras fueron rechazadas. Se recomienda revisar el proceso de toma.'})

        if muestras_pendientes > 20:
            insights.append({'tipo': 'alerta', 'titulo': 'Acumulación de muestras pendientes', 'mensaje': f'Hay {muestras_pendientes} muestras en estado pendiente de procesamiento.'})
        elif muestras_pendientes > 10:
            insights.append({'tipo': 'advertencia', 'titulo': 'Muestras pendientes por atender', 'mensaje': f'{muestras_pendientes} muestras están pendientes. Revisar capacidad del equipo.'})

        if sol_pendientes > 10:
            insights.append({'tipo': 'advertencia', 'titulo': 'Solicitudes acumuladas', 'mensaje': f'{sol_pendientes} solicitudes de examen están pendientes de atención.'})

        if fuera_rango > 0:
            insights.append({'tipo': 'info', 'titulo': 'Parámetros clínicos fuera de rango', 'mensaje': f'{fuera_rango} parámetro(s) registrados fuera del rango de referencia normal.'})

        if ingresos_mes > 0:
            insights.append({'tipo': 'exito', 'titulo': 'Ingresos del mes en curso', 'mensaje': f'Ingresos acumulados este mes: Bs. {ingresos_mes:,.2f}'})

        if not insights:
            insights.append({'tipo': 'exito', 'titulo': 'Sistema operando con normalidad', 'mensaje': 'No se detectaron alertas críticas. Todos los indicadores están dentro de parámetros normales.'})

        return Response({'insights': insights, 'total': len(insights)})


# ─────────────────────────────────────────────────────────────────────────────
# CHATBOT IA — GOOGLE GEMINI
# ─────────────────────────────────────────────────────────────────────────────

class ChatbotLabView(APIView):
    """Chatbot inteligente del laboratorio usando Grok (xAI)."""
    permission_classes = [EsStaffInterno]

    def post(self, request):
        pregunta = request.data.get('pregunta', '').strip()
        if not pregunta:
            return Response({'error': 'La pregunta no puede estar vacía.'}, status=400)

        api_key = (
            os.environ.get('GROK_API_KEY', '')
            or getattr(settings, 'GROK_API_KEY', '')
        )
        if not api_key:
            return Response(
                {'error': 'El servicio de IA no está configurado. '
                          'Agrega GROK_API_KEY en el archivo .env y reinicia el servidor.'},
                status=503,
            )

        hoy = date.today()
        inicio_mes = date(hoy.year, hoy.month, 1)

        total_muestras       = Muestra.objects.count()
        muestras_pendientes  = Muestra.objects.filter(estado='pendiente').count()
        muestras_completadas = Muestra.objects.filter(estado='completada').count()
        muestras_rechazadas  = Muestra.objects.filter(estado='rechazada').count()
        total_solicitudes    = SolicitudExamen.objects.count()
        sol_pendientes       = SolicitudExamen.objects.filter(estado='pendiente').count()
        sol_completadas      = SolicitudExamen.objects.filter(estado='completado').count()
        total_pacientes      = Paciente.objects.count()
        ingresos_totales     = float(Cobro.objects.aggregate(t=Sum('monto_total'))['t'] or 0)
        ingresos_mes         = float(Cobro.objects.filter(fecha__date__gte=inicio_mes).aggregate(t=Sum('monto_total'))['t'] or 0)
        fuera_rango          = ResultadoParametro.objects.filter(interpretacion__in=['ALTO', 'BAJO']).count()
        top_examenes         = list(OrdenExamen.objects.values('examen__nombre_examen').annotate(total=Count('id')).order_by('-total')[:5])
        tasa_rechazo         = (muestras_rechazadas / total_muestras * 100) if total_muestras else 0

        system_prompt = f"""Eres VetBot, el asistente inteligente del laboratorio veterinario LACLIVET.
        Responde ÚNICAMENTE preguntas relacionadas al laboratorio veterinario, sus operaciones, datos y buenas prácticas clínicas.
        Si la pregunta no está relacionada al laboratorio, indica amablemente que solo puedes ayudar con temas del laboratorio.
        Responde siempre en español, de forma clara, concisa y profesional. Usa Markdown cuando sea útil.
        
        === DATOS ACTUALES DEL SISTEMA ({hoy.strftime('%d/%m/%Y')}) ===
        MUESTRAS: Total={total_muestras} | Pendientes={muestras_pendientes} | Completadas={muestras_completadas} | Rechazadas={muestras_rechazadas} | Tasa rechazo={tasa_rechazo:.1f}%
        SOLICITUDES: Total={total_solicitudes} | Pendientes={sol_pendientes} | Completadas={sol_completadas}
        PACIENTES: {total_pacientes} registrados
        INGRESOS: Total histórico=Bs.{ingresos_totales:,.2f} | Este mes=Bs.{ingresos_mes:,.2f}
        RESULTADOS: Parámetros fuera de rango={fuera_rango}
        TOP 5 EXÁMENES: {', '.join(f'{e["examen__nombre_examen"]}({e["total"]})' for e in top_examenes)}"""

        try:
            from openai import OpenAI, APIError, RateLimitError

            client = OpenAI(
                api_key=api_key,
                base_url="https://api.x.ai/v1",
            )
            completion = client.chat.completions.create(
                model="grok-4-fast",  # o "grok-4" si necesitas más capacidad de razonamiento
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": pregunta},
                ],
                max_tokens=500,
                temperature=0.7,
            )
            respuesta = completion.choices[0].message.content

        except RateLimitError as exc:
            logger.warning("Cuota de Grok agotada: %s", exc)
            return Response(
                {'error': 'El asistente de IA no está disponible en este momento '
                          '(cuota del servicio agotada). Intenta más tarde.'},
                status=503,
            )
        except APIError as exc:
            logger.exception("Error de la API de Grok")
            return Response(
                {'error': f'Error al comunicarse con el servicio de IA: {exc}'},
                status=502,
            )
        except Exception as exc:
            logger.exception("Error inesperado llamando a Grok API")
            return Response(
                {'error': f'Error al comunicarse con el servicio de IA: {exc}'},
                status=502,
            )

        return Response({'respuesta': respuesta})


# ─────────────────────────────────────────────────────────────────────────────
# REPORTES DINÁMICOS — JSON + PDF + CSV
# ─────────────────────────────────────────────────────────────────────────────

ALL_COLS_MUESTRAS    = ['codigo', 'tipo_muestra', 'estado', 'fecha_recepcion', 'paciente', 'especie', 'solicitud_codigo', 'observaciones']
ALL_COLS_SOLICITUDES = ['codigo', 'estado', 'fecha_solicitud', 'paciente', 'especie', 'medico_veterinario', 'examenes', 'monto_total', 'metodo_pago']
ALL_COLS_EXAMENES    = ['id', 'examen', 'catalogo', 'estado', 'fecha_resultado', 'paciente', 'especie', 'veterinario', 'observaciones']


def _parse_columnas(raw: str, all_cols: list) -> list:
    if not raw:
        return all_cols
    return [c for c in raw.split(',') if c in all_cols] or all_cols


class ReporteMuestrasView(APIView):
    """Reporte de muestras — soporta formato=json|pdf|csv."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        fecha_inicio = _parse_date(request.query_params.get('fecha_inicio'))
        fecha_fin    = _parse_date(request.query_params.get('fecha_fin'))
        estado       = request.query_params.get('estado', '')
        tipo_muestra = request.query_params.get('tipo_muestra', '')
        formato      = request.query_params.get('formato', 'json')
        columnas     = _parse_columnas(request.query_params.get('columnas', ''), ALL_COLS_MUESTRAS)

        qs = Muestra.objects.select_related(
            'paciente', 'paciente__raza', 'paciente__raza__especie', 'solicitud'
        ).order_by('-fecha_recepcion')

        if fecha_inicio: qs = qs.filter(fecha_recepcion__gte=fecha_inicio)
        if fecha_fin:    qs = qs.filter(fecha_recepcion__lte=fecha_fin)
        if estado:       qs = qs.filter(estado=estado)
        if tipo_muestra: qs = qs.filter(tipo_muestra__icontains=tipo_muestra)

        def _row(m):
            return {
                'id': m.id, 'codigo': m.codigo, 'tipo_muestra': m.tipo_muestra or '—',
                'estado': m.estado,
                'fecha_recepcion': m.fecha_recepcion.isoformat() if m.fecha_recepcion else None,
                'paciente': m.paciente.nombre if m.paciente else '—',
                'especie': (m.paciente.raza.especie.nombre if m.paciente and m.paciente.raza and m.paciente.raza.especie else '—'),
                'solicitud_codigo': m.solicitud.codigo if m.solicitud else '—',
                'observaciones': m.observaciones or '',
            }

        if formato == 'pdf':
            ctx = {'titulo': 'Reporte de Muestras', 'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin,
                   'filtros': {'estado': estado, 'tipo_muestra': tipo_muestra}, 'muestras': qs,
                   'total': qs.count(), 'columnas': columnas, 'fecha_generacion': date.today()}
            return _render_pdf('pdf/reporte_muestras.html', ctx, f'reporte_muestras_{date.today()}.pdf')

        if formato == 'csv':
            headers = {'codigo': 'Código', 'tipo_muestra': 'Tipo', 'estado': 'Estado',
                       'fecha_recepcion': 'Fecha Recepción', 'paciente': 'Paciente', 'especie': 'Especie',
                       'solicitud_codigo': 'Solicitud', 'observaciones': 'Observaciones'}
            resp = HttpResponse(content_type='text/csv; charset=utf-8')
            resp['Content-Disposition'] = f'attachment; filename="reporte_muestras_{date.today()}.csv"'
            resp.write('\ufeff')
            w = csv.writer(resp)
            w.writerow([headers[c] for c in columnas])
            for m in qs:
                r = _row(m)
                w.writerow([r[c] for c in columnas])
            return resp

        data = [_row(m) for m in qs]
        return Response({'total': len(data), 'resultados': data})


class ReporteSolicitudesView(APIView):
    """Reporte de solicitudes — soporta formato=json|pdf|csv."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        fecha_inicio = _parse_date(request.query_params.get('fecha_inicio'))
        fecha_fin    = _parse_date(request.query_params.get('fecha_fin'))
        estado       = request.query_params.get('estado', '')
        formato      = request.query_params.get('formato', 'json')
        columnas     = _parse_columnas(request.query_params.get('columnas', ''), ALL_COLS_SOLICITUDES)

        qs = SolicitudExamen.objects.select_related(
            'paciente', 'paciente__raza', 'paciente__raza__especie', 'medico_veterinario', 'cobro'
        ).prefetch_related('detalles__examen').order_by('-fecha_solicitud')

        if fecha_inicio: qs = qs.filter(fecha_solicitud__date__gte=fecha_inicio)
        if fecha_fin:    qs = qs.filter(fecha_solicitud__date__lte=fecha_fin)
        if estado:       qs = qs.filter(estado=estado)

        def _row(s):
            return {
                'id': s.id, 'codigo': s.codigo, 'estado': s.estado,
                'fecha_solicitud': s.fecha_solicitud.isoformat(),
                'paciente': s.paciente.nombre if s.paciente else '—',
                'especie': (s.paciente.raza.especie.nombre if s.paciente and s.paciente.raza and s.paciente.raza.especie else '—'),
                'medico_veterinario': str(s.medico_veterinario) if s.medico_veterinario else '—',
                'monto_total': float(s.cobro.monto_total) if s.cobro and s.cobro.monto_total else None,
                'metodo_pago': s.cobro.metodo_pago if s.cobro else None,
                'examenes': [d.examen.nombre_examen for d in s.detalles.all() if d.examen],
            }

        if formato == 'pdf':
            ctx = {'titulo': 'Reporte de Solicitudes de Examen', 'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin,
                   'filtros': {'estado': estado}, 'solicitudes': qs, 'total': qs.count(),
                   'total_ingresos': qs.aggregate(t=Sum('cobro__monto_total'))['t'] or 0,
                   'columnas': columnas, 'fecha_generacion': date.today()}
            return _render_pdf('pdf/reporte_solicitudes.html', ctx, f'reporte_solicitudes_{date.today()}.pdf')

        if formato == 'csv':
            headers = {'codigo': 'Código', 'estado': 'Estado', 'fecha_solicitud': 'Fecha',
                       'paciente': 'Paciente', 'especie': 'Especie', 'medico_veterinario': 'Médico Vet.',
                       'examenes': 'Exámenes', 'monto_total': 'Monto (Bs.)', 'metodo_pago': 'Método Pago'}
            resp = HttpResponse(content_type='text/csv; charset=utf-8')
            resp['Content-Disposition'] = f'attachment; filename="reporte_solicitudes_{date.today()}.csv"'
            resp.write('\ufeff')
            w = csv.writer(resp)
            w.writerow([headers[c] for c in columnas])
            for s in qs:
                r = _row(s)
                r['examenes'] = '; '.join(r['examenes'])
                r['fecha_solicitud'] = s.fecha_solicitud.strftime('%Y-%m-%d')
                w.writerow([r[c] for c in columnas])
            return resp

        data = [_row(s) for s in qs]
        return Response({'total': len(data), 'resultados': data})


class ReporteExamenesView(APIView):
    """Reporte de órdenes de examen — soporta formato=json|pdf|csv."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        fecha_inicio = _parse_date(request.query_params.get('fecha_inicio'))
        fecha_fin    = _parse_date(request.query_params.get('fecha_fin'))
        estado       = request.query_params.get('estado', '')
        catalogo_id  = request.query_params.get('catalogo', '')
        formato      = request.query_params.get('formato', 'json')
        columnas     = _parse_columnas(request.query_params.get('columnas', ''), ALL_COLS_EXAMENES)

        qs = OrdenExamen.objects.select_related(
            'examen', 'examen__catalogo', 'orden', 'orden__paciente',
            'orden__paciente__raza', 'orden__paciente__raza__especie', 'veterinario_responsable',
        ).order_by('-fecha_resultado', '-id')

        if fecha_inicio: qs = qs.filter(fecha_resultado__date__gte=fecha_inicio)
        if fecha_fin:    qs = qs.filter(fecha_resultado__date__lte=fecha_fin)
        if estado:       qs = qs.filter(estado=estado)
        if catalogo_id:  qs = qs.filter(examen__catalogo_id=catalogo_id)

        def _vet(oe):
            if not oe.veterinario_responsable: return '—'
            return (f"{oe.veterinario_responsable.first_name} {oe.veterinario_responsable.last_name}".strip()
                    or oe.veterinario_responsable.email)

        def _row(oe):
            return {
                'id': oe.id, 'examen': oe.examen.nombre_examen,
                'catalogo': oe.examen.catalogo.nombre if oe.examen.catalogo else '—',
                'estado': oe.estado,
                'fecha_resultado': oe.fecha_resultado.isoformat() if oe.fecha_resultado else None,
                'paciente': oe.orden.paciente.nombre if oe.orden.paciente else '—',
                'especie': (oe.orden.paciente.raza.especie.nombre if oe.orden.paciente and oe.orden.paciente.raza and oe.orden.paciente.raza.especie else '—'),
                'veterinario': _vet(oe), 'observaciones': oe.observaciones or '',
            }

        if formato == 'pdf':
            ctx = {'titulo': 'Reporte de Exámenes', 'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin,
                   'filtros': {'estado': estado}, 'examenes': qs, 'total': qs.count(),
                   'columnas': columnas, 'fecha_generacion': date.today()}
            return _render_pdf('pdf/reporte_examenes.html', ctx, f'reporte_examenes_{date.today()}.pdf')

        if formato == 'csv':
            headers = {'id': '#', 'examen': 'Examen', 'catalogo': 'Catálogo', 'estado': 'Estado',
                       'fecha_resultado': 'Fecha Resultado', 'paciente': 'Paciente', 'especie': 'Especie',
                       'veterinario': 'Veterinario Resp.', 'observaciones': 'Observaciones'}
            resp = HttpResponse(content_type='text/csv; charset=utf-8')
            resp['Content-Disposition'] = f'attachment; filename="reporte_examenes_{date.today()}.csv"'
            resp.write('\ufeff')
            w = csv.writer(resp)
            w.writerow([headers[c] for c in columnas])
            for oe in qs:
                r = _row(oe)
                if r['fecha_resultado']:
                    r['fecha_resultado'] = oe.fecha_resultado.strftime('%Y-%m-%d')
                w.writerow([r[c] for c in columnas])
            return resp

        data = [_row(oe) for oe in qs]
        return Response({'total': len(data), 'resultados': data})

