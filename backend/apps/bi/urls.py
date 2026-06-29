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
)

urlpatterns = [
    path('resumen/',              BiResumenView.as_view(),              name='bi-resumen'),
    path('muestras-por-mes/',     BiMuestrasPorMesView.as_view(),       name='bi-muestras-mes'),
    path('solicitudes-por-mes/',  BiSolicitudesPorMesView.as_view(),    name='bi-solicitudes-mes'),
    path('ingresos-por-mes/',     BiIngresosPorMesView.as_view(),       name='bi-ingresos-mes'),
    path('solicitudes-estado/',   BiSolicitudesPorEstadoView.as_view(), name='bi-solicitudes-estado'),
    path('tipos-muestra/',        BiTiposMuestraView.as_view(),         name='bi-tipos-muestra'),
    path('muestras-estado/',      BiMuestrasPorEstadoView.as_view(),    name='bi-muestras-estado'),
    path('especies/',             BiEspeciesView.as_view(),             name='bi-especies'),
    path('examenes-top/',         BiExamenesTopView.as_view(),          name='bi-examenes-top'),
]

