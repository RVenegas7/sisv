"""Recupera el establecimiento de las defunciones que quedaron sin él.

``importar_legacy_registros`` leía solo ``CERTIFICADO."HESTABLECIMIENTO_OCUR"``, que viene
**nulo en 87.203 de los 173.533 certificados**, mientras ``"HESTABLECIMIENTO"`` siempre
está. Esas muertes se importaron sin nombre de establecimiento, y por eso
``asignar_organizacion_legacy`` no pudo asignarles organización (el 50% del histórico
de defunciones quedó con ``organizacion_id IS NULL``).

Este comando rellena el nombre desde ``CERTIFICADO."HESTABLECIMIENTO"`` —mismo criterio de
precedencia que el importador ya corregido: ``_OCUR`` o, si es nulo, el otro— y **nunca
toca un establecimiento ya escrito**. Después, ``asignar_organizacion_legacy`` puede
enlazar esas muertes con su centro.

Es un único ``UPDATE ... FROM`` (no un bucle fila por fila) dentro de una transacción, e
idempotente. Sin ``--ejecutar`` solo informa.
"""

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from registros.models import Defuncion

# _OCUR manda; si es nulo se usa HESTABLECIMIENTO, que siempre viene.
JOIN_ESTABLECIMIENTO = (
    'JOIN sismai."ESTABLECIMIENTO" e '
    'ON e."ID" = COALESCE(c."HESTABLECIMIENTO_OCUR", c."HESTABLECIMIENTO")'
)
SOLO_CERTIFICADO = "d.legacy_id ~ '^[0-9]+$'"
CON_NOMBRE = "e.\"NOMBRE\" IS NOT NULL AND btrim(e.\"NOMBRE\") <> ''"


def _consulta(contar):
    destino = ("SELECT count(*) FROM registros_defuncion d "
               'JOIN sismai."CERTIFICADO" c ON c."ID"::bigint::text = d.legacy_id ' + JOIN_ESTABLECIMIENTO)
    if contar:
        return destino + f" WHERE btrim(d.establecimiento) = '' AND {SOLO_CERTIFICADO} AND {CON_NOMBRE}"
    return (
        "UPDATE registros_defuncion d SET establecimiento = btrim(e.\"NOMBRE\") "
        "FROM sismai.\"CERTIFICADO\" c " + JOIN_ESTABLECIMIENTO +
        f" WHERE c.\"ID\"::bigint::text = d.legacy_id AND btrim(d.establecimiento) = '' "
        f"AND {SOLO_CERTIFICADO} AND {CON_NOMBRE}"
    )


class Command(BaseCommand):
    help = "Rellena el establecimiento de las defunciones importadas sin él (desde CERTIFICADO)."

    def add_arguments(self, parser):
        parser.add_argument("--ejecutar", action="store_true",
                            help="Aplica los cambios (sin esto solo informa).")

    def handle(self, *args, **options):
        total = Defuncion.objects.count()
        sin_est = Defuncion.objects.filter(establecimiento="").count()
        with connection.cursor() as cur:
            cur.execute(_consulta(contar=True))
            recuperables = cur.fetchone()[0]

        self.stdout.write(
            f"Defunciones: {total:,} en total · {sin_est:,} sin establecimiento "
            f"({100.0 * sin_est / total:.1f}%) · {recuperables:,} recuperables desde CERTIFICADO."
        )
        if not recuperables:
            self.stdout.write(self.style.SUCCESS("No hay nada que recuperar."))
            return

        if not options["ejecutar"]:
            self.stdout.write(self.style.WARNING(
                "Dry-run: no se modificó nada. Use --ejecutar para aplicar."))
            return

        with transaction.atomic():
            with connection.cursor() as cur:
                cur.execute(_consulta(contar=False))
                aplicadas = cur.rowcount

        self.stdout.write(self.style.SUCCESS(
            f"Establecimiento recuperado en {aplicadas:,} defunciones."))
        if aplicadas:
            self.stdout.write("Siguiente paso: manage.py asignar_organizacion_legacy --ejecutar")
