#!/usr/bin/env bash
# ==============================================================================
# FASE 1 de la ventana del martes 29/09/2026 (PENDIENTES §17.17).
# Baja del Oracle 10g de SIS/Lara SOLO el periodo roto (>= 01/08/2026) para
# recuperar el hueco de muerte materna y neonatal.
#
# POR QUE: la captura se corto el 02/08/2026 (§17.21) pero la oficina aclaro que
# el envio semanal se sigue emitiendo todos los martes -> los datos EXISTEN en el
# sistema del centro, nunca llegaron al espejo. Esta fase los baja.
#
# SOLO LECTURA. No toca SISMAI.EVENTOS_SINC ni ninguna tabla de la cola.
# El SQL de las consultas esta en migracion/extraer_mm_mn_roto.sql (SELECT + SPOOL).
#
# Uso:
#   ./migracion/extraer_mm_mn_roto.sh
#   SALIDA=/ruta ./migracion/extraer_mm_mn_roto.sh
#   DESDE=01/07/2026 ./migracion/extraer_mm_mn_roto.sh      # ampliar el rango
#   HOST=192.168.5.200 USUARIO=respaldo CLAVE=respaldo ./migracion/extraer_mm_mn_roto.sh
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SQL="$SCRIPT_DIR/extraer_mm_mn_roto.sql"

DESDE="${DESDE:-01/08/2026}"
SALIDA="${SALIDA:-$SCRIPT_DIR/../salida_mm_mn_$(date +%Y%m%d_%H%M)}"
HOST="${HOST:-}"
USUARIO="${USUARIO:-respaldo}"
CLAVE="${CLAVE:-respaldo}"
ORACLE_SID="${ORACLE_SID:-lar1}"
SQLPLUS="${SQLPLUS:-/opt/oracle/bin/sqlplus}"
NLS_LANG="${NLS_LANG:-SPANISH_SPAIN.AL32UTF8}"

[ -r "$SQL" ] || { echo "ERROR: no existe $SQL" >&2; exit 1; }
command -v awk >/dev/null 2>&1 || { echo "ERROR: falta awk" >&2; exit 1; }

mkdir -p "$SALIDA"
SALIDA="$(cd "$SALIDA" && pwd)"

echo "=================================================================="
echo " Fase 1 - recuperacion del periodo roto (>= $DESDE)"
echo " Salida: $SALIDA"
echo " Modo:   SOLO LECTURA (SELECT + SPOOL)"
echo "=================================================================="

# El rango se fija en el SQL, que se genera desde la plantilla, para no depender de
# que el operador edite el archivo a mano el dia de la ventana.
TMP_SQL="$(mktemp)"
trap 'rm -f "$TMP_SQL"' EXIT
sed "s/DEFINE DESDE = '01\/08\/2026'/DEFINE DESDE = '$DESDE'/" "$SQL" > "$TMP_SQL"
if ! grep -q "DEFINE DESDE = '$DESDE'" "$TMP_SQL"; then
  echo "ERROR: no se pudo fijar DESDE=$DESDE en el SQL. Revisa la linea DEFINE." >&2
  exit 1
fi

export NLS_LANG

run_local() {
  echo ">> sqlplus local (SID $ORACLE_SID)"
  # shellcheck disable=SC2086
  "$SQLPLUS" -s "/ as sysdba" @"$TMP_SQL" "$SALIDA"
}

run_remote() {
  # El SQL viaja por stdin: el servidor no tiene el repo.
  if command -v sshpass >/dev/null 2>&1; then
    echo ">> sshpass: sqlplus remoto en $USUARIO@$HOST (SID $ORACLE_SID)"
    sshpass -p "$CLAVE" ssh -o StrictHostKeyChecking=no "$USUARIO@$HOST" \
      "$SQLPLUS -s $USUARIO/$CLAVE@$ORACLE_SID" < "$TMP_SQL" "$SALIDA"
  elif command -v expect >/dev/null 2>&1; then
    echo ">> expect: sqlplus remoto en $USUARIO@$HOST (SID $ORACLE_SID)"
    expect <<EOF
set timeout 3600
spawn ssh -o StrictHostKeyChecking=no $USUARIO@$HOST $SQLPLUS -s $USUARIO/$CLAVE@$ORACLE_SID $TMP_SQL $SALIDA
expect {
  "assword:" { send "$CLAVE\r"; exp_continue }
  "yes/no"   { send "yes\r"; exp_continue }
  eof
}
EOF
  else
    echo "ERROR: se pidio HOST= pero este equipo no tiene sshpass ni expect." >&2
    echo "Instale uno (sudo apt install sshpass) o corra el script en el servidor." >&2
    exit 1
  fi
}

BITACORA="$SALIDA/Extraccion_$(date +%Y%m%d_%H%M).log"
if [ -n "$HOST" ]; then
  run_remote 2>&1 | tee "$BITACORA"
else
  run_local  2>&1 | tee "$BITACORA"
fi

# -----------------------------------------------------------------------------
# Manifiesto: conteo real de lineas por CSV (control de que el spool no se cortó).
# -----------------------------------------------------------------------------
MANIFESTO="$SALIDA/manifiesto.txt"
if ! ls "$SALIDA"/*.csv >/dev/null 2>&1; then
  echo "ERROR: no se genero ningun CSV. La consulta fallo o el SQL no llego al" >&2
  echo "       servidor. Revisar $BITACORA antes de reintentar." >&2
  exit 1
fi
{
  echo "# Manifiesto fase 1 - generado $(date '+%Y-%m-%d %H:%M:%S')"
  echo "# Rango: FECHA >= $DESDE"
  echo "# Archivo|filas"
  for f in "$SALIDA"/*.csv; do
    n=$(awk 'END{print NR}' "$f")
    printf '%s|%s\n' "$(basename "$f")" "$n"
  done
} | tee "$MANIFESTO"

echo
echo "=================================================================="
echo " Listo. CSVs en: $SALIDA"
echo " Manifiesto:   $MANIFESTO"
echo " Bitacora:     $BITACORA"
echo
echo " SIGUIENTE: el control de calidad es que las filas de muerte.csv con"
echo " FECHA_M=2026-08-01 sean las mismas que tiene el espejo local. Si"
echo " coinciden, el corte del CSV no perdio nada y se puede pasar a carga."
echo "=================================================================="
