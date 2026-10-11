#!/usr/bin/env python3
"""Exporta a CSV los centros del legado para revisión de la oficina.

Sale del espejo en PostgreSQL (``sismai."ESTABLECIMIENTO"`` y
``sismai."ORG_GEOGRAFICA"``) y de las tablas de hechos de SISV
(``registros_*``). **Solo lectura**: no toca la BD de la app ni el espejo.

Genera dos archivos (UTF-8 con BOM, separador ``;``, para Excel):

1. ``centros_duplicados_<fecha>.csv`` — los establecimientos del **árbol Lara**
   cuyo ``NOMBRE`` exacto comparten **varios códigos distintos**. Una fila por
   ``(nombre, código)`` con su geografía (estado/municipio/parroquia/comunidad)
   y ``STATUS``, más la bandera ``en_registros_sisv``. Sirve para que la oficina
   decida cuál código corresponde a cada centro físico.

   ⚠ Los conteos de registros son **por nombre**, no por código: el ETL antiguo
   guardó el nombre del establecimiento y descartó el código
   (``importar_legacy_registros``), así que con los datos actuales no se pueden
   repartir entre las variantes de un mismo nombre.

2. ``centros_establecimientos_<fecha>.csv`` — **todos** los establecimientos
   del catálogo (21.148, de todo el país) con su geografía, ``STATUS`` y las
   banderas ``en_arbol_lara`` / ``en_registros_sisv``. El catálogo
   ``ESTABLECIMIENTO`` es **nacional**; SISMAI solo maneja datos de Lara, así
   que ``en_arbol_lara = no`` no significa error, solo que no es del alcance.

Uso:
    python migracion/exportar_centros_legacy.py [--directorio auditoria]
        [--fecha AAAA-MM-DD]

Sugerencia de lectura del ``STATUS`` (verificado por SQL):
    A → activo (casi todos ``FUNCIONAMIENTO='S'``),
    I → inactivo,
    B → no funciona (todos ``FUNCIONAMIENTO='N'``).
"""
import argparse
import csv
import datetime
import os
from pathlib import Path

import psycopg

DB = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": os.environ.get("PGPORT", "5436"),
    "dbname": os.environ.get("PGDATABASE", "sis_salud_db"),
    "user": os.environ.get("PGUSER", "sis_user"),
    "password": os.environ.get("PGPASSWORD", "sis_password"),
}

RAICES_LARA = [67754.0, 3441583108.0]  # DES LARA + DPS LARA
CATEGORIAS = {10: "pais", 20: "estado", 30: "municipio", 40: "parroquia", 50: "comunidad"}


def cargar_geografia(cur):
    """Mapa {NUM_REGION: (REGION_PRECEDENTE, COD_CATEGORIA, DES_REGION)}."""
    cur.execute(
        'SELECT "NUM_REGION", "REGION_PRECEDENTE", "COD_CATEGORIA", "DES_REGION" '
        'FROM sismai."ORG_GEOGRAFICA";'
    )
    return {int(n): (int(p) if p is not None else None, int(c) if c is not None else None, d or "")
            for n, p, c, d in cur.fetchall()}


def geografia_de(localidad, geo_map):
    """Sube por el árbol geográfico y devuelve estado/municipio/parroquia/comunidad."""
    out = {"pais": "", "estado": "", "municipio": "", "parroquia": "", "comunidad": ""}
    actual = int(localidad) if localidad is not None else None
    for _ in range(12):
        if actual is None or actual not in geo_map:
            break
        padre, categoria, nombre = geo_map[actual]
        clave = CATEGORIAS.get(categoria)
        if clave and not out[clave]:
            out[clave] = nombre.strip()
        actual = padre
    return out


def cargar_establecimientos(cur):
    cur.execute(
        'SELECT "ID", btrim("CODIGO"), "NOMBRE", "PADRE", "HLOCALIDAD", '
        'btrim("STATUS"), "FUNCIONAMIENTO" FROM sismai."ESTABLECIMIENTO";'
    )
    filas = []
    for i, cod, nombre, padre, loc, status, func in cur.fetchall():
        filas.append({
            "id": int(i) if i is not None else None,
            "codigo": cod or "",
            "nombre": (nombre or "").strip(),
            "padre": int(padre) if padre is not None else None,
            "localidad": int(loc) if loc is not None else None,
            "status": status or "",
            "funcionamiento": (func or "").strip(),
        })
    return filas


def arbol_lara(establecimientos):
    """IDs de los establecimientos colgando de las raíces de Lara."""
    hijos = {}
    for e in establecimientos:
        hijos.setdefault(e["padre"], []).append(e["id"])
    arbol, pila = set(), list(RAICES_LARA)
    while pila:
        actual = pila.pop()
        if actual in arbol or actual is None:
            continue
        arbol.add(actual)
        pila.extend(hijos.get(int(actual), []))
    return arbol


def conteos_registros(cur):
    """{(tabla, nombre_normalizado_bruto): n} por nombre de establecimiento."""
    out = {}
    for tabla in ("registros_nacimiento", "registros_defuncion", "registros_fichavigilancia"):
        cur.execute(f"SELECT btrim(establecimiento), count(*) FROM {tabla} "
                    "WHERE establecimiento <> '' GROUP BY 1;")
        for nombre, n in cur.fetchall():
            out[(tabla, nombre)] = n
    return out


def main():
    ap = argparse.ArgumentParser(description="Exporta centros del legado a CSV para la oficina.")
    ap.add_argument("--directorio", default="auditoria", help="Dónde escribir los CSV.")
    ap.add_argument("--fecha", default=datetime.date.today().isoformat(), help="Sufijo de fecha.")
    args = ap.parse_args()

    destino = Path(args.directorio)
    destino.mkdir(parents=True, exist_ok=True)

    conn = psycopg.connect(**DB)
    with conn.cursor() as cur:
        geo_map = cargar_geografia(cur)
        establecimientos = cargar_establecimientos(cur)
        conteos = conteos_registros(cur)
    conn.close()

    arbol = arbol_lara(establecimientos)
    nombres_en_registros = {nombre for (_, nombre) in conteos}

    # Geografía resuelta por establecimiento.
    for e in establecimientos:
        e["geo"] = geografia_de(e["localidad"], geo_map)
        e["en_lara"] = e["id"] in arbol
        e["nac"] = conteos.get(("registros_nacimiento", e["nombre"]), 0)
        e["def"] = conteos.get(("registros_defuncion", e["nombre"]), 0)
        e["ficha"] = conteos.get(("registros_fichavigilancia", e["nombre"]), 0)

    # --- Archivo 1: nombres duplicados dentro del árbol Lara (con registros) ---
    codigos_por_nombre = {}
    for e in establecimientos:
        if e["en_lara"]:
            codigos_por_nombre.setdefault(e["nombre"], set()).add(e["codigo"])
    nombres_dup = {n for n, cods in codigos_por_nombre.items() if len(cods) > 1}
    duplicados = sorted(
        (e for e in establecimientos if e["en_lara"] and e["nombre"] in nombres_dup),
        key=lambda e: (e["nombre"], e["codigo"]),
    )

    ruta_dup = destino / f"centros_duplicados_{args.fecha}.csv"
    with ruta_dup.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow([
            "nombre", "codigo", "estado", "municipio", "parroquia", "comunidad",
            "status", "funcionamiento", "centros_con_mismo_nombre", "en_registros_sisv",
            "nacimientos_por_nombre", "defunciones_por_nombre", "fichas_por_nombre",
        ])
        for e in duplicados:
            g = e["geo"]
            w.writerow([
                e["nombre"], e["codigo"], g["estado"], g["municipio"], g["parroquia"],
                g["comunidad"], e["status"], e["funcionamiento"],
                len(codigos_por_nombre[e["nombre"]]),
                "si" if e["nombre"] in nombres_en_registros else "no",
                e["nac"], e["def"], e["ficha"],
            ])

    # --- Archivo 2: catálogo completo de establecimientos ---
    ruta_todos = destino / f"centros_establecimientos_{args.fecha}.csv"
    with ruta_todos.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow([
            "codigo", "nombre", "estado", "municipio", "parroquia", "comunidad",
            "status", "funcionamiento", "en_arbol_lara", "en_registros_sisv",
            "nacimientos_por_nombre", "defunciones_por_nombre", "fichas_por_nombre",
        ])
        for e in sorted(establecimientos, key=lambda e: (not e["en_lara"], e["codigo"])):
            g = e["geo"]
            w.writerow([
                e["codigo"], e["nombre"], g["estado"], g["municipio"], g["parroquia"],
                g["comunidad"], e["status"], e["funcionamiento"],
                "si" if e["en_lara"] else "no",
                "si" if e["nombre"] in nombres_en_registros else "no",
                e["nac"], e["def"], e["ficha"],
            ])

    lara = [e for e in establecimientos if e["en_lara"]]
    sin_geo = [e for e in establecimientos if not e["geo"]["estado"]]
    print(f"Establecimientos totales: {len(establecimientos)} · árbol Lara: {len(lara)} · sin geografía: {len(sin_geo)}")
    print(f"Nombres duplicados en el árbol Lara: {len(nombres_dup)} ({len(duplicados)} centros) → {ruta_dup}")
    print(f"Catálogo completo: {len(establecimientos)} filas → {ruta_todos}")


if __name__ == "__main__":
    main()
