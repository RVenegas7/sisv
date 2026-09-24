#!/usr/bin/env bash
# ====================================================================
# Ejecuta la verificacion en vivo del punto critico (EVENTOS_SINC)
# contra el Oracle 10g de SIS/Lara (srvsis / SID lar1) por SSH.
# SQL: migracion/verificar_sinc_eventos_sinc.sql (solo lecturas)
# --------------------------------------------------------------------
# Uso:
#   ./migracion/verificar_sinc_live.sh                 # usa valores por defecto
#   HOST=192.168.5.200 USUARIO=respaldo CLAVE=... ./script.sh
# --------------------------------------------------------------------
# Requisitos: estar en la red de la oficina (192.168.5.x) o VPN.
#   - Si tiene `sshpass` instalado, corre directo.
#   - Si no, intenta con `expect`; si tampoco, muestra la orden manual.
# ====================================================================
set -euo pipefail

HOST="${HOST:-192.168.5.200}"
USUARIO="${USUARIO:-respaldo}"
CLAVE="${CLAVE:-respaldo}"
ORACLE_SID="${ORACLE_SID:-lar1}"
SQLPLUS="${SQLPLUS:-/opt/oracle/bin/sqlplus}"
SQL_FILE="$(cd "$(dirname "$0")/.." && pwd)/migracion/verificar_sinc_eventos_sinc.sql"

if [ ! -r "$SQL_FILE" ]; then
  echo "ERROR: no existe $SQL_FILE" >&2
  exit 1
fi

if command -v sshpass >/dev/null 2>&1; then
  echo ">> sshpass: corriendo sqlplus remoto en $USUARIO@$HOST (SID $ORACLE_SID)"
  sshpass -p "$CLAVE" ssh -o StrictHostKeyChecking=no "$USUARIO@$HOST" \
    "$SQLPLUS -s $USUARIO/$CLAVE@$ORACLE_SID" < "$SQL_FILE"

elif command -v expect >/dev/null 2>&1; then
  echo ">> expect: corriendo sqlplus remoto en $USUARIO@$HOST (SID $ORACLE_SID)"
  expect <<EOF
set timeout 120
spawn ssh -o StrictHostKeyChecking=no $USUARIO@$HOST $SQLPLUS -s $USUARIO/$CLAVE@$ORACLE_SID
expect {
  "assword:" { send "$CLAVE\r"; exp_continue }
  "yes/no"   { send "yes\r"; exp_continue }
  eof
}
EOF

else
  echo "No hay sshpass ni expect en este equipo. Instale uno, por ejemplo:"
  echo "  sudo apt install sshpass     # (Debian/Ubuntu)"
  echo
  echo "O ejecute manualmente:"
  echo "  # 1) copie el SQL al servidor:"
  echo "  scp $SQL_FILE $USUARIO@$HOST:/tmp/"
  echo "  # 2) con su sesion SSH en srvsis, corra:"
  echo "  ssh $USUARIO@$HOST"
  echo "  $SQLPLUS -s $USUARIO/$CLAVE@$ORACLE_SID @/tmp/verificar_sinc_eventos_sinc.sql"
  exit 2
fi