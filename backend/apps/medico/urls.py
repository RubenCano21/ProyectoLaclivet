from django.urls import path
from .views import MedicoVeterinarioListCreateView, MedicoVeterinarioDetailView

urlpatterns = [
    path('', MedicoVeterinarioListCreateView.as_view(), name='medico-list-create'),
    path('<int:pk>/', MedicoVeterinarioDetailView.as_view(), name='medico-detail'),
]

