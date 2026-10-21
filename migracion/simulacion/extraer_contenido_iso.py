#!/usr/bin/env python3
"""Extrae el contenido de las T_* del sobre real (esquema ENVxx del Oracle local) a CSV
pipe-delimited con las fechas en formato ISO, para compararlo campo a campo con lo que
genera SISV. Salida: /tmp/opencode/iso_<OWNER>_<TABLA>.csv

Uso: python3 extraer_contenido_iso.py ENV14
Genera /tmp/opencode/extra_iso_<OWNER>.sql, que hay que ejecutar con sqlplus en el
contenedor y luego copiar los CSV.
"""
import json
import sys

SPEC = "backend/registros/data/rutarala_spec.json"

# Columnas de tipo DATE conocidas en el legado (se emiten con TO_CHAR ISO)
FECHAS = {
    "FECHA", "FECHAOPERACION", "FECHANACIMIENTO", "FECHA_M", "FECHA_N", "FECHA_MV",
    "FECHAREGISTRO", "FECHACERTIFICADO", "FECHAEVOLUCION", "FECHA_ANULADO",
    "FECHA_OPERACION", "FECHAREPARA", "FECHANOTIFICACION", "FECHA_INTERV",
    "FECHA_INGRESO", "FECHA_SALIDA",
}


def main():
    owner = sys.argv[1]
    columnas = json.load(open(SPEC))["columnas"]
    sql = ["SET PAGES 0 FEED OFF LINES 32767 TRIMSPOOL ON"]
    for t, cols in sorted(columnas.items()):
        if t in ("T_CERTNACI", "T_EVENTOS", "T_AUDITORIA"):
            continue  # T_CERTNACI puede faltar; T_EVENTOS/T_AUDITORIA no son event-driven
        partes = [
            f"NVL(TO_CHAR(\"{c}\",'YYYY-MM-DD HH24:MI:SS'),'')" if c in FECHAS
            else f"NVL(TO_CHAR(\"{c}\"),'')"
            for c in cols
        ]
        sql.append(f"SPOOL /tmp/iso_{owner}_{t}.csv")
        sql.append("SELECT " + "||'|'||".join(partes) + f' FROM {owner}."{t}" ORDER BY "ID";')
        sql.append("SPOOL OFF")
    sql.append("EXIT")
    ruta = f"/tmp/opencode/extra_iso_{owner}.sql"
    open(ruta, "w").write("\n".join(sql) + "\n")
    print(f"escrito {ruta} — ejecutar con sqlplus y copiar /tmp/iso_{owner}_*.csv")


if __name__ == "__main__":
    main()
