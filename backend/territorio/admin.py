from django.contrib import admin

from .models import ASIC, DivisionTerritorial


@admin.register(DivisionTerritorial)
class DivisionTerritorialAdmin(admin.ModelAdmin):
    list_display = ["nombre", "nivel", "codigo", "padre", "activo"]
    list_filter = ["nivel", "activo"]
    search_fields = ["nombre", "codigo"]
    autocomplete_fields = ["padre"]
    ordering = ["nivel", "nombre"]


@admin.register(ASIC)
class AsicAdmin(admin.ModelAdmin):
    list_display = ["codigo", "nombre", "parroquia", "responsable", "telefono", "establecimientos_adscritos", "activo"]
    list_filter = ["activo"]
    search_fields = ["codigo", "nombre", "responsable", "telefono"]
    autocomplete_fields = ["parroquia"]