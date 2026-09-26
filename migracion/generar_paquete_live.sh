#!/usr/bin/env bash
# =============================================================================
#  generar_paquete_live.sh
#  SISV — Arma el sobre semanal (los 5 archivos) contra el Oracle de SIS/Lara
#  (srvsis / 192.168.5.200, SID lar1) cuando NO se puede usar la aplicacion
#  (RoutLar1 / SistemaTransferencia.exe del cliente Windows).
#  Ver PENDIENTES.md 17.13 y 17.14.
# -----------------------------------------------------------------------------
#  QUE HACE Y QUE NO HACE
#    - El `exp` del usuario TEMP y su log: REAL (es el que produce routlar1.dmp
#      y routlar1.log, los dos archivos grandes del sobre).
#    - repllar1.log: la salida de replicar_controlado_live.sh, que hace de fase
#      de replicacion. REAL, pero solo si se le pasa el log de la corrida del dia.
#    - copyhistlar1.log y bloqlar1.log: las fases NO estan reconstruidas. Por
#      defecto este guion SE NIEGA a inventarlas; con --con-stub escribe marcadores
#      y avisa por pantalla de que el sobre queda incompleto.
#    - NO envia nada al central, NO trunca la cola, NO escribe en la base.
#      Un `exp` solo lee.
# -----------------------------------------------------------------------------
#  LO QUE LE FALTA AL SOBRE CON RESPECTO AL ORIGINAL (importante al reportar)
#    - T_AUDITORIA (9.118 filas en el paquete del 04/08) queda vacia: la llenaba
#      la fase copyhist, que no esta reconstruida.
#    - Las ~60 T_* que no estan en el mapeo salen vacias. El plan B no las
#      limpia: si tienen filas viejas de una corrida anterior, el exp se las
#      lleva igual. Por eso el preflight las cuenta y BLOQUEA si hay alguna.
#    - Los 2 logs stub no son los del original.
#    => Es una recuperacion parcial. Si el central lo rechaza, escalar al
#       soporte SIS/Centura (ver PENDIENTES.md 17.7).
# -----------------------------------------------------------------------------
#  USO
#    # 1) Preflight: SOLO LECTURA, se puede con el sistema en uso.
#    ./migracion/generar_paquete_live.sh preflight
#
#    # 2) Armar el sobre (pide frase; con --con-stub pide doble confirmacion)
#    ./migracion/generar_paquete_live.sh armar
#    ./migracion/generar_paquete_live.sh armar --con-stub
#
#  Variables de entorno:
#    HOST, USUARIO, CLAVE, ORACLE_SID, SQLPLUS, DIR_SERV, DESTINO
#    El usuario por defecto (respaldo) probablemente NO pueda exportar el
#    usuario TEMP: el preflight lo dice. Con USUARIO=oracle (DBA) si.
# -----------------------------------------------------------------------------
#  CANCELAR: si el sobre ya salio mal, anular lo que escribio
#  replicar_controlado.sql (NO toca la cola) con la fecha LOTE_INICIO maxima
#  que imprimio esa corrida. Ver replicar_controlado_live.sh.
# =============================================================================
set -euo pipefail

HOST="${HOST:-192.168.5.200}"
USUARIO="${USUARIO:-respaldo}"
CLAVE="${CLAVE:-respaldo}"
ORACLE_SID="${ORACLE_SID:-lar1}"
SQLPLUS="${SQLPLUS:-/opt/oracle/bin/sqlplus}"
DIR_SERV="${DIR_SERV:-/tmp}"                 # donde se arma el exp en el servidor
FECHA_LARGA="$(date +%d%m%Y)"
FECHA_CORTA="$(date +%H%M)"
NOMBRE="routlar1_${FECHA_LARGA}_${FECHA_CORTA}"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
DESTINO="${DESTINO:-$RAIZ/auditoria/paquete_$FECHA_LARGA_$FECHA_CORTA}"
FRASE="AUTORIZAR_SOBRE_LARA_RUTLAR1"
FASE="${1:-}"
CON_STUB=0
[ "${2:-}" = "--con-stub" ] && CON_STUB=1

info() { echo "  $*"; }
die()  { echo "ERROR: $*" >&2; exit 1; }
sep()  { echo; echo "==================================================================="; echo "  $1"; echo "==================================================================="; }

case "$FASE" in
  preflight) ;;
  armar)
    [ "$CON_STUB" = 1 ] || true
    ;;
  *) die "uso: $0 preflight|armar [--con-stub]" ;;
esac
[ -n "$FASE" ] || die "uso: $0 preflight|armar [--con-stub]"

# --- El mapeo del plan B: las 23 T_ que este plan sabe llenar ----------------
MAPEADAS="T_CERTMORT T_CERTNACI T_DOCUMENT T_MORTCAUS T_CAUMMEDI T_MCAUMORB
          T_CASOSMM T_CASOSMMI T_RCASOSMI T_RENEPI15 T_RENGRES T_RENGTELE
          T_RESUMEN T_MADRNACI T_RNACNACI T_RNACANUL T_MORTANUL T_MORTFETA
          T_MORTMADR T_MORTVIOL T_MBASED T_MRESPA T_USUARIOS T_EVENTOS"

# --- SSH: sshpass, expect, o instrucciones manuales --------------------------
if command -v sshpass >/dev/null 2>&1; then
  ssh_en_servidor() { sshpass -p "$CLAVE" ssh -T -o StrictHostKeyChecking=no -o ConnectTimeout=15 "$USUARIO@$HOST" "$*"; }
  scp_del_servidor() { sshpass -p "$CLAVE" scp -o StrictHostKeyChecking=no -o ConnectTimeout=15 "$USUARIO@$HOST:$1" "$2"; }
elif command -v expect >/dev/null 2>&1; then
  expect_run() {
    expect <<EOF
set timeout 3600
log_user 1
spawn ssh -T -o StrictHostKeyChecking=no $USUARIO@$HOST $*
expect {
  "assword:" { send "$CLAVE\r"; exp_continue }
  "yes/no"   { send "yes\r"; exp_continue }
  eof
}
EOF
  }
  ssh_en_servidor() { expect_run "$*"; }
  scp_del_servidor() { die "con expect hay que copiar a mano: scp $USUARIO@$HOST:$1 $2"; }
else
  die "se necesita sshpass (sudo apt install sshpass) o expect"
fi

# =============================================================================
#  PREFLIGHT: todo solo lectura
# =============================================================================
SQL_PREFLIGHT="$(mktemp /tmp/preflight.XXXXXX.sql)"
trap 'rm -f "$SQL_PREFLIGHT"' EXIT
{
  cat <<'EOF'
SET SERVEROUTPUT ON SIZE UNLIMITED
SET LINESIZE 200
SET PAGESIZE 0
SET FEEDBACK OFF
SET HEADING OFF
DECLARE
  V_N NUMBER;
  PROCEDURE CHK(p_etiqueta VARCHAR2, p_sql VARCHAR2) IS
  BEGIN
    EXECUTE IMMEDIATE p_sql INTO V_N;
    DBMS_OUTPUT.PUT_LINE('CHK|'||p_etiqueta||'|'||NVL(TO_CHAR(V_N),'?'));
  EXCEPTION WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('CHK|'||p_etiqueta||'|ERROR: '||SUBSTR(SQLERRM,1,80));
  END CHK;
BEGIN
  CHK('cola SISMAI.EVENTOS_SINC',
      'SELECT COUNT(*) FROM SISMAI.EVENTOS_SINC');
  CHK('manifiesto TEMP.T_EVENTOS',
      'SELECT COUNT(*) FROM TEMP.T_EVENTOS');
  CHK('tablas en TEMP',
      'SELECT COUNT(*) FROM ALL_TABLES WHERE OWNER=''TEMP''');
  CHK('rol EXP_FULL_DATABASE',
      'SELECT COUNT(*) FROM SESSION_ROLES WHERE ROLE=''EXP_FULL_DATABASE''');
  CHK('privilegio SELECT ANY TABLE',
      'SELECT COUNT(*) FROM SESSION_PRIVS WHERE PRIVILEGE=''SELECT ANY TABLE''');
END;
/
-- Conteo real de cada T_ de TEMP: es lo que se va a exportar. PAGESIZE 0 para
-- que las lineas no se partan entre paginas.
DECLARE
  V_N NUMBER;
BEGIN
  FOR r IN (SELECT TABLE_NAME FROM ALL_TABLES
             WHERE OWNER='TEMP' ORDER BY TABLE_NAME) LOOP
    BEGIN
      EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM TEMP.'||r.TABLE_NAME INTO V_N;
      DBMS_OUTPUT.PUT_LINE('TABLA|'||r.TABLE_NAME||'|'||TO_CHAR(V_N));
    EXCEPTION WHEN OTHERS THEN
      DBMS_OUTPUT.PUT_LINE('TABLA|'||r.TABLE_NAME||'|ERROR');
    END;
  END LOOP;
END;
/
EXIT
EOF
} > "$SQL_PREFLIGHT"

PREFLIGHT_OUT="$(ssh_en_servidor "$SQLPLUS -s $USUARIO/$CLAVE@$ORACLE_SID" < "$SQL_PREFLIGHT" | tr -d '\r')"

chk()    { echo "$PREFLIGHT_OUT" | grep -m1 "^CHK|$1|" | cut -d'|' -f3- || true; }
tabla()  { echo "$PREFLIGHT_OUT" | grep -m1 "^TABLA|$1|" | cut -d'|' -f3- || true; }

es_mapeada() {
  local t="$1" m
  for m in $MAPEADAS; do [ "$t" = "$m" ] && return 0; done
  return 1
}

sep "PREFLIGHT  (solo lectura)  $USUARIO@$HOST  SID=$ORACLE_SID"

COLA=$(chk 'cola SISMAI.EVENTOS_SINC')
MANIF=$(chk 'manifiesto TEMP.T_EVENTOS')
NTAB=$(chk 'tablas en TEMP')
ROL=$(chk 'rol EXP_FULL_DATABASE')
SELANY=$(chk 'privilegio SELECT ANY TABLE')

[ -n "$COLA" ] || die "no se pudo leer nada del servidor. Revise USUARIO/CLAVE/ORACLE_SID y la red."
case "$COLA" in ERROR*) echo "  cola: $COLA"; die "sin acceso a SISMAI.EVENTOS_SINC" ;; esac
info "cola SISMAI.EVENTOS_SINC   : $COLA   (no se toca: este guion no escribe)"
info "manifiesto TEMP.T_EVENTOS  : $MANIF"
info "tablas en TEMP             : $NTAB"

BLOQUEOS=0
AVISOS=0

# 1. El manifiesto tiene que existir: sin el, el central no sabe que va.
if [ -z "$MANIF" ] || [ "$MANIF" = ERROR:* ] || [ "$MANIF" = "0" ]; then
  echo "  BLOQUEA  el manifiesto TEMP.T_EVENTOS esta vacio o no se puede leer."
  echo "          Sin el, el sobre no sirve: corra antes replicar_controlado_live.sh ejecutar."
  BLOQUEOS=$((BLOQUEOS+1))
fi

# 2. El `exp` tiene que poder exportar el usuario TEMP.
if [ "$ROL" != "1" ] && [ "$SELANY" != "1" ]; then
  echo "  BLOQUEA  $USUARIO no tiene EXP_FULL_DATABASE ni SELECT ANY TABLE:"
  echo "          el exp de owner=TEMP no va a funcionar."
  echo "          Opciones: USUARIO=oracle CLAVE=<la de oracle> $0 $FASE"
  echo "                    o que el DBA le grant SELECT ANY TABLE."
  BLOQUEOS=$((BLOQUEOS+1))
else
  info "puede exportar TEMP       : si (ROL=$ROL SELECT_ANY=$SELANY)"
fi

# 3. Lo mas importante: que NO haya filas en las T_ que este plan no controla.
#    El exp se lleva TODO TEMP, y esas filas se irian al central sin que nadie
#    las haya revisado (en el paquete del 04/08 iban todas en 0).
VACIAS_SIN_MAPEO=0
CON_FILAS_SIN_MAPEO=""
MAPEADAS_VACIAS=""
while IFS='|' read -r _ t c; do
  [ -n "${t:-}" ] || continue
  if es_mapeada "$t"; then
    [ "$c" = "0" ] && MAPEADAS_VACIAS="$MAPEADAS_VACIAS $t"
  else
    [ "$c" = "0" ] || CON_FILAS_SIN_MAPEO="$CON_FILAS_SIN_MAPEO $t($c)"
  fi
done < <(echo "$PREFLIGHT_OUT" | grep '^TABLA|')

if [ -n "$CON_FILAS_SIN_MAPEO" ]; then
  echo "  BLOQUEA  hay filas en tablas de TEMP que el plan B NO controla:"
  echo "          $CON_FILAS_SIN_MAPEO"
  echo "          El exp las incluiria en el sobre. Vaciar esas tablas es una"
  echo "          operacion del DBA con autorizacion; el plan B no las toca."
  BLOQUEOS=$((BLOQUEOS+1))
else
  info "tablas sin mapeo con filas  : ninguna (bien)"
fi
[ -n "$MAPEADAS_VACIAS" ] && info "AVISO  mapeadas vacias:$MAPEADAS_VACIAS"
[ -n "$MAPEADAS_VACIAS" ] && AVISOS=$((AVISOS+1))

# 4. Cuanto va a ocupar el dump, y hay espacio en el servidor.
LIBRE_KB="$(ssh_en_servidor "df -Pk '$DIR_SERV' | tail -1 | awk '{print \$4}'" | tr -d '\r' | head -1)"
if [ -n "$LIBRE_KB" ] && [ "$LIBRE_KB" -gt 0 ] 2>/dev/null; then
  info "espacio libre en $DIR_SERV : $((LIBRE_KB/1024)) MB"
  [ "$LIBRE_KB" -lt 262144 ] && { echo "  BLOQUEA  menos de 256 MB libres en $DIR_SERV"; BLOQUEOS=$((BLOQUEOS+1)); }
else
  echo "  AVISO  no se pudo leer el espacio libre en $DIR_SERV"
  AVISOS=$((AVISOS+1))
fi

# 5. El repllar1.log tiene que ser de HOY (el de la corrida que se acaba de hacer).
REPL_LOG="$(ls -1t "$RAIZ"/auditoria/replicar_controlado_ejecutar_*.txt 2>/dev/null | head -1 || true)"
if [ -z "$REPL_LOG" ]; then
  echo "  BLOQUEA  no hay ningun log de replicar_controlado_live.sh ejecutar en auditoria/"
  BLOQUEOS=$((BLOQUEOS+1))
elif [ "$(date -r "$REPL_LOG" +%Y%m%d)" != "$(date +%Y%m%d)" ]; then
  echo "  AVISO  el repllar1.log mas reciente es de HIER: $(basename "$REPL_LOG")"
  AVISOS=$((AVISOS+1))
else
  info "repllar1.log a usar        : $(basename "$REPL_LOG")"
fi

echo
if [ "$BLOQUEOS" -gt 0 ]; then
  die "$BLOQUEOS bloqueo(s). No se arma el sobre: resuelvalos primero."
fi
info "PREFLIGHT OK ($AVISOS aviso(s)). El sobre se puede armar."
[ "$FASE" = preflight ] && exit 0

# =============================================================================
#  ARMAR
# =============================================================================
sep "ARMAR EL SOBRE  $NOMBRE"
echo "  REAL     : routlar1.dmp, routlar1.log  (exp del usuario TEMP)"
echo "  REAL     : repllar1.log                (salida de replicar_controlado.sql)"
if [ "$CON_STUB" = 1 ]; then
  echo "  STUB     : copyhistlar1.log, bloqlar1.log  (fases NO reconstruidas)"
else
  echo "  FALTAN   : copyhistlar1.log, bloqlar1.log  (fases NO reconstruidas)"
fi
echo "  Se envia a:  $DESTINO   (este guion NO envia nada al central)"
echo
echo "  Ojo: el sobre NO es equivalente al original. Le falta el contenido de"
echo "  T_AUDITORIA y los 2 logs de copyhist/bloq serian de mentira."
printf '  Escriba esta frase exacta y Enter para armar el sobre:\n    %s\n  > ' "$FRASE"
read -r respuesta
[ "$respuesta" = "$FRASE" ] || die "frase incorrecta: no se genera nada"

if [ "$CON_STUB" = 0 ]; then
  echo
  echo "  Sin --con-stub este guion no inventa los 2 logs que faltan."
  echo "  Si el central exige los 5 archivos, vuelva con:  $0 armar --con-stub"
  die "faltan copyhistlar1.log y bloqlar1.log"
fi
echo
echo "  Segunda confirmacion: los 2 logs seran MARCADORES, no los originales."
printf '  Escriba STUB y Enter para continuar:\n  > '
read -r r2
[ "$r2" = "STUB" ] || die "cancelado"

mkdir -p "$DESTINO"

# --- 1. exp real del usuario TEMP en el servidor ----------------------------
sep "1/5  exp del usuario TEMP (esto puede tardar)"
ssh_en_servidor "cd $DIR_SERV && rm -f ${NOMBRE}.dmp ${NOMBRE}.log && \
  exp $USUARIO/$CLAVE@$ORACLE_SID owner=TEMP file=${NOMBRE}.dmp log=${NOMBRE}.log \
      statistics=N consistent=N; echo rc=\$?" > "$DESTINO/exp_salida.txt" 2>&1 || true
tail -3 "$DESTINO/exp_salida.txt" | sed 's/^/  /'
if ! ssh_en_servidor "test -s $DIR_SERV/${NOMBRE}.dmp"; then
  sed 's/^/  /' "$DESTINO/exp_salida.txt" | tail -15
  die "el exp no produjo dump. NO arme el sobre."
fi
scp_del_servidor "$DIR_SERV/${NOMBRE}.dmp"  "$DESTINO/routlar1.dmp"
scp_del_servidor "$DIR_SERV/${NOMBRE}.log" "$DESTINO/routlar1.log"
info "descargados: routlar1.dmp ($(du -h "$DESTINO/routlar1.dmp" | cut -f1)),  routlar1.log ($(du -h "$DESTINO/routlar1.log" | cut -f1))"

# --- 2. repllar1.log: la salida de la replicacion ---------------------------
sep "2/5  repllar1.log (salida de replicar_controlado.sql)"
cp "$REPL_LOG" "$DESTINO/repllar1.log"
info "$(basename "$REPL_LOG") -> repllar1.log ($(wc -l < "$DESTINO/repllar1.log") lineas)"

# --- 3. y 4. los dos logs que no estan reconstruidos ------------------------
sep "3/5  y 4/5  copyhistlar1.log y bloqlar1.log  (STUB)"
cat > "$DESTINO/copyhistlar1.log" <<EOF

-- STUB. La fase copyhist (historial: T_AUDITORIA y el respaldo de la semana
-- anterior) NO esta reconstruida. En el paquete real del 04/08/2026 este log
-- decia: 9862 rows updated. / 34 rows created. / 9118 rows updated.
-- T_AUDITORIA (9.118 filas) NO viaja en este sobre.
-- Ver PENDIENTES.md 17.13.

EOF
cat > "$DESTINO/bloqlar1.log" <<EOF

-- STUB. La fase de bloqueo NO esta reconstruida. En el paquete real del
-- 04/08/2026 este log tenia 2 lineas "System altered.".

EOF
info "escritos (marcadores). NO son los logs del original."

# --- 5. el ZIP con los 5 archivos -------------------------------------------
sep "5/5  empaquetando y verificando"
( cd "$DESTINO" && zip -q -X -j "${NOMBRE}.ZIP" \
    routlar1.dmp routlar1.log repllar1.log copyhistlar1.log bloqlar1.log )

ZIP="$DESTINO/${NOMBRE}.ZIP"
NENTRADAS="$(unzip -l "$ZIP" | tail -1 | awk '{print $2}')"
[ "$NENTRADAS" = "5" ] || die "el ZIP tiene $NENTRADAS archivos, deberian ser 5. No lo envie."

echo
info "contenido del sobre"
unzip -l "$ZIP" | sed -n '4,10p' | sed 's/^/    /'
echo
info "huellas (para el acta de entrega; van fuera del ZIP, el sobre lleva 5)"
( cd "$DESTINO" && sha256sum routlar1.dmp routlar1.log repllar1.log \
                            copyhistlar1.log bloqlar1.log "${NOMBRE}.ZIP" ) \
  | tee "$DESTINO/SHA256SUMS.txt" | sed 's/^/    /'

echo
info "conteos por tabla del exp (lo que va a viajar)"
python3 - "$DESTINO/routlar1.log" <<'PYEOF'
import re, sys
cur = None
out = {}
for ln in open(sys.argv[1], encoding='latin-1', errors='replace').read().replace('\r', '\n').splitlines():
    m = re.search(r'exporting table\s+(\S+)', ln)
    if m:
        cur = m.group(1)
        n = re.search(r'([\d,]+)\s+rows? exported', ln)
        if n:
            out[cur] = int(n.group(1).replace(',', '')); cur = None
        continue
    n = re.search(r'^\s*([\d,]+)\s+rows? exported', ln)
    if n and cur:
        out[cur] = int(n.group(1).replace(',', '')); cur = None
vacias = [t for t, c in sorted(out.items()) if c == 0]
print(f"    tablas exportadas: {len(out)}   con filas: {len(out)-len(vacias)}   vacias: {len(vacias)}")
print(f"    filas totales     : {sum(out.values())}")
if vacias:
    print(f"    en 0: {' '.join(vacias)}")
PYEOF

echo
info "SIGUIENTE PASO (no lo hace este guion): entregar el sobre por el canal"
info "que use la institucion. Si lo rechaza, ESCALAR al soporte SIS/Centura."
info "La cola SISMAI.EVENTOS_SINC quedo INTACTA: el purgado se decide aparte,"
info "con autorizacion, tras confirmar la recepcion del central."
