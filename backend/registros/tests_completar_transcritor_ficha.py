"""Pruebas del backfill de fichas legacy: transcriptor + subtipo MM/MI/VIOLENTA (§46).

En sqlite no existe el esquema espejo `sismai`, así que se interceptan solo las consultas
que lo mencionan (mismo patrón que ``tests_completar_transcritor.py``).
"""
import io
from unittest.mock import patch

from django.core.management import call_command
from django.db.backends.utils import CursorWrapper
from django.test import TestCase

from registros.management.commands import completar_transcritor_ficha as comando


class _EspejoFake:
    def __init__(self, mmi=0, violenta=0, actualizados=(0, 0), logins=(), resumen=()):
        self.valores = {"count_mmi": mmi, "count_violenta": violenta,
                        "upd_mmi": actualizados[0], "upd_violenta": actualizados[1]}
        self.logins = list(logins)
        self.resumen = list(resumen)
        self.sql = []

    def _tipo(self, sql):
        limpio = sql.lstrip()
        if limpio.startswith("UPDATE"):
            return "upd_violenta" if 'M_VIOLENTA" m' in sql else "upd_mmi"
        if "COALESCE(NULLIF(subtipo_legacy" in sql:
            return "resumen"
        if "sismai." not in sql:
            return None  # tablas propias: se dejan a sqlite
        if "GROUP BY" in sql and "UNION ALL" in sql:
            return "logins"
        if limpio.startswith("SELECT count(*)"):
            return "count_violenta" if 'M_VIOLENTA"' in sql else "count_mmi"
        return None

    def __enter__(self):
        self._execute = CursorWrapper.execute

        def execute(cur, sql, params=None):
            if self._tipo(sql):
                self.sql.append(sql)
                return None
            return self._execute(cur, sql, params)

        def fetchone(cur, *a, **kw):
            clave = self._tipo(self.sql[-1]) if self.sql else None
            if clave in self.valores:
                return (self.valores[clave],)
            return cur.cursor.fetchone(*a, **kw)

        def fetchall(cur, *a, **kw):
            clave = self._tipo(self.sql[-1]) if self.sql else None
            if clave == "logins":
                return self.logins
            if clave == "resumen":
                return self.resumen
            return cur.cursor.fetchall(*a, **kw)

        def rowcount(cur):
            clave = self._tipo(self.sql[-1]) if self.sql else None
            if clave in self.valores:
                return self.valores[clave]
            return cur.cursor.rowcount

        self._patches = [
            patch.object(CursorWrapper, "execute", execute),
            patch.object(CursorWrapper, "fetchone", fetchone, create=True),
            patch.object(CursorWrapper, "fetchall", fetchall, create=True),
            patch.object(CursorWrapper, "rowcount", property(rowcount), create=True),
        ]
        for p in self._patches:
            p.start()
        return self

    def __exit__(self, *exc):
        for p in self._patches:
            p.stop()
        return False


class SqlFichaTests(TestCase):
    def test_mm_y_mi_salen_de_los_renglones_del_formulario(self):
        self.assertIn('sismai."RENGLON_CASOSMM"', comando._SQL_MMI)
        self.assertIn('sismai."RENGLON_CASOSMI"', comando._SQL_MMI)
        self.assertIn("THEN 'MM' WHEN", comando._SQL_MMI)
        self.assertIn("THEN 'MI'", comando._SQL_MMI)

    def test_violenta_sale_de_m_violenta(self):
        self.assertIn('sismai."M_VIOLENTA"', comando._SQL_VIOLENTA)
        self.assertIn("THEN 'VIOLENTA'", comando._SQL_VIOLENTA)

    def test_no_pisa_el_transcriptor_ni_el_subtipo_ya_escritos(self):
        for sql in (comando._SQL_MMI, comando._SQL_VIOLENTA):
            self.assertIn("CASE WHEN btrim(COALESCE(f.transcrito_legacy", sql)
            self.assertIn("CASE WHEN btrim(COALESCE(f.subtipo_legacy", sql)

    def test_la_lista_de_logins_agrupa_dentro_de_cada_lado(self):
        # Regresión: un GROUP BY suelto tras el UNION ALL hace fallar la consulta en
        # PostgreSQL y abortaba la transacción del UPDATE.
        self.assertIn("FROM (", comando._TOP_LOGINS)
        self.assertEqual(comando._TOP_LOGINS.count("GROUP BY 1"), 3)
        self.assertTrue(comando._TOP_LOGINS.rstrip().endswith("LIMIT 12"))


class CompletarTranscritorFichaTests(TestCase):
    def test_dry_run_no_escribe(self):
        fake = _EspejoFake(mmi=10, violenta=4, logins=[("CAROLP", 9)])
        salida = io.StringIO()
        with fake:
            call_command("completar_transcritor_ficha", stdout=salida)
        texto = salida.getvalue()
        self.assertIn("10 de CASOS_MMI", texto)
        self.assertIn("4 de M_VIOLENTA", texto)
        self.assertIn("CAROLP", texto)
        self.assertFalse(any(s.lstrip().startswith("UPDATE") for s in fake.sql))

    def test_ejecutar_aplica_los_dos_update(self):
        fake = _EspejoFake(mmi=10, violenta=4, actualizados=(10, 4))
        salida = io.StringIO()
        with fake:
            call_command("completar_transcritor_ficha", "--ejecutar", stdout=salida)
        updates = [s for s in fake.sql if s.lstrip().startswith("UPDATE")]
        self.assertEqual(len(updates), 2)
        self.assertIn("Actualizadas: 14 fichas", salida.getvalue())

    def test_informa_el_reparto_por_subtipo(self):
        fake = _EspejoFake(
            mmi=10, violenta=4, actualizados=(10, 4),
            resumen=[("VIOLENTA", 4), ("MI", 8), ("MM", 2), ("SIN_CLASIFICAR", 2)],
        )
        salida = io.StringIO()
        with fake:
            call_command("completar_transcritor_ficha", "--ejecutar", stdout=salida)
        texto = salida.getvalue()
        self.assertIn("Reparto por subtipo", texto)
        self.assertIn("SIN_CLASIFICAR", texto)

    def test_un_fallo_al_listar_logins_no_impide_el_backfill(self):
        class _LoginsRoto(_EspejoFake):
            def _tipo(self, sql):
                if "UNION ALL" in sql:
                    raise RuntimeError("GROUP BY roto")
                return super()._tipo(sql)

        fake = _LoginsRoto(mmi=3, violenta=2, actualizados=(3, 2))
        salida = io.StringIO()
        with fake:
            call_command("completar_transcritor_ficha", "--ejecutar", stdout=salida)
        self.assertTrue(any(s.lstrip().startswith("UPDATE") for s in fake.sql))
        self.assertIn("Actualizadas: 5 fichas", salida.getvalue())
