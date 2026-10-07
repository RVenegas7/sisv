#!/usr/bin/env bash
# ====================================================================
# Recompilar los 16 objetos invalidos de la app SISMAI (Oracle 10g,
# 192.168.5.200 / SID lar1).  SQL: migracion/recompilar_16_objetos.sql
# --------------------------------------------------------------------
# Alcance: SOLO los 16 objetos autorizados (PENDIENTES §22.3). NO toca
# la cola SISMAI.EVENTOS_SINC ni recompila el esquema entero.
#
# El SQL NO aborta si falta TEMP.T_CERTNACI: avisa en [1], recompila los
# otros 15 y deja NATALIDAD invalida por dependencia (ORA-04063), que es
# justo lo que hay que ver antes de ir a crear esa tabla.
# --------------------------------------------------------------------
# Uso:
#   ./migracion/recompilar_16_live.sh --preparar
#       Deja el SQL copiado en el servidor (canal `respaldo`) e imprime
#       el comando exacto para correr en la CONSOLA como usuario oracle.
#       No escribe nada en Oracle: es el modo por defecto.
#
#   ./migracion/recompilar_16_live.sh --remoto
#       Ejecuta el SQL por SSH. Necesita un usuario con DBA (hoy NO hay
#       ninguno accesible: `respaldo` solo tiene ALTER ANY INDEX /
#       RESTRICTED SESSION / UNLIMITED TABLESPACE).
#       USUARIO=... CLAVE=... [sin clave si hay llave SSH]
#
#   --sin-verificar-respaldo   Solo si el DBA ya valido el restore point
#                              a mano (verificacion automatica por logs).
# ====================================================================
set -euo pipefail

MODO="preparar"
VERIFICAR_RESPALDO=1
while [ $# -gt 0 ]; do
  case "$1" in
    --preparar) MODO="preparar"; shift ;;
    --remoto)   MODO="remoto";   shift ;;
    --sin-verificar-respaldo) VERIFICAR_RESPALDO=0; shift ;;
    *) echo "Opción desconocida: $1" >&2; exit 64 ;;
  esac
done

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
SQL_FILE="$RAIZ/migracion/recompilar_16_objetos.sql"
SQLPLUS="${SQLPLUS:-/opt/oracle/bin/sqlplus}"
ORACLE_HOME="${ORACLE_HOME:-/opt/oracle}"
ORACLE_SID="${ORACLE_SID:-lar1}"
HOST="${HOST:-192.168.5.200}"
USUARIO="${USUARIO:-}"
CLAVE="${CLAVE:-}"
DESTINO="${DESTINO:-/home/respaldo/recompilar_16_objetos.sql}"

if [ ! -r "$SQL_FILE" ]; then
  echo "ERROR: no existe $SQL_FILE" >&2
  exit 1
fi

leer_credenciales() {
  local f="$RAIZ/legancy_conf/credenciales.env"
  [ -r "$f" ] || return 1
  set -a; . "$f"; set +a
  HOST="${SISV_SSH_HOST:-$HOST}"
  return 0
}

ssh_respaldo() {
  local cmd="$1"
  if [ -n "${SISV_SSH_CLAVE:-}${SSHPASS:-}" ]; then
    SSHPASS="${SISV_SSH_CLAVE:-$SSHPASS}" sshpass -e ssh -o StrictHostKeyChecking=accept-new \
      "${SISV_SSH_USUARIO:-respaldo}@$HOST" "$cmd"
  else
    ssh -o StrictHostKeyChecking=accept-new "${SISV_SSH_USUARIO:-respaldo}@$HOST" "$cmd"
  fi
}

verificar_respaldo() {
  local salida
  salida="$(ssh_respaldo '
    D=$(ls -dt ~/respaldo_* 2>/dev/null | head -1)
    if [ -z "$D" ]; then echo "NO_HAY_RESPALDO"; exit 0; fi
    echo "DIR=$D"
    for f in "$D"/exp_*.log; do
      [ -r "$f" ] || continue
      if grep -qiE "terminated successfully|terminado correctamente" "$f"; then
        echo "LOG_OK=$(basename "$f")"
      else
        echo "LOG_MAL=$(basename "$f")"
      fi
    done
    ls -l "$D"/*.dmp 2>/dev/null | wc -l | sed "s/^/DMP=/"
  ')"
  echo "$salida"
  local logs_ok logs_mal dmps dir
  logs_ok="$(printf '%s\n' "$salida" | grep -c '^LOG_OK=' || true)"
  logs_mal="$(printf '%s\n' "$salida" | grep -c '^LOG_MAL=' || true)"
  dmps="$(printf '%s\n' "$salida" | sed -n 's/^DMP=//p' | head -1)"
  dir="$(printf '%s\n' "$salida" | sed -n 's/^DIR=//p' | head -1)"
  if [ "$logs_ok" -eq 0 ] || [ "$logs_mal" -gt 0 ] || [ "${dmps:-0}" -lt 4 ]; then
    echo "FALLA: el último respaldo ($dir) no pasa la verificación" >&2
    echo "  logs con fin correcto: $logs_ok | logs con error: $logs_mal | .dmp: ${dmps:-0} (se esperan 4)" >&2
    return 1
  fi
  echo "Respaldo verificado: $dir ($dmps .dmp, $logs_ok logs con fin correcto)"
  return 0
}

leer_credenciales || true

if [ "$MODO" = "preparar" ]; then
  cat <<EOF
====================================================================
 MODO PREPARAR — no se escribe nada en Oracle
====================================================================
 Se va a copiar el SQL al servidor y a verificar el último respaldo.

EOF
  if [ "$VERIFICAR_RESPALDO" = 1 ]; then
    verificar_respaldo || { echo; echo "Use --sin-verificar-respaldo si el DBA ya lo validó a mano."; exit 1; }
  else
    echo "(verificación de respaldo omitida por --sin-verificar-respaldo)"
  fi
  echo
  echo ">> Copiando $SQL_FILE -> $HOST:$DESTINO"
  if [ -n "${SISV_SSH_CLAVE:-}${SSHPASS:-}" ]; then
    SSHPASS="${SISV_SSH_CLAVE:-$SSHPASS}" sshpass -e scp -o StrictHostKeyChecking=accept-new \
      "$SQL_FILE" "${SISV_SSH_USUARIO:-respaldo}@$HOST:$DESTINO"
  else
    scp -o StrictHostKeyChecking=accept-new "$SQL_FILE" "${SISV_SSH_USUARIO:-respaldo}@$HOST:$DESTINO"
  fi
  echo ">> Copiado."
  echo
  cat <<EOF
====================================================================
 AHORA, EN LA CONSOLA DEL SERVIDOR (192.168.5.200), como 'oracle':
====================================================================
   su - oracle
   export ORACLE_HOME=/opt/oracle ORACLE_SID=lar1
   export NLS_LANG=SPANISH_SPAIN.AL32UTF8
   cp $DESTINO /tmp/recompilar_16_objetos.sql
   $SQLPLUS -s / as sysdba @/tmp/recompilar_16_objetos.sql | tee ~/recompilar_16_$(date +%Y%m%d_%H%M).log

 Veredicto = la sección [5] del log: 0 invalidos es el éxito.
 Si NATALIDAD queda invalida, es por TEMP.T_CERTNACI (sección [1]).
EOF
  exit 0
fi

# ---- MODO REMOTO: hace falta un usuario con DBA ----
if [ -z "$USUARIO" ]; then
  echo "ERROR: --remoto necesita USUARIO=<cuenta con DBA> (no existe ninguna accesible)." >&2
  echo "       Use --preparar y corra el comando en la consola del servidor." >&2
  exit 64
fi
if [ "$VERIFICAR_RESPALDO" = 1 ]; then
  verificar_respaldo || { echo "Use --sin-verificar-respaldo si el DBA ya lo validó a mano."; exit 1; }
fi

SHPASS=()
SSH_OPTS=(-o StrictHostKeyChecking=accept-new -o BatchMode=yes)
if [ -n "$CLAVE" ]; then
  command -v sshpass >/dev/null 2>&1 || { echo "ERROR: dio CLAVE pero no hay sshpass." >&2; exit 69; }
  SSHPASS="$CLAVE" sshpass -e ssh "${SSH_OPTS[@]}" "$USUARIO@$HOST" \
    "export ORACLE_HOME=$ORACLE_HOME ORACLE_SID=$ORACLE_SID NLS_LANG=SPANISH_SPAIN.AL32UTF8; $SQLPLUS -s / as sysdba" < "$SQL_FILE"
else
  echo ">> AVISO: sin CLAVE; se intenta con llave pública (BatchMode)."
  ssh "${SSH_OPTS[@]}" "$USUARIO@$HOST" \
    "export ORACLE_HOME=$ORACLE_HOME ORACLE_SID=$ORACLE_SID NLS_LANG=SPANISH_SPAIN.AL32UTF8; $SQLPLUS -s / as sysdba" < "$SQL_FILE"
fi