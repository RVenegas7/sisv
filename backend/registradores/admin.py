from django.contrib import admin

from registradores.models import DesignacionRegistrador, RegistradorCivil, RegistroCivil


@admin.register(RegistroCivil)
class RegistroCivilAdmin(admin.ModelAdmin):
    list_display = ("nombre", "organizacion", "estado", "municipio", "activo")
    list_filter = ("activo", "estado")
    search_fields = ("nombre", "municipio", "parroquia")
    raw_id_fields = ("organizacion",)


@admin.register(RegistradorCivil)
class RegistradorCivilAdmin(admin.ModelAdmin):
    list_display = ("cedula_completa", "nombre_completo", "telefono", "activo")
    list_filter = ("activo", "nacionalidad")
    search_fields = ("nombres", "apellidos", "cedula")


@admin.register(DesignacionRegistrador)
class DesignacionRegistradorAdmin(admin.ModelAdmin):
    list_display = ("registro_civil", "registrador", "cargo", "desde", "hasta", "vigente")
    list_filter = ("cargo", "registro_civil")
    search_fields = ("acta_nombramiento", "observaciones")
    date_hierarchy = "desde"
    raw_id_fields = ("registro_civil", "registrador", "creado_por")
