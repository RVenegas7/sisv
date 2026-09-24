"""Pruebas de registros: CRUD, alcance multicentro, permisos, CIE por fecha, dashboard."""

from tests_sisv import SISVBase, FECHA_CORTE


class NacimientoCRUDTests(SISVBase):
    def test_crear_nacimiento_cie11(self):
        self.login(self.u_trans_hcb)
        r = self.client.post(
            "/api/registros/nacimientos/",
            self.datos_nacimiento("N-0001"),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 201)
        data = r.json()["data"]
        self.assertEqual(data["registro_numero"], "N-0001")
        self.assertEqual(data["organizacion"], self.org_hcb.pk)
        self.assertEqual(data["organizacion_nombre"], self.org_hcb.nombre)
        self.assertEqual(data["cie11_detalle"]["codigo"], self.cie11_categoria.codigo)

    def test_centro_se_ejecuta_ignorando_org_ajena(self):
        self.login(self.u_trans_hcb)
        r = self.client.post(
            "/api/registros/nacimientos/",
            self.datos_nacimiento("N-0002", organizacion=self.org_cabudare.pk),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["data"]["organizacion"], self.org_hcb.pk)

    def test_fecha_antigua_exige_cie10(self):
        self.login(self.u_trans_hcb)
        r = self.client.post(
            "/api/registros/nacimientos/",
            self.datos_nacimiento("N-0003", fecha="2020-03-01"),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["data"]["version_cie"], "CIE10")
        self.assertEqual(r.json()["data"]["cie10_detalle"]["codigo"], self.cie10_antiguo.codigo)

    def test_cie11_no_valido_en_evento_historico(self):
        self.login(self.u_trans_hcb)
        datos = self.datos_nacimiento("N-0003", fecha="2020-03-01")
        datos["version_cie"] = "CIE11"
        r = self.client.post("/api/registros/nacimientos/", datos, content_type="application/json")
        self.assertEqual(r.status_code, 400)

    def test_categoria_obliga_subgrupo(self):
        self.login(self.u_trans_hcb)
        r = self.client.post(
            "/api/registros/nacimientos/",
            self.datos_nacimiento("N-0004", cie11=self.cie11_con_subgrupo_oblig),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 400)

    def test_subgrupo_valido(self):
        self.login(self.u_trans_hcb)
        r = self.client.post(
            "/api/registros/nacimientos/",
            self.datos_nacimiento("N-0005", cie11=self.cie11_subgrupo),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 201)

    def test_registro_duplicado_rechazado(self):
        self.login(self.u_trans_hcb)
        payload = self.datos_nacimiento("N-0006")
        self.assertEqual(self.client.post("/api/registros/nacimientos/", payload,
                                          content_type="application/json").status_code, 201)
        self.assertEqual(self.client.post("/api/registros/nacimientos/", payload,
                                          content_type="application/json").status_code, 400)

    def test_editar_y_listar(self):
        self.login(self.u_dire_hcb)
        creado = self.client.post("/api/registros/nacimientos/", self.datos_nacimiento("N-0007"),
                                  content_type="application/json").json()["data"]
        r = self.client.patch(
            f"/api/registros/nacimientos/{creado['id']}/",
            {"madre_nombres": "María"},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        lista = self.client.get("/api/registros/nacimientos/?q=0007")
        self.assertEqual(lista.status_code, 200)
        self.assertEqual(lista.json()["count"], 1)


class PermisosRegistrosTests(SISVBase):
    def test_epidemiologo_solo_lee(self):
        self.login(self.u_epi_regional)
        r = self.client.post("/api/registros/nacimientos/", self.datos_nacimiento("N-0100"),
                             content_type="application/json")
        self.assertEqual(r.status_code, 403)

    def test_transcriptor_no_elimina(self):
        self.login(self.u_trans_hcb)
        creado = self.client.post("/api/registros/nacimientos/", self.datos_nacimiento("N-0101"),
                                  content_type="application/json").json()["data"]
        r = self.client.delete(f"/api/registros/nacimientos/{creado['id']}/")
        self.assertEqual(r.status_code, 403)

    def test_director_elimina(self):
        self.login(self.u_dire_hcb)
        creado = self.client.post("/api/registros/nacimientos/", self.datos_nacimiento("N-0102"),
                                  content_type="application/json").json()["data"]
        r = self.client.delete(f"/api/registros/nacimientos/{creado['id']}/")
        self.assertEqual(r.status_code, 200)

    def test_codificador_edita(self):
        self.login(self.u_cod_hcb)
        creado = self.client.post("/api/registros/nacimientos/", self.datos_nacimiento("N-0103"),
                                  content_type="application/json").json()["data"]
        r = self.client.patch(f"/api/registros/nacimientos/{creado['id']}/", {"sexo": "M"},
                              content_type="application/json")
        self.assertEqual(r.status_code, 200)


class AlcanceTests(SISVBase):
    def test_centro_solo_ve_su_centro(self):
        self.login(self.u_trans_hcb)
        self.client.post("/api/registros/nacimientos/", self.datos_nacimiento("HA-001"),
                         content_type="application/json")
        self.login(self.u_trans_cabudare)
        self.client.post("/api/registros/nacimientos/", self.datos_nacimiento("CA-001"),
                         content_type="application/json")
        self.login(self.u_trans_hcb)
        r = self.client.get("/api/registros/nacimientos/")
        self.assertEqual(r.json()["count"], 1)
        self.assertEqual(r.json()["data"][0]["organizacion"], self.org_hcb.pk)

    def test_centro_no_ve_detalle_ajeno(self):
        self.login(self.u_trans_cabudare)
        creado = self.client.post("/api/registros/nacimientos/", self.datos_nacimiento("CA-002"),
                                  content_type="application/json").json()["data"]
        self.login(self.u_trans_hcb)
        r = self.client.get(f"/api/registros/nacimientos/{creado['id']}/")
        self.assertEqual(r.status_code, 404)

    def test_regional_ve_todo_el_estado(self):
        self.login(self.u_trans_hcb)
        self.client.post("/api/registros/nacimientos/", self.datos_nacimiento("HA-002", estado="Lara"),
                         content_type="application/json")
        self.login(self.u_trans_cabudare)
        self.client.post("/api/registros/nacimientos/", self.datos_nacimiento("CA-003", estado="Lara"),
                         content_type="application/json")
        self.login(self.u_trans_otro)
        self.client.post("/api/registros/nacimientos/", self.datos_nacimiento("FO-001", estado="Falcón"),
                         content_type="application/json")
        self.login(self.u_trans_regional)
        r = self.client.get("/api/registros/nacimientos/")
        self.assertEqual(r.json()["count"], 2)

    def test_regional_puede_elegir_centro_destino(self):
        self.login(self.u_trans_regional)
        r = self.client.post(
            "/api/registros/nacimientos/",
            self.datos_nacimiento("RE-001", organizacion=self.org_cabudare.pk),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["data"]["organizacion"], self.org_cabudare.pk)

    def test_admin_ve_todo(self):
        self.login(self.u_trans_hcb)
        self.client.post("/api/registros/nacimientos/", self.datos_nacimiento("HA-003"),
                         content_type="application/json")
        self.login(self.u_trans_otro)
        self.client.post("/api/registros/nacimientos/", self.datos_nacimiento("FO-002"),
                         content_type="application/json")
        self.login(self.u_admin)
        r = self.client.get("/api/registros/nacimientos/")
        self.assertEqual(r.json()["count"], 2)


class DashboardTests(SISVBase):
    def test_dashboard_anio_y_todos(self):
        self.login(self.u_admin)
        self.client.post("/api/registros/nacimientos/", self.datos_nacimiento("DB-2020", fecha="2020-03-01"),
                         content_type="application/json")
        self.client.post("/api/registros/nacimientos/", self.datos_nacimiento("DB-2023"),
                         content_type="application/json")
        r_todos = self.client.get("/api/registros/dashboard/?anio=todos")
        self.assertEqual(r_todos.status_code, 200)
        self.assertEqual(r_todos.json()["data"]["totales"]["nacimientos"], 2)
        r_2020 = self.client.get("/api/registros/dashboard/?anio=2020")
        self.assertEqual(r_2020.json()["data"]["totales"]["nacimientos"], 1)
        r_2030 = self.client.get("/api/registros/dashboard/?anio=2030")
        self.assertEqual(r_2030.json()["data"]["totales"]["nacimientos"], 0)

    def test_dashboard_por_semana(self):
        self.login(self.u_admin)
        self.client.post("/api/registros/nacimientos/", self.datos_nacimiento("DB-001"),
                         content_type="application/json")
        r = self.client.get("/api/registros/dashboard/?anio=2023")
        data = r.json()["data"]
        self.assertIn("por_semana", data)
        self.assertEqual(sum(sum(v.values()) for v in data["por_semana"].values()), 1)


class ReportesYConfigTests(SISVBase):
    def test_reportes_requieren_sesion(self):
        r = self.anon_logout().get("/api/registros/reportes/?desde=2023-01-01&hasta=2023-12-31")
        self.assertIn(r.status_code, (401, 403))

    def test_reportes_exportar_csv(self):
        self.login(self.u_admin)
        r = self.client.get("/api/registros/reportes/exportar/?desde=2023-01-01&hasta=2023-12-31")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r["Content-Type"].startswith("text/csv"))
        self.assertTrue(b"".join(r.streaming_content).startswith(b"\xef\xbb\xbf"))

    def test_config_transcriptor_denegado(self):
        self.login(self.u_trans_hcb)
        r = self.client.put(
            "/api/registros/configuracion/",
            {"estado": "Lara", "fecha_corte_cie11": FECHA_CORTE.isoformat()},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 403)

    def test_config_director_autorizado(self):
        self.login(self.u_dire_hcb)
        r = self.client.put(
            "/api/registros/configuracion/",
            {"estado": "Lara", "municipio": "Iribarren", "parroquia": "Santa Rosa",
             "fecha_corte_cie11": FECHA_CORTE.isoformat()},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        r = self.client.get("/api/registros/configuracion/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["data"]["estado"], "Lara")

    def test_reporte_comparativo(self):
        self.login(self.u_admin)
        self.client.post("/api/registros/nacimientos/", self.datos_nacimiento("CMP-2023"),
                         content_type="application/json")
        r = self.client.get("/api/registros/reportes/comparativo/?anio1=2023&anio2=2022")
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertEqual(data["anio1"], 2023)
        claves = [s["clave"] for s in data["series"]]
        self.assertEqual(claves, ["nacimientos", "muertes", "muertes_maternas", "muertes_neonatales", "mmi"])
        self.assertEqual(data["totales"]["nacimientos"]["2023"], 1)
        self.assertEqual(len(data["semanas"]), 53)
        serie_nac = data["series"][0]["anio1"]
        self.assertEqual(sum(serie_nac.values()), 1)


class DefuncionYFichaTests(SISVBase):
    def test_crear_defuncion(self):
        self.login(self.u_trans_hcb)
        r = self.client.post(
            "/api/registros/defunciones/",
            {"registro_numero": "D-0001", "fecha_evento": "2023-06-01", "version_cie": "CIE11",
             "cie11": self.cie11_categoria.pk, "sexo": "F",
             "fallecido_nombres": "Pedro", "fallecido_apellidos": "Gómez"},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 201)

    def test_crear_ficha(self):
        self.login(self.u_trans_hcb)
        r = self.client.post(
            "/api/registros/fichas-vigilancia/",
            {"codigo_notificacion": "FV-0001", "nombre_evento": "Dengue",
             "fecha_evento": "2023-06-01", "fecha_notificacion": "2023-06-02",
             "version_cie": "CIE11", "cie11": self.cie11_categoria.pk,
             "sexo": "F", "paciente_nombres": "María", "paciente_apellidos": "Rojas",
             "clasificacion": "CONFIRMADO"},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 201)