-- ====================================================================
-- Correccion en vivo del PUNTO CRITICO del Informe_BD_SIS_LAR1
-- Cola de sincronizacion SISMAI.EVENTOS_SINC detenida desde 2026-08-27
-- --------------------------------------------------------------------
-- PASOS (en este orden, con respaldo previo obligatorio):
--   [A] Respaldo puntual de la cola (SIEMPRE antes de tocar nada)
--   [B] Recompilar los objetos invalidos de la app (informe 5.3)
--   [C] Estado de la cola y del staging TEMP (indicadores de remediacion)
--   [D] (OPCIONAL y NO automatico) purga solo cuando el central confirme
--       que recibio la carga del 27-08 por otra via. Ver seccion [D].
-- --------------------------------------------------------------------
-- Uso: sqlplus oracle/oracle@lar1 as sysdba @corregir_sinc_eventos_sinc.sql
-- O bien via SSH:  ./migracion/corregir_sinc_live.sh
-- NOTA: este script NO realiza TRUNCATE ni borra datos; la purga (seccion
-- [D]) queda comentada y se habilita manualmente cuando se autorice.
-- ====================================================================

SET PAGESIZE 200
SET LINESIZE 220
SET LONG 200
SET FEEDBACK ON
SET NULL (null)
WHENEVER SQLERROR CONTINUE

PROMPT ====================================================================
PROMPT [A] RESGUARDO PUNTUAL DE LA COLA (obligatorio antes de toda accion)
PROMPT ====================================================================
PROMPT A.0 Espacio libre en tablespaces (evitar llenar disco con el respaldo)
SELECT TABLESPACE_NAME AS TS,
       ROUND(SUM(BYTES)/1048576) AS MB_LIBRES,
       ROUND(SUM(MAXBYTES)/1048576) AS MB_MAX
  FROM DBA_FREE_SPACE
 GROUP BY TABLESPACE_NAME
 HAVING SUM(BYTES) < 2048 * 1048576
 ORDER BY MB_LIBRES;

PROMPT A.1 Dimensión actual de la cola (referencia: 3.372.065 el 18/09)
SELECT COUNT(*) AS TOTAL_COLA, TO_CHAR(MAX(FECHA),'YYYY-MM-DD HH24:MI:SS') AS ULTIMO
  FROM SISMAI.EVENTOS_SINC;

PROMPT A.2 Crear respaldo de la cola (idempotente a nivel de dia)
DECLARE
  v_dia  VARCHAR2(30) := TO_CHAR(SYSDATE,'YYYYMMDD');
  v_sql  VARCHAR2(200);
BEGIN
  -- Verifica si el respaldo del dia ya existe; si no, lo crea.
  SELECT COUNT(*) INTO v_dia
    FROM ALL_TABLES
   WHERE OWNER = 'SISMAI' AND TABLE_NAME LIKE 'EVENTOS_SINC_BK_' || v_dia || '%';
  IF v_dia = 0 THEN
    v_sql := 'CREATE TABLE SISMAI.EVENTOS_SINC_BK_' || TO_CHAR(SYSDATE,'YYYYMMDD')
          || ' AS SELECT * FROM SISMAI.EVENTOS_SINC';
    EXECUTE IMMEDIATE v_sql;
    DBMS_OUTPUT.PUT_LINE('Respaldo creado: EVENTOS_SINC_BK_' || TO_CHAR(SYSDATE,'YYYYMMDD'));
  ELSE
    DBMS_OUTPUT.PUT_LINE('Respaldo YA EXISTE para hoy; no se duplica.');
  END IF;
END;
/

PROMPT A.3 Verificar que el respaldo quedo completo (debe coincidir con A.1)
DECLARE
  v_tab  VARCHAR2(60);
  v_n    NUMBER;
BEGIN
  SELECT MAX(TABLE_NAME) INTO v_tab FROM ALL_TABLES
   WHERE OWNER = 'SISMAI'
     AND TABLE_NAME LIKE 'EVENTOS_SINC_BK_' || TO_CHAR(SYSDATE,'YYYYMMDD') || '%';
  IF v_tab IS NULL THEN
    DBMS_OUTPUT.PUT_LINE('AVISO: no encontré el respaldo del día en SISMAI.');
  ELSE
    EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM SISMAI.' || v_tab INTO v_n;
    DBMS_OUTPUT.PUT_LINE(v_tab || ' => ' || v_n || ' filas');
  END IF;
END;
/
PROMPT (El respaldo debe coincidir con la cola A.1 para proceder con la purga.)
SET SERVEROUTPUT OFF
SELECT 'EVENTOS_SINC' AS TABLA, COUNT(*) AS FILAS FROM SISMAI.EVENTOS_SINC;
SET SERVEROUTPUT ON

PROMPT
PROMPT ====================================================================
PROMPT [B] RECOMPILAR OBJETOS INVALIDOS DE LA APP (informe 5.3: 16 objetos)
PROMPT --------------------------------------------------------------------
PROMPT ATENCION: ejecutar en ventana de mantenimiento, fuera del horario
PROMPT de operacion de la app. No borra datos; solo revalida objetos.
PROMPT ====================================================================
PROMPT B.1 Invalidos antes de recompilar
SELECT OBJECT_TYPE, OBJECT_NAME, STATUS, COUNT(*) OVER () AS TOTAL_INVALIDOS
  FROM ALL_OBJECTS
 WHERE OWNER = 'SISMAI' AND STATUS = 'INVALID'
 ORDER BY OBJECT_TYPE, OBJECT_NAME;

PROMPT B.2 Recompilar el esquema completo (una sola pasada)
BEGIN DBMS_UTILITY.COMPILE_SCHEMA('SISMAI'); END;
/

PROMPT B.3 Invalidos despues de la recompilacion (ideal: 0 filas)
SELECT OBJECT_TYPE, OBJECT_NAME FROM ALL_OBJECTS
 WHERE OWNER = 'SISMAI' AND STATUS = 'INVALID'
 ORDER BY OBJECT_TYPE, OBJECT_NAME;
PROMPT (Si quedan objetos, ver nota en PENDIENTES §16 para compilacion
PROMPT  selectiva p. ej. ALTER ... COMPILE).

PROMPT
PROMPT ====================================================================
PROMPT [C] INDICADORES DE REMEDIACION
PROMPT ====================================================================
PROMPT C.1 Cola: TOTAL debe bajar 3,37M -> 0 y ULTIMO debe ser reciente
SELECT COUNT(*) AS TOTAL_COLA, TO_CHAR(MAX(FECHA),'YYYY-MM-DD HH24:MI:SS') AS ULTIMO
  FROM SISMAI.EVENTOS_SINC;

PROMPT C.2 Staging TEMP del ultimo envio (los sobres al central)
SELECT 'T_EVENTOS' AS SOBRE, COUNT(*) AS CANT FROM TEMP.T_EVENTOS
UNION ALL SELECT 'T_RENGTELE', COUNT(*) FROM TEMP.T_RENGTELE
UNION ALL SELECT 'T_RENEPI15', COUNT(*) FROM TEMP.T_RENEPI15
UNION ALL SELECT 'T_RENDSP04', COUNT(*) FROM TEMP.T_RENDSP04
UNION ALL SELECT 'T_DOCUMENT', COUNT(*) FROM TEMP.T_DOCUMENT
UNION ALL SELECT 'T_CERTMORT', COUNT(*) FROM TEMP.T_CERTMORT
UNION ALL SELECT 'T_RNACNACI', COUNT(*) FROM TEMP.T_RNACNACI
UNION ALL SELECT 'T_MADRNACI', COUNT(*) FROM TEMP.T_MADRNACI;

PROMPT C.3 Rango temporal del manifiesto del ultimo envio
SELECT TO_CHAR(MIN(FECHA),'YYYY-MM-DD HH24:MI') AS MIN_FECHA,
       TO_CHAR(MAX(FECHA),'YYYY-MM-DD HH24:MI') AS MAX_FECHA, COUNT(*) AS CANT
  FROM TEMP.T_EVENTOS;

PROMPT
PROMPT ====================================================================
PROMPT [D] PURGA OPCIONAL - NO AUTOMATICA, SOLO MANUAL CUANDO SE AUTORICE
PROMPT --------------------------------------------------------------------
PROMPT Ejecutar SOLO si, con respaldo ya confirmado (seccion [A]), el nivel
PROMPT central confirma que la carga del 27-08 llego por otra via (informe
PROMPT 6.1.4). Descomentar y ejecutar en ventana de mantenimiento:
PROMPT
PROMPT   -- TRUNCATE TABLE SISMAI.EVENTOS_SINC DROP STORAGE;
PROMPT
PROMPT Antes de purgar conviene que el proceso consumidor (RoutLar1,
PROMPT SincFich, plcer1) este restaurado, para no perder los eventos que
PROMPT aun no se han exportado al central.
PROMPT ====================================================================
EXIT