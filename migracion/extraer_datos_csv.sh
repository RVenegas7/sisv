#!/bin/bash
# ==============================================================================
# Exportación de datos SIS Oracle 10g -> CSV plano (una fila por línea, ; como separador)
# Ejecutar como usuario oracle, DESPUÉS de extraer la estructura.
# Revisa el encoding heredado (WE8MSWIN1252) y regenera con AL32UTF8 si el texto
# sale con mojibake. Prioriza 'exp' para tablas enormes; este CSV es para análisis.
# ==============================================================================
set -eu

if [ ! -f 1_tablas.csv ]; then
  echo "Falta 1_tablas.csv. Ejecuta primero extraer_estructura.sql" >&2
  exit 1
fi

OUT="$PWD/datos_csv"
mkdir -p "$OUT"

# Tablas de infraestructura de replicación SIN valor de negocio (colas de sincronización
# nunca procesadas; ver Informe_BD_SIS_LAR1_2026-09-18.md §5.1-5.2). Se excluyen siempre.
# Además se descarta el ruido de Oracle Enterprise Manager (SM*, SMP_*) y las internas
# de explain plan.
EXCLUIR='EVENTOS_SINC|EVENTOS_DBLINK|EVENTOS_RESP|PLAN_TABLE|PLAN_TABLE2|^SM|^SMP_'

while IFS=';' read -r TABLA ROWS COLS; do
  [ -n "${TABLA%%[^A-Za-z0-9_]*}" ] || continue
  if echo "$TABLA" | grep -Eq "$EXCLUIR"; then
    echo "Omitiendo $TABLA (infraestructura/ruido)"
    continue
  fi
  echo "Exportando $TABLA ($ROWS filas)"
  {
    echo "SET PAGESIZE 0 FEEDBACK OFF ECHO OFF TRIMSPOOL ON HEADING OFF TERMOUT OFF"
    echo "SET LINESIZE 4000"
    echo "SPOOL $OUT/$TABLA.csv"
    echo "SELECT * FROM $TABLA ORDER BY 1;"
    echo "SPOOL OFF"
    echo "EXIT;"
  } > _tmp_$TABLA.sql
  sqlplus -S / as sysdba @_tmp_$TABLA.sql > /dev/null
  rm -f _tmp_$TABLA.sql
done < 1_tablas.csv

echo "CSV generados en: $OUT"
exit 0