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
NLS_LANG="${NLS_LANG:-SPANISH_SPAIN.AL32UTF8}"
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
  ORDEN="$SQLPLUS -s '$USUARIO/$CLAVE@$ORACLE_SID' @$remoto_sql '$DESDE' '$HASTA'"
  if [ "${SIMULAR:-0}" = "1" ]; then
    simular "ssh $USUARIO@$HOST 'cd $REMOTE_DIR && NLS_LANG=$NLS_LANG $ORDEN'"
  else
    sshpass -e ssh -o StrictHostKeyChecking=no "$USUARIO@$HOST" \
      "cd '$REMOTE_DIR' && NLS_LANG=$NLS_LANG $ORDEN" > "$SALIDA/$CSV_SALIDA" 2>&1 || {
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
  ORDEN="$SQLPLUS -s '$USUARIO/$CLAVE@$ORACLE_SID' @$SQL '$DESDE' '$HASTA'"
  if [ "${SIMULAR:-0}" = "1" ]; then
    simular "cd $SALIDA && NLS_LANG=$NLS_LANG $ORDEN > $CSV_SALIDA"
  else
    ( cd "$SALIDA" && NLS_LANG="$NLS_LANG" \
      $SQLPLUS -s "$USUARIO/$CLAVE@$ORACLE_SID" "@$SQL" "$DESDE" "$HASTA" \
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

# El SQL devuelve "bloque;mes;n". Se resume minimo/maximo por bloque para
# responder la pregunta de un vistazo, sin obligar a abrir el archivo.
echo
echo "--- resumen por bloque ---"
awk -F'|' '
  /^(MESES|NACIMIENTOS|ULTIMO_DEFUNCION|ULTIMO_NACIMIENTO)\|/ {
    bloque=$1; mes=$2; n=$3
    if (bloque ~ /^ULTIMO/) { printf "  %-22s %s\n", bloque, mes; next }
    if (!(bloque in min) || n+0 < min[bloque]) min[bloque]=n+0
    if (n+0 > max[bloque]) max[bloque]=n+0
    suma[bloque]+=n+0
    n_meses[bloque]++
    if (!(bloque in mes_ultimo) || mes > mes_ultimo[bloque]) mes_ultimo[bloque]=mes
    if (!(bloque in mes_minimo) || mes < mes_minimo[bloque]) mes_minimo[bloque]=mes
  }
  END {
    for (b in suma)
      printf "  %-11s %s a %s · %2d meses · min %5d · max %5d · total %6d\n",
             b, mes_minimo[b], mes_ultimo[b], n_meses[b], min[b], max[b], suma[b]
  }
' "$SALIDA/$CSV_SALIDA" | sort

echo
echo "--- meses por debajo de 400 en el rango (señal de colapso) ---"
awk -F'|' '/^(MESES|NACIMIENTOS)\|/ && $3+0 < 400 { printf "  %-11s %s  %5d\n", $1, $2, $3 }' \
  "$SALIDA/$CSV_SALIDA" || true

echo
echo "Interpretacion:"
echo "  - Si entre 2019-06 y 2021-07 salen meses con menos de 400 certificados, el"
echo "    ORIGEN tampoco los tiene: la perdida es definitiva y las series 2019-2021"
echo "    se publican como incompletas."
echo "  - Si el origen trae ~1.000 en esos meses, el espejo esta incompleto y hay"
echo "    que reextraer antes de publicar (ver migracion/extraer_mm_mn_roto.sh)."
echo
echo "Detalle mes a mes: $SALIDA/$CSV_SALIDA"
