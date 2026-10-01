-- ====================================================================
-- DIAGNOSTICO DE `T_CERTNACI` (SOLO LECTURA) — 30/09/2026
-- --------------------------------------------------------------------
-- Que se responde con este archivo:
--   [1] Si TEMP.T_CERTNACI existe en el servidor. El sobre del 29/09
--       la exporto con 82 tablas y T_CERTNACI NO estaba entre ellas
--       (el 04/08 tenia 422 filas), mientras que T_MADRNACI (312) y
--       T_RNACNACI (312) si. O sea: al nivel central le llegaron partos
--       sin los certificados de nacimiento.
--   [2] Cuando desaparecio: LAST_DDL_TIME de cada T_ de natalidad. Si
--       T_CERTNACI es anterior a T_MADRNACI/T_RNACNACI, se borro sola
--       en una corrida y nadie lo volvio a crear; si es mas reciente,
--       se creo vacia.
--   [3] Si hay eventos de CERTNACIMIENTO en la cola: sin ellos el
--       `CREATE TABLE ... AS SELECT` de cr_repli_nata.sql:1-9 no puede
--       traer filas, pero si deberia crear la tabla. Que la tabla NO
--       exista apunta a que el script fallo ANTES de esa linea, no a que
--       la cola este vacia.
--   [4] El error concreto: se busca en la cola de errores que el propio
--       motor deja (HISTORICO.ERRORES_SINC, que crea SincFich/crear.sql)
--       y en el log del cliente si esta montado.
--   [5] Cuantos certificados hay en el origen, para saber que se
--       esta dejando de enviar y desde cuando.
-- --------------------------------------------------------------------
-- Uso: sqlplus respaldo/respaldo@lar1 @diagnostico_certnaci.sql
--       (o con el usuario DBA `oracle` para ver tambien ALL_ERRORS)
-- NO contiene DDL ni DML: unicamente SELECT y consultas de diccionario.
-- ====================================================================

SET PAGESIZE 300
SET LINESIZE 220
SET LONG 20000
SET FEEDBACK ON
SET SERVEROUTPUT ON
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
PROMPT [1] ¿EXISTEN LAS TABLAS DE NATALIDAD EN TEMP?
PROMPT Es el dato crudo del problema: el 29/09 falto T_CERTNACI.
PROMPT ====================================================================
SELECT OBJECT_NAME, OBJECT_TYPE,
       TO_CHAR(CREATED ,'YYYY-MM-DD HH24:MI:SS') AS CREADA,
       TO_CHAR(LAST_DDL_TIME,'YYYY-MM-DD HH24:MI:SS') AS MODIFICADA
  FROM ALL_OBJECTS
 WHERE OWNER = 'TEMP'
   AND OBJECT_NAME IN ('T_CERTNACI','T_MADRNACI','T_RNACNACI','T_RNACANUL',
                       'T_CERTMORT','T_CAUMMEDI','T_EVENTOS')
 ORDER BY OBJECT_NAME;

PROMPT
PROMPT --- Las que NO salen arriba son las que no existen. Para saber el
PROMPT --- ultimo instante en que existio cada una hay que mirar el recycle
PROMPT --- bin o el log del cliente; aqui se listan TODAS las T_ de TEMP
PROMPT --- con su fecha, que es la foto del estado real de la replicacion.
SELECT * FROM (
  SELECT OBJECT_NAME,
         TO_CHAR(LAST_DDL_TIME,'YYYY-MM-DD HH24:MI:SS') AS MODIFICADA
    FROM ALL_OBJECTS
   WHERE OWNER = 'TEMP' AND OBJECT_TYPE = 'TABLE'
   ORDER BY LAST_DDL_TIME DESC NULLS LAST
) WHERE ROWNUM <= 40;

PROMPT
PROMPT ====================================================================
PROMPT [2] CONTEO REAL DE CADA T_ DE NATALIDAD
PROMPT Si T_CERTNACI no existe, saltarla: dara ORA-00942 y el resto sigue.
PROMPT ====================================================================
SELECT 'T_CERTNACI' AS TABLA, COUNT(*) AS FILAS FROM TEMP.T_CERTNACI;
SELECT 'T_MADRNACI' AS TABLA, COUNT(*) AS FILAS FROM TEMP.T_MADRNACI;
SELECT 'T_RNACNACI' AS TABLA, COUNT(*) AS FILAS FROM TEMP.T_RNACNACI;

PROMPT
PROMPT ====================================================================
PROMPT [3] LA COLA: ¿hay eventos de CERTNACIMIENTO que replicar?
PROMPT cr_repli_nata.sql:12-15 arma T_CERTNACI con
PROMPT   FROM SISMAI.CERTNACIMIENTO A, SISMAI.EVENTOS_SINC B
PROMPT   WHERE B.TABLA='CERTNACIMIENTO' AND B.ID=A.ID
PROMPT Si hay eventos pero la tabla no existe, el fallo fue del script.
PROMPT ====================================================================
SELECT TABLA, EVENTO, COUNT(*) AS FILAS,
       TO_CHAR(MIN(FECHA),'YYYY-MM-DD HH24:MI') AS FECHA_MIN,
       TO_CHAR(MAX(FECHA),'YYYY-MM-DD HH24:MI') AS FECHA_MAX
  FROM SISMAI.EVENTOS_SINC
 GROUP BY TABLA, EVENTO
 ORDER BY TABLA, EVENTO;

PROMPT
PROMPT ====================================================================
PROMPT [4] ERRORES QUE DEJO EL MOTOR (HISTORICO.ERRORES_SINC)
PROMPT La crea SincFich/crear.sql:24-31. Ahi queda el ORA- de cada
PROMPT sentencia que fallo, que es la respuesta directa a por que no
PROMPT se creo T_CERTNACI.
PROMPT ====================================================================
SELECT ID, TABLA, ESQUEMA,
       TO_CHAR(FECHA,'YYYY-MM-DD HH24:MI:SS') AS FECHA,
       SQLCODIGO, SQLERROR, EVENTO
  FROM HISTORICO.ERRORES_SINC
 WHERE FECHA >= ADD_MONTHS(SYSDATE, -3)
   AND ROWNUM <= 50
 ORDER BY FECHA DESC;

PROMPT
PROMPT ====================================================================
PROMPT [5] EL ORIGEN: ¿cuantos certificados de nacimiento hay?
PROMPT Sirve para saber que se esta dejando de enviar y desde cuando.
PROMPT ====================================================================
SELECT COUNT(*) AS CERTNACIMIENTO_TOTAL,
       TO_CHAR(MIN(FECHACERTIFICADO),'YYYY-MM-DD') AS DESDE,
       TO_CHAR(MAX(FECHACERTIFICADO),'YYYY-MM-DD') AS HASTA
  FROM SISMAI.CERTNACIMIENTO;

PROMPT
PROMPT --- Los del anio en curso, que es lo que debe estar viajando.
SELECT ANO_CERTIF, COUNT(*) AS FILAS,
       TO_CHAR(MIN(FECHACERTIFICADO),'YYYY-MM-DD') AS DESDE,
       TO_CHAR(MAX(FECHACERTIFICADO),'YYYY-MM-DD') AS HASTA
  FROM SISMAI.CERTNACIMIENTO
 WHERE ANO_CERTIF >= 2026
 GROUP BY ANO_CERTIF
 ORDER BY ANO_CERTIF;

PROMPT
PROMPT ====================================================================
PROMPT [6] ¿QUE CUENTA CORRE LA REPLICACION?
PROMPT Si el `exp` lo hace el usuario de aplicacion, el mismo usuario
PROMPT tendria que poder leer SISMAI.EVENTOS_SINC y escribir en TEMP.
PROMPT ====================================================================
SELECT GRANTEE, TABLE_SCHEMA, TABLE_NAME, PRIVILEGE
  FROM ALL_TAB_PRIVS
 WHERE TABLE_SCHEMA IN ('TEMP','SISMAI')
   AND TABLE_NAME IN ('T_CERTNACI','T_MADRNACI','T_CERTMORT','EVENTOS_SINC')
 ORDER BY TABLE_SCHEMA, TABLE_NAME, GRANTEE;

PROMPT
PROMPT ====================================================================
PROMPT FIN. No se ejecuto ninguna escritura: solo SELECT.
PROMPT ====================================================================
EXIT;
