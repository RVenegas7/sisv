#!/usr/bin/env bash
# Script 1 del flujo semanal (opción A) — se corre en LA OFICINA.
#
#   Oracle vivo -> espejo crudo en PG + espejo_extra -> pg_dump para traer a casa
#
# Qué hace:
#   1. (Opcional, HACER_RESPALDO=1) exporta el Oracle vivo: migracion/respaldo_total.sh.
#      Deja los .dmp en el servidor; luego hay que copiarlos a respaldo/respaldos_sismai/.
#   2. Refresca el espejo crudo en PostgreSQL desde esos .dmp:
#      migracion/actualizar_espejo_pg.sh  (Oracle local en Docker -> CSV -> PG).
#   3. Carga la data cruda del nivel central: espejo_extra (lara_2019_2020.xlsx), si está.
#   4. (Opcional, HACER_ETL=1) corre el ETL para que las tablas de la app queden al día
#      (migracion/etl_comandos.sh). Sin esto la app muestra CEROS aunque el espejo esté
#      fresco: el EPI-15 y los consolidados ENO los llena el ETL, no el espejo (§40).
#   5. Produce el pg_dump de la base de la app para llevarla a casa + SHA256.
#
# Si no se pasa HACER_ETL=1, el ETL se corre en casa (script 2). El dump lleva el espejo
# crudo y espejo_extra; el resto de la app que vaya en el dump se ignora en casa.
#
# NO se toca ni se incluye la base de distribución geográfica (territorio_apn):
# es estática y se reproduce con `manage.py exportar_territorio_pg`.
#
# Uso:
#   bash migracion/oficina_refrescar_y_exportar.sh
#   HACER_RESPALDO=1 bash migracion/oficina_refrescar_y_exportar.sh
#   HACER_ETL=1      bash migracion/oficina_refrescar_y_exportar.sh
#
# Variables:
#   PG_CONT=sis_postgres_dev   contenedor PostgreSQL (oficina)
#   LOCAL_DB=sis_salud_db      base de la app
#   DUMPDIR=respaldo/respaldos_sismai   .dmp del Oracle vivo
#   SALIDA=descarga            salida del pg_dump
#   HACER_ETL=1                corre el ETL aquí (recomendado si se va a usar la app
#                              en la oficina: sin él el EPI-15 sale en cero)
#   HACER_TERRITORIO=1         regenera territorio_apn (exportar_territorio_pg)
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ"

PG_CONT="${PG_CONT:-sis_postgres_dev}"
LOCAL_DB="${LOCAL_DB:-sis_salud_db}"
DUMPDIR="${DUMPDIR:-$RAIZ/respaldo/respaldos_sismai}"
SALIDA="${SALIDA:-$RAIZ/descarga}"
VENV="${VENV:-$RAIZ/.venv/bin/python}"
HACER_RESPALDO="${HACER_RESPALDO:-0}"
HACER_ETL="${HACER_ETL:-0}"
HACER_TERRITORIO="${HACER_TERRITORIO:-0}"
XLSX="${XLSX:-$RAIZ/lara_2019_2020.xlsx}"
FECHA="$(date +%Y-%m-%d)"

log() { printf '\n=== %s ===\n' "$*"; }

# 1) Exportar el Oracle vivo (opcional)
if [ "$HACER_RESPALDO" = 1 ]; then
  log "Exportando el Oracle vivo"
  bash migracion/respaldo_total.sh
  echo "Los .dmp quedaron en el servidor. Cópialos a $DUMPDIR y vuelve a correr sin HACER_RESPALDO."
  exit 0
fi

# Verificar que están los .dmp del Oracle
log "Dumps del Oracle en $DUMPDIR"
if ! ls "$DUMPDIR"/*.dmp >/dev/null 2>&1; then
  echo "No hay .dmp en $DUMPDIR. Corre con HACER_RESPALDO=1 y copia los del servidor." >&2
  exit 1
fi
ls -1 "$DUMPDIR"/*.dmp | sed 's/^/  /'

# 2) Refrescar el espejo crudo en PostgreSQL (Oracle local -> CSV -> PG)
log "Refrescando el espejo crudo en PostgreSQL"
bash migracion/actualizar_espejo_pg.sh

# 3) Data cruda del nivel central (espejo_extra)
[ -f "$XLSX" ] || XLSX="$RAIZ/legancy/lara_2019_2020.xlsx"
if [ -f "$XLSX" ]; then
  log "Cargando espejo_extra desde $XLSX"
  "$VENV" migracion/cargar_lara_2019_2020_pg.py --archivo "$XLSX" --ejecutar
else
  log "No hay $XLSX; se omite espejo_extra"
fi

# 4) ETL en la oficina (opcional pero recomendado: sin esto la app ve ceros)
if [ "$HACER_ETL" = 1 ]; then
  log "ETL en la oficina (las tablas de la app quedan al día)"
  MANAGE="$RAIZ/backend/manage.py" VENV="$VENV" bash "$RAIZ/migracion/etl_comandos.sh" --ejecutar
else
  log "ETL omitido (HACER_ETL!=1): se correrá en casa. En la oficina el EPI-15 saldrá en cero."
fi

# 4b) Territorio (estático: no viene en el dump)
if [ "$HACER_TERRITORIO" = 1 ]; then
  log "Regenerando territorio_apn"
  DJANGO_DEBUG=1 "$VENV" "$RAIZ/backend/manage.py" exportar_territorio_pg
fi

# 5) pg_dump para llevar a casa (no incluye territorio_apn: es otra base)
log "Generando el dump para casa"
mkdir -p "$SALIDA"
DUMP="$SALIDA/sis_salud_db_${FECHA}.dump"
docker exec "$PG_CONT" pg_dump -U sis_user -Fc "$LOCAL_DB" > "$DUMP"
( cd "$SALIDA" && sha256sum "$(basename "$DUMP")" > SHA256SUMS )

log "Listo"
echo "Dump: $DUMP"
echo "Llévalo a casa y corre: migracion/aplicar_dump_oficina.sh"
