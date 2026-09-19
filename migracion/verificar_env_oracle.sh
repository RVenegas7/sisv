#!/bin/bash
# Verificación de entorno Oracle 10g en openSUSE 11.4 (usuario: oracle)
set -u

echo "=== Entorno Oracle (openSUSE 11.4) ==="
for f in ~/.bash_profile ~/.profile ~/.bashrc /etc/profile.d/oracle.sh; do
  [ -f "$f" ] && . "$f" 2>/dev/null
done

echo "ORACLE_HOME=${ORACLE_HOME:-<no definido>}"
echo "ORACLE_SID=${ORACLE_SID:-<no definido>}"
echo "NLS_LANG=${NLS_LANG:-<no definido>}"
echo "PATH=$PATH"

SQLPLUS=$(command -v sqlplus 2>/dev/null)
echo "sqlplus: ${SQLPLUS:-NO ENCONTRADO en PATH}"

if [ -z "${ORACLE_HOME:-}" ] && [ -n "$SQLPLUS" ]; then
  ORACLE_HOME="$(dirname "$(dirname "$SQLPLUS")")"
  echo "ORACLE_HOME inferido: $ORACLE_HOME"
fi

if [ -n "${ORACLE_HOME:-}" ] && [ -x "$ORACLE_HOME/bin/sqlplus" ]; then
  "$ORACLE_HOME/bin/sqlplus" -version 2>&1 | head -2
  echo "Prueba de conexión:"
  echo "SELECT 1 FROM dual;" | "$ORACLE_HOME/bin/sqlplus" -S / as sysdba 2>&1 | head -4
else
  echo "ADVERTENCIA: sqlplus no disponible."
  echo "Busca con: find /opt /usr /home -name sqlplus 2>/dev/null"
  echo "Y exporta: export ORACLE_HOME=...; export ORACLE_SID=...; export NLS_LANG=AMERICAN_AMERICA.WE8MSWIN1252"
fi
exit 0