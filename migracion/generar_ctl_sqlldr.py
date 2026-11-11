#!/usr/bin/env python3
# =============================================================================
#  generar_ctl_sqlldr.py
#  SISV — Generador de control files de SQL*Loader (`.ctl`) para cargar los CSV
#  de `exportar_rutalara` en el esquema TEMP del Oracle 10g de la oficina.
#
#  Cierra la única pieza de software que faltaba en PENDIENTES.md §39.6.3:
#  SISV ya produce el CONTENIDO del sobre (los 83 CSV), el DDL de TEMP y el exp
#  que arma el routlar1.dmp; lo que faltaba es el puente CSV -> TEMP, que es
#  justo este generador + su script de carga (cargar_temp_sqlldr.sh).
#
#  CONTEXTO (¿por qué sqlldr y no `replicar_controlado.sql`?)
#    - El central exige el `.dmp` que genera Oracle (exp 10.1.0.3.0), así que
#      el sobre se empaqueta con `exp owner=TEMP` en el servidor de la oficina
#      (PENDIENTES.md §39.6). Para que el dump salga idéntico al del legacy,
#      TEMP tiene que contener exactamente lo que viaja en el sobre.
#    - Antes se llenaba TEMP con el plan B (PL/SQL, replicar_controlado.sql);
#      ahora se llena con SQL*Loader desde los CSV de exportar_rutalara, que ya
#      replican el contrato del ruteo (PENDIENTES.md §38). El log de esa carga
#      es el nuevo repllar1.log del sobre (los otros 4 archivos los arma
#      generar_paquete_live.sh: routlar1.dmp + routlar1.log del exp, y los
#      2 logs stub copyhistlar1.log / bloqlar1.log).
#
#  QUÉ GENERA
#    - Un `.ctl` por cada CSV de exportar_rutalara, EXCEPTO T_CERTNACI (el
#      esquema TEMP real del servidor no tiene esa tabla; ver §39.6.3). El
#      manifiesto T_EVENTOS se carga también (sin cabecera, 4 de 6 columnas).
#    - Un archivo `_orden.txt` con el orden de carga y un resumen por tabla.
#
#  REGLAS QUE APLICA (PENDIENTES.md §39.6.3)
#    - CSV `|`-separados, con cabecera (salvo T_EVENTOS), sin comillas, NULL
#      como campo vacío, fechas `AAAA-MM-DD HH:MM:SS` (o `AAAA-MM-DD`).
#    - `FIELDS TERMINATED BY '|'` + `SKIP=1` (o `SKIP=0` para T_EVENTOS) y
#      `NULLIF col = BLANKS` para los opcionales.
#    - FALLA FUERTE si un `|` aparece dentro de un texto (no hay escapado en el
#      CSV); se detecta porque la línea deja de tener el nº exacto de campos.
#    - Tablas con solo cabecera (0 filas) cargan 0 filas sin error.
#    - Columnas del CSV que no existen en el DDL de TEMP (p. ej. VALSEXO y
#      VALCAUSABASICA de T_CERTMORT) se descartan con FILLER; columnas del DDL
#      que el CSV no trae (STATUS/AMS de T_EVENTOS) quedan NULL y se comprueba
#      que sean nullable.
#    - Las columnas DATE llevan su máscara, deducida de los datos del propio CSV
#      (se admite `YYYY-MM-DD` o `YYYY-MM-DD HH24:MI:SS`, nunca ambas mezcladas).
#
#  USO
#    # 1) Generar los CSV (si no los tiene ya):
#    ./manage.py exportar_rutalara --salida /tmp/sobre
#    # 2) Generar los .ctl:
#    ./.venv/bin/python migracion/generar_ctl_sqlldr.py \
#        --zip /tmp/sobre/generado_*.zip --salida /tmp/ctl
#    #    ...o desde un directorio ya descomprimido:
#    ./.venv/bin/python migracion/generar_ctl_sqlldr.py \
#        --csv-dir /tmp/sobre_extraido --salida /tmp/ctl
#    # 3) Solo validar (sin escribir nada):
#    ./.venv/bin/python migracion/generar_ctl_sqlldr.py --zip ... --validar
#
#  Opciones útiles:
#    --modo replace      usa REPLACE (DELETE + carga) en vez de TRUNCATE; útil
#                        si la cuenta de carga no tiene DROP ANY TABLE.
#    --charset UTF8      juego de caracteres del CSV (por defecto UTF8: los CSV
#                        salen UTF-8 de PostgreSQL y la BD destino es
#                        WE8ISO8859P1). Ver §39.6.4.
# =============================================================================
import argparse
import json
import os
import re
import sys
import zipfile

# --- tipos Oracle reconocidos en el DDL --------------------------------------
TIPOS_FECHA = {"DATE", "TIMESTAMP", "TIMESTAMP(6)"}
TIPOS_TEXTO = {"VARCHAR2", "VARCHAR", "CHAR", "NVARCHAR2", "NCHAR", "CLOB"}
TIPOS_NUMERO = {
    "NUMBER", "FLOAT", "INTEGER", "INT", "DECIMAL", "DOUBLE", "REAL",
    "BINARY_FLOAT", "BINARY_DOUBLE", "SMALLINT",
}

# --- expresiones para parsear el DDL -----------------------------------------
RE_TABLA = re.compile(r'CREATE TABLE "TEMP"\."(T_[A-Z0-9_]+)"\s*\((.*?)\)\s*SEGMENT', re.S)
RE_COLUMNA = re.compile(r'"([A-Z0-9_]+)"\s+([A-Z0-9]+(?:\([^)]*\))?)([^,]*?)(?:,|$)', re.S)

# --- formatos de fecha admitidos en los CSV ----------------------------------
RE_FECHA_HORA = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$')
RE_FECHA_SOLO = re.compile(r'^\d{4}-\d{2}-\d{2}$')

# Orden de columnas del manifiesto T_EVENTOS (es el único CSV sin cabecera).
T_EVENTOS_COLUMNAS = ["TABLA", "EVENTO", "FECHA", "ID"]

# La tabla T_CERTNACI existe en el spec (y en el DDL del espejo) pero NO en el
# esquema TEMP real del servidor de la oficina; el sobre real tampoco la trae.
# Ver PENDIENTES.md §39.6.3 y §34.
TABLA_SALTADA = "T_CERTNACI"


def _raiz():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parsear_ddl(texto):
    """Devuelve {tabla: (lista_ordenada, {columna: (tipo, not_null)})}."""
    tablas = {}
    for m in RE_TABLA.finditer(texto):
        nombre = m.group(1)
        cuerpo = m.group(2)
        orden, mapa = [], {}
        for cm in RE_COLUMNA.finditer(cuerpo):
            col = cm.group(1)
            tipo = cm.group(2)
            not_null = "NOT NULL" in cm.group(3).upper()
            orden.append(col)
            mapa[col] = (tipo, not_null)
        tablas[nombre] = (orden, mapa)
    return tablas


def leer_csv(nombre, csv_dir=None, zip_path=None):
    """Lee el contenido de un CSV desde un directorio o desde el ZIP."""
    if zip_path is not None:
        with zipfile.ZipFile(zip_path) as z:
            return z.read(nombre).decode("utf-8")
    with open(os.path.join(csv_dir, nombre), encoding="utf-8") as f:
        return f.read()


class ErrorCSV(Exception):
    """Un CSV no se puede cargar (p. ej. un `|` dentro de un texto)."""


def _lineas_datos(texto, nombre, n_columnas):
    """Parte el CSV en líneas de datos y FALLA FUERTE si un `|` está dentro de
    un texto (la línea no tendría el nº exacto de campos)."""
    lineas = []
    for num, ln in enumerate(texto.split("\n"), 1):
        if ln == "":
            continue  # última línea vacía del `\n` final
        campos = ln.split("|")
        if len(campos) != n_columnas:
            raise ErrorCSV(
                f"{nombre} línea {num}: esperaba {n_columnas} campos y hay "
                f"{len(campos)}. Hay un '|' dentro de un texto o el CSV está "
                f"malformado. No se genera nada (falla fuerte, ver §39.6.3)."
            )
        lineas.append(campos)
    return lineas


def _mascara_fecha(valores):
    """Deduce la máscara de una columna DATE desde sus valores no vacíos.

    Devuelve "YYYY-MM-DD", "YYYY-MM-DD HH24:MI:SS", o None si aparecen las dos
    formas en la misma columna (no debería pasar: se falla fuerte).
    """
    vio_hora = vio_solo = False
    for v in valores:
        if RE_FECHA_HORA.match(v):
            vio_hora = True
        elif RE_FECHA_SOLO.match(v):
            vio_solo = True
        elif v == "":
            continue
        else:
            return None  # valor que no parece fecha
    if vio_hora and vio_solo:
        return None
    if vio_solo:
        return "YYYY-MM-DD"
    return "YYYY-MM-DD HH24:MI:SS"


def _es_tipo(tipo, conjunto):
    base = tipo.upper().split("(")[0].strip()
    return base in conjunto


def generar_ctl(tabla, columnas_csv, ddl_orden, ddl_mapa, mascaras,
                modo, charset, con_cabecera):
    """Construye el texto del control file para una tabla."""
    out = []
    out.append("OPTIONS (SKIP=%d)" % (1 if con_cabecera else 0))
    out.append("LOAD DATA")
    out.append("CHARACTERSET %s" % charset)
    out.append("INFILE '%s.csv'" % tabla)
    out.append(modo.upper())  # TRUNCATE o REPLACE
    out.append("INTO TABLE TEMP.%s" % tabla)
    out.append("FIELDS TERMINATED BY '|'")
    out.append("TRAILING NULLCOLS")
    out.append("(")

    specs = []
    presentes = set()
    for col in columnas_csv:
        presentes.add(col)
        if col not in ddl_mapa:
            # columna del CSV que no existe en TEMP: se lee y se descarta
            specs.append('  "%s" FILLER' % col)
            continue
        tipo, not_null = ddl_mapa[col]
        if _es_tipo(tipo, TIPOS_FECHA):
            mascara = mascaras.get(col, "YYYY-MM-DD HH24:MI:SS")
            base = '"%s" DATE "%s"' % (col, mascara)
        else:
            base = '"%s"' % col
        if not not_null:
            base += ' NULLIF "%s" = BLANKS' % col
        specs.append("  " + base)

    # Columnas del DDL que el CSV no trae: deben poder quedar NULL.
    for col in ddl_orden:
        if col in presentes:
            continue
        tipo, not_null = ddl_mapa[col]
        if not_null:
            raise SystemExit(
                f"ERROR: {tabla}: la columna NOT NULL \"{col}\" no viene en el "
                f"CSV y quedaría vacía. Revise el spec o el DDL."
            )

    out.append(",\n".join(specs))
    out.append(")")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Genera .ctl de SQL*Loader para cargar TEMP.")
    ap.add_argument("--zip", help="ZIP de exportar_rutalara con los CSV.")
    ap.add_argument("--csv-dir", help="Directorio con los CSV ya descomprimidos.")
    ap.add_argument("--salida", default="ctl", help="Directorio de salida de los .ctl (def: ctl).")
    ap.add_argument("--ddl", default=os.path.join(_raiz(), "migracion", "simulacion", "00_ddl_temp_04082026.sql"),
                    help="DDL de TEMP (def: el del espejo, migracion/simulacion/00_ddl_temp_04082026.sql).")
    ap.add_argument("--spec", default=os.path.join(_raiz(), "backend", "registros", "data", "rutarala_spec.json"),
                    help="Spec de exportar_rutalara (rutarala_spec.json).")
    ap.add_argument("--modo", choices=["truncate", "replace"], default="truncate",
                    help="Modo de carga en el .ctl: TRUNCATE (def) o REPLACE.")
    ap.add_argument("--charset", default="UTF8",
                    help="Juego de caracteres del CSV para SQL*Loader (def: UTF8).")
    ap.add_argument("--validar", action="store_true",
                    help="Solo valida los CSV contra el DDL/spec; no escribe .ctl.")
    args = ap.parse_args()

    if bool(args.zip) == bool(args.csv_dir):
        ap.error("Indique --zip O --csv-dir (exactamente uno).")

    if not os.path.exists(args.ddl) or not os.path.exists(args.spec):
        ap.error("No se encontró el DDL o el spec; revíselos con --ddl/--spec.")

    ddl = parsear_ddl(open(args.ddl, encoding="utf-8").read())
    spec = json.load(open(args.spec, encoding="utf-8"))
    columnas = spec["columnas"]

    # Orden de los CSV tal como los escribe exportar_rutalara: T_EVENTOS primero,
    # luego el resto ordenado alfabéticamente.
    tablas = ["T_EVENTOS"] + sorted(columnas)

    orden_carga = []
    generados = {}  # tabla -> texto del .ctl (solo se escribe si no hay errores)
    total_filas = 0
    total_saltadas = 0
    problemas = []

    for tabla in tablas:
        if tabla == TABLA_SALTADA:
            total_saltadas += 1
            print(f"  [SALTADA] {tabla}: no existe en TEMP (ver §39.6.3); no se genera .ctl")
            continue

        # Columnas que trae el CSV y cabecera sí/no.
        if tabla == "T_EVENTOS":
            cols_csv = T_EVENTOS_COLUMNAS
            con_cabecera = False
        else:
            cols_csv = columnas[tabla]
            con_cabecera = True

        if tabla not in ddl:
            problemas.append(f"{tabla}: no está en el DDL, no se puede generar .ctl")
            continue

        ddl_orden, ddl_mapa = ddl[tabla]

        # Columnas del CSV que no existen en TEMP -> FILLER (aviso informativo).
        solo_csv = [c for c in cols_csv if c not in ddl_mapa]

        texto = leer_csv(tabla + ".csv", args.csv_dir, args.zip)

        # Validar cabecera (para las tablas con cabecera) y quedarnos solo con
        # el cuerpo de datos.
        primera = texto.split("\n", 1)[0]
        if con_cabecera:
            esperada = "|".join(cols_csv)
            if primera != esperada:
                problemas.append(
                    f"{tabla}: la cabecera no coincide con el spec.\n"
                    f"    esperado: {esperada}\n"
                    f"    real    : {primera}"
                )
                continue
            cuerpo = texto.split("\n", 1)[1] if "\n" in texto else ""
        else:
            cuerpo = texto

        try:
            lineas = _lineas_datos(cuerpo, tabla, len(cols_csv))
        except ErrorCSV as e:
            problemas.append(str(e))
            continue

        # Deducir máscara de las columnas DATE recorriendo las filas una vez.
        columnas_date = [c for c in cols_csv if c in ddl_mapa and _es_tipo(ddl_mapa[c][0], TIPOS_FECHA)]
        valores_date = {c: [] for c in columnas_date}
        for campos in lineas:
            for i, c in enumerate(cols_csv):
                if c in valores_date and campos[i] != "":
                    valores_date[c].append(campos[i])

        mascaras = {}
        mascara_err = None
        for c in columnas_date:
            m = _mascara_fecha(valores_date[c])
            if m is None:
                mascara_err = (
                    f"{tabla}.{c}: valores de fecha mixtos o no reconocidos; "
                    f"no se puede fijar una sola máscara"
                )
                break
            mascaras[c] = m
        if mascara_err:
            problemas.append(mascara_err)
            continue

        ctl = generar_ctl(tabla, cols_csv, ddl_orden, ddl_mapa, mascaras,
                          args.modo, args.charset, con_cabecera)

        n_filas = len(lineas)
        total_filas += n_filas
        orden_carga.append(tabla)
        generados[tabla] = ctl
        print(f"  [OK] {tabla}: {n_filas} filas, {len(cols_csv)} columnas "
              f"({len(columnas_date)} fecha)" + (f", FILLER {solo_csv}" if solo_csv else ""))

    if problemas:
        print("\nERRORES DE VALIDACIÓN (no se escribe nada):")
        for p in problemas:
            print("  - " + p)
        sys.exit(1)

    if not args.validar:
        os.makedirs(args.salida, exist_ok=True)
        for tabla, ctl in generados.items():
            with open(os.path.join(args.salida, tabla + ".ctl"), "w", encoding="utf-8") as f:
                f.write(ctl)
        with open(os.path.join(args.salida, "_orden.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(orden_carga) + "\n")
        print(f"\nEscritos {len(generados)} .ctl en {args.salida}/ + _orden.txt")

    print(f"\nResumen: {len(generados)} tablas listas, {total_filas} filas, "
          f"{total_saltadas} saltadas ({TABLA_SALTADA}).")


if __name__ == "__main__":
    main()
