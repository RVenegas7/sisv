from rest_framework import serializers

from .models import Defuncion, FichaVigilancia, Nacimiento
from .services import validar_seleccion_cie


def _validar_cie(attrs, partial):
    if partial and not ({"version_cie", "cie10", "cie11", "fecha_evento"} & set(attrs)):
        return
    errores = validar_seleccion_cie(
        attrs.get("version_cie", "CIE11"),
        attrs.get("cie10"),
        attrs.get("cie11"),
        attrs.get("fecha_evento"),
    )
    if errores:
        raise serializers.ValidationError(errores)


class _CIEDetalleMixin:
    def get_cie10_detalle(self, obj):
        if not obj.cie10:
            return None
        return {"codigo": obj.cie10.codigo, "descripcion": obj.cie10.descripcion}

    def get_cie11_detalle(self, obj):
        if not obj.cie11:
            return None
        return {
            "codigo": obj.cie11.codigo,
            "titulo": obj.cie11.titulo,
            "nivel": obj.cie11.nivel,
            "nivel_label": obj.cie11.get_nivel_display(),
            "requiere_subgrupo": obj.cie11.requiere_subgrupo,
        }


class _OrganizacionMixin:
    def get_organizacion(self, obj):
        return obj.organizacion_id

    def get_organizacion_id(self, obj):
        return obj.organizacion_id

    def get_organizacion_nombre(self, obj):
        return obj.organizacion.nombre if obj.organizacion_id else None

    def get_organizacion_nivel(self, obj):
        return obj.organizacion.nivel if obj.organizacion_id else None


class NacimientoSerializer(_CIEDetalleMixin, _OrganizacionMixin, serializers.ModelSerializer):
    cie10_detalle = serializers.SerializerMethodField()
    cie11_detalle = serializers.SerializerMethodField()
    organizacion = serializers.SerializerMethodField()
    organizacion_id = serializers.SerializerMethodField()
    organizacion_nombre = serializers.SerializerMethodField()
    organizacion_nivel = serializers.SerializerMethodField()
    sexo_label = serializers.CharField(source="get_sexo_display", read_only=True)
    tipo_parto_label = serializers.CharField(source="get_tipo_parto_display", read_only=True)

    class Meta:
        model = Nacimiento
        fields = [
            "id", "registro_numero", "lote_id", "fecha_evento", "hora_nacimiento",
            "sexo", "sexo_label", "peso_gramos", "talla_cm", "edad_gestacional_semanas",
            "tipo_parto", "tipo_parto_label", "tipo_embarazo", "numero_gemelar",
            "sitio_nacimiento", "establecimiento", "estado", "municipio", "parroquia",
            "nacido_vivo", "apgar_1m", "apgar_5m",
            "madre_nombres", "madre_apellidos", "madre_cedula", "madre_edad", "madre_estado_civil",
            "padre_nombres", "padre_apellidos", "padre_cedula",
            "libro", "folio", "acta",
            "version_cie", "cie10", "cie11", "cie10_detalle", "cie11_detalle", "creado_en",
            "organizacion", "organizacion_id", "organizacion_nombre", "organizacion_nivel",
        ]

    def validate(self, attrs):
        _validar_cie(attrs, getattr(self, "partial", False))
        return attrs


class DefuncionSerializer(_CIEDetalleMixin, _OrganizacionMixin, serializers.ModelSerializer):
    cie10_detalle = serializers.SerializerMethodField()
    cie11_detalle = serializers.SerializerMethodField()
    organizacion = serializers.SerializerMethodField()
    organizacion_id = serializers.SerializerMethodField()
    organizacion_nombre = serializers.SerializerMethodField()
    organizacion_nivel = serializers.SerializerMethodField()

    class Meta:
        model = Defuncion
        fields = [
            "id", "registro_numero", "lote_id", "fecha_evento", "hora_defuncion",
            "fallecido_nombres", "fallecido_apellidos", "fallecido_cedula", "sexo",
            "fecha_nacimiento", "lugar_defuncion", "establecimiento", "estado", "municipio", "parroquia",
            "causa_directa", "embarazo_o_puerperio", "autopsia", "embalsamado",
            "certificador_nombres", "certificador_cedula",
            "version_cie", "cie10", "cie11", "cie10_detalle", "cie11_detalle", "creado_en",
            "cie10_legacy", "codificacion_pendiente",
            "organizacion", "organizacion_id", "organizacion_nombre", "organizacion_nivel",
        ]

    def validate(self, attrs):
        _validar_cie(attrs, getattr(self, "partial", False))
        return attrs


class FichaVigilanciaSerializer(_CIEDetalleMixin, _OrganizacionMixin, serializers.ModelSerializer):
    cie10_detalle = serializers.SerializerMethodField()
    cie11_detalle = serializers.SerializerMethodField()
    organizacion = serializers.SerializerMethodField()
    organizacion_id = serializers.SerializerMethodField()
    organizacion_nombre = serializers.SerializerMethodField()
    organizacion_nivel = serializers.SerializerMethodField()

    class Meta:
        model = FichaVigilancia
        fields = [
            "id", "codigo_notificacion", "nombre_evento", "fecha_notificacion",
            "fecha_evento", "fecha_inicio_sintomas", "clasificacion",
            "establecimiento", "estado", "municipio", "parroquia",
            "paciente_nombres", "paciente_apellidos", "paciente_cedula", "sexo", "edad",
            "sintomas", "nota",
            "version_cie", "cie10", "cie11", "cie10_detalle", "cie11_detalle", "creado_en",
            "organizacion", "organizacion_id", "organizacion_nombre", "organizacion_nivel",
        ]

    def validate(self, attrs):
        _validar_cie(attrs, getattr(self, "partial", False))
        return attrs