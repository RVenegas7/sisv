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
SET FEEDBACK OFF
SET ECHO OFF
-- Si una consulta falla a la mitad, SQL*Plus por defecto sigue y deja un CSV
-- truncado que el conteo del manifiesto daria por bueno. Con esto se aborta y el
-- driver borra los CSV parciales en vez de dar por buena una extraction incompleta.
WHENEVER SQLERROR EXIT SQL.SQLCODE

SET TRIMSPOOL ON
SET HEADING OFF
SET TERMOUT OFF
SET COLSEP ';'
SET LINESIZE 32767
-- FEEDBACK OFF y VERIFY OFF (05/10/2026, verificado en vivo): con FEEDBACK ON el
-- "N rows selected." y con VERIFY ON el eco old/new de &DESDE se escriben DENTRO
-- del CSV spoolado, y el CSV deja de ser un CSV. El conteo de filas lo da el
-- manifiesto del driver, que mira el archivo.
SET VERIFY OFF
-- NLS_LANG NO va aqui: es variable de entorno del cliente, no un comando SET de
-- SQL*Plus. La exporta el driver. Se pone AL32UTF8 a proposito para que el SPOOL
-- escriba UTF-8 aunque la base sea WE8MSWIN1252: asi el CSV entra directo en
-- PostgreSQL sin transcribir acentos.

-- Oracle las dobles comillas harian identificador y TO_DATE reventaria.
--
-- Las comillas van ADEMAS dentro de la cadena (05/10/2026, verificado en vivo):
-- SQL*Plus se las quita al sustituir, asi que con
--   DEFINE DESDE = '01/08/2026'     ->  &DESDE se expande a  01/08/2026
-- y TO_DATE(01/08/2026,'DD/MM/YYYY') da ORA-01858. Con las comillas dentro:
--   DEFINE DESDE = "'01/08/2026'"   ->  &DESDE se expande a '01/08/2026'
DEFINE DESDE = "'01/08/2026'"

-- OJO: NO filtrar por "STATUS IS NULL". En este esquema STATUS es 1/0 y nunca es NULL
-- (173.533/173.533 con valor), asi que ese filtro devuelve CERO filas. Se baja el
-- periodo completo y se decide el filtro de anulamiento en la carga, donde si se
-- puede comparar con el criterio que usa el importador.
--
-- Van los datos IDENTIFICATORIOS del fallecido (NOMBRE/APELLIDO/CEDULA): sin ellos la
-- defuncion cargada queda sin nombre y no sirve para nada. Tambien HORAMUERTE,
-- AUTOPSIA y OTROMEDFIRMANTE, que el modelo tiene. Ojo con HESTABLECIMIENTO_OCUR (el
-- establecimiento donde ocurrio la muerte) que es el que usa el importador, distinto
-- del HESTABLECIMIENTO del certificado.
SPOOL __SALIDA__/muerte.csv
SELECT 'ID;FECHA_M;NOMBRE;APELLIDO;CEDULA;SEXO;EDAD;TIPOEDAD;FECHA_N;HORAMUERTE;HESTADOCIVIL;HSITIO_M;HESTABLECIMIENTO;HESTABLECIMIENTO_OCUR;HLOCARESIDENCIA;HPRESENCIAEMBARAZO;HCAUSABASICA;AUTOPSIA;HMEDICOFIRMANTE;OTROMEDFIRMANTE;MFETAL;STATUS;FECHAOPERACION' FROM DUAL;
SELECT  c."ID",
        TO_CHAR(c."FECHA_M",'YYYY-MM-DD HH24:MI:SS') AS FECHA_M,
        c."NOMBRE",
        c."APELLIDO",
        c."CEDULA",
        c."SEXO",
        c."EDAD",
        c."TIPOEDAD",
        TO_CHAR(c."FECHA_N",'YYYY-MM-DD') AS FECHA_N,
        -- HORAMUERTE es VARCHAR2(20), NO es DATE (05/10/2026, verificado con
        -- DUMP: Typ=1, '04:00  PM'). Aplicarle TO_CHAR da ORA-01722 y tumbaba
        -- toda la extraccion. Se baja tal cual, con el AM/PM que trae.
        c."HORAMUERTE",
        c."HESTADOCIVIL",
        c."HSITIO_M",
        c."HESTABLECIMIENTO",
        c."HESTABLECIMIENTO_OCUR",
        c."HLOCARESIDENCIA",
        c."HPRESENCIAEMBARAZO",
        c."HCAUSABASICA",
        c."AUTOPSIA",
        c."HMEDICOFIRMANTE",
        c."OTROMEDFIRMANTE",
        c."MFETAL",
        c."STATUS",
        TO_CHAR(c."FECHAOPERACION",'YYYY-MM-DD HH24:MI:SS') AS FECHAOPERACION
FROM SISMAI."CERTIFICADO" c
WHERE c."FECHA_M" >= TO_DATE(&DESDE,'DD/MM/YYYY')
ORDER BY c."FECHA_M", c."ID";
SPOOL OFF

-- CAUSAS por certificado (hasta 4 renglones por defuncion, ordenados por ORDENLISTA).
-- Sin esto la defuncion llega sin causa: HCAUSABASICA es solo la CLAVE foránea al
-- catalogo CIE10, y el texto de la causa vive aqui.
SPOOL __SALIDA__/causa_m.csv
SELECT 'HCERTIFICADO;HCIE10;ORDENLISTA;DESENFERMEDAD' FROM DUAL;
SELECT  cm."HCERTIFICADO",
        cm."HCIE10",
        cm."ORDENLISTA",
        cm."DESENFERMEDAD"
FROM SISMAI."CAUSA_M" cm
WHERE EXISTS (SELECT 1
              FROM SISMAI."CERTIFICADO" c
              WHERE c."ID" = cm."HCERTIFICADO"
                AND c."FECHA_M" >= TO_DATE(&DESDE,'DD/MM/YYYY'))
ORDER BY cm."HCERTIFICADO", cm."ORDENLISTA";
SPOOL OFF

-- NACIMIENTOS: el filtro va por FECHANACIMIENTO (fecha real del nacimiento), NO por
-- FECHACERTIFICADO. En el espejo hay 1.522 certificados emitidos desde el 01/08 que
-- corresponden a nascimientos de junio y julio (registro tardio): si se filtra por el
-- certificado, el CSV trae datos que ya tenemos y se pierde la verdad del periodo.
-- El importador usa la misma regla (FECHANACIMIENTO y, si falta, FECHACERTIFICADO).
SPOOL __SALIDA__/nacimiento.csv
SELECT 'ID;FECHACERTIFICADO;HESTABLECIMIENTO;CEDULA;NOMBRES;NROPLANILLA;STATUS;FECHAOPERACION' FROM DUAL;
SELECT  n."ID",
        TO_CHAR(n."FECHACERTIFICADO",'YYYY-MM-DD HH24:MI:SS') AS FECHACERTIFICADO,
        n."HESTABLECIMIENTO",
        n."CEDULA",
        n."NOMBRES",
        n."NROPLANILLA",
        n."STATUS",
        TO_CHAR(n."FECHAOPERACION",'YYYY-MM-DD HH24:MI:SS') AS FECHAOPERACION
FROM SISMAI."CERTNACIMIENTO" n
WHERE EXISTS (SELECT 1
              FROM SISMAI."NAC_RNACIDO" r
              WHERE r."HCERTIFICADO" = n."ID"
                AND r."FECHANACIMIENTO" >= TO_DATE(&DESDE,'DD/MM/YYYY'))
ORDER BY n."FECHACERTIFICADO", n."ID";
SPOOL OFF

-- Y al reves: los certificados del periodo que son de nacimientos anteriores. Van en
-- su propio archivo para poder conciliarlos sin mezclarlos con el hueco.
SPOOL __SALIDA__/nacimiento_tardio.csv
SELECT 'ID;FECHACERTIFICADO;HESTABLECIMIENTO;FECHANACIMIENTO;STATUS' FROM DUAL;
SELECT  n."ID",
        TO_CHAR(n."FECHACERTIFICADO",'YYYY-MM-DD HH24:MI:SS') AS FECHACERTIFICADO,
        n."HESTABLECIMIENTO",
        TO_CHAR(r."FECHANACIMIENTO",'YYYY-MM-DD') AS FECHANACIMIENTO,
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
SPOOL __SALIDA__/nac_madre.csv
SELECT 'ID;HCERTIFICADO;CEDULA;NOMBRES;APELLIDOS;EDADM;EDADP;ESTADOCIVIL;FECHANACIMIENTO_MADRE;HRESIDENCIA;NACVIVOS;MUERTESFETALES;HULTIMOGRADO;CONTROLPRENATAL' FROM DUAL;
SELECT  m."ID",
        m."HCERTIFICADO",
        m."CEDULA",
        m."NOMBRES",
        m."APELLIDOS",
        m."EDADM",
        m."EDADP",
        m."ESTADOCIVIL",
        TO_CHAR(m."FECHANACIMIENTO",'YYYY-MM-DD') AS FECHANACIMIENTO_MADRE,
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

SPOOL __SALIDA__/nac_rnacido.csv
SELECT 'ID;HCERTIFICADO;NOMBRES;HSEXO;NACIMIENTO;PESO;TALLA;HTIPOPARTO;HFORMAPARTO;VIVO_MUERTO;SEMANAGESTACION' FROM DUAL;
SELECT  r."ID",
        r."HCERTIFICADO",
        r."NOMBRES",
        r."HSEXO",
        TO_CHAR(r."FECHANACIMIENTO",'YYYY-MM-DD') || ' ' || r."HORA" AS NACIMIENTO,
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
SPOOL __SALIDA__/casosmmi.csv
SELECT 'ID;HDOCUMENTO;NOMBRE;APELLIDO;EDAD;UNIDAD_EDAD;HSEXO;FECHAOCURRENCIA;HRESIDENCIA;FECHAOPERACION' FROM DUAL;
SELECT  m."ID",
        m."HDOCUMENTO",
        m."NOMBRE",
        m."APELLIDO",
        m."EDAD",
        m."UNIDAD_EDAD",
        m."HSEXO",
        TO_CHAR(m."FECHAOCURRENCIA",'YYYY-MM-DD') AS FECHAOCURRENCIA,
        m."HRESIDENCIA",
        TO_CHAR(m."FECHAOPERACION",'YYYY-MM-DD HH24:MI:SS') AS FECHAOPERACION
FROM SISMAI."CASOS_MMI" m
WHERE m."FECHAOCURRENCIA" >= TO_DATE(&DESDE,'DD/MM/YYYY');
SPOOL OFF

SPOOL __SALIDA__/renglon_casosmm.csv
SELECT 'ID;HCASOSMMI;FECHAOPERACION;HESTABLECIMIENTO;HCAUSA_CIE10;HCAUSABAS_CIE10;EDAD_GESTACIONAL;CONTROL_PRENATAL;HFORMAPARTO;PERIODOOCURRENCIA;NUM_PARTOS;HIJOS_NACVIVOS;HIJOS_NACMUERTOS' FROM DUAL;
SELECT  r."ID",
        r."HCASOSMMI",
        TO_CHAR(r."FECHAOPERACION",'YYYY-MM-DD HH24:MI:SS') AS FECHAOPERACION,
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

SPOOL __SALIDA__/renglon_casosmi.csv
SELECT 'ID;HCASOSMMI;FECHAOPERACION;HESTABLECIMIENTO;HCAUSA_CIE10;HCAUSABAS_CIE10;EDAD_GESTACIONAL;CONTROL_PRENATAL;PESO;HNUTRICION;ESTANCIAHOSP' FROM DUAL;
SELECT  r."ID",
        r."HCASOSMMI",
        TO_CHAR(r."FECHAOPERACION",'YYYY-MM-DD HH24:MI:SS') AS FECHAOPERACION,
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
--
-- OJO, 05/10/2026: NO se baja "DESCRIPCION". Es un LONG y trae saltos de linea
-- dentro, que SPOOL escribe tal cual (sin comillas): cada uno parte la fila en
-- dos lineas fisicas y el cargador descarta las que no tienen el mismo numero de
-- columnas que el encabezado. Se perdian ~9 establecimientos del catalogo sin que
-- nada lo dijera. El cargador solo usa ID/NOMBRE/PADRE.
SPOOL __SALIDA__/establecimiento.csv
SELECT 'ID;CODIGO;NOMBRE;PADRE;HTIPO;HLOCALIDAD;STATUS' FROM DUAL;
SELECT e."ID", e."CODIGO", e."NOMBRE", e."PADRE", e."HTIPO", e."HLOCALIDAD", e."STATUS"
FROM SISMAI."ESTABLECIMIENTO" e;
SPOOL OFF

-- Catalogo CIE-10 del legacy. HCAUSABASICA y HCIE10 son CLAVES FORANEAS a
-- SEQ_ID_ACTUAL, no codigos: sin esta tabla la carga no puede traducirlas a un
-- codigo CIE real ni resolver el cross-walk a CIE-11. Trae la descripcion, que
-- es el texto de causa de reserva cuando el certificado no tiene renglon en CAUSA_M.
SPOOL __SALIDA__/cie10_legacy.csv
SELECT 'SEQ_ID_ACTUAL;COD_CLASIFICACION;DES_CLASIFICACIO1;DES_CLASIFICACIO2' FROM DUAL;
SELECT c."SEQ_ID_ACTUAL", c."COD_CLASIFICACION", c."DES_CLASIFICACIO1", c."DES_CLASIFICACIO2"
FROM SISMAI."CIE10" c;
SPOOL OFF

-- ORG_GEOGRAFICA: HLOCARESIDENCIA y HRESIDENCIA apuntan aqui, y el texto trae
-- "Estado X, Municipio Y, Parroquia Z" en un solo campo. Sin esto no se puede
-- sacar el terno estado/municipio/parroquia que usan los filtros del tablero.
SPOOL __SALIDA__/org_geografica.csv
SELECT 'NUM_REGION;NOMBRELARGO' FROM DUAL;
SELECT o."NUM_REGION", o."NOMBRELARGO"
FROM SISMAI."ORG_GEOGRAFICA" o;
SPOOL OFF

EXIT;
