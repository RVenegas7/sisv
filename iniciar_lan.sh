#!/usr/bin/env bash
# Levanta SISV (Django + Vite) accesible desde CUALQUIER dispositivo de la red local:
#   - backend  → http://0.0.0.0:8000
#   - frontend → http://0.0.0.0:5173  (el celular/otra PC entra solo por este puerto)
# Uso:  ./iniciar_lan.sh        (Ctrl+C detiene ambos)
cd "$(dirname "${BASH_SOURCE[0]}")"

IP=$(hostname -I 2>/dev/null | awk '{print $1}')
if [ -z "$IP" ]; then
  IP=$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{print $7; exit}')
fi
IP=${IP:-127.0.0.1}

echo "──────────────────────────────────────────────────────────────"
echo "  SISV en red local"
echo "  En tu computador : http://localhost:5173"
echo "  Desde el celular : http://${IP}:5173"
echo "  Backend (opcional): http://${IP}:8000/api/"
echo "  (usuarios demo: admin / laraepid / codificadora / hbcentral, clave Sisv.2026!)"
echo "  ✓ Ctrl+C para detener ambos servicios"
echo "──────────────────────────────────────────────────────────────"

./.venv/bin/python backend/manage.py runserver 0.0.0.0:8000 --noreload &
DJANGO_PID=$!
trap 'kill "$DJANGO_PID" 2>/dev/null || true' EXIT

(cd frontend && exec npm run dev -- --host 0.0.0.0)