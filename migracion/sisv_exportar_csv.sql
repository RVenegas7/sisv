-- Exportador CSV generico Oracle -> archivo (semicolon, comillas dobles, UTF-8)
-- NULL = campo vacio SIN comillas; el cargador usa NULL '' en COPY.
CREATE OR REPLACE PROCEDURE SYSTEM.SISV_EXPORTAR_CSV(
  p_owner IN VARCHAR2,
  p_table IN VARCHAR2,
  p_dir   IN VARCHAR2,
  p_file  IN VARCHAR2,
  p_sep   IN VARCHAR2 DEFAULT ';'
) AUTHID CURRENT_USER AS
  c        INTEGER;
  ncol     INTEGER;
  desc_t   DBMS_SQL.DESC_TAB;
  f        UTL_FILE.FILE_TYPE;
  v        VARCHAR2(32767);
  d        DATE;
  line     VARCHAR2(32767);
  vn       VARCHAR2(32767);
  nrow     INTEGER;
BEGIN
  c := DBMS_SQL.OPEN_CURSOR;
  DBMS_SQL.PARSE(c, 'SELECT * FROM "'||p_owner||'"."'||p_table||'"', DBMS_SQL.NATIVE);
  DBMS_SQL.DESCRIBE_COLUMNS(c, ncol, desc_t);
  FOR i IN 1..ncol LOOP
    IF desc_t(i).col_type = 12 THEN
      DBMS_SQL.DEFINE_COLUMN(c, i, d);
    ELSE
      DBMS_SQL.DEFINE_COLUMN(c, i, v, 32767);
    END IF;
  END LOOP;

  nrow := DBMS_SQL.EXECUTE(c);

  f := UTL_FILE.FOPEN(p_dir, p_file, 'W', 32767);

  line := NULL;
  FOR i IN 1..ncol LOOP
    IF i > 1 THEN line := line || p_sep; END IF;
    line := line || '"' || REPLACE(desc_t(i).col_name, '"', '""') || '"';
  END LOOP;
  UTL_FILE.PUT_LINE(f, line);

  LOOP
    nrow := DBMS_SQL.FETCH_ROWS(c);
    EXIT WHEN nrow = 0;
    line := NULL;
    FOR i IN 1..ncol LOOP
      vn := NULL;
      IF desc_t(i).col_type = 12 THEN
        d := NULL;
        DBMS_SQL.COLUMN_VALUE(c, i, d);
        vn := TO_CHAR(d, 'YYYY-MM-DD HH24:MI:SS');
      ELSE
        v := NULL;
        DBMS_SQL.COLUMN_VALUE(c, i, v);
        vn := v;
      END IF;
      IF i > 1 THEN line := line || p_sep; END IF;
      IF vn IS NOT NULL THEN
        line := line || '"' || REPLACE(vn, '"', '""') || '"';
      END IF;
    END LOOP;
    UTL_FILE.PUT_LINE(f, line);
  END LOOP;

  DBMS_SQL.CLOSE_CURSOR(c);
  UTL_FILE.FCLOSE(f);
EXCEPTION WHEN OTHERS THEN
  BEGIN UTL_FILE.FCLOSE(f); EXCEPTION WHEN OTHERS THEN NULL; END;
  BEGIN DBMS_SQL.CLOSE_CURSOR(c); EXCEPTION WHEN OTHERS THEN NULL; END;
  RAISE;
END;
/
