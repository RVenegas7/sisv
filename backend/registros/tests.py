"""Pruebas de registros: CRUD, alcance multicentro, permisos, CIE por fecha, dashboard."""

import os
import shutil
import tempfile
from datetime import date, timedelta
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError

from tests_sisv import SISVBase, FECHA_CORTE

from registros.models import Defuncion, Nacimiento


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


class AnioEpidemiologicoTests(SISVBase):
    """El filtro por año es **epidemiológico**, no civil.

    Regresión del bug: la semana 53 de 2025 va del 28-12-2025 al 03-01-2026, así que
    los certificados del 1, 2 y 3 de enero de 2026 son de 2025, y la semana 1 de 2026
    arranca el domingo 04-01-2026. Con `fecha_evento__year` esos registros se contaban en
    2026 y desaparecían del reporte de 2025.
    """

    def _defuncion(self, uid, fecha):
        return Defuncion.objects.create(
            registro_numero=uid,
            fecha_evento=fecha,
            organizacion=self.org_hcb,
            fallecido_nombres="Test",
            sexo="F",
        )

    def test_enero_2026_pertenece_a_la_semana_53_de_2025(self):
        self._defuncion("D-30-DIC", date(2025, 12, 30))
        self._defuncion("D-01-ENE", date(2026, 1, 1))
        self._defuncion("D-03-ENE", date(2026, 1, 3))
        self._defuncion("D-04-ENE", date(2026, 1, 4))
        self.login(self.u_admin)
        d2025 = self.client.get("/api/registros/dashboard/?anio=2025").json()["data"]
        d2026 = self.client.get("/api/registros/dashboard/?anio=2026").json()["data"]
        self.assertEqual(d2025["totales"]["defunciones"], 3)
        self.assertEqual(d2026["totales"]["defunciones"], 1)
        # y en el comparativo, con la misma convención
        comp = self.client.get(
            "/api/registros/reportes/comparativo/?anio1=2025&anio2=2026"
        ).json()["data"]
        self.assertEqual(comp["totales"]["muertes"]["2025"], 3)
        self.assertEqual(comp["totales"]["muertes"]["2026"], 1)

    def test_la_semana_53_aparece_como_53_y_no_como_1(self):
        self._defuncion("D-53", date(2025, 12, 28))
        self.login(self.u_admin)
        por_semana = self.client.get("/api/registros/dashboard/?anio=2025").json()["data"]["por_semana"]
        # por_semana = {"<semana>": {"<módulo>": n}}
        self.assertEqual(por_semana.get("53", {}).get("defunciones"), 1)
        self.assertNotIn("1", por_semana)

    def test_lista_filtra_por_anio_epidemiologico(self):
        self._defuncion("D-LISTA-2025", date(2025, 12, 30))
        self._defuncion("D-LISTA-2026", date(2026, 1, 4))
        self.login(self.u_admin)
        r = self.client.get("/api/registros/defunciones/?anio=2025").json()
        self.assertEqual(r["count"], 1)
        self.assertEqual(r["data"][0]["registro_numero"], "D-LISTA-2025")


class MuerteMaternaTests(SISVBase):
    """La muerte materna sale del registro de investigación de la oficina.

    `Defuncion.embarazo_o_puerperio` (`CERTIFICADO.HPRESENCIAEMBARAZO`) es un aviso
    opcional del certificador, no un registro: en 2026 lo diligencia en 7 de las 18
    muertes maternas. Por eso el indicador de MM se lee de
    `sismai."RENGLON_CASOSMM"` enlazado a `CASOS_MMI`, y el del certificado se reporta
    aparte. Estas pruebas fijan ese comportamiento con la fuente legacy ausente
    (sqlite), que es exactamente cuando el tablero debe caer al certificado.
    """

    def _defuncion(self, uid, mm, pendiente):
        return Defuncion.objects.create(
            registro_numero=uid,
            fecha_evento=date(2023, 6, 1),
            organizacion=self.org_hcb,
            fallecido_nombres="Test",
            sexo="F",
            embarazo_o_puerperio=mm,
            codificacion_pendiente=pendiente,
        )

    def _registro_legacy(self, org_id, por_semana):
        """Simula el registro de investigación: `{org_id: {semana: cantidad}}`."""
        with patch("registros.views.muerte_materna_por_semana", return_value=por_semana):
            return self.client.get("/api/registros/dashboard/?anio=2023").json()["data"][
                "mortalidad_materno_infantil"]

    def test_sin_registro_legacy_cae_al_certificado(self):
        """Sin la fuente legacy el tablero usa el certificado y lo dice.

        Mostrar 0 porque no se pudo leer el registro sería afirmar que no hubo muertes
        maternas, que es lo contrario de lo que se sabe. Y avisar en el log es parte
        del contrato: un tablero que calla la caída de la fuente es un tablero que
        parece sano.
        """
        self._defuncion("MM-01", True, True)
        self._defuncion("MM-02", True, False)
        self._defuncion("NO-MM", False, False)
        self.login(self.u_admin)
        with self.assertLogs("registros.services", level="WARNING") as logs:
            mmi = self.client.get("/api/registros/dashboard/?anio=2023").json()["data"][
                "mortalidad_materno_infantil"]
        self.assertIn("RENGLON_CASOSMM", logs.output[0])
        self.assertEqual(mmi["mm"], 2)
        self.assertEqual(mmi["mm_fuente"], "CERTIFICADO")
        self.assertEqual(mmi["mm_codificadas"], 1)
        self.assertEqual(mmi["mm_pendientes"], 1)
        self.assertEqual(mmi["mm_codificadas"] + mmi["mm_pendientes"], mmi["mm_certificadas"])

    def test_el_registro_de_la_oficina_manda_sobre_el_certificado(self):
        """El caso real de 2026: 18 en el registro de la oficina, 7 en los certificados."""
        self._defuncion("MM-01", True, True)
        self.login(self.u_admin)
        mmi = self._registro_legacy(None, {22: 18})
        self.assertEqual(mmi["mm"], 18)
        self.assertEqual(mmi["mm_fuente"], "REGISTRO_INVESTIGACION")
        # El certificado no se pierde: sigue visible al lado.
        self.assertEqual(mmi["mm_certificadas"], 1)

    def test_un_registro_vacio_no_es_un_cero(self):
        """Un dict vacío significa "cero muertes en el periodo", no "no se pudo leer"."""
        self._defuncion("MM-01", True, True)
        self.login(self.u_admin)
        mmi = self._registro_legacy(None, {})
        self.assertEqual(mmi["mm"], 0)
        self.assertEqual(mmi["mm_fuente"], "REGISTRO_INVESTIGACION")

    def test_comparativo_cuenta_mm_sin_cie(self):
        self._defuncion("MM-03", True, True)
        self.login(self.u_admin)
        data = self.client.get(
            "/api/registros/reportes/comparativo/?anio1=2023&anio2=2022"
        ).json()["data"]
        self.assertEqual(data["totales"]["muertes_maternas"]["2023"], 1)


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

class CoberturaTableroTests(SISVBase):
    """El tablero tiene que avisar cuando la serie tiene un hueco.

    Sin esto, un corte de captura se ve igual que un mes sin casos: los dos son una
    linea que baja a cero. Estas pruebas fijan las dos señales que usa el aviso
    (`meses_sin_datos` y `atraso_dias`) y que el mes en curso NO se marque, porque a
    mitad de mes siempre esta a medias y avisar seria mentir.
    """

    def _cobertura(self, anio=2026):
        self.login(self.u_admin)
        return self.client.get(f"/api/registros/dashboard/?anio={anio}").json()["data"]["cobertura"]

    def test_marca_mes_terminado_sin_registros(self):
        # Datos en mayo y en julio: junio quedo en cero.
        for uid, mes in (("D-MAY", 5), ("D-JUL", 7)):
            Defuncion.objects.create(
                registro_numero=uid, fecha_evento=date(2026, mes, 10),
                organizacion=self.org_hcb, fallecido_nombres="T", sexo="F",
            )
        cov = self._cobertura()
        self.assertFalse(cov["completo"])
        self.assertEqual(cov["meses_sin_datos"], ["junio de 2026"])

    def test_mes_en_curso_no_se_marca_como_hueco(self):
        """Septiembre 2026 esta a medias hoy: no es un hueco, es carga en curso."""
        hoy = date.today()
        # Mes anterior y mes en curso: entre los dos no puede quedar ningun hueco.
        anterior = (hoy.replace(day=1) - timedelta(days=1))
        Defuncion.objects.create(
            registro_numero="D-MES-ANT", fecha_evento=anterior,
            organizacion=self.org_hcb, fallecido_nombres="T", sexo="F",
        )
        Defuncion.objects.create(
            registro_numero="D-MES-ACT", fecha_evento=hoy,
            organizacion=self.org_hcb, fallecido_nombres="T", sexo="F",
        )
        cov = self._cobertura()
        self.assertEqual(cov["meses_sin_datos"], [])

    def test_ultima_fecha_y_atraso_por_modulo(self):
        Defuncion.objects.create(
            registro_numero="D-ATRASO", fecha_evento=date(2026, 6, 1),
            organizacion=self.org_hcb, fallecido_nombres="T", sexo="F",
        )
        cov = self._cobertura()
        mod = cov["por_modulo"]["defunciones"]
        self.assertEqual(mod["ultima_fecha"], "2026-06-01")
        self.assertEqual(mod["atraso_dias"], (date.today() - date(2026, 6, 1)).days)
        # 2026-06-01 -> hoy es mucho mas de 45 dias: el tablero no esta completo.
        self.assertFalse(cov["completo"])

    def test_serie_sin_huecos_recientes_es_completa(self):
        Defuncion.objects.create(
            registro_numero="D-OK", fecha_evento=date.today() - timedelta(days=5),
            organizacion=self.org_hcb, fallecido_nombres="T", sexo="F",
        )
        cov = self._cobertura()
        self.assertEqual(cov["meses_sin_datos"], [])
        self.assertTrue(cov["completo"])


# --------------------------------------------------------------------------- #
# Cargador de la recuperacion MM/MN (PENDIENTES 17.17/17.24)                        #
# --------------------------------------------------------------------------- #
CAB_MUERTE = (
    "ID;FECHA_M;NOMBRE;APELLIDO;CEDULA;SEXO;EDAD;TIPOEDAD;FECHA_N;HORAMUERTE;"
    "HESTADOCIVIL;HSITIO_M;HESTABLECIMIENTO;HESTABLECIMIENTO_OCUR;HLOCARESIDENCIA;"
    "HPRESENCIAEMBARAZO;HCAUSABASICA;AUTOPSIA;HMEDICOFIRMANTE;OTROMEDFIRMANTE;MFETAL;"
    "STATUS;FECHAOPERACION"
)
CAB_ESTABLECIMIENTO = "ID;CODIGO;NOMBRE;PADRE;DESCRIPCION;HTIPO;HLOCALIDAD;STATUS"
CAB_CIE10 = "SEQ_ID_ACTUAL;COD_CLASIFICACION;DES_CLASIFICACIO1;DES_CLASIFICACIO2"
CAB_GEO = "NUM_REGION;NOMBRELARGO"
CAB_CAUSA_M = "HCERTIFICADO;HCIE10;ORDENLISTA;DESENFERMEDAD"
CAB_RNACIDO = (
    "ID;HCERTIFICADO;NOMBRES;HSEXO;NACIMIENTO;PESO;TALLA;HTIPOPARTO;HFORMAPARTO;"
    "VIVO_MUERTO;SEMANAGESTACION"
)
CAB_MADRE = (
    "ID;HCERTIFICADO;CEDULA;NOMBRES;APELLIDOS;EDADM;EDADP;ESTADOCIVIL;"
    "FECHANACIMIENTO_MADRE;HRESIDENCIA;NACVIVOS;MUERTESFETALES;HULTIMOGRADO;CONTROLPRENATAL"
)


def _csv(nombre, cabecera, filas):
    """Arma un CSV del legacy: encabezado del propio SQL + filas separadas por ';'."""
    return nombre, cabecera + "\n" + "".join(";".join(str(x) for x in f) + "\n" for f in filas)


class CargarMMMNTests(SISVBase):
    """Pruebas del comando `cargar_mm_mn_roto`.

    Lo que se protege aca, en orden de importancia:
      1. no duplica al re-correr (idempotencia),
      2. no borra la codificacion que hizo el codificador a mano,
      3. la muerte materna sale del CSV (HPRESENCIAEMBARAZO 1 o 2), no de un rango de fechas,
      4. la organizacion sale del arbol Lara por nombre, y los-setting de fuera quedan sueltos,
      5. la causa cae a CAUSA_M y, si no hay, al catalogo CIE-10 legacy.
    """

    def _montar(self, muertes=(), establishing=(), cie=(), geo=(), causas=(),
                rnacidos=(), madres=()):
        d = tempfile.mkdtemp(prefix="cargar_mm_mn_")
        self.addCleanup(shutil.rmtree, d, True)
        # El árbol Lara del legacy arranca en la raíz 67754 (DES Lara).
        arbol = [(67754, "LARA", "Direccion de Epidemiologia del Estado Lara", "", "", "", "", "1")]
        for r, n in establishing:
            padre = 67754 if r == 67754 else (r - 1)
            arbol.append((r, f"LARA-{r}", n, padre, "", "", "", "1"))
        archivos = [
            _csv("muerte.csv", CAB_MUERTE, muertes),
            _csv("establecimiento.csv", CAB_ESTABLECIMIENTO, arbol),
            _csv("cie10_legacy.csv", CAB_CIE10, cie),
            _csv("org_geografica.csv", CAB_GEO, geo),
            _csv("causa_m.csv", CAB_CAUSA_M, causas),
            _csv("nac_rnacido.csv", CAB_RNACIDO, rnacidos),
            _csv("nac_madre.csv", CAB_MADRE, madres),
        ]
        for nombre, texto in archivos:
            with open(os.path.join(d, nombre), "w", encoding="utf-8") as fh:
                fh.write(texto)
        return d

    @staticmethod
    def _muerte(id_, fecha_m, fecha_n, *, sexo=2, edad=30, embarazo=0,
                causa=0, est=1, est_ocur=None, res=0, omitidos=()):
        """Fila de muerte.csv con las 23 columnas en el orden del SQL."""
        base = [id_, fecha_m, "NOMBRE", "APELLIDO", "V12345678", sexo, edad, "A", fecha_n,
                "08:30 AM", 1, 1, est, est_ocur if est_ocur is not None else est, res,
                embarazo, causa, 0, 2, "", 0, 1, fecha_m]
        for i in omitidos:
            base[i] = ""
        return base

    # -- 1. idempotencia ----------------------------------------------------
    def test_dry_run_no_escribe(self):
        d = self._montar(muertes=[self._muerte(5001, "2026-08-10", "1950-01-01")])
        call_command("cargar_mm_mn_roto", directorio=d)
        self.assertFalse(Defuncion.objects.filter(registro_numero__startswith="LEG-CERT-").exists())

    def test_carga_y_no_duplica_al_recorrer(self):
        d = self._montar(muertes=[self._muerte(5001, "2026-08-10", "1950-01-01")])
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        self.assertEqual(Defuncion.objects.filter(registro_numero="LEG-CERT-5001").count(), 1)
        d2 = self._muerte(5002, "2026-08-11", "1951-01-01")
        self._montar(muertes=[d2])
        with open(os.path.join(d, "muerte.csv"), "w", encoding="utf-8") as fh:
            fh.write(CAB_MUERTE + "\n" + ";".join(str(x) for x in d2) + "\n")
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        self.assertEqual(Defuncion.objects.filter(registro_numero__startswith="LEG-CERT-").count(), 2)
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        self.assertEqual(Defuncion.objects.filter(registro_numero__startswith="LEG-CERT-").count(), 2)

    # -- 2. no pisa trabajo humano -----------------------------------------
    def test_no_pisa_cie_revisado_ni_causa_corregida(self):
        d = self._montar(muertes=[self._muerte(5003, "2026-08-10", "1950-01-01", causa=700)])
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        obj = Defuncion.objects.get(registro_numero="LEG-CERT-5003")
        obj.cie10_legacy = "J18.9"
        obj.cie10 = self.cie10_otro
        obj.codificacion_pendiente = False
        obj.causa_directa = "NEUMONIA (CORREGIDO A MANO)"
        obj.save()
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        obj.refresh_from_db()
        self.assertEqual(obj.cie10_legacy, "J18.9")
        self.assertEqual(obj.cie10, self.cie10_otro)
        self.assertFalse(obj.codificacion_pendiente)
        self.assertEqual(obj.causa_directa, "NEUMONIA (CORREGIDO A MANO)")

    def test_vacio_no_borra_causa_ya_cargada(self):
        """CAUSA_M vacio no puede borrar una causa que alguien ya cargo."""
        d = self._montar(muertes=[self._muerte(5004, "2026-08-10", "1950-01-01")])
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        obj = Defuncion.objects.get(registro_numero="LEG-CERT-5004")
        obj.causa_directa = "TBC"
        obj.save()
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        obj.refresh_from_db()
        self.assertEqual(obj.causa_directa, "TBC")

    # -- 3. muerte materna --------------------------------------------------
    def test_muerte_materna_por_codigo_1_y_2(self):
        """HPRIMERA 1 = al momento, 2 = ultimos 12 meses: las dos son MM."""
        filas = [self._muerte(6001 + c, "2026-08-10", "1990-01-01", sexo=1, edad=30, embarazo=c, causa=0)
                 for c in (1, 2)]
        d = self._montar(muertes=filas)
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        self.assertEqual(Defuncion.objects.filter(embarazo_o_puerperio=True).count(), 2)

    def test_no_muerte_materna_codigos_3_y_0(self):
        filas = [self._muerte(6010 + c, "2026-08-10", "1990-01-01", sexo=1, edad=30, embarazo=c)
                 for c in (0, 3)]
        d = self._montar(muertes=filas)
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        self.assertEqual(Defuncion.objects.filter(embarazo_o_puerperio=True).count(), 0)

    def test_muerte_neonatal_0_a_27_dias(self):
        """El MN del tablero son 0-27 dias; a los 28 ya no es neonatal."""
        filas = [self._muerte(7001, "2026-08-10", "2026-08-09"),   # 1 dia
                 self._muerte(7002, "2026-08-10", "2026-07-14"),   # 27 dias
                 self._muerte(7003, "2026-08-10", "2026-07-13")]   # 28 dias
        d = self._montar(muertes=filas)
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        mn = {obj.registro_numero for obj in Defuncion.objects.all()}
        self.assertIn("LEG-CERT-7001", mn)
        self.assertIn("LEG-CERT-7002", mn)

    # -- 4. organizacion ----------------------------------------------------
    def test_organizacion_por_nombre_del_arbol_lara(self):
        """Se resuelve por NOMBRE; el ID del legacy es una trampa."""
        d = self._montar(
            muertes=[self._muerte(8001, "2026-08-10", "1950-01-01", est=101, res=900)],
            establishing=[(101, "Hospital Central de Barquisimeto")],
            geo=[(900, "Estado Lara, Municipio Iribarren, Parroquia Santa Rosa")],
        )
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        obj = Defuncion.objects.get(registro_numero="LEG-CERT-8001")
        self.assertEqual(obj.organizacion, self.org_hcb)
        self.assertEqual(obj.establecimiento, "Hospital Central de Barquisimeto")
        self.assertEqual((obj.estado, obj.municipio, obj.parroquia), ("Lara", "Iribarren", "Santa Rosa"))

    def test_establecimiento_fuera_del_arbol_queda_sin_organizacion(self):
        """El hospital de otro estado existe en el catalogo pero cuelga de otra raiz."""
        d = self._montar(
            muertes=[self._muerte(8002, "2026-08-10", "1950-01-01", est=500)],
            establishing=[(500, "HOSPITAL DE OTRO ESTADO")],
        )
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        obj = Defuncion.objects.get(registro_numero="LEG-CERT-8002")
        self.assertIsNone(obj.organizacion_id)

    def test_catalogo_sin_raices_lara_aborta(self):
        """Sin las raíces NO se decide el alcance: se aborta, no se adivina."""
        d = self._montar(
            muertes=[self._muerte(8004, "2026-08-10", "1950-01-01")],
            establishing=[],
        )
        with open(os.path.join(d, "establecimiento.csv"), "w", encoding="utf-8") as fh:
            fh.write(CAB_ESTABLECIMIENTO + "\n1;X;HOSPITAL SIN RAIZ;0;;;;1\n")
        with self.assertRaisesMessage(CommandError, "raiz Lara"):
            call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        self.assertFalse(Defuncion.objects.filter(registro_numero__startswith="LEG-CERT-").exists())

    def test_duplicado_en_el_csv_no_revienta_el_lote(self):
        """El mismo certificado dos veces: avisa y sigue, no UNIQUE y lote perdido."""
        d = self._montar(muertes=[self._muerte(8005, "2026-08-10", "1950-01-01")],
                        establishing=[])
        with open(os.path.join(d, "muerte.csv"), "a", encoding="utf-8") as fh:
            fh.write(";".join(str(x) for x in self._muerte(8005, "2026-08-11", "1950-01-01")) + "\n")
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        self.assertEqual(Defuncion.objects.filter(registro_numero="LEG-CERT-8005").count(), 1)

    def test_limite_no_trunca_los_catalogos(self):
        """`--limite` es para los datos: si truncara el catalogo, la org quedaria mal."""
        d = self._montar(
            muertes=[self._muerte(8003, "2026-08-10", "1950-01-01", est=101)],
            establishing=[(101, "Hospital Central de Barquisimeto")],
        )
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True, limite=1)
        obj = Defuncion.objects.get(registro_numero="LEG-CERT-8003")
        self.assertEqual(obj.organizacion, self.org_hcb)

    # -- 5. causa -----------------------------------------------------------
    def test_causa_toma_primera_linea_de_causa_m(self):
        d = self._montar(
            muertes=[self._muerte(9001, "2026-08-10", "1950-01-01", causa=700)],
            causas=[(9001, 700, 2, "SEGUNDA LINEA"), (9001, 700, 1, "PRIMERA LINEA")],
        )
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        self.assertEqual(
            Defuncion.objects.get(registro_numero="LEG-CERT-9001").causa_directa, "PRIMERA LINEA"
        )

    def test_causa_cae_al_catalogo_cie10_legacy(self):
        d = self._montar(
            muertes=[self._muerte(9002, "2026-08-10", "1950-01-01", causa=700)],
            cie=[(700, "J18", "Neumonia", "")],
        )
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        self.assertEqual(
            Defuncion.objects.get(registro_numero="LEG-CERT-9002").causa_directa, "Neumonia"
        )

    def test_sin_causa_queda_pendiente_de_codificacion(self):
        d = self._montar(muertes=[self._muerte(9003, "2026-08-10", "1950-01-01")])
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        obj = Defuncion.objects.get(registro_numero="LEG-CERT-9003")
        self.assertTrue(obj.codificacion_pendiente)
        self.assertEqual(obj.causa_directa, "")

    # -- 6. limpios ---------------------------------------------------------
    def test_encabezado_equivocado_aborta_con_mensaje_util(self):
        d = self._montar(muertes=[self._muerte(9004, "2026-08-10", "1950-01-01")])
        with open(os.path.join(d, "muerte.csv"), "w", encoding="utf-8") as fh:
            fh.write("ID;FECHA;NOMBRE\n9004;2026-08-10;X\n")
        with self.assertRaisesMessage(CommandError, "faltan columnas"):
            call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)

    def test_fecha_ilegable_se_omite_y_no_rompe(self):
        filas = [self._muerte(9005, "NO-ES-FECHA", "1950-01-01"),
                 self._muerte(9006, "2026-08-10", "1950-01-01")]
        d = self._montar(muertes=filas)
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        self.assertTrue(Defuncion.objects.filter(registro_numero="LEG-CERT-9006").exists())
        self.assertFalse(Defuncion.objects.filter(registro_numero="LEG-CERT-9005").exists())

    # -- 7. nacimientos -----------------------------------------------------
    def test_nacimiento_desde_rnacido_sin_certificado(self):
        """6 de los 29 rnacidos de agosto no tienen certificado y aun así se cargan."""
        d = self._montar(
            rnacidos=[(3001, "", "BEBE UNO", 1, "2026-08-13", 3000, 49, 1, 1, 1, 39)],
            madres=[(4001, "", "V87654321", "MARIA", "PEREZ", 30, 24, 2, "1996-04-09", 900, 1, 0, "B", 1)],
        )
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        nac = Nacimiento.objects.get(registro_numero="LEG-RN-3001")
        self.assertEqual(nac.fecha_evento, date(2026, 8, 13))
        self.assertEqual(nac.sexo, "F")
        self.assertEqual(nac.peso_gramos, 3000)
        self.assertEqual(nac.madre_cedula, "V87654321")
        self.assertEqual(nac.madre_estado_civil, "CASADA")

    def test_nacimiento_no_inventa_estado_civil(self):
        d = self._montar(
            rnacidos=[(3002, "", "BEBE", 2, "2026-08-13", 3000, 49, 1, 1, 1, 39)],
            madres=[(4002, "", "V1", "ANA", "GOMEZ", 25, 20, "", "2001-01-01", 900, 1, 0, "A", 1)],
        )
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        self.assertEqual(Nacimiento.objects.get(registro_numero="LEG-RN-3002").madre_estado_civil, "SOLTERA")

    def test_nacimiento_muerto_nace_sin_fallecido(self):
        d = self._montar(rnacidos=[(3003, "", "BEBE", 1, "2026-08-13", 0, 0, 1, 1, 2, 39)])
        call_command("cargar_mm_mn_roto", directorio=d, ejecutar=True)
        self.assertTrue(Nacimiento.objects.filter(registro_numero="LEG-RN-3003").exists())
