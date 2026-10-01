-- ====================================================================
-- RECOMPILAR LOS 16 OBJETOS INVALIDOS DE LA APP (SISMAI) — 30/09/2026
-- --------------------------------------------------------------------
-- Alcance AUTORIZADO: SOLO estos 16 objetos de la aplicacion (informe
-- 5.3 / PENDIENTES §22.1):
--   11 vistas:         C_INFORMES, C_INFORMES1, NATALIDAD, V_REGISTROCIRUGIA,
--                      V_FICHAEPI13, C_ESTABLECIMIENTO, V_ESTABLE_DIREC,
--                      V_ORG_SANITARIA, V_PACIENTEVACUNACION, V_PACIENTECIRUGIA,
--                      H_DEPEN
--   4 procedimientos:  SPDOC, SPREGDSP, SPREGEPI, SPREGTEL
--   1 funcion:         FIDPADRE
-- NO se usa DBMS_UTILITY.COMPILE_SCHEMA (recompilaria todo el esquema)
-- y NO se toca la cola SISMAI.EVENTOS_SINC.
-- --------------------------------------------------------------------
-- Pre-requisito (§22.3): si TEMP.T_CERTNACI NO existe (su CREATE fallo),
-- hay que crearla ANTES: NATALIDAD depende de ella y sin la tabla la
-- vista no puede recompilar. El DDL del share `crear.sql` NO se usa
-- porque hace DROP+CREATE de EVENTOS_SINC.
-- --------------------------------------------------------------------
-- Uso:  sqlplus / as sysdba @recompilar_16_objetos.sql
--       o con el runner por SSH: ./migracion/recompilar_16_live.sh
-- ====================================================================

SET PAGESIZE 200
SET LINESIZE 220
SET LONG 200
SET FEEDBACK ON
SET SERVEROUTPUT ON SIZE 1000000
SET NULL (null)
WHENEVER SQLERROR CONTINUE

PROMPT ====================================================================
PROMPT [0] Contexto de la sesion y hora del servidor
PROMPT ====================================================================
SELECT banner FROM v$version WHERE ROWNUM = 1;
SELECT TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS') AS HORA_SERVIDOR,
       SYS_CONTEXT('USERENV','SESSION_USER') AS USUARIO
  FROM DUAL;

PROMPT
PROMPT ====================================================================
PROMPT [1] PRE-CONDICION: TEMP.T_CERTNACI (la necesita NATALIDAD)
PROMPT --------------------------------------------------------------------
PROMPT §22.1: el 29/09 T_CERTNACI no existia (el CREATE de natalidad corrio
PROMPT a medias). Si no aparece en el listado, CREARLA ANTES; sin ella
PROMPT NATALIDAD recompila pero queda invalida por dependencia.
PROMPT ====================================================================
SELECT OBJECT_NAME, OBJECT_TYPE, STATUS,
       TO_CHAR(LAST_DDL_TIME,'YYYY-MM-DD HH24:MI:SS') AS MODIFICADA
  FROM ALL_OBJECTS
 WHERE OWNER = 'TEMP'
   AND OBJECT_NAME IN ('T_CERTNACI','T_MADRNACI','T_RNACNACI','T_RNACANUL',
                       'T_CERTMORT','T_EVENTOS')
 ORDER BY OBJECT_NAME;

PROMPT
PROMPT ====================================================================
PROMPT [2] INVALIDOS ANTES (referencia: 16 en SISMAI, numero no impresion)
PROMPT ====================================================================
SELECT OBJECT_TYPE, OBJECT_NAME, STATUS,
       COUNT(*) OVER () AS TOTAL_INVALIDOS
  FROM ALL_OBJECTS
 WHERE OWNER IN ('SISMAI','TEMP') AND STATUS = 'INVALID'
 ORDER BY OWNER, OBJECT_TYPE, OBJECT_NAME;

PROMPT
PROMPT ====================================================================
PROMPT [3] CONTRASTE: cuantos de los 16 autorizados existen hoy en SISMAI
PROMPT ====================================================================
SELECT OBJECT_TYPE, OBJECT_NAME, STATUS
  FROM ALL_OBJECTS
 WHERE OWNER = 'SISMAI'
   AND OBJECT_NAME IN ('C_INFORMES','C_INFORMES1','NATALIDAD',
                       'V_REGISTROCIRUGIA','V_FICHAEPI13','C_ESTABLECIMIENTO',
                       'V_ESTABLE_DIREC','V_ORG_SANITARIA','V_PACIENTEVACUNACION',
                       'V_PACIENTECIRUGIA','H_DEPEN',
                       'SPDOC','SPREGDSP','SPREGEPI','SPREGTEL','FIDPADRE')
 ORDER BY OBJECT_TYPE, OBJECT_NAME;
PROMPT (Deben salir 16. Los que falten: o no se crearon o estan en otro
PROMPT  esquema; se compilan solo los existentes y se avisa por cada uno.)

PROMPT
PROMPT ====================================================================
PROMPT [4] RECOMPILAR LOS 16 (ALTER ... COMPILE, objeto por objeto)
PROMPT --------------------------------------------------------------------
PROMPT Autorizacion explicita del usuario (30/09/2026, PENDIENTES §22.3):
PROMPT alcanza SOLO a estos 16 objetos de aplicacion. No se toca nada mas.
PROMPT ====================================================================
DECLARE
  TYPE t_objeto IS RECORD (tipo  VARCHAR2(30), nombre VARCHAR2(60));
  TYPE t_lista IS TABLE OF t_objeto;
  v_lista t_lista := t_lista(
    t_objeto('VIEW','C_INFORMES'),
    t_objeto('VIEW','C_INFORMES1'),
    t_objeto('VIEW','NATALIDAD'),
    t_objeto('VIEW','V_REGISTROCIRUGIA'),
    t_objeto('VIEW','V_FICHAEPI13'),
    t_objeto('VIEW','C_ESTABLECIMIENTO'),
    t_objeto('VIEW','V_ESTABLE_DIREC'),
    t_objeto('VIEW','V_ORG_SANITARIA'),
    t_objeto('VIEW','V_PACIENTEVACUNACION'),
    t_objeto('VIEW','V_PACIENTECIRUGIA'),
    t_objeto('VIEW','H_DEPEN'),
    t_objeto('PROCEDURE','SPDOC'),
    t_objeto('PROCEDURE','SPREGDSP'),
    t_objeto('PROCEDURE','SPREGEPI'),
    t_objeto('PROCEDURE','SPREGTEL'),
    t_objeto('FUNCTION','FIDPADRE')
  );
  v_existe NUMBER;
  v_recs   NUMBER := 0;
  v_ok     NUMBER := 0;
  v_fallos NUMBER := 0;
BEGIN
  FOR i IN 1..v_lista.COUNT LOOP
    SELECT COUNT(*) INTO v_existe
      FROM ALL_OBJECTS
     WHERE OWNER='SISMAI'
       AND OBJECT_NAME = v_lista(i).nombre
       AND OBJECT_TYPE = v_lista(i).tipo;
    IF v_existe = 0 THEN
      DBMS_OUTPUT.PUT_LINE('  NO EXISTE, se omite: '||v_lista(i).tipo||' SISMAI.'||v_lista(i).nombre);
      v_fallos := v_fallos + 1;
    ELSE
      v_recs := v_recs + 1;
      BEGIN
        EXECUTE IMMEDIATE 'ALTER '||v_lista(i).tipo||' SISMAI.'||v_lista(i).nombre||' COMPILE';
        DBMS_OUTPUT.PUT_LINE('  RECOMPILADO: '||v_lista(i).tipo||' SISMAI.'||v_lista(i).nombre);
        v_ok := v_ok + 1;
      EXCEPTION
        -- Un ALTER que falla (p. ej. NATALIDAD sin T_CERTNACI) NO aborta
        -- el resto: se anota la causa y se sigue con los otros 15.
        WHEN OTHERS THEN
          DBMS_OUTPUT.PUT_LINE('  [FALLO] '||v_lista(i).tipo||' SISMAI.'||v_lista(i).nombre
            || ': '||SQLERRM);
          v_fallos := v_fallos + 1;
      END;
    END IF;
  END LOOP;
  DBMS_OUTPUT.PUT_LINE('Recompilados '||v_ok||' de '||v_recs
    ||' existentes ('||v_fallos||' omitidos/fallidos de 16).');
END;
/

PROMPT
PROMPT ====================================================================
PROMPT [5] INVALIDOS DESPUES (ideal: 0; eso es el veredicto, no una frase)
PROMPT ====================================================================
SELECT OBJECT_TYPE, OBJECT_NAME, STATUS,
       COUNT(*) OVER () AS TOTAL_INVALIDOS
  FROM ALL_OBJECTS
 WHERE OWNER IN ('SISMAI','TEMP') AND STATUS = 'INVALID'
 ORDER BY OWNER, OBJECT_TYPE, OBJECT_NAME;

PROMPT
PROMPT --------------------------------------------------------------------
PROMPT Los 16 autorizados, con su estado final:
SELECT OBJECT_TYPE, OBJECT_NAME, STATUS
  FROM ALL_OBJECTS
 WHERE OWNER = 'SISMAI'
   AND OBJECT_NAME IN ('C_INFORMES','C_INFORMES1','NATALIDAD',
                       'V_REGISTROCIRUGIA','V_FICHAEPI13','C_ESTABLECIMIENTO',
                       'V_ESTABLE_DIREC','V_ORG_SANITARIA','V_PACIENTEVACUNACION',
                       'V_PACIENTECIRUGIA','H_DEPEN',
                       'SPDOC','SPREGDSP','SPREGEPI','SPREGTEL','FIDPADRE')
 ORDER BY OBJECT_TYPE, OBJECT_NAME;

PROMPT
PROMPT ====================================================================
PROMPT [6] ERRORES DE LOS QUE SIGAN INVALIDOS (ALL_ERRORS, para el DBA)
PROMPT ====================================================================
SELECT NAME, TYPE, TO_CHAR(ATTRIBUTE) AS QUE, LINE, POSITION, TEXT
  FROM ALL_ERRORS
 WHERE OWNER = 'SISMAI' AND NAME IN ('C_INFORMES','C_INFORMES1','NATALIDAD',
                       'V_REGISTROCIRUGIA','V_FICHAEPI13','C_ESTABLECIMIENTO',
                       'V_ESTABLE_DIREC','V_ORG_SANITARIA','V_PACIENTEVACUNACION',
                       'V_PACIENTECIRUGIA','H_DEPEN',
                       'SPDOC','SPREGDSP','SPREGEPI','SPREGTEL','FIDPADRE')
 ORDER BY NAME, LINE;

PROMPT
PROMPT ====================================================================
PROMPT FIN. Si NATALIDAD sigue invalida y T_CERTNACI no existia en [1],
PROMPT crear primero TEMP.T_CERTNACI y volver a correr este script.
PROMPT ====================================================================
EXIT