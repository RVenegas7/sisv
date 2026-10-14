#!/usr/bin/env bash
# Script 2 del flujo semanal (opción A) — se corre en CASA.
#
#   oficina (script 1):  Oracle vivo -> espejo crudo en PG + espejo_extra -> pg_dump
#   casa    (script 2):  pg_dump -> refresca el espejo crudo local -> corre el ETL
#
# Qué hace:
#   1. Verifica el SHA256 del dump.
#   2. Lo restaura en una base temporal.
#   3. Guardia anti-regresión: si el espejo de la oficina viene ATRASADO respecto
#      al local (menos filas), aborta salvo --forzar.
#   4. Reemplaza el espejo crudo local: sismai + inbdlar1 + historico.
#      El esquema `legacy` (T_*) NO se toca: no viene del Oracle vivo y el local
#      va por delante (ver PENDIENTES.md).
#   5. Copia `espejo_extra` (data cruda del nivel central, p. ej. lara_2019_2020).
#   6. Corre el ETL en casa (idempotente, aditivo): importa los certificados
#      nuevos, reasigna centros y completa lo que falte. Conserva la codificación
#      CIE y todo el trabajo de la app.
#
# Lo que NUNCA trae:
#   - La base de distribución geográfica (`territorio_apn`): es estática, va en
#     otro dump y no se toca. El territorio de la app es idéntico entre bases.
#   - Nada de la app: fichas, consolidados, conciliaciones, registradores,
#     despacho, usuarios/perfiles, ASIC.
#
# Uso:
#   newgrp docker -c "bash migracion/aplicar_dump_oficina.sh"               # dry-run
#   newgrp docker -c "bash migracion/aplicar_dump_oficina.sh --ejecutar"    # aplica
#   newgrp docker -c "bash migracion/aplicar_dump_oficina.sh --solo-certificados --ejecutar"
#
# Variables:
#   PG_CONT=sis_postgres_dev      contenedor PostgreSQL
#   LOCAL_DB=sis_salud_db         base local de la app
#   TEMP_DB=sis_salud_db_oficina  base temporal para el dump
#   DESCARGA=descarga             directorio con el dump de la oficina
#   DUMP=...                      ruta explícita del dump (si no, el más reciente)
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ"

PG_CONT="${PG_CONT:-sis_postgres_dev}"
LOCAL_DB="${LOCAL_DB:-sis_salud_db}"
TEMP_DB="${TEMP_DB:-sis_salud_db_oficina}"
DESCARGA="${DESCARGA:-$RAIZ/descarga}"
VENV="${VENV:-$RAIZ/.venv/bin/python}"
MANAGE="${MANAGE:-$RAIZ/backend/manage.py}"
WORK="${WORK:-/tmp/opencode/oficina}"
export DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY:-flujo-oficina-local}"
# Espejo crudo que sí se reemplaza (legacy se conserva aparte)
ESQUEMAS_ESPEJO="${ESQUEMAS_ESPEJO:-sismai inbdlar1 historico}"
# Tablas clave para la guardia de regresión
TABLAS_GUARDIA="${TABLAS_GUARDIA:-sismai.CERTIFICADO sismai.NAC_RNACIDO sismai.CERTNACIMIENTO sismai.RENGLONTELE sismai.DOCUMENTO sismai.CASOS_MMI}"

EJECUTAR=0; FORZAR=0; LIMPIAR=0; SIN_ETL=0; SOLO_CERT=0; DUMP="${DUMP:-}"
while [ $# -gt 0 ]; do
  case "$1" in
    --ejecutar) EJECUTAR=1 ;;
    --forzar)   FORZAR=1 ;;
    --limpiar)  LIMPIAR=1 ;;
    --sin-etl)  SIN_ETL=1 ;;
    --solo-certificados) SOLO_CERT=1 ;;
    --dump)     DUMP="$2"; shift ;;
    *) echo "opción desconocida: $1" >&2; exit 2 ;;
  esac
  shift
done

log() { printf '\n=== %s ===\n' "$*"; }
psql_local() { docker exec "$PG_CONT" psql -U sis_user -d "$LOCAL_DB" -tAc "$1"; }
psql_temp()  { docker exec "$PG_CONT" psql -U sis_user -d "$TEMP_DB"  -tAc "$1"; }

# 0) Localizar el dump de la app (no el de territorio_apn)
if [ -z "$DUMP" ]; then
  DUMP="$(ls -t "$DESCARGA"/sis_salud_db_*.dump 2>/dev/null | head -1 || true)"
fi
[ -n "$DUMP" ] && [ -f "$DUMP" ] || { echo "No encuentro el dump de la oficina en $DESCARGA (usa --dump RUTA)." >&2; exit 1; }
log "Dump de la oficina: $DUMP"

# 1) Verificar integridad
if [ -f "$DESCARGA/SHA256SUMS" ] && grep -q "  $(basename "$DUMP")\$" "$DESCARGA/SHA256SUMS"; then
  log "Verificando SHA256"
  grep "  $(basename "$DUMP")\$" "$DESCARGA/SHA256SUMS" | ( cd "$DESCARGA" && sha256sum -c - ) \
    || { echo "SHA256 NO coincide: no aplico nada." >&2; exit 1; }
fi

mkdir -p "$WORK"

# 2) Restaurar en la base temporal
log "Restaurando en $TEMP_DB"
docker exec "$PG_CONT" dropdb -U sis_user --if-exists --force "$TEMP_DB"
docker exec "$PG_CONT" createdb -U sis_user -O sis_user "$TEMP_DB"
docker exec -i "$PG_CONT" pg_restore -U sis_user -d "$TEMP_DB" --no-owner --no-privileges < "$DUMP"

# 3) Guardia anti-regresión del espejo
log "Guardia: espejo de la oficina vs local"
atrasadas=0
for t in $TABLAS_GUARDIA; do
  e="${t%%.*}"; n="${t#*.}"
  po="$(psql_temp  "select count(*) from \"$e\".\"$n\"" 2>/dev/null || echo 'NA')"
  pl="$(psql_local "select count(*) from \"$e\".\"$n\"" 2>/dev/null || echo 'NA')"
  flag=""
  if [ "$po" != "NA" ] && [ "$pl" != "NA" ] && [ "$po" -lt "$pl" ]; then flag=" <-- ATRASADA"; atrasadas=$((atrasadas+1)); fi
  printf '  %-24s oficina=%-10s local=%-10s%s\n' "$t" "$po" "$pl" "$flag"
done
if [ "$atrasadas" -gt 0 ] && [ "$FORZAR" != 1 ]; then
  echo "El espejo de la oficina viene atrasado en $atrasadas tabla(s)." >&2
  echo "Corre el script 1 en la oficina para refrescarlo, o usa --forzar si sabes lo que haces." >&2
  exit 1
fi

if [ "$SOLO_CERT" = 1 ]; then
  # Camino rápido: solo fusionar certificados (no toca el espejo ni corre el ETL)
  log "Fusión aditiva de certificados (--solo-certificados)"
  args=(--local-db "$LOCAL_DB" --oficina-db "$TEMP_DB")
  [ "$EJECUTAR" = 1 ] && args+=(--ejecutar)
  "$VENV" migracion/aplicar_dump_oficina.py "${args[@]}"
else
  # 4) Reemplazar el espejo crudo
  log "Refrescando el espejo crudo ($ESQUEMAS_ESPEJO)"
  for e in $ESQUEMAS_ESPEJO; do
    echo "-- esquema $e"
    docker exec "$PG_CONT" pg_dump -U sis_user -Fc -n "$e" "$TEMP_DB" > "$WORK/$e.dump"
    if [ "$EJECUTAR" = 1 ]; then
      docker exec "$PG_CONT" psql -U sis_user -d "$LOCAL_DB" -q -c "DROP SCHEMA IF EXISTS $e CASCADE;"
      docker exec -i "$PG_CONT" pg_restore -U sis_user -d "$LOCAL_DB" --no-owner < "$WORK/$e.dump"
    fi
  done

  # 5) espejo_extra
  if [ "$(psql_temp "select 1 from information_schema.schemata where schema_name='espejo_extra'" 2>/dev/null)" = "1" ]; then
    log "Copiando espejo_extra"
    docker exec "$PG_CONT" pg_dump -U sis_user -Fc -n espejo_extra "$TEMP_DB" > "$WORK/espejo_extra.dump"
    if [ "$EJECUTAR" = 1 ]; then
      docker exec "$PG_CONT" psql -U sis_user -d "$LOCAL_DB" -q -c "DROP SCHEMA IF EXISTS espejo_extra CASCADE;"
      docker exec -i "$PG_CONT" pg_restore -U sis_user -d "$LOCAL_DB" --no-owner < "$WORK/espejo_extra.dump"
    fi
  else
    log "espejo_extra no viene en el dump (nada que copiar)"
  fi

  # 6) ETL en casa
  if [ "$SIN_ETL" != 1 ]; then
    if [ "$EJECUTAR" = 1 ]; then
      log "ETL: importando registros y vigilancia"
      "$VENV" "$MANAGE" importar_legacy_registros
      "$VENV" "$MANAGE" importar_legacy_vigilancia
      "$VENV" "$MANAGE" recuperar_establecimiento_defuncion --ejecutar
      "$VENV" "$MANAGE" asignar_organizacion_legacy --ejecutar
      "$VENV" "$MANAGE" completar_numero_certificado --ejecutar
      "$VENV" "$MANAGE" completar_nacimiento_legacy --ejecutar
      "$VENV" "$MANAGE" sembrar_registradores_legacy --ejecutar
    else
      log "ETL (dry-run): se correría importar_legacy_registros, importar_legacy_vigilancia,"
      echo "  recuperar_establecimiento_defuncion, asignar_organizacion_legacy,"
      echo "  completar_numero_certificado, completar_nacimiento_legacy, sembrar_registradores_legacy"
    fi
  fi
fi

# 7) Limpieza
if [ "$LIMPIAR" = 1 ]; then
  log "Eliminando $TEMP_DB"
  docker exec "$PG_CONT" dropdb -U sis_user --if-exists --force "$TEMP_DB"
fi

if [ "$EJECUTAR" = 1 ]; then
  log "Listo. Base local actualizada."
else
  log "DRY-RUN terminado. Vuelve a correrlo con --ejecutar para aplicar."
fi
