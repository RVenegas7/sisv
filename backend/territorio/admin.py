from django.contrib import admin

from .models import DivisionTerritorial


@admin.register(DivisionTerritorial)
class DivisionTerritorialAdmin(admin.ModelAdmin):
    list_display = ["nombre", "nivel", "codigo", "padre", "activo"]
    list_filter = ["nivel", "activo"]
    search_fields = ["nombre", "codigo"]
    autocomplete_fields = ["padre"]
    ordering = ["nivel", "nombre"]