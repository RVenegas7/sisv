"""Pruebas del backfill del transcriptor de defunciones (§46).

El comando copia ``sismai."CERTIFICADO"."LOGIN"`` a ``Defuncion.transcrito_legacy`` y la
fecha de operación a ``transcrito_en``, solo en campos vacíos. En sqlite no existe el
esquema espejo, así que se interceptan solo las consultas que lo mencionan (mismo patrón
que ``tests_completar_transcritor.py``).
"""
import io
from unittest.mock import patch

from django.db.backends.utils import CursorWrapper
from django.test import TestCase

from django.core.management import call_command

from registros.management.commands.completar_transcritor_defuncion import consulta_defunciones


class _EspejoFake:
    """Devuelve valores fijos para las consultas al espejo y para el UPDATE."""

    def __init__(self, pendientes=0, actualizados=0, sin_certificado=0, logins=(), resumen=()):
        self.valores = {
            "count": pendientes,
            "update": actualizados,
            "sin_cert": sin_certificado,
        }
        self.logins = list(logins)
        self.resumen = list(resumen)
        self.sql = []

    def _tipo(self, sql):
        limpio = sql.lstrip()
        if limpio.startswith("UPDATE"):
            return "update"
        if "GROUP BY" in sql:
            return "logins"
        if "NOT EXISTS" in sql:
            return "sin_cert"
        if limpio.startswith("SELECT count(*)"):
            return "count"
        if "COALESCE(NULLIF(subtipo_legacy" in sql:
            return "resumen"
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
            if clave == "update":
                return self.valores["update"]
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


class ConsultaDefuncionTests(TestCase):
    def test_actualiza_solo_campos_vacios(self):
        sql = consulta_defunciones()
        self.assertIn('transcrito_legacy = btrim(c."LOGIN")', sql)
        self.assertIn("COALESCE(d.transcrito_en", sql)
        self.assertIn("btrim(COALESCE(d.transcrito_legacy, '')) = ''", sql)

    def test_cruza_por_legacy_id_y_tabla(self):
        sql = consulta_defunciones()
        self.assertIn('c."ID"::bigint::text = d.legacy_id', sql)
        self.assertIn("d.legacy_tabla = 'CERTIFICADO'", sql)

    def test_limite_se_aplica_al_update(self):
        self.assertIn("LIMIT 10", consulta_defunciones(limite=10))


class CompletarTranscritorDefuncionTests(TestCase):
    def test_dry_run_no_escribe(self):
        fake = _EspejoFake(pendientes=7, logins=[("YOLISIMORT", 5)])
        salida = io.StringIO()
        with fake:
            call_command("completar_transcritor_defuncion", stdout=salida)
        self.assertIn("transcriptor recuperable: 7", salida.getvalue())
        self.assertIn("YOLISIMORT", salida.getvalue())
        self.assertFalse(any(s.lstrip().startswith("UPDATE") for s in fake.sql))

    def test_ejecutar_aplica_el_update(self):
        fake = _EspejoFake(pendientes=7, actualizados=7)
        salida = io.StringIO()
        with fake:
            call_command("completar_transcritor_defuncion", "--ejecutar", stdout=salida)
        self.assertTrue(any(s.lstrip().startswith("UPDATE") for s in fake.sql))
        self.assertIn("Actualizados: 7", salida.getvalue())

    def test_ejecutar_con_limite(self):
        fake = _EspejoFake(pendientes=7, actualizados=3)
        with fake:
            call_command("completar_transcritor_defuncion", "--ejecutar", "--limite", "3")
        update = next(s for s in fake.sql if s.lstrip().startswith("UPDATE"))
        self.assertIn("LIMIT 3", update)

    def test_informa_los_que_no_tienen_certificado(self):
        fake = _EspejoFake(pendientes=5, sin_certificado=2)
        salida = io.StringIO()
        with fake:
            call_command("completar_transcritor_defuncion", stdout=salida)
        self.assertIn("sin certificado en el espejo", salida.getvalue())
        self.assertIn("2", salida.getvalue())

    def test_un_fallo_al_listar_logins_no_impide_el_backfill(self):
        # Regresión: la lista de logins llegó a romper la transacción entera y el UPDATE
        # fallaba con «current transaction is aborted» en vez de escribir.
        class _LoginsRoto(_EspejoFake):
            def _tipo(self, sql):
                if "GROUP BY" in sql:
                    raise RuntimeError("GROUP BY roto")
                return super()._tipo(sql)

        fake = _LoginsRoto(pendientes=4, actualizados=4)
        salida = io.StringIO()
        with fake:
            call_command("completar_transcritor_defuncion", "--ejecutar", stdout=salida)
        self.assertTrue(any(s.lstrip().startswith("UPDATE") for s in fake.sql))
        self.assertIn("Actualizados: 4", salida.getvalue())
