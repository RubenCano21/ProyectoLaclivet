from django.urls import path
from .views import (
    CatalogoExamenListCreateView, CatalogoExamenDetailView,
    ExamenListCreateView, ExamenDetailView,
    ParametroListCreateView, ParametroDetailView,
    ValorReferenciaListCreateView, ValorReferenciaDetailView,
)

urlpatterns = [
    path('', CatalogoExamenListCreateView.as_view(), name='catalogo-list-create'),
    path('<int:pk>/', CatalogoExamenDetailView.as_view(), name='catalogo-detail'),
    path('examenes/', ExamenListCreateView.as_view(), name='examen-list-create'),
    path('examenes/<int:pk>/', ExamenDetailView.as_view(), name='examen-detail'),
    path('parametros/', ParametroListCreateView.as_view(), name='parametro-list-create'),
    path('parametros/<int:pk>/', ParametroDetailView.as_view(), name='parametro-detail'),
    path('valores-referencia/', ValorReferenciaListCreateView.as_view(), name='valor-referencia-list-create'),
    path('valores-referencia/<int:pk>/', ValorReferenciaDetailView.as_view(), name='valor-referencia-detail'),
]
