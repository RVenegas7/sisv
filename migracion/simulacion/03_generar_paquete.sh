#!/usr/bin/env bash
# =============================================================================
#  03_generar_paquete.sh
#  SISV — Simulación del paquete semanal: arma un ZIP con la misma estructura
#  del que el legacy envía al nivel central, a partir de lo que dejó
#  replicar_controlado.sql en el espejo, y lo compara con el original.
#
#  Los 5 archivos del paquete real (routlar1_482026_1526.ZIP, 04/08/2026):
#     routlar1.dmp       exp del usuario TEMP  -> las 83 tablas T_*
#     routlar1.log       log de ese exp        -> "N rows exported" por tabla
#     repllar1.log       spool de la fase de replicacion
#     copyhistlar1.log   spool de la fase de historial
#     bloqlar1.log       spool de la fase de bloqueo
#
#  Qué es real y qué no en la simulación:
#     REAL  -> routlar1.dmp y routlar1.log (exp de verdad del usuario TEMP)
#     REAL  -> repllar1.log (es la salida de replicar_controlado.sql, que hace
#             de fase de replicación)
#     STUB  -> copyhistlar1.log y bloqlar1.log. Esas dos fases no están
#             reconstruidas (ver PENDIENTES.md 17.13); se generan como
#             marcadores para que el ZIP tenga los 5 archivos y se pueda
#             medir el tamaño y la estructura, NO para simular su contenido.
#
#  Uso:
#    ./migracion/simulacion/03_generar_paquete.sh [contenedor] [ref_zip]
#  Por defecto: contenedor sis_oracle_legacy, ref enviados/routlar1_482026_1526.ZIP
# =============================================================================
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
CONT="${1:-sis_oracle_legacy}"
REF="${2:-$RAIZ/enviados/routlar1_482026_1526.ZIP}"
SALIDA="$RAIZ/auditoria/simulacion"
USUARIO="system/oracle123@XE"
FECHA_LARGA="$(date +%d%m%Y)"
FECHA_CORTA="$(date +%H%M)"
NOMBRE="routlar1_${FECHA_LARGA}_${FECHA_CORTA}"
WORK="$(mktemp -d /tmp/paq.XXXXXX)"
trap 'rm -rf "$WORK"' EXIT

info() { echo "  $*"; }
die()  { echo "ERROR: $*" >&2; exit 1; }

command -v docker >/dev/null || die "se necesita docker"
[ -n "$(docker ps -q -f "name=^${CONT}$")" ] || die "el contenedor $CONT no esta corriendo"
mkdir -p "$SALIDA"

echo
echo "==============================================================="
echo "  Generando el paquete simulado  ->  $NOMBRE.ZIP"
echo "==============================================================="

# --- 1. exp del usuario TEMP (lo que produce routlar1.dmp + routlar1.log) ----
info "1. exp del usuario TEMP (routlar1.dmp + routlar1.log)"
docker exec "$CONT" bash -c "cd /tmp && rm -f routlar1.dmp routlar1.log && \
  exp $USUARIO owner=TEMP file=routlar1.dmp log=routlar1.log \
      statistics=NONE consistent=N; echo \"rc=\$?\"" > "$WORK/exp.txt" 2>&1
docker cp "$CONT":/tmp/routlar1.dmp "$WORK/routlar1.dmp" >/dev/null
docker cp "$CONT":/tmp/routlar1.log "$WORK/routlar1.log" >/dev/null
[ -s "$WORK/routlar1.dmp" ] || { cat "$WORK/exp.txt"; die "el exp no produjo dump"; }
info "   dmp: $(du -h "$WORK/routlar1.dmp" | cut -f1)   log: $(du -h "$WORK/routlar1.log" | cut -f1)"

# --- 2. repllar1.log: la salida de la fase de replicacion -------------------
info "2. repllar1.log"
if [ -f "${DIR_AUDIT:-"$RAIZ/auditoria"}/replicar_ejecucion.txt" ]; then
  cp "${DIR_AUDIT:-"$RAIZ/auditoria"}/replicar_ejecucion.txt" "$WORK/repllar1.log"
else
  docker exec "$CONT" bash -c "test -f /tmp/rep_run.sql && echo existe" >/dev/null 2>&1 \
    && die "falta ${DIR_AUDIT:-"$RAIZ/auditoria"}/replicar_ejecucion.txt (guarde la salida de replicar_controlado.sql)"
fi

# --- 3. y 4. las dos fases que NO estan reconstruidas ------------------------
info "3. copyhistlar1.log y 4. bloqlar1.log (STUB: fases no reconstruidas)"
cat > "$WORK/copyhistlar1.log" <<'EOF'

-- STUB de simulacion. La fase copyhist (historial: T_AUDITORIA y el respaldo
-- de la semana anterior) NO esta reconstruida. En el paquete real del
-- 04/08/2026 este log decía:
--     9862 rows updated. / 34 rows created. / 9118 rows updated.
-- Ver PENDIENTES.md 17.13.

EOF
cat > "$WORK/bloqlar1.log" <<'EOF'

-- STUB de simulacion. La fase de bloqueo no esta reconstruida. En el paquete
-- real del 04/08/2026 este log tenia 2 lineas "System altered.".

EOF

# --- 5. el ZIP con los 5 archivos -------------------------------------------
info "5. empaquetando"
( cd "$WORK" && zip -q -X "$SALIDA/$NOMBRE.ZIP" \
    routlar1.dmp routlar1.log repllar1.log copyhistlar1.log bloqlar1.log )

ZIP="$SALIDA/$NOMBRE.ZIP"
info "   $ZIP  ($(du -h "$ZIP" | cut -f1))"

# --- 6. comparacion con el paquete real --------------------------------------
echo
echo "--- comparacion con el paquete real ---"
info "archivos"
unzip -l "$ZIP"    | sed -n '4,12p'
echo
info "tamano de cada archivo"
printf "  %-20s %12s %12s\n" ARCHIVO REAL SIMULADO
for f in routlar1.dmp routlar1.log repllar1.log copyhistlar1.log bloqlar1.log; do
  r=$(unzip -l "$REF" "$f" 2>/dev/null | awk 'NR==4{print $1}')
  s=$(stat -c%s "$WORK/$f")
  printf "  %-20s %12s %12s\n" "$f" "${r:-0}" "$s"
done
echo
info "conteos por tabla del log de exp: real vs simulado"
python3 - "$REF" "$WORK/routlar1.log" <<'PYEOF'
import re, sys, zipfile
ref_zip, sim_log = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(ref_zip) as z:
    real = z.read('routlar1.log').decode('latin-1')
sim = open(sim_log, encoding='latin-1').read()

def parse(txt):
    """Acepta los dos formatos de exp: 10.1 pone el conteo en la linea
    siguiente, 11.2 lo pone en la misma linea."""
    out, cur = {}, None
    for ln in txt.replace('\r', '\n').splitlines():
        m = re.search(r'exporting table\s+(\S+)', ln)
        if m:
            cur = m.group(1)
            n = re.search(r'([\d,]+)\s+rows? exported', ln)
            if n:
                out[cur] = int(n.group(1).replace(',', ''))
                cur = None
            continue
        n = re.search(r'^\s*([\d,]+)\s+rows? exported', ln)
        if n and cur:
            out[cur] = int(n.group(1).replace(',', ''))
            cur = None
    return out

r, s = parse(real), parse(sim)
print(f"  {'TABLA':<15}{'REAL':>8}{'SIMULADO':>10}   ESTADO")
ig = 0
for t in sorted(set(r) | set(s)):
    a, b = r.get(t), s.get(t)
    ok = (a == b)
    ig += ok
    print(f"  {t:<15}{str(a):>8}{str(b):>10}   {'ok' if ok else '<-- DIFERIE'}")
print(f"\n  tablas exportadas: real {len(r)}, simulado {len(s)}; identicas: {ig}")
print(f"  filas totales     : real {sum(r.values())}, simulado {sum(s.values())}")
if ig == len(r) == len(s):
    print("  >>> los conteos por tabla del exp coinciden con los del paquete real")
else:
    print("  >>> hay diferencias de conteo")
PYEOF
