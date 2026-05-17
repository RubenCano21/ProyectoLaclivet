from django.urls import path
from .views import PropietarioListCreateView, PropietarioDetailView

urlpatterns = [
    path('', PropietarioListCreateView.as_view(), name='propietario-list-create'),
    path('<int:pk>/', PropietarioDetailView.as_view(), name='propietario-detail'),
]

