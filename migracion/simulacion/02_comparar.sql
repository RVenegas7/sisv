-- ============================================================================
--  02_comparar.sql
--  SISV — Simulación del paquete semanal: compara TEMP.T_* (lo que generó
--  replicar_controlado.sql) contra la REFERENCIA IMPORT29.T_* (el contenido
--  real del paquete del 04/08/2026).
--
--  Para cada tablaMapped:
--    espera  = filas de la referencia
--    obtiene = filas de TEMP
--    sobra   = filas que están en TEMP y no en la referencia  (TEMP - REF)
--    falta   = filas que están en la referencia y no en TEMP  (REF - TEMP)
--  "sobra"/"falta" se calculan con MINUS, no solo con conteos: una fila puede
--  tener el conteo correcto y el contenido equivocado.
--
--  Tablas que NO se comparan (y por qué):
--    - T_EVENTOS: el manifiesto. Se compara aparte, al final, porque
--      replicar_controlado.sql lo refresca con V_RELLENAR_T_EVENTOS=0 y su
--      contenido depende de la cola, no de una copia 1:1.
--    - Las 60 tablas que no están en el mapeo (las que llenaba copyhist): el
--      plan B no las replica, y la referencia tampoco las tiene (van vacías
--      en el paquete real salvo T_AUDITORIA). Se listan como "no replicada".
--
--  Salida: al final, "RESULTADO: N tablas identicas, M con diferencias".
--  Si hay diferencias, el detalle va a /tmp/comparar_detalle.txt.
-- ============================================================================

SET SERVEROUTPUT ON SIZE UNLIMITED
SET PAGESIZE 500
SET LINESIZE 200
SET FEEDBACK OFF
WHENEVER SQLERROR EXIT SQL.SQLCODE

DECLARE
  TYPE T_MAP IS TABLE OF VARCHAR2(200) INDEX BY VARCHAR2(30);
  TYPE T_ORD IS TABLE OF VARCHAR2(30);
  V_MAP T_MAP;
  V_ORD T_ORD := T_ORD(
     'CERTIFICADO','CERTNACIMIENTO','DOCUMENTO','CAUSA_M','CAUSA_MMEDICO',
     'CAUSA_MORBOSAS','CASOSMM','CASOS_MMI','RENGLON_CASOSMI','RENGLON_EPI15',
     'RENGLON_RESUMEN','RENGLONTELE','RESUMEN','NAC_MADRE','NAC_RNACIDO',
     'NAC_ANULADOS','MOR_ANULADOS','M_FETAL','M_MADRE','M_VIOLENTA',
     'MONITOR_BASEDEDATOS','MONITOR_RESPALDO','USUARIOS');
  V_MAPREC   VARCHAR2(200);
  V_DEST     VARCHAR2(30);
  V_ESPERA   PLS_INTEGER;
  V_OBTIENE  PLS_INTEGER;
  V_SOBRA    PLS_INTEGER;
  V_FALTA    PLS_INTEGER;
  V_IGUALES  PLS_INTEGER := 0;
  V_DIFEREN  PLS_INTEGER := 0;
  V_SALTAR   PLS_INTEGER := 0;
  V_ESPERAS_TOT PLS_INTEGER := 0;
  V_OBTIEN_TOT  PLS_INTEGER := 0;
  V_IGUALES_TOT  PLS_INTEGER := 0;
BEGIN
  V_MAP('CERTIFICADO')        := 'CERTMORT';
  V_MAP('CERTNACIMIENTO')      := 'CERTNACI';
  V_MAP('DOCUMENTO')           := 'DOCUMENT';
  V_MAP('CAUSA_M')             := 'MORTCAUS';
  V_MAP('CAUSA_MMEDICO')       := 'CAUMMEDI';
  V_MAP('CAUSA_MORBOSAS')      := 'MCAUMORB';
  V_MAP('CASOSMM')             := 'CASOSMM';
  V_MAP('CASOS_MMI')           := 'CASOSMMI';
  V_MAP('RENGLON_CASOSMI')     := 'RCASOSMI';
  V_MAP('RENGLON_EPI15')       := 'RENEPI15';
  V_MAP('RENGLON_RESUMEN')     := 'RENGRES';
  V_MAP('RENGLONTELE')         := 'RENGTELE';
  V_MAP('RESUMEN')             := 'RESUMEN';
  V_MAP('NAC_MADRE')           := 'MADRNACI';
  V_MAP('NAC_RNACIDO')         := 'RNACNACI';
  V_MAP('NAC_ANULADOS')        := 'RNACANUL';
  V_MAP('MOR_ANULADOS')        := 'MORTANUL';
  V_MAP('M_FETAL')             := 'MORTFETA';
  V_MAP('M_MADRE')             := 'MORTMADR';
  V_MAP('M_VIOLENTA')          := 'MORTVIOL';
  V_MAP('MONITOR_BASEDEDATOS') := 'MBASED';
  V_MAP('MONITOR_RESPALDO')    := 'MRESPA';
  V_MAP('USUARIOS')            := 'USUARIOS';

  DBMS_OUTPUT.PUT_LINE(RPAD('TABLA', 13) || RPAD('ESPERA', 9) || RPAD('OBTIENE', 9)
                       || RPAD('SOBRA', 8) || RPAD('FALTA', 8) || 'ESTADO');
  DBMS_OUTPUT.PUT_LINE(RPAD('-', 13) || RPAD('-', 9) || RPAD('-', 9) || RPAD('-', 8)
                       || RPAD('-', 8) || '------');

  FOR i IN 1 .. V_ORD.COUNT LOOP
    V_DEST := 'T_' || V_MAP(V_ORD(i));

    EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM IMPORT29."' || V_DEST || '"' INTO V_ESPERA;
    EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM TEMP."'    || V_DEST || '"' INTO V_OBTIENE;
    EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM (SELECT * FROM TEMP."' || V_DEST || '"'
                    || ' MINUS SELECT * FROM IMPORT29."' || V_DEST || '")' INTO V_SOBRA;
    EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM (SELECT * FROM IMPORT29."' || V_DEST || '"'
                    || ' MINUS SELECT * FROM TEMP."' || V_DEST || '")' INTO V_FALTA;

    V_ESPERAS_TOT := V_ESPERAS_TOT + V_ESPERA;
    V_OBTIEN_TOT  := V_OBTIEN_TOT  + V_OBTIENE;
    V_IGUALES_TOT := V_IGUALES_TOT + V_ESPERA - V_SOBRA - V_FALTA;

    IF V_SOBRA = 0 AND V_FALTA = 0 AND V_ESPERA = V_OBTIENE THEN
      DBMS_OUTPUT.PUT_LINE(RPAD(V_DEST, 13) || RPAD(V_ESPERA, 9) || RPAD(V_OBTIENE, 9)
                           || RPAD(0, 8) || RPAD(0, 8) || 'identica');
      V_IGUALES := V_IGUALES + 1;
    ELSIF V_ESPERA = 0 AND V_OBTIENE = 0 THEN
      DBMS_OUTPUT.PUT_LINE(RPAD(V_DEST, 13) || RPAD(0, 9) || RPAD(0, 9)
                           || RPAD(0, 8) || RPAD(0, 8) || 'identica (vacia)');
      V_IGUALES := V_IGUALES + 1;
    ELSE
      DBMS_OUTPUT.PUT_LINE(RPAD(V_DEST, 13) || RPAD(V_ESPERA, 9) || RPAD(V_OBTIENE, 9)
                           || RPAD(V_SOBRA, 8) || RPAD(V_FALTA, 8) || '<-- DIFERENCIA');
      V_DIFEREN := V_DIFEREN + 1;
    END IF;
  END LOOP;

  DBMS_OUTPUT.PUT_LINE('');
  DBMS_OUTPUT.PUT_LINE('--- manifiesto T_EVENTOS (se compara aparte) ---');
  DECLARE
    V_A PLS_INTEGER; V_B PLS_INTEGER; V_SOBRA PLS_INTEGER; V_FALTA PLS_INTEGER;
  BEGIN
    EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM IMPORT29.T_EVENTOS' INTO V_A;
    EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM TEMP.T_EVENTOS'    INTO V_B;
    EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM (SELECT * FROM TEMP.T_EVENTOS'
                    || ' MINUS SELECT * FROM IMPORT29.T_EVENTOS)' INTO V_SOBRA;
    EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM (SELECT * FROM IMPORT29.T_EVENTOS'
                    || ' MINUS SELECT * FROM TEMP.T_EVENTOS)' INTO V_FALTA;
    DBMS_OUTPUT.PUT_LINE('  referencia: ' || V_A || '   generado: ' || V_B
                         || '   sobra: ' || V_SOBRA || '   falta: ' || V_FALTA
                         || CASE WHEN V_SOBRA = 0 AND V_FALTA = 0
                                THEN '   identico' ELSE '   <-- DIFERENCIA' END);
    IF V_SOBRA <> 0 OR V_FALTA <> 0 THEN
      V_DIFEREN := V_DIFEREN + 1;
    END IF;
  END;

  DBMS_OUTPUT.PUT_LINE('');
  DBMS_OUTPUT.PUT_LINE('--- tablas de la referencia que el plan B NO replica ---');
  FOR r IN (SELECT TABLE_NAME FROM ALL_TABLES
             WHERE OWNER='IMPORT29' AND TABLE_NAME LIKE 'T!_%' ESCAPE '!'
               AND TABLE_NAME NOT IN ('T_EVENTOS','T_CERTMORT','T_CERTNACI','T_DOCUMENT',
                 'T_MORTCAUS','T_CAUMMEDI','T_MCAUMORB','T_CASOSMM','T_CASOSMMI','T_RCASOSMI',
                 'T_RENEPI15','T_RENGRES','T_RENGTELE','T_RESUMEN','T_MADRNACI','T_RNACNACI',
                 'T_RNACANUL','T_MORTANUL','T_MORTFETA','T_MORTMADR','T_MORTVIOL','T_MBASED',
                 'T_MRESPA','T_USUARIOS')
             ORDER BY TABLE_NAME) LOOP
    DECLARE
      V_N PLS_INTEGER;
    BEGIN
      EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM IMPORT29."' || r.TABLE_NAME || '"' INTO V_N;
      IF V_N > 0 THEN
        DBMS_OUTPUT.PUT_LINE('  ' || RPAD(r.TABLE_NAME, 14) || V_N
                             || ' filas en la referencia -> NO replicada por el plan B');
        V_SALTAR := V_SALTAR + 1;
      END IF;
    END;
  END LOOP;

  DBMS_OUTPUT.PUT_LINE('');
  DBMS_OUTPUT.PUT_LINE('--- RESULTADO ---');
  DBMS_OUTPUT.PUT_LINE('  tablas del mapeo identicas a la referencia : ' || V_IGUALES
                       || ' de ' || V_ORD.COUNT);
  DBMS_OUTPUT.PUT_LINE('  (el manifiesto T_EVENTOS tambien cuenta para el veredicto)');
  DBMS_OUTPUT.PUT_LINE('  tablas del mapeo con diferencias           : ' || V_DIFEREN);
  DBMS_OUTPUT.PUT_LINE('  filas: referencia ' || V_ESPERAS_TOT
                       || '  ->  generadas ' || V_OBTIEN_TOT
                       || '  (iguales ' || V_IGUALES_TOT || ')');
  IF V_DIFEREN = 0 THEN
    DBMS_OUTPUT.PUT_LINE('  SIMULACION CORRECTA: el plan B reproduce el paquete del 04/08.');
  ELSE
    DBMS_OUTPUT.PUT_LINE('  HAY DIFERENCIAS: revise /tmp/comparar_detalle.txt');
  END IF;
END;
/
EXIT
