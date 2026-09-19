import csv
import os
import re
import zipfile
from pathlib import Path

from django.core.management.base import BaseCommand

from catalogos.models import CIE10, CIE11, MapeoCIE

DEMO = [
    ("A09", "1A40.Z", "PAR"),
    ("B54", "1F4Z", "EXA"),
    ("I10", "BA00.Z", "EXA"),
    ("K30", "MD92", "EXA"),
]

CODIGO_CIE10 = re.compile(r"^([A-Z]\d\d)(\d*)$")


def normalizar_cie10(codigo):
    """Pasa 'A000' → 'A00.0', deja 'A00' como está y devuelve '' para rangos (A00-B99)."""
    codigo = (codigo or "").strip()
    if "." in codigo:
        return codigo
    m = CODIGO_CIE10.match(codigo)
    if not m:
        return ""
    base, resto = m.group(1), m.group(2)
    return base if not resto else f"{base}.{resto}"


class Command(BaseCommand):
    help = (
        "Importa equivalencias CIE-10 <-> CIE-11 (cross-walk). Fuentes: zip oficial de la OMS "
        "(mapping.zip con 10To11*/11To10*) o CSV manual codigo_cie10;codigo_cie11;tipo(EXA|PAR|INE)."
    )

    def add_arguments(self, parser):
        parser.add_argument("archivo", nargs="?", default=None, help="Ruta a mapping.zip de la OMS o CSV manual.")
        parser.add_argument("--omision", dest="omision", default=None, help="Tipo por defecto (EXA|PAR|INE).")
        parser.add_argument("--borrar", action="store_true", help="Elimina las equivalencias existentes.")
        parser.add_argument("--demo", action="store_true", help="Siembra un conjunto de ejemplo verificado.")
        parser.add_argument("--solo-categorias", action="store_true", help="Omite bloques/capítulos (solo códigos reales).")

    def handle(self, *args, **options):
        if options["borrar"]:
            n = MapeoCIE.objects.all().delete()[0]
            self.stdout.write(f"Equivalencias eliminadas: {n}")

        flag = options.get("archivo")
        if flag and (flag.lower().endswith(".zip") or Path(flag).is_dir()):
            self.std_out = self.stdout
            creados, saltados = self._importar_oms_zip(flag, options)
        else:
            pares = []
            if flag:
                pares = list(self._leer(flag))
            elif options["demo"]:
                pares = DEMO
            else:
                self.stderr.write("Indique mapping.zip, un CSV o use --demo.")
                return
            creados = 0
            saltados = 0
            omision = (options["omision"] or "").upper()
            for c10, c11, tipo in pares:
                if not omision:
                    pasos = self._resolver_tipo(c10, c11)
                    tipo = pasos[0] if pasos else "PAR"
                o10 = CIE10.objects.filter(codigo=c10).first()
                o11 = CIE11.objects.filter(codigo=c11).first()
                if o10 is None or o11 is None:
                    saltados += 1
                    self.stderr.write(f"Sin coincidencia en catálogos: {c10} -> {c11}")
                    continue
                _, nuevo = MapeoCIE.objects.get_or_create(cie10=o10, cie11=o11, defaults={"tipo": tipo})
                if nuevo:
                    creados += 1
            self.stdout.write(self.style.SUCCESS(f"Equivalencias importadas: {creados} (omitidas: {saltados})"))

    def _importar_oms_zip(self, ruta, options):
        """Importa mapping.zip de la OMS (release CC BY-ND).

        Usa 10To11MapToOneCategory.txt como base y 11To10MapToOneCategory.txt
        para clasificar el round-trip (EXA si c10 -> c11 y c11 -> c10 coincide).
        """
        Path("/tmp").mkdir(exist_ok=True)
        destino = Path("/tmp") / f"mapeos_oms_{abs(hash(str(ruta)))}"
        if Path(ruta).is_dir():
            dir_src = Path(ruta)
        else:
            with zipfile.ZipFile(ruta) as z:
                z.extractall(destino)
            dir_src = destino

        fw = dir_src / "10To11MapToOneCategory.txt"
        bw = dir_src / "11To10MapToOneCategory.txt"
        if not fw.exists():
            self.stdout.write(self.style.ERROR("No se encontró 10To11MapToOneCategory.txt."))
            return 0, 0

        # Mapa inverso c11base -> {c10} para el round-trip
        reverso = {}
        if bw.exists():
            with open(bw, encoding="utf-8-sig", errors="replace") as f:
                for r in csv.DictReader(f, delimiter="\t"):
                    c11 = (r.get("icd11Code") or "").strip().split("&")[0]
                    c10 = normalizar_cie10(r.get("icd10Code"))
                    if c11 and c10:
                        reverso.setdefault(c11, set()).add(c10)

        tipo_fuerzado = (options["omision"] or "").upper()
        creados = 0
        saltados = 0
        with open(fw, encoding="utf-8-sig", errors="replace") as f:
            filas = csv.DictReader(f, delimiter="\t")
            n_total = 0
            for r in filas:
                c10 = normalizar_cie10(r.get("icd10Code"))
                c11raw = (r.get("icd11Code") or "").strip()
                c11 = c11raw.split("&")[0]
                if not c10 or not c11:
                    continue
                n_total += 1
                if options["solo_categorias"] and re.fullmatch(r"[A-Z]\d\d(?:\.\d+[A-Z]?)?", c10) is None:
                    continue
                tipo_usar = tipo_fuerzado
                if not tipo_usar:
                    c11_fuentes = reverso.get(c11)
                    if c11_fuentes == {c10} and "&" not in c11raw:
                        tipo_usar = "EXA"
                    elif "&" in c11raw or (c11_fuentes and len(c11_fuentes) > 1):
                        tipo_usar = "PAR"
                    else:
                        tipo_usar = "INE"
                o10 = CIE10.objects.filter(codigo=c10).first()
                o11 = CIE11.objects.filter(codigo=c11).first()
                if o10 is None or o11 is None:
                    saltados += 1
                    if saltados <= 15:
                        self.stderr.write(f"Sin coincidencia en catálogos: {c10} -> {c11}")
                    continue
                _, nuevo = MapeoCIE.objects.get_or_create(cie10=o10, cie11=o11, defaults={"tipo": tipo_usar})
                if nuevo:
                    creados += 1
        self.stdout.write(self.style.SUCCESS(f"Equivalencias importadas: {creados} (omitidas: {saltados})"))
        return creados, saltados

    def _resolver_tipo(self, c10, c11):
        """Heurística EXA/PAR/INE según cobertura de códigos base."""
        c10b = c10.replace(".", "")
        c11b = c11.replace(".", "")
        if not c10b or not c11b:
            return ("PAR", "INE")
        # Misma raíz (ej. A00 y 1A00): 1:1 → exacto
        if c10b == c11b or (len(c10b) < 4 and c10b == c11b[:3]) or (len(c11b) < 4 and c11b == c10b[:3]):
            return ("EXA", "PAR", "INE")
        # Un código más específico (CIE-10 de 4-5 dígitos apuntando a un solo CIE-11)
        if len(c10b) > len(c11b):
            return ("PAR", "EXA", "INE")
        return ("INE", "PAR", "EXA")

    def _leer(self, ruta):
        with open(ruta, newline="", encoding="utf-8-sig") as f:
            for fila in csv.reader(f, delimiter=";"):
                if not fila or not fila[0].strip():
                    continue
                c10 = fila[0].strip().upper()
                c11 = fila[1].strip().upper() if len(fila) > 1 else ""
                if not c10 or not c11:
                    continue
                tipo = fila[2].strip().upper() if len(fila) > 2 and fila[2].strip() else ""
                if tipo not in ("EXA", "PAR", "INE"):
                    tipo = "PAR"
                yield (c10, c11, tipo)