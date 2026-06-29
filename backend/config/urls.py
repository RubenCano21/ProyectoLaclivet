from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from drf_yasg import openapi

# Configuracion Basica de LACLIVET
schema_view = get_schema_view(
    openapi.Info(
        title="LACLIVET API",
        default_version='v1',
        description="Documentacion de la API de LACLIVET",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/usuarios/', include('apps.usuarios.urls')),
    path('api/propietarios/', include('apps.propietario.urls')),
    path('api/catalogos/', include('apps.catalogo.urls')),
    path('api/medicos/', include('apps.medico.urls')),
    path('api/pacientes/', include('apps.paciente.urls')),
    path('api/recepcion/', include('apps.recepcion.urls')),
    path('api/bitacora/', include('apps.bitacora.urls')),
    path('api/muestras/', include('apps.muestra.urls')),
    path('api/bi/',       include('apps.bi.urls')),

    # --- RUTAS DE SWAGGER ---
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
