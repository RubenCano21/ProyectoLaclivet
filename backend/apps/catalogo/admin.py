from django.contrib import admin
from .models import CatalogoExamen


@admin.register(CatalogoExamen)
class CatalogoExamenAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'area', 'precio']
    search_fields = ['nombre', 'area']
    list_filter = ['area']

