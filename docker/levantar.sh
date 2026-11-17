#!/usr/bin/env bash
# Construye y levanta SISV en Docker, dejándolo con `--restart always`.
#
#   ./docker/levantar.sh              # build + (re)arranque
#   ./docker/levantar.sh --sin-build  # solo reinicia el contenedor existente
#   PUERTO=8021 ./docker/levantar.sh  # otro puerto en el host
#
# La base de datos NO se levanta aquí: es `sis_postgres_dev` (puerto 5436), que ya corre
# con `--restart always` y conserva los datos en el volumen `sis_postgres_data`.
#
# Este equipo no tiene el plugin `docker compose`; por eso se usa docker build/run.
# Equivale al servicio `app` de docker-compose.yml.
set -euo pipefail

cd "$(dirname "$0")/.."

IMAGEN="${IMAGEN:-sisv:latest}"
NOMBRE="${NOMBRE:-sisv_app}"
PUERTO="${PUERTO:-8020}"
ENVFILE="${ENVFILE:-docker/sisv.env}"

if ! docker info >/dev/null 2>&1; then
  echo "No se puede hablar con el daemon de Docker." >&2
  echo "Si el usuario pertenece al grupo docker pero la sesión es vieja, use:" >&2
  echo "  newgrp docker -c \"./docker/levantar.sh\"" >&2
  exit 1
fi

if [ ! -f "$ENVFILE" ]; then
  echo "Falta $ENVFILE." >&2
  echo "Créelo con: cp docker/sisv.env.example $ENVFILE   (y cambie DJANGO_SECRET_KEY)" >&2
  exit 1
fi

if [ "${1:-}" != "--sin-build" ]; then
  echo "== Construyendo la imagen ${IMAGEN} (frontend + backend) =="
  docker build -t "$IMAGEN" .
fi

if docker ps -a --format '{{.Names}}' | grep -qx "$NOMBRE"; then
  echo "== Deteniendo el contenedor anterior ${NOMBRE} =="
  docker rm -f "$NOMBRE" >/dev/null
fi

echo "== Levantando ${NOMBRE} en el puerto ${PUERTO} =="
docker run -d \
  --name "$NOMBRE" \
  --restart always \
  -p "${PUERTO}:8000" \
  --env-file "$ENVFILE" \
  --add-host host.docker.internal:host-gateway \
  "$IMAGEN" >/dev/null

echo
echo "SISV levantado. Primeros segundos (migraciones y estáticos):"
echo "  docker logs -f ${NOMBRE}"
IP=$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{for (i = 1; i <= NF; i++) if ($i == "src") {print $(i + 1); exit}}')
echo
echo "  Local : http://localhost:${PUERTO}"
[ -n "$IP" ] && echo "  Red   : http://${IP}:${PUERTO}"
echo
echo "Queda con --restart always: al iniciar Docker, la aplicación sube sola."
echo "Para detenerla: docker stop ${NOMBRE}"
