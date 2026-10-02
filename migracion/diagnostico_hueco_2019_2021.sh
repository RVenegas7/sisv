#!/usr/bin/env bash
# ==============================================================================
# DIAGNOSTICO del colapso de captura 2019-2021 (PENDIENTES §20).
#
# POR QUE: entre 2019-06 y 2021-07 el sistema de certificados de muerte dejo de
# capturar (11-90 registros/mes en vez de ~1.000) y entre 2019-10 y 2021-11 el de
# nacimientos (5-45 en vez de ~900). En el espejo faltan ~19.700 certificados en
# solo 21 meses. Es la mayor perdida silenciosa del historico y nadie la habia
# detectado: el tablero solo avisa "dejaste de registrar hace N dias", nunca
# "este periodo esta incompleto".
#
# LA PREGUNTA QUE RESPONDE: ¿el Oracle de ORIGEN tiene esos certificados?
#   - Si tiene mas que el espejo -> hay recuperacion posible, igual que la
#     ventana de agosto-septiembre 2026 (migracion/extraer_mm_mn_roto.sh).
#   - Si tiene lo mismo -> nunca se capturaron, la perdida es definitiva y hay
#     que decirlo asi al publicar las series de 2019-2021.
#
# SOLO LECTURA: un SELECT de conteo por mes. No escribe nada, ni en SISMAI, ni en
# TEMP, ni en la cola de EVENTOS_SINC.
#
# Uso:
#   ./migracion/diagnostico_hueco_2019_2021.sh                  # en el servidor
#   HOST=192.168.5.200 ./migracion/diagnostico_hueco_2019_2021.sh   # por ssh
#   DESDE=01/01/2019 HASTA=01/01/2022 ./migracion/diagnostico_hueco_2019_2021.sh
#   SIMULAR=1 ./migracion/diagnostico_hueco_2019_2021.sh         # ver que haria
#   USUARIO=respaldo CLAVE=respaldo ./migracion/diagnostico_hueco_2019_2021.sh
#
# La clave va en SSHPASS y no en la linea de este script, para que no aparezca en
# la tabla de procesos local. En la invocacion de sqlplus si queda escrita, igual
# que en migracion/extraer_mm_mn_roto.sh: en ese servidor no hay alias TNS y el
# SID tiene que ir embebido en la cadena de conexion.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SQL="$SCRIPT_DIR/diagnostico_hueco_2019_2021.sql"

DESDE="${DESDE:-01/01/2018}"
HASTA="${HASTA:-01/01/2022}"
SALIDA="${SALIDA:-$SCRIPT_DIR/../salida_diagnostico_$(date +%Y%m%d_%H%M)}"
HOST="${HOST:-}"
USUARIO="${USUARIO:-respaldo}"
CLAVE="${CLAVE:-respaldo}"
ORACLE_SID="${ORACLE_SID:-lar1}"
SQLPLUS="${SQLPLUS:-/opt/oracle/bin/sqlplus}"
ORACLE_HOME="${ORACLE_HOME:-/opt/oracle}"
NLS_LANG="${NLS_LANG:-SPANISH_SPAIN.AL32UTF8}"
# El environment Oracle tiene que viajar al remoto. Sin ORACLE_HOME en el
# entorno, `sqlplus` no encuentra ni sus propios archivos de mensajes y
# falla con "Error 6 initializing SQL*Plus / sp1<lang>.msb not found",
# que parece de permisos y es otra cosa (02/10).
# Ojo: `ENV_ORACLE NLS_LANG=... $ORDEN` sin `&&` en el medio hace que bash
# intente exportar el comando entero y falla con "not a valid identifier".
# El `;` separa el export de la ejecucion.
ENV_ORACLE="export ORACLE_HOME=$ORACLE_HOME PATH=$ORACLE_HOME/bin:\$PATH;"
# Cadena de conexion de sqlplus. Es Easy Connect (nombre de SERVICIO, no
# SID) porque es la unica forma que funciona aqui, y las tres alternativas
# fallan, todas comprobadas el 02/10/2026:
#   usuario/clave                -> ORA-12162 (no hay nombre de servicio)
#   usuario/clave@lar1           -> ORA-12154 (no hay alias TNS; el
#                                   listener advertido en AGENTS.md)
#   usuario/clave@//host:1521/lar1-> ORA-12514 (lar1 es el SID; el
#                                   SERVICIO se llama bdlar1, segun el
#                                   SID_LIST_LISTENER del listener.ora)
# El listener escucha en 1521 y `lsnrctl status` da lar1 READY. Ojo: con
# Easy Connect el ORACLE_SID del entorno deja de hacer falta para resolver.
SERVICIO="${SERVICIO:-bdlar1}"
HOST_SQL="${HOST_SQL:-localhost:1521}"
CONEXION="${SQLPLUS_CONEXION:-$USUARIO/$CLAVE@//$HOST_SQL/$SERVICIO}"
CSV_SALIDA="salida_diagnostico_2019_2021.txt"

[ -r "$SQL" ] || { echo "ERROR: no existe $SQL" >&2; exit 1; }
command -v awk >/dev/null 2>&1 || { echo "ERROR: falta awk" >&2; exit 1; }

mkdir -p "$SALIDA"
SALIDA="$(cd "$SALIDA" && pwd)"

echo "=================================================================="
echo " Diagnostico del colapso de captura 2019-2021"
echo " Rango:  $DESDE a $HASTA"
echo " Salida: $SALIDA"
if [ -n "$HOST" ]; then
  echo " Servidor: $USUARIO@$HOST (SID $ORACLE_SID) por ssh"
else
  echo " Servidor: local (SID $ORACLE_SID)"
fi
echo " Modo:    SOLO LECTURA (SELECT de conteo)"
echo "=================================================================="

simular() { echo "  [simular] $*"; }

REMOTE_DIR="/tmp/sisv_diagnostico_$$"

if [ -n "$HOST" ]; then
  export SSHPASS="$CLAVE"
  remoto_sql="$REMOTE_DIR/diagnostico_hueco_2019_2021.sql"
  echo ">> 1/3 subiendo el SQL a $REMOTE_DIR"
  if [ "${SIMULAR:-0}" = "1" ]; then
    simular "ssh $USUARIO@$HOST 'mkdir -p $REMOTE_DIR'"
    simular "ssh $USUARIO@$HOST 'cat > $remoto_sql' < $SQL"
  else
    sshpass -e ssh -o StrictHostKeyChecking=no "$USUARIO@$HOST" "mkdir -p '$REMOTE_DIR'"
    sshpass -e ssh -o StrictHostKeyChecking=no "$USUARIO@$HOST" \
      "cat > '$remoto_sql'" < "$SQL"
  fi

  echo ">> 2/3 ejecutando sqlplus en $USUARIO@$HOST"
  # El SID va DENTRO de la cadena de conexion ('usuario/clave@lar1'): en este
  # servidor no hay alias TNS, y un '@lar1' aparte da ORA-12154. El &1/&2 del SQL
  # los rellena sqlplus con los argumentos que van al final.
  ORDEN="$SQLPLUS -s '$CONEXION' @$remoto_sql '$DESDE' '$HASTA'"
  if [ "${SIMULAR:-0}" = "1" ]; then
    simular "ssh $USUARIO@$HOST 'cd $REMOTE_DIR && $ENV_ORACLE NLS_LANG=$NLS_LANG $ORDEN'"
  else
    sshpass -e ssh -o StrictHostKeyChecking=no "$USUARIO@$HOST" \
      "cd '$REMOTE_DIR' && $ENV_ORACLE NLS_LANG=$NLS_LANG $ORDEN" > "$SALIDA/$CSV_SALIDA" 2>&1 || {
      echo "ERROR: fallo sqlplus en remoto." >&2
      cat "$SALIDA/$CSV_SALIDA" >&2 || true
      echo "        No se puede distinguir un error de conexion de uno de SQL en" >&2
      echo "        el remoto: el comando se copio al servidor a proposito." >&2
      exit 1
    }
  fi
  echo ">> 3/3 limpiando $REMOTE_DIR en el servidor"
  if [ "${SIMULAR:-0}" = "1" ]; then
    simular "ssh $USUARIO@$HOST 'rm -rf $REMOTE_DIR'"
  else
    sshpass -e ssh -o StrictHostKeyChecking=no "$USUARIO@$HOST" "rm -rf '$REMOTE_DIR'"
  fi
else
  echo ">> 1/3 ejecutando sqlplus en local"
  ORDEN="$SQLPLUS -s '$CONEXION' @$SQL '$DESDE' '$HASTA'"
  if [ "${SIMULAR:-0}" = "1" ]; then
    simular "cd $SALIDA && NLS_LANG=$NLS_LANG $ORDEN > $CSV_SALIDA"
  else
    ( cd "$SALIDA" && ORACLE_HOME="$ORACLE_HOME" NLS_LANG="$NLS_LANG" \
      $SQLPLUS -s "$CONEXION" "@$SQL" "$DESDE" "$HASTA" \
      > "$CSV_SALIDA" 2>&1 ) || {
      echo "ERROR: fallo sqlplus." >&2
      cat "$SALIDA/$CSV_SALIDA" >&2 || true
      exit 1
    }
  fi
fi

if [ "${SIMULAR:-0}" = "1" ]; then
  echo
  echo "SIMULAR=1: nada se ejecuto. Se habria corrido:"
  echo "  $ORDEN"
  echo "  (rango $DESDE a $HASTA, solo SELECT sobre CERTIFICADO y NAC_RNACIDO)"
  exit 0
fi

[ -s "$SALIDA/$CSV_SALIDA" ] || { echo "ERROR: no hay salida en $SALIDA/$CSV_SALIDA" >&2; exit 1; }

# Se resume minimo/maximo por bloque para responder la pregunta de un
# vistazo, sin obligar a abrir el archivo.
#
# OJO con el parseo: el SQL arma 'bloque|mes|n', pero sqlplus en -S no deja
# los campos como una columna limpia, los alinea con tabulaciones y mete
# espacios (el numero sale como "MESES\t\t2018-01 \t\t    1172"). Por eso
# el separador de campo es [ \t]+ y no '|'. Con -F'|' el resumen salia
# VACIO con los 48 meses bien cargados (02/10), que es lo peor que puede
# pasar: aparenta que no hay datos.
echo
echo "--- resumen por bloque ---"
# El SQL arma la cadena 'bloque|mes|n', pero sqlplus en modo -S no la deja
# como una sola columna: alinea los campos con tabulaciones y mete espacios
# (la columna queda ancha y la barra acaba separada del dato). Por eso el
# resumen se parsea con una expresion regular, no con -F'|'. Con -F'|'
# el resumen salia VACIO aunque la consulta trajera los 48 meses bien
# (02/10), que es el peor fallo posible: parece que no hay datos.
awk -F'[ \t]+' '
  $1=="MESES"       { b="MESES";         mes=$2; n=$3 }
  $1=="NACIMIENTOS" { b="NACIMIENTOS";   mes=$2; n=$3 }
  b!="" && mes ~ /^[0-9]{4}-[0-9]{2}$/ && n ~ /^[0-9]+$/ {
    suma[b]+=n+0; c[b]++
    if (!(b in mn) || n+0 < mn[b]) mn[b]=n+0
    if (n+0 > mx[b])              mx[b]=n+0
    if (!(b in u)  || mes >  u[b]) u[b]=mes
    if (!(b in s)  || mes <  s[b]) s[b]=mes
  }
  END {
    for (k in suma)
      printf "  %-11s %s a %s · %2d meses · min %5d · max %5d · total %6d\n",
             k, s[k], u[k], c[k], mn[k], mx[k], suma[k]
  }
' "$SALIDA/$CSV_SALIDA" | sort

echo
echo "--- meses por debajo de 400 en el rango (senal de colapso) ---"
awk -F'[ \t]+' '
  $1=="MESES"       { b="MESES";       mes=$2; n=$3 }
  $1=="NACIMIENTOS" { b="NACIMIENTOS"; mes=$2; n=$3 }
  b!="" && mes ~ /^[0-9]{4}-[0-9]{2}$/ && n ~ /^[0-9]+$/ && n+0 < 400 {
    printf "  %-11s %s  %5d\n", b, mes, n
  }
' "$SALIDA/$CSV_SALIDA" | head -60 || true

echo
echo "Interpretacion:"
echo "  - Si entre 2019-06 y 2021-07 salen meses con menos de 400 certificados, el"
echo "    ORIGEN tampoco los tiene: la perdida es definitiva y las series 2019-2021"
echo "    se publican como incompletas."
echo "  - Si el origen trae ~1.000 en esos meses, el espejo esta incompleto y hay"
echo "    que reextraer antes de publicar (ver migracion/extraer_mm_mn_roto.sh)."
echo
echo "Detalle mes a mes: $SALIDA/$CSV_SALIDA"
