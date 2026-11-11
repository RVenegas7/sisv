"""Completa la edad declarada del fallecido en los registros del legacy (§44).

El certificado legacy guarda la edad del fallecido en ``EDAD`` + ``TIPOEDAD``
(``A`` años, ``M`` meses, ``D`` días, ``H`` horas). El ETL ya la importa para las
defunciones nuevas; este comando la **rellena en las que ya estaban cargadas**, que
son la mayoría del histórico.

¿Para qué? Para clasificar la mortalidad infantil sin depender solo de
``fecha_evento - fecha_nacimiento``: hay certificados con la fecha de nacimiento mal.
El caso reportado es el **4957244** (Jacob Alexander Cantillo Castillo, murió a los
20 minutos el 10/01/2026, Hospital Central de Barquisimeto): su ``FECHA_N`` es
``2025-01-10``, un año antes, y por eso el sistema lo mostraba como «1 año» y lo dejaba
fuera de la mortalidad neonatal. Su edad declarada es ``0 H``.

**Nunca pisa un valor ya escrito** (solo toca ``edad IS NULL``) y es idempotente. Es un
``UPDATE`` dentro de una transacción; sin ``--ejecutar`` solo informa. Requiere el
esquema espejo ``sismai`` (PostgreSQL), así que se corre contra el espejo refrescado.
"""

from django.core.management.base import BaseCommand
from django.db import connection, transaction

# Unidades del legacy que el modelo entiende (A/M/D/H). Cualquier otro valor se ignora.
_UNIDAD_SQL = (
    "CASE c.\"TIPOEDAD\" "
    "WHEN 'A' THEN 'ANIOS' WHEN 'M' THEN 'MESES' "
    "WHEN 'D' THEN 'DIAS' WHEN 'H' THEN 'HORAS' END"
)

_FILTRO = (
    "c.\"ID\"::bigint::text = d.legacy_id AND d.legacy_tabla = 'CERTIFICADO' "
    "AND d.edad IS NULL "
    "AND c.\"EDAD\" IS NOT NULL "
    "AND c.\"TIPOEDAD\" IN ('A', 'M', 'D', 'H')"
)

# Certificados con edad en horas/días cuya FECHA_N no cuadra (más de 31 días de
# diferencia): son justo los que se clasificaban mal por mirar solo las fechas.
_ANOMALIAS = (
    'SELECT count(*) FROM sismai."CERTIFICADO" '
    "WHERE \"TIPOEDAD\" IN ('H', 'D') "
    "AND (\"FECHA_M\" IS NOT NULL) "
    "AND (\"FECHA_N\" IS NULL OR \"FECHA_N\" < \"FECHA_M\" - interval '31 days')"
)


def consulta_edades(contar):
    if contar:
        return (
            'SELECT count(*) FROM registros_defuncion d JOIN sismai."CERTIFICADO" c '
            f"ON {_FILTRO}"
        )
    return (
        'UPDATE registros_defuncion d SET '
        'edad = GREATEST(LEAST(round(c."EDAD")::int, 1000), 0), '
        f"edad_unidad = {_UNIDAD_SQL} "
        'FROM sismai."CERTIFICADO" c '
        f"WHERE {_FILTRO}"
    )


class Command(BaseCommand):
    help = (
        "Completa edad/edad_unidad en las defunciones del legacy (CERTIFICADO.EDAD + "
        "TIPOEDAD). Dry-run por defecto; --ejecutar aplica."
    )

    def add_arguments(self, parser):
        parser.add_argument("--ejecutar", action="store_true", help="Aplica el UPDATE.")

    def handle(self, *args, **opts):
        ejecutar = opts["ejecutar"]
        with connection.cursor() as cur, transaction.atomic():
            cur.execute(consulta_edades(contar=True))
            pendientes = cur.fetchone()[0]
            self.stdout.write(
                "defunciones: %d con edad declarada recuperable (EDAD ← CERTIFICADO.EDAD, "
                "TIPOEDAD → edad_unidad)." % pendientes
            )
            if pendientes and ejecutar:
                cur.execute(consulta_edades(contar=False))
                self.stdout.write(f"  Actualizados: {cur.rowcount}")

            cur.execute(_ANOMALIAS)
            anomalias = cur.fetchone()[0]
            if anomalias:
                self.stdout.write(
                    f"  Ojo (§44): {anomalias} certificados con edad en horas/días y FECHA_N "
                    "que no cuadra; con la edad declarada ya se clasifican bien."
                )
            if not ejecutar:
                transaction.set_rollback(True)

        if not ejecutar:
            self.stdout.write("Dry-run: no se modificó nada. Use --ejecutar para aplicar.")
