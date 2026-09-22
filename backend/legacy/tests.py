"""Pruebas del mapa de modelos del legacy SISMAI.

Usan una conexión psycopg directa a la BD PostgreSQL migrada (sin tocar las
bases de prueba de Django) y un esquema temporal de juguete para la prueba de
escritura. Nada altera el flujo del sistema: la lectura es contra las tablas
reales (solo SELECT) y la escritura vive en un esquema ``zz_test_legacy`` que
se crea y se elimina dentro de la propia prueba.
"""

import psycopg

from django.test import SimpleTestCase

ESQUEMAS = ("sismai", "inbdlar1", "legacy", "historico")


def _crear_conexion():
    return psycopg.connect(
        host="127.0.0.1",
        port=5436,
        dbname="sis_salud_db",
        user="sis_user",
        password="sis_password",
        connect_timeout=5,
        autocommit=True,
    )


class LegacyMapaTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        try:
            cls.conn = _crear_conexion()
        except psycopg.OperationalError as e:
            raise cls.skipTest(f"BD legacy no disponible: {e}")

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, "conn", None):
            cls.conn.close()
        super().tearDownClass()

    def test_cuatro_esquemas_y_total_de_tablas(self):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT n.nspname, count(*)
                FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = ANY(%s)
                  AND c.relkind IN ('r', 'p', 'v')
                GROUP BY n.nspname ORDER BY 1
                """,
                (list(ESQUEMAS),),
            )
            filas = dict(cur.fetchall())
        self.assertEqual(sorted(filas), sorted(ESQUEMAS))
        self.assertEqual(sum(filas.values()), 430, "Deben quedar 430 tablas/vistas tras la limpieza de colas")

    def test_centro_130659_en_establecimiento(self):
        with self.conn.cursor() as cur:
            cur.execute(
                'SELECT "CODIGO", "NOMBRE", "STATUS" FROM sismai."ESTABLECIMIENTO" WHERE "CODIGO" = %s',
                ("130659",),
            )
            fila = cur.fetchone()
        self.assertIsNotNone(fila, "El centro 130659 debe existir en el legacy migrado")
        self.assertEqual(fila[1], "CMP CAJA DE AGUA")
        self.assertEqual(fila[2], "I", "El centro 130659 debe estar marcado como inactivo")

    def test_usuarios_y_estatus_de_yasminmorb(self):
        with self.conn.cursor() as cur:
            cur.execute('SELECT count(*) FROM sismai."USUARIOS"')
            total = cur.fetchone()[0]
            cur.execute('SELECT "ESTATUS" FROM sismai."USUARIOS" WHERE "LOGIN" = %s', ("YASMINMORB",))
            estatus = cur.fetchone()[0]
        self.assertGreaterEqual(total, 800)
        self.assertEqual(estatus, 2, "YASMINMORB está en ESTATUS=2 (activo/normal), no bloqueada en la BD")

    def test_models_legacy_coincide_con_el_esquema(self):
        from legacy import models_legacy as m

        tablas = set()
        for cls in m.__all__:
            modelo = getattr(m, cls)
            tablas.add(modelo._meta.db_table)
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT n.nspname, c.relname
                FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = ANY(%s) AND c.relkind IN ('r', 'p', 'v')
                """,
                (list(ESQUEMAS),),
            )
            reales = {f'"{s}"."{t}"' for s, t in cur.fetchall()}
        self.assertEqual(len(m.__all__), 430)
        self.assertEqual(tablas, reales, "El mapa debe cubrir exactamente las tablas/vistas migradas")

    def test_lectura_y_escritura_en_esquema_temporal(self):
        with self.conn.cursor() as cur:
            cur.execute('DROP SCHEMA IF EXISTS "zz_test_legacy" CASCADE')
            cur.execute('CREATE SCHEMA "zz_test_legacy"')
            try:
                cur.execute(
                    'CREATE TABLE "zz_test_legacy"."zz_establecimiento" ('
                    '"ID" numeric, "CODIGO" varchar(20), "NOMBRE" varchar(150),'
                    '"STATUS" varchar(1), "FECHAOPERACION" timestamp)'
                )
                cur.execute(
                    'INSERT INTO "zz_test_legacy"."zz_establecimiento" '
                    '("ID", "CODIGO", "NOMBRE", "STATUS", "FECHAOPERACION") VALUES '
                    "(%s, %s, %s, %s, %s)",
                    (1, "999999", "PRUEBA LECTURA/ESCRITURA", "A", "2026-01-01 00:00:00"),
                )
                cur.execute('SELECT count(*) FROM "zz_test_legacy"."zz_establecimiento" WHERE "CODIGO" = %s', ("999999",))
                n = cur.fetchone()[0]
                self.assertEqual(n, 1, "La escritura debe poder leerse en el esquema temporal")
            finally:
                cur.execute('DROP SCHEMA IF EXISTS "zz_test_legacy" CASCADE')