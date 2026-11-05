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
#   MONTAR=0                    1 = monta DUMPDIR y CSV_DIR en el contenedor
#                               en vez de copiarlos con `docker cp`.
#
# `MONTAR=1` nacio el 04/11/2026 porque la raiz de este equipo estaba al 100 %
# (281 MB libres) y `docker cp` de los 1,2 GB de .dmp + 0,7 GB de CSV dentro del
# contenedor (que vive en /var/lib/docker, o sea en /) no cabia. Con montajes los
# artefactos se quedan en /home y el contenedor solo escribe en su volumen.
# Ojo: los montajes se fijan al CREAR el contenedor; si ya existe sin ellos el
# script aborta y hay que borrarlo (`docker rm sis_oracle_legacy`, el volumen
# `sis_oracle_legacy_data` se conserva).
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
MONTAR="${MONTAR:-0}"

log() { printf '\n=== %s ===\n' "$*"; }

# Espera a que la instancia abra. OJO: SQL*Plus devuelve 0 aunque la conexion
# falle (p. ej. ORA-12514 mientras el listener ya escucha pero la instancia
# todavia no se registro), asi que comprobar el CODIGO DE SALIDA daba "listo" al
# instante y el pipeline seguia contra una base cerrada (visto el 04/11/2026:
# ORA-12541 en el paso 3). Lo que se comprueba es la SALIDA del SELECT: solo
# vale si imprime un 1.
esperar_oracle() {
  local listo=0
  for _ in $(seq 1 60); do
    if docker exec "$CONT" bash -lc \
         "echo 'select 1 from dual;' | sqlplus -s system/$ORA_PASS@XE" 2>/dev/null \
         | grep -qE '^[[:space:]]*1[[:space:]]*$'; then
      listo=1; break
    fi
    sleep 10
  done
  if [ "$listo" != 1 ]; then
    echo " [FALLO] la instancia XE no responde despues de 10 minutos."
    echo "         Revisa: docker logs $CONT --tail 40"
    exit 1
  fi
}

# Semantica de longitud de los VARCHAR2. El dump trae `VARCHAR2(n)` SIN BYTE ni
# CHAR, asi que la decide la base destino. Con BYTE (el defecto de este XE) un
# texto con acentos ocupa 2 bytes por caracter y las filas que llegan justo al
# limite se rechazan: `imp` avisa con IMP-00019/ORA-12899, SIGUE y termina "OK",
# asi que la perdida es silenciosa. El 04/11/2026 se perdieron 194 filas
# (CERTNACIMIENTO 50, NAC_MADRE 35, CASOS_MMI 2, CIE10 37...), entre ellas
# certificados y madres que el ETL necesita. Con CHAR quedan como
# VARCHAR2(n CHAR) y no se pierde ninguna. Se fija en el SPFILE (persiste en el
# volumen) y se reinicia una sola vez.
asegurar_semantica_char() {
  local sem
  sem="$(docker exec -i "$CONT" bash -lc 'sqlplus -s / as sysdba' <<'SQL'
set pagesize 0 feedback off heading off
select value from v$parameter where name='nls_length_semantics';
exit;
SQL
  )"
  sem="$(echo "$sem" | tr -d '[:space:]' | grep -oE 'BYTE|CHAR' | head -1)"
  if [ "$sem" = "CHAR" ]; then
    echo " [ OK ]   NLS_LENGTH_SEMANTICS=CHAR"
    return 0
  fi
  echo " [AVISO] NLS_LENGTH_SEMANTICS=${sem:-desconocida}: se fija en CHAR (SPFILE) y se reinicia"
  docker exec -i "$CONT" bash -lc 'sqlplus -s / as sysdba' <<'SQL'
ALTER SYSTEM SET NLS_LENGTH_SEMANTICS=CHAR SCOPE=SPFILE;
exit;
SQL
  docker restart "$CONT" >/dev/null
  esperar_oracle
  echo " [ OK ]   NLS_LENGTH_SEMANTICS=CHAR tras el reinicio"
}

# 1) Asegurar el contenedor Oracle en marcha
log "Contenedor Oracle ($CONT)"
MONTAS=()
if [ "$MONTAR" = 1 ]; then
  mkdir -p "$CSV_DIR"
  # El Oracle del contenedor corre como uid 54321 y escribe los CSV con UTL_FILE:
  # sobre un bind mount del host necesita permiso de escritura real, y el duenio
  # del directorio es el usuario de la sesion. Sin esto el export falla con
  # ORA-29283 (invalid file operation).
  chmod 777 "$CSV_DIR" 2>/dev/null || true
  MONTAS=(-v "$(cd "$DUMPDIR" && pwd):/dmp:ro" -v "$(cd "$CSV_DIR" && pwd):/tmp/csv")
fi
if ! docker inspect "$CONT" >/dev/null 2>&1; then
  docker run -d --name "$CONT" -p "${PUERTO}:1521" \
    -e ORACLE_PASSWORD="$ORA_PASS" \
    -e APP_USER=legacy -e APP_USER_PASSWORD=legacy123 \
    -v sis_oracle_legacy_data:/u01/app/oracle/oradata \
    -v "$RAIZ/legancy:/backup:ro" \
    ${MONTAS[@]+"${MONTAS[@]}"} \
    "$IMAGEN"
elif [ "$MONTAR" = 1 ] && \
     ! docker inspect -f '{{range .Mounts}}{{.Destination}} {{end}}' "$CONT" | grep -q '/dmp'; then
  echo " [FALLO] $CONT existe sin los montajes de MONTAR=1."
  echo "         Borralo (el volumen de datos se conserva) y reintenta:"
  echo "           docker rm $CONT"
  exit 1
elif [ "$(docker inspect -f '{{.State.Running}}' "$CONT")" != "true" ]; then
  docker start "$CONT"
fi
esperar_oracle
asegurar_semantica_char

docker exec "$CONT" bash -lc 'mkdir -p /tmp/dmp /tmp/csv'
if [ "$MONTAR" = 1 ]; then
  # Los .dmp se leen del montaje (/dmp). `imp` abre su bitacora en el directorio
  # actual, y /dmp es de solo lectura, asi que se enlazan desde /tmp/dmp: asi el
  # parfile (que dice FILE=SISMAI.dmp, sin ruta) sigue funcionando igual y el
  # .log se escribe en el contenedor.
  log "Los .dmp se leen del montaje (/dmp); se enlazan en /tmp/dmp"
  docker exec "$CONT" bash -lc 'for f in /dmp/*.dmp; do ln -sf "$f" /tmp/dmp/; done; ls -l /tmp/dmp/*.dmp'
else
  docker cp "$DUMPDIR/." "$CONT:/tmp/dmp/"
fi

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
docker exec -e NLS_LENGTH_SEMANTICS=CHAR "$CONT" bash -lc \
  "cd /tmp/dmp && sqlplus -s system/$ORA_PASS@XE @espejo_crear_usuarios.sql"

# 4) Importar cada esquema con imp clasico
# `NLS_LENGTH_SEMANTICS=CHAR` va en el ENTORNO del cliente: imp fija la semantica
# de su sesion desde su propio NLS y no hereda la del servidor. Sin esto las
# tablas se crean VARCHAR2(n BYTE) aunque la instancia diga CHAR, y las filas con
# acentos que llegan al limite se rechazan en silencio (IMP-00019/ORA-12899).
for e in $ESQUEMAS; do
  U="$(echo "$e" | tr '[:lower:]' '[:upper:]')"
  log "Importando $U"
  docker exec -e NLS_LENGTH_SEMANTICS=CHAR "$CONT" bash -lc \
    "cd /tmp/dmp && imp system/$ORA_PASS@XE parfile=imp_$U.par" 2>&1 | tee "$WORK/imp_$U.log"
done

# 4b) Reparar los rechazos por semantica BYTE (ver espejo_reparar_rechazos.py).
# `imp` recrea las columnas con la semantica del ORIGEN (BYTE) e ignora
# NLS_LENGTH_SEMANTICS del cliente y del servidor, asi que las filas con acentos
# que llegan al limite se pierden en silencio (IMP-00019/ORA-12899). El
# reparador las detecta en imp_*.log, pasa la columna a CHAR y reimporta esas
# tablas. Sin esto el 04/11/2026 se perdieron 194 filas.
log "Reparando rechazos de imp (semantica BYTE)"
"$VENV" migracion/espejo_reparar_rechazos.py --work "$WORK" \
  --contenedor "$CONT" --ora-pass "$ORA_PASS" --ejecutar

# 5) Exportar a CSV
log "Exportando a CSV"
docker exec "$CONT" bash -lc \
  "cd /tmp/dmp && rm -f /tmp/csv/*.csv && sqlplus -s system/$ORA_PASS@XE @export.sql"

# 6) Traer los CSV al host
if [ "$MONTAR" = 1 ]; then
  log "Los CSV ya estan en $CSV_DIR (montaje); no se copian"
else
  log "Copiando CSV a $CSV_DIR"
  rm -rf "$CSV_DIR"; mkdir -p "$CSV_DIR"
  docker cp "$CONT:/tmp/csv/." "$CSV_DIR/"
fi

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
