import re
import unicodedata
from pathlib import Path

from django.core.management.base import BaseCommand

from vigilancia.models import EventoENO

RAIZ = Path(__file__).resolve().parent.parent.parent.parent.parent
NORMATIVA = RAIZ / "docs" / "normativa"

LINEA = re.compile(r"^\s*(\d{1,3})\s+(\S.*)$")

NOTIFICACION_INMEDIATA = [
    "cólera", "cólera", "peste", "ebola", "viruela", "sarampión", "parálisis flácida",
    "fiebre amarilla", "rabia", "tétanos neonatal", "meningitis meningocóccica",
    "covid", "hantavirosis", "sindrome respiratorio agudo severo", "sars", "difteria",
]

GRUPO_MATERNO_INFANTIL = [
    "sífilis congénita", "tétanos neonatal", "tétanos obstétrico", "sindrome de rubeola congenita",
    "muerte infantil", "muerte materna", "caso morbilidad materna", "síndrome de rubeola congénita",
]
GRUPO_IRA = [
    "rinofaringitis", "sinusitis", "faringitis", "amigdalitis", "laringitis", "traqueitis",
    "epiglotitis", "bronquitis", "bronquiolitis", "neumonías", "influenza", "covid",
    "infeccion respiratoria aguda grave", "infección respiratoria aguda grave", "sars",
    "vías respirat", "vias respirat", "sindrome respiratorio agudo severo",
]
GRUPO_ITS = [
    "sífilis", "gonocóccica", "papiloma", "condiloma", "tricomoniasis", "candidiasis genital",
    "leucorrea", "vih", "sida", "iaas",
]
GRUPO_CARGAS = [
    "hipertension", "cardiopatía", "enfermedad cerebrovascular", "epoc", "asma",
    "diabetes", "tumores", "trast.", "enfermedad renal", "accid",
]


def limpiar_nombre(texto):
    """Texto del formulario sin punto final residual ni espacios extra."""
    texto = texto.strip().rstrip(".")
    return re.sub(r"\s{2,}", " ", texto)


def normalizar(texto):
    """Clave de unión: sin paréntesis, mayúsculas, sin tildes, espacios colapsados."""
    sin_parentesis = re.sub(r"\([^)]*\)", "", texto)
    sin_acentos = unicodedata.normalize("NFD", sin_parentesis)
    sin_acentos = "".join(c for c in sin_acentos if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", (sin_acentos or "").lower()).strip()


def extraer_codigos(texto):
    m = re.findall(r"\(([^)]*)\)", texto)
    raw = " ".join(m).replace("CIE 11", "").replace("CIE-11", "")
    codigos = re.findall(
        r"(?:\b[1-9][A-Z]|\b[A-Z]{2})[0-9][A-Z0-9]*(?:\.[A-Z0-9]+)?"
        r"(?:-(?:[1-9][A-Z]|[A-Z]{2})[0-9][A-Z0-9]*(?:\.[A-Z0-9]+)?)*",
        raw,
    )
    return ", ".join(codigos) if codigos else ""


def extraer_codigos_cie10(texto):
    """Extrae códigos CIE-10 (una letra + dígitos, p. ej. Y40 o Y40-Y57).

    El formulario oficial duplica ciertos eventos: la primera fila lleva el
    código CIE-11 y la segunda el equivalente CIE-10 (p. ej. EPI-14 46/48 y
    47/49 «Efectos Adversos»). Esta función captura el juego CIE-10 de la
    segunda aparición para conservarlo en `codigos_cie10`.
    """
    m = re.findall(r"\(([^)]*)\)", texto)
    raw = " ".join(m).replace("CIE 10", "").replace("CIE-10", "")
    codigos = re.findall(
        r"\b[A-Z]\d{1,2}(?:\.\d+)?"
        r"(?:-[A-Z]\d{1,2}(?:\.\d+)?)*",
        raw,
    )
    return ", ".join(codigos) if codigos else ""


def parsear(ruta, rango, es_epi12):
    """Extrae (orden, nombre) de las líneas del formulario dentro de `rango`."""
    rutas = NORMATIVA / ruta
    if not rutas.exists():
        return {}
    eventos = {}
    for linea in rutas.read_text(encoding="utf-8", errors="replace").splitlines():
        m = LINEA.match(linea)
        if not m:
            continue
        orden = int(m.group(1))
        if orden not in rango:
            continue
        nombre = limpiar_nombre(m.group(2))
        if "enfermedades micoticas" in normalizar(nombre):
            continue
        eventos[orden] = nombre
    return eventos


def slug_evento(nombre, orden, usado):
    base = re.sub(r"[^a-z0-9]+", "_", normalizar(nombre)).strip("_")[:40]
    cand = f"ENO_{base}" or "ENO"
    i = 2
    while cand in usado:
        i += 1
        cand = f"ENO_{base}_{orden}"
    usado.add(cand)
    return cand


def grupo_de(nombre, es_epi12, orden):
    n = normalizar(nombre)
    if (es_epi12 and orden >= 102) or (not es_epi12 and orden >= 95):
        return "MICOTICAS"
    if any(pat in n for pat in GRUPO_MATERNO_INFANTIL):
        return "MATERNO_INFANTIL"
    if any(pat in n for pat in GRUPO_CARGAS):
        return "CARGAS"
    if any(pat in n for pat in GRUPO_ITS):
        return "ITS"
    if any(pat in n for pat in GRUPO_IRA):
        return "IRA"
    return "TRANSMISIBLES"


def notificacion_de(nombre):
    n = normalizar(nombre)
    if any(pat in n for pat in NOTIFICACION_INMEDIATA):
        return EventoENO.NOTIFICACION_INMEDIATA
    return EventoENO.NOTIFICACION_SEMANAL


class Command(BaseCommand):
    help = "Carga el catálogo de Eventos ENO (notificación obligatoria) desde los formularios oficiales EPI-12/EPI-14."

    def add_arguments(self, parser):
        parser.add_argument("--borrar", action="store_true", help="Borra el catálogo existente antes de cargar.")
        parser.add_argument(
            "--archivo-epi12",
            default=str(NORMATIVA / "EPI-12_texto.txt"),
            help="Ruta al texto del formulario EPI-12 (morbilidad).",
        )
        parser.add_argument(
            "--archivo-epi14",
            default=str(NORMATIVA / "EPI-14_texto.txt"),
            help="Ruta al texto del formulario EPI-14 (mortalidad).",
        )

    def handle(self, *args, **options):
        if options["borrar"]:
            borrados = EventoENO.objects.all().delete()[0]
            self.stdout.write(f"Catálogo ENO existente eliminado: {borrados}")

        epi12 = parsear(options["archivo_epi12"], range(1, 115), es_epi12=True)
        epi14 = parsear(options["archivo_epi14"], range(1, 108), es_epi12=False)
        self.stdout.write(f"EPI-12: {len(epi12)} eventos · EPI-14: {len(epi14)} eventos")

        por_clave = {}
        for orden, nombre in epi12.items():
            por_clave.setdefault(normalizar(nombre), {"epi12": [], "epi14": []})["epi12"].append((orden, nombre))
        for orden, nombre in epi14.items():
            por_clave.setdefault(normalizar(nombre), {"epi12": [], "epi14": []})["epi14"].append((orden, nombre))

        usado = set()

        def _unir(extractor, textos):
            vistos = set()
            salida = []
            for t in textos:
                for c in (extractor(t) or "").split(","):
                    c = c.strip()
                    if c and c not in vistos:
                        vistos.add(c)
                        salida.append(c)
            return ", ".join(salida)

        creados = actualizados = 0
        for clave, info in sorted(por_clave.items(), key=lambda kv: (min(o for o, _ in (kv[1]["epi12"] or kv[1]["epi14"])))):
            epi12_items = sorted(info["epi12"])
            epi14_items = sorted(info["epi14"])
            orden12 = epi12_items[0][0] if epi12_items else None
            orden14 = epi14_items[0][0] if epi14_items else None
            nombre = epi12_items[0][1] if epi12_items else epi14_items[0][1]
            texto12 = [n for _, n in epi12_items]
            texto14 = [n for _, n in epi14_items]
            codigo12 = _unir(extraer_codigos, texto12)
            codigo14 = _unir(extraer_codigos, texto14)
            codigos_cie11 = " / ".join(c for c in (codigo12, codigo14) if c)
            c10_12 = _unir(extraer_codigos_cie10, texto12)
            c10_14 = _unir(extraer_codigos_cie10, texto14)
            codigos_cie10 = " / ".join(c for c in (c10_12, c10_14) if c)

            obj, nuevo = EventoENO.objects.update_or_create(
                orden_epi12=orden12,
                orden_epi14=orden14,
                defaults={
                    "codigo_evento": slug_evento(nombre, orden12 or orden14, usado),
                    "nombre": nombre,
                    "en_epi12": bool(epi12_items),
                    "en_epi14": bool(epi14_items),
                    "codigos_cie11": codigos_cie11,
                    "notificacion": notificacion_de(nombre),
                    "grupo": grupo_de(nombre, bool(epi12_items), orden12 or orden14),
                    "activo": True,
                    **({"codigos_cie10": codigos_cie10} if codigos_cie10 else {}),
                },
            )
            creados += int(nuevo)
            actualizados += int(not nuevo)

        total = EventoENO.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Eventos ENO: {creados} creados, {actualizados} actualizados, {total} en catálogo."
            )
        )