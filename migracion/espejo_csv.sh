#!/usr/bin/env bash
# ====================================================================
# ESPEJO DEL ORACLE 10g -> CSV (SOLO LECTURA) — 30/09/2026
# --------------------------------------------------------------------
# Por que CSV y no el .dmp de `exp`:
#   1. `exp` necesita la clave de una cuenta de BASE, y la unica disponible
#      (la del SO) solo abre el SSH: en la base da ORA-01017. Las claves de
#      SISMAI/TEMP/HISTORICO estan ofuscadas en SaludCor/ActualizaS/System.cfg
#      del share, y no es seguro descifrar credenciales de produccion para
#      armar un respaldo. `sqlplus / as sysdba` no necesita ninguna.
#   2. Un .dmp es binario de Oracle: PostgreSQL no lo puede leer
#      (AGENTS.md / PENDIENTES 17.8). El CSV si.
#   3. Con `sqlplus / as sysdba` (autenticacion del SO) no hace falta
#      ninguna clave de base, y tampoco se toca la produccion.
# El .dmp queda como pendiente para cuando el DBA entregue una clave.
#
# Encoding: la base es WE8ISO8859P1 (verificado con
# NLS_DATABASE_PARAMETERS el 30/09/2026, no WE8MSWIN1252 como decia
# AGENTS.md). PostgreSQL es UTF-8, asi que cada sesion fuerza
#   ALTER SESSION SET NLS_LANG='AL32UTF8'
# para que el spool salga en UTF-8 y el COPY no lo rechace.
#
# Es SOLO LECTURA: unicamente SELECT y SPOOL. No toca SISMAI, ni
# EVENTOS_SINC, ni TEMP. Se puede correr con usuarios capturando.
#
# Uso:
#   ./migracion/espejo_csv.sh                # ejecuta
#   SIMULAR=1 ./migracion/espejo_csv.sh      # solo el plan, no extrae
#   ESQUEMAS="SISMAI" ./migracion/espejo_csv.sh
# ====================================================================
set -uo pipefail

HOST="${HOST:-192.168.5.200}"
USUARIO="${USUARIO:-oracle}"
# La clave del SO NO va con valor por defecto: se lee del entorno o de
# legancy_conf/credenciales.env (ignorado por git).
set -a
[ -f "$(dirname "$0")/../legancy_conf/credenciales.env" ] && \
  . "$(dirname "$0")/../legancy_conf/credenciales.env"
set +a
CLAVE="${CLAVE:-${SSHPASS_ORACLE:-}}"
if [ -z "$CLAVE" ]; then
  echo "Falta la clave SSH del usuario '$USUARIO'."
  echo "Defina CLAVE en el entorno o SSHPASS_ORACLE en legancy_conf/credenciales.env (ignorado por git)."
  exit 1
fi
ORACLE_HOME="/opt/oracle"
ORACLE_SID="lar1"
ESQUEMAS="${ESQUEMAS:-SISMAI TEMP HISTORICO INBDLAR1}"
SIMULAR="${SIMULAR:-0}"
# Filas por paquete: agrupa en un solo INSERT para que el spool no
# crezca de forma absurda. 5000 es el mismo corte que usa el propio
# legacy en sus pl*.sql.
LOTE="${LOTE:-5000}"
# Tablas a las que no se les saca el conteo previo: son las colas de
# replicacion y las de auditoria de la app, que no aportan al espejo y
# son las mas grandes.
SIN_CONTEO="'EVENTOS_SINC','EVENTOS_DBLINK','EVENTOS_RESP','ERRORES_SINC'"

FECHA="$(date +%Y%m%d)"
HORA="$(date +%H%M)"
DIR="/home/oracle/espejo_csv_${FECHA}_${HORA}"
LOG_LOCAL="/tmp/opencode/espejo_csv_${FECHA}_${HORA}.log"

sxs() { sshpass -p "$CLAVE" ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 "$USUARIO@$HOST" "$@"; }

# "SISMAI TEMP" -> "'SISMAI','TEMP'". El separador de la lista de
# esquemas tiene que ser la coma de SQL, no un espacio: por eso no se
# puede pasar $ESQUEMAS crudo dentro del IN (...).
LISTA_IN="$(echo $ESQUEMAS | sed "s/\([A-Z0-9_]\{1,\}\)/'\1'/g; s/ /,/g")"

echo "=================================================================="
echo " Espejo Oracle -> CSV — $FECHA $HORA"
echo " servidor: $HOST ($USUARIO)   esquemas: $ESQUEMAS"
echo " salida:   $DIR"
echo "=================================================================="

# --- 0. Pre-vuelo -----------------------------------------------------
echo
echo ">> 0. Pre-vuelo"
if [ -n "$(sxs "ps -ef | grep -E '[e]xp |[e]xpdp' | grep -v grep" 2>/dev/null)" ]; then
  echo " [FALLO] hay un export corriendo: no se lee la base a medio respaldar"
  exit 1
fi
echo " [ OK ]   no hay ningun exp/expdp corriendo"

if [ -d "$DIR" ]; then
  echo " [FALLO] $DIR ya existe; no se pisa un espejo a medio hacer"
  exit 1
fi
sxs "mkdir -p $DIR" || { echo " [FALLO] no se pudo crear $DIR"; exit 1; }
echo " [ OK ]   creado $DIR"

# --- 1. Volcado de control: el numero de filas de cada tabla ----------
# Son ~520 consultas de un segundo y dan el contraste para validar la
# carga despues. Sin esto no hay forma de saber si algo se perdio.
echo
echo ">> 1. Volcado de control (conteo por tabla)"
sxs "export ORACLE_HOME=$ORACLE_HOME ORACLE_SID=$ORACLE_SID PATH=$ORACLE_HOME/bin:\$PATH NLS_LANG=AMERICAN_AMERICA.AL32UTF8; sqlplus -S / as sysdba <<'EOF'
SET PAGESIZE 0 FEEDBACK OFF HEADING OFF TRIMSPOOL ON LINESIZE 300
SPOOL $DIR/conteo_tablas.csv
-- LAST_DDL_TIME no existe en ALL_TABLES de 10.1 (comprobado el
-- 30/09: ORA-00904); hay que sacarlo de ALL_OBJECTS.
SELECT T.OWNER||'|'||T.TABLE_NAME||'|'||NVL(TO_CHAR(T.NUM_ROWS),'?')||'|'||
       NVL(TO_CHAR(O.LAST_DDL_TIME,'YYYY-MM-DD HH24:MI'),'?')
  FROM ALL_TABLES T
  LEFT JOIN ALL_OBJECTS O
    ON O.OWNER = T.OWNER AND O.OBJECT_NAME = T.TABLE_NAME
   AND O.OBJECT_TYPE = 'TABLE'
 WHERE T.OWNER IN ($LISTA_IN)
 ORDER BY T.OWNER, T.TABLE_NAME;
SPOOL OFF
EXIT;
EOF" 2>&1 | tail -3
CONT="$(sxs "wc -l < $DIR/conteo_tablas.csv" 2>/dev/null | tr -dc '0-9')"
if [ -n "${CONT:-}" ] && [ "$CONT" -ge 400 ]; then
  echo " [ OK ]   conteo_tablas.csv con $CONT tablas"
else
  # Un "OK" con 0 filas es peor que un fallo: el 30/09 asi se reporto un
  # sqlplus que ni se pudo conectar. Si el conteo no cuadra con las ~520
  # tablas no-system, algo fallo y hay que verlo antes de seguir.
  echo " [FALLO] conteo_tablas.csv tiene ${CONT:-0} lineas (se esperaban ~520)."
  sxs "head -3 $DIR/conteo_tablas.csv 2>/dev/null" 2>/dev/null | sed 's/^/           /'
  exit 1
fi

# --- 2. Volcado de control: DDL --------------------------------------
echo
echo ">> 2. Volcado de la estructura (una vez por esquema)"
sxs "export ORACLE_HOME=$ORACLE_HOME ORACLE_SID=$ORACLE_SID PATH=$ORACLE_HOME/bin:\$PATH NLS_LANG=AMERICAN_AMERICA.AL32UTF8; sqlplus -S / as sysdba <<'EOF'
SET LINESIZE 32767 PAGESIZE 0 LONG 100000 LONGCHUNKSIZE 32767 TRIMSPOOL ON FEEDBACK OFF HEADING OFF
SPOOL $DIR/estructura.sql
-- GET_DDL en un SELECT puro, sin DBMS_OUTPUT: el buffer de DBMS_OUTPUT
-- es acumulativo y en 10.1 esta capado a 32767 (UNLIMITED no existe),
-- asi que un bloque con las 525 tablas revienta con ORA-06512 a la
-- tercera. Comprobado el 30/09: por SELECT directo salen las 82 de TEMP
-- completas y por PL/SQL solo 29.
SELECT DBMS_METADATA.GET_DDL('TABLE', TABLE_NAME, OWNER)||';'
  FROM ALL_TABLES WHERE OWNER IN ($LISTA_IN) ORDER BY OWNER, TABLE_NAME;
SPOOL OFF
EXIT;
EOF" 2>&1 | tail -3
DDL="$(sxs "wc -l < $DIR/estructura.sql" 2>/dev/null | tr -dc '0-9')"
# El contraste es de CREATE TABLE contra el conteo de arriba: comparar
# solo lineas deja pasar un DDL a medias (el 30/09 dio 324 lineas y solo
# 29 tablas de 525, porque el bloque PL/SQL revanto a la tercera).
CREATES="$(sxs "grep -c 'CREATE TABLE' $DIR/estructura.sql" 2>/dev/null | tr -dc '0-9')"
if [ "${CREATES:-0}" = "$CONT" ]; then
  echo " [ OK ]   estructura.sql con ${CREATES} CREATE TABLE (=$CONT tablas)"
else
  echo " [FALLO] estructura.sql trae ${CREATES:-0} CREATE TABLE pero el conteo dice $CONT."
  exit 1
fi

if [ "$SIMULAR" = "1" ]; then
  echo
  echo "== SIMULACION: no se extrae nada. Se extraerian estos CSV: =="
  sxs "export ORACLE_HOME=$ORACLE_HOME ORACLE_SID=$ORACLE_SID PATH=$ORACLE_HOME/bin:\$PATH NLS_LANG=AMERICAN_AMERICA.AL32UTF8; sqlplus -S / as sysdba <<'EOF'
SET PAGESIZE 0 FEEDBACK OFF HEADING OFF
SELECT OWNER||'/'||TABLE_NAME||'.csv  (~'||NVL(NUM_ROWS,0)||' filas)'
  FROM ALL_TABLES WHERE OWNER IN ($LISTA_IN)
 ORDER BY NVL(NUM_ROWS,0) DESC;
EXIT;
EOF" 2>&1 | head -30
  echo
  echo "== Fin de la simulacion =="
  exit 0
fi

# --- 3. Extraccion de datos ------------------------------------------
# Un .sql generico y un sqlplus por tabla, con tope de 4 simultaneos:
# extraer 525 tablas a la vez reventaria el UNDO de 1G y degradaria el
# servicio de captura.
#
# Ajustes de sqlplus que NO son opcionales (sin ellos el CSV no se puede
# leer, comprobado el 30/09 con T_USUARIOS):
#   SET WRAP OFF / TAB OFF  -> sin esto sqlplus parte una fila larga en
#       varias lineas y mete relleno de espacios, y una fila acaba siendo
#       varias: el COPY de PostgreSQL no cuadra el numero de columnas.
#   SET TRIMSPOOL ON        -> quita el relleno a la derecha.
#   SET COLSEP ','          -> separador de columna coma, no espacio.
#   SET NUMWIDTH 20         -> los NUMBER no salen con notacion cientifica.
# NLS_LANG va en el ENTORNO del proceso: `ALTER SESSION SET NLS_LANG` no
# existe en 10g (ORA-00922, visto el 30/09).
# Los parametros van con DEFINE y NO con DEFINE OFF: sqlplus pide por
# stdin lo que no este definido, y en un proceso en segundo plano eso es
# EOF (ORA-00942 con el esquema literal).
echo
echo ">> 3. Extrayendo datos (4 sqlplus simultaneos)"
GENERADOR="/home/oracle/gen_espejo_${HORA}.sql"
sxs "cat > $GENERADOR <<'GEN'
SET PAGESIZE 0 FEEDBACK OFF HEADING OFF LINESIZE 32767
SET ESCAPE ON VERIFY OFF ECHO OFF
SET COLSEP ','
SET NUMWIDTH 20
SET WRAP OFF
SET TAB OFF
SET TRIMSPOOL ON
SET CONCAT OFF
DEFINE SAL=&1
DEFINE ESQ=&2
DEFINE TAB=&3
SPOOL &SAL
SELECT * FROM \"&ESQ\".\"&TAB\";
SPOOL OFF
EXIT;
GEN
echo generador listo" 2>&1 | tail -2

LANZADOS=0
while read -r ESQ TAB; do
  [ -z "$TAB" ] && continue
  # Se salta lo que no aporta al espejo (colas de replicacion).
  case "$TAB" in
    EVENTOS_SINC|EVENTOS_DBLINK|EVENTOS_RESP) continue ;;
  esac
  # Orden de los parametros segun los DEFINE del generador:
  # SAL=&1 (ruta del csv), ESQ=&2, TAB=&3.
  sxs "export ORACLE_HOME=$ORACLE_HOME ORACLE_SID=$ORACLE_SID PATH=$ORACLE_HOME/bin:\$PATH NLS_LANG=AMERICAN_AMERICA.AL32UTF8; nohup sqlplus -S / as sysdba @$GENERADOR $DIR/${ESQ}_${TAB}.csv $ESQ $TAB > $DIR/${ESQ}_${TAB}.nohup 2>&1 &" 2>/dev/null
  LANZADOS=$((LANZADOS + 1))
  # Con 4 a la vez: por encima de eso el UNDO de 1G se satura (§17.7
  # ya lo registro: 429.500 filas de prueba dieron "log buffer space").
  if [ $((LANZADOS % 4)) -eq 0 ]; then
    # Espera a que baje de 4 antes de lanzar el siguiente grupo.
    while [ "$(sxs "pgrep -c sqlplus" 2>/dev/null | tr -dc '0-9')" -ge 4 ]; do sleep 10; done
  fi
done < <(sxs "export ORACLE_HOME=$ORACLE_HOME ORACLE_SID=$ORACLE_SID PATH=$ORACLE_HOME/bin:\$PATH NLS_LANG=AMERICAN_AMERICA.AL32UTF8; sqlplus -S / as sysdba <<'EOF'
SET PAGESIZE 0 FEEDBACK OFF HEADING OFF TRIMSPOOL ON
SELECT OWNER||' '||TABLE_NAME FROM ALL_TABLES WHERE OWNER IN ($LISTA_IN) ORDER BY OWNER, TABLE_NAME;
EXIT;
EOF" 2>/dev/null)

echo "   lanzadas $LANZADOS tablas"
echo "   (esto tarda 2-4 h; se puede dejar corriendo y volver)"
echo
echo ">> Estado en vivo:  sxs 'ls $DIR/*.csv | wc -l; du -sh $DIR'"
echo ">> Bitacora del cliente: $LOG_LOCAL"
echo
echo "=================================================================="
echo " Extraccion en curso. Para seguirla:"
echo "   ssh $USUARIO@$HOST   y despues:  du -sh $DIR ; ls $DIR/*.csv | wc -l"
echo "=================================================================="
