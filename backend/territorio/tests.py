"""Pruebas del módulo territorio: división territorial y ASIC."""

from tests_sisv import SISVBase


class TerritorioTests(SISVBase):
    def test_estados_requieren_sesion(self):
        r = self.anon_logout().get("/api/territorio/?nivel=ESTADO")
        self.assertIn(r.status_code, (401, 403))

    def test_arbol_estados(self):
        self.login(self.u_trans_hcb)
        r = self.client.get("/api/territorio/?nivel=ESTADO")
        self.assertEqual(r.status_code, 200)
        nombres = [x["nombre"] for x in r.json()["data"]]
        self.assertIn("Lara", nombres)

    def test_municipios_hijos(self):
        self.login(self.u_trans_hcb)
        r = self.client.get(f"/api/territorio/?nivel=MUNICIPIO&padre={self.par_estado.pk}")
        nombres = [x["nombre"] for x in r.json()["data"]]
        self.assertIn("Iribarren", nombres)

    def test_ruta_territorial(self):
        self.login(self.u_trans_hcb)
        r = self.client.get(f"/api/territorio/{self.par_comunidad.pk}/ruta/")
        self.assertEqual(r.status_code, 200)
        camino = r.json()["data"]
        self.assertEqual([x["nombre"] for x in camino], ["Lara", "Iribarren", "Santa Rosa", "La Mata"])


class ASICPermisosTests(SISVBase):
    def _payload(self):
        return {
            "nombre": "ASIC de Prueba",
            "codigo": "ASIC-TEST-1",
            "parroquia": self.par_parroquia.pk,
            "direccion": "Av. Libertador",
        }

    def test_listar_asic(self):
        self.login(self.u_trans_hcb)
        r = self.client.get("/api/territorio/asic/")
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(r.json()["count"], 1)

    def test_transcriptor_no_puede_crear(self):
        self.login(self.u_trans_hcb)
        r = self.client.post("/api/territorio/asic/", self._payload(), content_type="application/json")
        self.assertEqual(r.status_code, 403)

    def test_director_crea_y_edita(self):
        self.login(self.u_dire_hcb)
        r = self.client.post("/api/territorio/asic/", self._payload(), content_type="application/json")
        self.assertEqual(r.status_code, 201)
        asic_id = r.json()["data"]["id"]
        r = self.client.patch(
            f"/api/territorio/asic/{asic_id}/",
            {"responsable": "Dra. Rivas"},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)

    def test_director_elimina(self):
        self.login(self.u_dire_hcb)
        r = self.client.post("/api/territorio/asic/", self._payload(), content_type="application/json")
        asic_id = r.json()["data"]["id"]
        r = self.client.delete(f"/api/territorio/asic/{asic_id}/")
        self.assertEqual(r.status_code, 200)

    def test_director_asocia_comunidades(self):
        self.login(self.u_dire_hcb)
        r = self.client.post("/api/territorio/asic/", self._payload(), content_type="application/json")
        asic_id = r.json()["data"]["id"]
        r = self.client.patch(
            f"/api/territorio/asic/{asic_id}/",
            {"comunidades": [self.par_comunidad.pk]},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["data"]["comunidad_count"], 1)
        nombres = [c["nombre"] for c in r.json()["data"]["comunidades"]]
        self.assertEqual(nombres, ["La Mata"])

    def test_rechaza_comunidades_de_otro_nivel(self):
        self.login(self.u_dire_hcb)
        r = self.client.post("/api/territorio/asic/", self._payload(), content_type="application/json")
        asic_id = r.json()["data"]["id"]
        r = self.client.patch(
            f"/api/territorio/asic/{asic_id}/",
            {"comunidades": [self.par_parroquia.pk]},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 400)

    def test_limpia_comunidades(self):
        self.login(self.u_dire_hcb)
        r = self.client.post("/api/territorio/asic/", self._payload(), content_type="application/json")
        asic_id = r.json()["data"]["id"]
        self.client.patch(
            f"/api/territorio/asic/{asic_id}/",
            {"comunidades": [self.par_comunidad.pk]},
            content_type="application/json",
        )
        r = self.client.patch(
            f"/api/territorio/asic/{asic_id}/",
            {"comunidades": []},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["data"]["comunidad_count"], 0)