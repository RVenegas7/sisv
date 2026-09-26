#!/usr/bin/env bash
# ====================================================================
# replicar_controlado_live.sh
# Ejecuta replicar_controlado.sql contra el Oracle 10g de SIS/Lara
# (srvsis / 192.168.5.200, SID lar1, base bdlar1) por SSH.
# --------------------------------------------------------------------
# PLAN B: reconstruye TEMP.T_* desde SISMAI.EVENTOS_SINC porque la
# fase original (plcer1.sql / cr_repli_*.sql) no esta disponible.
# Ver PENDIENTES.md 17.12.
# --------------------------------------------------------------------
# Uso:
#   # 1) INFORME: cero escrituras, no pide autorizacion
#   ./migracion/replicar_controlado_live.sh informe
#
#   # 2) ESCRITURA: exige las 3 condiciones + la frase exacta
#   BACKUP_COLA_OK=SI BACKUP_TEMP_OK=SI CENTRAL_OK=SI \
#     ./migracion/replicar_controlado_live.sh ejecutar
#   AUTORIZAR_PLAN_B_REPLICA_LARA
#
# Condiciones para escribir (el guion se niega a seguir si falta una):
#   BACKUP_COLA_OK=SI  respaldo verificado de SISMAI.EVENTOS_SINC (SHA-256).
#                       Ver respaldo_20260925/eventos_sinc_20260925.csv
#                       (16.741 filas) y PENDIENTES.md 17.2.
#   BACKUP_TEMP_OK=SI  respaldo de las TEMP.T_* que se van a tocar.
#   CENTRAL_OK=SI      el nivel central ya CONFIRMO por escrito la recepcion
#                       del sobre anterior. Sin esto, las filas que quedan en
#                       TEMP de corridas previas se volverian a enviar.
#   ademas: fuera de la ventana del exp diario de las 13:00, y NUNCA junto
#           a SincFich/crear.sql (que DROPea EVENTOS_SINC).
# --------------------------------------------------------------------
# El SQL del repositorio SIEMPRE queda con V_EJECUTAR := 0: este guion
# trabaja sobre una copia temporal y es lo unico que la cambia a 1.
# --------------------------------------------------------------------
# Requisitos: estar en la red de la oficina (192.168.5.x) o VPN, y tener
#   `sshpass` (o `expect`; si no, muestra la orden manual).
# El usuario por defecto (respaldo) NO tiene INSERT ANY TABLE: para
# ejecutar hay que correr esto como DBA, p.ej.:
#   USUARIO=oracle CLAVE=<la de oracle> ./migracion/replicar_controlado_live.sh informe
# --------------------------------------------------------------------
# ANULACION si algo sale mal (no toca la cola):
#   DELETE FROM TEMP.T_<TABLA> WHERE ID IN (... IDs del lote ...);
#   DELETE FROM TEMP.T_EVENTOS  WHERE TABLA = '<TABLA>';
#   COMMIT;
# Use la fecha maxima LOTE_INICIO que imprime la salida.
# ====================================================================
set -euo pipefail

HOST="${HOST:-192.168.5.200}"
USUARIO="${USUARIO:-respaldo}"
CLAVE="${CLAVE:-respaldo}"
ORACLE_SID="${ORACLE_SID:-lar1}"
SQLPLUS="${SQLPLUS:-/opt/oracle/bin/sqlplus}"

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
SQL_LOCAL="$RAIZ/migracion/replicar_controlado.sql"
FECHA="$(date +%Y%m%d_%H%M%S)"
FASE="${1:-}"
FRASE="AUTORIZAR_PLAN_B_REPLICA_LARA"

die() { echo "ERROR: $*" >&2; exit 1; }
info() { echo "  $*"; }

[ -r "$SQL_LOCAL" ] || die "no existe $SQL_LOCAL"
case "$FASE" in
  informe|ejecutar) ;;
  *) die "uso: $0 informe|ejecutar" ;;
esac

# --- 1. La copia temporal es la unica que puede llevar V_EJECUTAR := 1 ------
SQL_TMP="$(mktemp /tmp/replicar_controlado.XXXXXX.sql)"
trap 'rm -f "$SQL_TMP"' EXIT
if [ "$FASE" = "ejecutar" ]; then
  sed 's/^\(  V_EJECUTAR  *PLS_INTEGER *:\?= *\)0;/\11;/' "$SQL_LOCAL" > "$SQL_TMP"
else
  cp "$SQL_LOCAL" "$SQL_TMP"
fi

# --- 2. Condiciones y autorizacion ------------------------------------------
if [ "$FASE" = "ejecutar" ]; then
  echo
  echo "  ================================================================"
  echo "   MODO ESCRITURA sobre TEMP.T_* de $HOST"
  echo "   Escribe en la base de datos de produccion de Lara."
  echo "   NO trunca ni borra SISMAI.EVENTOS_SINC. NO envia nada al central."
  echo "  ================================================================"
  [ "${BACKUP_COLA_OK:-NO}" = "SI" ] || die "falta BACKUP_COLA_OK=SI (respaldo verificado de SISMAI.EVENTOS_SINC)"
  [ "${BACKUP_TEMP_OK:-NO}" = "SI" ] || die "falta BACKUP_TEMP_OK=SI (respaldo de las TEMP.T_* que se van a tocar)"
  [ "${CENTRAL_OK:-NO}"    = "SI" ] || die "falta CENTRAL_OK=SI (el central ya confirmo la recepcion del sobre anterior)"
  printf '  Escriba esta frase exacta y Enter para autorizar:\n    %s\n  > ' "$FRASE"
  read -r respuesta
  [ "$respuesta" = "$FRASE" ] || die "frase incorrecta: no se escribe nada"
  grep -q "V_EJECUTAR .*:= 1;" "$SQL_TMP" || die "no se pudo forzar V_EJECUTAR := 1 en la copia"
  info "autorizado por el operador en esta terminal"
else
  info "modo INFORME: V_EJECUTAR := 0, cero escrituras en la base"
  grep -q "V_EJECUTAR .*:= 0;" "$SQL_TMP" || die "el SQL deberia venir con V_EJECUTAR := 0"
fi

LOG_DIR="$RAIZ/auditoria"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/replicar_controlado_${FASE}_${FECHA}.txt"
info "servidor : $USUARIO@$HOST  (SID $ORACLE_SID)"
info "log      : $LOG"
echo

# --- 3. Correr -------------------------------------------------------------
run_sqlplus() {
  if command -v sshpass >/dev/null 2>&1; then
    sshpass -p "$CLAVE" ssh -T -o StrictHostKeyChecking=no -o ConnectTimeout=15 \
      "$USUARIO@$HOST" "$SQLPLUS -s $USUARIO/$CLAVE@$ORACLE_SID" < "$SQL_TMP"
  elif command -v expect >/dev/null 2>&1; then
    expect <<EOF
set timeout 1800
log_user 1
spawn ssh -T -o StrictHostKeyChecking=no $USUARIO@$HOST $SQLPLUS -s $USUARIO/$CLAVE@$ORACLE_SID
expect {
  "assword:" { send "$CLAVE\r"; exp_continue }
  "yes/no"   { send "yes\r"; exp_continue }
  eof
}
EOF
  else
    echo "No hay sshpass ni expect en este equipo. Instale uno, por ejemplo:"
    echo "  sudo apt install sshpass     # (Debian/Ubuntu)"
    echo "O ejecute manualmente:"
    echo "  # 1) copie el SQL (ya con V_EJECUTAR := $FASE) al servidor:"
    echo "  scp $SQL_TMP $USUARIO@$HOST:/tmp/replicar_controlado.sql"
    echo "  # 2) con su sesion SSH en srvsis, corra:"
    echo "  ssh $USUARIO@$HOST"
    echo "  $SQLPLUS -s $USUARIO/$CLAVE@$ORACLE_SID @/tmp/replicar_controlado.sql"
    exit 2
  fi
}

# El script remoto se identifica en la salida y se graba el log.
{
  echo "--- $(date '+%Y-%m-%d %H:%M:%S')  $USUARIO@$HOST  SID=$ORACLE_SID  fase=$FASE ---"
  run_sqlplus
} 2>&1 | tee "$LOG"

# --- 4. Verificar que no hubo ERROR (el bloque PL/SQL los absorbe) ---------
if grep -qE "ERROR GENERAL:|ERROR en TEMP\.|ERROR en T_EVENTOS" "$LOG"; then
  echo
  die "la salida contiene errores: revise $LOG. NO arme el sobre."
fi

echo
info "OK, sin errores en la salida. Log: $LOG"
if [ "$FASE" = "ejecutar" ]; then
  cat <<'FIN'

  SIGUIENTE PASO (lo hace la aplicacion, no este script):
    - arme el sobre con RoutLar1 / SistemaTransferencia.exe;
    - verifique que lleva los 5 archivos, incluido repllar1.log;
    - anule con el DELETE mostrado arriba si algo salio mal (LOTE_INICIO).
    La cola SISMAI.EVENTOS_SINC quedo INTACTA: el purgado se decide aparte.
FIN
fi
