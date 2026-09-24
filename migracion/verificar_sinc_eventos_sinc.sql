-- ====================================================================
-- Verificacion en vivo del PUNTO CRITICO del Informe_BD_SIS_LAR1
-- Cola de sincronizacion SISMAI.EVENTOS_SINC detenida desde 2026-08-27
-- --------------------------------------------------------------------
-- Referencia (informe 18/09/2026): EVENTOS_SINC = 3.372.065 filas,
--   MAX(FECHA)=2026-08-27 12:53:50; 3.359.781 insertadas el 27-08.
-- Envio del 22/09/2026 (routlar1) ya espejado en PostgreSQL:
--   T_EVENTOS cubre SOLO 2026-09-16 .. 2026-09-22 (9.496 filas) =>
--   el backlog NO viajo en el sobre semanal.
-- --------------------------------------------------------------------
-- Uso: sqlplus respaldo/respaldo@lar1 @verificar_sinc_eventos_sinc.sql
-- (sin modificaciones en el servidor; solo lecturas)
-- ====================================================================

SET PAGESIZE 200
SET LINESIZE 220
SET LONG 200
SET FEEDBACK ON
SET NULL (null)

PROMPT ====================================================================
PROMPT [0] Contexto de la sesion y hora del servidor
PROMPT ====================================================================
SELECT banner FROM v$version WHERE ROWNUM = 1;
SELECT TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS') AS HORA_SERVIDOR FROM DUAL;
SELECT SYS_CONTEXT('USERENV','SESSION_USER') AS SESION_ACTUAL FROM DUAL;

PROMPT
PROMPT ====================================================================
PROMPT [1] EVENTOS_SINC, cola principal (CRITICO)
PROMPT Total/primera/ultima fecha. Resuelto si:
PROMPT   - TOTAL baja respecto a 3.372.065 y MAX(FECHA) es reciente (<1 dia)
PROMPT   - y, ademas, TEMP.T_* de un envio contuvo el backlog (seccion [6])
PROMPT ====================================================================
PROMPT [1.1] Total, minimo y maximo de FECHA
SELECT COUNT(*) AS TOTAL_EVENTOS,
       TO_CHAR(MIN(FECHA),'YYYY-MM-DD HH24:MI:SS') AS PRIMER_EVENTO,
       TO_CHAR(MAX(FECHA),'YYYY-MM-DD HH24:MI:SS') AS ULTIMO_EVENTO
  FROM SISMAI.EVENTOS_SINC;

PROMPT [1.2] Impacto del 27/08 y nuevos desde el 27/08
SELECT COUNT(*) AS TOTAL,
       SUM(CASE WHEN TRUNC(FECHA) <= TO_DATE('2026-08-27','YYYY-MM-DD')
                THEN 1 ELSE 0 END) AS HASTA_20260827,
       SUM(CASE WHEN TRUNC(FECHA) >  TO_DATE('2026-08-27','YYYY-MM-DD')
                THEN 1 ELSE 0 END) AS POST_20260827
  FROM SISMAI.EVENTOS_SINC;

PROMPT [1.3] Distribucion por TABLA/EVENTO (informe 6.1)
SELECT TABLA, EVENTO, COUNT(*) AS CANT
  FROM SISMAI.EVENTOS_SINC
 GROUP BY TABLA, EVENTO
 ORDER BY CANT DESC;

PROMPT [1.4] Por dia (ultimos 75 dias)
SELECT TO_CHAR(TRUNC(FECHA),'YYYY-MM-DD') AS DIA, COUNT(*) AS CANT
  FROM SISMAI.EVENTOS_SINC
 WHERE FECHA >= TRUNC(SYSDATE) - 75
 GROUP BY TRUNC(FECHA)
 ORDER BY TRUNC(FECHA) DESC;

PROMPT [1.5] Distribucion por STATUS
SELECT STATUS, COUNT(*) AS CANT
  FROM SISMAI.EVENTOS_SINC
 GROUP BY STATUS
 ORDER BY STATUS;

PROMPT [1.6] Respaldo puntual recomendado por el informe
SELECT OWNER, TABLE_NAME
  FROM ALL_TABLES
 WHERE TABLE_NAME LIKE 'EVENTOS_SINC_BK%'
 ORDER BY TABLE_NAME;

PROMPT
PROMPT ====================================================================
PROMPT [2] Backlog EVENTOS_DBLINK / HISTORICO.EVENTOS_RESP (hallazgo ALTO)
PROMPT Todos STATUS=0 y creciendo ~33.281/mes. Confirmar si algo los consume.
PROMPT ====================================================================
PROMPT [2.1] SISMAI.EVENTOS_DBLINK
SELECT COUNT(*) AS TOTAL,
       SUM(CASE WHEN STATUS = 0 THEN 1 ELSE 0 END) AS STATUS_0,
       TO_CHAR(MIN(FECHA),'YYYY-MM-DD HH24:MI:SS') AS PRIMER_EVENTO,
       TO_CHAR(MAX(FECHA),'YYYY-MM-DD HH24:MI:SS') AS ULTIMO_EVENTO
  FROM SISMAI.EVENTOS_DBLINK;

PROMPT [2.2] HISTORICO.EVENTOS_RESP
SELECT COUNT(*) AS TOTAL,
       SUM(CASE WHEN STATUS = 0 THEN 1 ELSE 0 END) AS STATUS_0,
       TO_CHAR(MIN(FECHA),'YYYY-MM-DD HH24:MI:SS') AS PRIMER_EVENTO,
       TO_CHAR(MAX(FECHA),'YYYY-MM-DD HH24:MI:SS') AS ULTIMO_EVENTO
  FROM HISTORICO.EVENTOS_RESP;

PROMPT
PROMPT ====================================================================
PROMPT [3] HISTORICO.EVENTOS, bitacora de procesamientos COMPLETADOS
PROMPT (STATUS<>0, informe 5.4: 15.281 filas, 976 en el ultimo mes)
PROMPT Si sigue creciendo a diario, el motor SI procesa en algo.
PROMPT ====================================================================
SELECT TO_CHAR(TRUNC(FECHA),'YYYY-MM-DD') AS DIA, COUNT(*) AS CANT
  FROM HISTORICO.EVENTOS
 WHERE FECHA >= TRUNC(SYSDATE) - 30
 GROUP BY TRUNC(FECHA)
 ORDER BY TRUNC(FECHA) DESC;

PROMPT
PROMPT ====================================================================
PROMPT [4] SISMAI.EVENTOS (movimiento diario, STATUS=0 en vivo)
PROMPT ====================================================================
SELECT TO_CHAR(TRUNC(FECHA),'YYYY-MM-DD') AS DIA, COUNT(*) AS CANT
  FROM SISMAI.EVENTOS
 WHERE FECHA >= TRUNC(SYSDATE) - 30
 GROUP BY TRUNC(FECHA)
 ORDER BY TRUNC(FECHA) DESC;

PROMPT
PROMPT ====================================================================
PROMPT [5] ERRORES (buena senal si vacias)
PROMPT ====================================================================
SELECT 'SISMAI.ERRORES' AS TABLA, COUNT(*) AS CANT FROM SISMAI.ERRORES
UNION ALL SELECT 'SISMAI.ERRORES_SINC', COUNT(*) FROM SISMAI.ERRORES_SINC;

PROMPT
PROMPT ====================================================================
PROMPT [6] TEMP staging (los sobres del envio al central)
PROMPT Comparar con lo enviado: el paso de ruteo llena TEMP.T_* y TRUNCA.
PROMPT Si TEMP.T_RENGTELE/T_RENEPI15/T_RENDSP04 siguen en miles (no millones)
PROMPT entonces el backlog del 27/08 NO se replico por esta via.
PROMPT (Referencia 22/09 en PG: T_EVENTOS 9.496; T_RENGTELE 5.520;
PROMPT  T_RENEPI15 1.472; T_DOCUMENT 458; T_CERTMORT 148; T_RNACNACI 278)
PROMPT ====================================================================
SELECT 'T_EVENTOS'   AS SOBRE, COUNT(*) AS CANT FROM TEMP.T_EVENTOS
UNION ALL SELECT 'T_RENGTELE',  COUNT(*) FROM TEMP.T_RENGTELE
UNION ALL SELECT 'T_RENEPI15',  COUNT(*) FROM TEMP.T_RENEPI15
UNION ALL SELECT 'T_RENDSP04',  COUNT(*) FROM TEMP.T_RENDSP04
UNION ALL SELECT 'T_DOCUMENT',  COUNT(*) FROM TEMP.T_DOCUMENT
UNION ALL SELECT 'T_CERTMORT',  COUNT(*) FROM TEMP.T_CERTMORT
UNION ALL SELECT 'T_RNACNACI',  COUNT(*) FROM TEMP.T_RNACNACI
UNION ALL SELECT 'T_MADRNACI',  COUNT(*) FROM TEMP.T_MADRNACI;

PROMPT [6.1] Rango temporal del indice TEMP.T_EVENTOS
SELECT TO_CHAR(MIN(FECHA),'YYYY-MM-DD HH24:MI') AS MIN_FECHA,
       TO_CHAR(MAX(FECHA),'YYYY-MM-DD HH24:MI') AS MAX_FECHA,
       COUNT(*) AS CANT
  FROM TEMP.T_EVENTOS;

PROMPT
PROMPT ====================================================================
PROMPT [7] Resumen automatico del veredicto (lectura orientativa)
PROMPT ====================================================================
PROMPT [7.1] EVENTOS_SINC sigue estancado en ~3,37 M?
SELECT CASE WHEN COUNT(*) > 3000000 THEN 'STAL- 6 POSIBLE SIN RESOLVER (cola > 3 M)'
            WHEN COUNT(*) = 0            THEN 'OK- 7 COLA VACIA (truncada/reprocesada)'
            WHEN MAX(FECHA) > SYSDATE-1  THEN 'OK- 7 COLA CONSUMIENDOSE (reciente)'
            ELSE 'PAR- 6 PUEDE HABER BACKLOG PARCIAL'
       END AS VEREDICTO_EVENTOS_SINC
  FROM SISMAI.EVENTOS_SINC;

PROMPT [7.2] El backlog viajo en TEMP? (T_RENGTELE millones?)
SELECT CASE WHEN COUNT(*) > 1000000 THEN 'SI- 8 BACKLOG REPLICADO en los sobres'
            ELSE 'NO- 9 BACKLOG AUSENTE de los sobres del envio'
       END AS VEREDICTO_TEMP
  FROM TEMP.T_RENGTELE;

PROMPT
PROMPT ====================================================================
PROMPT [8] Criterio final (interpretar a la luz de 1.1 y 6.1)
PROMPT RESUELTO  => EVENTOS_SINC ~0 y TEMP muestran las semanas 28-37
PROMPT ESTANCADO => EVENTOS_SINC sigue ~3,37 M (o >1 M) y la cola no baja
PROMPT PERDIDO   => EVENTOS_SINC ~0 pero los sobres NUNCA incluyeron el
PROMPT              backlog (sin rastro en TEMP de semanas 29-36)
PROMPT ====================================================================
EXIT