#!/usr/bin/env python3
"""Trae a la base local, de forma ADITIVA, los certificados de un dump de la oficina.

Este es el **script 2** del flujo semanal (ver ``PENDIENTES.md`` §31/§32): la
oficina refresca su PostgreSQL desde el Oracle vivo y produce un ``pg_dump``;
este script lo aplica en casa sin perder el trabajo de la aplicación.

Qué hace
--------
1. Se apoya en una base **temporal** con el dump de la oficina ya restaurado
   (``sis_salud_db_oficina``, la crea ``migracion/aplicar_dump_oficina.sh``).
2. Inserta en ``registros_defuncion`` y ``registros_nacimiento`` las filas que
   falten por **clave natural** ``registro_numero``. Nunca borra ni actualiza
   una fila existente, así que **conserva la codificación CIE** (``cie10_id``,
   ``cie11_id``, ``codificacion_pendiente``…) y cualquier edición local.

Reglas de atribución de centro
------------------------------
Los ``id`` de ``seguridad_organizacion`` **no coinciden** entre bases, así que
el centro se remapea por **nombre**, en este orden:

1. Si el ``establecimiento`` del propio certificado coincide **exactamente** con
   el nombre de una organización local, manda ese. Esto es lo que separa dos
   centros que la oficina tiene agrupados bajo una sola organización: los dos
   «HOSP. DR. PASTOR OROPEZA» (IVSS/Barquisimeto y Carora) comparten la org 800
   de la oficina y solo el ``establecimiento`` los distingue.
2. Si no, se usa el nombre de la organización de origen en la oficina.

Si un centro no tiene equivalente local, la fila se inserta con
``organizacion_id = NULL`` y se avisa (queda visible, no se inventa).

Uso::

    ./.venv/bin/python migracion/aplicar_dump_oficina.py [--ejecutar]
        [--local-db sis_salud_db] [--oficina-db sis_salud_db_oficina]
        [--limite N]

Sin ``--ejecutar`` solo informa (dry-run). Es idempotente: volver a correrlo no
duplica nada.

No toca: fichas, consolidados, conciliaciones, registradores, despacho,
usuarios/perfiles, ASIC ni el territorio. El espejo crudo y ``espejo_extra`` los
gestiona ``migracion/aplicar_dump_oficina.sh`` (opción ``--espejo``).
"""
import argparse
import os
import sys

import psycopg

TABLAS = ["registros_defuncion", "registros_nacimiento"]


def db(**over):
    base = {
        "host": os.environ.get("PGHOST", "localhost"),
        "port": os.environ.get("PGPORT", "5436"),
        "user": os.environ.get("PGUSER", "sis_user"),
        "password": os.environ.get("PGPASSWORD", "sis_password"),
    }
    base.update(over)
    return base


def columnas(cur, tabla):
    cur.execute(
        "select column_name from information_schema.columns "
        "where table_schema='public' and table_name=%s order by ordinal_position",
        (tabla,),
    )
    return [r[0] for r in cur.fetchall() if r[0] != "id"]


def mapa_organizaciones(cur):
    """nombre -> id (el primero si hay nombres repetidos)."""
    cur.execute("select id, nombre from seguridad_organizacion")
    por_nombre, por_id = {}, {}
    for oid, nombre in cur.fetchall():
        por_id[oid] = nombre
        por_nombre.setdefault(nombre, oid)
    return por_nombre, por_id


def resolver_centro(establecimiento, oficina_oid, org_nombre, local_por_nombre):
    """Devuelve (id_local, criterio). Prioriza el establecimiento sobre la org."""
    if establecimiento and establecimiento in local_por_nombre:
        return local_por_nombre[establecimiento], "establecimiento"
    if oficina_oid is None:
        return None, "sin_org"
    nombre = org_nombre.get(oficina_oid)
    if nombre and nombre in local_por_nombre:
        return local_por_nombre[nombre], "organizacion"
    return None, "sin_equivalente"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--local-db", default="sis_salud_db")
    ap.add_argument("--oficina-db", default="sis_salud_db_oficina")
    ap.add_argument("--ejecutar", action="store_true", help="aplica los cambios (por defecto: dry-run)")
    ap.add_argument("--limite", type=int, default=0, help="máximo de filas a insertar por tabla (0 = todas)")
    args = ap.parse_args()

    total = 0
    with psycopg.connect(**db(dbname=args.local_db)) as loc, \
            psycopg.connect(**db(dbname=args.oficina_db)) as off:
        loc.autocommit = False
        with loc.cursor() as c:
            local_por_nombre, _ = mapa_organizaciones(c)

        for tabla in TABLAS:
            with loc.cursor() as c:
                c.execute(f"select registro_numero from {tabla} where registro_numero is not null")
                claves_local = {r[0] for r in c.fetchall()}
            with off.cursor() as c:
                c.execute(f"select registro_numero from {tabla} where registro_numero is not null")
                claves_oficina = {r[0] for r in c.fetchall()}

            falta = sorted(claves_oficina - claves_local)
            if args.limite:
                falta = falta[: args.limite]
            print(f"\n===== {tabla}: faltan {len(falta)} de {len(claves_oficina)} en la oficina =====")
            if not falta:
                continue

            with off.cursor() as oc, loc.cursor() as lc:
                cols = columnas(oc, tabla)
                _, org_nombre = mapa_organizaciones(oc)
                sel = ", ".join(f'"{c}"' for c in cols)
                oc.execute(f"select {sel} from {tabla} where registro_numero = any(%s)", (falta,))
                filas = oc.fetchall()

                idx_org = cols.index("organizacion_id")
                idx_est = cols.index("establecimiento")
                insert_sql = (
                    f"INSERT INTO {tabla} (" + ", ".join(f'"{c}"' for c in cols) + ") VALUES ("
                    + ", ".join(["%s"] * len(cols)) + ")"
                )

                nuevos, sin_centro, por_est, por_org, distintos = 0, 0, 0, 0, 0
                for fila in filas:
                    fila = list(fila)
                    oficina_oid = fila[idx_org]
                    nuevo_id, criterio = resolver_centro(
                        fila[idx_est], oficina_oid, org_nombre, local_por_nombre
                    )
                    if criterio == "establecimiento":
                        por_est += 1
                    elif criterio == "organizacion":
                        por_org += 1
                        # ¿el establecimiento apuntaría a otro centro local?
                        est = fila[idx_est]
                        if est and est in local_por_nombre and local_por_nombre[est] != nuevo_id:
                            distintos += 1
                    if nuevo_id is None:
                        sin_centro += 1
                        print(f"    !! sin centro local: establecimiento={fila[idx_est]!r} "
                              f"org_oficina={org_nombre.get(oficina_oid)!r}")
                    fila[idx_org] = nuevo_id
                    if args.ejecutar:
                        lc.execute(insert_sql, fila)
                    nuevos += 1

                print(f"  a insertar={nuevos}  centro_por_establecimiento={por_est}  "
                      f"centro_por_organizacion={por_org}  sin_centro_local={sin_centro}")
                total += nuevos

        if args.ejecutar:
            loc.commit()
            print(f"\nCOMMIT OK. Filas nuevas totales: {total}")
        else:
            loc.rollback()
            print(f"\nDRY-RUN (nada aplicado). Filas a insertar: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
