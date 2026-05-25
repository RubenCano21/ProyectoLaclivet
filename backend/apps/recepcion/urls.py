from django.urls import path
from .views import (
    CobroListCreateView, CobroDetailView,
    SolicitudExamenListCreateView, SolicitudExamenDetailView,
    DetalleSolicitudListCreateView, DetalleSolicitudDetailView,
)

urlpatterns = [
    path('cobros/', CobroListCreateView.as_view(), name='cobro-list-create'),
    path('cobros/<int:pk>/', CobroDetailView.as_view(), name='cobro-detail'),
    path('solicitudes/', SolicitudExamenListCreateView.as_view(), name='solicitud-list-create'),
    path('solicitudes/<int:pk>/', SolicitudExamenDetailView.as_view(), name='solicitud-detail'),
    path('detalles/', DetalleSolicitudListCreateView.as_view(), name='detalle-list-create'),
    path('detalles/<int:pk>/', DetalleSolicitudDetailView.as_view(), name='detalle-detail'),
]
