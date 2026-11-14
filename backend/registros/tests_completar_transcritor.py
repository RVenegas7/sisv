"""Pruebas del backfill del transcriptor legacy (§45).

El comando copia ``sismai."CERTNACIMIENTO"."USUARIO"`` a
``Nacimiento.transcrito_legacy`` (y la fecha del certificado a ``transcrito_en``) solo en
campos vacíos. En sqlite no existe el esquema espejo, así que se intercepta únicamente lo
que lo menciona, igual que en ``tests_completar_numero_certificado.py``.
"""
import io
from unittest.mock import patch

from django.core.management import call_command
from django.db.backends.utils import CursorWrapper
from django.test import TestCase

from registros.management.commands.completar_transcritor_nacimiento import consulta_nacimientos


class _LegacyFake:
    def __init__(self, candidatos=0, actualizados=0, logins=(), sin_nac=0, sin_cert=0):
        self.valores = {"count": candidatos, "update": actualizados,
                        "sin_nac": sin_nac, "sin_cert": sin_cert}
        self.logins = list(logins)
        self.sql = []

    def _tipo(self, sql):
        if "GROUP BY 1" in sql:
            return "logins"
        if "NOT EXISTS" in sql:
            return "sin_cert" if 'JOIN sismai."CERTNACIMIENTO"' in sql else "sin_nac"
        if sql.lstrip().startswith("UPDATE"):
            return "update"
        if "sismai." in sql and sql.lstrip().startswith("SELECT count(*)"):
            return "count"
        return None

    def __enter__(self):
        self._exec = CursorWrapper.execute

        def execute(cur, sql, params=None):
            if self._tipo(sql):
                self.sql.append(sql)
                return None
            return self._exec(cur, sql, params)

        def fetchone(cur, *a, **kw):
            clave = self._tipo(self.sql[-1]) if self.sql else None
            if clave in ("count", "update", "sin_nac", "sin_cert"):
                return (self.valores[clave],)
            return cur.cursor.fetchone(*a, **kw)

        def fetchall(cur, *a, **kw):
            clave = self._tipo(self.sql[-1]) if self.sql else None
            if clave == "logins":
                return self.logins
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


class ConsultaTranscritorTests(TestCase):
    def test_actualiza_solo_campos_vacios(self):
        sql = consulta_nacimientos()
        self.assertIn('transcrito_legacy = btrim(cn."USUARIO")', sql)
        self.assertIn("COALESCE(n.transcrito_en", sql)
        self.assertIn("btrim(COALESCE(n.transcrito_legacy, '')) = ''", sql)

    def test_limite_se_aplica_al_update(self):
        self.assertIn("LIMIT 10", consulta_nacimientos(limite=10))

    def test_cuenta_usa_el_mismo_cruce(self):
        sql = consulta_nacimientos(contar=True)
        self.assertTrue(sql.startswith("SELECT count(*)"))
        self.assertIn('JOIN sismai."NAC_RNACIDO"', sql)


class CompletarTranscritorCommandTests(TestCase):
    def _correr(self, *args, **kwargs):
        salida = io.StringIO()
        with _LegacyFake(**kwargs):
            call_command("completar_transcritor_nacimiento", *args, stdout=salida)
        return salida.getvalue()

    def test_dry_run_no_escribe(self):
        fake = _LegacyFake(candidatos=7, logins=[("MARINAT", 5), ("JUANANAT", 2)])
        salida = io.StringIO()
        with fake:
            call_command("completar_transcritor_nacimiento", stdout=salida)
        self.assertIn("transcriptor recuperable: 7", salida.getvalue())
        self.assertIn("MARINAT", salida.getvalue())
        self.assertFalse(any(s.lstrip().startswith("UPDATE") for s in fake.sql))

    def test_ejecutar_aplica_el_update(self):
        fake = _LegacyFake(candidatos=7, actualizados=7)
        salida = io.StringIO()
        with fake:
            call_command("completar_transcritor_nacimiento", "--ejecutar", stdout=salida)
        self.assertTrue(any(s.lstrip().startswith("UPDATE") for s in fake.sql))
        self.assertIn("Actualizados: 7", salida.getvalue())

    def test_ejecutar_con_limite(self):
        fake = _LegacyFake(candidatos=7, actualizados=3)
        with fake:
            call_command("completar_transcritor_nacimiento", "--ejecutar", "--limite", "3")
        update = next(s for s in fake.sql if s.lstrip().startswith("UPDATE"))
        self.assertIn("LIMIT 3", update)

    def test_informa_los_que_no_unen(self):
        salida = self._correr(candidatos=5, sin_nac=2, sin_cert=3)
        self.assertIn("sin NAC_RNACIDO (no unen): 2", salida)
        self.assertIn("sin certificado enlazado: 3", salida)
