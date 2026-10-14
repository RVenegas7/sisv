#!/usr/bin/env bash
# Levanta SISV (Django + Vite) accesible desde CUALQUIER dispositivo de la red local:
#   - backend  → http://0.0.0.0:<puerto-backend>
#   - frontend → http://0.0.0.0:<puerto-frontend>  (el celular/otra PC entra solo por este puerto)
# Los puertos se detectan solos: el 8000/5173 pueden estar ocupados por otros contenedores
# (p. ej. `banco_sangre-app-1` escucha en 127.0.0.1:8000), así que se toma el primero libre.
# Uso:  ./iniciar_lan.sh        (Ctrl+C detiene ambos)
cd "$(dirname "${BASH_SOURCE[0]}")"

# ── Puerto libre ──────────────────────────────────────────────────────────────
# ¿Hay algo escuchando en ese puerto, en cualquier interfaz?
_puerto_ocupado() {
  ss -ltn 2>/dev/null | awk 'NR > 1 {print $4}' | grep -qE "[:.]${1}\$"
}

# Primer puerto libre de la lista; si todos están ocupados, el SO asigna uno efímero.
_elegir_puerto() {
  local p
  for p in "$@"; do
    if ! _puerto_ocupado "$p"; then printf '%s' "$p"; return 0; fi
  done
  ./.venv/bin/python -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])'
}

PUERTO_BACKEND="$(_elegir_puerto 8000 8001 8002 8003 8004 8005 8006 8007 8008 8009)"
PUERTO_FRONTEND="$(_elegir_puerto 5173 5174 5175 5176 5177 5178)"

# ── IP de la red local ────────────────────────────────────────────────────────
IP=$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{for (i = 1; i <= NF; i++) if ($i == "src") {print $(i + 1); exit}}')
[ -z "$IP" ] && IP=$(hostname -I 2>/dev/null | awk '{print $1}')
IP=${IP:-127.0.0.1}

# ── Orígenes confiables para el CSRF ──────────────────────────────────────────
# El navegador habla con Django a través del proxy de Vite: su Origin es el del frontend
# (http://IP:<puerto-frontend>), así que hay que confiarlo o el login/POST da 403.
_ORIGENES="http://localhost:${PUERTO_FRONTEND},http://127.0.0.1:${PUERTO_FRONTEND},"
_ORIGENES="${_ORIGENES}http://localhost:${PUERTO_BACKEND},http://127.0.0.1:${PUERTO_BACKEND}"
if [ "$IP" != "127.0.0.1" ]; then
  _ORIGENES="${_ORIGENES},http://${IP}:${PUERTO_FRONTEND},http://${IP}:${PUERTO_BACKEND}"
fi
export DJANGO_CSRF_TRUSTED_ORIGINS="${DJANGO_CSRF_TRUSTED_ORIGINS:+${DJANGO_CSRF_TRUSTED_ORIGINS},}${_ORIGENES}"

# ── Entorno de desarrollo ─────────────────────────────────────────────────────
# DEBUG=1 hace falta para probar por HTTP: sin él las cookies de sesión llevan `Secure`
# y el login desde el celular (http://) se rechaza. Exporta DJANGO_DEBUG=0 para anularlo.
export DJANGO_DEBUG="${DJANGO_DEBUG:-1}"
export DJANGO_ALLOWED_HOSTS="${DJANGO_ALLOWED_HOSTS:-*}"
export VITE_API_PROXY="http://127.0.0.1:${PUERTO_BACKEND}"

echo "──────────────────────────────────────────────────────────────"
echo "  SISV en red local"
echo "  En tu computador  : http://localhost:${PUERTO_FRONTEND}"
echo "  Desde el celular  : http://${IP}:${PUERTO_FRONTEND}"
echo "  Backend (opcional): http://${IP}:${PUERTO_BACKEND}/api/  (el frontend enruta /api ahí)"
echo "  (usuarios demo: admin / laraepid / codificadora / hbcentral, clave Sisv.2026!)"
echo "  ✓ Ctrl+C para detener ambos servicios"
echo "──────────────────────────────────────────────────────────────"

./.venv/bin/python backend/manage.py runserver "0.0.0.0:${PUERTO_BACKEND}" --noreload &
DJANGO_PID=$!
trap 'kill "$DJANGO_PID" 2>/dev/null || true' EXIT

(cd frontend && exec npm run dev -- --host 0.0.0.0 --port "${PUERTO_FRONTEND}")
