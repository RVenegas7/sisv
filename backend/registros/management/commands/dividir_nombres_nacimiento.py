"""Separa el nombre compuesto de la madre/padre/recién nacido en nacimientos (§35).

El legacy guardó en un solo campo «apellidos + nombres» (``NAC_MADRE."NOMBRES"``,
``NAC_RNACIDO."NOMBRES"``…), así que al abrir un certificado se ve todo en *Nombres*
y *Apellidos* queda vacío. Este comando lo divide con ``services.dividir_nombre_compuesto``:

- ``madre_apellidos`` + ``madre_nombres``     ← ``madre_nombres``
- ``padre_apellidos`` + ``padre_nombres``     ← ``padre_nombres``
- ``nino_apellidos``  + ``nino_nombres``      ← ``nino_nombres``

Reglas:

- **Solo toca lo que está a medias:** actúa cuando los apellidos están vacíos y el
  nombre tiene al menos dos palabras (o una coma). Con una sola palabra no hay nada
  que separar y se deja igual, lo que además hace el comando **idempotente**: una vez
  separados, los apellidos ya no están vacíos y la fila deja de seleccionarse.
- **Nunca inventa ni borra:** reparte lo que ya había; no toca otras columnas.
- Sin ``--ejecutar`` solo informa (dry-run). ``--limite`` recorta para probar.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from registros.models import Nacimiento
from registros.services import dividir_nombre_compuesto

# Cada grupo: (prefijo del par nombres/apellidos, etiqueta legible).
GRUPOS = (
    ("madre", "madre"),
    ("padre", "padre"),
    ("nino", "recién nacido"),
)

TAMANO_LOTE = 1000


def _candidatos(queryset, grupos):
    """Filtro de filas con apellidos vacíos y nombre de al menos dos palabras/coma."""
    cond = Q()
    for prefijo in grupos:
        cond |= Q(**{f"{prefijo}_apellidos": "", f"{prefijo}_nombres__regex": r"[\s,]"})
    return queryset.filter(cond)


class Command(BaseCommand):
    help = "Divide el nombre compuesto de madre/padre/recién nacido en apellidos y nombres."

    def add_arguments(self, parser):
        parser.add_argument("--ejecutar", action="store_true",
                            help="Aplica los cambios (sin esto solo informa).")
        parser.add_argument("--solo", choices=[p for p, _ in GRUPOS],
                            help="Limita el trabajo a un solo grupo de persona.")
        parser.add_argument("--limite", type=int, default=0,
                            help="Procesa como máximo N filas (para probar).")

    def handle(self, *args, **options):
        grupos = [prefijo for prefijo, _ in GRUPOS
                  if options["solo"] in (None, prefijo)]
        etiquetas = dict(GRUPOS)

        qs = _candidatos(Nacimiento.objects.all(), grupos).only(
            "id", *[f"{p}_{campo}" for p in grupos for campo in ("nombres", "apellidos")]
        )
        total = qs.count()
        self.stdout.write(
            "Nacimientos con nombre compuesto por separar: " + ", ".join(
                f"{etiquetas[p]}={_candidatos(Nacimiento.objects.all(), [p]).count():,}"
                for p in grupos
            ) + f". Total de filas: {total:,}."
        )
        if not total:
            self.stdout.write(self.style.SUCCESS("No hay nada que separar."))
            return
        if not options["ejecutar"]:
            self.stdout.write(self.style.WARNING(
                "Dry-run: no se modificó nada. Use --ejecutar para aplicar."))
            return

        limite = options["limite"] or None
        cambios = 0
        lote = []
        with transaction.atomic():
            for registro in qs.iterator(chunk_size=TAMANO_LOTE):
                cambio = False
                for prefijo in grupos:
                    nombres = getattr(registro, f"{prefijo}_nombres")
                    if getattr(registro, f"{prefijo}_apellidos"):
                        continue
                    nuevos_nombres, nuevos_apellidos = dividir_nombre_compuesto(nombres)
                    if nuevos_apellidos:
                        setattr(registro, f"{prefijo}_nombres", nuevos_nombres)
                        setattr(registro, f"{prefijo}_apellidos", nuevos_apellidos)
                        cambio = True
                if cambio:
                    lote.append(registro)
                    cambios += 1
                if len(lote) >= TAMANO_LOTE:
                    Nacimiento.objects.bulk_update(
                        lote, [f"{p}_{c}" for p in grupos for c in ("nombres", "apellidos")]
                    )
                    lote = []
                if limite and cambios >= limite:
                    break
            if lote:
                Nacimiento.objects.bulk_update(
                    lote, [f"{p}_{c}" for p in grupos for c in ("nombres", "apellidos")]
                )

        self.stdout.write(self.style.SUCCESS(f"Nacimientos actualizados: {cambios:,}."))
