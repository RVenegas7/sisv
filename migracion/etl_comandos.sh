#!/usr/bin/env bash
# ETL de la app sobre el espejo crudo — LISTA ÚNICA, compartida por los dos lados.
#
#   Casa    (script 2):  migracion/aplicar_dump_oficina.sh   -> lo invoca en su paso 6
#   Oficina (script 1):  migracion/oficina_refrescar_y_exportar.sh -> con HACER_ETL=1
#
# Por qué existe este archivo: hasta el 20/10/2026 la lista de comandos del ETL vivía
# SOLO dentro del script de casa, así que la oficina refrescaba el espejo pero nunca
# llenaba las tablas de la app -> el EPI-15, los consolidados ENO y el MM/MN salían en
# cero (§40 de PENDIENTES.md). Con una sola fuente de verdad, si mañana se añade un
# comando del ETL no hay que recordar tocarlo en dos scripts.
#
# Todos los comandos son IDEMPOTENTES y ADITIVOS: se pueden correr las veces que haga
# falta, no duplican filas y nunca pisan lo ya cargado (el CIE revisado, la codificación
# pendiente y la configuración se conservan).
#
# Uso:
#   bash migracion/etl_comandos.sh            # lista lo que correría (dry-run)
#   bash migracion/etl_comandos.sh --ejecutar # lo corre de verdad
#   bash migracion/etl_comandos.sh --ejecutar --solo-certificados   # sin vigilancia
#
# Variables:
#   VENV     python del virtualenv (def. ./.venv/bin/python)
#   MANAGE   manage.py            (def. backend/manage.py)
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ"

VENV="${VENV:-$RAIZ/.venv/bin/python}"
MANAGE="${MANAGE:-$RAIZ/backend/manage.py}"

# DJANGO_DEBUG=1 es obligatorio: settings.py aborta sin él por el SECRET_KEY de desarrollo.
export DJANGO_DEBUG="${DJANGO_DEBUG:-1}"
export DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY:-etl-local}"

EJECUTAR=0; SOLO_CERT=0
while [ $# -gt 0 ]; do
  case "$1" in
    --ejecutar)          EJECUTAR=1 ;;
    --solo-certificados) SOLO_CERT=1 ;;
    *) echo "opción desconocida: $1" >&2; exit 2 ;;
  esac
  shift
done

log() { printf '\n=== %s ===\n' "$*"; }

if [ ! -x "$VENV" ]; then
  echo "No existe el virtualenv en $VENV. Instálalo con:" >&2
  echo "  ./.venv/bin/pip install -r backend/requirements.txt" >&2
  exit 1
fi

# Lista de comandos. Los dos importadores NO llevan --ejecutar (importan directo);
# los cinco de mantenimiento SÍ (dry-run por defecto).
COMANDOS=(
  "importar_legacy_registros"
  "importar_legacy_vigilancia"
  "recuperar_establecimiento_defuncion --ejecutar"
  "asignar_organizacion_legacy --ejecutar"
  "completar_numero_certificado --ejecutar"
  "completar_nacimiento_legacy --ejecutar"
  "sembrar_registradores_legacy --ejecutar"
)

# Camino rápido aditivo: solo fusiona certificados, sin tocar vigilancia.
if [ "$SOLO_CERT" = 1 ]; then
  COMANDOS=(
    "importar_legacy_registros"
    "recuperar_establecimiento_defuncion --ejecutar"
    "asignar_organizacion_legacy --ejecutar"
    "completar_numero_certificado --ejecutar"
    "completar_nacimiento_legacy --ejecutar"
    "sembrar_registradores_legacy --ejecutar"
  )
fi

if [ "$EJECUTAR" != 1 ]; then
  log "ETL (dry-run): se correría, en este orden"
  for c in "${COMANDOS[@]}"; do echo "  $VENV $MANAGE $c"; done
  echo
  echo "Vuelve a correrlo con --ejecutar para aplicar."
  exit 0
fi

for c in "${COMANDOS[@]}"; do
  log "ETL: $c"
  # shellcheck disable=SC2086  # la lista de arriba viene con sus propios flags
  "$VENV" "$MANAGE" $c
done

log "ETL terminado"
