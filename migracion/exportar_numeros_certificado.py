#!/usr/bin/env python3
"""Exporta el cruce «número que muestra SISV ↔ número real del certificado».

Motivo (10/10/2026): en SISV el ``registro_numero`` de los registros legacy es
``LEG-CERT-{ID}`` / ``LEG-RN-{ID}``, donde ``{ID}`` es la **clave interna de
Oracle** (CERTIFICADO.ID / NAC_RNACIDO.ID), no el número del certificado. Por eso
los números no coinciden con los físicos. Los campos reales del número son:

* Defunción  → ``sismai.CERTIFICADO."NUMEROMSDS"`` (nunca vacío, ~único). El
  ``"NUMEROPARTIDA"`` es otro dato (partida) y viene vacío en el 95 %.
* Nacimiento → ``sismai.CERTNACIMIENTO."NROPLANILLA"`` (nº de la planilla
  impresa). El ``"CONSECUTIVO"`` es un consecutivo con prefijo del
  establecimiento/estado (``000013-NNNNNNN``).

Solo lectura. Escribe en ``auditoria/`` (ignorada por git) un único CSV con
ambos tipos, filtrable por año y/o tipo, para comparar contra los certificados
físicos.

Uso:
    python migracion/exportar_numeros_certificado.py [--anio 2026]
        [--tipo defuncion|nacimiento] [--directorio auditoria]
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

CATEGORIAS = {10: "pais", 20: "estado", 30: "municipio", 40: "parroquia", 50: "comunidad"}


def mapa_establecimientos(cur):
    cur.execute('SELECT "ID", "NOMBRE", "HLOCALIDAD" FROM sismai."ESTABLECIMIENTO";')
    return {int(i): (n or "", int(l) if l is not None else None) for i, n, l in cur.fetchall()}


def mapa_geografia(cur):
    cur.execute(
        'SELECT "NUM_REGION", "REGION_PRECEDENTE", "COD_CATEGORIA", "DES_REGION" '
        'FROM sismai."ORG_GEOGRAFICA";'
    )
    return {int(n): (int(p) if p is not None else None, int(c) if c is not None else None, d or "")
            for n, p, c, d in cur.fetchall()}


def estado_de(localidad, geo):
    actual = localidad
    for _ in range(12):
        if actual is None or actual not in geo:
            return ""
        padre, categoria, nombre = geo[actual]
        if categoria == 20:
            return nombre.strip()
        actual = padre
    return ""


def filas_defunciones(cur, anio, estab, geo):
    sql = ('SELECT c."ID", btrim(c."NUMEROMSDS"), btrim(c."NUMEROPARTIDA"), '
           'c."ANNOCERTIFICADO", c."FECHA_M", btrim(c."NOMBRE"), btrim(c."APELLIDO"), '
           'c."HESTABLECIMIENTO", c."HESTABLECIMIENTO_OCUR" '
           'FROM sismai."CERTIFICADO" c')
    params = []
    if anio:
        sql += ' WHERE c."ANNOCERTIFICADO" = %s'
        params.append(anio)
    sql += ' ORDER BY c."FECHA_M"'
    cur.execute(sql, params)
    for cid, nmsds, npart, annio, fecha, nombre, apellido, est, est_ocur in cur.fetchall():
        localidad = estab.get(int(est_ocur) if est_ocur is not None else None,
                              estab.get(int(est) if est is not None else -1, ("", None)))[1]
        yield {
            "tipo": "DEFUNCION",
            "legacy_id": str(int(cid)),
            "registro_numero_sisv": f"LEG-CERT-{int(cid)}",
            "numero_certificado": nmsds,
            "numero_planilla": "",
            "consecutivo": "",
            "numero_partida": npart,
            "anio": int(annio) if annio is not None else "",
            "fecha_evento": fecha.date().isoformat() if fecha else "",
            "nombre": f"{nombre} {apellido}".strip(),
            "establecimiento": estab.get(int(est) if est is not None else -1, ("", None))[0],
            "estado": estado_de(localidad, geo),
        }


def filas_nacimientos(cur, anio, estab, geo):
    sql = ('SELECT r."ID", c."ID", btrim(c."NROPLANILLA"), btrim(c."CONSECUTIVO"), '
           'c."ANO_CERTIF", r."FECHANACIMIENTO", c."FECHACERTIFICADO", btrim(r."NOMBRES"), '
           'c."HESTABLECIMIENTO" '
           'FROM sismai."NAC_RNACIDO" r JOIN sismai."CERTNACIMIENTO" c ON c."ID" = r."HCERTIFICADO"')
    params = []
    if anio:
        sql += ' WHERE c."ANO_CERTIF" = %s'
        params.append(anio)
    sql += ' ORDER BY r."FECHANACIMIENTO"'
    cur.execute(sql, params)
    for rn_id, cert_id, planilla, consec, annio, f_nac, f_cert, nombres, est in cur.fetchall():
        localidad = estab.get(int(est) if est is not None else -1, ("", None))[1]
        yield {
            "tipo": "NACIMIENTO",
            "legacy_id": str(int(rn_id)),
            "registro_numero_sisv": f"LEG-RN-{int(rn_id)}",
            "numero_certificado": "",
            "numero_planilla": planilla,
            "consecutivo": consec,
            "numero_partida": "",
            "anio": int(annio) if annio is not None else "",
            "fecha_evento": f_nac.date().isoformat() if f_nac else "",
            "nombre": nombres,
            "establecimiento": estab.get(int(est) if est is not None else -1, ("", None))[0],
            "estado": estado_de(localidad, geo),
        }


def main():
    ap = argparse.ArgumentParser(description="Cruce número SISV vs número real del certificado.")
    ap.add_argument("--anio", type=int, default=None, help="Año (ANNOCERTIFICADO/ANO_CERTIF).")
    ap.add_argument("--tipo", choices=["defuncion", "nacimiento"], default=None)
    ap.add_argument("--directorio", default="auditoria")
    args = ap.parse_args()

    destino = Path(args.directorio)
    destino.mkdir(parents=True, exist_ok=True)
    sufijo = f"{args.anio or 'todos'}" + (f"_{args.tipo}" if args.tipo else "")
    ruta = destino / f"numeros_certificado_{sufijo}_{datetime.date.today().isoformat()}.csv"

    conn = psycopg.connect(**DB)
    with conn.cursor() as cur:
        estab = mapa_establecimientos(cur)
        geo = mapa_geografia(cur)
        filas = []
        if args.tipo in (None, "defuncion"):
            filas += list(filas_defunciones(cur, args.anio, estab, geo))
        if args.tipo in (None, "nacimiento"):
            filas += list(filas_nacimientos(cur, args.anio, estab, geo))
    conn.close()

    with ruta.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, delimiter=";", fieldnames=[
            "tipo", "legacy_id", "registro_numero_sisv", "numero_certificado",
            "numero_planilla", "consecutivo", "numero_partida", "anio",
            "fecha_evento", "nombre", "establecimiento", "estado",
        ])
        w.writeheader()
        w.writerows(filas)

    defs = sum(1 for f in filas if f["tipo"] == "DEFUNCION")
    nacs = len(filas) - defs
    print(f"Defunciones: {defs} · Nacimientos: {nacs} → {ruta}")


if __name__ == "__main__":
    main()
