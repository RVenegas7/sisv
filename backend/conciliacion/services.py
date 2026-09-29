import re
import unicodedata

from .models import RESOLUCION_CHOICES

PREFIXOS_TOTAL = ("TOTAL",)
SUFIJOS_TOTAL = ("TOTAL DE",)


def normalizar_centro(nombre):
    """Clave de unión centro legacy ↔ organización.

    Se reutiliza **exactamente** la normalización del ETL
    (`importar_legacy_vigilancia.normalizar`): sin paréntesis, minúsculas, sin
    tildes y espacios colapsados. Si aquí se normalizara distinto, la conciliación
    mediría un error que ella misma inventaría.
    """
    from vigilancia.management.commands.importar_legacy_vigilancia import normalizar

    return normalizar(nombre)


def es_pseudo_total(nombre):
    """¿La fila del catálogo legacy es un total agregado y no una enfermedad?

    En `sismai."CODIFICADOR"` hay 125 filas `TOTAL ...` (de 400). La mayor,
    `1126717818` = "TOTAL DE PACIENTES ATENDIDOS (ATENCIÓN AMBULATORIA Y EMERGENCIA)",
    arrastra el **72,6 % de todos los casos transcritos**: sumarla como si fuera
    una enfermedad multiplica el total por 3,6.

    ⚠ "TOTAL DE PACIENTES HOSPITALIZADOS POR TODAS CAUSAS" (`1126717832`) sí está
    mapeada a propósito, al evento `ENO_total_pacientes_hospitalizados_por_todas`.
    No es un olvido: se conserva para poder separarla en el reporte.
    """
    texto = re.sub(r"\s+", " ", (nombre or "")).strip().upper()
    if not texto:
        return False
    if any(texto.startswith(p) for p in PREFIXOS_TOTAL):
        return True
    return any(s in texto for s in SUFIJOS_TOTAL)


def resolver_organizacion(nombre, org_por_nombre):
    """Organización destino de un establecimiento legacy, o `None` si no casa.

    Devuelve `None` cuando el nombre no está en el catálogo: es el caso que el ETL
    resuelve consolidados en *"Legacy regional (histórico)"*, que es justamente la
    pérdida de identidad de centro que la conciliación debe hacer visible.
    """
    clave = normalizar_centro(nombre)
    return org_por_nombre.get(clave) if clave else None


def clasificar(crudo_h, crudo_m, sisv_h, sisv_m, sin_org, tiene_evento, es_pseudo=False):
    """Devuelve `(estado, resolucion)` de una fila de conciliación.

    El orden importa: una enfermedad sin equivalente ENO **nunca** podría cuadrar
    contra SISV, así que se marca antes de comparar números. Y una fila de total
    se marca como excluida por diseño para que no se lea como una pérdida.
    """
    vacio_crudo = not crudo_h and not crudo_m
    vacio_sisv = not sisv_h and not sisv_m

    if vacio_crudo and vacio_sisv:
        return "CUADRA", "CENTRO_SIN_ORG" if sin_org else "CONCILIADO"
    if not tiene_evento and es_pseudo:
        return "EXCLUIDO_EN_ETL", "PSEUDO_TOTAL_EXCLUIDO"
    if not tiene_evento:
        return "SOLO_CRUDO", "EVENTO_SIN_EQUIVALENTE"
    if vacio_crudo:
        return "SOLO_SISV", "SIN_FUENTE_EN_CRUDO"
    if vacio_sisv:
        return "SOLO_CRUDO", "CENTRO_SIN_ORG" if sin_org else "CONCILIADO"
    if (crudo_h, crudo_m) == (sisv_h, sisv_m):
        return "CUADRA", "CENTRO_SIN_ORG" if sin_org else "CONCILIADO"
    return "DIFERENCIA", "CENTRO_SIN_ORG" if sin_org else "CONCILIADO"


CODIGOS_RESOLUCION = {c for c, _ in RESOLUCION_CHOICES}
