from django.contrib import admin

from .models import CIE10, CIE11, MapeoCIE


@admin.register(CIE10)
class CIE10Admin(admin.ModelAdmin):
    list_display = ["codigo", "descripcion", "capitulo", "activo"]
    search_fields = ["codigo", "descripcion"]


@admin.register(CIE11)
class CIE11Admin(admin.ModelAdmin):
    list_display = ["codigo", "titulo", "nivel", "padre", "requiere_subgrupo", "activo"]
    list_filter = ["nivel", "activo", "requiere_subgrupo"]
    search_fields = ["codigo", "titulo"]


@admin.register(MapeoCIE)
class MapeoCIEAdmin(admin.ModelAdmin):
    list_display = ["cie10", "cie11", "tipo"]
    search_fields = ["cie10__codigo", "cie11__codigo"]