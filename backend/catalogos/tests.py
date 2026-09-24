"""Pruebas del módulo catalogos: CIE-10, CIE-11 y mapeos."""

from tests_sisv import SISVBase


class CatalogosTests(SISVBase):
    def test_cie10_buscar_requiere_sesion(self):
        r = self.anon_logout().get("/api/catalogos/cie10/buscar/?q=A15")
        self.assertIn(r.status_code, (401, 403))

    def test_cie10_buscar_por_texto_y_codigo(self):
        self.login(self.u_trans_hcb)
        r = self.client.get("/api/catalogos/cie10/buscar/?q=A15")
        self.assertEqual(r.status_code, 200)
        codigos = [x["codigo"] for x in r.json()["data"]]
        self.assertIn("A15.0", codigos)
        r = self.client.get("/api/catalogos/cie10/buscar/?q=tuberculosis")
        self.assertEqual(len(r.json()["data"]), 1)

    def test_cie11_buscar(self):
        self.login(self.u_trans_hcb)
        r = self.client.get("/api/catalogos/cie11/buscar/?q=CA40")
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(r.json()["data"]), 1)

    def test_cie11_arbol(self):
        self.login(self.u_trans_hcb)
        r = self.client.get("/api/catalogos/cie11/arbol/")
        self.assertEqual(r.status_code, 200)

    def test_mapeos_por_cie10(self):
        self.login(self.u_trans_hcb)
        r = self.client.get("/api/catalogos/mapeos/?cie10=A15.0")
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["tipo"], "EXA")