from django.contrib import admin

from .models import (
    AlertaEpidemia,
    ConsolidadoEpi15,
    ConsolidadoSemanal,
    EventoENO,
    FilaConsolidado,
    FilaEpi15,
    SituacionEspecial,
)


@admin.register(EventoENO)
class EventoENOAdmin(admin.ModelAdmin):
    list_display = ["orden_epi12", "orden_epi14", "nombre", "en_epi12", "en_epi14", "notificacion", "grupo", "activo"]
    list_filter = ["en_epi12", "en_epi14", "notificacion", "grupo", "activo"]
    search_fields = ["nombre", "codigo_evento", "codigos_cie11", "codigos_cie10"]


class FilaConsolidadoInline(admin.TabularInline):
    model = FilaConsolidado
    extra = 0


class SituacionEspecialInline(admin.TabularInline):
    model = SituacionEspecial
    extra = 0


class AlertaEpidemiaInline(admin.TabularInline):
    model = AlertaEpidemia
    extra = 0


@admin.register(ConsolidadoSemanal)
class ConsolidadoSemanalAdmin(admin.ModelAdmin):
    list_display = ["anio", "semana", "tipo", "organizacion", "estado", "origen", "enviado_en"]
    list_filter = ["tipo", "estado", "origen", "anio", "organizacion"]
    search_fields = ["organizacion__nombre"]
    inlines = [FilaConsolidadoInline, SituacionEspecialInline, AlertaEpidemiaInline]


class FilaEpi15Inline(admin.TabularInline):
    model = FilaEpi15
    extra = 0


@admin.register(ConsolidadoEpi15)
class ConsolidadoEpi15Admin(admin.ModelAdmin):
    list_display = ["anio", "semana", "organizacion", "estado", "origen"]
    list_filter = ["estado", "origen", "anio", "organizacion"]
    search_fields = ["organizacion__nombre"]
    inlines = [FilaEpi15Inline]