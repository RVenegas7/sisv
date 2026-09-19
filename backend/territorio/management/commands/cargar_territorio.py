import csv
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from territorio.models import DivisionTerritorial


class Command(BaseCommand):
    help = (
        "Importa la división territorial desde un CSV o JSON. "
        "CSV (columnas): nivel;nombre;codigo;padre_nombre   (padre_nombre vacío en ESTADO). "
        "JSON: lista de objetos {nivel, nombre, codigo, padre_nombre}."
    )

    def add_arguments(self, parser):
        parser.add_argument("archivo", nargs="?", help="Ruta del archivo CSV o JSON a importar")
        parser.add_argument("--borrar", action="store_true", help="Vacía la tabla antes de importar")
        parser.add_argument("--solo-estados", action="store_true", help="Solo siembra los estados de Venezuela")

    def handle(self, *args, **opts):
        archivo = opts["archivo"]
        if opts["borrar"]:
            DivisionTerritorial.objects.all().delete()
            self.stdout.write("División territorial previa eliminada.")

        if opts["solo_estados"]:
            self._cargar_estados()
            return

        if not archivo:
            raise CommandError("Indique un archivo CSV/JSON o use --solo-estados")

        ruta = Path(archivo)
        if not ruta.exists():
            raise CommandError(f"No existe: {archivo}")

        if ruta.suffix.lower() == ".json":
            registros = json.loads(ruta.read_text(encoding="utf-8"))
        elif ruta.suffix.lower() == ".csv":
            with ruta.open(encoding="utf-8-sig") as f:
                registros = [
                    {
                        "nivel": r[0].strip().upper(),
                        "nombre": r[1].strip(),
                        "codigo": (r[2].strip() if len(r) > 2 else ""),
                        "padre_nombre": (r[3].strip() if len(r) > 3 else ""),
                    }
                    for r in csv.reader(f, delimiter=";")
                ][1:]
        else:
            raise CommandError("Formato no soportado (use .csv o .json)")

        creados = 0
        for i, reg in enumerate(registros, start=1):
            nivel = reg["nivel"].upper()
            nombre = reg["nombre"].strip()
            if not nombre or nivel not in dict(DivisionTerritorial.NIVEL_CHOICES):
                self.stderr.write(f"[fila {i}] Saltada (nivel inválido o sin nombre): {reg}")
                continue
            padre = None
            padre_nombre = (reg.get("padre_nombre") or "").strip()
            nivel_padre = DivisionTerritorial.NIVEL_ANTERIOR.get(nivel)
            if padre_nombre and nivel_padre:
                padre = (
                    DivisionTerritorial.objects.filter(
                        nivel=nivel_padre, nombre__iexact=padre_nombre, activo=True
                    ).first()
                )
                if padre is None:
                    self.stderr.write(f"[fila {i}] No se halló padre «{padre_nombre}» ({nivel_padre}) para «{nombre}»")
                    continue
            _, creado = DivisionTerritorial.objects.get_or_create(
                nivel=nivel,
                nombre=nombre.title(),
                padre=padre,
                defaults={"codigo": reg.get("codigo", "")},
            )
            if creado:
                creados += 1
        self.stdout.write(self.style.SUCCESS(f"Importados {creados} registros de territorio."))

    def _cargar_estados(self):
        from territorio.data.estados import ESTADOS

        creados = 0
        for codigo, nombre in ESTADOS:
            _, creado = DivisionTerritorial.objects.get_or_create(
                nivel="ESTADO", nombre=nombre, defaults={"codigo": codigo}
            )
            if creado:
                creados += 1
        self.stdout.write(self.style.SUCCESS(f"Estados sembrados: {creados}."))