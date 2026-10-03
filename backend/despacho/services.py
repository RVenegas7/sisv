"""Cruce entre los talonarios despachados y los certificados cargados en la BD.

La serie del talonario es el consecutivo que va dentro del «Nº de certificado»
(`registro_numero`). Se extrae el bloque de dígitos finales para poder comparar:
`NC-2026-000123` → `123`, `DEF-2026-000045` → `45`, `LEG-CERT-12345` → `12345`.

El centro se resuelve por el árbol de organizaciones: un talonario entregado a una
organización cubre también sus descendientes (una regional entrega a sus centros).
"""

import re

from despacho.models import NovedadCertificado, Talonario
from registros.models import Defuncion, Nacimiento
from vigilancia.services import organizaciones_descendientes

_RE_DIGITOS_FINALES = re.compile(r"(\d+)\s*$")

MODELO_POR_TIPO = {
    Talonario.TIPO_NACIMIENTO: Nacimiento,
    Talonario.TIPO_DEFUNCION: Defuncion,
}


def numero_de_registro(registro_numero):
    """Consecutivo final del Nº de certificado, o None si no tiene dígitos."""
    if not registro_numero:
        return None
    coincidencia = _RE_DIGITOS_FINALES.search(str(registro_numero).strip())
    return int(coincidencia.group(1)) if coincidencia else None


def _ids_organizaciones(centro):
    return [o.id for o in organizaciones_descendientes(centro)]


def persona_registro(modelo, registro):
    """Nombre y apellidos para identificar el certificado, y de quién son.

    En defunción son del fallecido. En nacimiento es del recién nacido; mientras el
    certificado cargado no traiga su nombre (los que importationó el legacy, anteriores
    al EV-25) se recurre al de la madre y así se dice en la etiqueta, porque un
    certificado identificado por el nombre de la madre parece de otra persona.
    """
    if modelo is Defuncion:
        return registro.fallecido_nombres or "", registro.fallecido_apellidos or "", "Fallecido"
    nombres = registro.nino_nombres or registro.madre_nombres or ""
    apellidos = registro.nino_apellidos or registro.madre_apellidos or ""
    etiqueta = "Recién nacido" if registro.nino_nombres else "Madre"
    return nombres, apellidos, etiqueta


def certificados_usados(talonario):
    """Certificados de la serie que ya están cargados, indexados por consecutivo.

    Devuelve `{numero: registro}`. Solo mira dentro del subárbol del centro y dentro
    del rango de la serie; el `registro_numero` que no termina en dígitos se ignora
    (no se puede ubicar en la serie, así que no se cuenta como usado ni como faltante
    — queda fuera del cálculo y el reporte lo advierte).
    """
    modelo = MODELO_POR_TIPO[talonario.tipo]
    ids = _ids_organizaciones(talonario.centro)
    qs = modelo.objects.filter(organizacion_id__in=ids).only(
        "id", "registro_numero", "organizacion_id"
    )
    usados = {}
    for registro in qs.iterator():
        numero = numero_de_registro(registro.registro_numero)
        if numero is not None and talonario.serie_desde <= numero <= talonario.serie_hasta:
            usados[numero] = registro
    return usados


def resumen_talonario(talonario, usados=None):
    """Estado del talonario: cuántos usados, dañados, devueltos, en tránsito y faltantes."""
    if usados is None:
        usados = certificados_usados(talonario)

    novedades = list(talonario.novedades.all())
    por_estado = {"DANADO": set(), "EN_TRANSITO": set(), "DEVUELTO": set()}
    for novedad in novedades:
        if novedad.estado in por_estado:
            por_estado[novedad.estado].add(novedad.numero)

    usados_numeros = set(usados)
    danados = por_estado["DANADO"]
    devueltos = por_estado["DEVUELTO"]
    en_transito = por_estado["EN_TRANSITO"]

    # Un certificado en tránsito no está ni usado ni disponible. El faltante
    # (entregado y sin justificar) es lo que queda tras descontar todo lo explicado.
    justificados_o_en_curso = usados_numeros | danados | devueltos | en_transito
    faltantes = sorted(set(range(talonario.serie_desde, talonario.serie_hasta + 1)) - justificados_o_en_curso)

    return {
        "cantidad": talonario.cantidad,
        "usados": len(usados_numeros),
        "danados": len(danados),
        "devueltos": len(devueltos),
        "en_transito": len(en_transito),
        "faltantes": faltantes,
        "faltantes_total": len(faltantes),
    }


def detalle_certificados(talonario, usados=None):
    """Una fila por certificado de la serie, con su estatus y su persona si está usado."""
    if usados is None:
        usados = certificados_usados(talonario)
    modelo = MODELO_POR_TIPO[talonario.tipo]
    novedades = {n.numero: n for n in talonario.novedades.all()}

    filas = []
    for numero in range(talonario.serie_desde, talonario.serie_hasta + 1):
        registro = usados.get(numero)
        novedad = novedades.get(numero)
        if registro is not None:
            nombres, apellidos, persona = persona_registro(modelo, registro)
            filas.append({
                "numero": numero,
                "estatus": "CARGADO",
                "nombres": nombres,
                "apellidos": apellidos,
                "persona": persona,
                "fecha": str(registro.fecha_evento),
                "registro_id": registro.id,
                "registro_numero": registro.registro_numero,
            })
        elif novedad is not None:
            filas.append({
                "numero": numero,
                "estatus": novedad.estado,
                "nombres": novedad.transitado_nombres,
                "apellidos": novedad.transitado_apellidos,
                "fecha": str(novedad.fecha_salio_centro or novedad.justificacion_fecha or ""),
                "justificacion_numero": novedad.justificacion_numero,
                "observaciones": novedad.observaciones,
            })
        else:
            filas.append({
                "numero": numero,
                "estatus": "SIN_ASIGNAR",
                "nombres": "",
                "apellidos": "",
                "fecha": "",
            })
    return filas
