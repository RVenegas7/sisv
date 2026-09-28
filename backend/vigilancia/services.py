from datetime import date, timedelta

from .models import CAMPOS_COLUMNA, EventoENO, columna


def domingo_de(fecha):
    """El domingo que abre la semana epidemiológica que contiene a `fecha`."""
    return fecha - timedelta(days=(fecha.weekday() + 1) % 7)


def inicio_anio_epidemiologico(anio):
    """Primer día (domingo) de la semana 1 del año epidemiológico `anio`.

    El ancla es el **4 de enero** (no el 1): la semana 1 es la que contiene el 4 de enero, de
    modo que el año siempre arranca en domingo. Anclar en el 1 de enero daría otro número de
    semanas, porque el 1 cae a mitad de semana.
    """
    return domingo_de(date(anio, 1, 4))


def fin_anio_epidemiologico(anio):
    """Domingo de la última semana del año epidemiológico `anio` (53 en 2025, 52 en 2026)."""
    return inicio_anio_epidemiologico(anio + 1) - timedelta(days=7)


def semanas_en_anio(anio):
    """Cuántas semanas tiene el año epidemiológico `anio` (52 o 53)."""
    return (inicio_anio_epidemiologico(anio + 1) - inicio_anio_epidemiologico(anio)).days // 7


def rango_anio_epidemiologico(anio):
    """(desde, hasta) inclusive de todas las fechas del año epidemiológico `anio`.

    Contiguo y sin huecos: el rango de `anio` termina el sábado justo antes del domingo
    con que arranca `anio + 1`. Así una fecha pertenece a un único año epidemiológico y el
    filtro por año no deja registros fuera ni los duplica.
    """
    return inicio_anio_epidemiologico(anio), inicio_anio_epidemiologico(anio + 1) - timedelta(days=1)


def semana_epidemiologica(fecha):
    """(año, semana 1..53) de la semana epidemiológica venezolana.

    ⚠ **NO es ISO 8601.** La semana va de **domingo a sábado** y la semana **no se parte al
    cambiar de año**: pertenece al año ``Y`` si empieza en el rango de ``Y`` (desde
    ``inicio_anio_epidemiologico(Y)`` hasta antes del de ``Y+1``). Por eso **2025 tiene 53
    semanas y 2026 tiene 52** (las invertidas de la ISO): la semana del 29-12-2024 es la
    **1 de 2025**, la del 28-12-2025 es la **53 de 2025** (y el 1, 2 y 3 de enero de 2026
    pertenecen a ella), y la semana 1 de 2026 arranca el 04-01-2026.

    Verificado contra el propio legacy, que es la fuente de la verdad: `sismai."DOCUMENTO"`
    guarda `ANNO`/`PERIODO` y para 2026 llega a 37 periodos, consolidando el 37 el 21-22/09
    (la semana que cerró el sábado 19/09, que es la 37 y no la 38 ISO). La oficina reporta
    2026 "semanas 1 a 37" y envía los martes la semana ya cargada, que es exactamente esto.
    """
    if isinstance(fecha, str):
        fecha = date.fromisoformat(fecha)
    elif hasattr(fecha, "date"):
        fecha = fecha.date()
    domingo = domingo_de(fecha)
    anio = fecha.year
    while domingo < inicio_anio_epidemiologico(anio):
        anio -= 1
    while domingo >= inicio_anio_epidemiologico(anio + 1):
        anio += 1
    return anio, (domingo - inicio_anio_epidemiologico(anio)).days // 7 + 1


def organizaciones_descendientes(org, incluir_org=True):
    """Todos los nodos bajo `org` en el árbol de organizaciones (recursivo)."""
    resultado = []
    if org is None:
        return resultado
    if incluir_org:
        resultado.append(org)
    for hijo in org.hijos.filter(activo=True):
        resultado.extend(organizaciones_descendientes(hijo))
    return resultado


def _fila_suma(filas):
    """Suma de las 26 columnas de un conjunto de filas (mismo evento)."""
    suma = {columna(g, s): 0 for g, s in CAMPOS_COLUMNA}
    for f in filas:
        for g, s in CAMPOS_COLUMNA:
            suma[columna(g, s)] += getattr(f, columna(g, s)) or 0
    return suma


def sembrar_filas(consolidado, borrar_existentes=True):
    """Garantiza una fila por cada evento del formulario (EPI-12/EPI-14).

    - EPI-12 (MORBILIDAD): eventos con en_epi12=True.
    - EPI-14 (MORTALIDAD): eventos con en_epi14=True.

    Si el consolidado es de nivel superior (organización con dependientes),
    precarga la suma de los consolidados de sus organizaciones hijas en la misma
    semana/tipo; de lo contrario siembra filas en 0. Nunca modifica las fuentes.
    """
    if borrar_existentes:
        consolidado.filas.all().delete()

    eventos_qs = EventoENO.objects.filter(activo=True)
    if consolidado.tipo == "MORBILIDAD":
        eventos_qs = eventos_qs.filter(en_epi12=True)
    else:
        eventos_qs = eventos_qs.filter(en_epi14=True)
    eventos_qs = eventos_qs.order_by("orden_epi12", "orden_epi14")

    hijas_ids = [o.id for o in organizaciones_descendientes(consolidado.organizacion, incluir_org=False)]
    suma_por_evento = {}
    if hijas_ids:
        hijos = type(consolidado).objects.filter(
            organizacion_id__in=hijas_ids,
            anio=consolidado.anio,
            semana=consolidado.semana,
            tipo=consolidado.tipo,
        ).prefetch_related("filas__evento")
        for hijo in hijos:
            for fila in hijo.filas.all():
                suma_por_evento.setdefault(fila.evento_id, []).append(fila)

    creadas = 0
    for evento in eventos_qs:
        valores = {columna(g, s): 0 for g, s in CAMPOS_COLUMNA}
        if suma_por_evento:
            valores.update(_fila_suma(suma_por_evento.get(evento.id, [])))
        consolidado.filas.create(evento=evento, **valores)
        creadas += 1
    return creadas