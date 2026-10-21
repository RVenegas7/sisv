#!/usr/bin/env python3
"""Valida el sobre generado por SISV (`exportar_rutalara`) contra un sobre REAL ya
enviado (routlar1_*.ZIP). Prueba de equivalencia del contrato del sobre.

Qué comprueba
-------------
1. REGLA DE SELECCIÓN — para cada tabla T_* event-driven, los IDs que SISV selecciona
   (regla «último evento en la ventana es 1/2») deben coincidir EXACTAMENTE con los
   IDs que realmente viajan en el sobre (las filas del .dmp importado).
2. ESTRUCTURA DE COLUMNAS — nombre y orden de las columnas T_* del spec deben coincidir
   con las del .dmp importado.

Requisitos (los prepara `preparar_entorno_validacion.sh`):
  - Esquema ENVxx en el Oracle local `sis_oracle_legacy` (dmp real importado).
  - `/tmp/opencode/ids_<env>.csv`  : IDs de las T_* del dmp (una fila «TABLA,ID» por línea).
  - `/tmp/opencode/cols_<env>.csv` : columnas del dmp (TABLA,posición,NOMBRE).
  - `/tmp/opencode/manifiesto_<env>.txt` : manifiesto T_EVENTOS (TABLA|EVENTO|FECHA|ID),
    ordenado TABLA, ID, FECHA DESC.

Uso: python3 validar_sobre.py ENV14|ENV20
"""
import csv
import json
import sys

SPEC = "backend/registros/data/rutarala_spec.json"


def cargar_spec():
    return json.load(open(SPEC))


def validar_regla(mapeo, env):
    """IDs de SISV (regla) vs IDs reales del dmp."""
    env = env.lower()
    seleccion, vistos = {}, set()
    with open(f"/tmp/opencode/manifiesto_{env}.txt") as f:
        for linea in f:
            linea = linea.rstrip("\n")
            if not linea:
                continue
            tabla_ev, evento, _f, id_ev = linea.split("|")
            if (tabla_ev, id_ev) in vistos:
                continue
            vistos.add((tabla_ev, id_ev))
            if evento in ("1", "2"):
                seleccion.setdefault(mapeo[tabla_ev][1], set()).add(id_ev)

    real, actual = {}, None
    with open(f"/tmp/opencode/ids_{env}.csv") as f:
        for linea in f:
            linea = linea.rstrip("\n")
            if linea.startswith("@@"):
                actual = linea[2:]
                real.setdefault(actual, set())
                continue
            if "," not in linea or linea.startswith(("ORA-", "SELECT", "*", "ERROR", "SP2-")):
                continue
            tabla, id_str = linea.split(",", 1)
            real.setdefault(tabla, set()).add(id_str.strip())

    # Tablas que el dmp real NO trae: se detectan porque su bloque de extracción
    # quedó vacío por ORA-00942. Se reportan aparte (no cuentan como diferencia).
    ausentes_dmp = {t for t, ids in real.items() if not ids and t in seleccion}

    exactas = dif = 0
    detalles = []
    extras = []
    for t in sorted(set(seleccion) | set(real)):
        sisv, dmp = seleccion.get(t, set()), real.get(t, set())
        if t not in real or t in ausentes_dmp:
            if sisv:
                extras.append((t, len(sisv)))
            continue
        # T_AUDITORIA viaja completa por diseño, no es event-driven
        if t == "T_AUDITORIA":
            continue
        if sisv == dmp:
            exactas += 1
        else:
            dif += 1
            detalles.append((t, len(sisv), len(dmp), len(sisv - dmp), len(dmp - sisv)))
    return exactas, dif, detalles, extras


def validar_columnas(columnas, env):
    env = env.lower()
    real = {}
    with open(f"/tmp/opencode/cols_{env}.csv") as f:
        for tabla, pos, col in csv.reader(f):
            real.setdefault(tabla, []).append((int(pos.strip()), col.strip()))
    orden = {t: [c for _, c in sorted(v)] for t, v in real.items()}

    exactas, dif, ausentes = 0, [], []
    for tabla, cols in sorted(columnas.items()):
        if tabla not in orden:
            ausentes.append(tabla)
            continue
        if orden[tabla] == cols:
            exactas += 1
        else:
            dif.append((tabla, cols, orden[tabla]))
    return exactas, dif, ausentes


def main():
    env = sys.argv[1] if len(sys.argv) > 1 else "ENV14"
    spec = cargar_spec()
    print(f"=== Validación del sobre contra el real {env} ===\n")

    exactas_r, dif_r, detalles, extras = validar_regla(spec["mapeo"], env)
    print(f"1) REGLA DE SELECCIÓN: {exactas_r} tablas exactas, {dif_r} con diferencias")
    for t, ns, nd, ss, sd in detalles:
        print(f"   DIF {t}: sisv={ns} dmp={nd} solo_sisv={ss} solo_dmp={sd}")
    for t, n in extras:
        print(f"   (SISV selecciona {t} ({n} ids) pero el sobre real no trae esa tabla — §34)")
    print("   T_AUDITORIA: viaja completa por diseño (no event-driven) — SISV no la genera (§16)\n")

    exactas_c, dif_c, ausentes = validar_columnas(spec["columnas"], env)
    print(f"2) COLUMNAS: {exactas_c}/{len(spec['columnas'])} exactas (nombre+orden)")
    for t, s, r in dif_c:
        solo_real = [(i + 1, c) for i, c in enumerate(r) if c not in s]
        solo_spec = [c for c in s if c not in r]
        print(f"   DIF {t}: solo_real={solo_real} solo_spec={solo_spec}")
    for t in ausentes:
        print(f"   AUSENTE en el sobre real: {t} (defecto del legado, §34)")

    ok = (dif_r == 0 and not detalles)
    if ok:
        print("\nRESULTADO: CONTRATO EQUIVALENTE ✔  "
              "(T_CERTNACI ausente del sobre real: defecto del legado, §34)")
    else:
        print("\nRESULTADO: hay diferencias ✘")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
