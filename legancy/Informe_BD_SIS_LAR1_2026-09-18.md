# Informe de Diagnóstico – Base de Datos SIS/Oracle (SID LAR1 / BDLAR1)

**Fecha:** 2026-09-18  
**Hora del análisis:** 15:37 (GMT-4)  
**Analizado por:** Rafael Venegas  
**Servidor:** srvsis (192.168.5.200) – SUSE Linux SL 11.4, 32 bits  
**Motor:** Oracle Database 10g Enterprise Edition **10.1.0.3.0** (EOL: sin soporte/parches)  
**Instancia:** lar1 – Base:** BDLAR1 – creada 2024-01-09  
**Alcance:** análisis en vivo mediante SQL*Plus (usuario `respaldo`, habilitado por el propio script de respaldo diario `expbdsismai.bat`). Sin modificaciones en el servidor; solo lecturas.

---

## 1. Resumen ejecutivo

- La base está **arriba y respondiendo** desde el **2026-08-11 08:37** (≥ 38 días sin reinicio). El alert log no muestra errores nuevos desde el 03-08-2026.
- El **respaldo lógico diario funciona** (cron 13:00, `exp respaldo/respaldo` → `BDSISMAI.DMP` ~1.2 GB + `bkbdlar1_*.tgz` ~203 MB, "Export terminated successfully without warnings" el día de hoy).
- Los tablespaces tienen **holgura** (uso 0.7%–40%); espacio en disco OK (~29–61 GB libres).
- **Hallazgo crítico:** la **cola de sincronización `SISMAI.EVENTOS_SINC` está detenida desde el 2026-08-27 12:53**, con **3.372.065 eventos sin procesar** (99.6 % insertados ese mismo día). Los cambios de Lara no se están replicando al nivel central desde hace 3 semanas.
- **Hallazgo de riesgo:** las tablas `EVENTOS_DBLINK` (2.329.199 filas) y `EVENTOS_RESP` (1.929.662 filas) están al **100 % con STATUS=0** y siguen creciendo (~33.281 eventos/mes) sin que nada las procese.
- Otros riesgos: base en **NOARCHIVELOG** (sin RMAN/redo archivado), `undo_retention=900 s`, auditoría desactivada, contraseñas sin política de expiración, y 92 objetos inválidos (16 de la aplicación `SISMAI`).

---

## 2. Infraestructura descubierta

| Elemento | Detalle |
|---|---|
| Servidor BD | `srvsis` = 192.168.5.200 (SUSE 11.4, i686, kernel 2.6.37) |
| Oracle Home | `/opt/oracle` (binarios 32 bits), SID `lar1` (oratab) |
| Datafiles | `/bd/bdlar1/*.dbf` (+ redo logs `log1..3lar1.rdo`) |
| Listener | `/opt/oracle/bin/tnslsnr` en 1521 |
| Alert log | `/opt/oracle/rdbms/log/alert_lar1.log` (instalación "sin admin", bdump no estándar) |
| Usuarios BD | `SISMAI` (DBA), `HISTORICO` (DBA), `TEMP` (DBA), `TEMP3` (DBA), `INBDLAR1`, `ANALISTA`, `RESPALDO` (EXP/IMP full), `SYSTEM`, `SYS`, `OUTLN`, `DBSNMP` |
| Credenciales de respaldo | `respaldo/respaldo` (en `creausu.sql` y en el `.bat` de respaldo) |
| Acceso SSH | user `respaldo` / pass `respaldo` (el mismo uso real: `pscp -pw respaldo ...`) |
| Samba | share `Salud` → `/home/salud/Aplicaciones`, readonly, solo user `salud` |

> La IP que servía la BD no es la .201 (que resulta un proxmox/proxy) ni la .14 (filtrada): **es la .200**.

---

## 3. Estado general de la instancia

| Parámetro | Valor | Comentario |
|---|---|---|
| Uptime | 2026-08-11 08:37:31 | 38+ días arriba |
| `sga_target` | 1 GB | shared/large/java pool automáticos |
| `pga_aggregate_target` | 256 MB | bajo para cargas masivas |
| `processes` / `sessions` | 100 / 115 | 15 usado de 100 en el muestreo |
| Sesiones | 14 (12 activas / 2 inactivas) | |
| `compatible` | 10.0.0 | (release binaria 10.1.0.3) |
| Modo de archivado | **NOARCHIVELOG** | riesgo alto (sin redo archivado) |
| `undo_management` | AUTO · UNDODB · retención **900 s** | riesgo ORA-01555 en consultas largas |
| `audit_trail` | NONE | sin auditoría |
| `job_queue_processes` | 0 | DBMS_JOB deshabilitado (no se usan jobs) |
| DB links | **ninguno** | la replicación es por ficheros, no enlazada por dblink |
| Scheduler | `SYS.PURGE_LOG`, `SYS.GATHER_STATS_JOB` activos (ventana nocturna 22:00) | |

### Tablespaces

| Tablespace | Tamaño | Usado | % | Libre aprox. |
|---|---|---|---|---|
| DATOS | 8.000 MB | 3.225 MB | 40 % | 4.775 MB |
| INDICE | 8.000 MB | 2.332 MB | 29 % | 5.668 MB |
| DATOS2 | 6.000 MB | 1.530 MB | 25 % | 4.470 MB |
| INDICE2 | 6.000 MB | 554 MB | 9 % | 5.446 MB |
| SYSTEM | 1.000 MB | 166 MB | 17 % | 834 MB |
| SYSAUX | 1.000 MB | 155 MB | 16 % | 845 MB |
| UNDODB | 1.000 MB | 7 MB | 1 % | 993 MB |
| TEMPORAL (temp) | 10.000 MB (1 tempfile) | – | – | **se agotó en el pasado** |

### Volúmenes por esquema

| Esquema | Tablas | Filas estimadas |
|---|---|---|
| SISMAI | 350 | 14.226.938 |
| HISTORICO | 10 | 1.861.368 |
| INBDLAR1 | 83 | 38.790 |
| TEMP | 82 | 22.562 |

Tablas más grandes (basado en el DMP/estadística previa y re-análisis): `EVENTOS_SINC` (3,37 M), `RENGLONTELE` (2,66 M), `EVENTOS_DBLINK` (2,33 M), `SMP_JOB_HISTORY_U`/`EVENTOS_RESP` (~1,93 M), `HISTORICO.EVENTOS_RESP` (~1,93 M).

---

## 4. Respaldos

- Script: `/home/respaldo/bin/expbdsismai.bat` (cron de root: `00 13 * * *`).
- Flujo: `exp respaldo/respaldo parfile=expbdsismai.sql` + `sqlplus respaldo/respaldo @monitor_respaldo.sql` (inserta en `SISMAI.MONITOR_RESPALDO` y `MONITOR_BASEDEDATOS`) + `tar cvfz bkbdlar1_FECHA.tgz BDSISMAI*`.
- Últimos DMP: ~1.235 MB constantes en los últimos 30 días; `bkbdlar1_*.tgz` ~203 MB (2026) vs ~113–138 MB (2019–2023) → **la BD creció ~10× desde 2019**.
- Monitoreo: `/home` usado crece ~197 MB/día (24.325 M el 03-08 → 33.076 M el 17-09); en `/bd` uso estable ~40 GB.
- **Sin respaldo físico**: NOARCHIVELOG + sólo export lógico → una corrupción de datafile implica pérdida del día completo.

---

## 5. Hallazgos de errores (priorizados)

### 5.1 CRÍTICO – Sincronización SISMAI detenida desde 2026-08-27
- `SISMAI.EVENTOS_SINC` = **3.372.065 filas**; última con fecha **2026-08-27 12:53:50** (tipo: `DOCUMENTO_DENGUE`).
- Distribución diaria (últ. 45 días): actividad normal de 2–105 eventos/día hasta el 25-08, y **3.359.781 eventos el 27-08** (carga masiva de documentos) que quedaron **sin procesar** (STATUS vacío).
- El diseño (`SincFich/mort/cr_repli_mort.sql`, `plcer1.sql`) confirma el ciclo: la app inserta en `EVENTOS_SINC`; el proceso de replicación exporta `TEMP.T_EVENTOS`, envía al central y **trunca la cola**. Ese truncate **no se ejecutó**.
- Evidencia de que el motor de sinc no corre: `/home/salud/bin` **vacío**, scripts `SincFich/*` y `RoutLar1/*` sin ejecutar (mtime 2020-04-04), rutas ZIP de RoutLar1 antiguas (2019), y cron del sistema sin tareas de sincronización (solo respaldo).
- Conclusión: **los cambios acumulados en Lara desde el 27-08 NO se están replicando** al sistema central (riesgo operativo/sanitario de reportes desactualizados).

### 5.2 ALTO – Backlog `EVENTOS_DBLINK` y `EVENTOS_RESP` sin consumir
- `SISMAI.EVENTOS_DBLINK`: 2.329.199 filas, **todas STATUS=0**, ~33.281 en los últimos 30 días, última 2026-09-18 13:00 (crecimiento diario).
- `HISTORICO.EVENTOS_RESP`: 1.929.662 filas, **todas STATUS=0**, mismo crecimiento y horario.
- Ningún proceso marca STATUS=1 los eventos; los eventos de "history/dblink" se acumulan.

### 5.3 MEDIO – Objetos inválidos (92 total)
- **De aplicación SISMAI (16):**
  - 11 vistas: `C_INFORMES`, `C_INFORMES1`, `NATALIDAD`, `V_REGISTROCIRUGIA`, `V_FICHAEPI13`, `C_ESTABLECIMIENTO`, `V_ESTABLE_DIREC`, `V_ORG_SANITARIA`, `V_PACIENTEVACUNACION`, `V_PACIENTECIRUGIA`, `H_DEPEN`.
  - 4 procedimientos: `SPREGTEL`, `SPDOC`, `SPREGDSP`, `SPREGEPI`.
  - 1 función: `FIDPADRE`.
- De catálogo SYS/PUBLIC (≈76): vistas/sinónimos `DBA_HIST_*` (estadísticas históricas), replicación `DBMS_REP*`/`DBMS_DEFER*`/`DBMS_SNAPSHOT`, `DBMS_SQLTUNE`, `AQ$_DEF*`. Típico de 10.1.0.3 sin parches; impide usar AWR/estadísticas históricas.

### 5.4 MEDIO – Tabla de errores y eventos de la aplicación
- Las tablas `SISMAI.ERRORES`, `ERRORES_SINC`, `ERRORES_LABO`, `ERRORES_RESI`, `ERRORES_ANUARIO` y `HISTORICO.ERRORES*` están **vacías** (buena señal: sin errores de aplicación vigentes).
- `SISMAI.EVENTOS`: 2.365 filas recientes (movimiento diario, STATUS=0).
- `HISTORICO.EVENTOS`: 15.281 filas todas con STATUS≠0 (es la que sí refleja procesamientos completados; 976 en el último mes).

### 5.5 MEDIO – Agotamiento de tablespace TEMPORAL (ORA-1652)
- Alert log acumula **69 × ORA-1652** "unable to extend temp segment by 128" en tablespace **TEMPORAL** (10 GB, un solo tempfile). Últimos episodios: **2026-08-03 08:49–10:27** (previos también esporádicos). La instancia **fue reiniciada el 11-08** (posiblemente tras esa contingencia).
- Sugerencia: agregar un segundo tempfile o ampliar `TEMPORAL` (el proceso de re-creación de índices / importaciones masivas lo agota).

### 5.6 MEDIO – Configuración y riesgos operativos
- **NOARCHIVELOG sin RMAN**: pérdida potencial del último día en cualquier fallo de media físicamente.
- `undo_retention=900 s` (15 min): con el `exp` diario (~1,2 GB, >15 min) y consultas largas hay riesgo de **ORA-01555**.
- **Estadísticas desactualizadas**: tablas `HISTORICO.*` sin `last_analyzed` desde **2024-01-15** (GATHER_STATS_JOB parece no cubrirlas); `SISMAI.*` re-anali­zadas 2026-09-12 (ok).
- `TEMP` (esquema, no tablespace) recreado el **2026-09-16**: es el esquema de stage del pipeline TEMP→INBDLAR1→SISMAI.

### 5.7 MEDIO/BAJO – Seguridad
- `audit_trail=NONE`; profile `DEFAULT` sin política de contraseñas (PASSWORD_LIFE_TIME/LOCK_TIME/FAILED_LOGIN_ATTEMPTS = UNLIMITED).
- Usuarios de aplicación con rol **DBA** (`GRANT DBA TO SISMAI/HISTORICO/TEMP` en `creausu.sql`).
- Credenciales triviales (`respaldo/respaldo`, `SISMAI/SISMAI`, `TEMP/TEMP`) y la clave SSH/DB documentada en `.bat` de Windows en claro.
- Sistema operativo 32 bits SUSE 11.4 (EOL), motor 10.1.0.3 (EOL).

---

## 6. Sugerencias de resolución de los hallazgos (plan de acción)

### 6.1 Sincronización detenida – `EVENTOS_SINC` (ver 5.1)

1. **Localizar el componente de sincronización:** el motor que lee `EVENTOS_SINC`, exporta `TEMP.T_EVENTOS` y trunca la cola no está corriendo (`/home/salud/bin` vacío, crontab solo tiene el respaldo). Revisar con el soporte SIS/Centura dónde se instaló (cliente Windows, servidor central) y restaurar su ejecución.
2. **Diagnóstico previo a reprocesar** (solo consulta):
   ```sql
   SELECT TABLA, EVENTO, COUNT(*) FROM SISMAI.EVENTOS_SINC GROUP BY TABLA, EVENTO;
   SELECT COUNT(*), MAX(FECHA) FROM SISMAI.EVENTOS_SINC;
   ```
3. **Respaldo puntual de la cola** (antes de cualquier purga/reproceso):
   ```sql
   CREATE TABLE SISMAI.EVENTOS_SINC_BK_20260918 AS SELECT * FROM SISMAI.EVENTOS_SINC;
   ```
4. **Verificar con el destino central** si los 3,37 M de `DOCUMENTO_DENGUE` del 27-08 ya llegaron; si ya se replicaron por otra vía, purgar:
   ```sql
   TRUNCATE TABLE SISMAI.EVENTOS_SINC DROP STORAGE;
   ``` 
   (solo después de restablecer el consumo; nunca truncar a ciegas).
5. **Alertas de cola:** monitoreo diario: alertar si `MAX(FECHA)` > 1 día o si el conteo supera un umbral (p. ej. 10.000).

### 6.2 Backlog `EVENTOS_DBLINK` y `EVENTOS_RESP` (ver 5.2)

1. **Definir la semántica de `STATUS`** con el desarrollador antes de tocar datos (0 = pendiente frente a 0 = normal).
2. Si se confirma que son eventos pendientes de un proceso inexistente, **archivar** antes de depurar:
   ```sql
   CREATE TABLE HISTORICO.EVENTOS_RESP_ARCH_2026 AS SELECT * FROM HISTORICO.EVENTOS_RESP WHERE STATUS = 0;
   CREATE TABLE SISMAI.EVENTOS_DBLINK_ARCH_2026  AS SELECT * FROM SISMAI.EVENTOS_DBLINK  WHERE STATUS = 0;
   ```
3. **Purga por lotes** (fuera de horario hábil y con commit periódico) de las ~4,2 M filas acumuladas, p. ej. `DELETE ... WHERE ROWNUM <= 50000` en loop o `TRUNCATE` tras respaldo.

### 6.3 Objetos inválidos (ver 5.3)

1. **Recompilar todo el esquema** (una sola vez, en ventana de mantenimiento):
   ```sql
   BEGIN DBMS_UTILITY.COMPILE_SCHEMA('SISMAI'); END;
   -- o paralelo: BEGIN UTL_RECOMP.RECOMP_PARALLEL(4, 'SISMAI'); END;
   ```
2. Si quedan piezas individuales:
   ```sql
   ALTER VIEW       SISMAI.NATALIDAD COMPILE;
   ALTER PROCEDURE  SISMAI.SPDOC     COMPILE;
   ALTER FUNCTION   SISMAI.FIDPADRE  COMPILE;
   ```
3. **Revisar dependencias** si una pieza sigue inválida (`SELECT * FROM DBA_DEPENDENCIES WHERE REFERENCED_OBJECT_NAME='...'`); probable causa: recreación del esquema `TEMP` el 16-09 o importación parcial.
4. **Catálogo SYS/PUBLIC:** ejecutar el utilitario estándar antes de ignorarlos:
   ```sql
   @?/rdbms/admin/utlrp.sql
   ```
   Los que persistan (replicación `DBMS_REP*`/`DBMS_DEFER*`, `DBA_HIST_*`, `DBMS_SQLTUNE`) son piezas sin uso real en 10.1.0.3 o dependientes de parches; documentar y no intervenir.

### 6.4 Agotamiento del tablespace TEMPORAL – ORA-1652 (ver 5.5)

1. **Ampliar el temp** (evita recurrencia en cargas masivas):
   ```sql
   ALTER TABLESPACE TEMPORAL ADD TEMPFILE '/bd/bdlar1/temp02.dbf' SIZE 10G AUTOEXTEND ON NEXT 1G MAXSIZE UNLIMITED;
   ```
2. **Programar** importaciones/recreación de índices fuera de horario, por partes, con `NOLOGGING`.
3. Opcional: radicar el temp en disco con espacio garantizado (`/bd` tiene ~29 GB libres).

### 6.5 Respaldo y modo NOARCHIVELOG (ver 5.6)

1. **Planificar el cambio a ARCHIVELOG** (requiere ventana + reinicio de la instancia; coordinar con producción):
   ```sql
   SHUTDOWN IMMEDIATE;
   STARTUP MOUNT;
   ALTER DATABASE ARCHIVELOG;
   ALTER DATABASE OPEN;
   ALTER SYSTEM SET log_archive_dest='/bd/arch' SCOPE=SPFILE;
   ```
   (verificar `log_archive_format` y espacio en disco antes).
2. **Activar RMAN** con backups diarios (`BACKUP DATABASE PLUS ARCHIVELOG`). Hasta entonces, **duplicar el `bkbdlar1_*.tgz` diario fuera de la máquina** (otro servidor/medio externo).

### 6.6 Undo, estadísticas y seguridad (ver 5.6–5.7)

1. **Undo:** `ALTER SYSTEM SET undo_retention=1800 SCOPE=BOTH;` y evaluar incrementar `UNDODB` para las ventanas de carga (riesgo de ORA-01555 durante el `exp` diario).
2. **Estadísticas de HISTORICO** (desactualizadas desde 2024-01-15):
   ```sql
   EXEC DBMS_STATS.GATHER_SCHEMA_STATS('HISTORICO', CASCADE=>TRUE, DEGREE=>4);
   ```
3. **Auditoría básica:** `ALTER SYSTEM SET audit_trail=DB SCOPE=SPFILE;` (requiere reinicio) y auditar conexiones fallidas/roles.
4. **Política de contraseñas** aplicable a los perfiles:
   ```sql
   CREATE PROFILE SIS_PROF LIMIT FAILED_LOGIN_ATTEMPTS 5 PASSWORD_LIFE_TIME 90 PASSWORD_LOCK_TIME 1 IDLE_TIME 15;
   ALTER USER SISMAI PROFILE SIS_PROF;
   ```
5. **Reducir privilegios:** sustituir `GRANT DBA` por roles mínimos (`CONNECT`, `RESOURCE` + tablas específicas) en `SISMAI`, `HISTORICO` y `TEMP`; rotar las contraseñas triviales (`respaldo/respaldo`, `SISMAI/SISMAI`) y **eliminar la clave en claro del `backupOra10g.bat`/scripts**.
6. **EOL:** planificar migración (SO SUSE 11.4 32-bit + Oracle 10.1.0.3 están fuera de soporte; clientes modernos como python-oracledb thin no conectan a 10g: `DPY-3010`).

---

## 7. Recomendaciones (orden de prioridad)

1. **Sincronización SIS:** restaurar/ejecutar el proceso que consume `EVENTOS_SINC` y trunca la cola (o, a propósito, reprocesar los 3,37 M de `DOCUMENTO_DENGUE`). Verificar que el envío al central recomience. **No** truncar la cola a ciegas sin respaldo ni revisión.
2. **Respaldos:** evaluar pasar a **ARCHIVELOG + RMAN** (o al menos doble exp + copia fuera de máquina); el actual es solo lógico-diario.
3. **Objetos inválidos SISMAI:** recompilar (`ALTER PROCEDURE/VIEW/FUNCTION ... COMPILE`) las 16 piezas de aplicación; documentar/descargar piezas SYS sin uso.
4. **Temp/undo:** ampliar o añadir tempfile a `TEMPORAL`; subir `undo_retention` a ≥1800 s (p.ej. `ALTER SYSTEM SET undo_retention=1800`).
5. **Estadísticas:** ejecutar `DBMS_STATS.GATHER_TABLE_STATS` para `HISTORICO.*` y verificar ventana de GATHER_STATS.
6. **Seguridad/operación:** activar auditoría básica (`audit_trail=DB`), política de contraseñas, limitar rol DBA a lo mínimo, quitar la contraseña `respaldo` en claro de los scripts de backup.
7. **Backlog DBLINK/RESP:** aclarar con el administrador la semántica de `STATUS` y depurar/limpiar las ~4,2 M filas pendientes (con respaldo previo).

---

## 8. Notas para el futuro cargador de datos en Python

- La versión 10.1.0.3 **no soporta** `expdp`/`impdp` ni clientes modernos (python-oracledb en modo thin no conecta: `DPY-3010`).
- Vías viables hoy:
  - **SQL*Plus por SSH** (método usado en este diagnóstico; readonly, sin tocar el servidor) para extraer/consultar.
  - Cliente Oracle **11.2 (32 bits)** desplegado en un contenedor Docker (o `instantclient 11.2`) para usar python-oracledb/cx_Oracle en modo thick contra 10g.
  - Para carga: `exp` (como el actual) o consulta directa y transporte por fi­cheros (`sinccod/sincdoc/sincfich`).
- Vigilar **charset** (`WE8ISO8859P1` en servidor; export US7ASCII) al normalizar a UTF-8 en el nuevo pipeline.