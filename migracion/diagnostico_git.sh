#!/usr/bin/env bash
# =============================================================================
# diagnostico_git.sh — por que "lo que subi en la oficina" no aparece en GitHub
#
# Correr en la MAQUINA DONDE ESTAN LOS COMMITS QUE NO APARECEN (la de la
# oficina). Solo lectura: no modifica nada, no pushea, no cambia config.
#
# Lo que decide el resultado:
#   1. remote -v        : origin debe ser git@github.com:RVenegas7/sisv.git
#   2. status -sb       : rama actual y cuantos commits no estan en origin
#   3. log origin..HEAD : los commits "sin subir"; si lista lo que crees que
#                         subiste, el push no llego, no es que no se hizo.
#   4. ssh -T git@github.com : comprueba que la llave del remoto carga la
#                         cuenta correcta. Si dice "permission denied", el
#                         push enmudecio por llave.
# =============================================================================

set -u
REPO="${1:-.}"
cd "$REPO" 2>/dev/null || { echo "ERROR: no encuentro el repo en $REPO"; exit 1; }

echo "═══════════════════════════════════════════════════════════════"
echo " DIAGNOSTICO GIT — $(hostname) — $(date '+%Y-%m-%d %H:%M')"
echo " repo: $(pwd)"
echo "═══════════════════════════════════════════════════════════════"

echo
echo "[1] remote -v  (origin debe decir RVenegas7/sisv.git)"
git remote -v

echo
echo "[2] status -sb  (la rama y cuantos commits sin pushear)"
git status -sb

echo
echo "[3] ultimos 10 commits locales"
git log --oneline -10 2>/dev/null

echo
echo "[4] commits locales que NO estan en origin/main"
echo "    (si aqui lista algo que crees haber subido, el push fallo)"
n=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "?")
echo "    commits sin subir: $n"
git log --oneline origin/main..HEAD 2>/dev/null

echo
echo "[5] ramas locales y seguimiento"
git branch -vv

echo
echo "[6] llave SSH que usaria el remoto"
echo "    > ~/.ssh/$(git config --get remote.origin.url 2>/dev/null | sed -E 's#.*:##; s#\.git##; s#/$##')"
for k in ~/.ssh/id_* ~/.ssh/sisv_github ~/.ssh/*_github; do
  [ -e "$k" ] && [ -f "$k" ] && echo "      presente: $k"
done

echo
echo "[7] prueba SSH a GitHub (la llave cargada en el agente)"
if command -v ssh >/dev/null; then
  timeout 15 ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -T git@github.com 2>&1 \
    | sed -E 's/^.*authenticated/OK: authenticated/'
else
  echo "      ssh no esta instalado"
fi

echo
echo "[8] fetch de referencia (no modifica nada)"
git fetch origin --prune 2>&1 | sed 's/^/    /'
echo "    origin/main ahora: $(git rev-list -n1 origin/main 2>/dev/null)"

echo
echo "[9] ¿Hay stashes sin subir?"
git stash list || true

echo
echo "═══════════════════════════════════════════════════════════════"
echo " LEE ESTO:"
echo "  - Si [4] lista tus commits de hoy y [7] da OK -> el push fallo por"
echo "    otra razon; pega la salida de 'git push -v origin main -n' a un"
echo "    humano responsable de leerla."
echo "  - Si [1] NO dice RVenegas7/sisv.git -> el equipo de la oficina"
echo "    apunta a OTRO remoto: esa es la causa, hay que corregir origin."
echo "  - Si [7] dice permission denied -> falta la llave SSH de github"
echo "    en esta maquina; el push sale en silencio con esa cuenta."
echo "  - Si [4] no lista nada -> no quedaron cambios sin subir: los"
echo "    commits 'de hoy' estan en otra rama o en otro checkout."
echo "═══════════════════════════════════════════════════════════════"