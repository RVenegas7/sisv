#!/usr/bin/env bash
# ====================================================================
# RECONOCIMIENTO (SOLO LECTURA) de quien genera `repllar1.log` en el
# servidor SIS/Lara (srvsis 192.168.5.200 / SID lar1), por SSH.
#
# Que hace y que NO hace:
#   - Recorre el sistema (rutas del orquestador, cron, procesos, logs
#     del sobre, historial) y consulta el estado de TEMP.T_* y de la
#     cola SISMAI.EVENTOS_SINC.
#   - NO ejecuta la fase de replicacion, NO escribe nada en el servidor
#     y NO hace DDL/DML. Es seguro correrlo con el sistema en uso.
#
# --------------------------------------------------------------------
# Uso:
#   ./migracion/recon_repllar1.sh                      # valores por defecto
#   HOST=192.168.5.200 USUARIO=respaldo CLAVE=... ./migracion/recon_repllar1.sh
#   USUARIO=oracle ./migracion/recon_repllar1.sh        # incluye ALL_ERRORS
#   SALIDA=/ruta/informe.txt ./migracion/recon_repllar1.sh
#
# Requisitos: estar en la red de la oficina (192.168.5.x) o VPN, y
# `sshpass` instalado (sudo apt install sshpass). Sin sshpass el script
# imprime las ordenes manuales.
#
# Archivos:
#   migracion/recon_repllar1_remoto.sh  (se ejecuta en el servidor)
#   migracion/recon_repllar1.sql        (se ejecuta en sqlplus)
#   Salida por defecto: auditoria/recon_repllar1_AAAAMMDD.txt
#     (auditoria/ esta en .gitignore: el informe puede traer usuarios
#      del legacy y rastros de comandos con credenciales)
# ====================================================================
set -uo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
HOST="${HOST:-192.168.5.200}"
USUARIO="${USUARIO:-respaldo}"
CLAVE="${CLAVE:-respaldo}"
ORACLE_SID="${ORACLE_SID:-lar1}"
SQLPLUS="${SQLPLUS:-/opt/oracle/bin/sqlplus}"
REMOTO="$RAIZ/migracion/recon_repllar1_remoto.sh"
SQL_FILE="$RAIZ/migracion/recon_repllar1.sql"
SALIDA="${SALIDA:-$RAIZ/auditoria/recon_repllar1_$(date +%Y%m%d).txt}"

for f in "$REMOTO" "$SQL_FILE"; do
  [ -r "$f" ] || { echo "ERROR: no existe $f" >&2; exit 1; }
done
mkdir -p "$(dirname "$SALIDA")"

echo "Reporte: $SALIDA"
echo ">> [1/2] Reconocimiento del sistema en $USUARIO@$HOST (solo lectura)"

if command -v sshpass >/dev/null 2>&1; then
  sshpass -p "$CLAVE" ssh -o StrictHostKeyChecking=no -o LogLevel=ERROR \
    "$USUARIO@$HOST" 'bash -s' < "$REMOTO" > "$SALIDA" 2>&1
  RC=$?
else
  echo 'AVISO: no hay sshpass; se omite la parte remota.'
  echo "       Para obtenerla, en una terminal con sesion SSH:"
  echo "         scp $REMOTO $USUARIO@$HOST:/tmp/"
  echo "         ssh $USUARIO@$HOST 'bash /tmp/recon_repllar1_remoto.sh' > $SALIDA"
  : > "$SALIDA"
  RC=2
fi

echo ">> [2/2] Estado de la cola y de TEMP.T_* en Oracle (SID $ORACLE_SID)"
{
  echo
  echo "############################################################"
  echo "## ESTADO EN BASE DE DATOS (sqlplus $USUARIO@$ORACLE_SID)"
  echo "############################################################"
} >> "$SALIDA"

if [ "$RC" = 2 ]; then
  {
    echo "(pendiente: correr a mano)"
    echo "  scp $SQL_FILE $USUARIO@$HOST:/tmp/"
    echo "  ssh $USUARIO@$HOST '$SQLPLUS -s $USUARIO/$CLAVE@$ORACLE_SID @/tmp/recon_repllar1.sql' >> $SALIDA"
  } >> "$SALIDA"
elif command -v sshpass >/dev/null 2>&1; then
  sshpass -p "$CLAVE" ssh -o StrictHostKeyChecking=no -o LogLevel=ERROR \
    "$USUARIO@$HOST" \
    "$SQLPLUS -s $USUARIO/$CLAVE@$ORACLE_SID" < "$SQL_FILE" >> "$SALIDA" 2>&1
fi

echo
echo "Listo: $SALIDA"
echo
echo "Como leerlo:"
echo "  [2]/[2.2]  si TEMP.T_* NO se recrean (LAST_DDL_TIME viejo) => la fase"
echo "             'repl' no corre: encolar natalidad el lunes no haria"
echo "             que nada viaje el martes."
echo "  [4]        con solo SELECT: que ventana de T_EVENTOS esta lista."
echo "  [5]        si el motor (paquete/procedimiento de SINC) esta INVALIDO."
echo "  [2] del recon remoto  archivo que menciona repllar1 = el generador;"
echo '  [3]/[7]                cron/at/historial = quien lo lanza.'
