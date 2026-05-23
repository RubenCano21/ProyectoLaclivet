from django.urls import path
from .views import CatalogoExamenListCreateView, CatalogoExamenDetailView

urlpatterns = [
    path('', CatalogoExamenListCreateView.as_view(), name='catalogo-list-create'),
    path('<int:pk>/', CatalogoExamenDetailView.as_view(), name='catalogo-detail'),
]

