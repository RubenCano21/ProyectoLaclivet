from django.urls import path
from .views import (
    CatalogoExamenListCreateView, CatalogoExamenDetailView,
    ExamenListCreateView, ExamenDetailView,
)

urlpatterns = [
    path('', CatalogoExamenListCreateView.as_view(), name='catalogo-list-create'),
    path('<int:pk>/', CatalogoExamenDetailView.as_view(), name='catalogo-detail'),
    path('examenes/', ExamenListCreateView.as_view(), name='examen-list-create'),
    path('examenes/<int:pk>/', ExamenDetailView.as_view(), name='examen-detail'),
]
