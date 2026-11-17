# SISV — imagen única: Django (gunicorn) sirve el API y el frontend compilado.
#
#   docker build -t sisv:latest .
#   docker run -d --name sisv_app --restart always -p 8020:8000 --env-file docker/sisv.env \
#              --add-host host.docker.internal:host-gateway sisv:latest
#
# o, más simple, ./docker/levantar.sh
#
# La base de datos NO va dentro de la imagen: es el contenedor PostgreSQL existente
# (`sis_postgres_dev`, puerto 5436) con su volumen `sis_postgres_data`, que también arranca
# solo (`--restart always`). Al iniciar el daemon de Docker suben los dos.

# --------------------------------------------------------------------------- frontend
FROM node:22-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# --------------------------------------------------------------------------- backend
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=America/Caracas \
    PUERTO=8000 \
    GUNICORN_WORKERS=3 \
    GUNICORN_TIMEOUT=120

# tzdata: Django usa America/Caracas (sin la base de zonas, falla al arrancar).
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ /app/
COPY --from=frontend /frontend/dist /app/frontend_dist
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh

# collectstatic necesita importar settings (SECRET_KEY real solo en ejecución; aquí vale
# cualquier valor y no se conecta a la base).
ARG DJANGO_SECRET_KEY=solo-para-construir-la-imagen
ENV DJANGO_DEBUG=0 \
    DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
RUN mkdir -p /app/staticfiles \
    && python manage.py collectstatic --noinput \
    && useradd --create-home --shell /bin/bash sisv \
    && chown -R sisv:sisv /app \
    && chmod +x /usr/local/bin/entrypoint.sh

# La clave de construcción no debe sobrevivir: vacía = el arranque falla con un mensaje
# claro si el entorno no define DJANGO_SECRET_KEY (docker/sisv.env lo hace).
ENV DJANGO_SECRET_KEY=""
USER sisv

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/', timeout=4)"

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
