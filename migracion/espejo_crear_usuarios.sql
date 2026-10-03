-- Prepara el Oracle local (contenedor) para el espejo legacy:
-- tablespaces DATOS/DATOS2/INDICE y usuarios SISMAI/HISTORICO/INBDLAR1.
-- Idempotente: si un usuario existe se elimina con CASCADE antes de recrearlo
-- (refresco limpio; los tablespaces se conservan).
--
-- Uso: sqlplus -s system/oracle123@XE @espejo_crear_usuarios.sql
SET ECHO OFF
DECLARE
  PROCEDURE crear_ts(n VARCHAR2, archivo VARCHAR2, tam VARCHAR2) IS
  BEGIN
    EXECUTE IMMEDIATE 'CREATE TABLESPACE ' || n || ' DATAFILE ''' || archivo ||
                      ''' SIZE 100M AUTOEXTEND ON NEXT 100M MAXSIZE ' || tam;
  EXCEPTION WHEN OTHERS THEN
    IF SQLCODE NOT IN (-1543, -1537) THEN RAISE; END IF;
  END;
BEGIN
  crear_ts('DATOS',  '/u01/app/oracle/oradata/XE/datos01.dbf',  '5G');
  crear_ts('DATOS2', '/u01/app/oracle/oradata/XE/datos201.dbf', '1500M');
  crear_ts('INDICE', '/u01/app/oracle/oradata/XE/indice01.dbf', '2G');
END;
/
BEGIN
  FOR r IN (SELECT username FROM dba_users
            WHERE username IN ('SISMAI', 'HISTORICO', 'INBDLAR1')) LOOP
    EXECUTE IMMEDIATE 'DROP USER ' || r.username || ' CASCADE';
  END LOOP;
END;
/
DECLARE
  PROCEDURE crear_usr(n VARCHAR2) IS
  BEGIN
    EXECUTE IMMEDIATE 'CREATE USER ' || n || ' IDENTIFIED BY legacy123 ' ||
      'DEFAULT TABLESPACE USERS ' ||
      'QUOTA UNLIMITED ON USERS QUOTA UNLIMITED ON DATOS ' ||
      'QUOTA UNLIMITED ON DATOS2 QUOTA UNLIMITED ON INDICE';
    EXECUTE IMMEDIATE 'GRANT CONNECT, RESOURCE TO ' || n;
  EXCEPTION WHEN OTHERS THEN
    IF SQLCODE != -1920 THEN RAISE; END IF;
  END;
BEGIN
  crear_usr('SISMAI');
  crear_usr('HISTORICO');
  crear_usr('INBDLAR1');
END;
/
exit
