"""Pruebas del módulo de registradores civiles con historial de vigencias."""

from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from tests_sisv import SISVBase

from registradores.models import DesignacionRegistrador, RegistradorCivil, RegistroCivil
from registradores.services import (
    consolidar_registradores,
    dividir_nombre,
    nacionalidad_legacy,
    normalizar_cedula,
    normalizar_nombre,
)

User = get_user_model()


class RegistradoresBase(SISVBase):
    def setUp(self):
        self.rc_hcb = RegistroCivil.objects.create(
            nombre="Registro Civil de Barquisimeto",
            organizacion=self.org_hcb,
            estado="Lara",
            municipio="Iribarren",
        )
        self.rc_otro = RegistroCivil.objects.create(
            nombre="Registro Civil de Coro",
            organizacion=self.org_otro_estado,
            estado="Falcon",
            municipio="Miranda",
        )
        self.reg_a = RegistradorCivil.objects.create(
            nacionalidad="V", cedula="12345678", nombres="Ana", apellidos="Pérez"
        )
        self.reg_b = RegistradorCivil.objects.create(
            nacionalidad="V", cedula="87654321", nombres="Beto", apellidos="Gómez"
        )

    def crear_designacion(self, registrador, desde, hasta=None, registro_civil=None,
                          cargo=DesignacionRegistrador.CARGO_TITULAR):
        return DesignacionRegistrador.objects.create(
            registro_civil=registro_civil or self.rc_hcb,
            registrador=registrador,
            cargo=cargo,
            desde=desde,
            hasta=hasta,
        )

    def datos_registro_civil(self, **extra):
        datos = {
            "nombre": "Registro Civil de Cabudare",
            "organizacion": self.org_cabudare.pk,
            "estado": "Lara",
            "municipio": "Palavecino",
        }
        datos.update(extra)
        return datos

    def datos_designacion(self, registrador=None, **extra):
        datos = {
            "registro_civil": self.rc_hcb.pk,
            "registrador": (registrador or self.reg_a).pk,
            "cargo": DesignacionRegistrador.CARGO_TITULAR,
            "desde": "2020-01-01",
        }
        datos.update(extra)
        return datos


class RegistroCivilApiTests(RegistradoresBase):
    def test_lectura_autenticada(self):
        self.login(self.u_trans_hcb)
        r = self.client.get("/api/registradores/registros-civiles/")
        self.assertEqual(r.status_code, 200)
        nombres = [x["nombre"] for x in r.json()["data"]]
        self.assertIn("Registro Civil de Barquisimeto", nombres)

    def test_escritura_requiere_permiso(self):
        self.login(self.u_trans_hcb)
        r = self.client.post(
            "/api/registradores/registros-civiles/",
            self.datos_registro_civil(),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 403)

    def test_director_crea(self):
        self.login(self.u_dire_hcb)
        r = self.client.post(
            "/api/registradores/registros-civiles/",
            self.datos_registro_civil(),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["data"]["nombre"], "Registro Civil de Cabudare")

    def test_eliminar_registro_con_designaciones_protegido(self):
        self.crear_designacion(self.reg_a, "2020-01-01")
        self.login(self.u_dire_hcb)
        r = self.client.delete(f"/api/registradores/registros-civiles/{self.rc_hcb.pk}/")
        self.assertEqual(r.status_code, 400)


class RegistradorApiTests(RegistradoresBase):
    def test_cedula_duplicada(self):
        self.login(self.u_dire_hcb)
        r = self.client.post(
            "/api/registradores/registradores/",
            {
                "nacionalidad": "V",
                "cedula": "12345678",
                "nombres": "Otra",
                "apellidos": "Persona",
            },
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 400)

    def test_desactivar_registrador(self):
        self.login(self.u_dire_hcb)
        r = self.client.patch(
            f"/api/registradores/registradores/{self.reg_a.pk}/",
            {"activo": False},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        self.reg_a.refresh_from_db()
        self.assertFalse(self.reg_a.activo)

    def test_eliminar_registrador_con_designaciones_protegido(self):
        self.crear_designacion(self.reg_a, "2020-01-01")
        self.login(self.u_dire_hcb)
        r = self.client.delete(f"/api/registradores/registradores/{self.reg_a.pk}/")
        self.assertEqual(r.status_code, 400)


class DesignacionApiTests(RegistradoresBase):
    def test_vigencia_invalida(self):
        self.login(self.u_dire_hcb)
        r = self.client.post(
            "/api/registradores/designaciones/",
            self.datos_designacion(desde="2024-01-01", hasta="2023-01-01"),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 400)

    def test_designacion_duplicada(self):
        self.crear_designacion(self.reg_a, "2020-01-01")
        self.login(self.u_dire_hcb)
        r = self.client.post(
            "/api/registradores/designaciones/",
            self.datos_designacion(self.reg_a, desde="2020-01-01"),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 400)

    def test_crear_y_listar_vigentes(self):
        self.crear_designacion(self.reg_a, "2020-01-01", hasta="2022-12-31")
        self.crear_designacion(self.reg_b, "2023-01-01")
        self.login(self.u_dire_hcb)
        r = self.client.get("/api/registradores/designaciones/?vigente=1")
        self.assertEqual(r.status_code, 200)
        datos = r.json()["data"]
        self.assertEqual(len(datos), 1)
        self.assertEqual(datos[0]["registrador_cedula"], "V-87654321")
        self.assertTrue(datos[0]["vigente"])


class QuienFirmabaTests(RegistradoresBase):
    def test_retroactivo(self):
        self.crear_designacion(self.reg_a, "2020-01-01", hasta="2022-12-31")
        self.crear_designacion(self.reg_b, "2023-01-01")
        self.login(self.u_trans_hcb)

        r = self.client.get(
            f"/api/registradores/quien-firmaba/?registro_civil={self.rc_hcb.pk}&fecha=2021-06-15"
        )
        self.assertEqual(r.status_code, 200)
        vigentes = r.json()["data"]["vigentes"]
        self.assertEqual(len(vigentes), 1)
        self.assertEqual(vigentes[0]["registrador_cedula"], "V-12345678")

        r = self.client.get(
            f"/api/registradores/quien-firmaba/?registro_civil={self.rc_hcb.pk}&fecha=2024-02-01"
        )
        vigentes = r.json()["data"]["vigentes"]
        self.assertEqual(len(vigentes), 1)
        self.assertEqual(vigentes[0]["registrador_cedula"], "V-87654321")

    def test_solape_titular_y_suplente(self):
        self.crear_designacion(self.reg_a, "2020-01-01", cargo="TITULAR")
        self.crear_designacion(self.reg_b, "2021-01-01", cargo="SUPLENTE")
        self.login(self.u_trans_hcb)
        r = self.client.get(
            f"/api/registradores/quien-firmaba/?registro_civil={self.rc_hcb.pk}&fecha=2022-01-01"
        )
        self.assertEqual(len(r.json()["data"]["vigentes"]), 2)

    def test_parametros_invalidos(self):
        self.login(self.u_trans_hcb)
        r = self.client.get("/api/registradores/quien-firmaba/")
        self.assertEqual(r.status_code, 400)
        r = self.client.get(
            f"/api/registradores/quien-firmaba/?registro_civil={self.rc_hcb.pk}&fecha=15-06-2021"
        )
        self.assertEqual(r.status_code, 400)
        r = self.client.get(
            "/api/registradores/quien-firmaba/?registro_civil=abc&fecha=2021-06-15"
        )
        self.assertEqual(r.status_code, 404)


class SembrarRegistradoresLegacyTests(SISVBase):
    def test_normalizar_cedula(self):
        self.assertEqual(normalizar_cedula("V-12.345.678"), "12345678")
        self.assertEqual(normalizar_cedula(""), "")
        self.assertEqual(normalizar_cedula(None), "")

    def test_normalizar_nombre(self):
        self.assertEqual(normalizar_nombre("  pérez   ana "), "PÉREZ ANA")

    def test_nacionalidad_legacy(self):
        self.assertEqual(nacionalidad_legacy(1), "V")
        self.assertEqual(nacionalidad_legacy(2), "E")
        self.assertEqual(nacionalidad_legacy(None), "V")

    def test_dividir_nombre(self):
        self.assertEqual(dividir_nombre("ESPINOZA NELIDA"), ("NELIDA", "ESPINOZA"))
        self.assertEqual(dividir_nombre("VALERA ELVIA ROSA"), ("ELVIA ROSA", "VALERA"))
        self.assertEqual(
            dividir_nombre("GARCIA LOPEZ JUAN CARLOS"), ("JUAN CARLOS", "GARCIA LOPEZ")
        )
        self.assertEqual(dividir_nombre("COLMENAREZ"), ("COLMENAREZ", ""))

    def test_consolidar_agrupa_por_cedula_y_elige_canonico(self):
        filas = [
            (1, "V-74.492.39", "ESPINOZA NELIDA"),
            (1, "7449239", "ESPINOZA NELIDA"),
            (1, "7449239", "NELIDA ESPINOZA"),
            (2, "12345678", "SMITH JOHN"),
            (1, "", "SIN CEDULA"),
            (1, "99999999", "   "),
        ]
        personas, descartados = consolidar_registradores(filas)
        por_cedula = {p["cedula"]: p for p in personas}
        self.assertEqual(set(por_cedula), {"7449239", "12345678"})

        ana = por_cedula["7449239"]
        self.assertEqual(ana["nacionalidad"], "V")
        self.assertEqual(ana["nombres"], "NELIDA")
        self.assertEqual(ana["apellidos"], "ESPINOZA")
        self.assertEqual(ana["variantes"], 2)
        self.assertEqual(ana["certificados"], 3)

        self.assertEqual(por_cedula["12345678"]["nacionalidad"], "E")
        self.assertEqual(descartados["sin_cedula"], 1)
        self.assertEqual(descartados["sin_nombre"], 1)

    def test_comando_avisa_sin_legacy(self):
        salida = StringIO()
        call_command("sembrar_registradores_legacy", stderr=salida)
        self.assertIn("legacy", salida.getvalue().lower())


class AlcanceTests(RegistradoresBase):
    def test_centro_solo_ve_su_registro(self):
        self.login(self.u_trans_hcb)
        r = self.client.get("/api/registradores/registros-civiles/")
        nombres = [x["nombre"] for x in r.json()["data"]]
        self.assertIn("Registro Civil de Barquisimeto", nombres)
        self.assertNotIn("Registro Civil de Coro", nombres)

    def test_regional_ve_su_estado(self):
        self.login(self.u_trans_regional)
        r = self.client.get("/api/registradores/registros-civiles/")
        nombres = [x["nombre"] for x in r.json()["data"]]
        self.assertIn("Registro Civil de Barquisimeto", nombres)
        self.assertNotIn("Registro Civil de Coro", nombres)

    def test_centro_no_ve_designacion_ajena(self):
        self.crear_designacion(self.reg_a, "2020-01-01", registro_civil=self.rc_otro)
        self.login(self.u_trans_hcb)
        r = self.client.get("/api/registradores/designaciones/")
        self.assertEqual(r.json()["data"], [])
