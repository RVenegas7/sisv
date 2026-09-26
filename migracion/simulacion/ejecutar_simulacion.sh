#!/usr/bin/env bash
# =============================================================================
#  ejecutar_simulacion.sh
#  SISV — Orquestador de la simulación del paquete semanal.
#
#  Reproduce, en el espejo Oracle local, lo que el legacy hace cada semana:
#  crear TEMP.T_*, llenarlas desde la cola y exportar el ZIP de 5 archivos.
#  La fase de replicación la reemplaza migracion/replicar_controlado.sql, y el
#  resultado se compara con el ÚLTIMO PAQUETE QUE EL LEGACY SÍ ENVIÓ
#  (enviados/routlar1_482026_1526.ZIP, 04/08/2026), que está íntegro en el
#  esquema IMPORT29 del espejo.
#
#  Etapas:
#    1. Escenario: SISMAI.EVENTOS_SINC y las 23 fuentes, desde la referencia.
#    2. TEMP.T_* vacías con la estructura REAL (83 tablas, 86 índices).
#    3. replicar_controlado.sql con V_EJECUTAR := 1.
#    4. Comparación fila por fila (MINUS en ambos sentidos) contra IMPORT29.
#    5. ZIP de 5 archivos + comparación de conteos con el paquete real.
#    6. Idempotencia: se repite el paso 3 y se vuelve a comparar.
#
#  Uso:
#    ./migracion/simulacion/ejecutar_simulacion.sh [contenedor]
#  Requisitos: contenedor sis_oracle_legacy levantado (con el espejo de
#  legancy/BDSISMAI.DMP montado), docker, y el usuario SYSTEM de XE.
#
#  NO toca nada de 192.168.5.200. Todo ocurre en el espejo local.
#  Ver PENDIENTES.md 17.13.
# =============================================================================
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
CONT="${1:-sis_oracle_legacy}"
SIM="$RAIZ/migracion/simulacion"
AUD="$RAIZ/auditoria"
SQLPLUS="sqlplus -s system/oracle123@XE"
PASS="oracle123"

info() { echo "  $*"; }
die()  { echo "ERROR: $*" >&2; exit 1; }
sep()  { echo; echo "==============================================================="; echo "  $1"; echo "==============================================================="; }

command -v docker >/dev/null || die "se necesita docker"
docker info >/dev/null 2>&1 || die "no se puede hablar con docker (grupo docker)"
if [ -z "$(docker ps -q -f "name=^${CONT}$")" ]; then
  info "el contenedor $CONT no esta corriendo; se levanta"
  docker start "$CONT" >/dev/null
  sleep 20
fi
mkdir -p "$AUD"

# Copia los SQL al contenedor y los corre, dejando la salida en $2
sql_en_contenedor() {
  local origen="$1" destino="/tmp/$(basename "$1")" salida="${2:-/dev/null}"
  docker cp "$origen" "${CONT}:${destino}" >/dev/null
  # @script: SQL*Plus lo ejecuta tal cual (no hay que anadir terminador)
  docker exec "$CONT" bash -c "$SQLPLUS @${destino} 2>&1" | tr -d '\r' > "$salida"
}

# --- 0. El DDL de TEMP se aplica cada vez: la fase original lo hacia asi -----
# OJO: el cuerpo del here-doc tiene que ir DENTRO del texto que se pasa a
# `bash -c` (la comilla cierra despues del terminador SQL). Si cierra antes,
# el bash de dentro recibe solo la linea del <<'SQL', no encuentra el
# terminador y falla con "here-document delimited by end-of-file".
aplicar_ddl_temp() {
  docker exec "$CONT" bash -c "$SQLPLUS <<'SQL' 2>&1
SET FEEDBACK ON
-- DROP condicional: en la primera corrida TEMP no existe y el DROP a pelo
-- solo produce un ORA-01918 que parece un fallo.
BEGIN EXECUTE IMMEDIATE 'DROP USER TEMP CASCADE'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
CREATE USER TEMP IDENTIFIED BY TEMP QUOTA UNLIMITED ON SYSTEM QUOTA UNLIMITED ON USERS;
GRANT CREATE SESSION TO TEMP;
@/tmp/00_ddl_temp_04082026.sql
EXIT
SQL
" | tr -d '\r' | grep -E "ORA-|Table created|Index created" | sort | uniq -c
}

sep "1/6  Escenario de prueba (desde la referencia del 04/08/2026)"
sql_en_contenedor "$SIM/01_preparar_escenario.sql" "$AUD/sim_1_escenario.txt"
grep -E "^[0-9]\." "$AUD/sim_1_escenario.txt" | sed 's/^/  /'
grep -q "ERROR" "$AUD/sim_1_escenario.txt" && die "fallo la etapa 1 (ver $AUD/sim_1_escenario.txt)"

sep "2/6  TEMP.T_* vacías con la estructura real"
aplicar_ddl_temp | sed 's/^/  /'

sep "3/6  replicar_controlado.sql con V_EJECUTAR := 1"
sed 's/^\(  V_EJECUTAR  *PLS_INTEGER *:\?= *\)0;/\11;/' \
    "$RAIZ/migracion/replicar_controlado.sql" > /tmp/rep_run.sql
docker cp /tmp/rep_run.sql "${CONT}:/tmp/rep_run.sql" >/dev/null
docker exec "$CONT" bash -c "$SQLPLUS @/tmp/rep_run.sql 2>&1" | tr -d '\r' \
  > "$AUD/replicar_ejecucion.txt"
if grep -qE "ORA-|PLS-|ERROR" "$AUD/replicar_ejecucion.txt"; then
  grep -E "ORA-|PLS-|ERROR" "$AUD/replicar_ejecucion.txt" | head -5 | sed 's/^/  /'
  die "la replicacion dio errores (ver $AUD/replicar_ejecucion.txt)"
fi
grep -E "filas insertadas en TEMP|T_EVENTOS:" "$AUD/replicar_ejecucion.txt" | sed 's/^/  /'

sep "4/6  Comparacion fila por fila contra IMPORT29 (el paquete real)"
sql_en_contenedor "$SIM/02_comparar.sql" "$AUD/sim_4_comparacion.txt"
grep -vE "^\s*$" "$AUD/sim_4_comparacion.txt" | tail -32 | sed 's/^/  /'
grep -q "SIMULACION CORRECTA" "$AUD/sim_4_comparacion.txt" \
  || echo "  >>> HAY DIFERENCIAS: el paquete simulado NO reproduce al original"

sep "5/6  ZIP de 5 archivos y comparacion de conteos"
"$SIM/03_generar_paquete.sh" "$CONT" 2>&1 | sed 's/^/  /'

sep "6/6  Idempotencia: se repite la replicacion y se vuelve a comparar"
docker exec "$CONT" bash -c "$SQLPLUS @/tmp/rep_run.sql 2>&1" | tr -d '\r' \
  > "$AUD/replicar_ejecucion_2.txt"
grep -E "filas insertadas en TEMP|filas borradas de TEMP" "$AUD/replicar_ejecucion_2.txt" | sed 's/^/  /'
sql_en_contenedor "$SIM/02_comparar.sql" "$AUD/sim_6_comparacion_2.txt"
if grep -q "SIMULACION CORRECTA" "$AUD/sim_6_comparacion_2.txt"; then
  echo "  IDEMPOTENTE: la segunda corrida deja el mismo resultado"
else
  echo "  >>> la segunda corrida difiere: NO es idempotente"
  grep -E "DIFERENCIA" "$AUD/sim_6_comparacion_2.txt" | sed 's/^/  /'
fi

echo
info "evidencia en $AUD/"
ls -1 "$AUD" | sed 's/^/    /'
