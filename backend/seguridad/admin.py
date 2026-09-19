from django.contrib import admin

from .models import Organizacion, Perfil


class HijosInline(admin.TabularInline):
    model = Organizacion
    fk_name = "padre"
    extra = 0
    fields = ["codigo", "nombre", "nivel", "activo"]


@admin.register(Organizacion)
class OrganizacionAdmin(admin.ModelAdmin):
    list_display = ["codigo", "nombre", "nivel", "estado", "municipio", "activo"]
    list_filter = ["nivel", "estado", "activo"]
    search_fields = ["codigo", "nombre"]
    inlines = [HijosInline]


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    autocomplete_fields = ["user"]
    list_display = ["user", "rol", "organizacion"]
    list_filter = ["rol"]