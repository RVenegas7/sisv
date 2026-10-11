"""Pruebas del Consolidado Semanal de ENO (vigilancia)."""

from datetime import date

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from tests_sisv import SISVBase

from .legacy_mapeo import GRUPO_EDAD_LEGACY, LEGACY_ENFERMEDAD_EVENTO, por_evento_id
from .models import ConsolidadoEpi15, ConsolidadoSemanal, EventoENO, FilaConsolidado, FilaEpi15
from .services import (
    fin_anio_epidemiologico,
    inicio_anio_epidemiologico,
    rango_anio_epidemiologico,
    semana_epidemiologica,
    semanas_en_anio,
)


class SemanaEpidemiologicaTests(SimpleTestCase):
    """La semana venezolana va de domingo a sábado y NO es la ISO 8601.

    Cifras de la oficina y verificadas contra `sismai."DOCUMENTO"` (ANNO/PERIODO):
    2025 tiene 53 semanas, 2026 tiene 52; la semana 53 de 2025 va del 28-12-2025 al
    03-01-2026 y la semana 1 de 2026 arranca el 04-01-2026.
    """

    def test_anios_con_53_y_52_semanas(self):
        self.assertEqual(semanas_en_anio(2025), 53)
        self.assertEqual(semanas_en_anio(2026), 52)
        self.assertEqual(semanas_en_anio(2027), 52)

    def test_2025_tiene_53_y_2026_52_invertido_contra_iso(self):
        for anio, iso in ((2025, 52), (2026, 53)):
            with self.subTest(anio=anio):
                self.assertNotEqual(semanas_en_anio(anio), iso)

    def test_la_semana_53_de_2025_se_mete_a_enero(self):
        self.assertEqual(semana_epidemiologica(date(2025, 12, 28)), (2025, 53))
        for dia in (1, 2, 3):
            with self.subTest(dia=dia):
                self.assertEqual(semana_epidemiologica(date(2026, 1, dia)), (2025, 53))

    def test_la_semana_1_de_2026_arranca_el_4_de_enero(self):
        self.assertEqual(semana_epidemiologica(date(2026, 1, 4)), (2026, 1))
        self.assertEqual(semana_epidemiologica(date(2026, 1, 10)), (2026, 1))
        self.assertEqual(semana_epidemiologica(date(2026, 1, 11)), (2026, 2))

    def test_2025_empieza_con_la_semana_que_contiene_el_1_de_enero(self):
        self.assertEqual(inicio_anio_epidemiologico(2025), date(2024, 12, 29))
        self.assertEqual(semana_epidemiologica(date(2025, 1, 1)), (2025, 1))

    def test_ultima_semana_cierra_en_sabado(self):
        for anio in (2025, 2026):
            with self.subTest(anio=anio):
                self.assertEqual(fin_anio_epidemiologico(anio).weekday(), 6)  # sábado
                self.assertEqual(inicio_anio_epidemiologico(anio).weekday(), 6)

    def test_la_semana_37_de_2026_es_la_que_cerro_el_19_de_septiembre(self):
        # Es la que el legacy consolidó el 21-22/09 y la que la oficina tenía reportada.
        self.assertEqual(semana_epidemiologica(date(2026, 9, 19)), (2026, 37))
        self.assertEqual(semana_epidemiologica(date(2026, 9, 13)), (2026, 37))
        self.assertEqual(semana_epidemiologica(date(2026, 9, 20)), (2026, 38))
        # La ISO de 2026 le daría 38: por eso el código anterior se equivocaba.
        self.assertEqual(date(2026, 9, 19).isocalendar()[1], 38)

    def test_rango_del_anio_para_filtrar(self):
        self.assertEqual(rango_anio_epidemiologico(2026), (date(2026, 1, 4), date(2027, 1, 2)))
        self.assertEqual(rango_anio_epidemiologico(2025), (date(2024, 12, 29), date(2026, 1, 3)))

    def test_todas_las_fechas_de_un_anio_dan_ese_anio(self):
        for anio in (2025, 2026):
            with self.subTest(anio=anio):
                inicio, hasta = rango_anio_epidemiologico(anio)
                dia = inicio
                while dia <= hasta:
                    self.assertEqual(semana_epidemiologica(dia)[0], anio)
                    dia += date.resolution
                # y ninguna fecha de la semana 53 se cuela en el año siguiente
                for dia in (date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3)):
                    self.assertEqual(semana_epidemiologica(dia)[0], 2025)


class EventosENOTests(SISVBase):
    def test_listar_eventos(self):
        self.login(self.u_trans_hcb)
        r = self.client.get("/api/vigilancia/eventos-eno/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 2)

    def test_filtrar_por_grupo(self):
        self.login(self.u_trans_hcb)
        r = self.client.get("/api/vigilancia/eventos-eno/?grupo=TRANSMISIBLES")
        self.assertEqual(r.json()["count"], 2)
        r = self.client.get("/api/vigilancia/eventos-eno/?grupo=IRA")
        self.assertEqual(r.json()["count"], 0)


class ConsolidadoTests(SISVBase):
    def _crear(self, uid):
        return self.client.post(
            "/api/vigilancia/consolidados/",
            {"anio": 2026, "semana": 3, "tipo": "MORBILIDAD"},
            content_type="application/json",
        )

    def test_crear_siembra_filas_del_catalogo(self):
        self.login(self.u_trans_hcb)
        r = self._crear("C-01")
        self.assertEqual(r.status_code, 201)
        data = r.json()["data"]
        self.assertEqual(data["anio"], 2026)
        self.assertEqual(len(data["filas"]), 2)

    def test_centro_org_forzada(self):
        self.login(self.u_trans_hcb)
        r = self.client.post(
            "/api/vigilancia/consolidados/",
            {"anio": 2026, "semana": 4, "tipo": "MORBILIDAD", "organizacion": self.org_cabudare.pk},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 201)
        c = ConsolidadoSemanal.objects.get()
        self.assertEqual(c.organizacion_id, self.org_hcb.pk)

    def test_regional_puede_elegir_destino(self):
        self.login(self.u_trans_regional)
        r = self.client.post(
            "/api/vigilancia/consolidados/",
            {"anio": 2026, "semana": 5, "tipo": "MORBILIDAD", "organizacion": self.org_cabudare.pk},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 201)
        c = ConsolidadoSemanal.objects.get()
        self.assertEqual(c.organizacion_id, self.org_cabudare.pk)

    def test_org_obligatoria_en_nivel_superior(self):
        self.login(self.u_admin)
        r = self.client.post(
            "/api/vigilancia/consolidados/",
            {"anio": 2026, "semana": 6, "tipo": "MORBILIDAD"},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 400)

    def test_alcance_centro_no_ve_consolidados_ajenos(self):
        self.login(self.u_trans_regional)
        self.client.post(
            "/api/vigilancia/consolidados/",
            {"anio": 2026, "semana": 7, "tipo": "MORBILIDAD", "organizacion": self.org_cabudare.pk},
            content_type="application/json",
        )
        self.login(self.u_trans_hcb)
        r = self.client.get("/api/vigilancia/consolidados/")
        self.assertEqual(r.json()["count"], 0)

    def test_transcriptor_no_elimina(self):
        self.login(self.u_trans_hcb)
        creado = self._crear("C-02").json()["data"]
        r = self.client.delete(f"/api/vigilancia/consolidados/{creado['id']}/")
        self.assertEqual(r.status_code, 403)

    def test_director_elimina(self):
        self.login(self.u_dire_hcb)
        creado = self._crear("C-03").json()["data"]
        r = self.client.delete(f"/api/vigilancia/consolidados/{creado['id']}/")
        self.assertEqual(r.status_code, 200)

    def test_exportar_csv(self):
        self.login(self.u_dire_hcb)
        r = self.client.get("/api/vigilancia/consolidados/exportar/?anio=2026")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r["Content-Type"].startswith("text/csv"))
        self.assertTrue(r.content.startswith(b"\xef\xbb\xbf"))

    def test_anonimo_bloqueado(self):
        r = self.anon_logout().get("/api/vigilancia/consolidados/")
        self.assertIn(r.status_code, (401, 403))


class ConsolidadoResumenTests(SISVBase):
    """Resumen por semana y «crear / abrir» del Consolidado Semanal (EPI-12/14)."""

    def _crear(self, uid, semana, org=None):
        self.login(uid)
        payload = {"anio": 2026, "semana": semana, "tipo": "MORBILIDAD"}
        if org is not None:
            payload["organizacion"] = org
        return self.client.post(
            "/api/vigilancia/consolidados/", payload, content_type="application/json"
        )

    def test_resumen_agrupa_por_semana(self):
        self._crear(self.u_admin, 3, self.org_hcb.pk)
        self._crear(self.u_admin, 3, self.org_cabudare.pk)
        fila = FilaConsolidado.objects.filter(
            consolidado__anio=2026, consolidado__semana=3
        ).first()
        fila.menor_1_h = 4
        fila.save(update_fields=["menor_1_h"])
        self.login(self.u_admin)
        r = self.client.get("/api/vigilancia/consolidados/resumen/?anio=2026")
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["semana"], 3)
        self.assertEqual(data[0]["consolidados"], 2)
        self.assertEqual(data[0]["establecimientos"], 2)
        self.assertEqual(data[0]["morbilidad"], 4)

    def test_resumen_exige_anio(self):
        self.login(self.u_admin)
        r = self.client.get("/api/vigilancia/consolidados/resumen/")
        self.assertEqual(r.status_code, 400)

    def test_crear_abre_el_existente(self):
        primero = self._crear(self.u_trans_hcb, 8).json()["data"]
        segundo = self.client.post(
            "/api/vigilancia/consolidados/",
            {"anio": 2026, "semana": 8, "tipo": "MORBILIDAD"},
            content_type="application/json",
        )
        self.assertEqual(segundo.status_code, 200)
        self.assertEqual(segundo.json()["data"]["id"], primero["id"])
        self.assertEqual(ConsolidadoSemanal.objects.filter(anio=2026, semana=8).count(), 1)


class ConsolidadoEpi15Tests(SISVBase):
    def test_crear_con_traza_legacy(self):
        c = ConsolidadoEpi15.objects.create(
            organizacion=self.org_hcb, anio=2019, semana=12,
            estado="CERRADO", origen="PROPIO", legacy_tabla="RENGLON_EPI15",
        )
        f = FilaEpi15.objects.create(
            consolidado=c, legacy_id=67910, nombre_legacy="CÓLERA",
            evento=self.ev_dengue, casosp=3, casoss=1, casosx=0,
        )
        self.assertEqual(f.total, 4)
        self.assertEqual(c.anio, 2019)
        self.assertEqual(str(c), f"EPI-15 2019-S12 @ {self.org_hcb}")

    def test_unique_org_anio_semana(self):
        ConsolidadoEpi15.objects.create(organizacion=self.org_hcb, anio=2019, semana=12)
        with self.assertRaises(Exception):
            ConsolidadoEpi15.objects.create(organizacion=self.org_hcb, anio=2019, semana=12)

    def test_evento_puede_ser_nulo(self):
        c = ConsolidadoEpi15.objects.create(organizacion=self.org_hcb, anio=2019, semana=13)
        f = FilaEpi15.objects.create(
            consolidado=c, legacy_id=99999, nombre_legacy="SÍNDROME VIRAL",
            evento=None, casosp=5,
        )
        self.assertIsNone(f.evento)
        self.assertEqual(f.nombre_legacy, "SÍNDROME VIRAL")


class Epi15ResumenTests(SISVBase):
    """Resumen por semana del EPI-15 (solo lectura del legado)."""

    def test_resumen_por_semana(self):
        c = ConsolidadoEpi15.objects.create(organizacion=self.org_hcb, anio=2019, semana=12)
        FilaEpi15.objects.create(
            consolidado=c, legacy_id=1, nombre_legacy="CÓLERA",
            evento=self.ev_dengue, casosp=3, casoss=1, casosx=0,
        )
        c2 = ConsolidadoEpi15.objects.create(organizacion=self.org_cabudare, anio=2019, semana=12)
        FilaEpi15.objects.create(
            consolidado=c2, legacy_id=2, nombre_legacy="DENGUE",
            evento=self.ev_dengue, casosp=2,
        )
        self.login(self.u_admin)
        r = self.client.get("/api/vigilancia/epi15/resumen/?anio=2019")
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["semana"], 12)
        self.assertEqual(data[0]["casos"], 6)
        self.assertEqual(data[0]["consolidados"], 2)
        self.assertEqual(data[0]["establecimientos"], 2)

    def test_resumen_exige_anio(self):
        self.login(self.u_admin)
        r = self.client.get("/api/vigilancia/epi15/resumen/")
        self.assertEqual(r.status_code, 400)


class LegacyMapeoTests(SISVBase):
    def test_por_evento_id_resuelve_codigos(self):
        EventoENO.objects.create(codigo_evento="ENO_colera", nombre="Cólera")
        EventoENO.objects.create(codigo_evento="ENO_tuberculosis", nombre="TB")
        por_codigo = dict(EventoENO.objects.values_list("codigo_evento", "id"))
        mapa = por_evento_id(por_codigo)
        self.assertIn(67910, mapa)  # cólera
        self.assertIn(67905, mapa)  # tuberculosis
        self.assertEqual(mapa[67910], por_codigo["ENO_colera"])
        self.assertEqual(mapa[67905], por_codigo["ENO_tuberculosis"])
        for v in mapa.values():
            self.assertIn(v, por_codigo.values())

    def test_legacy_enfermedad_evento_es_no_vacio(self):
        self.assertGreater(len(LEGACY_ENFERMEDAD_EVENTO), 50)
        claves_legitimas = all(isinstance(k, int) for k in LEGACY_ENFERMEDAD_EVENTO)
        self.assertTrue(claves_legitimas)

    def test_grupos_edad_legacy_cubren_matriz(self):
        for g in ("menor_1", "de_1_4", "de_5_6", "de_7_9", "de_10_11", "de_12_14",
                  "de_15_19", "de_20_24", "de_25_44", "de_45_59", "de_60_64", "de_65",
                  "edad_ignorada"):
            self.assertIn(g, GRUPO_EDAD_LEGACY.values())

    def test_edad_ignorada_anota_en_hombres(self):
        c = ConsolidadoSemanal.objects.create(
            organizacion=self.org_hcb, anio=2019, semana=12, tipo="MORBILIDAD",
            estado="CERRADO",
        )
        f = FilaConsolidado.objects.create(
            consolidado=c, evento=self.ev_dengue, edad_ignorada_h=4, edad_ignorada_m=0,
        )
        self.assertEqual(f.total, 4)