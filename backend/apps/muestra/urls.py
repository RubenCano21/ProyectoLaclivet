from django.urls import path
from .views import (
    MuestraListCreateView, MuestraDetailView,
    IncidenciaMuestraListCreateView, IncidenciaMuestraDetailView,
)

urlpatterns = [
    path('', MuestraListCreateView.as_view(), name='muestra-list-create'),
    path('<int:pk>/', MuestraDetailView.as_view(), name='muestra-detail'),
    path('incidencias/', IncidenciaMuestraListCreateView.as_view(), name='incidencia-list-create'),
    path('incidencias/<int:pk>/', IncidenciaMuestraDetailView.as_view(), name='incidencia-detail'),
]

