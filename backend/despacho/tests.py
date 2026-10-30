"""Pruebas del módulo de despacho de talonarios de certificados."""

import io

from django.contrib.auth import get_user_model
from django.core.management import call_command
from tests_sisv import SISVBase

from despacho.models import NovedadCertificado, Talonario
from despacho.services import resumen_talonario, series_deducidas
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

    def test_cantidad_deriva_serie_hasta(self):
        """El alta pide cantidad y la serie hasta se calcula (desde + cantidad - 1)."""
        self.login(self.u_jefe)
        datos = self.datos_talonario(serie_desde=500, cantidad=50)
        del datos["serie_hasta"]
        r = self.client.post("/api/despacho/talonarios/", datos, content_type="application/json")
        self.assertEqual(r.status_code, 201, r.content.decode())
        tal = Talonario.objects.get()
        self.assertEqual(tal.serie_desde, 500)
        self.assertEqual(tal.serie_hasta, 549)
        self.assertEqual(tal.cantidad, 50)

    def test_cantidad_o_hasta_obligatoria(self):
        self.login(self.u_jefe)
        datos = self.datos_talonario(serie_desde=500)
        del datos["serie_hasta"]
        r = self.client.post("/api/despacho/talonarios/", datos, content_type="application/json")
        self.assertEqual(r.status_code, 400)

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

    def test_superusuario_sin_organizacion_debe_elegir_centro(self):
        """Sin organización no hay centro por defecto: el talonario exige indicarlo."""
        self.login(self.u_admin)
        datos = self.datos_talonario()
        del datos["centro"]
        r = self.client.post("/api/despacho/talonarios/", datos, content_type="application/json")
        self.assertEqual(r.status_code, 400, r.content.decode())
        self.assertIn("centro", r.json()["errors"])
        self.assertEqual(Talonario.objects.count(), 0)

        r = self.client.post("/api/despacho/talonarios/", self.datos_talonario(),
                             content_type="application/json")
        self.assertEqual(r.status_code, 201, r.content.decode())
        self.assertEqual(Talonario.objects.get().centro_id, self.org_hcb.pk)


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
    def test_cruce_usa_numero_fisico_real_cuando_existe(self):
        """LEG-CERT-<id> es la PK de Oracle: sin numero_certificado no cuadra con la
        serie física; con él sí (§27.16)."""
        tal = self.crear_talonario(desde=250, hasta=259)
        d = self.crear_defuncion("LEG-CERT-999473093")
        self.assertEqual(resumen_talonario(tal)["usados"], 0)  # PK de Oracle, fuera de serie
        d.numero_certificado = "253"
        d.save(update_fields=["numero_certificado"])
        resumen = resumen_talonario(self.crear_talonario(desde=260, hasta=269))
        self.assertEqual(resumen["usados"], 0)
        tal.refresh_from_db()
        self.assertEqual(resumen_talonario(tal)["usados"], 1)

    def test_cruce_nacimiento_usa_numero_planilla(self):
        tal = self.crear_talonario(desde=70, hasta=79, tipo=Talonario.TIPO_NACIMIENTO)
        n = self.crear_nacimiento("LEG-RN-55")
        n.numero_planilla = "0072"
        n.save(update_fields=["numero_planilla"])
        self.assertEqual(resumen_talonario(tal)["usados"], 1)

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

    def test_reporte_certificados_expone_numero_impreso(self):
        """La referencia visible es el número impreso; el de registro va aparte (§31.2)."""
        d = self.crear_defuncion("LEG-CERT-999473093")
        d.numero_certificado = "5143453"
        d.save(update_fields=["numero_certificado"])
        self.crear_defuncion("DEF-2026-000002")
        self.login(self.u_jefe)
        r = self.client.get("/api/despacho/reportes/certificados/?tipo=DEFUNCION")
        items = {i["numero"]: i for i in r.json()["data"]["items"]}
        self.assertEqual(items["LEG-CERT-999473093"]["numero_fisico"], "5143453")
        self.assertEqual(items["LEG-CERT-999473093"]["numero"], "LEG-CERT-999473093")
        self.assertEqual(items["DEF-2026-000002"]["numero_fisico"], "")

    def test_reporte_certificados_csv_usa_numero_impreso(self):
        d = self.crear_defuncion("LEG-CERT-999473093")
        d.numero_certificado = "5143453"
        d.save(update_fields=["numero_certificado"])
        self.crear_defuncion("DEF-2026-000002")
        self.login(self.u_jefe)
        r = self.client.get("/api/despacho/reportes/certificados/?tipo=DEFUNCION&formato=csv")
        self.assertEqual(r.status_code, 200)
        lineas = r.content.decode("utf-8-sig").splitlines()
        self.assertIn("No Registro", lineas[0])
        filas = "\n".join(lineas[1:])
        self.assertIn("5143453,LEG-CERT-999473093", filas)
        # Sin número impreso, la columna cae al de registro (no queda vacía).
        self.assertIn("DEF-2026-000002,DEF-2026-000002", filas)

    def test_reporte_certificados_conserva_ceros_de_la_planilla(self):
        """«0072» es lo impreso: no se convierte en 72 (§31.2)."""
        n = self.crear_nacimiento("LEG-RN-999761189")
        n.numero_planilla = "0072"
        n.save(update_fields=["numero_planilla"])
        self.login(self.u_jefe)
        r = self.client.get("/api/despacho/reportes/certificados/?tipo=NACIMIENTO")
        self.assertEqual(r.json()["data"]["items"][0]["numero_fisico"], "0072")

    def test_reporte_certificados_nacimiento_usa_madre(self):
        self.crear_nacimiento("NC-2026-000001")
        self.login(self.u_jefe)
        r = self.client.get("/api/despacho/reportes/certificados/?tipo=NACIMIENTO")
        items = r.json()["data"]["items"]
        self.assertEqual(items[0]["apellidos"], "Pérez")
        self.assertEqual(items[0]["persona"], "Madre")

    def test_reporte_certificados_agrupado_por_centro(self):
        self.crear_defuncion("DEF-2026-000001")
        self.crear_defuncion("DEF-2026-000002")
        self.crear_defuncion("DEF-2026-000003", organizacion=self.org_cabudare)
        self.login(self.u_admin)
        r = self.client.get("/api/despacho/reportes/certificados/?tipo=DEFUNCION&agrupado=1")
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertTrue(data["agrupado"])
        self.assertEqual(data["total"], 3)
        por_centro = {f["centro"]: f["cantidad"] for f in data["items"]}
        self.assertEqual(por_centro[self.org_hcb.nombre], 2)
        self.assertEqual(por_centro[self.org_cabudare.nombre], 1)

    def test_reporte_certificados_agrupado_respeta_centro(self):
        self.crear_defuncion("DEF-2026-000001")
        self.crear_defuncion("DEF-2026-000002", organizacion=self.org_cabudare)
        self.login(self.u_admin)
        r = self.client.get(
            f"/api/despacho/reportes/certificados/?tipo=DEFUNCION&agrupado=1"
            f"&centro={self.org_cabudare.pk}"
        )
        items = r.json()["data"]["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["cantidad"], 1)
        self.assertEqual(items[0]["centro"], self.org_cabudare.nombre)

    def test_reporte_certificados_agrupado_csv(self):
        self.crear_defuncion("DEF-2026-000001")
        self.login(self.u_jefe)
        r = self.client.get(
            "/api/despacho/reportes/certificados/?tipo=DEFUNCION&agrupado=1&formato=csv")
        self.assertEqual(r.status_code, 200)
        cuerpo = r.content.decode("utf-8")
        self.assertTrue(cuerpo.startswith("\ufeff"))
        self.assertIn(self.org_hcb.nombre, cuerpo)

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

    def test_reporte_centros_entregados_vs_regresados(self):
        self.crear_talonario(desde=1, hasta=10)
        self.crear_talonario(desde=100, hasta=109, tipo=Talonario.TIPO_NACIMIENTO)
        self.crear_defuncion("DEF-2026-000003")
        self.login(self.u_jefe)
        r = self.client.get("/api/despacho/reportes/centros/")
        self.assertEqual(r.status_code, 200)
        items = r.json()["data"]["items"]
        self.assertEqual(len(items), 2)
        defunciones = next(i for i in items if i["tipo"] == "DEFUNCION")
        self.assertEqual(defunciones["centro_id"], self.org_hcb.pk)
        self.assertEqual(defunciones["talonarios"], 1)
        self.assertEqual(defunciones["entregados"], 10)
        self.assertEqual(defunciones["regresados"], 1)
        self.assertEqual(defunciones["faltantes"], 9)
        nacimientos = next(i for i in items if i["tipo"] == "NACIMIENTO")
        self.assertEqual(nacimientos["entregados"], 10)
        self.assertEqual(nacimientos["regresados"], 0)

    def test_reporte_centros_respeta_alcance(self):
        self.crear_talonario(desde=1, hasta=5)
        self.login(self.u_trans_hcb)
        r = self.client.get("/api/despacho/reportes/centros/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()["data"]["items"]), 1)
        self.login(self.u_trans_cabudare)
        r = self.client.get("/api/despacho/reportes/centros/")
        self.assertEqual(r.json()["data"]["items"], [])


class DespachoSeriesDeducidasTests(DespachoBase):
    """Deducción del rango de serie de los talonarios desde la BD (§31)."""

    def defuncion_fisica(self, numero_fisico, organizacion=None, fecha="2026-01-10"):
        """Defunción con número impreso (``numero_certificado``) real."""
        sufijo = organizacion.pk if organizacion else "x"
        d = self.crear_defuncion(f"LEG-CERT-{numero_fisico}-{sufijo}",
                                 organizacion=organizacion, fecha=fecha)
        d.numero_certificado = str(numero_fisico)
        d.save(update_fields=["numero_certificado"])
        return d

    def test_deduce_serie_desde_numeros_fisicos(self):
        for numero in (101, 102, 103, 104):
            self.defuncion_fisica(numero)
        self.login(self.u_jefe)
        r = self.client.get("/api/despacho/reportes/series-deducidas/?tipo=DEFUNCION")
        self.assertEqual(r.status_code, 200)
        items = r.json()["data"]["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["centro_id"], self.org_hcb.pk)
        self.assertEqual(items[0]["serie_desde"], 101)
        self.assertEqual(items[0]["serie_hasta"], 104)
        self.assertEqual(items[0]["usados"], 4)
        self.assertEqual(items[0]["extension"], 4)
        self.assertFalse(items[0]["ya_registrado"])

    def test_ignora_certificados_sin_numero_fisico(self):
        """El sufijo de LEG-CERT-<id> es la PK de Oracle, no la serie física."""
        self.crear_defuncion("DEF-2026-000123")
        self.login(self.u_jefe)
        r = self.client.get("/api/despacho/reportes/series-deducidas/?tipo=DEFUNCION")
        self.assertEqual(r.json()["data"]["items"], [])

    def test_descarta_series_dispersas(self):
        """Un rango salpicado (baja densidad) no es una serie."""
        for numero in (1, 11, 21):
            self.defuncion_fisica(numero)
        self.login(self.u_jefe)
        r = self.client.get("/api/despacho/reportes/series-deducidas/?tipo=DEFUNCION")
        self.assertEqual(r.json()["data"]["items"], [])
        # Con densidad 0 se muestran (el filtro es configurable).
        r = self.client.get("/api/despacho/reportes/series-deducidas/?tipo=DEFUNCION&densidad=0")
        self.assertEqual(len(r.json()["data"]["items"]), 1)

    def test_separa_series_por_hueco(self):
        for numero in (10, 11, 12, 9000, 9001, 9002):
            self.defuncion_fisica(numero)
        self.login(self.u_jefe)
        items = self.client.get(
            "/api/despacho/reportes/series-deducidas/?tipo=DEFUNCION").json()["data"]["items"]
        self.assertEqual([(i["serie_desde"], i["serie_hasta"]) for i in items],
                         [(10, 12), (9000, 9002)])

    def test_respeta_alcance_centro(self):
        for numero in (101, 102, 103):
            self.defuncion_fisica(numero, organizacion=self.org_hcb)
        for numero in (201, 202, 203):
            self.defuncion_fisica(numero, organizacion=self.org_cabudare)
        self.login(self.u_trans_hcb)
        items = self.client.get(
            "/api/despacho/reportes/series-deducidas/?tipo=DEFUNCION").json()["data"]["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["centro_id"], self.org_hcb.pk)

    def test_centro_fuera_de_alcance(self):
        self.login(self.u_trans_hcb)
        r = self.client.get(
            f"/api/despacho/reportes/series-deducidas/?tipo=DEFUNCION&centro={self.org_cabudare.pk}")
        self.assertEqual(r.status_code, 403)

    def test_marca_ya_registrado(self):
        for numero in (101, 102, 103):
            self.defuncion_fisica(numero)
        self.crear_talonario(desde=100, hasta=110)
        self.login(self.u_jefe)
        items = self.client.get(
            "/api/despacho/reportes/series-deducidas/?tipo=DEFUNCION").json()["data"]["items"]
        self.assertTrue(items[0]["ya_registrado"])

    def test_deduce_nacimientos_por_numero_planilla(self):
        for numero in ("0071", "0072", "0073"):
            n = self.crear_nacimiento(f"LEG-RN-{numero}")
            n.numero_planilla = numero
            n.save(update_fields=["numero_planilla"])
        self.login(self.u_jefe)
        items = self.client.get(
            "/api/despacho/reportes/series-deducidas/?tipo=NACIMIENTO").json()["data"]["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual((items[0]["serie_desde"], items[0]["serie_hasta"]), (71, 73))

    def test_csv_con_bom(self):
        for numero in (101, 102, 103):
            self.defuncion_fisica(numero)
        self.login(self.u_jefe)
        r = self.client.get(
            "/api/despacho/reportes/series-deducidas/?tipo=DEFUNCION&formato=csv")
        cuerpo = r.content.decode("utf-8")
        self.assertTrue(cuerpo.startswith("\ufeff"))
        self.assertIn(self.org_hcb.nombre, cuerpo)

    def test_comando_dry_run_no_crea(self):
        for numero in (101, 102, 103):
            self.defuncion_fisica(numero)
        salida = io.StringIO()
        call_command("deducir_talonarios", "--tipo", "DEFUNCION", stdout=salida)
        self.assertEqual(Talonario.objects.count(), 0)
        self.assertIn("Dry-run", salida.getvalue())

    def test_comando_ejecutar_crea_talonario(self):
        for numero in (101, 102, 103):
            self.defuncion_fisica(numero)
        salida = io.StringIO()
        call_command("deducir_talonarios", "--tipo", "DEFUNCION", "--ejecutar",
                     "--responsable-recibe", "Dra. Prueba", stdout=salida)
        tal = Talonario.objects.get()
        self.assertEqual((tal.serie_desde, tal.serie_hasta), (101, 103))
        self.assertEqual(tal.centro_id, self.org_hcb.pk)
        self.assertEqual(tal.responsable_recibe, "Dra. Prueba")
        self.assertTrue(tal.observaciones.startswith("Deducido de la BD"))


class DespachoRedondeoSeriesTests(DespachoBase):
    """Redondeo del rango deducido al corte de decena (opt-in, §36)."""

    def fisica(self, numero, organizacion=None):
        """Defunción con número impreso (``numero_certificado``) real."""
        d = self.crear_defuncion(
            f"LEG-CERT-{numero}-{(organizacion or self.org_hcb).pk}",
            organizacion=organizacion,
        )
        d.numero_certificado = str(numero)
        d.save(update_fields=["numero_certificado"])
        return d

    def test_apagado_por_defecto(self):
        """Sin ``redondeo`` la serie es el rango observado, como siempre."""
        for numero in (105, 106, 107, 108, 109, 110):
            self.fisica(numero)
        self.login(self.u_jefe)
        item = self.client.get(
            "/api/despacho/reportes/series-deducidas/?tipo=DEFUNCION"
        ).json()["data"]["items"][0]
        self.assertEqual((item["serie_desde"], item["serie_hasta"]), (105, 110))
        self.assertEqual(item["serie_desde_observada"], 105)
        self.assertEqual(item["serie_hasta_observada"], 110)
        self.assertFalse(item["redondeado"])

    def test_estira_al_corte_de_decena(self):
        """Con ``redondeo=5`` el extremo se corre a la decena si el hueco está libre."""
        for numero in (105, 106, 107, 108, 109, 110):
            self.fisica(numero)
        self.login(self.u_jefe)
        dato = self.client.get(
            "/api/despacho/reportes/series-deducidas/?tipo=DEFUNCION&redondeo=5"
        ).json()["data"]
        item = dato["items"][0]
        self.assertEqual(dato["margen_redondeo"], 5)
        self.assertEqual((item["serie_desde"], item["serie_hasta"]), (101, 110))
        self.assertEqual((item["serie_desde_observada"], item["serie_hasta_observada"]),
                         (105, 110))
        self.assertTrue(item["redondeado"])
        self.assertEqual(item["usados"], 6)
        self.assertEqual(item["extension"], 10)
        self.assertEqual(item["densidad"], 0.6)
        self.assertEqual(item["densidad_observada"], 1.0)

    def test_margen_pequeno_no_estira(self):
        """Si el corte de decena queda más lejos que el margen, no se toca."""
        for numero in (105, 106, 107, 108, 109, 110):
            self.fisica(numero)
        self.login(self.u_jefe)
        item = self.client.get(
            "/api/despacho/reportes/series-deducidas/?tipo=DEFUNCION&redondeo=3"
        ).json()["data"]["items"][0]
        self.assertEqual((item["serie_desde"], item["serie_hasta"]), (105, 110))
        self.assertFalse(item["redondeado"])

    def test_no_pisa_numeros_del_vecino(self):
        """El estirón se cancela si el corte pertenece a otro centro del libro."""
        for numero in (105, 106, 107, 108):
            self.fisica(numero, organizacion=self.org_hcb)
        for numero in (109, 110, 111):
            self.fisica(numero, organizacion=self.org_cabudare)
        candidatas = series_deducidas(Defuncion, margen_redondeo=5)
        por_centro = {c["centro_id"]: c for c in candidatas}
        hcb = por_centro[self.org_hcb.pk]
        cabudare = por_centro[self.org_cabudare.pk]
        # El tope del HCB no puede pasar a 110: 109 y 110 son del otro centro.
        self.assertEqual((hcb["serie_desde"], hcb["serie_hasta"]), (101, 108))
        self.assertEqual((cabudare["serie_desde"], cabudare["serie_hasta"]), (109, 111))
        self.assertFalse(cabudare["redondeado"])

    def test_comando_crea_talonario_redondeado(self):
        for numero in (105, 106, 107, 108, 109, 110):
            self.fisica(numero)
        salida = io.StringIO()
        call_command("deducir_talonarios", "--tipo", "DEFUNCION", "--ejecutar",
                     "--redondeo", "5", stdout=salida)
        tal = Talonario.objects.get()
        self.assertEqual((tal.serie_desde, tal.serie_hasta), (101, 110))
        self.assertIn("redondeado", salida.getvalue())

    def test_filtro_de_densidad_usa_el_rango_observado(self):
        """Redondear no descarta una serie densa solo porque el rango se estiró."""
        for numero in (103, 104, 105):
            self.fisica(numero)
        self.login(self.u_jefe)
        item = self.client.get(
            "/api/despacho/reportes/series-deducidas/?tipo=DEFUNCION&redondeo=9"
        ).json()["data"]["items"][0]
        self.assertEqual((item["serie_desde"], item["serie_hasta"]), (101, 110))
        self.assertEqual(item["densidad_observada"], 1.0)
        self.assertEqual(item["densidad"], 0.3)

    def test_csv_trae_observado_y_redondeo(self):
        for numero in (105, 106, 107, 108, 109, 110):
            self.fisica(numero)
        self.login(self.u_jefe)
        cuerpo = self.client.get(
            "/api/despacho/reportes/series-deducidas/?tipo=DEFUNCION&redondeo=5&formato=csv"
        ).content.decode("utf-8")
        self.assertIn("Observado desde", cuerpo)
        self.assertIn("Densidad observada", cuerpo)
        self.assertIn("Sí", cuerpo)
