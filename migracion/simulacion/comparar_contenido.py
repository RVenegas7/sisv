#!/usr/bin/env python3
"""Compara el CONTENIDO campo a campo entre un sobre generado por SISV y el sobre real,
para las filas que existen en ambos lados. Clasifica cada diferencia para separar
frescura del espejo de posibles bugs.

Contexto: el espejo local `sismai.*` suele estar congelado en una fecha anterior a la
ventana del sobre, así que MUCHAS filas del sobre real aún no están en el espejo. Este
script solo mira las filas presentes en ambos (intersección por ID) y clasifica:
  - ARTEFACTO_FECHA   : mismo instante con/sin la hora '00:00:00'
  - ARTEFACTO_PADDING : solo difieren espacios extremos (CHAR de ancho fijo)
  - FRESCURA          : la fila real trae FECHAOPERACION posterior al congelamiento,
                        o un USUARIO/LOGIN distinto (fila re-editada)
  - REAL              : cualquier otra cosa → revisar (posible bug)

Requisitos: los CSV del lado real extraídos con formato ISO por
  migracion/simulacion/extraer_contenido_iso.py (salida en /tmp/opencode/iso_<OWNER>_*.csv)
y el ZIP generado por SISV en /tmp/opencode/simulacion/<env>/.

Uso: python3 comparar_contenido.py ENV14 <ruta_zip_generado>
"""
import glob
import json
import re
import sys
import zipfile

SPEC = "backend/registros/data/rutarala_spec.json"
CARPETA_SIM = "/tmp/opencode/simulacion"
MESES = {m: i + 1 for i, m in enumerate("JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split())}
RE_F = re.compile(r"^(\d{2})-([A-Z]{3})-(\d{2})(?: (\d{2}:\d{2}:\d{2}))?$")
# Fecha de congelamiento asumida del espejo (ajustar si se refresca el espejo)
CONGELADO = "2026-10-02"


def normalizar(v):
    v = v.strip()
    m = RE_F.match(v)
    if m:
        d, me, a, h = m.groups()
        y = int(a) + (2000 if int(a) < 70 else 1900)
        return f"{y:04d}-{MESES[me]:02d}-{int(d):02d}" + (f" {h}" if h else "")
    return v


def es_fecha_sin_hora(x):
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", x))


def main():
    owner = sys.argv[1]
    env = owner.lower()
    zpath = sys.argv[2] if len(sys.argv) > 2 else glob.glob(f"{CARPETA_SIM}/{env}/*.zip")[0]
    columnas = json.load(open(SPEC))["columnas"]
    mapeo = json.load(open(SPEC))["mapeo"]
    z = zipfile.ZipFile(zpath)

    # IDs que el manifiesto del sobre marca como tocados en la ventana (evento 1/2)
    # → si una fila está en esta lista y difiere, es frescura del espejo garantizada.
    tocados = set()
    try:
        for linea in open(f"/tmp/opencode/manifiesto_{env}.txt"):
            partes = linea.rstrip("\n").split("|")
            if len(partes) == 4 and partes[1] in ("1", "2"):
                tocados.add((partes[0], partes[3]))
    except FileNotFoundError:
        pass

    tablas = sorted({n[:-4] for n in z.namelist() if n.endswith(".csv") and n != "T_EVENTOS.csv"})
    clases = {"ARTEFACTO_FECHA": 0, "ARTEFACTO_PADDING": 0, "FRESCURA": 0, "REAL": 0}
    reales, filas_cmp = [], 0

    for t in tablas:
        ruta = f"/tmp/opencode/iso_{owner}_{t}.csv"
        try:
            lineas_reales = open(ruta, errors="replace").read().splitlines()
        except FileNotFoundError:
            continue          # tabla no extraída (sin filas comunes)
        real = {r.split("|", 1)[0].strip(): r.rstrip("\n") for r in lineas_reales if r}
        esp = {r.split("|", 1)[0]: r for r in
               z.read(f"{t}.csv").decode("utf-8", errors="replace").splitlines()[1:] if r}
        cols = columnas[t]
        for id_ in sorted(set(real) & set(esp)):
            filas_cmp += 1
            vr = [c.rstrip() for c in real[id_].split("|")]
            ve = esp[id_].split("|")
            if len(vr) != len(ve):
                clases["REAL"] += 1
                reales.append((t, id_, "nº de campos", len(vr), len(ve)))
                continue
            for i in range(len(vr)):
                a, b = normalizar(vr[i]), normalizar(ve[i])
                if a == b:
                    continue
                if vr[i].strip() == ve[i].strip():
                    clases["ARTEFACTO_PADDING"] += 1
                elif (es_fecha_sin_hora(a) and b == a + " 00:00:00") or \
                     (es_fecha_sin_hora(b) and a == b + " 00:00:00"):
                    clases["ARTEFACTO_FECHA"] += 1
                elif cols[i] in ("USUARIO", "LOGIN"):
                    clases["FRESCURA"] += 1
                else:
                    try:
                        fo = normalizar(vr[cols.index("FECHAOPERACION")])
                        if fo > CONGELADO:
                            clases["FRESCURA"] += 1
                            continue
                    except (ValueError, IndexError):
                        pass
                    # Fila tocada en la ventana del sobre → el espejo no la tenía aún
                    tabla_evento = next((k for k, v in mapeo.items() if v[1] == t), t)
                    if (tabla_evento, id_) in tocados:
                        clases["FRESCURA"] += 1
                        continue
                    clases["REAL"] += 1
                    reales.append((t, id_, cols[i], a, b))

    print(f"[{owner}] filas comparadas (intersección): {filas_cmp}")
    print("Clasificación de diferencias de campo:")
    for k, v in clases.items():
        print(f"   {k:18} {v}")
    if reales:
        print("\nCasos NO explicados (revisar):")
        for t, id_, c, a, b in reales:
            print(f"   {t} ID {id_} {c}: real={a!r} espejo={b!r}")
    return 1 if clases["REAL"] else 0


if __name__ == "__main__":
    sys.exit(main())
