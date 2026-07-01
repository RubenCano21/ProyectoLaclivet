from django.urls import path
from .views import PropietarioListCreateView, PropietarioDetailView, ResultadosPropietarioView

urlpatterns = [
    path('', PropietarioListCreateView.as_view(), name='propietario-list-create'),
    path('<int:pk>/', PropietarioDetailView.as_view(), name='propietario-detail'),
    path('mis-resultados/', ResultadosPropietarioView.as_view(), name='propietario-mis-resultados'),
]

