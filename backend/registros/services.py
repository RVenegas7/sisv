import datetime
import logging
from collections import Counter

from django.conf import settings
from django.db import connection

from vigilancia.services import semana_epidemiologica

logger = logging.getLogger(__name__)

# El registro de investigación de muerte materna es `RENGLON_CASOSMM` enlazado a
# `CASOS_MMI` por ID de persona (`HCASOSMMI` → `CASOS_MMI."ID"`, 748 de 748 enlazan).
# El establecimiento sale por `CASOS_MMI."HDOCUMENTO"` → `DOCUMENTO."HORIGEN"`, igual
# que la conciliación neonatal, así que **el MM sí es atribuible a un centro**: las 748
# filas se reparten en 19 establecimientos, todas dentro del árbol Lara.
#
# ⚠ `HCASOSMMI` es el ID de la persona, no un contador: `SUM(HCASOSMMI)` da
# 658.439.440.845. Y la fecha de la muerte está en `CASOS_MMI."FECHAOCURRENCIA"`, no en
# `RENGLON_CASOSMM."PERIODOOCURRENCIA"`, que viene nula en las 749 filas.
SQL_MM_LEGADO = """
    SELECT c."FECHAOCURRENCIA"::date, d."HORIGEN"::bigint, count(DISTINCT r."HCASOSMMI")
    FROM sismai."RENGLON_CASOSMM" r
    JOIN sismai."CASOS_MMI" c ON c."ID" = r."HCASOSMMI"
    JOIN sismai."DOCUMENTO" d ON d."ID" = c."HDOCUMENTO"
    WHERE c."FECHAOCURRENCIA" >= %s AND c."FECHAOCURRENCIA" <= %s
    GROUP BY 1, 2
"""

# Detalle caso a caso de las muertes maternas del registro de investigación, para el
# anexo semanal. `DISTINCT ON (c."ID")` porque `RENGLON_CASOSMM` tiene una fila por
# (persona, causa) y aquí se quiere una por persona: es la misma deduplicación que
# `count(DISTINCT r."HCASOSMMI")` del conteo.
SQL_MM_DETALLE = """
    SELECT DISTINCT ON (c."ID")
           c."ID"::bigint, c."FECHAOCURRENCIA"::date, d."HORIGEN"::bigint,
           c."NACIONALIDAD", c."CEDULA", c."NOMBRE", c."APELLIDO",
           c."EDAD", c."UNIDAD_EDAD", c."HSEXO",
           c."HRESIDENCIA_PAIS", g."DES_REGION", g."NOMBRELARGO"
    FROM sismai."RENGLON_CASOSMM" r
    JOIN sismai."CASOS_MMI" c ON c."ID" = r."HCASOSMMI"
    JOIN sismai."DOCUMENTO" d ON d."ID" = c."HDOCUMENTO"
    LEFT JOIN sismai."ORG_GEOGRAFICA" g ON g."NUM_REGION" = c."HRESIDENCIA"
    WHERE c."FECHAOCURRENCIA" >= %s AND c."FECHAOCURRENCIA" <= %s
    ORDER BY c."ID"
"""

SQL_NOMBRES_ESTABLECIMIENTO = 'SELECT "ID"::bigint, "NOMBRE" FROM sismai."ESTABLECIMIENTO"'


def _resolver_organizaciones():
    """Mapa `nombre normalizado de establecimiento legacy` → `id de organización`.

    Reusa la normalización del ETL (`conciliacion.services.normalizar_centro`), que
    quita tildes, paréntesis y mayúsculas. Normalizar distinto aquí mediría un
    error que la propia función inventaría.
    """
    from conciliacion.services import normalizar_centro
    from seguridad.models import Organizacion

    with connection.cursor() as cur:
        cur.execute(SQL_NOMBRES_ESTABLECIMIENTO)
        nombres = {int(a): (b or "").strip() for a, b in cur.fetchall()}
    org_por_nombre = {
        normalizar_centro(n): i
        for n, i in Organizacion.objects.filter(activo=True).values_list("nombre", "id")
    }
    return {est_id: org_por_nombre.get(normalizar_centro(nombre))
            for est_id, nombre in nombres.items()}


def muerte_materna_por_organizacion(fecha_desde, fecha_hasta, organizaciones=None):
    """Muertes maternas del registro de investigación por organización y semana.

    Devuelve ``{org_id: {semana: cantidad}}`` o ``None`` si la fuente legacy no está
    disponible, para que el tablero caiga al conteo de certificados en vez de mostrar
    un cero que parece "no hubo muertes" cuando en realidad no se pudo leer.

    Los establecimientos legacy que no resuelven a organización propia se agrupan en
    `organizaciones=None` (clave `0`), que es el mismo agregado regional que usa la
    conciliación neonatal: no se pierden, se ven aparte.
    """
    if not fecha_desde or not fecha_hasta:
        return None
    try:
        with connection.cursor() as cur:
            cur.execute(SQL_MM_LEGADO, [fecha_desde, fecha_hasta])
            filas = cur.fetchall()
        org_de_establecimiento = _resolver_organizaciones()
    except Exception:  # noqa: BLE001 - la fuente legacy puede no existir (sqlite, espejo parcial)
        logger.warning("No se pudo leer sismai.RENGLON_CASOSMM: se usa el conteo de certificados.",
                       exc_info=True)
        return None

    if organizaciones is not None:
        organizaciones = set(organizaciones)

    por_org = {}
    for fecha, est_id, cantidad in filas:
        if not fecha or est_id is None:
            continue
        org_id = org_de_establecimiento.get(int(est_id)) or 0
        if organizaciones is not None and org_id not in organizaciones:
            continue
        semana = semana_epidemiologica(fecha)[1]
        por_org.setdefault(org_id, Counter())[semana] += int(cantidad or 0)
    return {org: {int(se): n for se, n in c.items()} for org, c in por_org.items()}


def muerte_materna_por_semana(fecha_desde, fecha_hasta, organizaciones=None):
    """Muertes maternas del registro de investigación, por semana epidemiológica.

    Suma todas las organizaciones. Devuelve `None` si la fuente legacy no está
    disponible (ver `muerte_materna_por_organizacion`).
    """
    por_org = muerte_materna_por_organizacion(fecha_desde, fecha_hasta, organizaciones)
    if por_org is None:
        return None
    total = Counter()
    for por_semana_org in por_org.values():
        total.update(por_semana_org)
    return {int(se): n for se, n in total.items()}


def muerte_materna_detalle(fecha_desde, fecha_hasta, organizaciones=None):
    """Casos de muerte materna del registro de investigación, uno por persona.

    Devuelve una lista de dicts con los campos que pide el anexo (identificación, edad,
    residencia y ocurrencia), ordenada por organización y fecha. ``None`` si la fuente
    legacy no está disponible, igual que `muerte_materna_por_organizacion`, para no
    confundir "no se pudo leer" con "no hubo casos".
    """
    if not fecha_desde or not fecha_hasta:
        return None
    try:
        with connection.cursor() as cur:
            cur.execute(SQL_MM_DETALLE, [fecha_desde, fecha_hasta])
            filas = cur.fetchall()
        org_de_establecimiento = _resolver_organizaciones()
    except Exception:  # noqa: BLE001 - la fuente legacy puede no existir (sqlite, espejo parcial)
        logger.warning("No se pudo leer el detalle de sismai.RENGLON_CASOSMM.", exc_info=True)
        return None

    if organizaciones is not None:
        organizaciones = set(organizaciones)

    detalle = []
    for (cid, fecha, est_id, nacion, cedula, nombres, apellidos, edad,
         unidad, sexo, pais, residencia, ubicacion) in filas:
        org_id = org_de_establecimiento.get(int(est_id)) if est_id is not None else None
        org_id = org_id or 0
        if organizaciones is not None and org_id not in organizaciones:
            continue
        detalle.append({
            "legacy_id": int(cid),
            "organizacion_id": org_id,
            "fecha": fecha.isoformat() if fecha else "",
            "nacionalidad": (nacion or "").strip(),
            "cedula": (cedula or "").strip(),
            "nombres": (nombres or "").strip(),
            "apellidos": (apellidos or "").strip(),
            "edad": int(edad) if edad not in (None, "") else None,
            "unidad_edad": (unidad or "").strip(),
            "sexo": int(sexo) if sexo not in (None, "") else None,
            "residencia": (residencia or "").strip(),
            "residencia_ubicacion": (ubicacion or "").strip(),
            "residencia_pais": int(pais) if pais not in (None, "") else None,
        })
    detalle.sort(key=lambda x: (x["organizacion_id"], x["fecha"]))
    return detalle


def version_cie_por_fecha(fecha_evento):
    if fecha_evento is None:
        return "CIE11"
    if isinstance(fecha_evento, str):
        fecha_evento = datetime.date.fromisoformat(fecha_evento)
    return "CIE10" if fecha_evento < settings.FECHA_CORTE_CIE11 else "CIE11"


def validar_seleccion_cie(version, cie10, cie11, fecha_evento):
    errores = {}
    version_esperada = version_cie_por_fecha(fecha_evento)
    if version != version_esperada:
        errores["version_cie"] = f"La fecha del evento exige la versión {version_esperada}."
    if version == "CIE10":
        if not cie10:
            errores["cie10"] = "Código CIE-10 obligatorio para eventos históricos."
        if cie11:
            errores["cie11"] = "No usar CIE-11 en eventos anteriores a la fecha de corte."
    if version == "CIE11":
        if not cie11:
            errores["cie11"] = "Código CIE-11 obligatorio para eventos actuales."
        elif getattr(cie11, "nivel", None) and cie11.requiere_subgrupo and cie11.nivel == 3:
            errores["cie11"] = "Esta categoría CIE-11 exige seleccionar un subgrupo obligatorio."
        if cie10 and version == "CIE11":
            errores["cie10"] = "Use el catálogo CIE-11 para este evento."
    return errores