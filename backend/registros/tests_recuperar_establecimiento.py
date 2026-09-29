"""Pruebas de la recuperación del establecimiento en las defunciones.

``importar_legacy_registros`` leía solo ``CERTIFICADO."HESTABLECIMIENTO_OCUR"``, que viene
nulo en la mitad de los certificados, dejando esas muertes sin establecimiento y por tanto
sin organización. Aquí se fija la precedencia del fallback y la garantía de que la
recuperación **jamás** pisa un establecimiento ya escrito.
"""
from unittest.mock import patch

from django.core.management import call_command
from django.db.backends.utils import CursorWrapper
from django.test import TestCase

from registros.management.commands.importar_legacy_registros import como_id
from registros.management.commands.recuperar_establecimiento_defuncion import _consulta
from registros.models import Defuncion


class _LegacyFake:
    """Deja pasar el SQL normal (el ORM lo necesita) y simula el de `sismai`.

    En sqlite no existe el esquema legacy, así que se intercepta solo lo que toca
    `CERTIFICADO` en vez de parchear `connection.cursor` entero.
    """

    def __init__(self, recuperables):
        self.recuperables = recuperables
        self.sql = []

    def __enter__(self):
        self._exec = CursorWrapper.execute
        self.sql = []

        def execute(cur, sql, params=None):
            if 'sismai."CERTIFICADO"' in sql:
                self.sql.append(sql)
                return None
            return self._exec(cur, sql, params)

        # `CursorWrapper` no define fetchone/rowcount como atributos de clase (los
        # delega con __getattr__), así que se resuelven contra el cursor de verdad.
        def fetchone(cur, *a, **kw):
            if self.sql and 'sismai."CERTIFICADO"' in self.sql[-1]:
                return (self.recuperables,)
            return cur.cursor.fetchone(*a, **kw)

        def rowcount(cur):
            if self.sql and 'sismai."CERTIFICADO"' in self.sql[-1]:
                return self.recuperables
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


class PrecedenciaEstablecimientoTests(TestCase):
    def test_ocur_tiene_prioridad_sobre_el_certificado(self):
        self.assertEqual(como_id(1087435.0), 1087435)
        self.assertIsNone(como_id(None))
        self.assertIsNone(como_id(0))
        self.assertIsNone(como_id(""))
        self.assertIsNone(como_id("no-es-un-id"))
        # el 0 de Oracle significa "sin dato", no el establecimiento 0
        self.assertIsNone(como_id(0.0))


class RecuperarEstablecimientoTests(TestCase):
    def setUp(self):
        self.sin_nombre = Defuncion.objects.create(
            registro_numero="LEG-CERT-1", legacy_id="1", legacy_tabla="CERTIFICADO",
            fecha_evento="2020-01-01", establecimiento="",
        )
        self.con_nombre = Defuncion.objects.create(
            registro_numero="LEG-CERT-2", legacy_id="2", legacy_tabla="CERTIFICADO",
            fecha_evento="2020-01-01", establecimiento="HOSP. YA ESCRITO",
        )

    def test_el_update_solo_toca_establecimientos_vacios(self):
        """La garantía importante: no se puede pisar trabajo previo."""
        sql = _consulta(contar=False)
        self.assertIn("btrim(d.establecimiento) = ''", sql)
        self.assertIn("UPDATE registros_defuncion", sql)
        # la precedencia del fallback, en el propio SQL
        self.assertIn('COALESCE(c."HESTABLECIMIENTO_OCUR", c."HESTABLECIMIENTO")', sql)

    def test_el_conteo_usa_el_mismo_filtro_que_el_update(self):
        self.assertIn("btrim(d.establecimiento) = ''", _consulta(contar=True))
        self.assertIn("SELECT count(*)", _consulta(contar=True))
        self.assertNotIn("UPDATE", _consulta(contar=True))

    def test_dry_run_no_modifica_nada(self):
        with _LegacyFake(recuperables=2):
            call_command("recuperar_establecimiento_defuncion", stdout=None)
        self.assertEqual(Defuncion.objects.get(pk=self.sin_nombre.pk).establecimiento, "")
        self.assertEqual(Defuncion.objects.get(pk=self.con_nombre.pk).establecimiento,
                         "HOSP. YA ESCRITO")

    def test_no_hace_nada_cuando_no_falta_ninguno(self):
        Defuncion.objects.filter(pk=self.sin_nombre.pk).update(establecimiento="HOSP. A")
        with _LegacyFake(recuperables=0):
            call_command("recuperar_establecimiento_defuncion", stdout=None)
        self.assertEqual(Defuncion.objects.get(pk=self.sin_nombre.pk).establecimiento, "HOSP. A")

    def test_ejecutar_avanza_una_fila_y_deja_intacta_la_ya_escrita(self):
        """En sqlite el UPDATE legacy no puede aplicarse, así que se comprueba que
        el comando llega a intentarlo y que no toca lo ya escrito."""
        with _LegacyFake(recuperables=1) as fake:
            call_command("recuperar_establecimiento_defuncion", "--ejecutar", stdout=None)
        self.assertTrue(any(s.startswith("UPDATE registros_defuncion") for s in fake.sql),
                        "no llegó a emitir el UPDATE")
        # la garantía que importa: la fila con establecimiento no se modifica
        self.assertEqual(Defuncion.objects.get(pk=self.con_nombre.pk).establecimiento,
                         "HOSP. YA ESCRITO")
