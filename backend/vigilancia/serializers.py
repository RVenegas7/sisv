from rest_framework import serializers

from seguridad.models import Organizacion

from .models import (
    CAMPOS_COLUMNA,
    AlertaEpidemia,
    ConsolidadoEpi15,
    ConsolidadoSemanal,
    EventoENO,
    FilaConsolidado,
    FilaEpi15,
    SituacionEspecial,
    columna,
)


class EventoENOSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventoENO
        fields = [
            "id", "codigo_evento", "nombre", "orden_epi12", "orden_epi14",
            "en_epi12", "en_epi14", "codigos_cie11", "codigos_cie10",
            "notificacion", "notificacion_label", "grupo", "grupo_label", "activo",
        ]

    notificacion_label = serializers.CharField(source="get_notificacion_display", read_only=True)
    grupo_label = serializers.CharField(source="get_grupo_display", read_only=True)


class FilaConsolidadoSerializer(serializers.ModelSerializer):
    columnas = serializers.SerializerMethodField()
    total_hombres = serializers.SerializerMethodField()
    total_mujeres = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    evento_detalle = serializers.SerializerMethodField()

    class Meta:
        model = FilaConsolidado
        fields = ["id", "evento", "evento_detalle", "columnas", "total_hombres", "total_mujeres", "total"]

    def get_columnas(self, obj):
        return {columna(g, s): _entero(getattr(obj, columna(g, s))) for g, s in CAMPOS_COLUMNA}

    def get_total_hombres(self, obj):
        return _entero(obj.total_hombres())

    def get_total_mujeres(self, obj):
        return _entero(obj.total_mujeres())

    def get_total(self, obj):
        return _entero(obj.total)

    def get_evento_detalle(self, obj):
        return {
            "id": obj.evento_id,
            "nombre": obj.evento.nombre,
            "orden_epi12": obj.evento.orden_epi12,
            "orden_epi14": obj.evento.orden_epi14,
            "codigos_cie11": obj.evento.codigos_cie11,
            "codigos_cie10": obj.evento.codigos_cie10,
            "notificacion": obj.evento.notificacion,
        }


def _entero(v):
    return v or 0


class FilaEpi15Serializer(serializers.ModelSerializer):
    evento_nombre = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = FilaEpi15
        fields = [
            "id", "legacy_id", "codigo_legacy", "nombre_legacy",
            "evento", "evento_nombre", "casosp", "casoss", "casosx", "total",
        ]

    def get_evento_nombre(self, obj):
        return obj.evento.nombre if obj.evento_id else (obj.nombre_legacy or "Sin evento")

    def get_total(self, obj):
        return _entero(obj.total)


class ConsolidadoEpi15Serializer(serializers.ModelSerializer):
    organizacion_nombre = serializers.CharField(source="organizacion.nombre", read_only=True)
    estado_label = serializers.CharField(source="get_estado_display", read_only=True)
    filas = FilaEpi15Serializer(many=True, read_only=True)

    class Meta:
        model = ConsolidadoEpi15
        fields = [
            "id", "organizacion", "organizacion_nombre", "anio", "semana",
            "estado", "estado_label", "origen", "legacy_tabla", "legacy_documento",
            "creado_en", "actualizado_en", "filas",
        ]


class ConsolidadoEpi15EscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsolidadoEpi15
        fields = ["estado", "origen"]


class SituacionEspecialSerializer(serializers.ModelSerializer):
    tipo_evento_label = serializers.CharField(source="get_tipo_evento_display", read_only=True)

    class Meta:
        model = SituacionEspecial
        fields = [
            "id", "tipo_evento", "tipo_evento_label", "comunidad", "casos", "muertes",
            "descripcion", "medidas_tomadas",
        ]


class AlertaEpidemiaSerializer(serializers.ModelSerializer):
    clase_label = serializers.CharField(source="get_clase_display", read_only=True)

    class Meta:
        model = AlertaEpidemia
        fields = [
            "id", "clase", "clase_label", "evento", "enfermedad", "casos", "muertes",
            "grave", "inusitado", "impacto_nacional", "fecha_inicio", "fecha_fin",
            "unidad_geografica", "unidad_sanitaria",
        ]


class FilaConsolidadoEscribeSerializer(serializers.ModelSerializer):
    """Crea/actualiza filas a partir de {'evento': id, 'columnas': {…}}."""

    columnas = serializers.DictField(write_only=True, required=False)
    evento = serializers.PrimaryKeyRelatedField(queryset=EventoENO.objects.all())

    class Meta:
        model = FilaConsolidado
        fields = ["id", "evento", "columnas"]

    def _aplicar_columnas(self, obj, columnas):
        columnas = dict(columnas or {})
        if columnas.get("edad_ignorada_m"):
            columnas["edad_ignorada_h"] = int(columnas.get("edad_ignorada_h") or 0) + int(columnas.pop("edad_ignorada_m"))
            columnas["edad_ignorada_m"] = 0
        for g, s in CAMPOS_COLUMNA:
            nombre = columna(g, s)
            valor = columnas.get(nombre)
            setattr(obj, nombre, max(0, int(valor or 0)))
        obj.save()

    def create(self, validated_data):
        columnas = validated_data.pop("columnas", None)
        obj = FilaConsolidado.objects.create(**validated_data)
        if columnas:
            self._aplicar_columnas(obj, columnas)
        return obj

    def update(self, instance, validated_data):
        columnas = validated_data.pop("columnas", None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if columnas is not None:
            self._aplicar_columnas(instance, columnas)
        else:
            instance.save()
        return instance


class ConsolidadoSemanalSerializer(serializers.ModelSerializer):
    organizacion = serializers.SerializerMethodField()
    organizacion_id = serializers.SerializerMethodField()
    organizacion_nombre = serializers.SerializerMethodField()
    organizacion_nivel = serializers.SerializerMethodField()
    creado_por_nombre = serializers.SerializerMethodField()
    tipo_label = serializers.CharField(source="get_tipo_display", read_only=True)
    estado_label = serializers.CharField(source="get_estado_display", read_only=True)
    origen_label = serializers.CharField(source="get_origen_display", read_only=True)
    filas = FilaConsolidadoSerializer(many=True, read_only=True)
    situaciones_especiales = SituacionEspecialSerializer(many=True, read_only=True)
    alertas_epidemias = AlertaEpidemiaSerializer(many=True, read_only=True)
    total_casos = serializers.SerializerMethodField()

    class Meta:
        model = ConsolidadoSemanal
        fields = [
            "id", "organizacion", "organizacion_id", "organizacion_nombre", "organizacion_nivel",
            "anio", "semana", "tipo", "tipo_label", "estado", "estado_label",
            "origen", "origen_label", "creado_por", "creado_por_nombre",
            "enviado_en", "creado_en", "actualizado_en", "filas",
            "situaciones_especiales", "alertas_epidemias", "total_casos",
        ]

    def get_organizacion(self, obj):
        return obj.organizacion_id

    def get_organizacion_id(self, obj):
        return obj.organizacion_id

    def get_organizacion_nombre(self, obj):
        return obj.organizacion.nombre if obj.organizacion_id else None

    def get_organizacion_nivel(self, obj):
        return obj.organizacion.nivel if obj.organizacion_id else None

    def get_creado_por_nombre(self, obj):
        if not obj.creado_por_id:
            return None
        u = obj.creado_por
        return u.get_full_name() or u.username

    def get_total_casos(self, obj):
        return sum(f.total for f in obj.filas.all().order_by("evento_id"))


class ConsolidadoSemanalEscribeSerializer(serializers.ModelSerializer):
    """Cabecera + sub-recursos opcionales: filas, situaciones y alertas."""

    filas = FilaConsolidadoEscribeSerializer(many=True, required=False)
    situaciones_especiales = SituacionEspecialSerializer(many=True, required=False)
    alertas_epidemias = AlertaEpidemiaSerializer(many=True, required=False)
    organizacion = serializers.PrimaryKeyRelatedField(
        queryset=Organizacion.objects.all(), required=False
    )

    class Meta:
        model = ConsolidadoSemanal
        fields = [
            "id", "organizacion", "anio", "semana", "tipo", "estado", "origen",
            "filas", "situaciones_especiales", "alertas_epidemias",
        ]

    def validate(self, attrs):
        anio = attrs.get("anio")
        semana = attrs.get("semana")
        if semana is not None and not (1 <= semana <= 53):
            raise serializers.ValidationError({"semana": "La semana debe estar entre 1 y 53."})
        return attrs