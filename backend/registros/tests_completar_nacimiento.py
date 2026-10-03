"""Pruebas del backfill de nacimientos del legacy (EV-25).

``importar_legacy_registros`` leyó ``NAC_RNACIDO."NOMBRES"`` y
``NAC_MADRE."HRESIDENCIA"`` pero no había campos donde guardarlos hasta la migración
``0006``. Aquí se fija que el comando solo rellena vacíos (jamás pisa un valor ya
escrito) y que el conteo del dry-run usa el mismo filtro que el UPDATE.
"""
from unittest.mock import patch

from django.core.management import call_command
from django.db.backends.utils import CursorWrapper
from django.test import TestCase

from registros.management.commands.completar_nacimiento_legacy import (
    consulta_nombres,
    consulta_residencia,
)
from registros.models import Nacimiento


class _LegacyFake:
    """Deja pasar el SQL normal (el ORM lo necesita) y simula el del esquema legacy.

    En sqlite no existe `sismai`, así que se intercepta solo lo que lo menciona. Cada
    consulta de conteo devuelve el valor configurado; los UPDATE no aplican.
    """

    def __init__(self, nombres=0, residencia=0):
        self.valores = {"nombres": nombres, "residencia": residencia}
        self.sql = []

    def _cual(self, sql):
        if 'sismai."NAC_MADRE"' in sql or "regexp_match" in sql:
            return "residencia"
        if 'sismai."NAC_RNACIDO"' in sql:
            return "nombres"
        return None

    def __enter__(self):
        self._exec = CursorWrapper.execute

        def execute(cur, sql, params=None):
            clave = self._cual(sql)
            if clave:
                self.sql.append(sql)
                return None
            return self._exec(cur, sql, params)

        def fetchone(cur, *a, **kw):
            clave = self._cual(self.sql[-1]) if self.sql else None
            if clave:
                return (self.valores[clave],)
            return cur.cursor.fetchone(*a, **kw)

        def rowcount(cur):
            clave = self._cual(self.sql[-1]) if self.sql else None
            if clave:
                return self.valores[clave]
            return cur.cursor.rowcount

        self._patches = [
            patch.object(CursorWrapper, "execute", execute),
            patch.object(CursorWrapper, "fetchone", fetchone, create=True),
            patch.object(CursorWrapper, "rowcount", property(rowcount), create=True),
        ]
        for p in self._patches:
            p.start()
        return self

    def __exit__(self, *exc):
        for p in self._patches:
            p.stop()
        return False


class CompletarNacimientoTests(TestCase):
    def setUp(self):
        self.con_nombre = Nacimiento.objects.create(
            registro_numero="LEG-RN-1", legacy_id="1", legacy_tabla="NAC_RNACIDO",
            fecha_evento="2020-01-01", nino_nombres="",
            madre_nombres="Ana", madre_edad=25,
        )
        self.ya_escrito = Nacimiento.objects.create(
            registro_numero="LEG-RN-2", legacy_id="2", legacy_tabla="NAC_RNACIDO",
            fecha_evento="2020-01-01", nino_nombres="NOMBRE REVISADO",
            madre_nombres="Ana", madre_edad=25,
        )

    def test_el_update_solo_toca_vacios(self):
        for sql in (consulta_nombres(False), consulta_residencia(False)):
            self.assertTrue(sql.startswith("WITH") or sql.startswith("UPDATE"))
        self.assertIn("btrim(COALESCE(n.nino_nombres, '')) = ''", consulta_nombres(False))
        self.assertIn("n.madre_residencia_parroquia_id IS NULL", consulta_residencia(False))
        self.assertIn('UPDATE registros_nacimiento', consulta_residencia(False))

    def test_el_conteo_usa_el_mismo_filtro_que_el_update(self):
        self.assertIn("SELECT count(*)", consulta_nombres(True))
        self.assertNotIn("UPDATE", consulta_nombres(True))
        self.assertIn("SELECT count(*)", consulta_residencia(True))
        self.assertNotIn("UPDATE", consulta_residencia(True))
        self.assertIn("btrim(COALESCE(n.nino_nombres, '')) = ''", consulta_nombres(True))

    def test_dry_run_no_modifica_nada(self):
        with _LegacyFake(nombres=1, residencia=1):
            call_command("completar_nacimiento_legacy", stdout=None)
        self.assertEqual(Nacimiento.objects.get(pk=self.con_nombre.pk).nino_nombres, "")
        self.assertEqual(Nacimiento.objects.get(pk=self.ya_escrito.pk).nino_nombres,
                         "NOMBRE REVISADO")

    def test_no_hace_nada_cuando_no_falta_ninguno(self):
        with _LegacyFake(nombres=0, residencia=0):
            call_command("completar_nacimiento_legacy", "--ejecutar", stdout=None)
        self.assertEqual(Nacimiento.objects.get(pk=self.con_nombre.pk).nino_nombres, "")

    def test_ejecutar_emite_los_updates_y_respeta_lo_ya_escrito(self):
        with _LegacyFake(nombres=1, residencia=0) as fake:
            call_command("completar_nacimiento_legacy", "--ejecutar", stdout=None)
        self.assertTrue(any(s.startswith("UPDATE registros_nacimiento") for s in fake.sql))
        self.assertEqual(Nacimiento.objects.get(pk=self.ya_escrito.pk).nino_nombres,
                         "NOMBRE REVISADO")

    def test_solo_nombres_no_toca_la_residencia(self):
        with _LegacyFake(nombres=1, residencia=5) as fake:
            call_command("completar_nacimiento_legacy", "--ejecutar", "--solo", "nombres",
                         stdout=None)
        self.assertEqual(len(fake.sql), 2)
        self.assertFalse(any("madre_residencia" in s for s in fake.sql))
