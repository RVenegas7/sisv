#!/usr/bin/env bash
# ====================================================================
# RESPALDO TOTAL DEL ORACLE POR ESQUEMAS (solo lectura) — 30/09/2026
# --------------------------------------------------------------------
# Por que hace falta: el servidor NO tiene ningun respaldo programado.
# El crontab de `oracle` solo tiene los tres .bat de los sabados
# (borrtemp, recreidx, mantenimiento) y no hay ningun exp/expdp
# corriendo. El unico dump que existe es el del 24/09, ya copiado a
# PostgreSQL, y el de hoy seria el primero que sale de la maquina.
#
# `exp` unicamente SELECTea: se puede correr con usuarios capturando y
# no bloquea las escrituras de negocio. Aun asi, comprueba al principio
# que no haya otro export ya corriendo, porque dos `exp` a la vez se
# pelean por el UNDO y degradan el servicio.
#
# Se usa el cliente nativo /opt/oracle/bin/exp: `oracledb` en modo
# Thin falla contra este 10g por cifrado obsoleto (AGENTS.md), y no
# hay Instant Client en este equipo.
#
# Uso (desde este equipo, con sshpass):
#   ./migracion/respaldo_total.sh                    # informe y ejecuta
#   SIMULAR=1 ./migracion/respaldo_total.sh          # solo muestra
#   ESQUEMAS="SISMAI TEMP" ./migracion/respaldo_total.sh
#
# Salida en el servidor: /home/oracle/respaldo_<AAAAMMDD_HHMM>/
# ====================================================================
set -uo pipefail

HOST="${HOST:-192.168.5.200}"
USUARIO="${USUARIO:-oracle}"
# Las claves del SO y de la BD NO van con valor por defecto: se leen del
# entorno o de legancy_conf/credenciales.env (ignorado por git).
#   CLAVE / SSHPASS_ORACLE : clave del SSH (abre el servidor).
#   CLAVE_ORACLE           : clave de la cuenta de BASE para `exp`. La del
#                            SO NO sirve (probado el 30/09: ORA-01017).
#                            Sin ella el script ABORTA, no lo intenta.
#                            (PENDIENTES.md 22.2.1)
set -a
[ -f "$(dirname "$0")/../legancy_conf/credenciales.env" ] && \
  . "$(dirname "$0")/../legancy_conf/credenciales.env"
set +a
CLAVE="${CLAVE:-${SSHPASS_ORACLE:-}}"
CLAVE_ORACLE="${CLAVE_ORACLE:-}"
if [ -z "$CLAVE" ]; then
  echo "Falta la clave SSH del usuario '$USUARIO'."
  echo "Defina CLAVE en el entorno o SSHPASS_ORACLE en legancy_conf/credenciales.env (ignorado por git)."
  exit 1
fi
if [ -z "$CLAVE_ORACLE" ]; then
  echo "Falta CLAVE_ORACLE (clave de una cuenta de BASE con permisos de lectura)."
  echo "La clave del SO solo abre el SSH; contra Oracle da ORA-01017."
  echo "Pida la clave al DBA o defina CLAVE_ORACLE en legancy_conf/credenciales.env (ignorado por git)."
  exit 1
fi
ORACLE_HOME="/opt/oracle"
ORACLE_SID="lar1"
DESTINO_BASE="/home/oracle"
ESQUEMAS="${ESQUEMAS:-SISMAI TEMP HISTORICO INBDLAR1}"
SIMULAR="${SIMULAR:-0}"
# Cuenta de BASE para `exp` (la da el DBA). La del SO no sirve. Puede ser
# distinta del usuario SSH (p. ej. respaldo): por eso se parametriza.
USUARIO_DB="${USUARIO_DB:-$USUARIO}"

FECHA="$(date +%Y%m%d)"
HORA="$(date +%H%M)"
DIR="${DESTINO_BASE}/respaldo_${FECHA}_${HORA}"
LOG_LOCAL="/tmp/opencode/respaldo_${FECHA}_${HORA}"

sxs() { sshpass -p "$CLAVE" ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 "$USUARIO@$HOST" "$@"; }
sxs_put() { sshpass -p "$CLAVE" ssh -o StrictHostKeyChecking=accept-new "$USUARIO@$HOST" "cat > $1" ; }

echo "=================================================================="
echo " Respaldo total por esquemas — $FECHA $HORA"
echo " servidor: $HOST ($USUARIO)   esquemas: $ESQUEMAS"
echo "=================================================================="

# --- 0. Pre-vuelo: no leer mientras otro export escribe ----------------
echo
echo ">> 0. Pre-vuelo"
EXP_VIVOS="$(sxs "ps -ef | grep -E '[e]xp |[e]xpdp' | grep -v grep" 2>/dev/null)"
if [ -n "$EXP_VIVOS" ]; then
  echo " [FALLO] ya hay un export corriendo en el servidor:"
  echo "$EXP_VIVOS" | sed 's/^/         /'
  echo "         no se puede leer la base a medio respaldar. Abortando."
  exit 1
fi
echo " [ OK ]   no hay ningun exp/expdp corriendo"

ESPACIO="$(sxs "df -BG /home | tail -1 | awk '{print \$4}'" 2>/dev/null | tr -dc '0-9')"
if [ -n "$ESPACIO" ] && [ "$ESPACIO" -lt 20 ]; then
  echo " [FALLO] solo hay ${ESPACIO}G libres en /home; se necesitan ~15G"
  exit 1
fi
echo " [ OK ]   ${ESPACIO}G libres en /home"

if [ ! -d "$DIR" ]; then
  sxs "mkdir -p $DIR" || { echo " [FALLO] no se pudo crear $DIR"; exit 1; }
fi
echo " [ OK ]   destino en el servidor: $DIR"

if [ "$SIMULAR" = "1" ]; then
  echo
  echo "== SIMULACION: se mostraria esto, no se ejecuta =="
  echo "  Para cada esquema, de forma SECUENCIAL (el UNDO es de 1 GB):"
  for e in $ESQUEMAS; do
    echo "  exp PARFILE=$DIR/exp_$e.par OWNER=$e LOG=$DIR/exp_$e.log"
    echo "     -> $DIR/${e}_full_${FECHA}.dmp"
  done
  echo
  echo "== Fin de la simulacion. Quite SIMULAR=1 para ejecutar. =="
  exit 0
fi

# --- 1. Un exp por esquema, SECUENCIAL, con bitacora --------------------
# §22.2.4: correr los esquemas UNO a uno (no los 4 a la vez) porque el
# UNDO es de 1 GB y varios `exp` simultaneos lo saturan (visto el 30/09).
echo
echo ">> 1. Exportando (secuencial)"
for e in $ESQUEMAS; do
  PAR="$DIR/exp_$e.par"
  # USERID va dentro del PARFILE: sin TNS en el servidor, `exp` no puede
  # resolver el connect string y ademas pide usuario por stdin, que en un
  # proceso en segundo plano se lee como EOF (EXP-00030, visto el 30/09).
  # La clave de base NUNCA va en texto plano legible: el parfile se escribe
  # con permisos 600 y se borra al terminar (PENDIENTES.md 22.2.3).
  sxs_put "$PAR" <<PARFILE
OWNER=$e
USERID=$USUARIO_DB/$CLAVE_ORACLE
GRANTS=Y
INDEXES=Y
CONSTRAINTS=Y
CONSISTENT=Y
DIRECT=N
LOG=$DIR/exp_$e.log
FILE=$DIR/${e}_full_${FECHA}.dmp
PARFILE
  sxs "chmod 600 $PAR" 2>/dev/null || true
  echo "   arrancando exp $e ... (log: $DIR/exp_$e.log)"
  # Se lanza en segundo plano y se espera a que el proceso termine: el
  # `exp` puede tardar minutos y la sesion SSH no debe caerse. Se espera
  # el PID en vez de un grep: el grep puede fallar justo cuando el export
  # esta arrancando y todavia no se ve.
  PID_EXP="$(sxs "export ORACLE_HOME=$ORACLE_HOME ORACLE_SID=$ORACLE_SID PATH=$ORACLE_HOME/bin:\$PATH; nohup exp PARFILE=$PAR > $DIR/exp_$e.nohup 2>&1 & echo \$!" 2>/dev/null | tr -dc '0-9')"

  # --- Esperar a que ESTE esquema termine antes del siguiente -----------
  echo "   esperando a $e (pid ${PID_EXP:-?})..."
  INT=0
  while [ "$INT" -lt 120 ]; do
    [ -z "${PID_EXP:-}" ] && break
    VIVO="$(sxs "ps -p $PID_EXP -o pid= 2>/dev/null | wc -l" 2>/dev/null | tr -dc '0-9')"
    [ "${VIVO:-0}" = "0" ] && break
    sleep 15
    INT=$((INT + 1))
  done
  if [ "$INT" -ge 120 ]; then
    echo " [AVISO] $e sigue corriendo despues de 30 min; revisa $DIR/exp_$e.log"
  else
    # El log del exp dice si termino bien y con que cantidad de filas.
    # Se comparan las dos fuentes porque el .log a veces no se escribe.
    DMP="$DIR/${e}_full_${FECHA}.dmp"
    TAM="$(sxs "stat -c %s $DMP 2>/dev/null" 2>/dev/null | tr -dc '0-9')"
    if [ -n "${TAM:-}" ] && [ "$TAM" -gt 10000 ]; then
      if sxs "grep -q 'terminado correctamente' $DIR/exp_$e.log 2>/dev/null"; then
        echo "   OK ($(numfmt --to=iec --suffix=B "$TAM" 2>/dev/null || echo "${TAM}B"))"
      else
        echo " [REVISAR] dmp de $(numfmt --to=iec --suffix=B "$TAM" 2>/dev/null || echo "${TAM}B") pero el log no confirma: $DIR/exp_$e.log"
      fi
    else
      echo " [FALLO] no se genero $DMP (ver $DIR/exp_$e.nohup)"
      sxs "tail -5 $DIR/exp_$e.nohup 2>/dev/null" 2>/dev/null | sed 's/^/             /'
    fi
  fi
  # El parfile tenia la clave: no queda regado en el servidor.
  sxs "rm -f $PAR" 2>/dev/null || true
done

# --- 2. Inventario con SHA-256 ----------------------------------------
echo
echo ">> 2. Inventario"
sxs "cd $DIR && ls -la *.dmp 2>/dev/null; echo '--- SHA256 ---'; sha256sum *.dmp 2>/dev/null" 2>/dev/null
sxs "cd $DIR && du -sh $DIR 2>/dev/null" 2>/dev/null

echo
echo "=================================================================="
echo " Respaldo terminado. En el servidor: $DIR"
echo " Log de esta corrida: $LOG_LOCAL"
echo "=================================================================="
