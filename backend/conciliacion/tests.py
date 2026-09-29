import csv
import os
import tempfile
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from conciliacion.models import (ConciliacionENO, ConciliacionENOCentro, ConciliacionMaterna,
                                 ConciliacionNeonatal)
from conciliacion.services import clasificar, es_pseudo_total, normalizar_centro
from seguridad.models import Organizacion
from vigilancia.models import EventoENO


class ServiciosConciliacionTests(TestCase):
    def test_pseudo_total_detecta_los_totales_de_la_oficina(self):
        self.assertTrue(es_pseudo_total("TOTAL DE PACIENTES ATENDIDOS (ATENCIÓN AMBULATORIA Y EMERGENCIA)"))
        self.assertTrue(es_pseudo_total("TOTAL DE PACIENTES HOSPITALIZADOS POR TODAS CAUSAS"))
        self.assertTrue(es_pseudo_total("total de pacientes atendidos"))
        self.assertFalse(es_pseudo_total("SINDROME VIRAL (VIROSIS) (B34)"))
        self.assertFalse(es_pseudo_total("MORTALIDAD NEONATAL TARDÍA DE 7 A 27 DÍAS"))
        self.assertFalse(es_pseudo_total(""))
        self.assertFalse(es_pseudo_total(None))

    def test_normalizar_centro_ignora_tildes_parentesis_y_caixa(self):
        self.assertEqual(normalizar_centro("HOSP. LA CARUCIEÑA"),
                         normalizar_centro("HOSP LA CARUCIENA"))
        self.assertEqual(normalizar_centro("AMB. EL ROBLE (LAR)"), "amb el roble")

    def test_clasificar_por_estado(self):
        self.assertEqual(clasificar(5, 7, 5, 7, False, True)[0], "CUADRA")
        self.assertEqual(clasificar(5, 7, 4, 7, False, True)[0], "DIFERENCIA")
        self.assertEqual(clasificar(5, 0, 0, 0, False, True)[0], "SOLO_CRUDO")
        self.assertEqual(clasificar(0, 0, 3, 0, False, True)[0], "SOLO_SISV")
        self.assertEqual(clasificar(0, 0, 0, 0, False, True)[0], "CUADRA")

    def test_clasificar_por_resolucion(self):
        self.assertEqual(clasificar(1, 0, 1, 0, True, True)[1], "CENTRO_SIN_ORG")
        self.assertEqual(clasificar(1, 0, 0, 0, False, False)[1], "EVENTO_SIN_EQUIVALENTE")
        self.assertEqual(clasificar(0, 0, 1, 0, False, True)[1], "SIN_FUENTE_EN_CRUDO")
        self.assertEqual(clasificar(9, 0, 0, 0, False, False, es_pseudo=True)[0], "EXCLUIDO_EN_ETL")
        self.assertEqual(clasificar(9, 0, 0, 0, False, False, es_pseudo=True)[1],
                         "PSEUDO_TOTAL_EXCLUIDO")


class ConciliarENOCommandTests(TestCase):
    def setUp(self):
        self.org = Organizacion.objects.create(
            codigo="HOSP-A", nombre="HOSP. A", nivel="CENTRO", activo=True)
        self.fallback = Organizacion.objects.create(
            codigo="LEGACY-LARA", nombre="Legacy regional (histórico)",
            nivel="REGIONAL", activo=True)
        self.evento = EventoENO.objects.create(
            codigo_evento="eno_prueba", nombre="Gripe", orden_epi12=1)
        self.catalogo = {
            111: ("001", "GRIPE"),
            999: ("236", "TOTAL DE PACIENTES ATENDIDOS (ATENCIÓN AMBULATORIA Y EMERGENCIA)"),
            888: ("041", "SINDROME VIRAL (VIROSIS) (B34)"),
        }
        self.nombres = {10: "HOSP. A", 11: "CENTRO QUE NO EXISTE"}

    def _correr(self, crudo, sisv, anio=2026, csv="", ejecutar=True):
        salida = StringIO()
        # el comando ahora devuelve (…, documento, instancia) en cada fila cruda
        crudo = [tuple(fila) + (fila[0] * 1000, "ESTACION-A") for fila in crudo]
        with patch("conciliacion.management.commands.conciliar_eno."
                   "Command._catalogo_legacy", return_value=(self.catalogo, self.nombres)), \
             patch("conciliacion.management.commands.conciliar_eno."
                   "Command._transcriptores", return_value={}), \
             patch("conciliacion.management.commands.conciliar_eno."
                   "Command._area", return_value={10.0, 11.0}), \
             patch("conciliacion.management.commands.conciliar_eno."
                   "por_evento_id", return_value={111: self.evento.id}), \
             patch("conciliacion.management.commands.conciliar_eno."
                   "Command._crudo", return_value=crudo), \
             patch("conciliacion.management.commands.conciliar_eno."
                   "Command._sisv", return_value=sisv):
            call_command("conciliar_eno", "--anio", str(anio),
                         *(["--ejecutar"] if ejecutar else []),
                         *(["--csv", csv] if csv else []), stdout=salida)
        return salida.getvalue()

    def _fila(self, **kwargs):
        return ConciliacionENO.objects.get(**kwargs)

    def test_cuadra_cuando_el_legacy_y_sisv_coinciden(self):
        salida = self._correr(
            crudo=[(10, 5, 111, 5, 7, 0, 0)],
            sisv={(self.org.id, 5, "MORBILIDAD", self.evento.id): (5, 7)},
        )
        f = self._fila(anio=2026, semana=5, legado_enfermedad_id=111)
        self.assertEqual(f.estado, "CUADRA")
        self.assertEqual(f.resolucion, "CONCILIADO")
        self.assertEqual((f.crudo_h, f.crudo_m), (5, 7))
        self.assertEqual((f.sisv_h, f.sisv_m), (5, 7))
        self.assertEqual((f.diferencia_h, f.diferencia_m), (0, 0))
        self.assertIn("diferencia=0", salida)

    def test_detecta_la_diferencia_y_no_la_oculta(self):
        self._correr(
            crudo=[(10, 5, 111, 5, 7, 0, 0)],
            sisv={(self.org.id, 5, "MORBILIDAD", self.evento.id): (4, 7)},
        )
        f = self._fila(anio=2026, semana=5, legado_enfermedad_id=111)
        self.assertEqual(f.estado, "DIFERENCIA")
        self.assertEqual(f.diferencia_h, 1)
        self.assertEqual(f.diferencia_m, 0)

    def test_la_fila_de_total_no_cuenta_como_enfermedad(self):
        self._correr(crudo=[(10, 5, 999, 900, 0, 0, 0)], sisv={})
        f = self._fila(anio=2026, semana=5, legado_enfermedad_id=999)
        self.assertEqual(f.estado, "EXCLUIDO_EN_ETL")
        self.assertEqual(f.resolucion, "PSEUDO_TOTAL_EXCLUIDO")
        self.assertTrue(f.es_pseudo_total)
        self.assertEqual(f.crudo_h, 900)
        self.assertIsNone(f.evento_id)

    def test_evento_sin_equivalente_queda_visible_como_no_conciliado(self):
        self._correr(crudo=[(10, 5, 888, 4, 0, 0, 0)], sisv={})
        f = self._fila(anio=2026, semana=5, legado_enfermedad_id=888)
        self.assertEqual(f.estado, "SOLO_CRUDO")
        self.assertEqual(f.resolucion, "EVENTO_SIN_EQUIVALENTE")
        self.assertEqual(f.diferencia_h, 4)

    def test_centro_sin_organizacion_cae_al_fallback_y_sigue_cuadrando(self):
        self._correr(
            crudo=[(11, 5, 111, 3, 0, 0, 0)],
            sisv={(self.fallback.id, 5, "MORBILIDAD", self.evento.id): (3, 0)},
        )
        f = self._fila(anio=2026, semana=5, legado_enfermedad_id=111)
        self.assertEqual(f.organizacion_id, self.fallback.id)
        self.assertEqual(f.estado, "CUADRA")
        self.assertEqual(f.resolucion, "CENTRO_SIN_ORG")

    def test_guarda_el_detalle_por_centro(self):
        self._correr(
            crudo=[(10, 5, 111, 5, 7, 0, 0), (11, 5, 111, 3, 0, 0, 0)],
            sisv={(self.org.id, 5, "MORBILIDAD", self.evento.id): (5, 7),
                  (self.fallback.id, 5, "MORBILIDAD", self.evento.id): (3, 0)},
        )
        detalles = {d.legado_establecimiento_id: d for d in ConciliacionENOCentro.objects.all()}
        self.assertEqual(set(detalles), {10, 11})
        self.assertEqual(detalles[10].crudo_h, 5)
        self.assertEqual(detalles[10].sisv_h, 5)
        self.assertEqual(detalles[10].legado_establecimiento_nombre, "HOSP. A")

    def test_guarda_la_estacion_que_transcribio(self):
        self._correr(crudo=[(10, 5, 111, 5, 7, 0, 0)], sisv={})
        d = ConciliacionENOCentro.objects.get(legado_establecimiento_id=10)
        self.assertEqual(d.transcrito_por, "ESTACION-A")
        self.assertEqual(d.legado_documento, 10000)

    def test_solo_en_sisv_no_se_inventa_un_centro(self):
        self._correr(
            crudo=[],
            sisv={(self.org.id, 5, "MORBILIDAD", self.evento.id): (2, 0)},
        )
        f = self._fila(anio=2026, semana=5)
        self.assertEqual(f.estado, "SOLO_SISV")
        self.assertEqual(f.sisv_h, 2)
        self.assertEqual(f.crudo_h, 0)

    def test_mortalidad_se_cuadra_por_separado(self):
        self._correr(
            crudo=[(10, 5, 111, 5, 7, 1, 2)],
            sisv={(self.org.id, 5, "MORBILIDAD", self.evento.id): (5, 7),
                  (self.org.id, 5, "MORTALIDAD", self.evento.id): (1, 2)},
        )
        m = self._fila(anio=2026, semana=5, tipo="MORTALIDAD")
        self.assertEqual(m.estado, "CUADRA")
        self.assertEqual((m.sisv_h, m.sisv_m), (1, 2))

    def test_ignora_celdas_en_cero_y_semanas_invalidas(self):
        self._correr(
            crudo=[(10, 5, 111, 0, 0, 0, 0), (10, 99, 111, 4, 0, 0, 0), (10, 0, 111, 4, 0, 0, 0)],
            sisv={},
        )
        self.assertEqual(ConciliacionENO.objects.count(), 0)

    def test_el_csv_de_un_anio_no_arrastra_otros_anios(self):
        self._correr(crudo=[(10, 5, 111, 5, 7, 0, 0)], sisv={}, anio=2026)
        self._correr(crudo=[(10, 5, 111, 1, 2, 0, 0)], sisv={}, anio=2010)
        ruta = tempfile.mktemp(suffix=".csv")
        try:
            self._correr(crudo=[], sisv={}, anio=2026, csv=ruta, ejecutar=False)
            with open(ruta, encoding="utf-8-sig") as fh:
                lineas = list(csv.DictReader(fh, delimiter=";"))
        finally:
            os.unlink(ruta)
        self.assertEqual({int(l["anio"]) for l in lineas}, {2026})
        self.assertEqual(len(lineas), 1)

    def test_el_csv_de_centros_lleva_la_estacion(self):
        self._correr(crudo=[(10, 5, 111, 5, 7, 0, 0)], sisv={}, anio=2026)
        self._correr(crudo=[(10, 5, 111, 1, 2, 0, 0)], sisv={}, anio=2010)
        ruta = tempfile.mktemp(suffix=".csv")
        try:
            self._correr(crudo=[], sisv={}, anio=2026, csv=ruta, ejecutar=False)
            with open(f"{os.path.splitext(ruta)[0]}_centros.csv", encoding="utf-8-sig") as fh:
                lineas = list(csv.DictReader(fh, delimiter=";"))
        finally:
            os.unlink(f"{os.path.splitext(ruta)[0]}_centros.csv")
            if os.path.exists(ruta):
                os.unlink(ruta)
        self.assertEqual({int(l["anio"]) for l in lineas}, {2026})
        self.assertEqual(lineas[0]["transcrito_por"], "ESTACION-A")
        self.assertEqual(lineas[0]["establecimiento"], "HOSP. A")


class ConciliarNeonatalCommandTests(TestCase):
    """Conciliación de mortalidad neonatal (0-27 días) del registro MMI vs SISV."""

    def setUp(self):
        self.org = Organizacion.objects.create(
            codigo="HOSP-A", nombre="HOSP. A", nivel="CENTRO", activo=True)
        self.fallback = Organizacion.objects.create(
            codigo="LEGACY-LARA", nombre="Legacy regional (histórico)",
            nivel="REGIONAL", activo=True)
        self.nombres = {10: "HOSP. A", 11: "CENTRO QUE NO EXISTE"}

    def _correr(self, legacy, sisv, anio=2026, csv="", ejecutar=True, alerta=5):
        salida = StringIO()
        with patch("conciliacion.management.commands.conciliar_neonatal."
                   "Command._nombres_establecimiento", return_value=self.nombres), \
             patch("conciliacion.management.commands.conciliar_neonatal."
                   "Command._area", return_value={10.0, 11.0}), \
             patch("conciliacion.management.commands.conciliar_neonatal."
                   "Command._legacy", return_value=legacy), \
             patch("conciliacion.management.commands.conciliar_neonatal."
                   "Command._sisv", return_value=sisv):
            call_command("conciliar_neonatal", "--anio", str(anio),
                         "--alerta", str(alerta),
                         *(["--ejecutar"] if ejecutar else []),
                         *(["--csv", csv] if csv else []), stdout=salida)
        return salida.getvalue()

    def test_el_tipo_de_documento_mmi_no_es_el_del_eno(self):
        """`DOCUMENTO.TIPO` 1 es el ENO de mortalidad; los formularios MMI son 23.

        Filtrar por 1 deja el lado legacy vacío en silencio, que es como se
        perdió la primera corrida de esta conciliación.
        """
        from conciliacion.management.commands import conciliar_neonatal as cmd
        self.assertEqual(cmd.TIPO_MMI, 23)
        self.assertNotEqual(cmd.TIPO_MMI, 1)

    def test_estado_por_lado(self):
        from conciliacion.management.commands.conciliar_neonatal import Command
        est = Command._estado
        self.assertEqual(est(3, 3), "CUADRA")
        self.assertEqual(est(5, 3), "DIFERENCIA")
        self.assertEqual(est(4, 0), "SOLO_CRUDO")
        self.assertEqual(est(0, 2), "SOLO_SISV")
        self.assertEqual(est(0, 0), "CUADRA")

    def test_cuadra_cuando_el_registro_y_sisv_coinciden(self):
        self._correr(legacy=[(10, 2026, 5, 4)], sisv=[(self.org.id, 2026, 5, 4)])
        f = ConciliacionNeonatal.objects.get(anio=2026, semana=5, organizacion=self.org)
        self.assertEqual(f.estado, "CUADRA")
        self.assertEqual(f.resolucion, "CONCILIADO")
        self.assertEqual((f.legado, f.sisv, f.diferencia), (4, 4, 0))

    def test_detecta_el_hueco_de_captura(self):
        """El caso 2019-2020: el registro de la oficina tiene y SISV no."""
        self._correr(legacy=[(10, 2020, 10, 9)], sisv=[(self.org.id, 2020, 10, 0)])
        f = ConciliacionNeonatal.objects.get(anio=2020, semana=10, organizacion=self.org)
        self.assertEqual(f.estado, "SOLO_CRUDO")
        self.assertEqual(f.diferencia, 9)

    def test_el_centro_sin_organizacion_va_al_agregado_y_no_se_pierde(self):
        self._correr(legacy=[(11, 2026, 5, 2)], sisv=[])
        f = ConciliacionNeonatal.objects.get(anio=2026, semana=5,
                                             organizacion=self.fallback)
        self.assertTrue(f.es_agregado_sin_org)
        self.assertEqual(f.resolucion, "CENTRO_SIN_ORG")
        self.assertEqual(f.legado, 2)
        self.assertEqual(f.cantidad_centros_legacy, 1)

    def test_sin_ejecutar_no_escribe_nada(self):
        self._correr(legacy=[(10, 2026, 5, 4)], sisv=[(self.org.id, 2026, 5, 4)],
                     ejecutar=False)
        self.assertEqual(ConciliacionNeonatal.objects.count(), 0)

    def test_avisa_las_semanas_con_el_registro_por_encima(self):
        salida = self._correr(legacy=[(10, 2020, 10, 9)], sisv=[(self.org.id, 2020, 10, 0)])
        self.assertIn("por encima de SISV", salida)
        self.assertIn("2020 S10", salida)

    def test_el_agregado_no_dispara_la_alerta_de_hueco(self):
        """El agregado regional siempre queda 'todo legacy y nada de SISV'.

        Si saltara la alerta, cada semana llenaría el aviso de falsos positivos.
        """
        salida = self._correr(legacy=[(11, 2026, 5, 40)], sisv=[])
        self.assertNotIn("por encima de SISV", salida)
        self.assertIn("Agregado regional", salida)

    def test_el_csv_lleva_una_fila_por_semana_y_organizacion(self):
        ruta = tempfile.mktemp(suffix=".csv")
        try:
            self._correr(legacy=[(10, 2026, 5, 4), (10, 2026, 6, 2)],
                         sisv=[(self.org.id, 2026, 5, 4)], csv=ruta)
            with open(ruta, encoding="utf-8-sig") as fh:
                lineas = list(csv.DictReader(fh, delimiter=";"))
        finally:
            os.unlink(ruta)
            self.assertEqual(len(lineas), 2)
            self.assertEqual({int(l["semana"]) for l in lineas}, {5, 6})
            self.assertEqual(lineas[0]["organizacion"], "HOSP. A")


class ConciliarMMCommandTests(TestCase):
    """Conciliación de muerte materna: registro de investigación vs certificado.

    A diferencia del neonatal, aquí los dos lados **no son la misma definición** y la
    diferencia es el hallazgo: el certificado marca el embarazo o puerperio en una
    fracción de las muertes que el registro de investigación documenta. Por eso el
    comando no trata la diferencia como una falla, sino como el resultado.
    """

    def setUp(self):
        self.org = Organizacion.objects.create(
            codigo="HOSP-A", nombre="HOSP. A", nivel="CENTRO", activo=True)
        self.fallback = Organizacion.objects.create(
            codigo="LEGACY-LARA", nombre="Legacy regional (histórico)",
            nivel="REGIONAL", activo=True)
        self.nombres = {10: "HOSP. A", 11: "CENTRO QUE NO EXISTE"}

    def _correr(self, legacy, sisv, anio=2026, csv="", ejecutar=True):
        salida = StringIO()
        with patch("conciliacion.management.commands.conciliar_mm."
                   "Command._nombres_establecimiento", return_value=self.nombres), \
             patch("conciliacion.management.commands.conciliar_mm."
                   "Command._area", return_value={10.0, 11.0}), \
             patch("conciliacion.management.commands.conciliar_mm."
                   "Command._legacy", return_value=legacy), \
             patch("conciliacion.management.commands.conciliar_mm."
                   "Command._sisv", return_value=sisv):
            call_command("conciliar_mm", "--anio", str(anio),
                         *(["--ejecutar"] if ejecutar else []),
                         *(["--csv", csv] if csv else []), stdout=salida)
        return salida.getvalue()

    def test_el_tipo_de_documento_mmi_no_es_el_del_eno(self):
        """`DOCUMENTO.TIPO` 1 es el ENO de mortalidad; los formularios MMI son 23.

        Filtrar por 1 deja el lado legacy vacío en silencio.
        """
        from conciliacion.management.commands import conciliar_mm as cmd
        self.assertEqual(cmd.TIPO_MMI, 23)
        self.assertNotEqual(cmd.TIPO_MMI, 1)

    def test_el_caso_real_de_2026(self):
        """Registro 18, certificados 7: el certificado no marca 11 de cada 18."""
        salida = self._correr(legacy=[(10, 2026, 22, 18)],
                              sisv=[(self.org.id, 2026, 22, 7)])
        f = ConciliacionMaterna.objects.get(anio=2026, semana=22, organizacion=self.org)
        self.assertEqual((f.legado, f.sisv, f.diferencia), (18, 7, 11))
        self.assertEqual(f.estado, "DIFERENCIA")
        # El comando informa el porcentaje marcado, que es el hallazgo.
        self.assertIn("38.9", salida)

    def test_cuadra_cuando_el_certificado_tambien_lo_marca(self):
        """Las semanas en que el certificado sí marca la muerte materna cuadran."""
        self._correr(legacy=[(10, 2026, 22, 3)], sisv=[(self.org.id, 2026, 22, 3)])
        f = ConciliacionMaterna.objects.get(anio=2026, semana=22, organizacion=self.org)
        self.assertEqual(f.estado, "CUADRA")
        self.assertEqual(f.diferencia, 0)

    def test_avisa_cuando_el_certificado_tiene_y_el_registro_no(self):
        """Ninguna fuente es completa: hay muertes que el registro no registró."""
        salida = self._correr(legacy=[(10, 2026, 22, 0)],
                              sisv=[(self.org.id, 2026, 22, 2)])
        f = ConciliacionMaterna.objects.get(anio=2026, semana=22, organizacion=self.org)
        self.assertEqual(f.estado, "SOLO_SISV")
        self.assertIn("no llegó a registrar", salida)

    def test_el_centro_sin_organizacion_va_al_agregado_y_no_se_pierde(self):
        self._correr(legacy=[(11, 2026, 5, 2)], sisv=[])
        f = ConciliacionMaterna.objects.get(anio=2026, semana=5, organizacion=self.fallback)
        self.assertTrue(f.es_agregado_sin_org)
        self.assertEqual(f.resolucion, "CENTRO_SIN_ORG")
        self.assertEqual(f.legado, 2)

    def test_sin_ejecutar_no_escribe_nada(self):
        self._correr(legacy=[(10, 2026, 5, 4)], sisv=[(self.org.id, 2026, 5, 1)], ejecutar=False)
        self.assertEqual(ConciliacionMaterna.objects.count(), 0)

    def test_el_agregado_no_infla_el_conteo_de_centros(self):
        """`cantidad_centros_legacy` es por celda: un centro en 5 semanas sigue siendo 1.

        Sumar las celdas daría 5 centros donde hay 1, y el informe de MM presentaría
        una red de centros que no existe.
        """
        salida = self._correr(legacy=[(11, 2026, 5, 1), (11, 2026, 6, 1),
                                      (11, 2026, 7, 1), (11, 2026, 8, 1),
                                      (11, 2026, 9, 1)], sisv=[])
        f = ConciliacionMaterna.objects.get(anio=2026, semana=5, organizacion=self.fallback)
        self.assertEqual(f.cantidad_centros_legacy, 1)
        self.assertIn("1 establecimientos", salida)

    def test_el_csv_lleva_una_fila_por_semana_y_organizacion(self):
        ruta = tempfile.mktemp(suffix=".csv")
        try:
            self._correr(legacy=[(10, 2026, 5, 4), (10, 2026, 6, 2)],
                         sisv=[(self.org.id, 2026, 5, 1)], csv=ruta)
            with open(ruta, encoding="utf-8-sig") as fh:
                lineas = list(csv.DictReader(fh, delimiter=";"))
        finally:
            os.unlink(ruta)
        self.assertEqual(len(lineas), 2)
        self.assertEqual({int(l["semana"]) for l in lineas}, {5, 6})
        self.assertEqual(lineas[0]["organizacion"], "HOSP. A")
        self.assertEqual(lineas[0]["registro_oficina"], "4")
        self.assertEqual(lineas[0]["certificados"], "1")
