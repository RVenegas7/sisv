#!/usr/bin/env bash
# Prepara el entorno para validar un sobre REAL (routlar1_*.ZIP) contra lo que genera
# SISV con `exportar_rutalara`. Deja los artefactos en /tmp/opencode/ que consume
# `validar_sobre.py`.
#
# Qué hace:
#   1. Importa el routlar1.dmp del ZIP en un esquema ENVxx del Oracle local
#      `sis_oracle_legacy` (puerto 1529). Usa `imp` clásico.
#   2. Extrae de ese esquema los IDs y las columnas de cada T_* → ids_<env>.csv, cols_<env>.csv
#   3. Extrae el manifiesto T_EVENTOS del dmp y lo carga en PG (esquema simulacion)
#      → manifiesto_<env>.txt
#
# Uso:
#   ./preparar_entorno_validacion.sh <ZIP> <ESQUEMA>
# Ejemplo:
#   ./preparar_entorno_validacion.sh enviados/routlar1_14102026_1244.ZIP ENV14
#
# Requisitos: contenedor sis_oracle_legacy activo, contenedor sis_postgres_dev activo,
# y el usuario en el grupo docker → invocar con `newgrp docker -c "..."` si hace falta.
set -euo pipefail

ZIP="${1:?Uso: $0 <ZIP> <ESQUEMA>}"
ESQUEMA="${2:?Uso: $0 <ZIP> <ESQUEMA>}"
ENV_LC="$(echo "$ESQUEMA" | tr '[:upper:]' '[:lower:]')"
CONT_ORA=sis_oracle_legacy
CONT_PG=sis_postgres_dev
ORA_PASS="${ORA_PASS:-oracle123}"
WORK=/tmp/opencode
mkdir -p "$WORK"

echo "== 1. Importando $ZIP como esquema $ESQUEMA en $CONT_ORA =="
TI=$(mktemp -d)
unzip -o -q "$ZIP" -d "$TI"
DMP="$(find "$TI" -name '*.dmp' | head -1)"
[ -n "$DMP" ] || { echo "ERROR: el ZIP no trae .dmp"; exit 1; }

docker exec "$CONT_ORA" bash -lc "echo \"DROP USER $ESQUEMA CASCADE;\" | sqlplus -s system/$ORA_PASS@XE" >/dev/null 2>&1 || true
docker exec "$CONT_ORA" bash -lc "echo \"CREATE USER $ESQUEMA IDENTIFIED BY $ESQUEMA DEFAULT TABLESPACE USERS QUOTA UNLIMITED ON USERS; GRANT CONNECT,RESOURCE TO $ESQUEMA;\" | sqlplus -s system/$ORA_PASS@XE"
docker cp "$DMP" "$CONT_ORA:/tmp/routlar1.dmp"
docker exec "$CONT_ORA" bash -lc \
  "imp USERID=system/$ORA_PASS FILE=/tmp/routlar1.dmp FROMUSER=$ESQUEMA TOUSER=$ESQUEMA INDEXES=N CONSTRAINTS=N GRANTS=N IGNORE=Y LOG=/tmp/imp.log; tail -5 /tmp/imp.log"

echo "== 2. Extrayendo IDs y columnas de cada T_* =="
cat > "$WORK/_ids.sql" <<SQL
SET PAGES 0 FEED OFF COLSEP ,
SPOOL /tmp/ids_${ENV_LC}.csv
$(python3 - "$ESQUEMA" <<'PY'
import json, sys
owner = sys.argv[1]
spec = json.load(open("backend/registros/data/rutarala_spec.json"))
destinos = {v[1] for v in spec["mapeo"].values()} | {"T_AUDITORIA"}
for t in sorted(destinos):
    print(f"PROMPT @@{t}")
    print(f"SELECT '{t},'||TO_CHAR(\"ID\",'TM9') FROM {owner}.\"{t}\" ORDER BY \"ID\";")
PY
)
SPOOL OFF
EXIT
SQL

cat > "$WORK/_cols.sql" <<SQL
SET PAGES 0 FEED OFF COLSEP ,
SPOOL /tmp/cols_${ENV_LC}.csv
SELECT table_name||','||column_id||','||column_name FROM all_tab_columns WHERE owner='$ESQUEMA' ORDER BY table_name, column_id;
SPOOL OFF
EXIT
SQL

docker cp "$WORK/_ids.sql"  "$CONT_ORA:/tmp/_ids.sql"
docker cp "$WORK/_cols.sql" "$CONT_ORA:/tmp/_cols.sql"
docker exec "$CONT_ORA" bash -lc "sqlplus -s system/$ORA_PASS@XE @/tmp/_ids.sql >/dev/null 2>&1; sqlplus -s system/$ORA_PASS@XE @/tmp/_cols.sql >/dev/null 2>&1"
docker cp "$CONT_ORA:/tmp/ids_${ENV_LC}.csv"  "$WORK/ids_${ENV_LC}.csv"
docker cp "$CONT_ORA:/tmp/cols_${ENV_LC}.csv" "$WORK/cols_${ENV_LC}.csv"

echo "== 3. Cargando manifiesto T_EVENTOS en PostgreSQL (esquema simulacion) =="
cat > "$WORK/_ev.sql" <<SQL
SET PAGES 0 FEED OFF COLSEP '|'
SPOOL /tmp/eventos_${ENV_LC}.csv
SELECT "TABLA"||'|'||"EVENTO"||'|'||TO_CHAR("FECHA",'YYYY-MM-DD HH24:MI:SS')||'|'||TO_CHAR("ID",'TM9') FROM $ESQUEMA."T_EVENTOS" ORDER BY "TABLA","ID","FECHA" DESC;
SPOOL OFF
EXIT
SQL
docker cp "$WORK/_ev.sql" "$CONT_ORA:/tmp/_ev.sql"
docker exec "$CONT_ORA" bash -lc "sqlplus -s system/$ORA_PASS@XE @/tmp/_ev.sql >/dev/null 2>&1"
docker cp "$CONT_ORA:/tmp/eventos_${ENV_LC}.csv" "$WORK/manifiesto_${ENV_LC}.txt"

docker exec "$CONT_PG" psql -U sis_user -d sis_salud_db -q -c "CREATE SCHEMA IF NOT EXISTS simulacion;"
docker exec "$CONT_PG" psql -U sis_user -d sis_salud_db -q -c \
  "DROP TABLE IF EXISTS simulacion.eventos_${ENV_LC}; CREATE TABLE simulacion.eventos_${ENV_LC} (\"TABLA\" text, \"EVENTO\" text, \"FECHA\" timestamp, \"ID\" bigint);"
docker cp "$WORK/manifiesto_${ENV_LC}.txt" "$CONT_PG:/tmp/eventos_${ENV_LC}.csv"
docker exec "$CONT_PG" psql -U sis_user -d sis_salud_db -q -c \
  "\\copy simulacion.eventos_${ENV_LC} FROM '/tmp/eventos_${ENV_LC}.csv' WITH (FORMAT csv, DELIMITER '|')"

echo
echo "Listo. Artefactos en $WORK:"
echo "  ids_${ENV_LC}.csv  cols_${ENV_LC}.csv  manifiesto_${ENV_LC}.txt"
echo "Siguiente: python3 migracion/simulacion/validar_sobre.py $ESQUEMA"
