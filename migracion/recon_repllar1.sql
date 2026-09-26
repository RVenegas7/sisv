-- ====================================================================
-- RECONOCIMIENTO EN VIVO (SOLO LECTURAS) de la fase de REPLICACION
-- que produce `repllar1.log` y arma TEMP.T_* en el Oracle 10g de
-- SIS/Lara (srvsis / SID lar1).
-- --------------------------------------------------------------------
-- Que se responde con este archivo:
--   [2] Si las tablas TEMP.T_* se recrearon en la ultima corrida
--        (LAST_DDL_TIME): delata si la fase `repl` corbio o no.
--   [3] Conteo real de cada TEMP.T_*: es la misma lista de conteos
--        que cierra `repllar1.log`; al compararla con el `routlar1.log`
--        del ultimo sobre se ve que tablas quedaron a medio llenar.
--   [5] Si existe en la BD el motor (paquete/procedimiento) que hace
--        la replicacion y si esta INVALIDO (16 objetos de SISMAI lo
--        estaban el 18/09/2026).
--   [8] Que cuenta tiene permiso sobre TEMP.T_*: quien podria correr
--        el script a mano.
-- --------------------------------------------------------------------
-- Uso: sqlplus respaldo/respaldo@lar1 @recon_repllar1.sql
--   (o con usuario DBA `oracle` para ver tambien ALL_ERRORS)
-- NO contiene DDL ni DML: unicamente SELECT y consultas de diccionario.
-- ====================================================================

SET PAGESIZE 300
SET LINESIZE 220
SET LONG 20000
SET FEEDBACK ON
SET SERVEROUTPUT ON SIZE UNLIMITED
SET NULL (null)

PROMPT ====================================================================
PROMPT [0] Contexto de la sesion y hora del servidor
PROMPT ====================================================================
SELECT banner FROM v$version WHERE ROWNUM = 1;
SELECT TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS') AS HORA_SERVIDOR,
       SYS_CONTEXT('USERENV','SESSION_USER') AS USUARIO,
       SYS_CONTEXT('USERENV','SID')        AS SID
  FROM DUAL;

PROMPT
PROMPT ====================================================================
PROMPT [1] COLA VIVA SISMAI.EVENTOS_SINC (origen de TEMP.T_*)
PROMPT La recreo SincFich/crear.sql (DROP+CREATE) el 21/09/2026 09:08:37;
PROMPT   16.741 filas, sin indices ni restricciones. Si esta en 16.741
PROMPT   el dia del envio, la replicacion NO se esta alimentando.
PROMPT ====================================================================
SELECT COUNT(*) AS TOTAL,
       TO_CHAR(MIN(FECHA),'YYYY-MM-DD HH24:MI:SS') AS PRIMER_EVENTO,
       TO_CHAR(MAX(FECHA),'YYYY-MM-DD HH24:MI:SS') AS ULTIMO_EVENTO
  FROM SISMAI.EVENTOS_SINC;

PROMPT [1.1] Distribucion por TABLA/EVENTO (que viajaria al central)
SELECT TABLA, EVENTO, COUNT(*) AS CANT,
       TO_CHAR(MAX(FECHA),'YYYY-MM-DD HH24:MI') AS ULTIMO
  FROM SISMAI.EVENTOS_SINC
 GROUP BY TABLA, EVENTO
 ORDER BY CANT DESC;

PROMPT [1.2] STATUS (NULL = la replicacion no lo consume)
SELECT STATUS, COUNT(*) AS CANT FROM SISMAI.EVENTOS_SINC GROUP BY STATUS ORDER BY 1;

PROMPT [1.3] Conteo total de la cola (las 4 fases del ciclo, solo lectura)
SELECT (SELECT COUNT(*) FROM SISMAI.EVENTOS)          AS SISMAI_EVENTOS,
       (SELECT COUNT(*) FROM SISMAI.EVENTOS_SINC)     AS EVENTOS_SINC,
       (SELECT COUNT(*) FROM SISMAI.EVENTOS_DBLINK)   AS EVENTOS_DBLINK,
       (SELECT COUNT(*) FROM HISTORICO.EVENTOS)       AS HIST_EVENTOS,
       (SELECT COUNT(*) FROM HISTORICO.EVENTOS_RESP)  AS HIST_EVENTOS_RESP
  FROM DUAL;

PROMPT
PROMPT ====================================================================
PROMPT [2] TEMP.T_* : EXISTEN? CUANDO SE RECREARON? (huella de `repl`)
PROMPT La fase `repl` hace DROP/CREATE de las 83 tablas + 86 indices
PROMPT (segun repllar1.log del 04/08). Si LAST_DDL_TIME coincide con la
PROMPT fecha del ultimo envio, `repl` corrio ese dia.
PROMPT ====================================================================
SELECT COUNT(*) AS TABLAS_T,
       TO_CHAR(MIN(LAST_DDL_TIME),'YYYY-MM-DD HH24:MI') AS DDL_MAS_ANTIGUA,
       TO_CHAR(MAX(LAST_DDL_TIME),'YYYY-MM-DD HH24:MI') AS DDL_MAS_RECIENTE
  FROM ALL_OBJECTS
 WHERE OWNER = 'TEMP' AND OBJECT_TYPE = 'TABLE';

PROMPT [2.1] Las 20 T_* con DDL mas reciente
SELECT * FROM (
  SELECT object_name, object_type,
         TO_CHAR(last_ddl_time,'YYYY-MM-DD HH24:MI') AS ultimo_ddl, status
    FROM ALL_OBJECTS
   WHERE OWNER = 'TEMP'
     AND last_ddl_time IS NOT NULL
   ORDER BY last_ddl_time DESC
) WHERE ROWNUM <= 20;

PROMPT [2.2] Histograma diario de DDL en TEMP (dias en que corrio `repl`)
SELECT TO_CHAR(TRUNC(last_ddl_time),'YYYY-MM-DD') AS DIA,
       COUNT(*) AS OBJETOS,
       MIN(object_name) AS EJEMPLO
  FROM ALL_OBJECTS
 WHERE OWNER = 'TEMP'
   AND last_ddl_time IS NOT NULL
   AND last_ddl_time >= TRUNC(SYSDATE) - 120
 GROUP BY TRUNC(last_ddl_time)
 ORDER BY 1 DESC;

PROMPT [2.3] Cuantas T_* hay (integridad del esquema TEMP)
SELECT COUNT(DISTINCT table_name) AS T_QUE_EMPIEZAN_T
  FROM ALL_TABLES WHERE OWNER = 'TEMP' AND table_name LIKE 'T%';

PROMPT
PROMPT ====================================================================
PROMPT [3] CONTEO REAL DE CADA TEMP.T_* (la "cola de conteos" de
PROMPT     repllar1.log, medida en vivo). Comparar con el `routlar1.log`
PROMPT     del ultimo sobre: si aqui hay mas filas que las exportadas,
PROMPT     la tabla se lleno despues del export.
PROMPT ====================================================================
DECLARE
  v_cant NUMBER;
BEGIN
  FOR r IN (SELECT table_name
              FROM all_tables
             WHERE owner = 'TEMP' AND table_name LIKE 'T!_%' ESCAPE '!'
             ORDER BY table_name) LOOP
    BEGIN
      EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM TEMP.' || r.table_name INTO v_cant;
      IF v_cant > 0 THEN
        DBMS_OUTPUT.PUT_LINE(RPAD(r.table_name, 22) || TO_CHAR(v_cant));
      END IF;
    EXCEPTION WHEN OTHERS THEN
      DBMS_OUTPUT.PUT_LINE(RPAD(r.table_name, 22) || 'ERROR: ' || SQLERRM);
    END;
  END LOOP;
END;
/

PROMPT [3.1] Tablas T_* VACIAS (no aportan nada al sobre)
DECLARE
  v_cant NUMBER;
  v_vacias PLS_INTEGER := 0;
  v_total  PLS_INTEGER := 0;
BEGIN
  FOR r IN (SELECT table_name
              FROM all_tables
             WHERE owner = 'TEMP' AND table_name LIKE 'T!_%' ESCAPE '!'
             ORDER BY table_name) LOOP
    v_total := v_total + 1;
    BEGIN
      EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM TEMP.' || r.table_name INTO v_cant;
      IF v_cant = 0 THEN v_vacias := v_vacias + 1; END IF;
    EXCEPTION WHEN OTHERS THEN NULL;
    END;
  END LOOP;
  DBMS_OUTPUT.PUT_LINE('T_ totales: ' || v_total || '   vacias: ' || v_vacias);
END;
/

PROMPT
PROMPT ====================================================================
PROMPT [4] TEMP.T_EVENTOS : la ventana que viajaria en el proximo sobre
PROMPT ====================================================================
SELECT COUNT(*) AS TOTAL,
       TO_CHAR(MIN(FECHA),'YYYY-MM-DD HH24:MI') AS MIN_FECHA,
       TO_CHAR(MAX(FECHA),'YYYY-MM-DD HH24:MI') AS MAX_FECHA
  FROM TEMP.T_EVENTOS;

PROMPT [4.1] T_EVENTOS por dia y evento
SELECT TO_CHAR(TRUNC(FECHA),'YYYY-MM-DD') AS DIA, EVENTO, COUNT(*) AS CANT
  FROM TEMP.T_EVENTOS
 WHERE FECHA >= TRUNC(SYSDATE) - 60
 GROUP BY TRUNC(FECHA), EVENTO
 ORDER BY 1 DESC, 2;

PROMPT
PROMPT ====================================================================
PROMPT [5] EL MOTOR DE REPLICACION: existe? VALIDO? (16 objetos de
PROMPT     SISMAI estaban INVALIDOS el 18/09/2026)
PROMPT ====================================================================
SELECT owner, object_type, object_name, status,
       TO_CHAR(last_ddl_time,'YYYY-MM-DD HH24:MI') AS ultimo_ddl
  FROM ALL_OBJECTS
 WHERE (UPPER(object_name) LIKE '%SINC%'
     OR UPPER(object_name) LIKE '%REPLI%'
     OR UPPER(object_name) LIKE '%PLCER%'
     OR UPPER(object_name) LIKE '%TRANSF%'
     OR UPPER(object_name) LIKE '%RUT%')
   AND owner IN ('SISMAI','TEMP','HISTORICO','INBDLAR1')
 ORDER BY owner, object_type, object_name;

PROMPT [5.1] Objetos INVALIDOS de SISMAI (si uno es del motor, `repl` falla)
SELECT object_type, object_name, status,
       TO_CHAR(last_ddl_time,'YYYY-MM-DD HH24:MI') AS ultimo_ddl
  FROM ALL_OBJECTS
 WHERE owner = 'SISMAI' AND status = 'INVALID'
 ORDER BY object_type, object_name;

PROMPT [5.2] Errores de compilacion (requiere permiso DBA sobre ALL_ERRORS)
DECLARE
  v_cant NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_cant FROM ALL_ERRORS;
  DBMS_OUTPUT.PUT_LINE('ALL_ERRORS accesible (' || v_cant || ' filas).');
EXCEPTION WHEN OTHERS THEN
  DBMS_OUTPUT.PUT_LINE('ALL_ERRORS sin permiso: ' || SQLERRM);
  DBMS_OUTPUT.PUT_LINE('Repita como DBA: sqlplus oracle/oracle@lar1 @recon_repllar1.sql');
END;
/
DECLARE
  v_txt VARCHAR2(300);
BEGIN
  FOR r IN (SELECT owner, name, type, line, position, text
              FROM ALL_ERRORS
             WHERE owner = 'SISMAI'
               AND (UPPER(name) LIKE '%SINC%' OR UPPER(name) LIKE '%REPLI%'
                 OR UPPER(name) LIKE '%PLCER%' OR UPPER(name) LIKE '%TRANSF%')) LOOP
    DBMS_OUTPUT.PUT_LINE(r.owner || '.' || r.name || ' (' || r.type || ') linea ' || r.line);
  END LOOP;
EXCEPTION WHEN OTHERS THEN
  DBMS_OUTPUT.PUT_LINE('No se pudieron leer los errores: ' || SQLERRM);
END;
/

PROMPT
PROMPT ====================================================================
PROMPT [6] ESTRUCTURA QUE CREA LA FASE `repl` (TEMP.T_EVENTOS)
PROMPT ====================================================================
DECLARE
  v_ddl CLOB;
  v_pos PLS_INTEGER := 1;
  v_txt VARCHAR2(8000);
BEGIN
  EXECUTE IMMEDIATE
    'SELECT DBMS_METADATA.GET_DDL(''TABLE'',''T_EVENTOS'',''TEMP'') FROM DUAL'
    INTO v_ddl;
  DBMS_OUTPUT.PUT_LINE('-- longitud: ' || DBMS_LOB.GETLENGTH(v_ddl) || ' bytes');
  WHILE v_pos <= DBMS_LOB.GETLENGTH(v_ddl) LOOP
    v_txt := DBMS_LOB.SUBSTR(v_ddl, 8000, v_pos);
    EXIT WHEN v_txt IS NULL;
    DBMS_OUTPUT.PUT_LINE(v_txt);
    v_pos := v_pos + 8000;
  END LOOP;
EXCEPTION WHEN OTHERS THEN
  DBMS_OUTPUT.PUT_LINE('No se pudo obtener el DDL: ' || SQLERRM);
END;
/

PROMPT
PROMPT ====================================================================
PROMPT [7] Programacion de la base (job_queue_processes = 0, sin jobs)
PROMPT ====================================================================
DECLARE
  v_txt VARCHAR2(32767);
  v_cnt NUMBER;
  c     SYS_REFCURSOR;
BEGIN
  EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM ALL_JOBS' INTO v_cnt;
  DBMS_OUTPUT.PUT_LINE('ALL_JOBS visibles: ' || v_cnt);
  OPEN c FOR 'SELECT owner || '' | '' || job_name FROM ALL_JOBS ORDER BY 1';
  LOOP
    FETCH c INTO v_txt;
    EXIT WHEN v_txt IS NULL;
    DBMS_OUTPUT.PUT_LINE('  ' || v_txt);
  END LOOP;
  CLOSE c;
EXCEPTION WHEN OTHERS THEN
  DBMS_OUTPUT.PUT_LINE('Detalle de ALL_JOBS no disponible: ' || SUBSTR(SQLERRM,1,200));
END;
/

PROMPT
PROMPT ====================================================================
PROMPT [8] QUIEN PUEDE CORRER LA REPLICACION (privilegios sobre TEMP)
PROMPT ====================================================================
SELECT grantee, privilege, COUNT(*) AS OBJETOS
  FROM ALL_TAB_PRIVS
 WHERE table_schema = 'TEMP' AND table_name = 'T_EVENTOS'
 GROUP BY grantee, privilege
 ORDER BY 1, 2;

PROMPT [8.1] Roles de los usuarios de aplicacion (¿alguno con DBA, como SISMAI/TEMP?)
PROMPT      (requiere DBA: con usuario `respaldo` saldra ORA-00942, es esperado)
SELECT granted_role, grantee, default_role
  FROM DBA_ROLE_GRANTS
 WHERE grantee IN ('SISMAI','TEMP','HISTORICO','RESPALDO','INBDLAR1')
 ORDER BY grantee, granted_role;

PROMPT
PROMPT ====================================================================
PROMPT [9] VEREDICTO DE ORIENTACION
PROMPT ====================================================================
SELECT CASE
         WHEN (SELECT COUNT(*) FROM SISMAI.EVENTOS_SINC) = 0
           THEN 'OK-1  COLA VACIA: la replicacion consumio todo'
         WHEN (SELECT MAX(last_ddl_time) FROM ALL_OBJECTS
             WHERE OWNER='TEMP' AND OBJECT_TYPE='TABLE')
              > SYSDATE - 8
           THEN 'OK-2  TEMP.T_* recreadas esta semana: `repl` CORRIO'
         WHEN (SELECT MAX(last_ddl_time) FROM ALL_OBJECTS
             WHERE OWNER='TEMP' AND OBJECT_TYPE='TABLE')
              > SYSDATE - 40
           THEN 'PAR-3 `repl` corrio, pero no en la ultima corrida'
         ELSE 'MAL-4 `repl` NO corre desde hace mas de 40 dias'
       END AS VEREDICTO_FASE_REPL
  FROM DUAL;

PROMPT
PROMPT Cruce con el ultimo sobre recibido:
PROMPT   - Si [2] dice que TEMP.T_* no se recrean => la fase `repl` no corre:
PROMPT     encolar natalidad el lunes NO haria que nada viaje el martes.
PROMPT   - Si [3] muestra mas filas que `routlar1.log` => algo lleno TEMP
PROMPT     despues del ultimo export (o sea, el export no es el unico
PROMPT     que escribe en TEMP).
PROMPT ====================================================================
EXIT
