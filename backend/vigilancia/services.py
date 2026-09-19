from datetime import date

from .models import CAMPOS_COLUMNA, EventoENO, columna


def semana_epidemiologica(fecha):
    """Semana epidemiológica ISO-8601 (criterio OMS): (año ISO, semana 1..53)."""
    if isinstance(fecha, str):
        fecha = date.fromisoformat(fecha)
    iso = fecha.isocalendar()
    return iso[0], iso[1]


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