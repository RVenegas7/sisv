"""Base compartida para las pruebas del backend SISV.

Crea una vez por TestCase la jerarquía mínima (territorio, organizaciones,
usuarios demo, catálogos CIE y eventos ENO) y ofrece clientes autenticados.
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from catalogos.models import CIE10, CIE11, MapeoCIE
from seguridad.models import Organizacion, Perfil
from territorio.models import ASIC, DivisionTerritorial
from vigilancia.models import EventoENO

User = get_user_model()

FECHA_CORTE = date(2022, 1, 1)


class SISVBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._crear_territorio()
        cls._crear_organizaciones()
        cls._crear_usuarios()
        cls._crear_cie()
        cls._crear_eventos()

    # -- Territorio -------------------------------------------------------
    @classmethod
    def _crear_territorio(cls):
        cls.par_estado = DivisionTerritorial.objects.create(
            nivel="ESTADO", nombre="Lara", codigo="12"
        )
        cls.par_municipio = DivisionTerritorial.objects.create(
            nivel="MUNICIPIO", nombre="Iribarren", codigo="1201", padre=cls.par_estado
        )
        cls.par_parroquia = DivisionTerritorial.objects.create(
            nivel="PARROQUIA", nombre="Santa Rosa", codigo="120101", padre=cls.par_municipio
        )
        cls.par_comunidad = DivisionTerritorial.objects.create(
            nivel="COMUNIDAD", nombre="La Mata", codigo="12010100001", padre=cls.par_parroquia
        )
        cls.asic_hcb = ASIC.objects.create(
            nombre="ASIC Antonio José de Sucre", codigo="ASIC-HCB-01", parroquia=cls.par_parroquia
        )

    # -- Organizaciones ---------------------------------------------------
    @classmethod
    def _crear_organizaciones(cls):
        cls.org_ministerio = Organizacion.objects.create(
            nombre="Ministerio del Poder Popular para la Salud (MPPS)",
            codigo="MPPS",
            nivel=Organizacion.NIVEL_MINISTERIO,
        )
        cls.org_gobernacion = Organizacion.objects.create(
            nombre="Gobernación del Estado Lara",
            codigo="GOB-LARA",
            nivel=Organizacion.NIVEL_GOBERNACION,
            padre=cls.org_ministerio,
        )
        cls.org_regional = Organizacion.objects.create(
            nombre="Dirección de Epidemiología del Estado Lara",
            codigo="DREP-LARA",
            nivel=Organizacion.NIVEL_REGIONAL,
            estado="Lara",
            padre=cls.org_gobernacion,
        )
        cls.org_hcb = Organizacion.objects.create(
            nombre="Hospital Central de Barquisimeto",
            codigo="HCB",
            nivel=Organizacion.NIVEL_CENTRO,
            estado="Lara",
            municipio="Iribarren",
            parroquia="Santa Rosa",
            asic=cls.asic_hcb,
            padre=cls.org_regional,
        )
        cls.org_cabudare = Organizacion.objects.create(
            nombre="Ambulatorio Cabudare",
            codigo="CABUDARE",
            nivel=Organizacion.NIVEL_CENTRO,
            estado="Lara",
            municipio="Palavecino",
            parroquia="Cabudare",
            padre=cls.org_regional,
        )
        cls.org_otro_estado = Organizacion.objects.create(
            nombre="Hospital de Coro",
            codigo="CORO",
            nivel=Organizacion.NIVEL_CENTRO,
            estado="Falcón",
            municipio="Miranda",
            parroquia="San Antonio",
            padre=cls.org_gobernacion,
        )

    # -- Usuarios ---------------------------------------------------------
    @classmethod
    def _crear_usuarios(cls):
        def _usuario(nombre, rol=None, org=None, superuser=False):
            u = User.objects.create_user(username=nombre, password="clave.test.123", first_name=nombre.title())
            if superuser:
                u.is_superuser = True
                u.save()
            elif rol:
                Perfil.objects.create(user=u, rol=rol, organizacion=org)
            return u

        cls.u_admin = _usuario("admin", superuser=True)
        cls.u_trans_hcb = _usuario("trans_hcb", Perfil.ROL_TRANSCRIPTOR, cls.org_hcb)
        cls.u_cod_hcb = _usuario("cod_hcb", Perfil.ROL_CODIFICADOR, cls.org_hcb)
        cls.u_dire_hcb = _usuario("dire_hcb", Perfil.ROL_DIRECTOR, cls.org_hcb)
        cls.u_epi_regional = _usuario("epi_regional", Perfil.ROL_EPIDEMIOLOGO, cls.org_regional)
        cls.u_trans_regional = _usuario("trans_regional", Perfil.ROL_TRANSCRIPTOR, cls.org_regional)
        cls.u_dire_regional = _usuario("dire_regional", Perfil.ROL_DIRECTOR, cls.org_regional)
        cls.u_trans_cabudare = _usuario("trans_cabudare", Perfil.ROL_TRANSCRIPTOR, cls.org_cabudare)
        cls.u_trans_otro = _usuario("trans_otro", Perfil.ROL_TRANSCRIPTOR, cls.org_otro_estado)

    # -- Catálogos CIE ------------------------------------------------------
    @classmethod
    def _crear_cie(cls):
        cls.cie10_antiguo = CIE10.objects.create(codigo="A15.0", descripcion="Tuberculosis respiratoria")
        cls.cie10_otro = CIE10.objects.create(codigo="J18.9", descripcion="Neumonía no especificada")
        cls.cie11_capitulo = CIE11.objects.create(
            codigo="01", titulo="Ciertas enfermedades infecciosas o parasitarias",
            nivel=CIE11.NIVEL_CAPITULO,
        )
        cls.cie11_categoria = CIE11.objects.create(
            codigo="CA40", titulo="Dengue", nivel=CIE11.NIVEL_CATEGORIA,
            capitulo=cls.cie11_capitulo, padre=cls.cie11_capitulo,
        )
        cls.cie11_subgrupo = CIE11.objects.create(
            codigo="CA40.0", titulo="Dengue grave", nivel=CIE11.NIVEL_SUBGRUPO,
            capitulo=cls.cie11_capitulo, padre=cls.cie11_categoria,
        )
        cls.cie11_con_subgrupo_oblig = CIE11.objects.create(
            codigo="CB10", titulo="Fiebre hemorrágica", nivel=CIE11.NIVEL_CATEGORIA,
            capitulo=cls.cie11_capitulo, padre=cls.cie11_capitulo,
            requiere_subgrupo=True,
        )
        MapeoCIE.objects.create(cie10=cls.cie10_antiguo, cie11=cls.cie11_categoria, tipo=MapeoCIE.TIPO_EXACTO)
        MapeoCIE.objects.create(cie10=cls.cie10_otro, cie11=cls.cie11_categoria, tipo=MapeoCIE.TIPO_PARCIAL)

    # -- Eventos ENO --------------------------------------------------------
    @classmethod
    def _crear_eventos(cls):
        cls.ev_dengue = EventoENO.objects.create(
            codigo_evento="EV-DENGUE", nombre="Dengue", orden_epi12=17,
            en_epi12=True, en_epi14=True, grupo="TRANSMISIBLES",
        )
        EventoENO.objects.create(
            codigo_evento="EV-LEP", nombre="Lepra", orden_epi12=63,
            en_epi12=True, grupo="TRANSMISIBLES",
        )

    # -- Utilidades ----------------------------------------------------------
    def login(self, user):
        self.client.force_login(user)
        return self.client

    def anon_logout(self):
        self.client.logout()
        return self.client

    def datos_nacimiento(self, uid, fecha="2023-05-01", cie11=None, **extra):
        datos = {
            "registro_numero": uid,
            "fecha_evento": fecha,
            "version_cie": "CIE10" if fecha < FECHA_CORTE.isoformat() else "CIE11",
            "sexo": "F",
            "madre_nombres": "Ana",
            "madre_apellidos": "Pérez",
            "madre_cedula": "V-12345678",
            "madre_edad": 25,
        }
        if datos["version_cie"] == "CIE10":
            datos["cie10"] = self.cie10_antiguo.pk
        else:
            datos["cie11"] = (cie11 or self.cie11_categoria).pk
        datos.update(extra)
        return datos

    def crear_nacimiento(self, uid, fecha="2023-05-01", organizacion=None, cie11=None, **extra):
        return self.client.post(
            "/api/registros/nacimientos/",
            self.datos_nacimiento(uid, fecha=fecha, cie11=cie11, organizacion=organizacion, **extra),
            content_type="application/json",
        )