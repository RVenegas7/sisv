import re

from django.core.management.base import BaseCommand
from django.db import connection

from catalogos.models import CIE10

REAL = re.compile(r"^[A-Z][0-9]{2}(\.[0-9A-Z]{1,2})?$")
RANGO_X = re.compile(r"^[A-Z][0-9]{2}\.X$")


def normalizar(codigo):
    """Deja el código en formato OMS (A00.0) sin dagas/asteriscos ni marcadores."""
    codigo = (codigo or "").strip()
    codigo = codigo.replace("\u0086", "").replace("\u2020", "").replace("\u2021", "").replace("*", "")
    codigo = re.sub(r"[^A-Za-z0-9.]", "", codigo)
    return codigo.upper()


class Command(BaseCommand):
    help = (
        "Importa a 'catalogos_cie10' los códigos reales del CIE-10 del sistema legacy "
        "(espejo 'sismai.\"CIE10\"') que no existen en el catálogo nuevo, para no perder "
        "las codificaciones históricas. Se marcan con origen=LEGACY."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--incluir-rangos",
            action="store_true",
            help="Incluye además los códigos de rango/artefactos (p. ej. A00.X, A00A09).",
        )
        parser.add_argument("--dry-run", action="store_true", help="Solo informa, no escribe.")

    def handle(self, *args, **opts):
        with connection.cursor() as cur:
            cur.execute(
                'SELECT "SEQ_ID_ACTUAL", "COD_CLASIFICACION", "DES_CLASIFICACIO1", '
                '"DES_CLASIFICACIO2" FROM sismai."CIE10" ORDER BY "SEQ_ID_ACTUAL";'
            )
            filas = cur.fetchall()

        existentes = dict(CIE10.objects.values_list("codigo", "capitulo"))
        base3 = {}
        letra = {}
        for codigo, capitulo in existentes.items():
            if len(codigo) >= 3:
                base3.setdefault(codigo[:3], capitulo)
            base3.setdefault(codigo.split(".")[0], capitulo)
            letra.setdefault(codigo[:1], capitulo)

        def capitulo_de(codigo):
            if codigo in existentes and existentes[codigo]:
                return existentes[codigo]
            b = codigo.split(".")[0]
            if base3.get(b):
                return base3[b]
            if letra.get(codigo[:1]):
                return letra[codigo[:1]]
            if codigo[:1] == "U":
                return "Códigos para propósitos especiales"
            return ""

        rango = 0
        descartados = 0
        nuevos = {}
        for _, cod_raw, d1, d2 in filas:
            codigo = normalizar(cod_raw)
            if not codigo:
                descartados += 1
                continue
            if RANGO_X.match(codigo) or not REAL.match(codigo):
                rango += 1
                if not opts["incluir_rangos"]:
                    continue
            if codigo in existentes or codigo in nuevos:
                continue
            descripcion = (d1 or d2 or "").strip()[:500]
            if not descripcion:
                descripcion = "(sin descripción en el legacy)"
            nuevos[codigo] = descripcion

        self.stdout.write(
            f"Legacy: {len(filas)} filas | rangos/sin formato: {rango} | sin código: {descartados}"
        )
        self.stdout.write(f"Códigos nuevos a importar: {len(nuevos)}")

        if opts["dry_run"]:
            for codigo in sorted(nuevos)[:50]:
                self.stdout.write(f"  {codigo}: {nuevos[codigo][:70]}")
            return

        objetos = [
            CIE10(
                codigo=codigo,
                descripcion=descripcion,
                capitulo=capitulo_de(codigo),
                origen=CIE10.ORIGEN_LEGACY,
                activo=True,
            )
            for codigo, descripcion in sorted(nuevos.items())
        ]
        creados = CIE10.objects.bulk_create(objetos, batch_size=1000, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS(
                f"CIE-10 legacy importados: {len(creados)} | total en catálogo: {CIE10.objects.count()}"
            )
        )
