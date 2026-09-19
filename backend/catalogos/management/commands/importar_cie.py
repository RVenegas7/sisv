import csv
import os
import re
import sqlite3
import zipfile
from pathlib import Path
from urllib.parse import unquote

from django.core.management.base import BaseCommand

from catalogos.models import CIE10, CIE11, MapeoCIE

ENTITY_RE = re.compile(r"entity(?:%2F|/)(\d+)")
LEADING = re.compile(r"^[\-\s]+")
DASH_GROUPS = re.compile(r"^(?:- )+")
CODIGO_CIE10 = re.compile(r"^([A-Z]\d\d)(\d*)$")


def normalizar_cie10(codigo):
    """Pasa 'A000' → 'A00.0', deja 'A00' como está y descarta códigos con rango (A00-B99)."""
    codigo = (codigo or "").strip()
    if "." in codigo:
        return codigo
    m = CODIGO_CIE10.match(codigo)
    if not m:
        return ""
    base, resto = m.group(1), m.group(2)
    return base if not resto else f"{base}.{resto}"


class Command(BaseCommand):
    help = "Importa catálogos CIE-10 (WHO/OPS español) y CIE-11 (linealización MMS) desde archivos."

    def add_arguments(self, parser):
        parser.add_argument("--cie10", help="Ruta a la base sqlite CIE-10 (tabla CIE: CAPITULO;CODIGO;TITULO)")
        parser.add_argument(
            "--cie10-oms",
            help="Ruta al zip o directorio 'Plain text tabular' de la OMS (capítulos, grupos y códigos) en inglés.",
        )
        parser.add_argument(
            "--cie10-es",
            help="Ruta al CSV en español (formato verasativa/CIE-10 o ciecl): code,code_0..code_4,description,level,source",
        )
        parser.add_argument("--cie11", help="Ruta al CSV de linealización CIE-11 MMS (Code,Title,ClassKind,...)")
        parser.add_argument("--no-clean", action="store_true", help="No borrar los catálogos antes de importar")

    def handle(self, *args, **opts):
        hay_cie10 = bool(opts["cie10"] or opts["cie10_oms"] or opts["cie10_es"])
        if not opts["no_clean"]:
            MapeoCIE.objects.all().delete()
            if hay_cie10:
                CIE10.objects.all().delete()
            if opts["cie11"]:
                CIE11.objects.all().delete()
            self.stdout.write("Catálogos CIE previos eliminados (según lo que se importa).")

        if opts["cie10"]:
            self.importar_cie10(opts["cie10"])
        if opts["cie10_oms"]:
            self.importar_cie10_oms(opts["cie10_oms"])
        if opts["cie10_es"]:
            self.importar_cie10_es(opts["cie10_es"])
        if opts["cie11"]:
            self.importar_cie11(opts["cie11"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Resumen -> CIE10: {CIE10.objects.count()} | CIE11: {CIE11.objects.count()}"
            )
        )

    def importar_cie10(self, ruta):
        if not os.path.exists(ruta):
            self.stdout.write(self.style.ERROR(f"No existe {ruta}"))
            return
        conn = sqlite3.connect(ruta)
        filas = conn.execute("SELECT CAPITULO, CODIGO, TITULO FROM CIE").fetchall()
        conn.close()
        registros = [
            CIE10(
                codigo=(codigo or "").strip(),
                descripcion=(titulo or "").strip(),
                capitulo=(capitulo or "").strip(),
            )
            for capitulo, codigo, titulo in filas
            if (codigo or "").strip()
        ]
        CIE10.objects.bulk_create(registros, batch_size=2000)
        self.stdout.write(f"CIE-10 importados: {len(registros)}")

    def _extraer_oms(self, ruta):
        """Devuelve un Path al directorio con los .txt de la OMS."""
        ruta = Path(ruta)
        if ruta.is_dir():
            return ruta
        destino = Path("/tmp") / f"ie10_oms_{abs(hash(str(ruta)))}"
        with zipfile.ZipFile(ruta) as z:
            z.extractall(destino)
        return destino

    def importar_cie10_oms(self, ruta):
        """Importa el 'Plain text tabular' de la OMS (3 txt separados por ;).

        Estructura de los archivos (descarga oficial https://icdcdn.who.int/icd10/):
        - capítulos:  Nº;Título
        - grupos:     Inicio;Fin;Nº capítulo;Título del bloque
        - códigos:    17 campos; [0]=nivel(3|4|5) [1]=T/N [2]=X/S [3]=capítulo
          [4]=bloque [5]=código con '-' para 3-char [6]=código sin dagger
          [7]=sin punto [8]=título [9]=título corto [10]+=tablas de mortalidad/morbilidad
        """
        if not os.path.exists(ruta):
            self.stdout.write(self.style.ERROR(f"No existe {ruta}"))
            return
        dir_ = self._extraer_oms(ruta)
        capitulos_txt = next(dir_.glob("*chapters.txt"), None)
        codigos_txt = next(dir_.glob("*codes.txt"), None)
        if not capitulos_txt or not codigos_txt:
            self.stdout.write(
                self.style.ERROR("El zip/directorio debe contener ...chapters.txt y ...codes.txt")
            )
            return

        capitulos = {}
        for linea in capitulos_txt.read_text(encoding="latin-1", errors="replace").splitlines():
            partes = linea.split(";")
            if len(partes) >= 2 and partes[0].strip().isdigit():
                capitulos[partes[0].strip()] = partes[1].strip()

        registros = []
        for linea in codigos_txt.read_text(encoding="latin-1", errors="replace").splitlines():
            f = linea.split(";")
            if len(f) < 9:
                continue
            codigo = f[6].strip()
            if not codigo:
                continue
            capitulo = capitulos.get(f[3].strip(), f[3].strip())
            registros.append(
                CIE10(
                    codigo=codigo,
                    descripcion=f[8].strip(),
                    capitulo=capitulo,
                )
            )
        CIE10.objects.bulk_create(registros, batch_size=2000)
        self.stdout.write(f"CIE-10 importados (formato OMS): {len(registros)}")

    def importar_cie10_es(self, ruta):
        """Importa un CSV jerarquizado CIE-10 en español.

        Formato (verasativa/CIE-10 o dataset del paquete R ciecl):
          code,code_0,code_1,code_2,code_3,code_4,description,level,source
          - nivel 0 = capítulo (rango A00-B99), nivel 1 = bloque,
            nivel >=2 = categoría/subcategoría codificable (3,4,5+ dígitos).
        Los códigos van sin punto (A000); se normalizan a formato OMS (A00.0).
        El capítulo se deduce del code_0 y el nombre del capítulo se toma de la
        fila de nivel 0 (descripción en español).
        """
        if not os.path.exists(ruta):
            self.stdout.write(self.style.ERROR(f"No existe {ruta}"))
            return
        with open(ruta, encoding="utf-8-sig", errors="replace") as f:
            filas = list(csv.DictReader(f))

        capitulos = {}
        registros = []
        vistos = set()
        for fila in filas:
            nivel = int(fila.get("level") or 0)
            code = (fila.get("code") or "").strip()
            desc = (fila.get("description") or "").strip()
            if not code or not desc:
                continue
            if nivel == 0:
                capitulos[code] = desc
        for fila in filas:
            nivel = int(fila.get("level") or 0)
            if nivel < 2:
                continue
            codigo = normalizar_cie10(fila.get("code"))
            if not codigo or codigo in vistos:
                continue
            vistos.add(codigo)
            capitulo = capitulos.get((fila.get("code_0") or "").strip(), "")
            registros.append(
                CIE10(
                    codigo=codigo,
                    descripcion=(fila.get("description") or "").strip(),
                    capitulo=capitulo,
                )
            )
        CIE10.objects.bulk_create(registros, batch_size=2000)
        self.stdout.write(f"CIE-10 importados (español): {len(registros)}")

    def importar_cie11(self, ruta):
        if not os.path.exists(ruta):
            self.stdout.write(self.style.ERROR(f"No existe {ruta}"))
            return
        with open(ruta, encoding="utf-8-sig", errors="replace") as f:
            filas = list(csv.DictReader(f))

        objetos = []
        meta = []
        cap_actual = None
        for fila in filas:
            titulo_raw = fila["Title"] or ""
            m_depth = DASH_GROUPS.match(titulo_raw)
            profundidad = m_depth.group().count("-") if m_depth else 0
            titulo = LEADING.sub("", titulo_raw).strip()
            if not titulo:
                continue
            clase = fila["ClassKind"].strip().lower()
            codigo_raw = (fila.get("Code") or "").strip()
            if clase == "chapter":
                nivel = 1
            elif clase == "block":
                nivel = 2
            else:
                nivel = 4 if "." in codigo_raw else 3
            if not codigo_raw:
                m = ENTITY_RE.search(unquote(fila.get("BrowserLink", "")))
                codigo_raw = m.group(1) if m else f"X-{len(objetos)}"
            objetos.append(
                CIE11(
                    codigo=codigo_raw,
                    titulo=titulo,
                    nivel=nivel,
                    requiere_subgrupo=False,
                    activo=True,
                )
            )
            meta.append((profundidad, clase, nivel))

        CIE11.objects.bulk_create(objetos, batch_size=2000)
        indice = {objeto.id: objeto for objeto in objetos}

        pendientes = []
        ultimo_capitulo = None
        for i, (profundidad, clase, nivel) in enumerate(meta):
            if nivel == 1:
                ultimo_capitulo = i
                continue
            j = i - 1
            while j >= 0 and meta[j][0] >= profundidad:
                j -= 1
            padre = indice[objetos[j].id] if j >= 0 else None
            cap = indice[objetos[ultimo_capitulo].id] if ultimo_capitulo is not None else None
            objetos[i].padre = padre
            objetos[i].capitulo = cap
            pendientes.append(objetos[i])

        for inicio in range(0, len(pendientes), 2000):
            CIE11.objects.bulk_update(
                pendientes[inicio : inicio + 2000], ["padre", "capitulo"], batch_size=2000
            )
        padres_con_subgrupos = set(
            CIE11.objects.filter(nivel=4, padre__nivel=3).values_list("padre_id", flat=True)
        )
        if padres_con_subgrupos:
            CIE11.objects.filter(id__in=padres_con_subgrupos).update(requiere_subgrupo=True)
        self.stdout.write(f"CIE-11 importados: {len(objetos)}")