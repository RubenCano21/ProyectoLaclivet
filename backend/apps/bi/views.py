from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta, date

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.muestra.models import Muestra
from apps.recepcion.models import SolicitudExamen, Cobro
from apps.paciente.models import Paciente
from apps.catalogo.models import Examen, OrdenExamen


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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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

