#!/usr/bin/env python3
"""Carga en PostgreSQL el espejo legacy exportado a CSV desde Oracle.

Los CSV provienen de ``SYSTEM.SISV_EXPORTAR_CSV`` (separador ``;``, comillas
dobles, NULL como campo vacio sin comillas) y se nombran ``ESQUEMA__TABLA.csv``.

Uso:
    python migracion/cargar_espejo_pg.py --directorio DIR [--esquema sismai]
                                         [--ejecutar] [--limite N]

Sin ``--ejecutar`` solo informa (dry-run). Es idempotente: hace TRUNCATE + COPY
por tabla, cada tabla en su propia transaccion (si una falla, las demas siguen).
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

COPY_SQL = (
    'COPY "{schema}"."{table}" FROM STDIN '
    "WITH (FORMAT csv, DELIMITER ';', HEADER true, QUOTE '\"', NULL '')"
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--directorio", required=True, help="Carpeta con los CSV")
    ap.add_argument("--esquema", action="append", default=None,
                    help="Filtra por esquema (repetible); por defecto todos")
    ap.add_argument("--ejecutar", action="store_true", help="Aplica (si no, dry-run)")
    ap.add_argument("--limite", type=int, default=None)
    args = ap.parse_args()

    directorio = Path(args.directorio)
    if not directorio.is_dir():
        sys.exit(f"No existe el directorio {directorio}")

    csvs = sorted(directorio.glob("*__*.csv"))
    if args.esquema:
        wanted = {s.lower() for s in args.esquema}
        csvs = [c for c in csvs if c.name.split("__", 1)[0].lower() in wanted]
    if args.limite:
        csvs = csvs[: args.limite]

    print(f"{len(csvs)} CSV por cargar")
    if not args.ejecutar:
        for c in csvs:
            print(f"  dry-run {c.name}")
        return

    ok = err = 0
    with psycopg.connect(**DB) as con:
        for c in csvs:
            schema, table = c.stem.split("__", 1)
            schema = schema.lower()
            try:
                with con.transaction():
                    with con.cursor() as cur:
                        cur.execute(f'TRUNCATE TABLE "{schema}"."{table}"')
                        with open(c, "rb") as fh:
                            with cur.copy(
                                COPY_SQL.format(schema=schema, table=table)
                            ) as cp:
                                while True:
                                    chunk = fh.read(4 * 1024 * 1024)
                                    if not chunk:
                                        break
                                    cp.write(chunk)
                ok += 1
                print(f"  [{ok + err}/{len(csvs)}] {schema}.{table}", flush=True)
            except Exception as exc:  # noqa: BLE001
                err += 1
                print(f"  ERROR {schema}.{table}: {exc}", flush=True)

    print(f"Listo: {ok} cargadas, {err} con error")
    if err:
        sys.exit(1)


if __name__ == "__main__":
    main()
