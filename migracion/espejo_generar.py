#!/usr/bin/env python3
"""Genera los artefactos del pipeline Oracle local -> CSV -> PostgreSQL.

Lee la lista de tablas directamente del espejo PostgreSQL (fuente de verdad de
que tablas hay que refrescar) y escribe en el directorio de salida:

  imp_<ESQUEMA>.par    parfile de importacion (imp clasico) por esquema
  export.sql           instala SISV_EXPORTAR_CSV y exporta las tablas a CSV
  counts_oracle.sql    SELECT COUNT(*) por tabla en Oracle
  counts_pg.sql        SELECT COUNT(*) por tabla en PostgreSQL

Uso:
    python migracion/espejo_generar.py --salida DIR [--esquema sismai ...]

Variables de entorno para PostgreSQL: PGHOST, PGPORT, PGDATABASE, PGUSER,
PGPASSWORD (mismos valores por defecto que ``cargar_espejo_pg.py``).
"""
import argparse
import os
import sys
from pathlib import Path

import psycopg

DB = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": os.environ.get("PGPORT", "5436"),
    "dbname": os.environ.get("PGDATABASE", "sis_salud_db"),
    "user": os.environ.get("PGUSER", "sis_user"),
    "password": os.environ.get("PGPASSWORD", "sis_password"),
}

# Esquemas del espejo que se refrescan desde el respaldo (el esquema legacy no
# viene en respaldos_sismai y se deja intacto).
ESQUEMAS_DEFECTO = ["sismai", "inbdlar1", "historico"]


def tablas_por_esquema(esquemas):
    res = {e: [] for e in esquemas}
    with psycopg.connect(**DB) as con, con.cursor() as cur:
        cur.execute(
            "SELECT table_schema, table_name FROM information_schema.tables "
            "WHERE table_schema = ANY(%s) AND table_type='BASE TABLE' "
            "ORDER BY 1, 2",
            (esquemas,),
        )
        for schema, table in cur.fetchall():
            res.setdefault(schema, []).append(table)
    return res


def parfile(esquema, tablas, ruta):
    upper = esquema.upper()
    lista = ",".join(f'"{t.upper()}"' for t in tablas)
    contenido = (
        f"USERID=system/oracle123@XE\n"
        f"FILE={upper}.dmp\n"
        f"FROMUSER={upper}\n"
        f"TOUSER={upper}\n"
        f"TABLES=({lista})\n"
        "IGNORE=Y\n"
        "INDEXES=N\n"
        "CONSTRAINTS=N\n"
        "GRANTS=N\n"
        "ROWS=Y\n"
        "BUFFER=104857600\n"
        f"LOG=imp_{upper}.log\n"
    )
    ruta.write_text(contenido)
    return len(tablas)


def driver_export(proc_sql, tablas, ruta):
    partes = [
        proc_sql.rstrip(),
        "ALTER SESSION SET NLS_NUMERIC_CHARACTERS='.,';",
        "CREATE OR REPLACE DIRECTORY CSV_DIR AS '/tmp/csv';",
    ]
    for schema, t in tablas:
        owner = schema.upper()
        archivo = f"{owner}__{t.upper()}.csv"
        partes.append(
            f"EXEC SYSTEM.SISV_EXPORTAR_CSV('{owner}','{t.upper()}',"
            f"'CSV_DIR','{archivo}');"
        )
    partes += ["prompt EXPORT_DONE", "exit"]
    ruta.write_text("\n".join(partes) + "\n")


def driver_conteos(tablas, ruta, pg):
    if pg:
        lineas = ["\\pset tuples_only on", "\\pset format unaligned"]
        for schema, t in tablas:
            lineas.append(
                f"SELECT '{schema}|{t}|' || count(*) FROM \"{schema}\".\"{t}\";"
            )
    else:
        lineas = [
            "set pagesize 0 feedback off heading off trimspool on linesize 300",
            "spool /tmp/dmp/counts_oracle.txt",
        ]
        for schema, t in tablas:
            owner = schema.upper()
            lineas.append(
                f"SELECT '{owner}|{t.upper()}|' || COUNT(*) "
                f'FROM "{owner}"."{t.upper()}";'
            )
        lineas.append("spool off")
        lineas.append("exit")
    ruta.write_text("\n".join(lineas) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", required=True, help="Directorio de artefactos")
    ap.add_argument("--esquema", action="append", default=None,
                    help="Esquema a refrescar (repetible)")
    args = ap.parse_args()

    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)

    esquemas = args.esquema or ESQUEMAS_DEFECTO
    por_esquema = tablas_por_esquema(esquemas)

    proc_sql = (Path(__file__).with_name("sisv_exportar_csv.sql")).read_text()

    tablas = []
    for esquema in esquemas:
        tablas.extend((esquema, t) for t in por_esquema.get(esquema, []))
        n = parfile(esquema, por_esquema.get(esquema, []),
                    salida / f"imp_{esquema.upper()}.par")
        print(f"  imp_{esquema.upper()}.par: {n} tablas")

    driver_export(proc_sql, tablas, salida / "export.sql")
    driver_conteos(tablas, salida / "counts_oracle.sql", pg=False)
    driver_conteos(tablas, salida / "counts_pg.sql", pg=True)
    print(f"Total: {len(tablas)} tablas -> {salida}")


if __name__ == "__main__":
    main()
