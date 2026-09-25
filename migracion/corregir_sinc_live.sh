#!/usr/bin/env bash
# ====================================================================
# Correccion en vivo del punto critico (EVENTOS_SINC) contra el
# Oracle 10g de SIS/Lara (srvsis / SID lar1) por SSH.
# SQL: migracion/corregir_sinc_eventos_sinc.sql
# --------------------------------------------------------------------
# IMPORTANTE:
#   - El SQL hace RESGUARDO [A] y RECOMPILACION [B] de forma segura.
#   - La PURGA [D] esta comentada: se habilita manualmente solo cuando
#     el nivel central confirme que la carga del 27-08 llego por otra via.
#   - Ejecutar como usuario con privilegios DBA (recomendado: oracle).
# --------------------------------------------------------------------
# Uso:
#   ./migracion/corregir_sinc_live.sh                  # valores por defecto
#   HOST=192.168.5.200 USUARIO=oracle CLAVE=... el script
# --------------------------------------------------------------------
# Requisitos: estar en la red de la oficina (192.168.5.x) o VPN y tener
# sshpass (o expect). Si no, imprime la orden manual.
# ====================================================================
set -euo pipefail

HOST="${HOST:-192.168.5.200}"
USUARIO="${USUARIO:-oracle}"
CLAVE="${CLAVE:-oracle}"
ORACLE_SID="${ORACLE_SID:-lar1}"
SQLPLUS="${SQLPLUS:-/opt/oracle/bin/sqlplus}"
SQL_FILE="$(cd "$(dirname "$0")/.." && pwd)/migracion/corregir_sinc_eventos_sinc.sql"

if [ ! -r "$SQL_FILE" ]; then
  echo "ERROR: no existe $SQL_FILE" >&2
  exit 1
fi

echo "AVISO: asegurese de que la seccion [D] (TRUNCATE) este comentada"
echo "a menos que el nivel central haya confirmado la recepcion de los"
echo "3,37 M de DOCUMENTO_DENGUE del 27-08 por otra via."
read -r -p "Continuar? [y/N] " CONFIRMA
if [ "${CONFIRMA,,}" != "y" ]; then
  echo "Abortado por el usuario."
  exit 0
fi

if command -v sshpass >/dev/null 2>&1; then
  echo ">> sshpass: corriendo sqlplus remoto en $USUARIO@$HOST (SID $ORACLE_SID)"
  sshpass -p "$CLAVE" ssh -o StrictHostKeyChecking=no "$USUARIO@$HOST" \
    "$SQLPLUS -s $USUARIO/$CLAVE@$ORACLE_SID as sysdba" < "$SQL_FILE"

elif command -v expect >/dev/null 2>&1; then
  echo ">> expect: corriendo sqlplus remoto en $USUARIO@$HOST (SID $ORACLE_SID)"
  expect <<EOF
set timeout 600
spawn ssh -o StrictHostKeyChecking=no $USUARIO@$HOST $SQLPLUS -s $USUARIO/$CLAVE@$ORACLE_SID as sysdba
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
  echo "  # 2) con su sesion SSH en srvsis, corra:"
  echo "  ssh $USUARIO@$HOST"
  echo "  $SQLPLUS -s $USUARIO/$CLAVE@$ORACLE_SID as sysdba @/tmp/corregir_sinc_eventos_sinc.sql"
  exit 2
fi