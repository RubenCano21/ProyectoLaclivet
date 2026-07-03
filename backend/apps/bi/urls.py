from django.urls import path
from .views import (
    BiResumenView,
    BiMuestrasPorMesView,
    BiSolicitudesPorMesView,
    BiIngresosPorMesView,
    BiSolicitudesPorEstadoView,
    BiTiposMuestraView,
    BiMuestrasPorEstadoView,
    BiEspeciesView,
    BiExamenesTopView,
    # Nuevos analíticos
    BiIngresosPorMetodoPagoView,
    BiRendimientoVeterinariosView,
    BiAlertasParametrosView,
    BiPacientesMasActivosView,
    BiInsightsView,
    # Chatbot IA
    ChatbotLabView,
    # Reportes dinámicos
    ReporteMuestrasView,
    ReporteSolicitudesView,
    ReporteExamenesView,
)

urlpatterns = [
    path('resumen/',                  BiResumenView.as_view(),                 name='bi-resumen'),
    path('muestras-por-mes/',         BiMuestrasPorMesView.as_view(),          name='bi-muestras-mes'),
    path('solicitudes-por-mes/',      BiSolicitudesPorMesView.as_view(),       name='bi-solicitudes-mes'),
    path('ingresos-por-mes/',         BiIngresosPorMesView.as_view(),          name='bi-ingresos-mes'),
    path('solicitudes-estado/',       BiSolicitudesPorEstadoView.as_view(),    name='bi-solicitudes-estado'),
    path('tipos-muestra/',            BiTiposMuestraView.as_view(),            name='bi-tipos-muestra'),
    path('muestras-estado/',          BiMuestrasPorEstadoView.as_view(),       name='bi-muestras-estado'),
    path('especies/',                 BiEspeciesView.as_view(),                name='bi-especies'),
    path('examenes-top/',             BiExamenesTopView.as_view(),             name='bi-examenes-top'),
    # ── Nuevos endpoints analíticos ─────────────────────────────────────────
    path('ingresos-metodo-pago/',     BiIngresosPorMetodoPagoView.as_view(),   name='bi-ingresos-metodo'),
    path('rendimiento-veterinarios/', BiRendimientoVeterinariosView.as_view(), name='bi-rendimiento-vets'),
    path('alertas-parametros/',       BiAlertasParametrosView.as_view(),       name='bi-alertas-parametros'),
    path('pacientes-activos/',        BiPacientesMasActivosView.as_view(),     name='bi-pacientes-activos'),
    path('insights/',                 BiInsightsView.as_view(),                name='bi-insights'),
    # ── Chatbot IA ──────────────────────────────────────────────────────────
    path('chatbot/',                  ChatbotLabView.as_view(),                name='bi-chatbot'),
    # ── Reportes dinámicos ──────────────────────────────────────────────────
    path('reporte-muestras/',         ReporteMuestrasView.as_view(),           name='bi-reporte-muestras'),
    path('reporte-solicitudes/',      ReporteSolicitudesView.as_view(),        name='bi-reporte-solicitudes'),
    path('reporte-examenes/',         ReporteExamenesView.as_view(),           name='bi-reporte-examenes'),
]
