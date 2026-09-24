"""Pruebas de autenticación, control de intentos y permisos de organización/usuario."""

from django.core.cache import cache

from seguridad.models import Organizacion, Perfil
from seguridad.throttle import MAX_INTENTOS
from tests_sisv import SISVBase


class AuthTests(SISVBase):
    def test_csrf_publico(self):
        r = self.anon_logout().get("/api/auth/csrf/")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["data"]["csrf"])

    def test_me_sin_sesion_devuelve_401(self):
        r = self.anon_logout().get("/api/auth/me/")
        self.assertEqual(r.status_code, 401)

    def test_login_valido(self):
        r = self.anon_logout().post(
            "/api/auth/login/", {"username": "trans_hcb", "password": "clave.test.123"},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertEqual(data["username"], "trans_hcb")
        self.assertEqual(data["rol"], Perfil.ROL_TRANSCRIPTOR)
        self.assertEqual(data["organizacion"]["id"], self.org_hcb.pk)

    def test_login_clave_incorrecta(self):
        r = self.anon_logout().post(
            "/api/auth/login/", {"username": "trans_hcb", "password": "mala"},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 401)

    def test_login_bloquea_tras_intentos(self):
        self.anon_logout()
        remoto = {"REMOTE_ADDR": "203.0.113.55"}
        for _ in range(MAX_INTENTOS):
            r = self.client.post(
                "/api/auth/login/", {"username": "x", "password": "y"},
                content_type="application/json", **remoto,
            )
            self.assertIn(r.status_code, (401, 429))
        r = self.client.post(
            "/api/auth/login/", {"username": "x", "password": "y"},
            content_type="application/json", **remoto,
        )
        self.assertEqual(r.status_code, 429)
        cache.delete(f"auth_bloq:203.0.113.55")
        cache.delete(f"auth_login:203.0.113.55:*")

    def test_logout_invalida_sesion(self):
        self.login(self.u_trans_hcb)
        r = self.client.post("/api/auth/logout/", content_type="application/json")
        self.assertEqual(r.status_code, 200)
        r = self.anon_logout().get("/api/auth/me/")
        self.assertEqual(r.status_code, 401)

    def test_endpoint_privado_requiere_sesion(self):
        r = self.anon_logout().get("/api/registros/nacimientos/")
        self.assertIn(r.status_code, (401, 403))


class OrganizacionPermisosTests(SISVBase):
    def test_transcriptor_no_puede_crear_organizacion(self):
        self.login(self.u_trans_hcb)
        r = self.client.post(
            "/api/seguridad/organizaciones/",
            {"codigo": "NUEVO", "nombre": "Nuevo centro"},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 403)

    def test_director_puede_crear_organizacion(self):
        self.login(self.u_dire_hcb)
        r = self.client.post(
            "/api/seguridad/organizaciones/",
            {"codigo": "NUEVO", "nombre": "Nuevo centro", "nivel": "CENTRO"},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertTrue(Organizacion.objects.filter(codigo="NUEVO").exists())

    def test_codigo_duplicado_rechazado(self):
        self.login(self.u_dire_hcb)
        r = self.client.post(
            "/api/seguridad/organizaciones/",
            {"codigo": "HCB", "nombre": "Otro"},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 400)

    def test_transcriptor_no_elimina_usuario(self):
        self.login(self.u_trans_hcb)
        r = self.client.delete(f"/api/seguridad/usuarios/{self.u_cod_hcb.pk}/")
        self.assertEqual(r.status_code, 403)

    def test_director_crea_usuario_con_perfil(self):
        self.login(self.u_dire_hcb)
        r = self.client.post(
            "/api/seguridad/usuarios/",
            {"username": "nuevo", "password": "clave.nueva.1", "rol": "TRANSCRIPTOR",
             "organizacion": self.org_hcb.pk},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 201)
        u = self.u_trans_otro.__class__.objects.get(username="nuevo")
        self.assertEqual(u.perfil.rol, Perfil.ROL_TRANSCRIPTOR)
        self.assertEqual(u.perfil.organizacion_id, self.org_hcb.pk)