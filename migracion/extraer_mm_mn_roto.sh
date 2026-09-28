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
#   ./migracion/extraer_mm_mn_roto.sh                          # en el servidor
#   HOST=192.168.5.200 ./migracion/extraer_mm_mn_roto.sh       # desde casa, por ssh
#   DESDE=01/07/2026 ./migracion/extraer_mm_mn_roto.sh          # ampliar el rango
#   SIMULAR=1 ./migracion/extraer_mm_mn_roto.sh                 # ver que haria, sin correr
#   USUARIO=respaldo CLAVE=respaldo ./migracion/extraer_mm_mn_roto.sh
#
# La clave va en la variable de entorno (SSHPASS), no en la linea de comandos, para
# que no aparezca en la tabla de procesos. Si no defines CLAVE se toma de la que ya
# se usa para el reconocimiento de solo lectura.
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
if [ -n "$HOST" ]; then
  echo " Servidor: $USUARIO@$HOST (SID $ORACLE_SID) por ssh"
else
  echo " Servidor: local (SID $ORACLE_SID)"
fi
echo " Modo:   SOLO LECTURA (SELECT + SPOOL)"
echo "=================================================================="

REMOTE_DIR="/tmp/sisv_extraccion_$$"
# En remoto el SPOOL tiene que apuntar al directorio temporal DEL SERVIDOR, no al
# local, que es el error que hacia que la version anterior no bajara nada.
if [ -n "$HOST" ]; then
  DIR_SALIDA_SQL="$REMOTE_DIR"
  export SSHPASS="$CLAVE"
else
  DIR_SALIDA_SQL="$SALIDA"
fi

# El rango y el directorio de salida se fijan en el SQL, que se genera desde la
# plantilla, para no depender de que el operador edite el archivo a mano el dia de
# la ventana. __SALIDA__ se sustituye por el directorio REAL: el local si se corre
# en el servidor, o el temporal del servidor si se corre desde casa por ssh.
TMP_SQL="$(mktemp)"
trap 'rm -f "$TMP_SQL"' EXIT
sed -e "s|DEFINE DESDE = '01/08/2026'|DEFINE DESDE = '$DESDE'|" \
    -e "s|__SALIDA__|$DIR_SALIDA_SQL|g" "$SQL" > "$TMP_SQL"
if ! grep -q "DEFINE DESDE = '$DESDE'" "$TMP_SQL"; then
  echo "ERROR: no se pudo fijar DESDE=$DESDE en el SQL. Revisa la linea DEFINE." >&2
  exit 1
fi
if grep -q '__SALIDA__' "$TMP_SQL"; then
  echo "ERROR: quedo un __SALIDA__ sin sustituir en el SQL. Revisar la plantilla." >&2
  exit 1
fi

export NLS_LANG

simular() { echo "+ $*"; }

# -----------------------------------------------------------------------------
# Modo local: el script corre en el propio servidor Oracle.
# -----------------------------------------------------------------------------
run_local() {
  if [ "${SIMULAR:-0}" = "1" ]; then
    simular "$SQLPLUS -s '/ as sysdba' @$TMP_SQL"
    return 0
  fi
  # "/ as sysdba" va COMO UN SOLO argumento: si se parte en palabras, sqlplus
  # recibe tres argumentos sueltos y no arranca.
  "$SQLPLUS" -s "/ as sysdba" @"$TMP_SQL"
}

# -----------------------------------------------------------------------------
# Modo remoto: desde casa, por ssh. El SQL se sube al servidor, se ejecuta alli
# (el servidor no tiene el repo) y los CSV se traen de vuelta con un tar por ssh.
# Hay que hacerlo en ese orden: si se pasa la ruta local, el SPOOL apuntaria a un
# directorio que no existe alli y no volveria ningun CSV.
# -----------------------------------------------------------------------------

ssh_do() {
  if [ "${SIMULAR:-0}" = "1" ]; then simular "ssh $USUARIO@$HOST $*"; return 0; fi
  sshpass -e ssh -o StrictHostKeyChecking=no "$USUARIO@$HOST" "$@"
}

run_remote() {
  local remoto_sql="$REMOTE_DIR/extraer.sql"

  echo ">> 1/4 creando $REMOTE_DIR en el servidor"
  ssh_do "rm -rf '$REMOTE_DIR' && mkdir -p '$REMOTE_DIR'"

  echo ">> 2/4 subiendo el SQL (el servidor no tiene el repo)"
  if [ "${SIMULAR:-0}" = "1" ]; then
    simular "ssh $USUARIO@$HOST 'cat > $REMOTE_DIR/extraer.sql' < $TMP_SQL"
  else
    sshpass -e ssh -o StrictHostKeyChecking=no "$USUARIO@$HOST" \
      "cat > '$remoto_sql'" < "$TMP_SQL"
  fi

  echo ">> 3/4 ejecutando sqlplus en $USUARIO@$HOST (SID $ORACLE_SID)"
  # OJO: el SPOOL usa $REMOTE_DIR porque el SQL se genero con ese token.
  if [ "${SIMULAR:-0}" = "1" ]; then
    simular "ssh $USUARIO@$HOST '$SQLPLUS -s $USUARIO/\$CLAVE@$ORACLE_SID @$remoto_sql'"
  else
    sshpass -e ssh -o StrictHostKeyChecking=no "$USUARIO@$HOST" \
      "cd '$REMOTE_DIR' && NLS_LANG=$NLS_LANG $SQLPLUS -s '$USUARIO/$CLAVE@$ORACLE_SID' @$remoto_sql"
  fi

  echo ">> 4/4 trayendo los CSV"
  if [ "${SIMULAR:-0}" = "1" ]; then
    simular "ssh $USUARIO@$HOST 'tar cf - -C $REMOTE_DIR *.csv' | tar xf - -C $SALIDA"
  else
    # El tar viaja por stdout: no deja archivos a medio copiar si se corta el cable.
    sshpass -e ssh -o StrictHostKeyChecking=no "$USUARIO@$HOST" \
      "cd '$REMOTE_DIR' && tar cf - *.csv" | tar xf - -C "$SALIDA"
  fi

  if [ "${LIMPIAR_REMOTO:-1}" = "1" ]; then
    echo ">> limpiando $REMOTE_DIR en el servidor"
    ssh_do "rm -rf '$REMOTE_DIR'"
  else
    echo ">> los CSV quedan en el servidor en $REMOTE_DIR (LIMPIAR_REMOTO=0)"
  fi
}

BITACORA="$SALIDA/Extraccion_$(date +%Y%m%d_%H%M).log"

# El SQL aborta con WHENEVER SQLERROR EXIT, asi que un fallo a mitad de consulta
# deja CSVs a medio escribir. Con pipefail el pipeline devuelve el fallo de
# sqlplus, y aqui se borran los parciales: es preferible quedarse sin nada que
# quedarse con un archivo truncado que el manifiesto daria por bueno.
if ! { if [ -n "$HOST" ]; then run_remote; else run_local; fi; } 2>&1 | tee "$BITACORA"; then
  echo
  echo "ERROR: sqlplus fallo. Se borran los CSV parciales para no dar por buena" >&2
  echo "       una extraccion incompleta. Ver $BITACORA" >&2
  rm -f "$SALIDA"/*.csv
  if [ -n "$HOST" ] && [ "${SIMULAR:-0}" != "1" ]; then
    sshpass -e ssh -o StrictHostKeyChecking=no "$USUARIO@$HOST" "rm -rf '$REMOTE_DIR'" || true
  fi
  exit 1
fi

# -----------------------------------------------------------------------------
# Manifiesto: conteo real de lineas por CSV (control de que el spool no se cortó).
# -----------------------------------------------------------------------------
MANIFESTO="$SALIDA/manifiesto.txt"
if [ "${SIMULAR:-0}" = "1" ]; then
  echo
  echo " SIMULAR=1: no se ejecuto nada contra el servidor. Esta era la simulacion."
  exit 0
fi
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
