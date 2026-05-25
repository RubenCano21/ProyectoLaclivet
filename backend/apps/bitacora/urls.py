from django.urls import path
from .views import BitacoraListCreateView, BitacoraDetailView

urlpatterns = [
    path('', BitacoraListCreateView.as_view(), name='bitacora-list-create'),
    path('<int:pk>/', BitacoraDetailView.as_view(), name='bitacora-detail'),
]

