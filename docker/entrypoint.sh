#!/usr/bin/env bash
# Arranque del contenedor SISV: espera a PostgreSQL, aplica migraciones y sirve con gunicorn.
# El contenedor se levanta con `--restart always`, así que este script se repite en cada
# arranque del daemon de Docker y la aplicación vuelve sola tras un reinicio del equipo.
set -euo pipefail

PUERTO="${PUERTO:-8000}"
TRABAJADORES="${GUNICORN_WORKERS:-3}"
ESPERA="${GUNICORN_TIMEOUT:-120}"

echo "[SISV] Base de datos: ${DB_HOST:-host.docker.internal}:${DB_PORT:-5436}/${DB_NAME:-sis_salud_db}"
python - <<'PY'
import os
import socket
import sys
import time

host = os.environ.get("DB_HOST", "host.docker.internal")
puerto = int(os.environ.get("DB_PORT", "5436"))
limite = int(os.environ.get("DB_ESPERA_SEGUNDOS", "120"))
inicio = time.time()
while True:
    try:
        with socket.create_connection((host, puerto), timeout=3):
            print(f"[SISV] PostgreSQL responde en {host}:{puerto}")
            break
    except OSError as exc:
        if time.time() - inicio > limite:
            print(
                f"[SISV] No se pudo conectar a PostgreSQL en {host}:{puerto} ({exc}). "
                "¿Está arriba el contenedor de la base?",
                file=sys.stderr,
            )
            sys.exit(1)
        time.sleep(2)
PY

echo "[SISV] Aplicando migraciones…"
python manage.py migrate --noinput

echo "[SISV] Recolectando estáticos…"
python manage.py collectstatic --noinput >/dev/null

if [ "${SISV_SEMBRAR_DEMO:-0}" = "1" ]; then
  echo "[SISV] Sembrando datos/usuarios demo (idempotente)…"
  python manage.py sembrar_demo || true
fi

echo "[SISV] Sirviendo en 0.0.0.0:${PUERTO} (${TRABAJADORES} trabajadores)"
exec gunicorn sisv_backend.wsgi:application \
  --bind "0.0.0.0:${PUERTO}" \
  --workers "${TRABAJADORES}" \
  --timeout "${ESPERA}" \
  --access-logfile - \
  --error-logfile -
