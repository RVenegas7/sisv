#!/usr/bin/env bash
# ====================================================================
# Recompilar los 16 objetos invalidos de la app SISMAI (Oracle 10g,
# srvsis / SID lar1) por SSH.  SQL: migracion/recompilar_16_objetos.sql
# --------------------------------------------------------------------
# Alcance: SOLO los 16 objetos autorizados (PENDIENTES §22.3). NO toca
# la cola EVENTOS_SINC ni recompila el esquema entero.
# Pre-requisito: que TEMP.T_CERTNACI exista; si no, NATALIDAD queda
# invalida por dependencia (el SQL lo avisa en [1]).
# --------------------------------------------------------------------
# Uso:
#   ./migracion/recompilar_16_live.sh             # valores por defecto
#   HOST=192.168.5.200 USUARIO=oracle CLAVE=...    # parametros opcionales
# Requisitos: red de oficina / VPN y sshpass (o expect).
# ====================================================================
set -euo pipefail

HOST="${HOST:-192.168.5.200}"
USUARIO="${USUARIO:-oracle}"
CLAVE="${CLAVE:-oracle}"
ORACLE_SID="${ORACLE_SID:-lar1}"
SQLPLUS="${SQLPLUS:-/opt/oracle/bin/sqlplus}"
SQL_FILE="$(cd "$(dirname "$0")/.." && pwd)/migracion/recompilar_16_objetos.sql"

if [ ! -r "$SQL_FILE" ]; then
  echo "ERROR: no existe $SQL_FILE" >&2
  exit 1
fi

echo "AVISO: esto recompila SOLO los 16 objetos de aplicacion autorizados"
echo "por el usuario (PENDIENTES §22.3). Ejecutar en ventana de mantenimiento,"
echo "fuera del exp diario (13:00) para evitar ORA-01555."
echo "Pre-requisito: TEMP.T_CERTNACI debe existir (el SQL lo verifica en [1])."
read -r -p "Continuar? [y/N] " CONFIRMA
if [ "${CONFIRMA,,}" != "y" ]; then
  echo "Abortado por el usuario."
  exit 0
fi

if command -v sshpass >/dev/null 2>&1; then
  echo ">> sshpass: corriendo sqlplus remoto en $USUARIO@$HOST (SID $ORACLE_SID)"
  sshpass -p "$CLAVE" ssh -o StrictHostKeyChecking=no "$USUARIO@$HOST" \
    "$SQLPLUS -s / as sysdba" < "$SQL_FILE"

elif command -v expect >/dev/null 2>&1; then
  echo ">> expect: corriendo sqlplus remoto en $USUARIO@$HOST (SID $ORACLE_SID)"
  expect <<EOF
set timeout 600
spawn ssh -o StrictHostKeyChecking=no $USUARIO@$HOST $SQLPLUS -s / as sysdba
expect {
  "assword:" { send "$CLAVE\r"; exp_continue }
  "yes/no"   { send "yes\r"; exp_continue }
  eof
}
EOF

else
  echo "No hay sshpass ni expect en este equipo."
  echo
  echo "O ejecute manualmente:"
  echo "  # 1) copie el SQL al servidor:"
  echo "  scp $SQL_FILE $USUARIO@$HOST:/tmp/"
  echo "  # 2) con su sesion SSH en srvsis, corra como usuario oracle:"
  echo "  ssh $USUARIO@$HOST"
  echo "  $SQLPLUS -s / as sysdba @/tmp/recompilar_16_objetos.sql"
  exit 2
fi