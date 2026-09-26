#!/usr/bin/env bash
# =============================================================================
#  04_pruebas_negativas.sh
#  SISV — Contrapruebas del plan B en el espejo.
#
#  Que la simulación "pase" no prueba nada si el resultado fuera el mismo
#  siempre. Estas pruebas alteran la cola o el origen y comprueban que el plan B
#  reaccione como debe. Cada prueba dice qué espera y qué obtuvo.
#
#  Escenario base: el de 01_preparar_escenario.sql (cola = manifiesto del
#  paquete del 04/08). Referencia de comparación: IMPORT29.T_*.
#
#  Pruebas:
#    A  Se agrega un DELETE(3) al final del historial de un ID que viaja
#       -> la fila debe DESAPARECER de la T_ (y el evento quedar en el manifiesto)
#    B  Se agrega un INSERT(1) a un ID que NO viajaba (borrado antes)
#       -> la fila debe APARECER en la T_
#    C  Se quitan 2 columnas de la tabla origen
#       -> la T_ debe quedar igual (la interseccion de columnas copio menos, no mas)
#    D  Se agrega un evento de una TABLA sin mapeo
#       -> no debe entrar en ninguna T_ ni en el manifiesto, y el informe debe
#          listarla en la seccion [5]
#    E  Se ejecuta dos veces seguidas
#       -> el resultado no debe cambiar (idempotencia)
#
#  Al terminar restaura el escenario base.
#
#  Uso: ./migracion/simulacion/04_pruebas_negativas.sh [contenedor]
# =============================================================================
set -euo pipefail
trap 'echo ">>> ABORTADO en la linea $LINENO (rc=$?)" >&2' ERR

RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
CONT="${1:-sis_oracle_legacy}"
SIM="$RAIZ/migracion/simulacion"
AUD="$RAIZ/auditoria"
SQLPLUS="sqlplus -s system/oracle123@XE"
PASSES=0
FALLOS=0

mkdir -p "$AUD"
# sql <sql|@script>
#   - SQL*Plus no envia una sentencia sin ';', y CONFUNDE "COMMIT;" con su
#     propio comando COMMIT (que no admite ';') -> ORA-00911. De ahi las dos
#     reglas: una sentencia por linea, y ';' al final.
#   - Limitacion: no se admiten ';' dentro de literales (aqui no se usan).
sql() {
  local q="$1"
  case "$q" in
    @*|/*) : ;;                       # script o bloque: se pasa tal cual
    *';')
      if [ "$(printf '%s' "$q" | wc -l)" -eq 0 ]; then
        q="$(printf '%s' "$q" | sed 's/;/;\n/g')"   # una sola linea: separar
      fi ;;                          # multilinea: ya viene bien
    *)       q="$q;" ;;               # SELECT/INSERT/UPDATE...
  esac
  docker exec "$CONT" bash -c "$SQLPLUS <<SQL
SET FEEDBACK OFF PAGESIZE 100 LINESIZE 200
$q
EXIT
SQL" 2>&1 | tr -d '\r'
}

die() { echo "ERROR: $*" >&2; exit 1; }

# numero <sql> -> el primer valor numerico de la salida, o ERROR (nunca aborta)
# OJO: hay que borrar tambien el TABULADOR. SQL*Plus alinea a la derecha con
# espacios cuando el numero es ancho, pero con un solo digito (p. ej. un COUNT
# con WHERE que da 0) pone un tabulador: sin "tr -d '\t'" se leia ERROR donde
# habia un 0, y las comprobaciones de inyeccion daban FALLA falsas.
numero() {
  local r
  r=$(sql "$1" | tr -d ' \t' | grep -E '^[0-9]+(\.[0-9]+)?$' | head -1) || true
  printf '%s' "${r:-ERROR}"
}

contar() { numero "SELECT COUNT(*) FROM $1"; }

# La fase original recreaba TEMP.T_* en cada corrida: aqui tambien, para que
# cada prueba mida una replicacion desde cero.
dml_preparado() {
  docker exec "$CONT" bash -c "$SQLPLUS <<SQL >/dev/null 2>&1
DROP USER TEMP CASCADE;
CREATE USER TEMP IDENTIFIED BY TEMP QUOTA UNLIMITED ON SYSTEM QUOTA UNLIMITED ON USERS;
GRANT CREATE SESSION TO TEMP;
@/tmp/00_ddl_temp_04082026.sql
EXIT
SQL"
}

replicar() {
  docker cp /tmp/rep_run.sql "${CONT}:/tmp/rep_run.sql" >/dev/null 2>&1 || true
  docker exec "$CONT" bash -c "$SQLPLUS @/tmp/rep_run.sql 2>&1" | tr -d '\r' \
    > "$AUD/prueba_replicacion.txt"
}

# AMS es VARCHAR2: el centinela de los eventos de prueba es 'ZZPRUEBA'.
inyectar() {  # inyectar <TABLA> <ID> <EVENTO>  (verifica que la fila exista)
  sql "INSERT INTO SISMAI.EVENTOS_SINC (TABLA,ID,EVENTO,FECHA,AMS)
       VALUES ('$1',$2,$3,SYSDATE,'ZZPRUEBA')" > /dev/null
  local n
  n=$(numero "SELECT COUNT(*) FROM SISMAI.EVENTOS_SINC
               WHERE AMS='ZZPRUEBA' AND TABLA='$1' AND ID=$2")
  if [ "$n" = ERROR ] || [ "$n" -lt 1 ]; then
    echo "    FALLA no se pudo inyectar el evento de prueba ($1/$2/$3)"; FALLOS=$((FALLOS+1))
  fi
}
quitar() {    # quitar <TABLA> <ID>  -> borra solo los eventos de prueba
  sql "DELETE FROM SISMAI.EVENTOS_SINC WHERE AMS='ZZPRUEBA' AND TABLA='$1' AND ID=$2" > /dev/null
}
chequear() {  # chequear <nombre> <esperado> <obtenido>
  if [ "$2" = "$3" ]; then
    echo "    OK    $1: $3"; PASSES=$((PASSES+1))
  else
    echo "    FALLA $1: esperado $2, obtenido $3"; FALLOS=$((FALLOS+1))
  fi
}

echo
echo "==============================================================="
echo "  Contrapruebas del plan B  (contenedor $CONT)"
echo "==============================================================="

# SQL que necesita dentro del contenedor
docker cp "$SIM/01_preparar_escenario.sql"      "${CONT}:/tmp/01_preparar_escenario.sql"    >/dev/null
docker cp "$SIM/00_ddl_temp_04082026.sql"       "${CONT}:/tmp/00_ddl_temp_04082026.sql"   >/dev/null
# El SQL de replicar tiene que estar con V_EJECUTAR := 1
sed 's/^\(  V_EJECUTAR  *PLS_INTEGER *:\?= *\)0;/\11;/' \
    "$RAIZ/migracion/replicar_controlado.sql" > /tmp/rep_run.sql
docker cp /tmp/rep_run.sql "${CONT}:/tmp/rep_run.sql" >/dev/null

echo
echo "[base] escenario de referencia"
sql "@/tmp/01_preparar_escenario.sql" > "$AUD/prueba_base.txt"
dml_preparado
replicar
BASE_CERTMORT=$(contar TEMP.T_CERTMORT)
BASE_DOCUMENT=$(contar TEMP.T_DOCUMENT)
BASE_MANIF=$(contar TEMP.T_EVENTOS)
echo "    T_CERTMORT=$BASE_CERTMORT  T_DOCUMENT=$BASE_DOCUMENT  T_EVENTOS=$BASE_MANIF"

# ---------------------------------------------------------------- A ----------
echo
echo "[A] DELETE(3) al final del historial de un ID que viaja -> la fila desaparece"
ID_A=$(numero "SELECT MIN(ID) FROM TEMP.T_CERTMORT")
[ -n "$ID_A" ] || die "no se pudo leer un ID de TEMP.T_CERTMORT"
echo "    ID elegido: $ID_A  (filas con ese ID en T_CERTMORT: $(contar "TEMP.T_CERTMORT WHERE ID=$ID_A"))"
inyectar CERTIFICADO "$ID_A" 3
echo "    cola tras inyectar: $(contar SISMAI.EVENTOS_SINC) eventos"
dml_preparado; replicar
chequear "T_CERTMORT" "$((BASE_CERTMORT-1))" "$(contar TEMP.T_CERTMORT)"
chequear "T_EVENTOS (el DELETE queda en el manifiesto)" "$((BASE_MANIF+1))" "$(contar TEMP.T_EVENTOS)"
echo "        (el manifiesto lo mantiene: es lo que hace el legacy, PENDIENTES 17.13)"
# revertir
quitar CERTIFICADO "$ID_A"

# ---------------------------------------------------------------- B ----------
echo
echo "[B] INSERT(1) a un ID que NO viajaba (borrado antes) -> la fila aparece"
ID_B=$(numero "SELECT MIN(ID) FROM (SELECT DISTINCT R.ID FROM IMPORT29.T_EVENTOS R
         WHERE R.TABLA='DOCUMENTO'
           AND NOT EXISTS (SELECT 1 FROM IMPORT29.T_DOCUMENT D WHERE D.ID=R.ID))")
if [ -n "$ID_B" ]; then
  inyectar DOCUMENTO "$ID_B" 1
  # La fuente no tiene esa fila (se construyo desde la referencia), asi que el
  # aviso esperado es "IDs de la cola que no existen en el origen":
  dml_preparado; replicar
  chequear "T_DOCUMENT (el origen no tiene la fila, asi que no viaja)" "$BASE_DOCUMENT" "$(contar TEMP.T_DOCUMENT)"
  chequear "T_EVENTOS (si aparece: el manifiesto es copia de toda la cola)" "$((BASE_MANIF+1))" "$(contar TEMP.T_EVENTOS)"
  quitar DOCUMENTO "$ID_B"
else
  echo "    (sin ID que no viajara en DOCUMENTO: prueba omitida)"
fi

# ---------------------------------------------------------------- C ----------
echo
echo "[C] se quitan 2 columnas del origen -> la T_ debe quedar igual"
COLS_TOTAL=$(contar "ALL_TAB_COLUMNS WHERE OWNER='SISMAI' AND TABLE_NAME='CERTIFICADO'")
echo "    el origen tiene $COLS_TOTAL columnas"
COLS=$(sql "SET HEADING OFF
SELECT 'COL:'||COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE OWNER='SISMAI' AND TABLE_NAME='CERTIFICADO'
 AND COLUMN_ID>$((COLS_TOTAL-2)) ORDER BY COLUMN_ID" | tr -d ' \t' | sed -n 's/^COL:\([A-Z0-9_]*\)$/\1/p' | tr '\n' ' ' || true)
if [ -z "$COLS" ]; then
  echo "    FALLA no se pudo leer que columnas quitar"; FALLOS=$((FALLOS+1))
fi
for c in $COLS; do
  sql "ALTER TABLE SISMAI.CERTIFICADO DROP COLUMN $c" > /dev/null
  if [ "$(numero "SELECT COUNT(*) FROM ALL_TAB_COLUMNS WHERE OWNER='SISMAI' AND TABLE_NAME='CERTIFICADO' AND COLUMN_NAME='$c'")" != 0 ]; then
    echo "    NO se pudo quitar $c"; FALLOS=$((FALLOS+1))
  else
    echo "    quitada $c"
  fi
done
dml_preparado; replicar
if grep -qE "ORA-|PLS-|ERROR" "$AUD/prueba_replicacion.txt"; then
  echo "    FALLA la replicacion reporto error tras quitar columnas"; FALLOS=$((FALLOS+1))
  grep -E "ORA-|PLS-|ERROR" "$AUD/prueba_replicacion.txt" | head -3 | sed 's/^/      /'
fi
chequear "T_CERTMORT (interseccion de columnas: copia menos, no mas)" "$BASE_CERTMORT" "$(contar TEMP.T_CERTMORT)"
sql "@/tmp/01_preparar_escenario.sql" > /dev/null
echo "        (origen reconstruido exacto desde la referencia)"

# ---------------------------------------------------------------- D ----------
echo
echo "[D] evento de una TABLA sin mapeo -> no entra, y se reporta en [5]"
inyectar REG_VACUNACION 1 1
dml_preparado; replicar
chequear "T_CERTMORT (sin cambios)" "$BASE_CERTMORT" "$(contar TEMP.T_CERTMORT)"
chequear "T_EVENTOS (sin cambios: no esta mapeada)" "$BASE_MANIF" "$(contar TEMP.T_EVENTOS)"
if grep -q "SIN MAPEO: TABLA=REG_VACUNACION" "$AUD/prueba_replicacion.txt"; then
  echo "    OK    el informe la lista en la seccion [5] con candidatos"
else
  echo "    FALLA el informe no la reporta"; FALLOS=$((FALLOS+1))
fi
sql "DELETE FROM SISMAI.EVENTOS_SINC WHERE AMS='ZZPRUEBA'" > /dev/null

# ---------------------------------------------------------------- E ----------
echo
echo "[E] dos ejecuciones seguidas -> el resultado no cambia"
dml_preparado; replicar
dml_preparado; replicar
chequear "T_CERTMORT" "$BASE_CERTMORT" "$(contar TEMP.T_CERTMORT)"
chequear "T_CERTNACI" "422" "$(contar TEMP.T_CERTNACI)"
chequear "T_EVENTOS" "$BASE_MANIF" "$(contar TEMP.T_EVENTOS)"

# ---------------------------------------------------------------- restore -----
echo
echo "[fin] restaurando el escenario base"
sql "@/tmp/01_preparar_escenario.sql" > "$AUD/prueba_base.txt"
dml_preparado
replicar
chequear "T_CERTMORT (base restaurada)" "$BASE_CERTMORT" "$(contar TEMP.T_CERTMORT)"
chequear "T_EVENTOS (base restaurada)" "$BASE_MANIF" "$(contar TEMP.T_EVENTOS)"

echo
echo "==============================================================="
echo "  contrapruebas: $PASSES correctas, $FALLOS con falla"
echo "==============================================================="
[ "$FALLOS" -eq 0 ] || exit 1
