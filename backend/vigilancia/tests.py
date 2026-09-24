"""Pruebas del Consolidado Semanal de ENO (vigilancia)."""

from django.core.exceptions import ValidationError
from tests_sisv import SISVBase

from .legacy_mapeo import GRUPO_EDAD_LEGACY, LEGACY_ENFERMEDAD_EVENTO, por_evento_id
from .models import ConsolidadoEpi15, ConsolidadoSemanal, EventoENO, FilaConsolidado, FilaEpi15


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