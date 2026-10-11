from rest_framework import serializers

from .models import Defuncion, FichaVigilancia, Nacimiento
from .services import validar_seleccion_cie


def _validar_cie(attrs, partial, instance=None):
    if partial and not ({"version_cie", "cie10", "cie11", "fecha_evento"} & set(attrs)):
        return
    errores = validar_seleccion_cie(
        attrs.get("version_cie", "CIE11"),
        attrs.get("cie10"),
        attrs.get("cie11"),
        attrs.get("fecha_evento") or getattr(instance, "fecha_evento", None),
    )
    if errores:
        raise serializers.ValidationError(errores)


class _VaciosANullMixin:
    """El formulario envía "" en los campos numéricos/de fecha que deja en blanco.

    DRF rechaza "" en IntegerField/DateField aunque el modelo acepte nulos, así que
    esos vacíos se convierten a None antes de validar. Solo se tocan los campos que
    declaran `allow_null`, para no enmascarar los obligatorios.
    """

    _VACIO_A_NULL = (
        serializers.IntegerField,
        serializers.DecimalField,
        serializers.FloatField,
        serializers.DateField,
        serializers.DateTimeField,
        serializers.TimeField,
        serializers.DurationField,
    )

    def to_internal_value(self, data):
        if isinstance(data, dict) and not hasattr(data, "getlist"):
            limpio = dict(data)
            for nombre, campo in self.fields.items():
                if (
                    campo.allow_null
                    and isinstance(campo, self._VACIO_A_NULL)
                    and limpio.get(nombre) == ""
                ):
                    limpio[nombre] = None
            data = limpio
        return super().to_internal_value(data)


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

    def get_cie11_sugerido_detalle(self, obj):
        if not obj.cie11_sugerido_id:
            return None
        return {
            "id": obj.cie11_sugerido_id,
            "codigo": obj.cie11_sugerido.codigo,
            "titulo": obj.cie11_sugerido.titulo,
            "nivel": obj.cie11_sugerido.nivel,
            "nivel_label": obj.cie11_sugerido.get_nivel_display(),
        }

    def get_sugerencia_origen_label(self, obj):
        return obj.get_sugerencia_origen_display() if obj.sugerencia_origen else ""

    def get_codificado_por_nombre(self, obj):
        if not obj.codificado_por_id:
            return None
        usuario = obj.codificado_por
        return usuario.get_full_name() or usuario.get_username()


class _OrganizacionMixin:
    def get_organizacion(self, obj):
        return obj.organizacion_id

    def get_organizacion_id(self, obj):
        return obj.organizacion_id

    def get_organizacion_nombre(self, obj):
        return obj.organizacion.nombre if obj.organizacion_id else None

    def get_organizacion_nivel(self, obj):
        return obj.organizacion.nivel if obj.organizacion_id else None


def _ubicacion_nombres(ubicacion):
    """Los cuatro niveles del territorio de residencia con su nombre y su código.

    El frontend precarga la cascada por nombre (`SelectTerritorial` busca por `nombre`),
    así que los ids solos no alcanzan para devolver el formulario a su estado.
    """
    return {
        nivel: ({"id": nodo.id, "nombre": nodo.nombre, "codigo": nodo.codigo} if nodo else None)
        for nivel, nodo in ubicacion.items()
    }


class NacimientoSerializer(_VaciosANullMixin, _CIEDetalleMixin, _OrganizacionMixin, serializers.ModelSerializer):
    cie10_detalle = serializers.SerializerMethodField()
    cie11_detalle = serializers.SerializerMethodField()
    cie11_sugerido_detalle = serializers.SerializerMethodField()
    organizacion = serializers.SerializerMethodField()
    organizacion_id = serializers.SerializerMethodField()
    organizacion_nombre = serializers.SerializerMethodField()
    organizacion_nivel = serializers.SerializerMethodField()
    sugerencia_origen_label = serializers.SerializerMethodField()
    codificado_por_nombre = serializers.SerializerMethodField()
    sexo_label = serializers.CharField(source="get_sexo_display", read_only=True)
    tipo_parto_label = serializers.CharField(source="get_tipo_parto_display", read_only=True)
    madre_residencia_territorio = serializers.SerializerMethodField()
    padre_residencia_territorio = serializers.SerializerMethodField()

    NIVELES_RESIDENCIA = {
        "madre_residencia_parroquia": "PARROQUIA",
        "madre_residencia_comunidad": "COMUNIDAD",
        "padre_residencia_parroquia": "PARROQUIA",
        "padre_residencia_comunidad": "COMUNIDAD",
    }

    class Meta:
        model = Nacimiento
        fields = [
            "id", "registro_numero", "lote_id", "fecha_evento", "hora_nacimiento",
            "sexo", "sexo_label", "peso_gramos", "talla_cm", "edad_gestacional_semanas",
            "tipo_parto", "tipo_parto_label", "tipo_embarazo", "numero_gemelar",
            "persona_atendio_parto", "nombre_persona_atendio",
            "sitio_nacimiento", "establecimiento", "estado", "municipio", "parroquia",
            "nacido_vivo", "apgar_1m", "apgar_5m",
            "nino_nombres", "nino_apellidos", "numero_historia_clinica",
            "madre_nombres", "madre_apellidos", "madre_cedula", "madre_edad", "madre_ocupacion",
            "madre_estado_civil",
            "madre_nacionalidad", "madre_pasaporte", "madre_residencia", "madre_residencia_pais",
            "madre_residencia_direccion", "madre_residencia_parroquia", "madre_residencia_comunidad",
            "madre_residencia_territorio",
            "padre_nombres", "padre_apellidos", "padre_cedula", "padre_ocupacion", "padre_nacionalidad",
            "padre_pasaporte", "padre_residencia", "padre_residencia_pais",
            "padre_residencia_direccion", "padre_residencia_parroquia", "padre_residencia_comunidad",
            "padre_residencia_territorio",
            "libro", "folio", "acta",
            "fecha_registro", "registro_civil_nombre", "registrador_civil_nombres", "registrador_civil_cedula",
            "fecha_emision", "numero_planilla", "tipo_numero_certificado",
            "certificador_nombres", "certificador_cedula", "certificador_matricula_mpps",
            "director_establecimiento",
            "version_cie", "cie10", "cie11", "cie10_detalle", "cie11_detalle", "creado_en",
            "cie10_legacy", "codificacion_pendiente", "cie11_sugerido", "cie11_sugerido_detalle",
            "sugerencia_codigo", "sugerencia_titulo", "sugerencia_origen",
            "sugerencia_origen_label", "sugerencia_en",
            "codificado_por", "codificado_por_nombre", "codificado_en",
            "organizacion", "organizacion_id", "organizacion_nombre", "organizacion_nivel",
        ]

    def get_madre_residencia_territorio(self, obj):
        return _ubicacion_nombres(obj.residencia_ubicacion("madre"))

    def get_padre_residencia_territorio(self, obj):
        return _ubicacion_nombres(obj.residencia_ubicacion("padre"))

    def validate(self, attrs):
        _validar_cie(attrs, getattr(self, "partial", False), getattr(self, "instance", None))
        errores = {}
        for campo, nivel in self.NIVELES_RESIDENCIA.items():
            nodo = attrs.get(campo) or (
                getattr(self, "instance", None) and getattr(self.instance, campo)
            )
            if nodo is not None and nodo.nivel != nivel:
                etiqueta = "una parroquia" if nivel == "PARROQUIA" else "una comunidad"
                errores[campo] = f"La residencia habitual se registra con {etiqueta} del territorio."
        if errores:
            raise serializers.ValidationError(errores)
        return attrs


class DefuncionSerializer(_VaciosANullMixin, _CIEDetalleMixin, _OrganizacionMixin, serializers.ModelSerializer):
    cie10_detalle = serializers.SerializerMethodField()
    cie11_detalle = serializers.SerializerMethodField()
    cie11_sugerido_detalle = serializers.SerializerMethodField()
    organizacion = serializers.SerializerMethodField()
    organizacion_id = serializers.SerializerMethodField()
    organizacion_nombre = serializers.SerializerMethodField()
    organizacion_nivel = serializers.SerializerMethodField()
    sugerencia_origen_label = serializers.SerializerMethodField()
    codificado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Defuncion
        fields = [
            "id", "registro_numero", "lote_id", "fecha_evento", "hora_defuncion",
            "fallecido_nombres", "fallecido_apellidos", "fallecido_cedula", "sexo",
            "fecha_nacimiento", "lugar_defuncion", "establecimiento", "estado", "municipio", "parroquia",
            "causa_directa", "embarazo_o_puerperio", "autopsia", "embalsamado",
            "certificador_nombres", "certificador_cedula",
            "nacionalidad", "segundo_apellido", "segundo_nombre", "edad_ignorada",
            "lugar_nacimiento", "nacimiento_exterior", "estado_civil", "profesion",
            "ocupacion_lugar_trabajo", "sabe_leer_escribir", "residencia_habitual", "asistencia_medica",
            "es_muerte_fetal", "peso_nacer_gramos", "edad_gestacional_semanas", "tipo_embarazo", "tipo_parto",
            "asistencia_parto", "madre_apellidos", "madre_nombres", "madre_cedula",
            "madre_numero_gestas", "madre_fecha_ultima_gesta", "madre_embarazada", "madre_puerperio",
            "manera_de_morir", "fecha_hecho_violento", "hora_hecho_violento", "descripcion_hecho_violento",
            "causa_antecedentes", "otros_estados_patologicos",
            "diagnostico_examen_cadaver", "diagnostico_examen_laboratorio", "diagnostico_historia_clinica",
            "diagnostico_interrogatorio_familiar", "cirugia", "fecha_ultima_cirugia", "descripcion_cirugia",
            "intervalo_enf_muerte", "correo_contacto", "matricula_mpps",
            "registro_civil_nombre", "folio_defuncion", "numero_acta_defuncion", "fecha_registro",
            "declarante_nombres", "declarante_cedula", "registrador_civil_nombres", "registrador_civil_cedula",
            "gaceta", "resolucion",
            "etnia", "edad", "edad_unidad", "nacimiento_entidad", "nacimiento_pais",
            "sitio_ocurrencia", "area_ocurrencia", "codigo_comunidad", "ubicacion_geografica",
            "partida_tomo", "partida_folio", "partida_libro", "partida_acta",
            "fertil_numero_gestas", "fertil_fecha_ultima_gesta", "fertil_estaba_embarazada",
            "fertil_puerperio", "fertil_contribuyo_muerte", "fertil_nacidos_vivos",
            "fertil_nacidos_fallecidos", "fertil_muertes_fetales", "fertil_abortos",
            "causa_descrita_medico", "causa_aplicando_reglas", "causa_primera_parte",
            "causa_segunda_parte", "diagnostico_otro", "direccion_medico", "telefono_medico",
            "cargo_medico", "tipo_certificacion",
            "destino_cadaver", "numero_permiso",
            "registro_civil_entidad", "padre_fallecido_nombres", "padre_fallecido_cedula",
            "declarante_nacionalidad", "registrador_civil_nacionalidad",
            "version_cie", "cie10", "cie11", "cie10_detalle", "cie11_detalle", "creado_en",
            "cie10_legacy", "codificacion_pendiente", "cie11_sugerido", "cie11_sugerido_detalle",
            "sugerencia_codigo", "sugerencia_titulo", "sugerencia_origen",
            "sugerencia_origen_label", "sugerencia_en",
            "codificado_por", "codificado_por_nombre", "codificado_en",
            "organizacion", "organizacion_id", "organizacion_nombre", "organizacion_nivel",
        ]

    def validate(self, attrs):
        _validar_cie(attrs, getattr(self, "partial", False), getattr(self, "instance", None))
        return attrs


class FichaVigilanciaSerializer(_VaciosANullMixin, _CIEDetalleMixin, _OrganizacionMixin, serializers.ModelSerializer):
    cie10_detalle = serializers.SerializerMethodField()
    cie11_detalle = serializers.SerializerMethodField()
    cie11_sugerido_detalle = serializers.SerializerMethodField()
    organizacion = serializers.SerializerMethodField()
    organizacion_id = serializers.SerializerMethodField()
    organizacion_nombre = serializers.SerializerMethodField()
    organizacion_nivel = serializers.SerializerMethodField()
    sugerencia_origen_label = serializers.SerializerMethodField()
    codificado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = FichaVigilancia
        fields = [
            "id", "codigo_notificacion", "nombre_evento", "fecha_notificacion",
            "fecha_evento", "fecha_inicio_sintomas", "clasificacion",
            "establecimiento", "estado", "municipio", "parroquia",
            "paciente_nombres", "paciente_apellidos", "paciente_cedula", "sexo", "edad",
            "sintomas", "nota",
            "version_cie", "cie10", "cie11", "cie10_detalle", "cie11_detalle", "creado_en",
            "cie10_legacy", "codificacion_pendiente", "cie11_sugerido", "cie11_sugerido_detalle",
            "sugerencia_codigo", "sugerencia_titulo", "sugerencia_origen",
            "sugerencia_origen_label", "sugerencia_en",
            "codificado_por", "codificado_por_nombre", "codificado_en",
            "organizacion", "organizacion_id", "organizacion_nombre", "organizacion_nivel",
        ]

    def validate(self, attrs):
        _validar_cie(attrs, getattr(self, "partial", False), getattr(self, "instance", None))
        return attrs