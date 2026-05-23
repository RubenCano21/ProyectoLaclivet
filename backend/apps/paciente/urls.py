from django.urls import path
from .views import EspecieListCreateView, EspecieDetailView

urlpatterns = [
    path('especies/', EspecieListCreateView.as_view(), name='especie-list-create'),
    path('especies/<int:pk>/', EspecieDetailView.as_view(), name='especie-detail'),
]

