from django.urls import path
from .views import (
    EspecieListCreateView, EspecieDetailView,
    RazaListCreateView, RazaDetailView,
    PacienteListCreateView, PacienteDetailView, PacienteHistorialView,
    AntecedentePacienteListCreateView, AntecedentePacienteDetailView,
)

urlpatterns = [
    # Especies
    path('especies/', EspecieListCreateView.as_view(), name='especie-list-create'),
    path('especies/<int:pk>/', EspecieDetailView.as_view(), name='especie-detail'),

    # Razas
    path('razas/', RazaListCreateView.as_view(), name='raza-list-create'),
    path('razas/<int:pk>/', RazaDetailView.as_view(), name='raza-detail'),

    # Pacientes
    path('', PacienteListCreateView.as_view(), name='paciente-list-create'),
    path('<int:pk>/', PacienteDetailView.as_view(), name='paciente-detail'),

    # Historial dinámico CU16
    path('<int:pk>/historial/', PacienteHistorialView.as_view(), name='paciente-historial'),

    # Antecedentes
    path('antecedentes/', AntecedentePacienteListCreateView.as_view(), name='antecedente-list-create'),
    path('antecedentes/<int:pk>/', AntecedentePacienteDetailView.as_view(), name='antecedente-detail'),
]
