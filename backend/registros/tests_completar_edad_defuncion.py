"""Pruebas del backfill de la edad declarada del fallecido (§44).

El comando lee ``sismai."CERTIFICADO"`` (EDAD + TIPOEDAD) y solo rellena defunciones
con ``edad`` vacía. En sqlite no existe el esquema espejo, así que se sustituye el
cursor del comando por uno falso que cuenta filas.
"""

from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from registros.management.commands.completar_edad_defuncion import consulta_edades
from registros.models import Defuncion


class _CursorFalso:
    def __init__(self, pendientes=0, anomalias=0):
        self.pendientes = pendientes
        self.anomalias = anomalias
        self.sql = []
        self.rowcount = 0

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        self.sql.append(sql)
        if sql.lstrip().startswith("UPDATE"):
            self.rowcount = self.pendientes

    def fetchone(self):
        if "interval '31 days'" in self.sql[-1]:
            return (self.anomalias,)
        return (self.pendientes,)


def _correr(falso, *args):
    with patch(
        "registros.management.commands.completar_edad_defuncion.connection.cursor",
        return_value=falso,
    ):
        call_command("completar_edad_defuncion", *args, stdout=None)


class CompletarEdadDefuncionTests(TestCase):
    def setUp(self):
        self.def_sin_edad = Defuncion.objects.create(
            registro_numero="LEG-CERT-4957244", legacy_id="4957244",
            legacy_tabla="CERTIFICADO", fecha_evento="2026-01-10",
            fallecido_nombres="Jacob", sexo="M",
        )

    def test_los_updates_solo_tocan_edades_vacias(self):
        upd = consulta_edades(False)
        self.assertTrue(upd.startswith("UPDATE registros_defuncion"))
        self.assertIn("AND d.edad IS NULL", upd)
        self.assertIn('c."ID"::bigint::text = d.legacy_id', upd)
        # Solo las cuatro unidades que el modelo entiende.
        self.assertIn("IN ('A', 'M', 'D', 'H')", upd)
        self.assertIn("WHEN 'H' THEN 'HORAS'", upd)

    def test_dry_run_no_modifica_nada(self):
        _correr(_CursorFalso(pendientes=5))
        self.assertIsNone(Defuncion.objects.get(pk=self.def_sin_edad.pk).edad)

    def test_ejecutar_emite_el_update(self):
        falso = _CursorFalso(pendientes=5, anomalias=6)
        _correr(falso, "--ejecutar")
        self.assertTrue(any(s.lstrip().startswith("UPDATE") for s in falso.sql))
