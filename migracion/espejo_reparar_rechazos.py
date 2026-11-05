#!/usr/bin/env python3
"""Repara las filas que `imp` rechaza por la semantica BYTE de las columnas.

Por que existe (04-05/11/2026)
------------------------------
El `.dmp` trae las columnas como las tenia el Oracle de origen: `VARCHAR2(n BYTE)`.
`imp` las recrea con ESA semantica e ignora `NLS_LENGTH_SEMANTICS` del cliente y
del servidor (comprobado: con la instancia en CHAR y la variable de entorno en
CHAR, las tablas siguen saliendo BYTE). En una base `AL32UTF8` un texto con
acentos ocupa 2 bytes por caracter, asi que las filas que llegan justo al limite
se rechazan con `IMP-00019` / `ORA-12899`; `imp` avisa, sigue y termina "OK", de
modo que la perdida es **silenciosa**. En el refresco del 04/11/2026 fueron 194
filas: 50 `CERTNACIMIENTO`, 35 `NAC_MADRE`, 2 `CASOS_MMI` (entre ellas
certificados y madres que el ETL necesita para armar los nacimientos).

Que hace, por tabla afectada
----------------------------
1. `ALTER TABLE ... MODIFY (col VARCHAR2(n CHAR))` con el `maximum` que reporta
   el propio error (nunca se agranda el limite, solo cambia la semantica).
2. `TRUNCATE TABLE` (la tabla queda vacia conservando indices y constraints).
3. Reimporta **solo esa tabla** con un parfile propio e `IGNORE=Y`: como la tabla
   ya existe, `imp` no la recrea y solo inserta las filas.

Es idempotente: sin rechazos no hace nada, y si se corre dos veces la segunda no
encuentra rechazos.

Uso:
    python migracion/espejo_reparar_rechazos.py --work /home/program/espejo_work \
        [--contenedor sis_oracle_legacy] [--ora-pass oracle123] [--ejecutar]

Sin `--ejecutar` solo informa de lo que repararia y deja escritos el SQL y los
parfiles en el directorio de artefactos.
"""
import argparse
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# ORA-12899: value too large for column "SISMAI"."CERTNACIMIENTO"."JEFECIVIL" (actual: 41, maximum: 40)
RE_RECHAZO = re.compile(
    r'ORA-12899: value too large for column "([A-Z0-9_$#]+)"\."([A-Z0-9_$#]+)"\."([A-Z0-9_$#]+)"'
    r" \(actual: (\d+), maximum: (\d+)\)"
)
RE_IMPORTANDO = re.compile(r'\. \. importing table\s+"([A-Z0-9_$#]+)"')
# Tablas donde `imp` no puede recrear el DDL por LONG u otros tipos especiales:
# aqui solo se tocan VARCHAR2, pero se deja la puerta cerrada por claridad.
ESQUEMAS_SIN_REPARACION: set[str] = set()


def rechazos_de(log: Path):
    """{(esquema, tabla): {columna: limite_en_bytes}} de la bitacora de un `imp`."""
    out: dict[tuple[str, str], dict[str, int]] = defaultdict(dict)
    tabla_actual = None
    for linea in log.read_text(errors="replace").splitlines():
        m = RE_IMPORTANDO.search(linea)
        if m:
            tabla_actual = m.group(1)
        m = RE_RECHAZO.search(linea)
        if m:
            esquema, tabla, columna, _actual, maximo = m.groups()
            out[(esquema, tabla.upper())][columna.upper()] = int(maximo)
    return {k: v for k, v in out.items() if k[0] not in ESQUEMAS_SIN_REPARACION}


def sql_reparacion(rechazos, truncar=True):
    esquemas = sorted({e for (e, _t) in rechazos})
    lista = ", ".join(f"'{e}'" for e in esquemas)
    lineas = [
        "set pagesize 0 feedback off heading off verify off",
        "whenever sqlerror exit failure",
        # Los triggers del esquema de origen quedan INVALIDOS al cambiar una
        # columna (ORA-04098) y bloquean el INSERT del reimport. En un espejo de
        # solo lectura no aportan nada: se deshabilitan antes de tocar las tablas.
        "declare",
        "  v_sql varchar2(400);",
        "begin",
        "  for r in (select owner, trigger_name from all_triggers",
        f"             where owner in ({lista}) and status = 'ENABLED') loop",
        "    v_sql := 'alter trigger \"'||r.owner||'\".\"'||r.trigger_name||'\" disable';",
        "    begin execute immediate v_sql; exception when others then null; end;",
        "  end loop;",
        "end;",
        "/",
    ]
    for (esquema, tabla), columnas in sorted(rechazos.items()):
        cambios = ", ".join(
            f'"{c}" varchar2({n} char)' for c, n in sorted(columnas.items())
        )
        lineas.append(f'alter table "{esquema}"."{tabla}" modify ({cambios});')
        if truncar:
            lineas.append(f'truncate table "{esquema}"."{tabla}";')
    lineas.append("exit;")
    return "\n".join(lineas) + "\n"


def parfiles_reparacion(rechazos, dir_work: Path, ora_pass: str, dumps: dict[str, str]):
    """Un parfile por esquema con las tablas a reimportar."""
    por_esquema: dict[str, list[str]] = defaultdict(list)
    for (esquema, tabla) in rechazos:
        por_esquema[esquema].append(tabla)
    rutas = []
    for esquema, tablas in sorted(por_esquema.items()):
        ruta = dir_work / f"imp_fix_{esquema}.par"
        lista = ",".join(f'"{t}"' for t in sorted(tablas))
        ruta.write_text(
            "USERID=system/{p}@XE\n"
            "FILE={f}\n"
            "FROMUSER={e}\n"
            "TOUSER={e}\n"
            "TABLES=({l})\n"
            "INDEXES=N\n"
            "CONSTRAINTS=N\n"
            "GRANTS=N\n"
            "IGNORE=Y\n".format(p=ora_pass, f=dumps[esquema], e=esquema, l=lista)
        )
        rutas.append((esquema, ruta))
    return rutas


def ejecutar(contenedor: str, args: list[str], **kw):
    return subprocess.run(
        ["docker", "exec", contenedor, *args], check=False, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kw
    )


# Un registro puede chocar con varias columnas: al ensanchar la primera, el
# rechazo se muda a la siguiente del mismo INSERT. Por eso el reparador itera
# (cada vuelta vuelve a leer la bitacora del reimport y arregla lo que quede).
MAX_VUELTAS = 8


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--work", required=True, type=Path, help="directorio de artefactos (los imp_*.log)")
    ap.add_argument("--contenedor", default="sis_oracle_legacy")
    ap.add_argument("--ora-pass", default="oracle123")
    ap.add_argument("--ejecutar", action="store_true", help="aplica el arreglo (sin esto solo informa)")
    args = ap.parse_args()

    # Solo las bitacoras de la importacion completa (no las del propio reparador).
    logs = [p for p in sorted(args.work.glob("imp_*.log")) if not p.name.startswith("imp_fix_")]
    if not logs:
        print(f"No hay bitacoras imp_*.log en {args.work}; nada que reparar.")
        return 0

    # Los .dmp tal como los ve el contenedor: el parfile dice FILE=<ESQ>.dmp
    dumps = {p.stem.replace("imp_", ""): f"{p.stem.replace('imp_', '')}.dmp" for p in logs}

    pendientes: dict[tuple[str, str], dict[str, int]] = {}
    for log in logs:
        encontrados = rechazos_de(log)
        if encontrados:
            print(f"  {log.name}: {sum(len(c) for c in encontrados.values())} columnas afectadas en {len(encontrados)} tablas")
            for k, cols in encontrados.items():
                pendientes.setdefault(k, {}).update(cols)

    if not pendientes:
        print("Sin rechazos que reparar.")
        return 0

    total_cols = sum(len(c) for c in pendientes.values())
    print(f"\nTablas con rechazos: {len(pendientes)}  columnas: {total_cols}")

    for vuelta in range(1, MAX_VUELTAS + 1):
        sql = args.work / "fix_rechazos.sql"
        sql.write_text(sql_reparacion(pendientes))
        pars = parfiles_reparacion(pendientes, args.work, args.ora_pass, dumps)
        print(f"\n-- vuelta {vuelta}: {len(pendientes)} tablas --")
        print(f"SQL:     {sql}")
        for _esquema, ruta in pars:
            print(f"Parfile: {ruta}")

        if not args.ejecutar:
            print("\n(dry-run) Vuelve a correrlo con --ejecutar para aplicar.")
            return 0

        # 1) ALTER + TRUNCATE
        print("\n== Alargando columnas a CHAR y vaciando las tablas ==")
        subprocess.run(["docker", "cp", str(sql), f"{args.contenedor}:/tmp/dmp/fix_rechazos.sql"], check=True)
        r = ejecutar(args.contenedor, ["bash", "-lc",
                     f"cd /tmp/dmp && sqlplus -s system/{args.ora_pass}@XE @fix_rechazos.sql"])
        print(r.stdout.strip() or "(sin salida)")
        if r.returncode != 0 or "ORA-" in r.stdout:
            print(" [FALLO] el ALTER/TRUNCATE no termino bien; no se reimporta nada.")
            return 1

        # 2) Reimportar las tablas afectadas y leer los rechazos que queden
        nuevos: dict[tuple[str, str], dict[str, int]] = {}
        for esquema, ruta in pars:
            print(f"\n== Reimportando {esquema} (solo las tablas afectadas) ==")
            subprocess.run(["docker", "cp", str(ruta), f"{args.contenedor}:/tmp/dmp/{ruta.name}"], check=True)
            r = ejecutar(args.contenedor, ["bash", "-lc",
                         f"cd /tmp/dmp && imp system/{args.ora_pass}@XE parfile={ruta.name}"])
            salida = r.stdout or ""
            # Se guarda para que quede la evidencia de cada vuelta.
            (args.work / f"imp_fix_{esquema}.log").write_text(salida)
            print(salida.strip()[-1500:] or "(sin salida)")
            for k, cols in rechazos_de(args.work / f"imp_fix_{esquema}.log").items():
                nuevos.setdefault(k, {}).update(cols)

        if not nuevos:
            print(f"\n [ OK ]   sin rechazos pendientes (vuelta {vuelta})")
            return 0
        print(f"\n [INFO] siguen {sum(len(c) for c in nuevos.values())} columnas con rechazos; se corrigen en la vuelta {vuelta + 1}")
        pendientes = nuevos

    print(f" [FALLO] tras {MAX_VUELTAS} vueltas sigue habiendo rechazos.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
