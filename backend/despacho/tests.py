"""Pruebas del módulo de despacho de talonarios de certificados."""

from django.contrib.auth import get_user_model
from tests_sisv import SISVBase

from despacho.models import NovedadCertificado, Talonario
from registros.models import Defuncion, Nacimiento
from seguridad.models import Perfil

User = get_user_model()


class DespachoBase(SISVBase):
    def setUp(self):
        self.u_jefe = User.objects.create_user(username="jefe", password="clave.test.123")
        Perfil.objects.create(user=self.u_jefe, rol=Perfil.ROL_JEFE_UNIDAD, organizacion=self.org_hcb)

    def crear_talonario(self, tipo=Talonario.TIPO_DEFUNCION, centro=None, desde=1, hasta=10,
                        fecha="2026-01-05", recibe="Dra. Jefa"):
        return Talonario.objects.create(
            tipo=tipo, centro=centro or self.org_hcb, fecha_entrega=fecha,
            serie_desde=desde, serie_hasta=hasta, responsable_recibe=recibe,
        )

    def crear_defuncion(self, numero, organizacion=None, fecha="2026-01-10",
                        nombres="Pedro", apellidos="Gómez"):
        return Defuncion.objects.create(
            registro_numero=numero, fecha_evento=fecha, version_cie="CIE11",
            cie11=self.cie11_categoria, sexo="F",
            fallecido_nombres=nombres, fallecido_apellidos=apellidos,
            organizacion=organizacion or self.org_hcb,
        )

    def crear_nacimiento(self, numero, organizacion=None, fecha="2026-01-10"):
        return Nacimiento.objects.create(
            registro_numero=numero, fecha_evento=fecha, version_cie="CIE11",
            cie11=self.cie11_categoria, sexo="F",
            madre_nombres="Ana", madre_apellidos="Pérez", madre_cedula="V-12345678",
            madre_edad=25, organizacion=organizacion or self.org_hcb,
        )

    def datos_talonario(self, **extra):
        datos = {
            "tipo": Talonario.TIPO_DEFUNCION,
            "centro": self.org_hcb.pk,
            "fecha_entrega": "2026-01-05",
            "serie_desde": 1,
            "serie_hasta": 10,
            "responsable_recibe": "Dra. Jefa",
        }
        datos.update(extra)
        return datos


class DespachoTalonarioTests(DespachoBase):
    def test_transcriptor_no_puede_crear(self):
        self.login(self.u_trans_hcb)
        r = self.client.post("/api/despacho/talonarios/", self.datos_talonario(),
                             content_type="application/json")
        self.assertEqual(r.status_code, 403)

    def test_jefe_unidad_crea_y_calcula_cantidad(self):
        self.login(self.u_jefe)
        r = self.client.post("/api/despacho/talonarios/", self.datos_talonario(),
                             content_type="application/json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["data"]["cantidad"], 10)
        self.assertEqual(Talonario.objects.count(), 1)

    def test_serie_invalida(self):
        self.login(self.u_jefe)
        r = self.client.post(
            "/api/despacho/talonarios/",
            self.datos_talonario(serie_desde=20, serie_hasta=5),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 400)

    def test_serie_duplicada(self):
        self.crear_talonario(desde=1, hasta=10)
        self.login(self.u_jefe)
        r = self.client.post("/api/despacho/talonarios/", self.datos_talonario(),
                             content_type="application/json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Talonario.objects.count(), 1)

    def test_eliminar_requiere_puede_despachar(self):
        tal = self.crear_talonario()
        self.login(self.u_trans_hcb)
        r = self.client.delete(f"/api/despacho/talonarios/{tal.pk}/")
        self.assertEqual(r.status_code, 403)
        self.login(self.u_jefe)
        r = self.client.delete(f"/api/despacho/talonarios/{tal.pk}/")
        self.assertEqual(r.status_code, 200)


class DespachoCruceTests(DespachoBase):
    def test_resumen_marca_usados_y_faltantes(self):
        tal = self.crear_talonario(desde=1, hasta=5)
        self.crear_defuncion("DEF-2026-000003")
        self.login(self.u_jefe)
        r = self.client.get(f"/api/despacho/talonarios/{tal.pk}/certificados/")
        self.assertEqual(r.status_code, 200)
        datos = r.json()["data"]
        self.assertEqual(datos["resumen"]["usados"], 1)
        self.assertEqual(datos["resumen"]["faltantes_total"], 4)
        cargados = [f["numero"] for f in datos["certificados"] if f["estatus"] == "CARGADO"]
        self.assertEqual(cargados, [3])

    def test_certificado_de_otro_centro_no_cuenta(self):
        tal = self.crear_talonario(desde=1, hasta=5)
        self.crear_defuncion("DEF-2026-000002", organizacion=self.org_cabudare)
        self.login(self.u_jefe)
        r = self.client.get(f"/api/despacho/talonarios/{tal.pk}/certificados/")
        self.assertEqual(r.json()["data"]["resumen"]["usados"], 0)

    def test_certificado_de_un_descendiente_si_cuenta(self):
        tal = self.crear_talonario(centro=self.org_regional, desde=1, hasta=5)
        self.crear_defuncion("DEF-2026-000002", organizacion=self.org_hcb)
        self.login(self.u_jefe)
        r = self.client.get(f"/api/despacho/talonarios/{tal.pk}/certificados/")
        self.assertEqual(r.json()["data"]["resumen"]["usados"], 1)

    def test_numero_sin_digitos_finales_se_ignora(self):
        tal = self.crear_talonario(desde=1, hasta=5)
        self.crear_defuncion("SIN-NUMERO")
        self.login(self.u_jefe)
        r = self.client.get(f"/api/despacho/talonarios/{tal.pk}/certificados/")
        self.assertEqual(r.json()["data"]["resumen"]["usados"], 0)


class DespachoNovedadTests(DespachoBase):
    def test_novedad_fuera_de_serie(self):
        tal = self.crear_talonario(desde=1, hasta=5)
        self.login(self.u_jefe)
        r = self.client.post(
            "/api/despacho/novedades/",
            {"talonario": tal.pk, "numero": 99, "estado": NovedadCertificado.ESTADO_DANADO},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 400)

    def test_novedad_en_serie_reduce_faltantes(self):
        tal = self.crear_talonario(desde=1, hasta=5)
        self.login(self.u_jefe)
        r = self.client.post(
            "/api/despacho/novedades/",
            {"talonario": tal.pk, "numero": 2, "estado": NovedadCertificado.ESTADO_DANADO,
             "justificacion_numero": "ACTA-01"},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 201)
        r = self.client.get(f"/api/despacho/talonarios/{tal.pk}/certificados/")
        resumen = r.json()["data"]["resumen"]
        self.assertEqual(resumen["danados"], 1)
        self.assertEqual(resumen["faltantes_total"], 4)

    def test_novedad_duplicada(self):
        tal = self.crear_talonario(desde=1, hasta=5)
        NovedadCertificado.objects.create(talonario=tal, numero=2,
                                          estado=NovedadCertificado.ESTADO_EN_TRANSITO)
        self.login(self.u_jefe)
        r = self.client.post(
            "/api/despacho/novedades/",
            {"talonario": tal.pk, "numero": 2, "estado": NovedadCertificado.ESTADO_DANADO},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 400)


class DespachoAlcanceTests(DespachoBase):
    def test_centro_solo_ve_sus_talonarios(self):
        self.crear_talonario(centro=self.org_hcb, desde=1, hasta=5)
        self.crear_talonario(centro=self.org_cabudare, desde=1, hasta=5)
        self.login(self.u_trans_hcb)
        r = self.client.get("/api/despacho/talonarios/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 1)
        self.assertEqual(r.json()["data"][0]["centro"], self.org_hcb.pk)

    def test_regional_ve_todo_su_estado(self):
        self.crear_talonario(centro=self.org_hcb, desde=1, hasta=5)
        self.crear_talonario(centro=self.org_cabudare, desde=1, hasta=5)
        self.crear_talonario(centro=self.org_otro_estado, desde=1, hasta=5)
        self.login(self.u_trans_regional)
        r = self.client.get("/api/despacho/talonarios/")
        self.assertEqual(r.json()["count"], 2)


class DespachoReportesTests(DespachoBase):
    def test_reporte_certificados_defuncion(self):
        self.crear_defuncion("DEF-2026-000003", nombres="María", apellidos="Rojas")
        self.login(self.u_jefe)
        r = self.client.get("/api/despacho/reportes/certificados/?tipo=DEFUNCION")
        self.assertEqual(r.status_code, 200)
        items = r.json()["data"]["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["numero"], "DEF-2026-000003")
        self.assertEqual(items[0]["centro"], self.org_hcb.nombre)
        self.assertEqual(items[0]["persona"], "Fallecido")

    def test_reporte_certificados_nacimiento_usa_madre(self):
        self.crear_nacimiento("NC-2026-000001")
        self.login(self.u_jefe)
        r = self.client.get("/api/despacho/reportes/certificados/?tipo=NACIMIENTO")
        items = r.json()["data"]["items"]
        self.assertEqual(items[0]["apellidos"], "Pérez")
        self.assertEqual(items[0]["persona"], "Madre")

    def test_reporte_pendientes_csv_con_bom(self):
        tal = self.crear_talonario(desde=1, hasta=3)
        self.crear_defuncion("DEF-2026-000002")
        self.login(self.u_jefe)
        r = self.client.get("/api/despacho/reportes/pendientes/?formato=csv")
        self.assertEqual(r.status_code, 200)
        cuerpo = r.content.decode("utf-8")
        self.assertTrue(cuerpo.startswith("\ufeff"))
        self.assertIn("SIN_ASIGNAR", cuerpo)
        # El certificado cargado no sale en pendientes.
        self.assertNotIn("DEF-2026-000002", cuerpo)

    def test_reporte_pendientes_json(self):
        tal = self.crear_talonario(desde=1, hasta=3)
        self.crear_defuncion("DEF-2026-000002")
        self.login(self.u_jefe)
        r = self.client.get("/api/despacho/reportes/pendientes/")
        items = r.json()["data"]["items"]
        self.assertEqual(len(items), 2)
        self.assertEqual({i["numero"] for i in items}, {1, 3})
