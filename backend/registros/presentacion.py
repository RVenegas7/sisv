"""Armado del detalle legible de un certificado para la consulta por número.

La persona que codifica no debe ver el formulario de captura: necesita **toda la
información ya registrada**, agrupada y de solo lectura, para poder confirmar el código.
Aquí se traduce el registro ORM a bloques con su rótulo (`verbose_name` del modelo) y su
valor ya formateado (opciones, fechas, sí/no, relaciones). No hay lógica de captura ni
validación: solo presentación.
"""

import datetime

from django.db import models

# Campos internos que no aportan a la lectura clínica del certificado.
_OMITIR = {"legacy_tabla", "legacy_id", "creado_en", "sugerencia_json"}

_COMUNES = {
    "fecha_evento": "Certificado y evento",
    "organizacion": "Certificado y evento",
    "registro_numero": "Certificado y evento",
    "lote_id": "Certificado y evento",
    "version_cie": "Codificación CIE",
    "cie10": "Codificación CIE",
    "cie11": "Codificación CIE",
    "cie10_legacy": "Codificación CIE",
    "cie11_sugerido": "Codificación CIE",
    "codificacion_pendiente": "Codificación CIE",
    "sugerencia_codigo": "Codificación CIE",
    "sugerencia_titulo": "Codificación CIE",
    "sugerencia_origen": "Codificación CIE",
    "sugerencia_en": "Codificación CIE",
    "codificado_por": "Codificación CIE",
    "codificado_en": "Codificación CIE",
}

_GRUPOS = {
    "Defuncion": {
        **{c: "Certificado y evento" for c in (
            "hora_defuncion", "lugar_defuncion", "establecimiento", "estado", "municipio", "parroquia")},
        **{c: "Identificación del fallecido" for c in (
            "fallecido_nombres", "fallecido_apellidos", "fallecido_cedula", "sexo",
            "fecha_nacimiento", "edad", "edad_unidad", "edad_ignorada", "nacionalidad",
            "segundo_nombre", "segundo_apellido", "etnia", "estado_civil", "profesion",
            "ocupacion_lugar_trabajo", "sabe_leer_escribir", "residencia_habitual",
            "asistencia_medica", "lugar_nacimiento", "nacimiento_exterior",
            "nacimiento_entidad", "nacimiento_pais", "partida_tomo", "partida_folio",
            "partida_libro", "partida_acta")},
        **{c: "Sitio de ocurrencia" for c in (
            "sitio_ocurrencia", "area_ocurrencia", "codigo_comunidad", "ubicacion_geografica")},
        **{c: "Menor de un año / madre" for c in (
            "es_muerte_fetal", "peso_nacer_gramos", "edad_gestacional_semanas", "tipo_embarazo",
            "tipo_parto", "asistencia_parto", "madre_apellidos", "madre_nombres", "madre_cedula",
            "madre_numero_gestas", "madre_fecha_ultima_gesta", "madre_embarazada", "madre_puerperio")},
        **{c: "Mujeres en edad fértil" for c in (
            "fertil_numero_gestas", "fertil_fecha_ultima_gesta", "fertil_estaba_embarazada",
            "fertil_puerperio", "fertil_contribuyo_muerte", "fertil_nacidos_vivos",
            "fertil_nacidos_fallecidos", "fertil_muertes_fetales", "fertil_abortos")},
        **{c: "Muerte violenta" for c in (
            "manera_de_morir", "fecha_hecho_violento", "hora_hecho_violento",
            "descripcion_hecho_violento")},
        **{c: "Certificación médica" for c in (
            "causa_primera_parte", "causa_segunda_parte", "causa_antecedentes", "causa_directa",
            "causa_descrita_medico", "causa_aplicando_reglas", "otros_estados_patologicos",
            "intervalo_enf_muerte", "diagnostico_examen_cadaver", "diagnostico_examen_laboratorio",
            "diagnostico_historia_clinica", "diagnostico_interrogatorio_familiar", "diagnostico_otro",
            "cirugia", "fecha_ultima_cirugia", "descripcion_cirugia", "autopsia", "embalsamado",
            "embarazo_o_puerperio", "certificador_nombres", "certificador_cedula", "matricula_mpps",
            "cargo_medico", "tipo_certificacion", "correo_contacto", "direccion_medico",
            "telefono_medico", "destino_cadaver", "numero_permiso")},
        **{c: "Registro civil" for c in (
            "registro_civil_nombre", "registro_civil_entidad", "numero_acta_defuncion",
            "folio_defuncion", "fecha_registro", "gaceta", "resolucion", "declarante_nombres",
            "declarante_cedula", "declarante_nacionalidad", "registrador_civil_nombres",
            "registrador_civil_cedula", "registrador_civil_nacionalidad",
            "padre_fallecido_nombres", "padre_fallecido_cedula")},
    },
    "Nacimiento": {
        **{c: "Certificado y evento" for c in (
            "hora_nacimiento", "sitio_nacimiento", "establecimiento", "estado", "municipio",
            "parroquia", "fecha_emision", "numero_planilla", "tipo_numero_certificado")},
        **{c: "Recién nacido" for c in (
            "nino_nombres", "nino_apellidos", "numero_historia_clinica", "sexo", "peso_gramos",
            "talla_cm", "edad_gestacional_semanas", "tipo_parto", "tipo_embarazo", "numero_gemelar",
            "persona_atendio_parto", "nombre_persona_atendio",
            "nacido_vivo", "apgar_1m", "apgar_5m")},
        **{c: "Madre" for c in (
            "madre_nombres", "madre_apellidos", "madre_cedula", "madre_edad", "madre_ocupacion",
            "madre_estado_civil",
            "madre_nacionalidad", "madre_pasaporte", "madre_residencia", "madre_residencia_pais",
            "madre_residencia_direccion", "madre_residencia_parroquia", "madre_residencia_comunidad")},
        **{c: "Padre" for c in (
            "padre_nombres", "padre_apellidos", "padre_cedula", "padre_ocupacion", "padre_nacionalidad",
            "padre_pasaporte", "padre_residencia", "padre_residencia_pais",
            "padre_residencia_direccion", "padre_residencia_parroquia", "padre_residencia_comunidad")},
        **{c: "Registro civil" for c in (
            "libro", "folio", "acta", "fecha_registro", "registro_civil_nombre",
            "registrador_civil_nombres", "registrador_civil_cedula")},
        **{c: "Responsable" for c in (
            "certificador_nombres", "certificador_cedula", "certificador_matricula_mpps",
            "director_establecimiento")},
    },
    "FichaVigilancia": {
        **{c: "Notificación" for c in (
            "codigo_notificacion", "lote_id", "establecimiento", "estado", "municipio", "parroquia",
            "fecha_notificacion", "fecha_inicio_sintomas", "clasificacion", "nombre_evento")},
        **{c: "Paciente" for c in (
            "paciente_nombres", "paciente_apellidos", "paciente_cedula", "sexo", "edad")},
        **{c: "Clínica" for c in ("sintomas", "nota")},
    },
}

_ORDEN_GRUPOS = [
    "Certificado y evento", "Identificación del fallecido", "Sitio de ocurrencia",
    "Menor de un año / madre", "Mujeres en edad fértil", "Muerte violenta",
    "Certificación médica", "Registro civil",
    "Recién nacido", "Madre", "Padre",
    "Notificación", "Paciente", "Clínica",
    "Responsable", "Codificación CIE", "Otros datos",
]


def _etiqueta(field):
    return getattr(field, "verbose_name", None) or field.name.replace("_", " ").capitalize()


def _valor(registro, field):
    if field.choices:
        return getattr(registro, f"get_{field.name}_display")() or ""
    valor = getattr(registro, field.name, None)
    if isinstance(field, models.BooleanField):
        return "Sí" if valor else "No"
    if field.is_relation:
        return str(valor) if valor is not None else ""
    if isinstance(valor, (datetime.date, datetime.datetime)):
        return valor.isoformat()
    if valor is None:
        return ""
    return str(valor)


def detalle_certificado(registro):
    """Bloques `[{grupo, campos:[{campo, etiqueta, valor}]}]` con lo ya registrado."""
    modelo = type(registro).__name__
    grupos = dict(_COMUNES)
    grupos.update(_GRUPOS.get(modelo, {}))

    bloques = {}
    for field in registro._meta.get_fields():
        if not getattr(field, "concrete", False) or field.auto_created:
            continue
        if field.name in _OMITIR or field.name == "id":
            continue
        valor = _valor(registro, field)
        if valor == "":
            continue
        grupo = grupos.get(field.name, "Otros datos")
        bloques.setdefault(grupo, []).append({
            "campo": field.name,
            "etiqueta": _etiqueta(field),
            "valor": valor,
        })

    orden = {g: i for i, g in enumerate(_ORDEN_GRUPOS)}
    resultado = [{"grupo": g, "campos": campos} for g, campos in bloques.items()]
    resultado.sort(key=lambda b: orden.get(b["grupo"], len(_ORDEN_GRUPOS)))
    return resultado
