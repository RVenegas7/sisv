-- =============================================================================
-- Fase 1 de la ventana del 29/09/2026 (§17.17): recuperar el hueco de MM/MN.
--
-- POR QUE ESTAS TABLAS
--   La captura se cort�� el 02/08/2026 (PENDIENTES §17.21) y la oficina aclaro que
--   el envio semanal se sigue emitiendo todos los martes: los datos EXISTEN en el
--   sistema del centro, nunca llegaron al espejo. Este script los baja del vivo.
--
-- ALCANCE
--   Solo el periodo roto: FECHA_M >= 01/08/2026 (la semana 31 abre el domingo
--   02/08 bajo la convencion epidemiologica, PENDIENTES §17.19). Se empieza el
--   01/08 a proposito, para que ese dia de solape con el espejo sirva de control:
--   si el CSV trae los mismos conteos que el espejo, el corte del CSV esta bien.
--
-- REGLAS (no negociables)
--   * SOLO SELECT + SPOOL. Ni INSERT, ni TRUNCATE, ni DROP, ni DELETE.
--   * NO se toca SISMAI.EVENTOS_SINC ni ninguna tabla de la cola de sincronizacion.
--   * Se corre con el respaldo de las 13:00 ya terminado.
--   * Se exportan columnas explicitas, no SELECT *: en NAC_MADRE.HISTORIACLINICA y
--     NAC_RNACIDO.HISTORIACLINICA hay texto libre con saltos de linea y comas que
--     romperian el CSV.
--
-- USO:   sqlplus -s / as sysdbo @extraer_mm_mn_roto.sql <directorio_salida>
--        (el driver es extraer_mm_mn_roto.sh, que ademas arma el manifiesto)
-- =============================================================================

SET PAGESIZE 0
SET FEEDBACK ON
SET ECHO OFF
SET TRIMSPOOL ON
SET HEADING OFF
SET TERMOUT OFF
SET COLSEP ';'
SET LINESIZE 32767
SET NLS_LANG=SPANISH_SPAIN.AL32UTF8

-- &1 = directorio de salida (lo pasa el shell). &DESDE con comillas simples: en
-- Oracle las dobles comillas harian identificador y TO_DATE reventaria.
DEFINE OUT  = '&1'
DEFINE DESDE = '01/08/2026'

-- OJO: NO filtrar por "STATUS IS NULL". En este esquema STATUS es 1/0 y nunca es NULL
-- (173.533/173.533 con valor), asi que ese filtro devuelve CERO filas. Se baja el
-- periodo completo y se decide el filtro de anulamiento en la carga, donde si se
-- puede comparar con el criterio que usa el importador.
SPOOL &OUT/muerte.csv
SELECT  c."ID",
        TO_CHAR(c."FECHA_M",'YYYY-MM-DD HH24:MI:SS'),
        c."HESTABLECIMIENTO",
        c."SEXO",
        c."EDAD",
        c."TIPOEDAD",
        TO_CHAR(c."FECHA_N",'YYYY-MM-DD'),
        c."HESTADOCIVIL",
        c."HSITIO_M",
        c."HLOCARESIDENCIA",
        c."HPRESENCIAEMBARAZO",
        c."HCAUSABASICA",
        c."HMEDICOFIRMANTE",
        c."MFETAL",
        c."STATUS",
        TO_CHAR(c."FECHAOPERACION",'YYYY-MM-DD HH24:MI:SS')
FROM SISMAI."CERTIFICADO" c
WHERE c."FECHA_M" >= TO_DATE(&DESDE,'DD/MM/YYYY')
ORDER BY c."FECHA_M", c."ID";
SPOOL OFF

-- NACIMIENTOS: el filtro va por FECHANACIMIENTO (fecha real del nacimiento), NO por
-- FECHACERTIFICADO. En el espejo hay 1.522 certificados emitidos desde el 01/08 que
-- corresponden a nascimientos de junio y julio (registro tardio): si se filtra por el
-- certificado, el CSV trae datos que ya tenemos y se pierde la verdad del periodo.
-- El importador usa la misma regla (FECHANACIMIENTO y, si falta, FECHACERTIFICADO).
SPOOL &OUT/nacimiento.csv
SELECT  n."ID",
        TO_CHAR(n."FECHACERTIFICADO",'YYYY-MM-DD HH24:MI:SS'),
        n."HESTABLECIMIENTO",
        n."CEDULA",
        n."NOMBRES",
        n."NROPLANILLA",
        n."STATUS",
        TO_CHAR(n."FECHAOPERACION",'YYYY-MM-DD HH24:MI:SS')
FROM SISMAI."CERTNACIMIENTO" n
WHERE EXISTS (SELECT 1
              FROM SISMAI."NAC_RNACIDO" r
              WHERE r."HCERTIFICADO" = n."ID"
                AND r."FECHANACIMIENTO" >= TO_DATE(&DESDE,'DD/MM/YYYY'))
ORDER BY n."FECHACERTIFICADO", n."ID";
SPOOL OFF

-- Y al reves: los certificados del periodo que son de nacimientos anteriores. Van en
-- su propio archivo para poder conciliarlos sin mezclarlos con el hueco.
SPOOL &OUT/nacimiento_tardio.csv
SELECT  n."ID",
        TO_CHAR(n."FECHACERTIFICADO",'YYYY-MM-DD HH24:MI:SS'),
        n."HESTABLECIMIENTO",
        TO_CHAR(r."FECHANACIMIENTO",'YYYY-MM-DD') AS fecha_real_nacimiento,
        n."STATUS"
FROM SISMAI."CERTNACIMIENTO" n
JOIN SISMAI."NAC_RNACIDO" r ON r."HCERTIFICADO" = n."ID"
WHERE n."FECHACERTIFICADO" >= TO_DATE(&DESDE,'DD/MM/YYYY')
  AND r."FECHANACIMIENTO" < TO_DATE(&DESDE,'DD/MM/YYYY')
ORDER BY n."FECHACERTIFICADO", n."ID";
SPOOL OFF

-- Madre y recien nacido, arrastrados por su certificado para no traer las 439.220
-- filas historicas. VIVO_MUERTO es lo que permite identificar al recien nacido
-- que fallece (el insumo del indicador MN).
SPOOL &OUT/nac_madre.csv
SELECT  m."ID",
        m."HCERTIFICADO",
        m."CEDULA",
        m."NOMBRES",
        m."APELLIDOS",
        m."EDADM",
        m."EDADP",
        TO_CHAR(m."FECHANACIMIENTO",'YYYY-MM-DD'),
        m."HRESIDENCIA",
        m."NACVIVOS",
        m."MUERTESFETALES",
        m."HULTIMOGRADO",
        m."CONTROLPRENATAL"
FROM SISMAI."NAC_MADRE" m
WHERE EXISTS (SELECT 1
              FROM SISMAI."NAC_RNACIDO" r
              WHERE r."HCERTIFICADO" = m."HCERTIFICADO"
                AND r."FECHANACIMIENTO" >= TO_DATE(&DESDE,'DD/MM/YYYY'));
SPOOL OFF

SPOOL &OUT/nac_rnacido.csv
SELECT  r."ID",
        r."HCERTIFICADO",
        r."NOMBRES",
        r."HSEXO",
        TO_CHAR(r."FECHANACIMIENTO",'YYYY-MM-DD') || ' ' || r."HORA",
        r."PESO",
        r."TALLA",
        r."HTIPOPARTO",
        r."HFORMAPARTO",
        r."VIVO_MUERTO",
        r."SEMANAGESTACION"
FROM SISMAI."NAC_RNACIDO" r
WHERE r."FECHANACIMIENTO" >= TO_DATE(&DESDE,'DD/MM/YYYY')
ORDER BY r."FECHANACIMIENTO", r."ID";
SPOOL OFF

-- Muerte materna: cabecera e historico. §17.22 aclaro que RENGLON_CASOSMM.HCASOSMMI
-- es FK a CASOS_MMI, no un id corrido, asi que se bajan las dos mitades.
SPOOL &OUT/casosmmi.csv
SELECT  m."ID",
        m."HDOCUMENTO",
        m."NOMBRE",
        m."APELLIDO",
        m."EDAD",
        m."UNIDAD_EDAD",
        m."HSEXO",
        TO_CHAR(m."FECHAOCURRENCIA",'YYYY-MM-DD'),
        m."HRESIDENCIA",
        TO_CHAR(m."FECHAOPERACION",'YYYY-MM-DD HH24:MI:SS')
FROM SISMAI."CASOS_MMI" m
WHERE m."FECHAOCURRENCIA" >= TO_DATE(&DESDE,'DD/MM/YYYY');
SPOOL OFF

SPOOL &OUT/renglon_casosmm.csv
SELECT  r."ID",
        r."HCASOSMMI",
        TO_CHAR(r."FECHAOPERACION",'YYYY-MM-DD HH24:MI:SS'),
        r."HESTABLECIMIENTO",
        r."HCAUSA_CIE10",
        r."HCAUSABAS_CIE10",
        r."EDAD_GESTACIONAL",
        r."CONTROL_PRENATAL",
        r."HFORMAPARTO",
        r."PERIODOOCURRENCIA",
        r."NUM_PARTOS",
        r."HIJOS_NACVIVOS",
        r."HIJOS_NACMUERTOS"
FROM SISMAI."RENGLON_CASOSMM" r
JOIN SISMAI."CASOS_MMI" cab ON cab."ID" = r."HCASOSMMI"
WHERE cab."FECHAOCURRENCIA" >= TO_DATE(&DESDE,'DD/MM/YYYY')
ORDER BY cab."FECHAOCURRENCIA", r."ID";
SPOOL OFF

-- Muerte neonatal caso por caso. NO existe tabla CASOS_MI: RENGLON_CASOSMI tambien
-- cuelga de CASOS_MMI (10.004 de 10.005 con match), asi que la cabecera se baja una
-- sola vez, en casosmmi.csv, y aca solo va el renglon.

SPOOL &OUT/renglon_casosmi.csv
SELECT  r."ID",
        r."HCASOSMMI",
        TO_CHAR(r."FECHAOPERACION",'YYYY-MM-DD HH24:MI:SS'),
        r."HESTABLECIMIENTO",
        r."HCAUSA_CIE10",
        r."HCAUSABAS_CIE10",
        r."EDAD_GESTACIONAL",
        r."CONTROL_PRENATAL",
        r."PESO",
        r."HNUTRICION",
        r."ESTANCIAHOSP"
FROM SISMAI."RENGLON_CASOSMI" r
JOIN SISMAI."CASOS_MMI" cab ON cab."ID" = r."HCASOSMMI"
WHERE cab."FECHAOCURRENCIA" >= TO_DATE(&DESDE,'DD/MM/YYYY')
ORDER BY cab."FECHAOCURRENCIA", r."ID";
SPOOL OFF

-- Resolucion de establecimiento (todo el catalogo, son pocas filas).
-- La PK es "ID" (no IDESTABLECIMIENTO: esa no existe en ESTABLECIMIENTO).
SPOOL &OUT/establecimiento.csv
SELECT e."ID", e."CODIGO", e."DESCRIPCION", e."HTIPO", e."HLOCALIDAD", e."STATUS"
FROM SISMAI."ESTABLECIMIENTO" e;
SPOOL OFF

EXIT;
