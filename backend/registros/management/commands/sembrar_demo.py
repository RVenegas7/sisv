from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from catalogos.models import CIE10, CIE11
from seguridad.models import Organizacion, Perfil
from territorio.models import ASIC, DivisionTerritorial

from registros import mock_data
from registros.models import Defuncion, FichaVigilancia, Nacimiento
from vigilancia.models import ConsolidadoSemanal, FilaConsolidado
from vigilancia.services import sembrar_filas, semana_epidemiologica

User = get_user_model()

CLAVE_DEMO = "Sisv.2026!"

ORGANIZACIONES = [
    ("MPPS", "Ministerio del Poder Popular para la Salud", Organizacion.NIVEL_MINISTERIO, "", "", None),
    ("LARA-GOB", "Gobernación del Estado Lara", Organizacion.NIVEL_GOBERNACION, "Lara", "", "MPPS"),
    ("LARA-EPI", "Dirección de Epidemiología del Estado Lara", Organizacion.NIVEL_REGIONAL, "Lara", "", "LARA-GOB"),
    ("LARA-HCB", "Hospital Central de Barquisimeto", Organizacion.NIVEL_CENTRO, "Lara", "Iribarren", "LARA-EPI"),
    ("LARA-CAB", "Ambulatorio C.P. Cabudare", Organizacion.NIVEL_CENTRO, "Lara", "Palavecino", "LARA-EPI"),
]

USUARIOS = [
    ("admin", "", "", "admin@sisv.local", True, True, None, None),
    ("laraepid", "Epidemiología", "Regional", "", False, False, Perfil.ROL_TRANSCRIPTOR, "LARA-EPI"),
    ("hbcentral", "Transcripción", "HCB", "", False, False, Perfil.ROL_TRANSCRIPTOR, "LARA-HCB"),
    ("codificadora", "Codificadora", "Regional", "", False, False, Perfil.ROL_CODIFICADOR, "LARA-EPI"),
    ("epi", "", "", "", False, False, Perfil.ROL_EPIDEMIOLOGO, None),
    ("dir", "", "", "", False, False, Perfil.ROL_DIRECTOR, "LARA-EPI"),
]


def _campos(modelo):
    return {f.name for f in modelo._meta.fields}


def _cie10(codigo):
    if not codigo:
        return None
    return CIE10.objects.filter(codigo=codigo).first() or CIE10.objects.filter(codigo__startswith=codigo).first()


def _cie11(codigo):
    if not codigo:
        return None
    return CIE11.objects.filter(codigo=codigo).first()


class Command(BaseCommand):
    help = "Siembra organizaciones, usuarios y registros de demostración (mock_data) en la base de datos real."

    def add_arguments(self, parser):
        parser.add_argument("--borrar", action="store_true", help="Elimina los registros existentes antes de sembrar.")
        parser.add_argument(
            "--sin-usuarios",
            action="store_true",
            help="Omite la creación de organizaciones y usuarios demo.",
        )

    def handle(self, *args, **options):
        if not options["sin_usuarios"]:
            organizaciones = self._sembrar_organizaciones()
            self._sembrar_usuarios(organizaciones)
            self._sembrar_asic(organizaciones)

        if options["borrar"]:
            for modelo in (Nacimiento, Defuncion, FichaVigilancia):
                borrados = modelo.objects.all().delete()[0]
                self.stdout.write(f"{modelo.__name__}: {borrados} eliminados")
            borrados_cons = ConsolidadoSemanal.objects.all().delete()[0]
            self.stdout.write(f"ConsolidadoSemanal: {borrados_cons} eliminados")

        org = Organizacion.objects.filter(codigo="LARA-HCB").first()
        mapa = {
            Nacimiento: (mock_data.NACIMIENTOS, "registro_numero"),
            Defuncion: (mock_data.DEFUNCIONES, "registro_numero"),
            FichaVigilancia: (mock_data.FICHAS_VIGILANCIA, "codigo_notificacion"),
        }
        creados = 0
        for modelo, (registros, campo_unicidad) in mapa.items():
            campos = _campos(modelo)
            existentes = set(modelo.objects.values_list(campo_unicidad, flat=True))
            for r in registros:
                if r[campo_unicidad] in existentes:
                    continue
                valores = {k: v for k, v in r.items() if k in campos}
                valores.pop("id", None)
                valores["organizacion"] = org
                valores["cie10"] = _cie10((r.get("cie10_detalle") or {}).get("codigo"))
                valores["cie11"] = _cie11((r.get("cie11_detalle") or {}).get("codigo"))
                if org:
                    for campo in ("estado", "municipio"):
                        if getattr(org, campo):
                            valores[campo] = getattr(org, campo)
                modelo.objects.create(**valores)
                existentes.add(r[campo_unicidad])
                creados += 1
        self.stdout.write(self.style.SUCCESS(f"Registros de demostración sembrados: {creados}"))

        self._sembrar_consolidado(org)

    def _sembrar_organizaciones(self):
        creadas = 0
        organizaciones = {}
        for codigo, nombre, nivel, estado, municipio, padre_codigo in ORGANIZACIONES:
            padre = organizaciones.get(padre_codigo)
            org, nueva = Organizacion.objects.update_or_create(
                codigo=codigo,
                defaults={
                    "nombre": nombre,
                    "nivel": nivel,
                    "estado": estado,
                    "municipio": municipio,
                    "padre": padre,
                    "activo": True,
                },
            )
            organizaciones[codigo] = org
            creadas += int(nueva)
        self.stdout.write(self.style.SUCCESS(f"Organizaciones demo: {creadas} creadas, {len(organizaciones)} totales"))
        return organizaciones

    def _sembrar_usuarios(self, organizaciones):
        creados = 0
        for username, nombre, apellido, email, es_super, es_staff, rol, org_codigo in USUARIOS:
            user, nuevo = User.objects.get_or_create(username=username)
            if nuevo:
                user.set_password(CLAVE_DEMO)
                creados += 1
            user.first_name = nombre
            user.last_name = apellido
            user.email = email
            user.is_superuser = es_super
            user.is_staff = es_super or es_staff
            user.is_active = True
            user.save()
            if rol or org_codigo:
                Perfil.objects.update_or_create(
                    user=user,
                    defaults={
                        "rol": rol or Perfil.ROL_TRANSCRIPTOR,
                        "organizacion": organizaciones.get(org_codigo),
                    },
                )
        self.stdout.write(self.style.SUCCESS(f"Usuarios demo: {creados} creados, {len(USUARIOS)} totales"))

    def _sembrar_asic(self, organizaciones):
        lara = DivisionTerritorial.objects.filter(nivel="ESTADO", nombre__iexact="Lara").order_by("id").first()
        if lara is None:
            self.stdout.write("Sin estado Lara en territorio: se omite el ASIC demo.")
            return
        iribarren, _ = DivisionTerritorial.objects.get_or_create(
            nivel=DivisionTerritorial.NIVEL_MUNICIPIO, nombre="Iribarren", padre=lara,
            defaults={"codigo": ""},
        )
        catedral, _ = DivisionTerritorial.objects.get_or_create(
            nivel=DivisionTerritorial.NIVEL_PARROQUIA, nombre="Catedral", padre=iribarren,
            defaults={"codigo": ""},
        )
        asic, nuevo = ASIC.objects.update_or_create(
            codigo="ASIC-LARA-NORTE",
            defaults={
                "nombre": "ASIC Barquisimeto Norte",
                "parroquia": catedral,
                "direccion": "Av. Vargas con Calle 23, Barquisimeto",
                "responsable": "Coordinación ASIC (designe)",
                "telefono": "0251-0000000",
                "email": "asic.norte@mpps.gob.ve",
                "establecimientos_adscritos": 1,
                "activo": True,
            },
        )
        hcb = organizaciones.get("LARA-HCB")
        if hcb is not None:
            hcb.asic = asic
            hcb.parroquia = "Catedral"
            hcb.save(update_fields=["asic", "parroquia"])
        self.stdout.write(
            self.style.SUCCESS(
                f"ASIC demo: {'creado' if nuevo else 'ya existía'} → {asic} · vinculado a {hcb.nombre if hcb else 'HCB'}."
            )
        )

    def _sembrar_consolidado(self, org):
        if org is None:
            self.stdout.write("Sin organización demo: se omite el consolidado de vigilancia.")
            return
        anio, semana = semana_epidemiologica(timezone.localdate())
        cons, nuevo = ConsolidadoSemanal.objects.get_or_create(
            organizacion=org,
            anio=anio,
            semana=semana,
            tipo=ConsolidadoSemanal.TIPO_MORBILIDAD,
            defaults={
                "estado": ConsolidadoSemanal.ESTADO_BORRADOR,
                "origen": ConsolidadoSemanal.ORIGEN_PROPIO,
            },
        )
        if not nuevo:
            self.stdout.write("Consolidado semanal demo ya existente; sin cambios.")
            return
        sembrar_filas(cons)
        demo = {
            "Dengue sin signos de alarma": (2, 3, 1, 0),
            "Dengue con signos de alarma": (1, 2, 0, 1),
            "Cólera": (0, 0, 0, 0),
            "Tuberculosis": (1, 1, 0, 0),
        }
        ajustadas = 0
        for nombre, (menor_1_h, de_15_19_m, de_25_44_h, de_65_m) in demo.items():
            fila = cons.filas.filter(evento__nombre__icontains=nombre).first()
            if fila is None:
                continue
            fila.menor_1_h = menor_1_h
            fila.de_15_19_m = de_15_19_m
            fila.de_25_44_h = de_25_44_h
            fila.de_65_m = de_65_m
            fila.save()
            ajustadas += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Consolidado demo: {cons} (semana {semana} de {anio}), {cons.filas.count()} filas, {ajustadas} con datos de ejemplo."
            )
        )
