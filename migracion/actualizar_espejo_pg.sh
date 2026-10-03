#!/usr/bin/env bash
# Pipeline completo del espejo legacy:
#   respaldo Oracle (exp clasico) -> Oracle local en Docker -> CSV -> PostgreSQL
# Refresca los esquemas sismai/inbdlar1/historico del espejo en PostgreSQL.
# El esquema `legacy` (T_*) NO viene en respaldos_sismai y queda intacto.
#
# En este equipo el plugin `docker compose` no existe y el shell hereda grupos
# antiguos, asi que se invoca asi:
#     newgrp docker -c "bash migracion/actualizar_espejo_pg.sh"
#
# Variables de entorno (valores por defecto):
#   CONT=sis_oracle_legacy      contenedor Oracle local
#   PUERTO=1529                 puerto host -> 1521
#   IMAGEN=gvenzl/oracle-xe:11.2.0.2
#   DUMPDIR=respaldo/respaldos_sismai
#   WORK=/var/tmp/espejo        directorio de artefactos (fuera de /tmp: tmpfs)
#   CSV_DIR=$WORK/csv
#   ESQUEMAS="sismai inbdlar1 historico"
#   VENV=./.venv/bin/python
#   ORA_PASS=oracle123
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ"

CONT="${CONT:-sis_oracle_legacy}"
PUERTO="${PUERTO:-1529}"
IMAGEN="${IMAGEN:-gvenzl/oracle-xe:11.2.0.2}"
DUMPDIR="${DUMPDIR:-respaldo/respaldos_sismai}"
WORK="${WORK:-/var/tmp/espejo}"
CSV_DIR="${CSV_DIR:-$WORK/csv}"
ESQUEMAS="${ESQUEMAS:-sismai inbdlar1 historico}"
VENV="${VENV:-$RAIZ/.venv/bin/python}"
ORA_PASS="${ORA_PASS:-oracle123}"
PG_CONT="${PG_CONT:-sis_postgres_dev}"

log() { printf '\n=== %s ===\n' "$*"; }

# 1) Asegurar el contenedor Oracle en marcha
log "Contenedor Oracle ($CONT)"
if ! docker inspect "$CONT" >/dev/null 2>&1; then
  docker run -d --name "$CONT" -p "${PUERTO}:1521" \
    -e ORACLE_PASSWORD="$ORA_PASS" \
    -e APP_USER=legacy -e APP_USER_PASSWORD=legacy123 \
    -v sis_oracle_legacy_data:/u01/app/oracle/oradata \
    -v "$RAIZ/legancy:/backup:ro" \
    "$IMAGEN"
elif [ "$(docker inspect -f '{{.State.Running}}' "$CONT")" != "true" ]; then
  docker start "$CONT"
fi
for _ in $(seq 1 60); do
  docker exec "$CONT" bash -lc \
    "echo 'select 1 from dual;' | sqlplus -s system/$ORA_PASS@XE" \
    >/dev/null 2>&1 && break
  sleep 10
done

docker exec "$CONT" bash -lc 'mkdir -p /tmp/dmp /tmp/csv'
docker cp "$DUMPDIR/." "$CONT:/tmp/dmp/"

# 2) Generar artefactos (parfiles, driver de export, conteos)
log "Generando artefactos en $WORK"
mkdir -p "$WORK" "$CSV_DIR"
esq_args=()
for e in $ESQUEMAS; do esq_args+=(--esquema "$e"); done
"$VENV" migracion/espejo_generar.py --salida "$WORK" "${esq_args[@]}"
cp migracion/espejo_crear_usuarios.sql "$WORK/"
docker cp "$WORK/." "$CONT:/tmp/dmp/"

# 3) Preparar usuarios Oracle (drop CASCADE + recrear)
log "Preparando usuarios Oracle"
docker exec "$CONT" bash -lc \
  "cd /tmp/dmp && sqlplus -s system/$ORA_PASS@XE @espejo_crear_usuarios.sql"

# 4) Importar cada esquema con imp clasico
for e in $ESQUEMAS; do
  U="$(echo "$e" | tr '[:lower:]' '[:upper:]')"
  log "Importando $U"
  docker exec "$CONT" bash -lc \
    "cd /tmp/dmp && imp system/$ORA_PASS@XE parfile=imp_$U.par"
done

# 5) Exportar a CSV
log "Exportando a CSV"
docker exec "$CONT" bash -lc \
  "cd /tmp/dmp && rm -f /tmp/csv/*.csv && sqlplus -s system/$ORA_PASS@XE @export.sql"

# 6) Traer los CSV al host
log "Copiando CSV a $CSV_DIR"
rm -rf "$CSV_DIR"; mkdir -p "$CSV_DIR"
docker cp "$CONT:/tmp/csv/." "$CSV_DIR/"

# 7) Cargar en PostgreSQL
log "Cargando en PostgreSQL"
"$VENV" migracion/cargar_espejo_pg.py --directorio "$CSV_DIR" --ejecutar

# 8) Verificar conteos Oracle vs PostgreSQL
log "Verificando conteos"
docker exec "$CONT" bash -lc \
  "cd /tmp/dmp && rm -f counts_oracle.txt && sqlplus -s system/$ORA_PASS@XE @counts_oracle.sql"
docker cp "$CONT:/tmp/dmp/counts_oracle.txt" "$WORK/counts_oracle.txt"
docker exec -i "$PG_CONT" psql -U sis_user -d sis_salud_db -t -A \
  < "$WORK/counts_pg.sql" > "$WORK/counts_pg.txt"
"$VENV" - "$WORK/counts_oracle.txt" "$WORK/counts_pg.txt" <<'PY'
import sys
def load(p):
    d = {}
    for l in open(p):
        l = l.strip()
        if l and l.count('|') == 2:
            s, t, c = l.split('|')
            d[(s.upper(), t.upper())] = int(c)
    return d
o, p = load(sys.argv[1]), load(sys.argv[2])
dif = [(k, o[k], p[k]) for k in o if k in p and o[k] != p[k]]
print(f"tablas: oracle={len(o)} pg={len(p)} diferencias={len(dif)}")
for k, a, b in dif[:20]:
    print("  ", k, a, b)
sys.exit(1 if (dif or set(o) != set(p)) else 0)
PY

log "Pipeline terminado"
