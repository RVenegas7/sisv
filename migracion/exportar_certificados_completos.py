#!/usr/bin/env python3
"""Exporta los certificados legacy con **todas sus columnas**, separados por tipo.

Para la verificación física en la oficina: además de las columnas propias de la
tabla de SISV (``registros_nacimiento`` / ``registros_defuncion``), añade al
final el **número real del certificado** que el ETL no guardó:

* defunción  → ``CERTIFICADO."NUMEROMSDS"`` (+ ``"NUMEROPARTIDA"``, año);
* nacimiento → ``CERTNACIMIENTO."NROPLANILLA"`` y ``"CONSECUTIVO"``.

Motivo: el ``registro_numero`` de SISV es ``LEG-CERT-{ID}`` / ``LEG-RN-{ID}`` (la
clave interna de Oracle), no el número impreso (PENDIENTES §27.16).

Solo lectura. Escribe en ``auditoria/`` (ignorada por git) dos CSV con BOM y
separador ``;``:

* ``defunciones_certificados_<anio>_<fecha>.csv``
* ``nacimientos_certificados_<anio>_<fecha>.csv``

Uso:
    python migracion/exportar_certificados_completos.py --anio 2026
        [--criterio certificado|evento] [--directorio auditoria]

Sin ``--anio`` exporta **todo** el histórico (archivos grandes).
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

FECHA_COL = {"certificado": None, "evento": True}  # None = filtro por año del certificado


def exportar_defunciones(cur, anio, criterio, ruta):
    if criterio == "evento":
        filtro = 'EXTRACT(YEAR FROM t.fecha_evento) = %s' if anio else "TRUE"
    else:
        filtro = 'c."ANNOCERTIFICADO" = %s' if anio else "TRUE"
    sql = (
        'SELECT t.*, c."NUMEROMSDS" AS numero_certificado_real, '
        'c."NUMEROPARTIDA" AS numero_partida_real, c."ANNOCERTIFICADO" AS anio_certificado, '
        'o.nombre AS organizacion_nombre '
        'FROM registros_defuncion t '
        'LEFT JOIN sismai."CERTIFICADO" c ON '
        'c."ID" = CASE WHEN t.legacy_id ~ \'^[0-9]+$\' THEN t.legacy_id::bigint END '
        'LEFT JOIN seguridad_organizacion o ON o.id = t.organizacion_id '
        f'WHERE {filtro} '
        'ORDER BY t.fecha_evento, t.id'
    )
    cur.execute(sql, [anio] if anio else [])
    return escribir(cur, ruta)


def exportar_nacimientos(cur, anio, criterio, ruta):
    if criterio == "evento":
        filtro = 'EXTRACT(YEAR FROM t.fecha_evento) = %s' if anio else "TRUE"
    else:
        filtro = 'c."ANO_CERTIF" = %s' if anio else "TRUE"
    sql = (
        'SELECT t.*, c."NROPLANILLA" AS numero_planilla_real, c."CONSECUTIVO" AS consecutivo_real, '
        'c."ANO_CERTIF" AS anio_certificado, o.nombre AS organizacion_nombre '
        'FROM registros_nacimiento t '
        'LEFT JOIN sismai."NAC_RNACIDO" r ON '
        'r."ID" = CASE WHEN t.legacy_id ~ \'^[0-9]+$\' THEN t.legacy_id::bigint END '
        'LEFT JOIN sismai."CERTNACIMIENTO" c ON c."ID" = r."HCERTIFICADO" '
        'LEFT JOIN seguridad_organizacion o ON o.id = t.organizacion_id '
        f'WHERE {filtro} '
        'ORDER BY t.fecha_evento, t.id'
    )
    cur.execute(sql, [anio] if anio else [])
    return escribir(cur, ruta)


def escribir(cur, ruta):
    encabezado = [d[0] for d in cur.description]
    n = 0
    with ruta.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(encabezado)
        for fila in cur:
            w.writerow(fila)
            n += 1
    return n


def main():
    ap = argparse.ArgumentParser(description="Exporta certificados legacy con todas sus columnas.")
    ap.add_argument("--anio", type=int, default=None, help="Año; sin él exporta todo.")
    ap.add_argument("--criterio", choices=["certificado", "evento"], default="certificado",
                    help="Año del certificado (default) o del evento (fecha_evento).")
    ap.add_argument("--directorio", default="auditoria")
    args = ap.parse_args()

    destino = Path(args.directorio)
    destino.mkdir(parents=True, exist_ok=True)
    etiqueta = args.anio or "historico"
    hoy = datetime.date.today().isoformat()

    conn = psycopg.connect(**DB)
    with conn.cursor() as cur:
        ruta_def = destino / f"defunciones_certificados_{etiqueta}_{hoy}.csv"
        n_def = exportar_defunciones(cur, args.anio, args.criterio, ruta_def)
        ruta_nac = destino / f"nacimientos_certificados_{etiqueta}_{hoy}.csv"
        n_nac = exportar_nacimientos(cur, args.anio, args.criterio, ruta_nac)
    conn.close()

    print(f"Defunciones: {n_def} → {ruta_def}")
    print(f"Nacimientos: {n_nac} → {ruta_nac}")


if __name__ == "__main__":
    main()
