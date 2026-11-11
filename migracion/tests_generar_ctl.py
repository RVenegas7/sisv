#!/usr/bin/env python3
# =============================================================================
#  tests_generar_ctl.py — pruebas del generador de .ctl de SQL*Loader.
#
#  Se corre directo (sin Django, sin Oracle): solo valida la lógica pura del
#  generador (parseo del DDL, detección de `|` en texto, máscaras de fecha,
#  FILLER, columnas omitidas y salto de T_CERTNACI).
#
#    ./.venv/bin/python migracion/tests_generar_ctl.py
#    ./.venv/bin/python -m unittest migracion.tests_generar_ctl -v   (con cwd=raíz)
# =============================================================================
import os
import sys
import unittest

# Importar el módulo (no es un paquete: se agrega su directorio al path).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_ctl_sqlldr as g  # noqa: E402

DDL_MIN = '''
  CREATE TABLE "TEMP"."T_PRUEBA"
   ( "ID" NUMBER NOT NULL ENABLE,
 "NOMBRE" VARCHAR2(100),
 "FECHA_M" DATE,
 "CODIGO" CHAR(1) NOT NULL ENABLE
   ) SEGMENT CREATION IMMEDIATE
  PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 NOCOMPRESS LOGGING
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645)
  TABLESPACE "USERS"
;
'''


class ParsearDDLTests(unittest.TestCase):
    def test_parsea_tabla_columnas_y_not_null(self):
        ddl = g.parsear_ddl(DDL_MIN)
        self.assertIn("T_PRUEBA", ddl)
        orden, mapa = ddl["T_PRUEBA"]
        self.assertEqual(orden, ["ID", "NOMBRE", "FECHA_M", "CODIGO"])
        self.assertEqual(mapa["ID"], ("NUMBER", True))
        self.assertEqual(mapa["NOMBRE"], ("VARCHAR2(100)", False))
        self.assertEqual(mapa["FECHA_M"], ("DATE", False))
        self.assertEqual(mapa["CODIGO"], ("CHAR(1)", True))


class LineasDatosTests(unittest.TestCase):
    def test_detecta_pipe_en_texto(self):
        # 3 columnas esperadas; la fila trae 4 campos (un `|` dentro de un texto).
        with self.assertRaises(g.ErrorCSV):
            g._lineas_datos("a|b|c|d\n", "T_X", 3)

    def test_lineas_limpias_y_campos_vacios(self):
        lineas = g._lineas_datos("a||c\n", "T_X", 3)
        self.assertEqual(lineas, [["a", "", "c"]])

    def test_ignora_ultima_linea_vacia(self):
        lineas = g._lineas_datos("a|b\n", "T_X", 2)
        self.assertEqual(len(lineas), 1)


class MascaraFechaTests(unittest.TestCase):
    def test_solo_fecha(self):
        self.assertEqual(g._mascara_fecha(["2026-11-04"]), "YYYY-MM-DD")

    def test_fecha_hora(self):
        self.assertEqual(g._mascara_fecha(["2026-11-04 12:34:56"]), "YYYY-MM-DD HH24:MI:SS")

    def test_mezcla_da_none(self):
        self.assertIsNone(g._mascara_fecha(["2026-11-04", "2026-11-04 12:34:56"]))

    def test_vacio_da_mascara_por_defecto(self):
        self.assertEqual(g._mascara_fecha([]), "YYYY-MM-DD HH24:MI:SS")

    def test_valor_no_fecha_da_none(self):
        self.assertIsNone(g._mascara_fecha(["no-es-fecha"]))


class GenerarCtlTests(unittest.TestCase):
    def test_tabla_normal_con_fecha_y_nullif(self):
        orden = ["ID", "NOMBRE", "FECHA_M", "CODIGO"]
        mapa = {"ID": ("NUMBER", True), "NOMBRE": ("VARCHAR2(100)", False),
                "FECHA_M": ("DATE", False), "CODIGO": ("CHAR(1)", True)}
        ctl = g.generar_ctl("T_PRUEBA", orden, orden, mapa,
                            {"FECHA_M": "YYYY-MM-DD HH24:MI:SS"},
                            "truncate", "UTF8", con_cabecera=True)
        self.assertIn("OPTIONS (SKIP=1)", ctl)
        self.assertIn('"FECHA_M" DATE "YYYY-MM-DD HH24:MI:SS" NULLIF "FECHA_M" = BLANKS', ctl)
        self.assertIn('"NOMBRE" NULLIF "NOMBRE" = BLANKS', ctl)
        self.assertIn('"ID"', ctl)            # NOT NULL sin NULLIF
        self.assertIn('"CODIGO"', ctl)        # NOT NULL sin NULLIF
        self.assertIn("FIELDS TERMINATED BY '|'", ctl)
        self.assertIn("TRUNCATE", ctl)

    def test_filler_para_columna_sin_destino(self):
        # columna del CSV que NO está en TEMP -> FILLER
        orden_ddl = ["ID", "NOMBRE"]
        mapa = {"ID": ("NUMBER", True), "NOMBRE": ("VARCHAR2(100)", False)}
        cols_csv = ["ID", "NOMBRE", "VALSEXO"]
        ctl = g.generar_ctl("T_PRUEBA", cols_csv, orden_ddl, mapa,
                            {}, "truncate", "UTF8", con_cabecera=True)
        self.assertIn('"VALSEXO" FILLER', ctl)

    def test_columna_not_null_ausente_del_csv_falla(self):
        # columna NOT NULL del DDL que el CSV no trae -> debe fallar fuerte.
        orden_ddl = ["ID", "NOMBRE"]
        mapa = {"ID": ("NUMBER", True), "NOMBRE": ("VARCHAR2(100)", True)}
        with self.assertRaises(SystemExit):
            g.generar_ctl("T_PRUEBA", ["ID"], orden_ddl, mapa, {},
                          "truncate", "UTF8", con_cabecera=True)

    def test_t_eventos_sin_cabecera_y_columnas_faltantes_nullable(self):
        # T_EVENTOS: el CSV trae 4 de 6 columnas; STATUS/AMS (nullable) quedan NULL.
        orden_ddl = ["TABLA", "EVENTO", "FECHA", "ID", "STATUS", "AMS"]
        mapa = {"TABLA": ("VARCHAR2(100)", True), "EVENTO": ("CHAR(1)", True),
                "FECHA": ("DATE", False), "ID": ("FLOAT(126)", True),
                "STATUS": ("NUMBER(1,0)", False), "AMS": ("VARCHAR2(12)", False)}
        cols_csv = ["TABLA", "EVENTO", "FECHA", "ID"]
        ctl = g.generar_ctl("T_EVENTOS", cols_csv, orden_ddl, mapa,
                            {"FECHA": "YYYY-MM-DD HH24:MI:SS"},
                            "truncate", "UTF8", con_cabecera=False)
        self.assertIn("OPTIONS (SKIP=0)", ctl)
        self.assertNotIn('"STATUS"', ctl)
        self.assertNotIn('"AMS"', ctl)

    def test_modo_replace(self):
        orden = ["ID"]
        mapa = {"ID": ("NUMBER", True)}
        ctl = g.generar_ctl("T_PRUEBA", orden, orden, mapa, {},
                            "replace", "UTF8", con_cabecera=False)
        self.assertIn("REPLACE", ctl)
        self.assertNotIn("TRUNCATE", ctl)


if __name__ == "__main__":
    unittest.main(verbosity=2)
