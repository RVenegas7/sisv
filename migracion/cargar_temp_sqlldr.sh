#!/usr/bin/env bash
# =============================================================================
#  cargar_temp_sqlldr.sh
#  SISV — Carga los CSV de `exportar_rutalara` en el esquema TEMP del Oracle
#  10g de la oficina usando SQL*Loader, a partir de los `.ctl` que genera
#  `generar_ctl_sqlldr.py`.
#
#  Es el paso que reemplaza a la fase `repl` del motor legacy: en vez de
#  reconstruir TEMP.T_* con PL/SQL (plan B, replicar_controlado.sql), se carga
#  con sqlldr desde los CSV que SISV ya produce fielmente (PENDIENTES.md §38,
#  §39.6.3). El log de esta carga es el nuevo `repllar1.log` del sobre.
#
#  FLUJO COMPLETO DEL SOBRE (5 archivos que espera el central, §39.6):
#    1. exportar_rutalara           -> los 83 CSV (el contenido).
#    2. generar_ctl_sqlldr.py       -> los .ctl (este puente CSV -> TEMP).
#    3. cargar_temp_sqlldr.sh       -> TEMP cargado + repllar1.log (este guion).
#    4. generar_paquete_live.sh armar --con-stub
#                                   -> routlar1.dmp + routlar1.log (exp de TEMP)
#                                      + repllar1.log (de aquí) + 2 logs stub.
#       El sobre final lleva los 5 archivos que exige el central.
#
#  DÓNDE SE EJECUTA: en el servidor de la oficina (192.168.5.200), que es donde
#  están sqlldr 10.1.0.3.0, el esquema TEMP con las 82 tablas y el `exp` que
#  emite el dump V10.01.00. Antes hay que copiar ahí:
#     - el directorio con los CSV descomprimidos,
#     - el directorio con los .ctl (generado en casa).
#
#  REQUISITO DE PERMISOS: la cuenta que carga necesita poder INSERTAR en las 82
#  tablas TEMP y, además, poder vaciarlas:
#     - con --modo truncate (defecto del .ctl): el TRUNCATE de una tabla ajena
#       pide DROP ANY TABLE (o ser dueño de la tabla); ver §39.6.2 opción 1.
#     - con --modo replace (generar_ctl_sqlldr.py --modo replace): el REPLACE
#       hace DELETE + INSERT, así que basta DELETE + INSERT (dos grants).
#  Elija el modo según lo que autorice el DBA. La opción mínima y reversible
#  (INSERT) se queda corta para vaciar la tabla entre cargas.
#
#  USO (dentro del servidor de la oficina):
#    export ORACLE_HOME=/opt/oracle ORACLE_SID=lar1
#    export NLS_LANG=AMERICAN_AMERICA.AL32UTF8        # o el de los otros scripts
#    ./cargar_temp_sqlldr.sh --ctl-dir /tmp/ctl --csv-dir /tmp/csv \
#        --usuario respaldo --clave respaldo
#
#  SALIDA:
#    - <dest>/repllar1.log        log concatenado de todas las cargas (el que va
#                                 al sobre como repllar1.log).
#    - <dest>/<tabla>.log         log individual de cada sqlldr.
#    - un resumen final por tabla (filas cargadas / rechazadas).
# =============================================================================
set -euo pipefail

# --- parámetros --------------------------------------------------------------
CTL_DIR=""
CSV_DIR=""
USUARIO="${USUARIO:-respaldo}"
CLAVE="${CLAVE:-respaldo}"
ORACLE_SID="${ORACLE_SID:-lar1}"
ORACLE_HOME="${ORACLE_HOME:-/opt/oracle}"
SQLLDR="${SQLLDR:-$ORACLE_HOME/bin/sqlldr}"
DEST="${DEST:-.}"

usage() { sed -n '1,60p' "$0" >&2; exit 1; }
while [ $# -gt 0 ]; do
  case "$1" in
    --ctl-dir)  CTL_DIR="$2"; shift 2 ;;
    --csv-dir)  CSV_DIR="$2"; shift 2 ;;
    --usuario)  USUARIO="$2"; shift 2 ;;
    --clave)    CLAVE="$2"; shift 2 ;;
    --sid)      ORACLE_SID="$2"; shift 2 ;;
    --oracle-home) ORACLE_HOME="$2"; shift 2 ;;
    --dest)     DEST="$2"; shift 2 ;;
    *) echo "opción desconocida: $1" >&2; usage ;;
  esac
done

[ -n "$CTL_DIR" ] && [ -n "$CSV_DIR" ] || { echo "faltan --ctl-dir y --csv-dir" >&2; usage; }
[ -f "$CTL_DIR/_orden.txt" ] || { echo "no se encontró $CTL_DIR/_orden.txt (corra generar_ctl_sqlldr.py antes)" >&2; exit 1; }
[ -x "$SQLLDR" ] || { echo "no se encontró sqlldr en $SQLLDR" >&2; exit 1; }
[ -d "$CSV_DIR" ] || { echo "no existe el directorio de CSV $CSV_DIR" >&2; exit 1; }

mkdir -p "$DEST"
LOG_GRANDE="$DEST/repllar1.log"
: > "$LOG_GRANDE"

info() { echo "  $*"; }
die()  { echo "ERROR: $*" >&2; exit 1; }

export ORACLE_SID ORACLE_HOME
export NLS_LANG="${NLS_LANG:-AMERICAN_AMERICA.AL32UTF8}"

echo
echo "==============================================================="
echo "  Cargando TEMP desde los CSV  (sqlldr, $USUARIO@$ORACLE_SID)"
echo "==============================================================="

# Control files que se van a cargar, en el orden de _orden.txt
mapfile -t TABLAS < "$CTL_DIR/_orden.txt"
[ "${#TABLAS[@]}" -gt 0 ] || die "_orden.txt está vacío"

TOTAL_FILAS=0
FALLOS=0

for t in "${TABLAS[@]}"; do
  ctl="$CTL_DIR/$t.ctl"
  csv="$CSV_DIR/$t.csv"
  [ -f "$ctl" ] || die "falta el control file $ctl"
  [ -f "$csv" ] || { echo "  [AVISO] no existe $csv, se omite $t"; continue; }

  # sqlldr corre desde $CSV_DIR para que INFILE 'T_X.csv' (relativo) resuelva.
  ( cd "$CSV_DIR" && \
      "$SQLLDR" "$USUARIO/$CLAVE@$ORACLE_SID" \
        control="$ctl" log="$DEST/$t.log" bad="$DEST/$t.bad" \
        discard="$DEST/$t.discard" > "$DEST/$t.stdout" 2>&1 )
  rc=$?

  # sqlldr NO devuelve código de error fiable en 10.1: hay que mirar el log.
  if grep -qiE "ORA-[0-9]{5}|SQL\*Loader-[0-9]{5}" "$DEST/$t.log" 2>/dev/null \
     || [ "$rc" -ne 0 ]; then
    echo "  [FALLA] $t (rc=$rc). Revisar $DEST/$t.log"
    FALLOS=$((FALLOS+1))
  else
    filas=$(grep -m1 -oE "[0-9]+ Rows? successfully loaded|[0-9]+ filas? cargadas" \
            "$DEST/$t.log" 2>/dev/null | grep -oE "^[0-9]+" || echo 0)
    info "$t: $filas filas cargadas"
    TOTAL_FILAS=$((TOTAL_FILAS + filas))
  fi

  # Se anexa igual al log grande (para dejar el repllar1.log con el detalle).
  {
    echo "===== $t ====="
    cat "$DEST/$t.log" 2>/dev/null || true
    echo
  } >> "$LOG_GRANDE"
done

echo
echo "-------------------------------------------------------------------"
echo "  resumen: ${#TABLAS[@]} tablas, $TOTAL_FILAS filas cargadas, $FALLOS con error"
echo "  repllar1.log -> $LOG_GRANDE"

# Un .bad con contenido = filas rechazadas: eso es un fallo que no se puede
# ignorar (sería el equivalente a las filas que el `imp` perdía, §43.1).
if compgen -G "$DEST/*.bad" > /dev/null; then
  for b in "$DEST"/*.bad; do
    [ -s "$b" ] && { echo "  [FALLA] $b tiene filas rechazadas ($(wc -l < "$b"))"; FALLOS=$((FALLOS+1)); }
  done
fi

if [ "$FALLOS" -gt 0 ]; then
  echo
  die "hubo $FALLOS error(es). NO arme el sobre: revise los .log/.bad antes."
fi

echo
echo "  OK. Siguiente paso: generar_paquete_live.sh armar --con-stub"
echo "  (el repllar1.log ya está en $LOG_GRANDE)."
