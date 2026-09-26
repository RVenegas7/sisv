-- ============================================================================
--  01_preparar_escenario.sql
--  SISV — Simulación del paquete semanal: arma el escenario de prueba en el
--  espejo Oracle local a partir de la REFERENCIA (el paquete real del
--  04/08/2026, que está en el esquema IMPORT29 del espejo).
--
--  Qué hace y por qué
--  ------------------
--  El plan B (migracion/replicar_controlado.sql) lee de SISMAI.<origen> y de
--  SISMAI.EVENTOS_SINC, y escribe en TEMP.T_*. El espejo no tiene el esquema
--  SISMAI (los fuentes no están en BDSISMAI.DMP con ese nombre), así que aquí
--  se REConstruye un escenario equivalente a partir de la referencia:
--
--    SISMAI.EVENTOS_SINC  <-  IMPORT29.T_EVENTOS
--        La cola tal como la vio la fase original: el manifiesto del paquete
--        del 04/08 (9.862 eventos, 23 TABLA) es exactamente el subconjunto de
--        la cola que produjo ese envío.
--
--    SISMAI.<ORIGEN>      <-  IMPORT29.T_<DESTINO>
--        Las tablas fuente con la misma estructura y el mismo contenido que su
--        tabla destino. NO es la fuente real: es una proyección. Por eso esta
--        simulación prueba la LÓGICA (filtro del último evento, intersección de
--        columnas, idempotencia, manifiesto), NO la transformación real
--        origen -> T_* ni las ~60 tablas que no están en el mapeo.
--
--    TEMP.T_*             <-  00_ddl_temp_04082026.sql, VACÍAS
--        La estructura REAL de las 83 tablas, tal como las creó la fase (83
--        CREATE TABLE + 86 CREATE INDEX). Se dejan vacías porque eso es lo que
--        hace la fase: crear y luego llenar.
--
--  Resultado esperado: tras correr replicar_controlado.sql, TEMP.T_* debe
--  quedar igual a IMPORT29.T_* (comparar con 02_comparar.sql).
-- ============================================================================

SET SERVEROUTPUT ON SIZE UNLIMITED
SET PAGESIZE 200
SET LINESIZE 200
SET FEEDBACK OFF
WHENEVER SQLERROR EXIT SQL.SQLCODE

DECLARE
  V_JOBS   PLS_INTEGER := 0;
  V_TABLA  VARCHAR2(30);
  V_ORIGEN VARCHAR2(30);
  V_DEST   VARCHAR2(30);
  V_N      PLS_INTEGER;
BEGIN
  ------------------------------------------------------------------
  -- 0. Limpieza total del escenario (idempotente)
  ------------------------------------------------------------------
  FOR r IN (SELECT USERNAME FROM ALL_USERS WHERE USERNAME IN ('TEMP', 'SISMAI')) LOOP
    EXECUTE IMMEDIATE 'DROP USER ' || r.USERNAME || ' CASCADE';
  END LOOP;
  DBMS_OUTPUT.PUT_LINE('0. escenarios anteriores eliminados');

  ------------------------------------------------------------------
  -- 1. Esquema de la cola y las fuentes
  ------------------------------------------------------------------
  EXECUTE IMMEDIATE 'CREATE USER SISMAI IDENTIFIED BY SISMAI'
                    || ' QUOTA UNLIMITED ON SYSTEM QUOTA UNLIMITED ON USERS';
  EXECUTE IMMEDIATE 'GRANT CREATE SESSION TO SISMAI';

  EXECUTE IMMEDIATE
    'CREATE TABLE SISMAI.EVENTOS_SINC AS SELECT * FROM IMPORT29.T_EVENTOS';
  V_N := 0; EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM SISMAI.EVENTOS_SINC' INTO V_N;
  DBMS_OUTPUT.PUT_LINE('1. SISMAI.EVENTOS_SINC: ' || V_N || ' eventos (copia de la referencia)');

  ------------------------------------------------------------------
  -- 2. Las 23 tablas fuente, derivadas de su tabla destino
  --    ('ORIGEN|DESTINO' = el mismo mapa de replicar_controlado.sql)
  ------------------------------------------------------------------
  FOR r IN (
    SELECT COLUMN_VALUE AS PAR FROM TABLE(
      SYS.ODCIVARCHAR2LIST(
        'CERTIFICADO|CERTMORT','CERTNACIMIENTO|CERTNACI','DOCUMENTO|DOCUMENT',
        'CAUSA_M|MORTCAUS','CAUSA_MMEDICO|CAUMMEDI','CAUSA_MORBOSAS|MCAUMORB',
        'CASOSMM|CASOSMM','CASOS_MMI|CASOSMMI','RENGLON_CASOSMI|RCASOSMI',
        'RENGLON_EPI15|RENEPI15','RENGLON_RESUMEN|RENGRES','RENGLONTELE|RENGTELE',
        'RESUMEN|RESUMEN','NAC_MADRE|MADRNACI','NAC_RNACIDO|RNACNACI',
        'NAC_ANULADOS|RNACANUL','MOR_ANULADOS|MORTANUL','M_FETAL|MORTFETA',
        'M_MADRE|MORTMADR','M_VIOLENTA|MORTVIOL','MONITOR_BASEDEDATOS|MBASED',
        'MONITOR_RESPALDO|MRESPA','USUARIOS|USUARIOS'))
  ) LOOP
    V_ORIGEN := SUBSTR(r.PAR, 1, INSTR(r.PAR, '|') - 1);
    V_DEST   := SUBSTR(r.PAR, INSTR(r.PAR, '|') + 1);
    V_TABLA  := 'T_' || V_DEST;
    EXECUTE IMMEDIATE 'CREATE TABLE SISMAI."' || V_ORIGEN || '" AS '
                    || 'SELECT * FROM IMPORT29."' || V_TABLA || '" WHERE 1=0';
    EXECUTE IMMEDIATE 'INSERT INTO SISMAI."' || V_ORIGEN || '" '
                    || 'SELECT * FROM IMPORT29."' || V_TABLA || '"';
    V_JOBS := V_JOBS + 1;
  END LOOP;
  DBMS_OUTPUT.PUT_LINE('2. ' || V_JOBS || ' tablas fuente SISMAI.* creadas desde la referencia');

  ------------------------------------------------------------------
  -- 3. Comprobaciones del escenario
  ------------------------------------------------------------------
  EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM ALL_TABLES WHERE OWNER=''IMPORT29'''
        || ' AND TABLE_NAME LIKE ''T!_%'' ESCAPE ''!''' INTO V_N;
  DBMS_OUTPUT.PUT_LINE('3. la referencia tiene ' || V_N || ' tablas T_*');
  EXECUTE IMMEDIATE 'SELECT COUNT(DISTINCT TABLA) FROM SISMAI.EVENTOS_SINC' INTO V_N;
  DBMS_OUTPUT.PUT_LINE('   la cola tiene ' || V_N || ' TABLA distintas');
EXCEPTION WHEN OTHERS THEN
  DBMS_OUTPUT.PUT_LINE('ERROR preparando el escenario: ' || SQLERRM);
  RAISE;
END;
/

PROMPT --- escenario listo: falta aplicar 00_ddl_temp_04082026.sql (crea TEMP.T_* vacias)
EXIT
