-- Diagnostico: la captura de mortalidad se colapso entre 2019-06 y 2021-07
-- (defunciones) y entre 2019-10 y 2021-11 (nacimientos). En el espejo hay 3.083
-- certificados en los 21 meses de 2019-06 a 2021-02, frente a 22.779 en los 21
-- meses previos: faltan ~19.700.
--
-- LA PREGUNTA: ¿el Oracle de ORIGEN tiene esos certificados y el espejo no los
-- trajo, o nunca se capturaron? Si el origen tiene mas, hay recuperacion
-- (igual que la ventana de agosto-septiembre 2026). Si no, la serie 2019-2021
-- esta incompleta de forma permanente y hay que decirlo al publicar.
--
-- SOLO LECTURA: un SELECT con conteo por mes. No escribe en SISMAI, ni en TEMP,
-- ni en la cola de EVENTOS_SINC.
--
-- Uso:  sqlplus -s usuario/clave@lar1 @diagnostico_hueco_2019_2021.sql 01/01/2018 01/01/2022
-- Los dos argumentos rellenan &1 y &2. La salida va por stdout, separada con '|'.
SET HEADING OFF
SET FEEDBACK OFF
SET PAGESIZE 0
SET LINESIZE 200
SET TRIMSPOOL ON
SET VERIFY OFF

PROMPT
PROMPT === BLOQUE MESES: certificados de muerte por mes ===
SELECT 'MESES' AS bloque,
       TO_CHAR(TRUNC("FECHA_M", 'MM'), 'YYYY-MM') AS mes,
       COUNT(*) AS n
FROM SISMAI.CERTIFICADO
WHERE "FECHA_M" IS NOT NULL
  AND "FECHA_M" >= TO_DATE('&1', 'DD/MM/YYYY')
  AND "FECHA_M" <  TO_DATE('&2', 'DD/MM/YYYY')
GROUP BY TRUNC("FECHA_M", 'MM')
ORDER BY 2;

PROMPT
PROMPT === BLOQUE NACIMIENTOS: por mes ===
-- El importador filtra NAC_RNACIDO.FECHANACIMIENTO, NO
-- CERTNACIMIENTO.FECHACERTIFICADO: este ultimo concentra los certificados
-- tardios y daria una serie distinta a la que tiene SISV.
SELECT 'NACIMIENTOS' AS bloque,
       TO_CHAR(TRUNC("FECHANACIMIENTO", 'MM'), 'YYYY-MM') AS mes,
       COUNT(*) AS n
FROM SISMAI.NAC_RNACIDO
WHERE "FECHANACIMIENTO" IS NOT NULL
  AND "FECHANACIMIENTO" >= TO_DATE('&1', 'DD/MM/YYYY')
  AND "FECHANACIMIENTO" <  TO_DATE('&2', 'DD/MM/YYYY')
GROUP BY TRUNC("FECHANACIMIENTO", 'MM')
ORDER BY 2;

PROMPT
PROMPT === BLOQUE ULTIMO: hasta donde llego la captura en el origen ===
SELECT 'ULTIMO_DEFUNCION' AS bloque, TO_CHAR(MAX("FECHA_M"), 'YYYY-MM-DD') AS mes, 0 AS n
FROM SISMAI.CERTIFICADO
UNION ALL
SELECT 'ULTIMO_NACIMIENTO', TO_CHAR(MAX("FECHANACIMIENTO"), 'YYYY-MM-DD'), 0
FROM SISMAI.NAC_RNACIDO;

EXIT
