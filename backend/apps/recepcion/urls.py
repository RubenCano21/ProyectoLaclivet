from django.urls import path
from .views import (
    CobroListCreateView, CobroDetailView,
    SolicitudExamenListCreateView, SolicitudExamenDetailView,
    DetalleSolicitudListCreateView, DetalleSolicitudDetailView,

    SolicitudExamenCrearConExamenesView,
    SolicitudExamenFullDetailView,
    SolicitudExamenListFiltradaView,
    SolicitudExamenCambiarEstadoView,
)

urlpatterns = [
    path('cobros/', CobroListCreateView.as_view(), name='cobro-list-create'),
    path('cobros/<int:pk>/', CobroDetailView.as_view(), name='cobro-detail'),
    path('solicitudes/', SolicitudExamenListCreateView.as_view(), name='solicitud-list-create'),
    path('solicitudes/<int:pk>/', SolicitudExamenDetailView.as_view(), name='solicitud-detail'),
    path('detalles/', DetalleSolicitudListCreateView.as_view(), name='detalle-list-create'),
    path('detalles/<int:pk>/', DetalleSolicitudDetailView.as_view(), name='detalle-detail'),

# NUEVO — flujo de gestión de exámenes/muestras
    path('solicitudes/crear-con-examenes/', SolicitudExamenCrearConExamenesView.as_view(), name='solicitud-crear-con-examenes'),
    path('solicitudes/listado/', SolicitudExamenListFiltradaView.as_view(), name='solicitud-listado-filtrado'),
    path('solicitudes/<int:pk>/completo/', SolicitudExamenFullDetailView.as_view(), name='solicitud-full-detail'),
    path('solicitudes/<int:pk>/cambiar-estado/', SolicitudExamenCambiarEstadoView.as_view(), name='solicitud-cambiar-estado'),
]
