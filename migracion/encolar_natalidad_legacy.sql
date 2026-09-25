-- ============================================================================
--  encolar_natalidad_legacy.sql
--  SISV / SAPS Lara — reencolado de natalidad hacia SISMAI.EVENTOS_SINC
--  Fecha: 2026-09-25
--
--  PROBLEMA QUE RESUELVE
--  Los scripts originales (SincFich/nata/plcna1.sql, plnma1.sql, plnrn1.sql,
--  plnan1.sql) fallan en la sincronizacion de natalidad por cuatro defectos,
--  todos verificados sobre produccion el 2026-09-25:
--
--    1) No tienen guarda de duplicados. SISMAI.EVENTOS_SINC no tiene NINGUNA
--       restriccion ni indice (USER_CONSTRAINTS y USER_INDEXES vacios para esa
--       tabla), asi que reejecutarlos inserta duplicados sin ninguna advertencia.
--       El 25/09 la cola tenia 16.741 filas de REG_VACUNACION,
--       PACIENTE_FICHA_EPI y PACIENTE_COND_ESPE y 0 duplicados, pero nada
--       impide que una segunda corrida duplique 1.295.152 filas.
--
--    2) V_I NUMBER(3) no se inicializa, por lo que el IF V_I = 500 nunca se
--       cumple: los ~1,3 M de filas quedan en una sola transaccion, con todo el
--       undo/redo hasta el final y sin posibilidad de reanudar.
--
--    3) plcna1.sql hace V_I := V_I + 1 dos veces por iteracion, con lo que
--       confirma cada 250 filas en vez de 500.
--
--    4) El patron "EXCEPTION WHEN OTHERS ... GOTO M_MODIFICA" reintenta en
--       bucle infinito la misma fila que acaba de fallar.
--
--  NOTA DE RENDIMIENTO (medido, no estimado)
--  La primera version de este script deduplicaba con NOT EXISTS correlacionado
--  dentro del cursor. Como EVENTOS_SINC no tiene indice, eso es un escaneo
--  completo por cada candidato: 429.577 candidatos contra 429.500 filas tardo mas
--  de 10 minutos solo en el conteo. Aqui la deduplicacion se hace con MINUS
--  (una sola operacion de conjuntos, O(n log n)) tanto en los cursores como en
--  los conteos, de modo que el numero reportado y el numero insertado salen
--  del mismo predicado y no pueden discrepar.
--
--  RITMO MEDIDO
--  En la prueba sobre una tabla de prueba en el esquema del usuario de solo
--  lectura: 429.500 filas de CERTNACIMIENTO en ~15 minutos (~480 filas/s con
--  confirmacion cada 500). El lote completo de 1.295.152 filas es del orden de
--  45 minutos. Se debe ejecutar en ventana de mantenimiento y con la cola
--  respaldada, nunca junto a SincFich/crear.sql.
--
--  ALCANCE (calculado sobre produccion el 2026-09-25, solo lectura)
--    plcna1  CERTNACIMIENTO  429.577
--    plnma1  NAC_MADRE       429.594
--    plnrn1  NAC_RNACIDO     429.583
--    plnan1  NAC_ANULADOS      6.398
--    TOTAL                  1.295.152
--  Nota: hay 320 certificados con ANO_CERTIF >= 2010 que no tienen madre o no
--  tienen recien nacido, por lo que el criterio original de plcna1 no los
--  envia. No se tocan aqui: puede ser intencional (certificados incompletos o
--  anulados) y su correccion es una decision funcional, no de sincronizacion.
--
--  USO
--    1) Guardar la salida del dry-run (V_EJECUTAR = 0) como evidencia.
--    2) Verificar que la cola actual este respaldada:
--         respaldo_20260925/eventos_sinc_20260925.csv
--         SHA-256 3ac3a054055da3f8006cb21c02937ff744dd7200e3f2ce53ed7d6d144c7aad51
--       16.741 filas, volcado del 2026-09-25.
--    3) Confirmar por escrito la recepcion central de los ZIP sincdoc y
--       sincnata del 2026-09-21 (3.391.421 eventos) para no repetir un lote
--       ya entregado.
--    4) Poner V_EJECUTAR := 1 y ejecutar con el usuario de aplicacion de SISMAI.
--
--  MODO SEGURO POR DEFECTO
--  V_EJECUTAR = 0 solo hace SELECT: no inserta, no confirma y no modifica nada.
--  V_EJECUTAR = 1 hace INSERT con confirmacion cada 5.000 filas.
--
--  REQUISITOS Y RIESGOS
--    - El usuario ejecutor necesita SELECT e INSERT sobre SISMAI.EVENTOS_SINC.
--      El usuario RESPALDO no los tiene (sin privilegios de objeto ni
--      INSERT ANY TABLE): el encolado debe correr con el usuario de aplicacion
--      de SISMAI o con un DBA.
--    - NO ejecutar SincFich/crear.sql antes, durante ni despues: DROPea y
--      recrea EVENTOS_SINC y perderia tanto los 16.741 eventos actuales como
--      este lote.
--    - Si el proceso se interrumpe, las filas ya confirmadas permanecen. La
--      recarga es segura: los cursores omiten lo ya presente.
--
--  ANULACION DEL LOTE
--  La fecha de inicio se imprime como LOTE_INICIO. Para revertir solo este
--  lote, sin tocar los 16.741 eventos previos:
--    DELETE FROM SISMAI.EVENTOS_SINC
--     WHERE FECHA >= TO_DATE('<LOTE_INICIO>','YYYY-MM-DD HH24:MI:SS')
--       AND TABLA IN ('CERTNACIMIENTO','NAC_MADRE','NAC_RNACIDO','NAC_ANULADOS');
--    COMMIT;
-- ============================================================================

SET SERVEROUTPUT ON SIZE 1000000
SET LINESIZE 200
SET PAGESIZE 200
SET FEEDBACK OFF
SET TRIMSPOOL ON
SET TIMING ON

DECLARE
  -- ==========================================================================
  -- 0 = dry-run: solo conteos, cero escrituras.   <-- VALOR INICIAL SEGURO
  -- 1 = ejecuta los INSERT
  -- ==========================================================================
  V_EJECUTAR            PLS_INTEGER := 0;

  -- Tamaño del lote confirmado. 5000 en vez de 500 para reducir el numero de
  -- commits durante los ~45 minutos de carga.
  V_LOTE                PLS_INTEGER := 5000;

  V_COLA_ANTES          PLS_INTEGER := 0;
  V_COLA_DESPUES        PLS_INTEGER := 0;
  V_LOTE_INICIO         DATE;
  V_CANDIDATOS          PLS_INTEGER := 0;
  V_PENDIENTES          PLS_INTEGER := 0;
  V_YA_EN_COLA          PLS_INTEGER := 0;
  V_INSERTADOS         PLS_INTEGER := 0;
  V_COMMITS             PLS_INTEGER := 0;
  V_TIEMPO_TOTAL        PLS_INTEGER := 0;

  TYPE T_TABLA IS TABLE OF VARCHAR2(30);
  V_TABLAS T_TABLA := T_TABLA('CERTNACIMIENTO','NAC_MADRE','NAC_RNACIDO','NAC_ANULADOS');

  ----------------------------------------------------------------------------
  -- Candidatos de cada bloque: MISMO predicado que usan los cursores ENCOLAR,
  -- mas el MINUS contra la cola. Asi el conteo y la insercion no pueden
  -- discrepar, y la deduplicacion es una operacion de conjuntos (no un
  -- EXISTS correlacionado, que sin indice es O(n*m)).
  ----------------------------------------------------------------------------
  FUNCTION CAND_CERTNACIMIENTO RETURN VARCHAR2 IS
  BEGIN
    RETURN 'SELECT DISTINCT A.ID FROM SISMAI.CERTNACIMIENTO A,'
        || ' SISMAI.NAC_RNACIDO B, SISMAI.NAC_MADRE C'
        || ' WHERE A.ID=B.HCERTIFICADO AND A.ANO_CERTIF>=2010 AND A.ID=C.HCERTIFICADO'
        || ' MINUS SELECT E.ID FROM SISMAI.EVENTOS_SINC E WHERE E.TABLA=''CERTNACIMIENTO''';
  END CAND_CERTNACIMIENTO;

  FUNCTION CAND_NAC_MADRE RETURN VARCHAR2 IS
  BEGIN
    RETURN 'SELECT DISTINCT A.ID FROM SISMAI.NAC_MADRE A,'
        || ' SISMAI.CERTNACIMIENTO B, SISMAI.NAC_RNACIDO C'
        || ' WHERE A.HCERTIFICADO=B.ID AND B.ANO_CERTIF>=2010'
        || ' AND A.HCERTIFICADO=C.HCERTIFICADO'
        || ' MINUS SELECT E.ID FROM SISMAI.EVENTOS_SINC E WHERE E.TABLA=''NAC_MADRE''';
  END CAND_NAC_MADRE;

  FUNCTION CAND_NAC_RNACIDO RETURN VARCHAR2 IS
  BEGIN
    RETURN 'SELECT DISTINCT A.ID FROM SISMAI.NAC_RNACIDO A,'
        || ' SISMAI.CERTNACIMIENTO B, SISMAI.NAC_MADRE C'
        || ' WHERE A.HCERTIFICADO=B.ID AND B.ANO_CERTIF>=2010'
        || ' AND A.HCERTIFICADO=C.HCERTIFICADO'
        || ' MINUS SELECT E.ID FROM SISMAI.EVENTOS_SINC E WHERE E.TABLA=''NAC_RNACIDO''';
  END CAND_NAC_RNACIDO;

  FUNCTION CAND_NAC_ANULADOS RETURN VARCHAR2 IS
  BEGIN
    RETURN 'SELECT DISTINCT A.ID FROM SISMAI.NAC_ANULADOS A WHERE A.ANO_CERTIF>=2010'
        || ' MINUS SELECT E.ID FROM SISMAI.EVENTOS_SINC E WHERE E.TABLA=''NAC_ANULADOS''';
  END CAND_NAC_ANULADOS;

  FUNCTION SQL_CANDIDATOS(p_tabla VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    IF p_tabla = 'CERTNACIMIENTO' THEN RETURN CAND_CERTNACIMIENTO;
    ELSIF p_tabla = 'NAC_MADRE'    THEN RETURN CAND_NAC_MADRE;
    ELSIF p_tabla = 'NAC_RNACIDO'  THEN RETURN CAND_NAC_RNACIDO;
    ELSE                                RETURN CAND_NAC_ANULADOS;
    END IF;
  END SQL_CANDIDATOS;

  -- Total de candidatos antes de restar los ya encolados.
  FUNCTION SQL_BRUTOS(p_tabla VARCHAR2) RETURN VARCHAR2 IS
    V_SQL VARCHAR2(4000);
  BEGIN
    V_SQL := SQL_CANDIDATOS(p_tabla);
    -- Se quita la parte MINUS para obtener el total bruto.
    RETURN 'SELECT COUNT(*) FROM ('
        || SUBSTR(V_SQL, 1, INSTR(V_SQL, ' MINUS ') - 1) || ')';
  END SQL_BRUTOS;

  PROCEDURE CABECERA(p_tabla VARCHAR2) IS
  BEGIN
    DBMS_OUTPUT.PUT_LINE(CHR(10)||'--- '||p_tabla||' ---');
  END CABECERA;

  ----------------------------------------------------------------------------
  -- Reporte por bloque. V_PENDIENTES se cuenta con el mismo MINUS que usan los
  -- cursores, asi que es exactamente lo que se insertara.
  ----------------------------------------------------------------------------
  PROCEDURE CONTEO(p_tabla VARCHAR2) IS
  BEGIN
    EXECUTE IMMEDIATE SQL_BRUTOS(p_tabla) INTO V_CANDIDATOS;
    EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM (' || SQL_CANDIDATOS(p_tabla) || ')'
      INTO V_PENDIENTES;

    V_YA_EN_COLA  := V_CANDIDATOS - V_PENDIENTES;
    V_INSERTADOS := V_PENDIENTES;

    DBMS_OUTPUT.PUT_LINE('  candidatos totales     : '||TO_CHAR(V_CANDIDATOS,'FM999999999'));
    DBMS_OUTPUT.PUT_LINE('  ya presentes en cola   : '||TO_CHAR(V_YA_EN_COLA,'FM999999999')
                         ||'  (omitidos por deduplicar)');
    DBMS_OUTPUT.PUT_LINE('  a insertar             : '||TO_CHAR(V_INSERTADOS,'FM999999999'));
  END CONTEO;

  ----------------------------------------------------------------------------
  -- Insercion. Los cursores son el mismo MINUS del conteo: lo ya presente en
  -- la cola no se vuelve a encolar, y V_i SI esta inicializado, con lo que el
  -- COMMIT por lote ocurre. Ante un error se registra y se continua, sin el
  -- GOTO infinito del script original.
  ----------------------------------------------------------------------------
  PROCEDURE ENCOLAR(p_tabla VARCHAR2) IS
    CURSOR C_CERT IS
      SELECT DISTINCT A.ID FROM SISMAI.CERTNACIMIENTO A, SISMAI.NAC_RNACIDO B, SISMAI.NAC_MADRE C
       WHERE A.ID=B.HCERTIFICADO AND A.ANO_CERTIF>=2010 AND A.ID=C.HCERTIFICADO
      MINUS
      SELECT E.ID FROM SISMAI.EVENTOS_SINC E WHERE E.TABLA='CERTNACIMIENTO';
    CURSOR C_MADRE IS
      SELECT DISTINCT A.ID FROM SISMAI.NAC_MADRE A, SISMAI.CERTNACIMIENTO B, SISMAI.NAC_RNACIDO C
       WHERE A.HCERTIFICADO=B.ID AND B.ANO_CERTIF>=2010 AND A.HCERTIFICADO=C.HCERTIFICADO
      MINUS
      SELECT E.ID FROM SISMAI.EVENTOS_SINC E WHERE E.TABLA='NAC_MADRE';
    CURSOR C_RNAC IS
      SELECT DISTINCT A.ID FROM SISMAI.NAC_RNACIDO A, SISMAI.CERTNACIMIENTO B, SISMAI.NAC_MADRE C
       WHERE A.HCERTIFICADO=B.ID AND B.ANO_CERTIF>=2010 AND A.HCERTIFICADO=C.HCERTIFICADO
      MINUS
      SELECT E.ID FROM SISMAI.EVENTOS_SINC E WHERE E.TABLA='NAC_RNACIDO';
    CURSOR C_ANUL IS
      SELECT DISTINCT A.ID FROM SISMAI.NAC_ANULADOS A WHERE A.ANO_CERTIF>=2010
      MINUS
      SELECT E.ID FROM SISMAI.EVENTOS_SINC E WHERE E.TABLA='NAC_ANULADOS';

    V_ID  NUMBER;
    V_i   PLS_INTEGER := 0;          -- inicializado a proposito
    V_INS PLS_INTEGER := 0;
    V_ERR PLS_INTEGER := 0;
  BEGIN
    IF p_tabla = 'CERTNACIMIENTO' THEN
      FOR R IN C_CERT LOOP
        BEGIN
          INSERT INTO SISMAI.EVENTOS_SINC (ID,TABLA,EVENTO,FECHA)
          VALUES (R.ID,'CERTNACIMIENTO','2',SYSDATE);
          V_INS := V_INS + 1;
        EXCEPTION
          WHEN OTHERS THEN
            V_ERR := V_ERR + 1;
            DBMS_OUTPUT.PUT_LINE('  ERROR en CERTNACIMIENTO ID='||R.ID
                                 ||' SQLCODE='||SQLCODE);
        END;
        V_i := V_i + 1;
        IF V_i >= V_LOTE THEN V_i := 0; COMMIT; V_COMMITS := V_COMMITS + 1; END IF;
      END LOOP;

    ELSIF p_tabla = 'NAC_MADRE' THEN
      FOR R IN C_MADRE LOOP
        BEGIN
          INSERT INTO SISMAI.EVENTOS_SINC (ID,TABLA,EVENTO,FECHA)
          VALUES (R.ID,'NAC_MADRE','2',SYSDATE);
          V_INS := V_INS + 1;
        EXCEPTION
          WHEN OTHERS THEN
            V_ERR := V_ERR + 1;
            DBMS_OUTPUT.PUT_LINE('  ERROR en NAC_MADRE ID='||R.ID
                                 ||' SQLCODE='||SQLCODE);
        END;
        V_i := V_i + 1;
        IF V_i >= V_LOTE THEN V_i := 0; COMMIT; V_COMMITS := V_COMMITS + 1; END IF;
      END LOOP;

    ELSIF p_tabla = 'NAC_RNACIDO' THEN
      FOR R IN C_RNAC LOOP
        BEGIN
          INSERT INTO SISMAI.EVENTOS_SINC (ID,TABLA,EVENTO,FECHA)
          VALUES (R.ID,'NAC_RNACIDO','2',SYSDATE);
          V_INS := V_INS + 1;
        EXCEPTION
          WHEN OTHERS THEN
            V_ERR := V_ERR + 1;
            DBMS_OUTPUT.PUT_LINE('  ERROR en NAC_RNACIDO ID='||R.ID
                                 ||' SQLCODE='||SQLCODE);
        END;
        V_i := V_i + 1;
        IF V_i >= V_LOTE THEN V_i := 0; COMMIT; V_COMMITS := V_COMMITS + 1; END IF;
      END LOOP;

    ELSE
      FOR R IN C_ANUL LOOP
        BEGIN
          INSERT INTO SISMAI.EVENTOS_SINC (ID,TABLA,EVENTO,FECHA)
          VALUES (R.ID,'NAC_ANULADOS','2',SYSDATE);
          V_INS := V_INS + 1;
        EXCEPTION
          WHEN OTHERS THEN
            V_ERR := V_ERR + 1;
            DBMS_OUTPUT.PUT_LINE('  ERROR en NAC_ANULADOS ID='||R.ID
                                 ||' SQLCODE='||SQLCODE);
        END;
        V_i := V_i + 1;
        IF V_i >= V_LOTE THEN V_i := 0; COMMIT; V_COMMITS := V_COMMITS + 1; END IF;
      END LOOP;
    END IF;

    IF V_INS > 0 THEN COMMIT; V_COMMITS := V_COMMITS + 1; END IF;
    DBMS_OUTPUT.PUT_LINE('  insertados realmente  : '||TO_CHAR(V_INS,'FM999999999')
                         ||'  (errores: '||V_ERR||', commits: '||V_COMMITS||')');
  END ENCOLAR;
BEGIN
  V_LOTE_INICIO := SYSDATE;
  DBMS_OUTPUT.PUT_LINE('======================================================================');
  DBMS_OUTPUT.PUT_LINE(' ENCOLADO DE NATALIDAD -> SISMAI.EVENTOS_SINC');
  DBMS_OUTPUT.PUT_LINE(' Ejecutado por : '||USER);
  DBMS_OUTPUT.PUT_LINE(' Modo         : '
    || CASE WHEN V_EJECUTAR=1 THEN 'EJECUCION (INSERT + COMMIT por '||V_LOTE||')'
            ELSE 'DRY-RUN (sin escrituras)' END);
  DBMS_OUTPUT.PUT_LINE(' LOTE_INICIO  : '||TO_CHAR(V_LOTE_INICIO,'YYYY-MM-DD HH24:MI:SS'));
  DBMS_OUTPUT.PUT_LINE('======================================================================');

  SELECT COUNT(*) INTO V_COLA_ANTES FROM SISMAI.EVENTOS_SINC;
  DBMS_OUTPUT.PUT_LINE(CHR(10)||'Cola actual ANTES del lote: '||TO_CHAR(V_COLA_ANTES,'FM999999999'));

  FOR I IN 1 .. V_TABLAS.COUNT LOOP
    CABECERA(V_TABLAS(I));
    CONTEO(V_TABLAS(I));
    IF V_EJECUTAR = 1 THEN
      ENCOLAR(V_TABLAS(I));
    END IF;
  END LOOP;

  IF V_EJECUTAR = 0 THEN
    DBMS_OUTPUT.PUT_LINE(CHR(10)||'>>> DRY-RUN terminado. No se escribio nada en EVENTOS_SINC.');
    DBMS_OUTPUT.PUT_LINE('>>> Para ejecutar: poner V_EJECUTAR := 1 y relanzar con el');
    DBMS_OUTPUT.PUT_LINE('>>> usuario de SISMAI, con la cola respaldada y en ventana');
    DBMS_OUTPUT.PUT_LINE('>>> de mantenimiento.');
  ELSE
    COMMIT;
    V_TIEMPO_TOTAL := (SYSDATE - V_LOTE_INICIO) * 86400;
    DBMS_OUTPUT.PUT_LINE(CHR(10)||'>>> EJECUCION terminada.');
    DBMS_OUTPUT.PUT_LINE('>>> Commits por lote: '||V_COMMITS
                         ||'   Duracion: '||TO_CHAR(TRUNC(V_TIEMPO_TOTAL/60))||' min '
                         ||TO_CHAR(MOD(V_TIEMPO_TOTAL,60),'FM00')||' s');
  END IF;

  SELECT COUNT(*) INTO V_COLA_DESPUES FROM SISMAI.EVENTOS_SINC;
  DBMS_OUTPUT.PUT_LINE('Cola actual DESPUES del lote: '||TO_CHAR(V_COLA_DESPUES,'FM999999999'));
  DBMS_OUTPUT.PUT_LINE('Diferencia: '||TO_CHAR(V_COLA_DESPUES - V_COLA_ANTES,'FM999999999')
                       ||'  (debe coincidir con la suma de "a insertar")');
  DBMS_OUTPUT.PUT_LINE(CHR(10)||'Anulacion de ESTE lote:');
  DBMS_OUTPUT.PUT_LINE('  DELETE FROM SISMAI.EVENTOS_SINC');
  DBMS_OUTPUT.PUT_LINE('   WHERE FECHA >= TO_DATE('''
       ||TO_CHAR(V_LOTE_INICIO,'YYYY-MM-DD HH24:MI:SS')
       ||''',''YYYY-MM-DD HH24:MI:SS'')');
  DBMS_OUTPUT.PUT_LINE('     AND TABLA IN (''CERTNACIMIENTO'',''NAC_MADRE'',''NAC_RNACIDO'',''NAC_ANULADOS'');');
  DBMS_OUTPUT.PUT_LINE('  COMMIT;');
  DBMS_OUTPUT.PUT_LINE('======================================================================');

  -- Red de seguridad opcional, DESCOMENTAR solo con autorizacion. Sin indice
  -- en (TABLA,ID) la cola sigue vulnerable a duplicados silenciosos y cualquier
  -- deduplicacion futura sera lenta. Comprobar antes que no hay duplicados.
  -- CREATE UNIQUE INDEX SISMAI.IX_EVENTOS_SINC_TAB_ID
  --   ON SISMAI.EVENTOS_SINC (TABLA, ID);
END;
/

PROMPT
PROMPT Verificacion final por tabla (SISMAI.EVENTOS_SINC):
COLUMN TABLA FORMAT A22
SELECT TABLA, COUNT(*) AS TOTAL,
       TO_CHAR(MIN(FECHA),'YYYY-MM-DD HH24:MI:SS') AS FECHA_MIN,
       TO_CHAR(TO_CHAR(MAX(FECHA),'YYYY-MM-DD HH24:MI:SS')) AS FECHA_MAX
  FROM SISMAI.EVENTOS_SINC
 GROUP BY TABLA
 ORDER BY TABLA;

PROMPT Duplicados por TABLA+ID (debe ser 0):
SELECT COUNT(*) AS DUPLICADOS FROM (
  SELECT TABLA, ID FROM SISMAI.EVENTOS_SINC
   GROUP BY TABLA, ID HAVING COUNT(*) > 1);

PROMPT Eventos de natalidad ya encolados (debe ser 0 antes de ejecutar el lote):
SELECT COUNT(*) AS NATALIDAD_EN_COLA FROM SISMAI.EVENTOS_SINC
 WHERE TABLA IN ('CERTNACIMIENTO','NAC_MADRE','NAC_RNACIDO','NAC_ANULADOS');
EXIT
