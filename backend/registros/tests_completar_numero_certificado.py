"""Pruebas del backfill del número físico del certificado (§27.16).

El comando rellena ``numero_certificado`` (defunción, desde NUMEROMSDS) y
``numero_planilla`` (nacimiento, desde NROPLANILLA) solo en campos vacíos. En sqlite
no existe el esquema espejo, así que se intercepta solo lo que lo menciona.
"""
from unittest.mock import patch

from django.core.management import call_command
from django.db.backends.utils import CursorWrapper
from django.test import TestCase

from registros.management.commands.completar_numero_certificado import (
    consulta_defunciones,
    consulta_nacimientos,
)
from registros.models import Defuncion, Nacimiento


class _LegacyFake:
    def __init__(self, defunciones=0, nacimientos=0):
        self.valores = {"def": defunciones, "nac": nacimientos}
        self.sql = []

    def _cual(self, sql):
        if 'sismai."CERTIFICADO"' in sql:
            return "def"
        if 'sismai."CERTNACIMIENTO"' in sql or 'sismai."NAC_RNACIDO"' in sql:
            return "nac"
        return None

    def __enter__(self):
        self._exec = CursorWrapper.execute

        def execute(cur, sql, params=None):
            if self._cual(sql):
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


class CompletarNumeroCertificadoTests(TestCase):
    def setUp(self):
        self.def_vacia = Defuncion.objects.create(
            registro_numero="LEG-CERT-1", legacy_id="1", legacy_tabla="CERTIFICADO",
            fecha_evento="2020-01-01", fallecido_nombres="Ana", sexo="F",
        )
        self.nac_vacia = Nacimiento.objects.create(
            registro_numero="LEG-RN-2", legacy_id="2", legacy_tabla="NAC_RNACIDO",
            fecha_evento="2020-01-01", madre_nombres="Ana", madre_edad=25,
        )

    def test_los_updates_solo_tocan_vacios(self):
        upd_def = consulta_defunciones(False)
        upd_nac = consulta_nacimientos(False)
        self.assertTrue(upd_def.startswith("UPDATE registros_defuncion"))
        self.assertTrue(upd_nac.startswith("UPDATE registros_nacimiento"))
        self.assertIn("btrim(COALESCE(d.numero_certificado, '')) = ''", upd_def)
        self.assertIn("btrim(COALESCE(n.numero_planilla, '')) = ''", upd_nac)
        self.assertIn('c."ID"::bigint::text = d.legacy_id', upd_def)
        self.assertIn('cn."ID" = r."HCERTIFICADO"', upd_nac)

    def test_dry_run_no_modifica_nada(self):
        with _LegacyFake(defunciones=5, nacimientos=7):
            call_command("completar_numero_certificado", stdout=None)
        self.assertEqual(Defuncion.objects.get(pk=self.def_vacia.pk).numero_certificado, "")
        self.assertEqual(Nacimiento.objects.get(pk=self.nac_vacia.pk).numero_planilla, "")

    def test_ejecutar_emite_ambos_updates(self):
        with _LegacyFake(defunciones=5, nacimientos=7) as fake:
            call_command("completar_numero_certificado", "--ejecutar", stdout=None)
        updates = [s for s in fake.sql if s.startswith("UPDATE")]
        self.assertEqual(len(updates), 2)

    def test_solo_nacimientos_no_toca_defunciones(self):
        with _LegacyFake(defunciones=5, nacimientos=7) as fake:
            call_command("completar_numero_certificado", "--ejecutar",
                         "--solo", "nacimientos", stdout=None)
        self.assertFalse(any('UPDATE registros_defuncion' in s for s in fake.sql))
