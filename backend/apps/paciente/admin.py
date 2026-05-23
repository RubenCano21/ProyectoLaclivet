from django.contrib import admin
from .models import Especie


@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre']
    search_fields = ['nombre']

