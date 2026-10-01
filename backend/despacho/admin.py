from django.contrib import admin

from despacho.models import NovedadCertificado, Talonario


@admin.register(Talonario)
class TalonarioAdmin(admin.ModelAdmin):
    list_display = (
        "tipo", "centro", "serie_desde", "serie_hasta", "cantidad",
        "fecha_entrega", "responsable_recibe",
    )
    list_filter = ("tipo", "centro")
    search_fields = ("responsable_recibe", "responsable_entrega", "observaciones")
    date_hierarchy = "fecha_entrega"
    raw_id_fields = ("centro",)


@admin.register(NovedadCertificado)
class NovedadCertificadoAdmin(admin.ModelAdmin):
    list_display = (
        "talonario", "numero", "estado", "justificacion_numero", "fecha_salio_centro",
    )
    list_filter = ("estado",)
    search_fields = ("justificacion_numero", "transitado_nombres", "transitado_apellidos")
    raw_id_fields = ("talonario",)
