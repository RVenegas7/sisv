#!/usr/bin/env bash
# ====================================================================
# RECONOCIMIENTO DE SOLO LECTURA en el servidor SIS/LARA (srvsis).
# Objetivo: identificar QUE componente genera /home/.../repllar1.log
# (fase de replicacion que arma TEMP.T_* desde SISMAI.EVENTOS_SINC)
# y desde donde se lanza.
# --------------------------------------------------------------------
# Este script NO ejecuta la fase de replicacion, NO escribe nada en
# el servidor y NO modifica la base de datos: solo `ls`, `find`,
# `grep`, `ps`, `crontab -l` y `cat` de archivos de texto.
# --------------------------------------------------------------------
# Contexto (ver PENDIENTES.md 16 y 17.7):
#   - Los sobres `routlar1_*.ZIP` llevan 5 archivos; desde el 08/09/2026
#     solo 4 (falta `repllar1.log`) => la fase de replicacion no corre.
#   - El cron del servidor solo tiene el respaldo de las 13:00 y
#     `/home/salud/bin` esta vacio => el orquestador no esta en el Linux.
#   - La guia oficial indica que la sincronizacion se dispara desde el
#     menu Windows de `SistemaTransferencia.exe` (PENDIENTES.md 17.3).
#   - Este script averigua si queda algun rastro local de ese motor.
# --------------------------------------------------------------------
# Uso (en el servidor):   bash recon_repllar1_remoto.sh
# Uso (desde el PC):      ./migracion/recon_repllar1.sh
# ====================================================================

sep() { echo; echo "############################################################"; echo "## $1"; echo "############################################################"; }

sep "[0] ENTORNO (solo lectura)"
hostname
date
uname -a
uptime
id
echo "-- Interfaces/DNS:"
timeout 5 hostname -f 2>/dev/null || echo "(sin FQDN)"

sep "[1] /home Y EL USUARIO salud (share Samba 'Salud')"
ls -la --time-style=long-iso /home 2>&1
for d in /home/salud /home/salud/bin /home/salud/Aplicaciones /home/salud/Aplicaciones/*; do
  echo "-- $d"
  ls -la --time-style=long-iso "$d" 2>&1 | head -40
done

sep "[2] BUSQUEDA DEL ORQUESTADOR (SincFich / RoutLar1 / plcer1 / SistemaTransferencia)"
echo "-- mtime tamano ruta (los mas antiguos al final)"
timeout 120 find /home /opt /usr/local /srv /etc -maxdepth 5 \
  \( -iname "*sinc*" -o -iname "*routlar*" -o -iname "*repl*" \
     -o -iname "*plcer*" -o -iname "*transfer*" -o -iname "*sis*" \) \
  -printf "%TY-%Tm-%Td %TH:%TM %10s %p\n" 2>/dev/null | sort | tail -150

sep "[3] DESDE DONDE SE LANZA (cron / at / init)"
echo "-- crontab del usuario actual:"
crontab -l 2>&1
echo "-- /etc/crontab:"
grep -v "^#" /etc/crontab 2>/dev/null | grep -v "^[[:space:]]*$"
echo "-- /etc/crontabs (SuSE):"
ls -la --time-style=long-iso /etc/crontabs 2>&1
for f in /etc/crontabs/*; do
  echo "### $f"
  grep -v "^#" "$f" 2>/dev/null | grep -v "^[[:space:]]*$"
done
echo "-- /etc/cron.d:"
ls -la --time-style=long-iso /etc/cron.d 2>&1
for f in /etc/cron.d/*; do
  echo "### $f"
  grep -v "^#" "$f" 2>/dev/null | grep -v "^[[:space:]]*$"
done
echo "-- /var/spool/cron/tabs (solo lectura del directorio):"
ls -la --time-style=long-iso /var/spool/cron/tabs 2>&1
echo "   (el crontab de root con el respaldo de las 13:00 NO es legible aqui;"
echo "    para verlo: sudo cat /var/spool/cron/tabs/root)"
echo "-- crontab de otros usuarios relevantes (requiere root):"
for u in oracle salud root; do
  printf "### crontab -u %s -l: " "$u"
  crontab -u "$u" -l 2>&1 | tr '\n' ' '
  echo
done
echo "-- /etc/cron.hourly|daily|weekly|monthly:"
ls -la /etc/cron.hourly /etc/cron.daily /etc/cron.weekly /etc/cron.monthly 2>&1
echo "-- /etc/init.d:"
ls /etc/init.d 2>&1
echo "-- cola de at:"
atq 2>&1

sep "[4] RASTRO: que archivo/escribe el nombre repllar1"
echo "-- archivos que mencionan 'repllar1' (el que aparezca es el generador):"
R="/home/salud /home/respaldo /opt /usr/local /srv /etc"
timeout 90 grep -rIl "repllar1" $R 2>/dev/null | head -40
echo "-- archivos que mencionan los otros logs del sobre:"
timeout 90 grep -rIl -e "copyhistlar1" -e "bloqlar1" -e "routlar1" $R 2>/dev/null | head -40
echo "-- archivos que mencionan el ejecutable de Windows:"
timeout 90 grep -rIil -e "SistemaTransferencia" -e "sistematransferencia" $R 2>/dev/null | head -40

sep "[5] LOS 5 ARCHIVOS DEL SOBRE: donde estan y de cuando son"
echo "-- (repllar1/routlar1/bloqlar1/copyhistlar1/routlar1.dmp)"
timeout 120 find /home /opt /srv -maxdepth 5 \
  \( -name "repllar1*" -o -name "routlar1*" -o -name "bloqlar1*" \
     -o -name "copyhistlar1*" \) \
  -printf "%TY-%Tm-%Td %TH:%TM %10s %p\n" 2>/dev/null | sort | tail -60

sep "[6] PROCESOS (nada deberia estar corriendo un martes a la tarde)"
ps -ef | grep -iE "sqlplus|exp |imp |zip |sinc|repl|transf" | grep -v grep
echo "-- Oracle:"
ps -ef | grep -iE "tnslsnr|ora_pmon" | grep -v grep

sep "[7] HISTORIAL DE COMANDOS (rastro de ejecuciones manuales)"
for h in "$HOME/.bash_history" "$HOME/.sh_history" /home/salud/.bash_history /home/salud/.sh_history; do
  echo "-- $h"
  if [ -r "$h" ]; then
    grep -inE "sinc|repl|plcer|routlar|transfer|zip|exp |imp " "$h" 2>/dev/null | tail -40
  else
    echo "   (no existe o no es legible)"
  fi
done

sep "[8] SAMBA (share 'Salud' -> /home/salud/Aplicaciones)"
grep -vE "^[[:space:]]*#|^[[:space:]]*$" /etc/samba/smb.conf 2>/dev/null | head -40

sep "[9] DISCO (holgura, por si hay que escribir logs/zips)"
df -h /home /bd /tmp 2>&1

sep "FIN DEL RECONOCIMIENTO (no se modifico nada)"
