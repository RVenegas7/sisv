#!/usr/bin/env bash
# ==============================================================================
# PRE-VUELO de la ventana del martes (PENDIENTES 17.17 / 17.24).
#
# Corre esto ANTES de extraer. No lee el Oracle: solo comprueba, en la maquina de
# trabajo, que estan las tres cosas de las que depende la extraccion y dice si se
# puede seguir. Es deliberadamente de SOLO LECTURA y sin efectos: si algo falla,
# el script informa y sigue, para que se pueda ver el estado completo de una vez.
#
# Que comprueba:
#   1. Herramientas disponibles en este equipo (ssh, sshpass, unzip, python).
#   2. Respaldo total de las 13:00: que haya un .dump/.dmp de HOY y que no haya
#      un exp/expdp colgado todavia. Si el respaldo no esta, NO se extrae: leer
#      mientras corre el exp es pedir una lectura a medio hacer.
#   3. Sobre semanal: que exista el routlar1_*.ZIP mas reciente y que traiga los
#      5 archivos (los 3 logs, routlar1.log y routlar1.dmp). Si el sobre no salio,
#      el central no tiene la semana y la conciliacion no se puede cerrar.
#   4. Fecha DESDE recomendada para la extraccion, a partir de lo ultimo que ya
#      esta cargado en PostgreSQL, con dias de solape.
#
# Uso:
#   ./migracion/preflight_ventana.sh
#   DIR_RESPALDO=/home/informatica/respaldo DIR_SOBRES=/home/salud/enviados \
#     ./migracion/preflight_ventana.sh
#   DESDE=01/08/2026 ./migracion/preflight_ventana.sh     # fuerza el rango
#   SOLO=herramientas,sql ./migracion/preflight_ventana.sh
#
# No requiere red ni servidor: se puede correr desde casa antes de salir.
# ==============================================================================
set -uo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
DIR_RESPALDO="${DIR_RESPALDO:-$RAIZ/dumps}"
DIR_SOBRES="${DIR_SOBRES:-$RAIZ/enviados}"
SOLO="${SOLO:-}"
PYTHON="${PYTHON:-$RAIZ/.venv/bin/python}"
MANAGE="$RAIZ/backend/manage.py"
HORA_RESPALDO="${HORA_RESPALDO:-13:00}"
SOLAPES="${SOLAPES:-7}"

# Los 5 archivos que tiene que traer el sobre. Son los mismos en todos los
# routlar1_*.ZIP revisados; si mañana aparece otro, esto lo delata.
ESPERADOS="bloqlar1.log copyhistlar1.log repllar1.log routlar1.log routlar1.dmp"

OK=0
AVISOS=0
FALLOS=0
ESTADO=()

titulo() { printf '\n== %s\n' "$1"; }
veredicto() {
  if [ "$1" = "OK" ]; then
    ESTADO+=("OK       $2"); OK=$((OK + 1))
  elif [ "$1" = "AVISO" ]; then
    ESTADO+=("AVISO    $2"); AVISOS=$((AVISOS + 1))
  else
    ESTADO+=("FALLO    $2"); FALLOS=$((FALLOS + 1))
  fi
  # Se imprime en el momento ademas de acumularlo, para que al ir mirando la
  # pantalla se sepa a que seccion pertenece cada cosa.
  case "$1" in
    OK)    printf ' [ OK ]    %s\n' "$2" ;;
    AVISO) printf ' [ AVISO ] %s\n' "$2" ;;
    *)     printf ' [FALLO]   %s\n' "$2" ;;
  esac
}
interesado() { [ -z "$SOLO" ] || printf '%s' ",$SOLO," | grep -q ",$1,"; }

echo "=================================================================="
echo " Pre-vuelo ventana de recuperacion MM/MN"
echo " fecha: $(date '+%Y-%m-%d %H:%M:%S')   host: $(hostname -s)"
echo "=================================================================="

# -----------------------------------------------------------------------------
titulo "1. Herramientas en este equipo"
# -----------------------------------------------------------------------------
for par in ssh unzip awk; do
  if command -v "$par" >/dev/null 2>&1; then
    veredicto OK "$par disponible ($(command -v "$par"))"
  else
    veredicto FALLO "$par NO esta instalado"
  fi
done
if command -v sshpass >/dev/null 2>&1; then
  veredicto OK "sshpass disponible (modo remoto automatizado)"
elif command -v expect >/dev/null 2>&1; then
  veredicto AVISO "no hay sshpass; se puede usar expect para el modo remoto"
else
  veredicto AVISO "no hay sshpass ni expect: el modo remoto hay que hacerlo a mano"
fi
if [ -x "$PYTHON" ]; then
  veredicto OK "venv de Python ($PYTHON)"
else
  veredicto FALLO "no existe $PYTHON (no se podra cargar en PostgreSQL)"
fi

# -----------------------------------------------------------------------------
titulo "2. Respaldo total de las $HORA_RESPALDO"
# -----------------------------------------------------------------------------
# Se mira, por orden: (a) que no haya un exp/expdp corriendo ahora mismo,
# (b) que exista un dump de HOY en DIR_RESPALDO.
# (a) y (b) se pueden desactivar con RESPALDO=0 si el respaldo lo hace otra
# persona y no queda rastro en esta maquina.
if [ "${RESPALDO:-1}" = "1" ] && interesado respaldo; then
  EXPANDO="$(ps -eo comm= 2>/dev/null | grep -E '^(exp|expdp)$' | head -1 || true)"
  if [ -n "$EXPANDO" ]; then
    veredicto FALLO "hay un '$EXPANDO' corriendo: el respaldo AUN NO termina"
  else
    veredicto OK "no hay exp/expdp corriendo"
  fi

  if [ -d "$DIR_RESPALDO" ]; then
    HOY="$(date +%Y-%m-%d)"
    CANDIDATOS="$(find "$DIR_RESPALDO" -maxdepth 1 -type f \
        \( -name "*.dump" -o -name "*.dmp" -o -name "*.sql.gz" \) \
        -newermt "$HOY 00:00" -printf '%T@ %s %p\n' 2>/dev/null | sort -rn | head -5)"
    if [ -z "$CANDIDATOS" ]; then
      veredicto FALLO "no hay ningun dump de HOY en $DIR_RESPALDO"
      veredicto AVISO "si el respaldo lo hace otra persona: RESPALDO=0 para no mirar"
    else
      veredicto OK "hay dump(s) de hoy en $DIR_RESPALDO"
      printf '%s\n' "$CANDIDATOS" | while read -r _ tam tamano ruta; do
        printf '           %10s  %s  %s\n' \
          "$(numfmt --to=iec --suffix=B "${tamano:-0}" 2>/dev/null || echo "${tamano:-0}B")" \
          "$(date -d "@${tam%.*}" '+%H:%M' 2>/dev/null || echo '?')" \
          "$(basename "$ruta")"
      done
      # El respaldo de la tarde es el que importa: si el unico dump de hoy es de
      # las 00:xx, el de las 13:00 todavia no esta.
      if printf '%s' "$CANDIDATOS" | awk -v h="$HORA_RESPALDO" '
            { split($0, a, " "); cmd="date -d @"a[1]" +%H%M"; cmd | getline hh; close(cmd);
              if (hh + 0 >= substr(h,1,2)*100 + substr(h,4,2) + 0) { ok=1 } }
            END { exit(ok ? 0 : 1) }'; then
        veredicto OK "hay un dump posterior a las $HORA_RESPALDO"
      else
        veredicto AVISO "ningun dump de hoy es posterior a las $HORA_RESPALDO"
      fi
    fi
  else
    veredicto AVISO "no existe $DIR_RESPALDO (ajustalo con DIR_RESPALDO=...)"
  fi
fi

# -----------------------------------------------------------------------------
titulo "3. Sobre semanal routlar1_*.ZIP"
# -----------------------------------------------------------------------------
if interesado sobre; then
  if [ ! -d "$DIR_SOBRES" ]; then
    veredicto AVISO "no existe $DIR_SOBRES (ajustalo con DIR_SOBRES=...)"
  else
    ULTIMO="$(ls -t "$DIR_SOBRES"/routlar1_*.ZIP 2>/dev/null | head -1 || true)"
    if [ -z "$ULTIMO" ]; then
      veredicto FALLO "no hay ningun routlar1_*.ZIP en $DIR_SOBRES"
    else
      veredicto OK "sobre mas reciente: $(basename "$ULTIMO")"
      printf '           generado %s, %s\n' \
        "$(date -r "$ULTIMO" '+%Y-%m-%d %H:%M')" \
        "$(numfmt --to=iec --suffix=B "$(stat -c %s "$ULTIMO")" 2>/dev/null || echo '?')"
      LISTA="$(unzip -l "$ULTIMO" 2>/dev/null | awk 'NF >= 4 && $1 ~ /^[0-9]+$/ {print $4}')"
      for e in $ESPERADOS; do
        if printf '%s\n' "$LISTA" | grep -qx "$e"; then
          veredicto OK "el sobre trae $e"
        else
          veredicto FALLO "el sobre NO trae $e (falta un archivo del paquete)"
        fi
      done
      if [ "$(printf '%s\n' "$LISTA" | wc -l)" -lt 5 ]; then
        veredicto FALLO "el sobre trae $(printf '%s\n' "$LISTA" | wc -l) archivos y deberian ser 5"
        veredicto AVISO "repllar1.log falta desde el sobre del 08/09/2026 (PENDIENTES 17):"
        veredicto AVISO "revisar en el servidor que lo siga produciendo /home/salud/bin"
      fi
      # routlar1.dmp es el que lleva los datos; si esta en 0, el sobre no sirve.
      if unzip -l "$ULTIMO" 2>/dev/null | awk '$4=="routlar1.dmp" {exit ($1+0 > 1000 ? 0 : 1)}'; then
        veredicto OK "routlar1.dmp tiene contenido"
      else
        veredicto FALLO "routlar1.dmp vacio o ausente: el sobre no lleva datos"
      fi
      # El central no recibe nada hasta que el sobre del martes llega al nivel
      # central: por eso la ventana es el dia del envio y no el del corte.
      if [ "$(date +%u)" = "2" ]; then
        veredicto OK "hoy es martes: es el dia de envio"
      else
        veredicto AVISO "hoy NO es martes: el envio semanal es solo los martes"
      fi
    fi
  fi
fi

# -----------------------------------------------------------------------------
titulo "4. Fecha DESDE recomendada para la extraccion"
# -----------------------------------------------------------------------------
# Lo ultimo que ya esta en PostgreSQL marca hasta donde llegamos. La extraccion
# arranca un poco antes para que el solape cubra cualquier registro que se haya
# cargado tarde, y la carga es idempotente: recargar el solape no duplica nada.
if interesado desde; then
  if [ -n "${DESDE:-}" ]; then
    veredicto OK "DESDE forzado por el operador: $DESDE"
  elif [ -f "$MANAGE" ] && [ -x "$PYTHON" ]; then
    SALIDA_SQL="$("$PYTHON" "$MANAGE" shell -c "
from django.db.models import Max
from registros.models import Defuncion, Nacimiento
f = Defuncion.objects.aggregate(m=Max('fecha_evento'))['m']
n = Nacimiento.objects.aggregate(m=Max('fecha_evento'))['m']
print(f'{f or \"\"}|{n or \"\"}')
" 2>/dev/null | tail -1)"
    if [ -z "$SALIDA_SQL" ] || [ "$SALIDA_SQL" = "|" ]; then
      veredicto AVISO "no se pudo leer la base (contenedor caido?): define DESDE a mano"
    else
      ULT_DEF="${SALIDA_SQL%%|*}"
      ULT_NAC="${SALIDA_SQL##*|}"
      veredicto OK "ultima defuncion cargada: ${ULT_DEF:-ninguna}"
      veredicto OK "ultimo nacimiento cargado: ${ULT_NAC:-ninguno}"
      RECOMENDADA="$("$PYTHON" -c "
from datetime import date, datetime, timedelta
cands = []
for d in ['$ULT_DEF', '$ULT_NAC']:
    if not d:
        continue
    try:
        cands.append(datetime.strptime(d[:10], '%Y-%m-%d').date())
    except ValueError:
        pass
if not cands:
    print('01/08/2026')
else:
    print((max(cands) - timedelta(days=$SOLAPES)).strftime('%d/%m/%Y'))
" 2>/dev/null || echo "01/08/2026")"
      veredicto OK "DESDE recomendado: $RECOMENDADA (ultimo - $SOLAPES dias de solape)"
      if [ "$RECOMENDADA" != "01/08/2026" ]; then
        veredicto AVISO "el rango por defecto es 01/08/2026 (inicio del hueco);"
        veredicto AVISO "$RECOMENDADA solo si el hueco ya se cubrio antes"
      fi
    fi
  else
    veredicto AVISO "no hay manage.py/venv: define DESDE a mano"
  fi
fi

# -----------------------------------------------------------------------------
titulo "Resumen"
# -----------------------------------------------------------------------------
for linea in "${ESTADO[@]}"; do printf ' %s\n' "$linea"; done
echo
echo "------------------------------------------------------------------"
printf ' %d correctos, %d avisos, %d fallos\n' "$OK" "$AVISOS" "$FALLOS"
echo "------------------------------------------------------------------"
if [ "$FALLOS" -gt 0 ]; then
  echo
  echo " HAY FALLOS: no extraigas todavia. Un 'DMP de hoy' que no existe o un"
  echo " 'exp corriendo' significan que se leeria la base a medio respaldar."
  echo
  exit 1
fi
echo
echo " Todo lo que se puede verificar aca esta en verde."
echo " Faltan dos cosas que solo se confirman en el servidor:"
echo "   1. que el respaldo total de las $HORA_RESPALDO haya terminado bien, y"
echo "   2. la CANTIDAD de MN que la oficina cargo en las semanas 36 y 37."
echo
echo " Siguiente paso (solo lectura, no toca la cola EVENTOS_SINC):"
echo "   DESDE=01/08/2026 $RAIZ/migracion/extraer_mm_mn_roto.sh"
echo "   $PYTHON $MANAGE cargar_mm_mn_roto --directorio <salida>            # dry-run"
echo "   $PYTHON $MANAGE cargar_mm_mn_roto --directorio <salida> --ejecutar  # aplica"
echo "=================================================================="
