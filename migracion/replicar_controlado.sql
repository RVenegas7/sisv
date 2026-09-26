-- ============================================================================
--  replicar_controlado.sql
--  SISV / SAPS Lara — PLAN B: replicacion CONTROLADA de SISMAI.EVENTOS_SINC
--  hacia TEMP.T_* (el staging del sobre semanal), sin ejecutar plcer1.sql
--  Fecha: 2026-09-26
--
--  QUE ES Y QUE NO ES
--  Este script NO es el motor original. `plcer1.sql` / `cr_repli_*.sql` no
--  estan disponibles (ver PENDIENTES.md 17.3) y la fase que se perdio el
--  08/09/2026 es precisamente la que crea y llena las 83 tablas TEMP.T_*.
--  Este script RECONSTRUYE solo el nucleo verificado de esa fase, con el
--  contrato que ya valido al 100% contra el sobre del 04/08/2026
--  (enviados/routlar1_482026_1526.ZIP; PENDIENTES.md 16 y la linea base):
--
--    "Viaja la fila si su ULTIMO evento en la cola es INSERT(1) o UPDATE(2);
--     si el ultimo es DELETE(3) no viaja. Se replica el ESTADO CONSOLIDADO
--     actual de la fila de origen, y el sobre se arma con la COLA COMPLETA
--     (no solo la ventana de la semana)."
--
--  Lo que SI reproduce: los 23 mapeos TABLA -> ORIGEN -> T_* del contrato
--  (backend/registros/data/rutarala_spec.json) y el manifiesto TEMP.T_EVENTOS.
--  Lo que NO reproduce, y por tanto no se debe esperar de el:
--    - Las ~60 tablas T_* que no estan en el mapeo (las que llenaba `copyhist`,
--      p.ej. T_AUDITORIA, que en el 04/08 viajaron enteras y sin eventos).
--    - El DROP/CREATE de las tablas: el DDL guardado en
--      legancy/analisis/schema_routlar1.sql esta TRUNCADO por linea, asi que
--      recrearlas aqui seria inventar estructura. Este script llena las tablas
--      que YA existen, sin recrearlas.
--    - El TRUNCATE final de SISMAI.EVENTOS_SINC (a proposito, ver garantias).
--    - El envio al nivel central: eso lo hace la aplicacion, no la base.
--
--  GARANTIAS
--    - No escribe NADA en SISMAI.*: solo SELECT sobre las tablas de origen.
--    - NO trunca, NO borra y NO actualiza SISMAI.EVENTOS_SINC. La cola queda
--      intacta (es el unico soporte que queda de los 3,37 M del 27/08, con
--      copia verificada en respaldo_20260925/eventos_sinc_20260925.csv).
--    - No hace DDL: no dropea ni crea nada.
--    - Es idempotente: borra de TEMP.T_* solo los IDs que va a insertar y los
--      reinserta. Reejecutarlo no duplica ni pierde filas, y las filas de TEMP
--      que no estan en la cola NO se tocan.
--    - Confirma por tabla (no una sola transaccion de 1,3 M de filas): si se
--      interrumpe, quedan las tablas ya confirmadas y se puede relanzar.
--    - Ante cualquier error en una tabla: ROLLBACK de esa tabla y sigue.
--    - MODO SEGURO POR DEFECTO: V_EJECUTAR = 0 hace solo SELECT y conteos.
--
--  REQUISITOS
--    - DBA. El usuario RESPALDO no tiene privilegios de objeto ni
--      INSERT ANY TABLE (ver encolar_natalidad_legacy.sql). Ideal: el usuario
--      de aplicacion de SISMAI, o el DBA `oracle`.
--    - SELECT sobre ALL_TAB_COLUMNS (SELECT_CATALOG_ROLE o DBA) para armar la
--      lista de columnas por interseccion.
--    - Cola respaldada y verificada: respaldo_20260925/eventos_sinc_20260925.csv
--      (16.741 filas, SHA-256 3ac3a054055da3f8006cb21c02937ff744dd7200e3f2ce53ed7d6d144c7aad51).
--    - Fuera de la ventana del `exp` diario de las 13:00.
--    - NO correr junto a SincFich/crear.sql (DROPea EVENTOS_SINC).
--
--  USO
--    1) V_EJECUTAR = 0: guardar la salida como evidencia y revisar que ningun
--       contador sea inesperado (secciones [3] y [5]).
--    2) Confirmar por escrito la recepcion central del sobre anterior.
--    3) V_EJECUTAR = 1: ejecutar. Cada tabla imprime LOTE_INICIO.
--    4) ARMAR EL SOBRE con la aplicacion (RoutLar1 / SistemaTransferencia.exe):
--       este script NO envia nada. El sobre debe llevar los 5 archivos.
--
--  ANULACION (solo lo hecho por este script, sin tocar la cola)
--    DELETE FROM TEMP.T_<TABLA> WHERE ID IN (<IDs del lote>);
--    DELETE FROM TEMP.T_EVENTOS  WHERE TABLA = '<TABLA>';
--    COMMIT;
--  Use la fecha maxima de LOTE_INICIO impresa por el script.
--
--  LO QUE EL DBA DEBE REVISAR ANTES DE EJECUTAR
--    - La seccion [5] lista los valores de TABLA de la cola SIN mapeo (al
--      21/09: REG_VACUNACION, PACIENTE_FICHA_EPI y PACIENTE_COND_ESPE, 16.741
--      filas). Esos eventos NO se replican hasta que se agregue su mapeo; la
--      seccion [5] propone candidatos por coincidencia de columnas, pero la
--      confirmacion (que T_ corresponde a que TABLA) es funcional: no se deduce
--      de la BD, la tiene que dar el soporte SIS/Centura.
--    - Si alguna tabla se salta por "columna NOT NULL sin origen", NO se
--      fuerce: significa que el mapeo no es 1:1 y la logica original hacia
--      otra cosa (transformaciones, no copia).
-- ============================================================================

SET SERVEROUTPUT ON SIZE 1000000
SET LINESIZE 200
SET PAGESIZE 500
SET FEEDBACK OFF
SET TRIMSPOOL ON
SET TIMING ON

DECLARE
  -- ==========================================================================
  -- 0 = dry-run: solo SELECT, cero escrituras.   <-- VALOR INICIAL SEGURO
  -- 1 = ejecuta DELETE+INSERT sobre TEMP.T_* y COMMIT por tabla
  -- ==========================================================================
  V_EJECUTAR                PLS_INTEGER := 0;

  -- 0 = T_EVENTOS se refresca solo para las claves replicadas (modo seguro;
  --     quedan filas de corridas previas, que volverian a viajar en el sobre)
  -- 1 = T_EVENTOS se recarga completo con la cola mapeada (lo que hacia el
  --     ciclo original al recrear la tabla). Descarta el manifiesto anterior:
  --     usese solo si el nivel central ya confirmo el sobre previo.
  V_RELLENAR_T_EVENTOS      PLS_INTEGER := 0;

  V_COLA_TOTAL              PLS_INTEGER := 0;
  V_LOTE_INICIO             DATE;
  V_TABLAS_MAPEADAS         PLS_INTEGER := 0;
  V_TABLAS_SALTADAS         PLS_INTEGER := 0;
  V_INS_TOTAL               PLS_INTEGER := 0;
  V_DEL_TOTAL               PLS_INTEGER := 0;
  V_FREO_MB                 PLS_INTEGER := 0;

  -- El mapa se guarda como 'ORIGEN|DESTINO' indexado por el nombre de la TABLA
  -- de la cola. No se usa un record porque el constructor de record no existe
  -- en PL/SQL de 10.1 y rompe la compilacion del bloque.
  TYPE T_MAP IS TABLE OF VARCHAR2(200) INDEX BY VARCHAR2(30);
  TYPE T_ORD IS TABLE OF VARCHAR2(30);

  -- Contrato validado contra el sobre del 04/08/2026
  -- (backend/registros/data/rutarala_spec.json -> "mapeo")
  V_MAP T_MAP;
  V_ORD T_ORD := T_ORD(
     'CERTIFICADO','CERTNACIMIENTO','DOCUMENTO','CAUSA_M','CAUSA_MMEDICO',
     'CAUSA_MORBOSAS','CASOSMM','CASOS_MMI','RENGLON_CASOSMI','RENGLON_EPI15',
     'RENGLON_RESUMEN','RENGLONTELE','RESUMEN','NAC_MADRE','NAC_RNACIDO',
     'NAC_ANULADOS','MOR_ANULADOS','M_FETAL','M_MADRE','M_VIOLENTA',
     'MONITOR_BASEDEDATOS','MONITOR_RESPALDO','USUARIOS');

  ----------------------------------------------------------------------------
  -- Utilidades
  ----------------------------------------------------------------------------
  FUNCTION EXISTE(p_propietario VARCHAR2, p_tabla VARCHAR2) RETURN NUMBER IS
    V_N NUMBER;
  BEGIN
    SELECT COUNT(*) INTO V_N FROM ALL_TABLES
     WHERE OWNER = p_propietario AND TABLE_NAME = p_tabla;
    RETURN V_N;
  END EXISTE;

  -- Columnas del destino (TEMP.T_*) que tambien existen en el origen
  -- (SISMAI.*), en el orden del destino. Es la unica fuente de verdad: el DDL
  -- de legancy/analisis/schema_routlar1.sql esta truncado y no sirve para
  -- reconstruir las tablas.
  FUNCTION COLS_COMUNES(p_origen VARCHAR2, p_destino VARCHAR2) RETURN VARCHAR2 IS
    V_LIST VARCHAR2(4000);
  BEGIN
    SELECT LISTAGG(B.COLUMN_NAME, ',') WITHIN GROUP (ORDER BY B.COLUMN_ID)
      INTO V_LIST
      FROM ALL_TAB_COLUMNS A, ALL_TAB_COLUMNS B
     WHERE A.OWNER = 'SISMAI' AND A.TABLE_NAME = p_origen
       AND B.OWNER = 'TEMP'  AND B.TABLE_NAME = p_destino
       AND A.COLUMN_NAME = B.COLUMN_NAME;
    RETURN V_LIST;
  EXCEPTION
    WHEN OTHERS THEN RETURN NULL;   -- incluye ORA-01489 (agregado > 4000)
  END COLS_COMUNES;

  -- Columnas del destino NOT NULL que NO existen en el origen: si hay alguna,
  -- el mapeo no es 1:1 y el INSERT no es seguro.
  FUNCTION FALTAN_NOT_NULL(p_origen VARCHAR2, p_destino VARCHAR2) RETURN VARCHAR2 IS
    V_LIST VARCHAR2(1000);
  BEGIN
    SELECT LISTAGG(B.COLUMN_NAME, ',') WITHIN GROUP (ORDER BY B.COLUMN_ID)
      INTO V_LIST
      FROM ALL_TAB_COLUMNS B
     WHERE B.OWNER = 'TEMP' AND B.TABLE_NAME = p_destino
       AND B.NULLABLE = 'N'
       AND NOT EXISTS (SELECT 1 FROM ALL_TAB_COLUMNS A
                        WHERE A.OWNER = 'SISMAI' AND A.TABLE_NAME = p_origen
                          AND A.COLUMN_NAME = B.COLUMN_NAME);
    RETURN V_LIST;
  EXCEPTION
    WHEN NO_DATA_FOUND THEN RETURN NULL;
    WHEN OTHERS        THEN RETURN '?';
  END FALTAN_NOT_NULL;

  FUNCTION NUM_COLS(p_lista VARCHAR2) RETURN PLS_INTEGER IS
  BEGIN
    IF p_lista IS NULL THEN RETURN 0; END IF;
    RETURN LENGTH(p_lista) - LENGTH(REPLACE(p_lista, ',', '')) + 1;
  END NUM_COLS;

  ----------------------------------------------------------------------------
  -- El lote: IDs cuyo ULTIMO evento en la cola es INSERT(1) o UPDATE(2).
  -- ROWID DESC desempata los eventos con la misma FECHA (gana el ultimo
  -- insertado), que es lo mas cercano a "lo que paso al final".
  -- Una sola pasada analitica: NO se usa NOT EXISTS correlacionado porque
  -- EVENTOS_SINC no tiene indice (mismo aviso que encolar_natalidad_legacy.sql).
  ----------------------------------------------------------------------------
  FUNCTION SQL_LOTE(p_tabla VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    RETURN 'SELECT ID FROM (SELECT E.ID, E.EVENTO,'
        || ' ROW_NUMBER() OVER (PARTITION BY E.ID ORDER BY E.FECHA DESC NULLS LAST, E.ROWID DESC) RN'
        || ' FROM SISMAI.EVENTOS_SINC E WHERE E.TABLA = ''' || p_tabla || ''')'
        || ' WHERE RN = 1 AND EVENTO IN (1,2)';
  END SQL_LOTE;

  -- Ultimo evento DELETE: cuenta con la misma pasada analitica (una sola vez).
  FUNCTION SQL_ULTIMOS_DELETE(p_tabla VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    RETURN 'SELECT COUNT(*) FROM (SELECT E.EVENTO,'
        || ' ROW_NUMBER() OVER (PARTITION BY E.ID ORDER BY E.FECHA DESC NULLS LAST, E.ROWID DESC) RN'
        || ' FROM SISMAI.EVENTOS_SINC E WHERE E.TABLA = ''' || p_tabla || ''')'
        || ' WHERE RN = 1 AND EVENTO = 3';
  END SQL_ULTIMOS_DELETE;

  FUNCTION SQL_FUENTE(p_cols VARCHAR2, p_origen VARCHAR2, p_tabla VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    RETURN 'SELECT ' || p_cols || ' FROM SISMAI.' || p_origen || ' X'
        || ' WHERE X.ID IN (' || SQL_LOTE(p_tabla) || ')';
  END SQL_FUENTE;

  FUNCTION SQL_BORRA(p_destino VARCHAR2, p_tabla VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    RETURN 'DELETE FROM TEMP.' || p_destino || ' WHERE ID IN (' || SQL_LOTE(p_tabla) || ')';
  END SQL_BORRA;

  PROCEDURE P(p_txt VARCHAR2) IS
  BEGIN DBMS_OUTPUT.PUT_LINE(p_txt); END P;

  FUNCTION N(p_n NUMBER) RETURN VARCHAR2 IS
  BEGIN RETURN TO_CHAR(p_n, 'FM999999999'); END N;

  ----------------------------------------------------------------------------
  -- [3] Una tabla mapeada: reporte y, si V_EJECUTAR=1, la carga
  ----------------------------------------------------------------------------
  PROCEDURE PROCESAR(p_tabla VARCHAR2) IS
    V_MAPREC     VARCHAR2(200);
    V_ORIGEN     VARCHAR2(30);
    V_DESTINO    VARCHAR2(30);
    V_COLS       VARCHAR2(4000);
    V_FALTAN     VARCHAR2(1000);
    V_LOTE_N     PLS_INTEGER := 0;
    V_FUENTE_N   PLS_INTEGER := 0;
    V_YA_TEMP    PLS_INTEGER := 0;
    V_DEL_N      PLS_INTEGER := 0;
    V_INS_N      PLS_INTEGER := 0;
    V_INI        DATE;
  BEGIN
    V_MAPREC  := V_MAP(p_tabla);
    V_ORIGEN  := SUBSTR(V_MAPREC, 1, INSTR(V_MAPREC, '|') - 1);
    V_DESTINO := SUBSTR(V_MAPREC, INSTR(V_MAPREC, '|') + 1);
    P(CHR(10) || '--- ' || p_tabla || ' -> SISMAI.' || V_ORIGEN
                || ' -> TEMP.' || V_DESTINO || ' ---');

    IF EXISTE('SISMAI', V_ORIGEN) = 0 THEN
      P('  SALTADA: no existe SISMAI.' || V_ORIGEN);
      V_TABLAS_SALTADAS := V_TABLAS_SALTADAS + 1;
      RETURN;
    END IF;
    IF EXISTE('TEMP', V_DESTINO) = 0 THEN
      P('  SALTADA: no existe TEMP.' || V_DESTINO
        || ' (esa tabla la creaba la fase original; este script no hace DDL)');
      V_TABLAS_SALTADAS := V_TABLAS_SALTADAS + 1;
      RETURN;
    END IF;

    V_COLS   := COLS_COMUNES(V_ORIGEN, V_DESTINO);
    V_FALTAN := FALTAN_NOT_NULL(V_ORIGEN, V_DESTINO);
    IF V_COLS IS NULL THEN
      P('  SALTADA: sin columnas en comun entre SISMAI.' || V_ORIGEN
        || ' y TEMP.' || V_DESTINO || ' (o lista > 4000 caracteres)');
      V_TABLAS_SALTADAS := V_TABLAS_SALTADAS + 1;
      RETURN;
    END IF;
    IF V_FALTAN IS NOT NULL THEN
      P('  SALTADA: ' || V_DESTINO || ' exige NOT NULL sin origen: ' || V_FALTAN
        || ' -> el mapeo no es 1:1; no se fuerza. Requiere la logica del original.');
      V_TABLAS_SALTADAS := V_TABLAS_SALTADAS + 1;
      RETURN;
    END IF;

    IF V_EJECUTAR = 0 THEN
      EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM (' || SQL_LOTE(p_tabla) || ')' INTO V_LOTE_N;
      EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM (' || SQL_ULTIMOS_DELETE(p_tabla) || ')' INTO V_DEL_N;
      EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM (' || SQL_FUENTE(V_COLS, V_ORIGEN, p_tabla) || ')'
        INTO V_FUENTE_N;
      EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM TEMP.' || V_DESTINO
        || ' WHERE ID IN (' || SQL_LOTE(p_tabla) || ')' INTO V_YA_TEMP;
      P('  IDs de la cola que viajan      : ' || N(V_LOTE_N));
      P('  filas disponibles en el origen : ' || N(V_FUENTE_N)
        || CASE WHEN V_FUENTE_N < V_LOTE_N
                THEN '   AVISO: ' || N(V_LOTE_N - V_FUENTE_N) || ' IDs de la cola no existen en el origen'
                ELSE '' END);
      P('  ya presentes en TEMP           : ' || N(V_YA_TEMP) || '  (se reemplazarian)');
      P('  cuyo ultimo evento es DELETE(3): ' || N(V_DEL_N) || '  (no viajan)');
      P('  columnas a replicar            : ' || NUM_COLS(V_COLS));
      P('  DRY-RUN: no se escribe nada.');
      V_TABLAS_MAPEADAS := V_TABLAS_MAPEADAS + 1;
      RETURN;
    END IF;

    V_INI := SYSDATE;
    EXECUTE IMMEDIATE SQL_BORRA(V_DESTINO, p_tabla);
    V_DEL_N := SQL%ROWCOUNT;
    EXECUTE IMMEDIATE 'INSERT INTO TEMP.' || V_DESTINO || ' (' || V_COLS || ') '
                     || SQL_FUENTE(V_COLS, V_ORIGEN, p_tabla);
    V_INS_N := SQL%ROWCOUNT;            -- COMMIT pone SQL%ROWCOUNT a 0
    COMMIT;
    V_DEL_TOTAL := V_DEL_TOTAL + V_DEL_N;
    V_INS_TOTAL := V_INS_TOTAL + V_INS_N;
    IF V_LOTE_INICIO IS NULL OR V_INI > V_LOTE_INICIO THEN V_LOTE_INICIO := V_INI; END IF;
    V_TABLAS_MAPEADAS := V_TABLAS_MAPEADAS + 1;
    P('  ESCRITO: borradas ' || N(V_DEL_N) || ', insertadas ' || N(V_INS_N)
      || ', commit OK, LOTE_INICIO ' || TO_CHAR(V_INI, 'YYYY-MM-DD HH24:MI:SS'));
  EXCEPTION WHEN OTHERS THEN
    ROLLBACK;
    P('  ERROR en TEMP.' || V_DESTINO || ': ' || SQLERRM);
    P('  -> ROLLBACK de esta tabla; las ya confirmadas siguen.');
    V_TABLAS_SALTADAS := V_TABLAS_SALTADAS + 1;
  END PROCESAR;

  ----------------------------------------------------------------------------
  -- [5] TABLA de la cola sin mapeo: candidatos por coincidencia de columnas.
  -- La confirmacion es FUNCIONAL: no se deduce de la BD.
  ----------------------------------------------------------------------------
  PROCEDURE SIN_MAPEO(p_tabla VARCHAR2, p_eventos PLS_INTEGER) IS
    V_CAND  VARCHAR2(32767);
    V_N     NUMBER;
  BEGIN
    P(CHR(10) || '--- SIN MAPEO: TABLA=' || p_tabla || ' (' || N(p_eventos) || ' eventos) ---');
    IF EXISTE('SISMAI', p_tabla) = 0 THEN
      P('  No existe SISMAI.' || p_tabla || ': no hay tabla de origen que replicar.');
      RETURN;
    END IF;
    V_CAND := NULL;
    FOR r IN (SELECT TABLE_NAME FROM ALL_TABLES
               WHERE OWNER = 'TEMP' AND TABLE_NAME LIKE 'T!_%' ESCAPE '!'
                 AND TABLE_NAME <> 'T_EVENTOS'
               ORDER BY TABLE_NAME) LOOP
      SELECT COUNT(*) INTO V_N
        FROM ALL_TAB_COLUMNS A, ALL_TAB_COLUMNS B
       WHERE A.OWNER = 'SISMAI' AND A.TABLE_NAME = p_tabla
         AND B.OWNER = 'TEMP'  AND B.TABLE_NAME = r.TABLE_NAME
         AND A.COLUMN_NAME = B.COLUMN_NAME;
      IF V_N > 0 THEN
        V_CAND := V_CAND || RPAD(r.TABLE_NAME, 14) || ' columnas_comunes=' || TO_CHAR(V_N, 'FM999')
                        || CHR(10);
      END IF;
    END LOOP;
    IF V_CAND IS NULL THEN
      P('  Ningun T_ de TEMP comparte columnas con SISMAI.' || p_tabla || '.');
    ELSE
      P('  Candidatos (los confirme el DBA / soporte SIS antes de mapear):');
      P(V_CAND);
    END IF;
  END SIN_MAPEO;

  ----------------------------------------------------------------------------
  -- [4] TEMP.T_EVENTOS, el manifiesto que viaja
  ----------------------------------------------------------------------------
  PROCEDURE MANIFIESTO IS
    V_CNT  PLS_INTEGER := 0;
    V_PREV PLS_INTEGER := 0;
    V_INS  PLS_INTEGER := 0;
    V_DEL  PLS_INTEGER := 0;
    V_COLS VARCHAR2(4000);
  BEGIN
    P(CHR(10) || '--- TEMP.T_EVENTOS (manifiesto) ---');
    EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM SISMAI.EVENTOS_SINC' INTO V_CNT;
    EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM TEMP.T_EVENTOS' INTO V_PREV;

    IF EXISTE('TEMP', 'T_EVENTOS') = 0 THEN
      P('  SALTADA: no existe TEMP.T_EVENTOS (la fase original la creaba).');
      RETURN;
    END IF;
    -- Interseccion de columnas, como en las tablas de datos: el manifiesto se
    -- arma con las columnas que T_EVENTOS y EVENTOS_SINC tengan en comun, sin
    -- depender de nombres como AMS que pueden no existir en una de las dos.
    V_COLS := COLS_COMUNES('EVENTOS_SINC', 'T_EVENTOS');
    IF V_COLS IS NULL OR NUM_COLS(V_COLS) < 3 THEN
      P('  SALTADA: TEMP.T_EVENTOS y SISMAI.EVENTOS_SINC no comparten columnas');
      P('           suficientes (haya: ' || NUM_COLS(V_COLS) || '). Revise el esquema');
      P('           real del manifiesto antes de ejecutar.');
      RETURN;
    END IF;
    P('  columnas del manifiesto: ' || V_COLS);

    IF V_EJECUTAR = 0 THEN
      P('  eventos totales en la cola      : ' || N(V_CNT));
      P('  filas actuales en TEMP.T_EVENTOS: ' || N(V_PREV));
      P('  DRY-RUN: no se escribe nada. Al ejecutar con V_RELLENAR_T_EVENTOS=0:');
      P('    se borran y reinscriben solo las claves replicadas; las filas de');
      P('    corridas previas SE QUEDAN y volverian a viajar en el sobre.');
      P('  Con V_RELLENAR_T_EVENTOS=1: recarga completa del manifiesto (descarta');
      P('    el anterior; solo si el central ya confirmo el sobre previo).');
      RETURN;
    END IF;

    IF V_RELLENAR_T_EVENTOS = 1 THEN
      EXECUTE IMMEDIATE 'DELETE FROM TEMP.T_EVENTOS';
      V_DEL := SQL%ROWCOUNT;
      P('  filas antes de la carga: ' || N(V_PREV));
      P('  DELETE total de T_EVENTOS: ' || N(V_DEL) || ' (manifiesto anterior descartado)');
    END IF;
    FOR i IN 1 .. V_ORD.COUNT LOOP
      EXECUTE IMMEDIATE 'DELETE FROM TEMP.T_EVENTOS WHERE TABLA = :1 AND ID IN ('
                        || SQL_LOTE(V_ORD(i)) || ')' USING V_ORD(i);
      V_DEL := V_DEL + SQL%ROWCOUNT;
      EXECUTE IMMEDIATE
        'INSERT INTO TEMP.T_EVENTOS (' || V_COLS || ') '
        || 'SELECT E.' || REPLACE(V_COLS, ',', ', E.') || ' FROM SISMAI.EVENTOS_SINC E '
        || 'WHERE E.TABLA = :1 AND E.ID IN (' || SQL_LOTE(V_ORD(i)) || ')' USING V_ORD(i);
      V_INS := V_INS + SQL%ROWCOUNT;
    END LOOP;
    COMMIT;
    P('  T_EVENTOS: borradas ' || N(V_DEL) || ', insertadas ' || N(V_INS) || ', commit OK');
  EXCEPTION WHEN OTHERS THEN
    ROLLBACK;
    P('  ERROR en T_EVENTOS: ' || SQLERRM || '  -> ROLLBACK de esta seccion');
  END MANIFIESTO;

BEGIN
  -- ==========================================================================
  -- [0] Aviso y contexto
  -- ==========================================================================
  -- Se carga el mapa: 'ORIGEN|DESTINO' por TABLA de la cola (contrato
  -- validado en backend/registros/data/rutarala_spec.json -> "mapeo").
  V_MAP('CERTIFICADO')        := 'CERTIFICADO|T_CERTMORT';
  V_MAP('CERTNACIMIENTO')      := 'CERTNACIMIENTO|T_CERTNACI';
  V_MAP('DOCUMENTO')           := 'DOCUMENTO|T_DOCUMENT';
  V_MAP('CAUSA_M')             := 'CAUSA_M|T_MORTCAUS';
  V_MAP('CAUSA_MMEDICO')       := 'CAUSA_MMEDICO|T_CAUMMEDI';
  V_MAP('CAUSA_MORBOSAS')      := 'CAUSA_MORBOSAS|T_MCAUMORB';
  V_MAP('CASOSMM')             := 'CASOSMM|T_CASOSMM';
  V_MAP('CASOS_MMI')           := 'CASOS_MMI|T_CASOSMMI';
  V_MAP('RENGLON_CASOSMI')     := 'RENGLON_CASOSMI|T_RCASOSMI';
  V_MAP('RENGLON_EPI15')       := 'RENGLON_EPI15|T_RENEPI15';
  V_MAP('RENGLON_RESUMEN')     := 'RENGLON_RESUMEN|T_RENGRES';
  V_MAP('RENGLONTELE')         := 'RENGLONTELE|T_RENGTELE';
  V_MAP('RESUMEN')             := 'RESUMEN|T_RESUMEN';
  V_MAP('NAC_MADRE')           := 'NAC_MADRE|T_MADRNACI';
  V_MAP('NAC_RNACIDO')         := 'NAC_RNACIDO|T_RNACNACI';
  V_MAP('NAC_ANULADOS')        := 'NAC_ANULADOS|T_RNACANUL';
  V_MAP('MOR_ANULADOS')        := 'MOR_ANULADOS|T_MORTANUL';
  V_MAP('M_FETAL')             := 'M_FETAL|T_MORTFETA';
  V_MAP('M_MADRE')             := 'M_MADRE|T_MORTMADR';
  V_MAP('M_VIOLENTA')          := 'M_VIOLENTA|T_MORTVIOL';
  V_MAP('MONITOR_BASEDEDATOS') := 'MONITOR_BASEDEDATOS|T_MBASED';
  V_MAP('MONITOR_RESPALDO')    := 'MONITOR_RESPALDO|T_MRESPA';
  V_MAP('USUARIOS')            := 'USUARIOS|T_USUARIOS';

  P(CHR(10) || '================================================================');
  P('  replicar_controlado.sql  (PLAN B: requiere autorizacion expresa)');
  P('  ' || TO_CHAR(SYSDATE, 'YYYY-MM-DD HH24:MI:SS')
    || '  usuario=' || SYS_CONTEXT('USERENV', 'SESSION_USER'));
  P('  V_EJECUTAR=' || V_EJECUTAR || '   V_RELLENAR_T_EVENTOS=' || V_RELLENAR_T_EVENTOS);
  IF V_EJECUTAR = 0 THEN
    P('  MODO SEGURO: cero escrituras. Esto es un informe.');
  ELSE
    P('  *** MODO ESCRITURA: escribe en TEMP.T_* y TEMP.T_EVENTOS.');
    P('  *** NO toca SISMAI.EVENTOS_SINC (no trunca, no borra, no actualiza).');
  END IF;
  P('================================================================');

  -- ==========================================================================
  -- [1] Pre-check: tamano de la cola y espacio libre
  -- ==========================================================================
  P(CHR(10) || '--- [1] Pre-check ---');
  EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM SISMAI.EVENTOS_SINC' INTO V_COLA_TOTAL;
  P('  SISMAI.EVENTOS_SINC: ' || N(V_COLA_TOTAL) || ' filas  (NO se modifica en ningun caso)');
  BEGIN
    SELECT SUM(BYTES) / 1048576 INTO V_FREO_MB FROM DBA_FREE_SPACE;
    IF V_FREO_MB < 2048 THEN
      P('  AVISO: solo ' || TO_CHAR(V_FREO_MB, 'FM999999') || ' MB libres. Con menos de 2 GB el');
      P('    INSERT puede fallar por espacio (ORA-0165x). NO ejecutar: amplie TEMP primero.');
    ELSE
      P('  Espacio libre en la BD: ' || TO_CHAR(V_FREO_MB, 'FM999999') || ' MB');
    END IF;
  EXCEPTION WHEN OTHERS THEN
    P('  (espacio libre: sin permiso para DBA_FREE_SPACE: ' || SQLERRM || ')');
  END;

  -- ==========================================================================
  -- [2] La cola por TABLA
  -- ==========================================================================
  P(CHR(10) || '--- [2] La cola por TABLA y evento ---');
  FOR r IN (SELECT TABLA, EVENTO, COUNT(*) AS CANT
              FROM SISMAI.EVENTOS_SINC GROUP BY TABLA, EVENTO ORDER BY TABLA, EVENTO) LOOP
    P('  ' || RPAD(r.TABLA, 22) || ' evento=' || RPAD(TO_CHAR(r.EVENTO), 3) || N(r.CANT));
  END LOOP;

  -- ==========================================================================
  -- [3] Mapeo validado (23 tablas)
  -- ==========================================================================
  P(CHR(10) || '--- [3] Mapeo validado (23 tablas) ---');
  FOR i IN 1 .. V_ORD.COUNT LOOP
    PROCESAR(V_ORD(i));
  END LOOP;

  -- ==========================================================================
  -- [4] Manifiesto T_EVENTOS
  -- ==========================================================================
  MANIFIESTO;

  -- ==========================================================================
  -- [5] Lo que se queda fuera: TABLA de la cola sin mapeo
  -- ==========================================================================
  P(CHR(10) || '--- [5] TABLAS DE LA COLA SIN MAPEO (se quedan fuera) ---');
  FOR r IN (SELECT E.TABLA, COUNT(*) AS CANT
              FROM SISMAI.EVENTOS_SINC E
             WHERE E.TABLA NOT IN
                   ('CERTIFICADO','CERTNACIMIENTO','DOCUMENTO','CAUSA_M','CAUSA_MMEDICO',
                    'CAUSA_MORBOSAS','CASOSMM','CASOS_MMI','RENGLON_CASOSMI','RENGLON_EPI15',
                    'RENGLON_RESUMEN','RENGLONTELE','RESUMEN','NAC_MADRE','NAC_RNACIDO',
                    'NAC_ANULADOS','MOR_ANULADOS','M_FETAL','M_MADRE','M_VIOLENTA',
                    'MONITOR_BASEDEDATOS','MONITOR_RESPALDO','USUARIOS')
             GROUP BY E.TABLA ORDER BY E.TABLA) LOOP
    SIN_MAPEO(r.TABLA, r.CANT);
  END LOOP;

  -- ==========================================================================
  -- [6] Resumen
  -- ==========================================================================
  P(CHR(10) || '--- [6] Resumen ---');
  P('  tablas mapeadas procesadas : ' || V_TABLAS_MAPEADAS || ' de ' || V_ORD.COUNT);
  P('  tablas saltadas            : ' || V_TABLAS_SALTADAS);
  IF V_EJECUTAR = 1 THEN
    P('  filas insertadas en TEMP   : ' || N(V_INS_TOTAL));
    P('  filas borradas de TEMP     : ' || N(V_DEL_TOTAL));
    P('  LOTE_INICIO (maximo)       : ' || TO_CHAR(V_LOTE_INICIO, 'YYYY-MM-DD HH24:MI:SS'));
    P('');
    P('  SIGUIENTE PASO (no lo hace este script): armar el sobre con la');
    P('  aplicacion (RoutLar1 / SistemaTransferencia.exe) y verificar que lleva');
    P('  los 5 archivos, con repllar1.log presente.');
    P('  La cola sigue intacta: NO se trunca. El purgado de la cola se decide');
    P('  aparte, con autorizacion, tras confirmar la recepcion central.');
  ELSE
    P('  DRY-RUN: no se escribio nada en la base.');
    P('  Para ejecutar: revisar este informe, confirmar la recepcion central del');
    P('  sobre anterior, respaldar la cola y poner V_EJECUTAR := 1 (con');
    P('  autorizacion expresa del responsable).');
  END IF;
  P('================================================================');
EXCEPTION WHEN OTHERS THEN
  DBMS_OUTPUT.PUT_LINE('ERROR GENERAL: ' || SQLERRM);
  ROLLBACK;
END;
/
EXIT
