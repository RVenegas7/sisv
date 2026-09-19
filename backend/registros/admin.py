from django.contrib import admin

from .models import Defuncion, FichaVigilancia, Nacimiento


@admin.register(Nacimiento)
class NacimientoAdmin(admin.ModelAdmin):
    list_display = ["registro_numero", "fecha_evento", "sexo", "madre_cedula", "version_cie"]
    list_filter = ["version_cie", "tipo_parto", "municipio"]
    search_fields = ["registro_numero", "madre_nombres", "madre_cedula"]


@admin.register(Defuncion)
class DefuncionAdmin(admin.ModelAdmin):
    list_display = ["registro_numero", "fecha_evento", "fallecido_nombres", "version_cie"]
    list_filter = ["version_cie", "municipio", "embarazo_o_puerperio"]
    search_fields = ["registro_numero", "fallecido_nombres", "fallecido_cedula"]


@admin.register(FichaVigilancia)
class FichaVigilanciaAdmin(admin.ModelAdmin):
    list_display = ["codigo_notificacion", "nombre_evento", "fecha_evento", "clasificacion", "version_cie"]
    list_filter = ["clasificacion", "version_cie", "municipio"]
    search_fields = ["codigo_notificacion", "nombre_evento", "paciente_nombres"]