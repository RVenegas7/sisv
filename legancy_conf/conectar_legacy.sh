#!/bin/bash
# =============================================================================
# Conecta al Oracle 10g del sistema legacy SIS/LAR1 usando credenciales.env
# (archivo local NO versionado; copiar/renombrar desde credenciales.env.ejemplo).
# Uso:  ./conectar_legacy.sh          (abre sqlplus contra la BD del servidor)
# =============================================================================
set -u

DIR="$(cd "$(dirname "$0")" && pwd)"
ENV="$DIR/credenciales.env"

if [ ! -f "$ENV" ]; then
  echo "Falta $ENV."
  echo "Copie legancy_conf/credenciales.env.ejemplo -> legancy_conf/credenciales.env y complételo."
  exit 1
fi

set -a
# shellcheck disable=SC1090
. "$ENV"
set +a

echo "== Entorno Oracle (según credenciales.env) =="
echo "ORACLE_HOME=${ORACLE_HOME:-<no definido>}"
echo "ORACLE_SID=${ORACLE_SID:-<no definido>}"
echo "NLS_LANG=${NLS_LANG:-<no definido>}"

SQLPLUS="$ORACLE_HOME/bin/sqlplus"
[ -x "$SQLPLUS" ] || SQLPLUS="$(command -v sqlplus 2>/dev/null)"

if [ -z "${SQLPLUS:-}" ]; then
  echo "ERROR: sqlplus no encontrado en \$ORACLE_HOME ni en PATH."
  exit 1
fi

CONEXION="${SQLPLUS_CONEXION:-$SQLPLUS_USUARIO/$SQLPLUS_CLAVE}"

echo "== Probando conexión =="
echo "SELECT SYS_CONTEXT('USERENV','DB_NAME') AS BD, SYS_CONTEXT('USERENV','CURRENT_SCHEMA') AS ESQUEMA FROM dual;" | "$SQLPLUS" -S "$CONEXION"
exit $?