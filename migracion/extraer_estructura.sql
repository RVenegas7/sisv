REM ============================================================================
REM Extracción de estructura SIS Oracle 10g - ejecutar como usuario oracle
REM   sqlplus -S / as sysdba @extraer_estructura.sql
REM Salida: 1_tablas.csv, 2_columnas.csv, 3_restricciones.csv, 4_ddl.sql, 5_secuencias.sql
REM Verificar NLS_LANG antes: WE8MSWIN1252 (o AL32UTF8). Los DDL se exportan con
REM caracteres del juego nacional; revisar encodings al importar en MariaDB.
REM ============================================================================
REM NO migrar infraestructura de replicación (colas de sincronización sin valor):
REM   EVENTOS_SINC, EVENTOS_DBLINK, EVENTOS_RESP (ver Informe_BD_SIS_LAR1_2026-09-18.md,
REM   sección 5.1-5.2). Estas tablas crecen ~33.281 filas/mes en el origen y el 27-08-2026
REM acumularon 3,36 M de filas nunca procesadas. Tampoco el ruido de Oracle Enterprise
REM Manager (SM*, SMP_*) ni las internas de explain plan (PLAN_TABLE, PLAN_TABLE2).
REM ============================================================================
SET PAGESIZE 0
SET LONG 2000000
SET LINESIZE 4000
SET TRIMSPOOL ON
SET FEEDBACK OFF
SET ECHO OFF
SET TERMOUT OFF
SET HEADING OFF

SPOOL 1_tablas.csv
SELECT table_name || ';' || NVL(num_rows, 0) || ';' ||
       (SELECT COUNT(*) FROM user_tab_columns c WHERE c.table_name = t.table_name)
FROM user_tables t
WHERE table_name NOT IN ('EVENTOS_SINC', 'EVENTOS_DBLINK', 'EVENTOS_RESP', 'PLAN_TABLE', 'PLAN_TABLE2')
  AND NOT (table_name LIKE 'SM%' OR table_name LIKE 'SMP_%')
ORDER BY table_name;
SPOOL OFF

SPOOL 2_columnas.csv
SELECT table_name || ';' || column_name || ';' || data_type || ';' ||
       NVL(data_length, 0) || ';' || NVL(data_precision, 0)
FROM user_tab_columns
ORDER BY table_name, column_id;
SPOOL OFF

SPOOL 3_restricciones.csv
SELECT uc.table_name || ';' || uc.constraint_type || ';' || uc.constraint_name ||
       ';' || NVL(ucc.column_name, '')
FROM user_constraints uc
LEFT JOIN user_cons_columns ucc ON uc.constraint_name = ucc.constraint_name
WHERE uc.constraint_type IN ('P', 'R')
ORDER BY uc.table_name;
SPOOL OFF

SPOOL 4_ddl.sql
SELECT DBMS_METADATA.GET_DDL('TABLE', table_name, USER) FROM user_tables;
SELECT DBMS_METADATA.GET_DDL('CONSTRAINT', constraint_name, USER)
FROM user_constraints WHERE constraint_type IN ('P', 'R')
ORDER BY table_name;
SPOOL OFF

SPOOL 5_secuencias.sql
SELECT 'CREATE SEQUENCE ' || sequence_name || ' START WITH ' || last_number || ';'
FROM user_sequences;
SPOOL OFF

EXIT;