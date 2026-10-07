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

def copy_sql(schema, table, delim, formato, sin_encabezado):
    """Construye la sentencia COPY.

    Dos rutas de origen, y cada una pide su propria opcion:

    * ``SYSTEM.SISV_EXPORTAR_CSV`` (§25): CSV con ``;``, comillas dobles y
      encabezado -> ``FORMAT csv`` + ``HEADER``.
    * ``migracion/espejo_csv.sh`` (§27): spool de SQL*Plus **sin encabezado**,
      separador ``\x01`` y los campos rellenos con espacios -> ``FORMAT text``
      (en CSV cualquier coma embebida en un texto parte la fila, y con ``\x01``
      eso deja de importar) y ``NULL ''`` para que un campo vacio sea NULL y no
      la cadena literal ``\\N``.
    """
    d = delim.replace("'", "''")
    if formato == "text":
        # HEADER solo existe en formato CSV: con text una cabecera real se
        # quita en el flujo (--quitar-encabezado), no en la sentencia.
        return (
            'COPY "{schema}"."{table}" FROM STDIN '
            "WITH (FORMAT text, DELIMITER '{d}', NULL '')"
        ).format(schema=schema, table=table, d=d)
    hdr = "false" if sin_encabezado else "true"
    return (
        'COPY "{schema}"."{table}" FROM STDIN '
        "WITH (FORMAT csv, DELIMITER '{d}', HEADER {h}, QUOTE '\"', NULL '')"
    ).format(schema=schema, table=table, d=d, h=hdr)


def stream(fh, delim, recortar, quitar_encabezado):
    """Itera los bloques de un CSV ya abierto en binario.

    * ``recortar``: quita el relleno que SQL*Plus pone a cada columna (alinea
      los numeros y rellena los textos) y convierte NULL (que sale como
      espacios) en campo vacio. Se recorta SOLO por los extremos de cada
      campo, para no tocar los espacios de dentro de los valores.
    * ``quitar_encabezado``: descarta la primera linea. Solo para FORMAT
      text cuando el CSV **si** trae cabecera: en text no existe la clausula
      HEADER. Ojo con no confundirlo con ``--sin-encabezado``, que dice que
      el archivo **no** tiene cabecera y por eso NO hay que borrar nada.
    * ``delim``: separador de campo. En la ruta de espejo es ``\x01``, byte
      que no aparece en los datos y por eso sirve para partir campos aunque
      el texto lleve comas o saltos de linea dentro.
    """
    pendiente = b""
    primera = True
    while True:
        bloque = fh.read(1 << 22)
        if not bloque:
            break
        pendiente += bloque
        lineas = pendiente.split(b"\n")
        pendiente = lineas.pop()
        for ln in lineas:
            if quitar_encabezado and primera:
                primera = False
                continue
            primera = False
            if recortar:
                ln = delim.join(c.strip() for c in ln.split(delim))
            yield ln + b"\n"
    if pendiente:
        if not (quitar_encabezado and primera):
            if recortar:
                pendiente = delim.join(c.strip() for c in pendiente.split(delim))
            yield pendiente + b"\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--directorio", required=True, help="Carpeta con los CSV")
    ap.add_argument("--esquema", action="append", default=None,
                    help="Filtra por esquema (repetible); por defecto todos")
    ap.add_argument("--ejecutar", action="store_true", help="Aplica (si no, dry-run)")
    ap.add_argument("--limite", type=int, default=None)
    ap.add_argument("--delimitador", default=";",
                    help="Separador del CSV (por defecto ';', que es el de "
                         "SYSTEM.SISV_EXPORTAR_CSV). La salida de "
                         "migracion/espejo_csv.sh trae coma.")
    ap.add_argument("--formato", choices=("csv", "text"), default="csv",
                    help="Formato del COPY. csv (por defecto) es el de "
                         "SYSTEM.SISV_EXPORTAR_CSV; text es el del spool de "
                         "SQL*Plus de migracion/espejo_csv.sh.")
    ap.add_argument("--sin-encabezado", action="store_true",
                    help="El CSV NO tiene fila de encabezado: la primera "
                         "linea ya es un dato (spool de SQL*Plus con "
                         "HEADING OFF). No se borra nada.")
    ap.add_argument("--quitar-encabezado", action="store_true",
                    help="El CSV si trae cabecera y el formato es text, que "
                         "no admite la clausula HEADER: se descarta la "
                         "primera linea durante la carga.")
    ap.add_argument("--recortar-campos", action="store_true",
                    help="Recorta los espacios de cada campo por los extremos "
                         "(relleno de SQL*Plus y NULL como espacios) sin tocar "
                         "el interior de los valores.")
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
        extra = f" formato={args.formato}"
        if args.delimitador != ";":
            extra += f" delimitador={args.delimitador!r}"
        if args.sin_encabezado:
            extra += " sin-encabezado"
        if args.quitar_encabezado:
            extra += " quitar-encabezado"
        if args.recortar_campos:
            extra += " recortar-campos"
        print(f"opciones:{extra or ' (por defecto)'}")
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
                            # Un COPY es una transaccion: si algo falla, el
                            # TRUNCATE de arriba se deshace y la tabla
                            # conserva sus datos.
                            with cur.copy(
                                copy_sql(schema, table, args.delimitador,
                                         args.formato, args.sin_encabezado)
                            ) as cp:
                                if args.recortar_campos or args.quitar_encabezado:
                                    for chunk in stream(
                                            fh, args.delimitador.encode(),
                                            args.recortar_campos,
                                            args.quitar_encabezado):
                                        cp.write(chunk)
                                else:
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
