from io import BytesIO

from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta, date

from rest_framework.views import APIView
from rest_framework.response import Response
from xhtml2pdf import pisa

from apps.core.permissions import EsStaffInterno

from apps.muestra.models import Muestra
from apps.recepcion.models import SolicitudExamen, Cobro
from apps.paciente.models import Paciente
from apps.catalogo.models import OrdenExamen


def _ultimos_meses(n=6):
    """Devuelve lista de los últimos n meses como strings 'YYYY-MM'."""
    hoy = date.today()
    meses = []
    for i in range(n - 1, -1, -1):
        d = date(hoy.year, hoy.month, 1) - timedelta(days=i * 30)
        meses.append(f"{d.year}-{d.month:02d}")
    return meses


class BiResumenView(APIView):
    """KPIs generales del laboratorio."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        total_muestras = Muestra.objects.count()
        total_solicitudes = SolicitudExamen.objects.count()
        total_pacientes = Paciente.objects.count()
        total_ingresos = Cobro.objects.aggregate(total=Sum('monto_total'))['total'] or 0

        solicitudes_pendientes = SolicitudExamen.objects.filter(estado='pendiente').count()
        muestras_pendientes = Muestra.objects.filter(estado='pendiente').count()

        # Variación respecto al mes anterior
        hoy = date.today()
        inicio_mes_actual = date(hoy.year, hoy.month, 1)
        inicio_mes_anterior = (inicio_mes_actual - timedelta(days=1)).replace(day=1)

        muestras_mes = Muestra.objects.filter(fecha_recepcion__gte=inicio_mes_actual).count()
        muestras_mes_ant = Muestra.objects.filter(
            fecha_recepcion__gte=inicio_mes_anterior,
            fecha_recepcion__lt=inicio_mes_actual
        ).count()

        sol_mes = SolicitudExamen.objects.filter(
            fecha_solicitud__date__gte=inicio_mes_actual
        ).count()
        sol_mes_ant = SolicitudExamen.objects.filter(
            fecha_solicitud__date__gte=inicio_mes_anterior,
            fecha_solicitud__date__lt=inicio_mes_actual
        ).count()

        ingresos_mes = Cobro.objects.filter(
            fecha__date__gte=inicio_mes_actual
        ).aggregate(total=Sum('monto_total'))['total'] or 0

        return Response({
            'total_muestras': total_muestras,
            'total_solicitudes': total_solicitudes,
            'total_pacientes': total_pacientes,
            'total_ingresos': float(total_ingresos),
            'solicitudes_pendientes': solicitudes_pendientes,
            'muestras_pendientes': muestras_pendientes,
            'muestras_este_mes': muestras_mes,
            'muestras_mes_anterior': muestras_mes_ant,
            'solicitudes_este_mes': sol_mes,
            'solicitudes_mes_anterior': sol_mes_ant,
            'ingresos_este_mes': float(ingresos_mes),
        })


class BiMuestrasPorMesView(APIView):
    """Tendencia de muestras recibidas en los últimos 6 meses."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        meses = _ultimos_meses(6)
        inicio = date.today().replace(day=1) - timedelta(days=150)

        qs = (
            Muestra.objects
            .filter(fecha_recepcion__gte=inicio)
            .annotate(mes=TruncMonth('fecha_recepcion'))
            .values('mes')
            .annotate(total=Count('id'))
            .order_by('mes')
        )

        por_mes = {m['mes'].strftime('%Y-%m'): m['total'] for m in qs if m['mes']}

        return Response({
            'labels': meses,
            'datos': [por_mes.get(m, 0) for m in meses],
        })


class BiSolicitudesPorMesView(APIView):
    """Tendencia de solicitudes en los últimos 6 meses."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        meses = _ultimos_meses(6)
        inicio = timezone.now() - timedelta(days=180)

        qs = (
            SolicitudExamen.objects
            .filter(fecha_solicitud__gte=inicio)
            .annotate(mes=TruncMonth('fecha_solicitud'))
            .values('mes')
            .annotate(total=Count('id'))
            .order_by('mes')
        )

        por_mes = {m['mes'].strftime('%Y-%m'): m['total'] for m in qs}

        return Response({
            'labels': meses,
            'datos': [por_mes.get(m, 0) for m in meses],
        })


class BiIngresosPorMesView(APIView):
    """Ingresos totales por mes (últimos 6 meses)."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        meses = _ultimos_meses(6)
        inicio = timezone.now() - timedelta(days=180)

        qs = (
            Cobro.objects
            .filter(fecha__gte=inicio)
            .annotate(mes=TruncMonth('fecha'))
            .values('mes')
            .annotate(total=Sum('monto_total'))
            .order_by('mes')
        )

        por_mes = {m['mes'].strftime('%Y-%m'): float(m['total'] or 0) for m in qs}

        return Response({
            'labels': meses,
            'datos': [por_mes.get(m, 0.0) for m in meses],
        })


class BiSolicitudesPorEstadoView(APIView):
    """Distribución de solicitudes por estado."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        qs = (
            SolicitudExamen.objects
            .values('estado')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        labels = [item['estado'].replace('_', ' ').capitalize() for item in qs]
        datos  = [item['total'] for item in qs]
        return Response({'labels': labels, 'datos': datos})


class BiTiposMuestraView(APIView):
    """Distribución de muestras por tipo."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        qs = (
            Muestra.objects
            .values('tipo_muestra')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        labels = [item['tipo_muestra'] or 'Sin tipo' for item in qs]
        datos  = [item['total'] for item in qs]
        return Response({'labels': labels, 'datos': datos})


class BiMuestrasPorEstadoView(APIView):
    """Distribución de muestras por estado."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        qs = (
            Muestra.objects
            .values('estado')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        labels = [item['estado'].replace('_', ' ').capitalize() for item in qs]
        datos  = [item['total'] for item in qs]
        return Response({'labels': labels, 'datos': datos})


class BiEspeciesView(APIView):
    """Distribución de pacientes por especie."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        qs = (
            Paciente.objects
            .exclude(raza__isnull=True)
            .values('raza__especie__nombre')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        labels = [item['raza__especie__nombre'] or 'Desconocida' for item in qs]
        datos  = [item['total'] for item in qs]

        # Pacientes sin especie asignada
        sin_especie = Paciente.objects.filter(raza__isnull=True).count()
        if sin_especie:
            labels.append('Sin especie')
            datos.append(sin_especie)

        return Response({'labels': labels, 'datos': datos})


class BiExamenesTopView(APIView):
    """Top 8 exámenes más solicitados."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        qs = (
            OrdenExamen.objects
            .values('examen__nombre_examen')
            .annotate(total=Count('id'))
            .order_by('-total')[:8]
        )
        labels = [item['examen__nombre_examen'] for item in qs]
        datos  = [item['total'] for item in qs]
        return Response({'labels': labels, 'datos': datos})


# ─────────────────────────────────────────────────────────────────────────────
# REPORTES DINÁMICOS CON FILTROS Y EXPORTACIÓN PDF
# ─────────────────────────────────────────────────────────────────────────────

def _parse_date(value):
    """Convierte string 'YYYY-MM-DD' a date o None."""
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _render_pdf(template_name, context, filename):
    """Renderiza una plantilla HTML a PDF y retorna HttpResponse."""
    html = render_to_string(template_name, context)
    buffer = BytesIO()
    result = pisa.CreatePDF(html, dest=buffer, encoding='utf-8')
    if result.err:
        return HttpResponse('Error generando PDF', status=500)
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


ALL_COLS_MUESTRAS    = ['codigo','tipo_muestra','estado','fecha_recepcion','paciente','especie','solicitud_codigo','observaciones']
ALL_COLS_SOLICITUDES = ['codigo','estado','fecha_solicitud','paciente','especie','medico_veterinario','examenes','monto_total','metodo_pago']
ALL_COLS_EXAMENES    = ['id','examen','catalogo','estado','fecha_resultado','paciente','especie','veterinario','observaciones']


def _parse_columnas(raw: str, all_cols: list) -> list:
    """Devuelve lista de columnas válidas; si no se especifica, devuelve todas."""
    if not raw:
        return all_cols
    return [c for c in raw.split(',') if c in all_cols] or all_cols


class ReporteMuestrasView(APIView):
    """Reporte de muestras con filtros de fecha, estado y tipo."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        fecha_inicio = _parse_date(request.query_params.get('fecha_inicio'))
        fecha_fin    = _parse_date(request.query_params.get('fecha_fin'))
        estado       = request.query_params.get('estado', '')
        tipo_muestra = request.query_params.get('tipo_muestra', '')
        formato      = request.query_params.get('formato', 'json')
        columnas     = _parse_columnas(request.query_params.get('columnas', ''), ALL_COLS_MUESTRAS)

        qs = Muestra.objects.select_related(
            'paciente', 'paciente__raza', 'paciente__raza__especie',
            'solicitud'
        ).order_by('-fecha_recepcion')

        if fecha_inicio:
            qs = qs.filter(fecha_recepcion__gte=fecha_inicio)
        if fecha_fin:
            qs = qs.filter(fecha_recepcion__lte=fecha_fin)
        if estado:
            qs = qs.filter(estado=estado)
        if tipo_muestra:
            qs = qs.filter(tipo_muestra__icontains=tipo_muestra)

        if formato == 'pdf':
            context = {
                'titulo': 'Reporte de Muestras',
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'filtros': {'estado': estado, 'tipo_muestra': tipo_muestra},
                'muestras': qs,
                'total': qs.count(),
                'columnas': columnas,
                'fecha_generacion': date.today(),
            }
            return _render_pdf('pdf/reporte_muestras.html', context,
                               f'reporte_muestras_{date.today()}.pdf')

        data = [
            {
                'id': m.id,
                'codigo': m.codigo,
                'tipo_muestra': m.tipo_muestra or '—',
                'estado': m.estado,
                'fecha_recepcion': m.fecha_recepcion.isoformat() if m.fecha_recepcion else None,
                'paciente': m.paciente.nombre if m.paciente else '—',
                'especie': (
                    m.paciente.raza.especie.nombre
                    if m.paciente and m.paciente.raza and m.paciente.raza.especie
                    else '—'
                ),
                'solicitud_codigo': m.solicitud.codigo if m.solicitud else '—',
                'observaciones': m.observaciones or '',
            }
            for m in qs
        ]
        return Response({'total': len(data), 'resultados': data})


class ReporteSolicitudesView(APIView):
    """Reporte de solicitudes de examen con filtros."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        fecha_inicio = _parse_date(request.query_params.get('fecha_inicio'))
        fecha_fin    = _parse_date(request.query_params.get('fecha_fin'))
        estado       = request.query_params.get('estado', '')
        formato      = request.query_params.get('formato', 'json')
        columnas     = _parse_columnas(request.query_params.get('columnas', ''), ALL_COLS_SOLICITUDES)

        qs = SolicitudExamen.objects.select_related(
            'paciente', 'paciente__raza', 'paciente__raza__especie',
            'medico_veterinario', 'cobro'
        ).prefetch_related('detalles__examen').order_by('-fecha_solicitud')

        if fecha_inicio:
            qs = qs.filter(fecha_solicitud__date__gte=fecha_inicio)
        if fecha_fin:
            qs = qs.filter(fecha_solicitud__date__lte=fecha_fin)
        if estado:
            qs = qs.filter(estado=estado)

        if formato == 'pdf':
            context = {
                'titulo': 'Reporte de Solicitudes de Examen',
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'filtros': {'estado': estado},
                'solicitudes': qs,
                'total': qs.count(),
                'total_ingresos': qs.aggregate(
                    t=Sum('cobro__monto_total')
                )['t'] or 0,
                'columnas': columnas,
                'fecha_generacion': date.today(),
            }
            return _render_pdf('pdf/reporte_solicitudes.html', context,
                               f'reporte_solicitudes_{date.today()}.pdf')

        data = [
            {
                'id': s.id,
                'codigo': s.codigo,
                'estado': s.estado,
                'fecha_solicitud': s.fecha_solicitud.isoformat(),
                'paciente': s.paciente.nombre if s.paciente else '—',
                'especie': (
                    s.paciente.raza.especie.nombre
                    if s.paciente and s.paciente.raza and s.paciente.raza.especie
                    else '—'
                ),
                'medico_veterinario': str(s.medico_veterinario) if s.medico_veterinario else '—',
                'monto_total': float(s.cobro.monto_total) if s.cobro and s.cobro.monto_total else None,
                'metodo_pago': s.cobro.metodo_pago if s.cobro else None,
                'examenes': [d.examen.nombre_examen for d in s.detalles.all() if d.examen],
            }
            for s in qs
        ]
        return Response({'total': len(data), 'resultados': data})


class ReporteExamenesView(APIView):
    """Reporte de órdenes de examen con filtros."""
    permission_classes = [EsStaffInterno]

    def get(self, request):
        fecha_inicio = _parse_date(request.query_params.get('fecha_inicio'))
        fecha_fin    = _parse_date(request.query_params.get('fecha_fin'))
        estado       = request.query_params.get('estado', '')
        catalogo_id  = request.query_params.get('catalogo', '')
        formato      = request.query_params.get('formato', 'json')
        columnas     = _parse_columnas(request.query_params.get('columnas', ''), ALL_COLS_EXAMENES)

        qs = OrdenExamen.objects.select_related(
            'examen', 'examen__catalogo',
            'orden', 'orden__paciente',
            'orden__paciente__raza', 'orden__paciente__raza__especie',
            'veterinario_responsable',
        ).order_by('-fecha_resultado', '-id')

        if fecha_inicio:
            qs = qs.filter(fecha_resultado__date__gte=fecha_inicio)
        if fecha_fin:
            qs = qs.filter(fecha_resultado__date__lte=fecha_fin)
        if estado:
            qs = qs.filter(estado=estado)
        if catalogo_id:
            qs = qs.filter(examen__catalogo_id=catalogo_id)

        if formato == 'pdf':
            context = {
                'titulo': 'Reporte de Exámenes',
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'filtros': {'estado': estado},
                'examenes': qs,
                'total': qs.count(),
                'columnas': columnas,
                'fecha_generacion': date.today(),
            }
            return _render_pdf('pdf/reporte_examenes.html', context,
                               f'reporte_examenes_{date.today()}.pdf')

        data = [
            {
                'id': oe.id,
                'examen': oe.examen.nombre_examen,
                'catalogo': oe.examen.catalogo.nombre if oe.examen.catalogo else '—',
                'estado': oe.estado,
                'fecha_resultado': oe.fecha_resultado.isoformat() if oe.fecha_resultado else None,
                'paciente': oe.orden.paciente.nombre if oe.orden.paciente else '—',
                'especie': (
                    oe.orden.paciente.raza.especie.nombre
                    if oe.orden.paciente and oe.orden.paciente.raza and oe.orden.paciente.raza.especie
                    else '—'
                ),
                'veterinario': (
                    f"{oe.veterinario_responsable.first_name} {oe.veterinario_responsable.last_name}".strip()
                    or oe.veterinario_responsable.email
                ) if oe.veterinario_responsable else '—',
                'observaciones': oe.observaciones or '',
            }
            for oe in qs
        ]
        return Response({'total': len(data), 'resultados': data})

