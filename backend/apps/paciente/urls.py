from django.urls import path
from .views import (
    EspecieListCreateView, EspecieDetailView,
    RazaListCreateView, RazaDetailView,
    HistorialClinicoListCreateView, HistorialClinicoDetailView,
    PacienteListCreateView, PacienteDetailView,
)

urlpatterns = [
    path('especies/', EspecieListCreateView.as_view(), name='especie-list-create'),
    path('especies/<int:pk>/', EspecieDetailView.as_view(), name='especie-detail'),
    path('razas/', RazaListCreateView.as_view(), name='raza-list-create'),
    path('razas/<int:pk>/', RazaDetailView.as_view(), name='raza-detail'),
    path('historiales/', HistorialClinicoListCreateView.as_view(), name='historial-list-create'),
    path('historiales/<int:pk>/', HistorialClinicoDetailView.as_view(), name='historial-detail'),
    path('pacientes/', PacienteListCreateView.as_view(), name='paciente-list-create'),
    path('pacientes/<int:pk>/', PacienteDetailView.as_view(), name='paciente-detail'),
]
