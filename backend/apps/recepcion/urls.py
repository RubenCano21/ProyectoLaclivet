from django.urls import path
from .views import CobroListCreateView, CobroDetailView

urlpatterns = [
    path('cobros/', CobroListCreateView.as_view(), name='cobro-list-create'),
    path('cobros/<int:pk>/', CobroDetailView.as_view(), name='cobro-detail'),
]

