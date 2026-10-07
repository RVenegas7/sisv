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

# Las claves NO van con valor por defecto: se leen del entorno o de
# legancy_conf/credenciales.env (ignorado por git), igual que respaldo_total.sh.
set -a
[ -f "$SCRIPT_DIR/../legancy_conf/credenciales.env" ] && \
  . "$SCRIPT_DIR/../legancy_conf/credenciales.env"
set +a
HOST="${HOST:-${SISV_SSH_HOST:-}}"
USUARIO="${USUARIO:-${SISV_SSH_USUARIO:-}}"
CLAVE="${CLAVE:-${SISV_SSH_CLAVE:-${SSHPASS_ORACLE:-}}}"

DESDE="${DESDE:-01/08/2026}"
SALIDA="${SALIDA:-$SCRIPT_DIR/../salida_mm_mn_$(date +%Y%m%d_%H%M)}"
ORACLE_HOME="${ORACLE_HOME:-/opt/oracle}"
ORACLE_SID="${ORACLE_SID:-lar1}"
SQLPLUS="${SQLPLUS:-/opt/oracle/bin/sqlplus}"
NLS_LANG="${NLS_LANG:-SPANISH_SPAIN.AL32UTF8}"

# OJO, 05/10/2026 (PENDIENTES §22, "Conexión a sqlplus"): en ese servidor NO hay
# alias TNS, y `lar1` es el SID, no el nombre de servicio. Easy Connect solo
# funciona con el SERVICIO `bdlar1` (sale del SID_LIST_LISTENER del listener.ora):
#   usuario/clave a secas  -> ORA-12162
#   @lar1                  -> ORA-12154
#   @//host:1521/lar1     -> ORA-12514
#   @//localhost:1521/bdlar1 -> funciona (02/10/2026)
CONEXION="${CONEXION:-//localhost:1521/bdlar1}"

if [ -z "$HOST" ]; then
  : # modo local: corre en el propio servidor, no hace falta host
elif [ -z "$CLAVE" ]; then
  echo "ERROR: falta la clave de '$USUARIO' (CLAVE / SISV_SSH_CLAVE en" >&2
  echo "       legancy_conf/credenciales.env). Sin ella no hay modo remoto." >&2
  exit 1
fi

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
# OJO, 05/10/2026: el DEFINE del SQL trae las comillas DENTRO de la cadena
# ("""01/08/2026"""), porque SQL*Plus se las quita al sustituir. Si el sed no
# encuentra la linea, aborta: seguir con un DEFINE sin comillas produce
# ORA-01858 y, peor, un CSV con el error adentro que parece bueno.
sed -e "s|DEFINE DESDE = \"'01/08/2026'\"|DEFINE DESDE = \"'$DESDE'\"|" \
    -e "s|__SALIDA__|$DIR_SALIDA_SQL|g" "$SQL" > "$TMP_SQL"
if ! grep -q "DEFINE DESDE = \"'$DESDE'\"" "$TMP_SQL"; then
  echo "ERROR: no se pudo fijar DESDE=$DESDE en el SQL. Revisa la linea DEFINE" >&2
  echo "       (debe ser  DEFINE DESDE = \"'01/08/2026'\")." >&2
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

  echo ">> 3/4 ejecutando sqlplus en $USUARIO@$HOST (servicio $CONEXION)"
  # ORACLE_HOME tiene que VIAJAR al remoto: sin el, sqlplus aborta con
  # "Error 6 initializing SQL*Plus / sp1<lang>.msb not found", que parece un
  # problema de permisos y en realidad es que no encuentra el software (05/10).
  # El TNS no existe en el servidor, por eso la conexion va por Easy Connect.
  if [ "${SIMULAR:-0}" = "1" ]; then
    simular "ssh $USUARIO@$HOST 'export ORACLE_HOME=$ORACLE_HOME ORACLE_SID=$ORACLE_SID; $SQLPLUS -s $USUARIO/\$CLAVE@$CONEXION @$remoto_sql'"
  else
    # OJO, 05/10/2026: el fallo de sqlplus se COMPRUEBA aqui y no se espera del
    # "if ! {...} | tee" de mas abajo. Ese patron tiene dos defectos que juntos
    # hacen que un fallo parezca una extraccion buena:
    #   * con `set -e` + tuberia, el codigo que sale es el de tee (0);
    #   * `set -e` NO actua dentro de un `if`, asi que run_remote seguia de largo
    #     (traia los CSV igual y borraba el remoto) tras el fallo de sqlplus.
    # Por eso el sqlplus va en un `if !` explicito: si falla, se aborta aqui y no
    # se baja nada.
    if ! sshpass -e ssh -o StrictHostKeyChecking=no "$USUARIO@$HOST" \
      "cd '$REMOTE_DIR' && export ORACLE_HOME=$ORACLE_HOME ORACLE_SID=$ORACLE_SID PATH=$ORACLE_HOME/bin:\$PATH NLS_LANG=$NLS_LANG && $SQLPLUS -s '$USUARIO/$CLAVE@$CONEXION' @$remoto_sql"; then
      echo ">> sqlplus fallo en el servidor. No se baja nada." >&2
      # SQL*Plus escribe el error DENTRO del archivo spoolado, no en la consola
      # (TERM/OFF), asi que sin esto el operador solo ve "fallo" y nada mas. Se
      # buscan los CSV con error y se muestran las primeras lineas.
      echo "---- error(es) en el servidor ----" >&2
      sshpass -e ssh -o StrictHostKeyChecking=no "$USUARIO@$HOST" \
        "for f in $REMOTE_DIR/*.csv; do
           if grep -qiE 'ORA-[0-9]{5}|ERROR at line|rows selected' \"\$f\" 2>/dev/null; then
             echo \"### \$(basename \$f)\"; head -8 \"\$f\"
           fi
         done" >&2 || true
      return 1
    fi
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
# deja CSVs a medio escribir. run_remote/run_local ya devuelven el fallo de sqlplus
# (dentro de un `if !` explicito, porque `set -e` no actua en la condicion de un
# `if` y el codigo de un pipeline con tee es el de tee). Aca se recoge ese codigo
# para borrar los parciales: es preferible quedarse sin nada que quedarse con un
# archivo truncado que el manifiesto daria por bueno.
FALLO=0
# `set +e` alrededor del pipeline: con errexit activo, un pipeline que devuelve
# distinto de 0 aborta el script ANTES de llegar al chequeo de abajo.
set +e
{ if [ -n "$HOST" ]; then run_remote; else run_local; fi; } 2>&1 | tee "$BITACORA"
# PIPESTATUS[0] es el del primer comando del pipeline (run_remote/run_local), no el
# de tee. Sin esto, el fallo se pierde y el manifiesto da por buena la extraccion.
FALLO="${PIPESTATUS[0]}"
set -e
if [ "$FALLO" != "0" ]; then
  echo
  echo "ERROR: sqlplus fallo (codigo $FALLO). Se borran los CSV parciales para no" >&2
  echo "       dar por buena una extraccion incompleta. Ver $BITACORA" >&2
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

# Red de seguridad (05/10/2026): SQL*Plus escribe sus mensajes de error y de
# "N rows selected." DENTRO del archivo spoolado, asi que un CSV puede traer un
# ORA-01858 y aun asi existir y "tener filas". El manifiesto solo contaria esas
# lineas como si fueran datos. Se busca el texto de error en cada CSV antes de
# declarar la extraccion buena.
for f in "$SALIDA"/*.csv; do
  if grep -qiE 'ORA-[0-9]{5}|^ERROR at line|rows selected\.$' "$f"; then
    echo "ERROR: $(basename "$f") contiene un error de SQL*Plus dentro del CSV." >&2
    echo "       No es un CSV de datos; se descarta todo para no cargarlo." >&2
    echo "       Primeras lineas:" >&2
    head -5 "$f" | sed 's/^/         /' >&2
    rm -f "$SALIDA"/*.csv
    exit 1
  fi
done
echo " [ OK ]   ningun CSV contiene errores de SQL*Plus"
{
  echo "# Manifiesto fase 1 - generado $(date '+%Y-%m-%d %H:%M:%S')"
  echo "# Rango: FECHA >= $DESDE"
  echo "# Archivo|filas|descartadas"
  for f in "$SALIDA"/*.csv; do
    n=$(awk 'END{print NR}' "$f")
    # "descartadas" son las lineas cuyo numero de columnas no coincide con el
    # encabezado: SPOOL no pone comillas, asi que un texto con salto de linea
    # parte la fila y el cargador la descarta. Contarlas aqui evita que el
    # manifiesto diga "todo bien" mientras se pierde gente.
    cols=$(head -1 "$f" | awk -F';' '{print NF}')
    malas=$(awk -F';' -v n="$cols" 'NR>1 && NF!=n {c++} END {print c+0}' "$f")
    printf '%s|%s|%s\n' "$(basename "$f")" "$n" "$malas"
    if [ "$malas" != "0" ]; then
      echo "# AVISO: $(basename "$f") tiene $malas lineas con $cols columnas distintas"
      echo "#       del encabezado; el cargador las va a descartar."
    fi
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
