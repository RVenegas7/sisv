"""Completa el número REAL del certificado físico en los registros del legacy.

El ETL importó ``registro_numero = LEG-CERT-<ID de Oracle>`` / ``LEG-RN-<ID>``; ese
número es la clave interna de Oracle, no el impreso en el certificado (§27.16 de
PENDIENTES.md). El número físico sí existe en el espejo:

- **Defunción** ← ``sismai."CERTIFICADO"."NUMEROMSDS"`` (nunca vacío).
- **Nacimiento** ← ``sismai."CERTNACIMIENTO"."NROPLANILLA"``
  (join por ``NAC_RNACIDO."HCERTIFICADO"``).

Lo rellena para que el cruce de `despacho` (talonarios entregados vs regresados)
trabaje contra la serie física del talonario y no contra la PK de Oracle.

**Nunca pisa un valor ya escrito** (solo toca campos vacíos) y es idempotente. Es un
``UPDATE`` por bloque dentro de una transacción. Sin ``--ejecutar`` solo informa.
Requiere el esquema espejo ``sismai`` (PostgreSQL); en la oficina debe correrse contra
el espejo refrescado.

Cautelas ya documentadas (§27.16.5): ``NUMEROMSDS`` tiene 62 valores repetidos y
algunos que parecen fecha (p. ej. ``05032026``); se reportan, no abortan.
"""

from django.core.management.base import BaseCommand
from django.db import connection, transaction

_FILTRO_DEF = (
    "c.\"ID\"::bigint::text = d.legacy_id AND d.legacy_tabla = 'CERTIFICADO' "
    "AND btrim(COALESCE(d.numero_certificado, '')) = '' "
    'AND btrim(COALESCE(c."NUMEROMSDS", \'\')) <> \'\''
)

_FILTRO_NAC = (
    "r.\"ID\"::bigint::text = n.legacy_id AND n.legacy_tabla = 'NAC_RNACIDO' "
    "AND btrim(COALESCE(n.numero_planilla, '')) = '' "
    'AND btrim(COALESCE(cn."NROPLANILLA", \'\')) <> \'\''
)


def consulta_defunciones(contar):
    if contar:
        return (
            'SELECT count(*) FROM registros_defuncion d JOIN sismai."CERTIFICADO" c '
            "ON c.\"ID\"::bigint::text = d.legacy_id AND d.legacy_tabla = 'CERTIFICADO' "
            "WHERE btrim(COALESCE(d.numero_certificado, '')) = '' "
            'AND btrim(COALESCE(c."NUMEROMSDS", \'\')) <> \'\''
        )
    return (
        'UPDATE registros_defuncion d SET numero_certificado = btrim(c."NUMEROMSDS") '
        f'FROM sismai."CERTIFICADO" c WHERE {_FILTRO_DEF}'
    )


def consulta_nacimientos(contar):
    if contar:
        return (
            'SELECT count(*) FROM registros_nacimiento n '
            'JOIN sismai."NAC_RNACIDO" r '
            "ON r.\"ID\"::bigint::text = n.legacy_id AND n.legacy_tabla = 'NAC_RNACIDO' "
            'JOIN sismai."CERTNACIMIENTO" cn ON cn."ID" = r."HCERTIFICADO" '
            "WHERE btrim(COALESCE(n.numero_planilla, '')) = '' "
            'AND btrim(COALESCE(cn."NROPLANILLA", \'\')) <> \'\''
        )
    return (
        'UPDATE registros_nacimiento n SET numero_planilla = btrim(cn."NROPLANILLA") '
        'FROM sismai."NAC_RNACIDO" r '
        'JOIN sismai."CERTNACIMIENTO" cn ON cn."ID" = r."HCERTIFICADO" '
        f"WHERE {_FILTRO_NAC}"
    )


# Anomalías conocidas del número físico (se reportan; no impiden el backfill).
_REPETIDOS_DEF = (
    'SELECT count(*) FROM (SELECT btrim("NUMEROMSDS") v FROM sismai."CERTIFICADO" '
    "WHERE btrim(COALESCE(\"NUMEROMSDS\", '')) <> '' GROUP BY 1 HAVING count(*) > 1) t"
)
_PARECE_FECHA_DEF = (
    'SELECT count(*) FROM sismai."CERTIFICADO" '
    'WHERE "NUMEROMSDS" ~ \'^[0-3][0-9][0-1][0-9](19|20)[0-9][0-9]$\''
)


class Command(BaseCommand):
    help = (
        "Completa numero_certificado (defunciones, desde NUMEROMSDS) y "
        "numero_planilla (nacimientos, desde NROPLANILLA) en los registros legacy. "
        "Dry-run por defecto; --ejecutar aplica."
    )

    def add_arguments(self, parser):
        parser.add_argument("--ejecutar", action="store_true", help="Aplica los UPDATE.")
        parser.add_argument("--solo", choices=["defunciones", "nacimientos"], default=None)

    def handle(self, *args, **opts):
        ejecutar = opts["ejecutar"]
        solo = opts["solo"]
        pasos = []
        if solo in (None, "defunciones"):
            pasos.append(("defunciones", "numero_certificado ← CERTIFICADO.NUMEROMSDS",
                          consulta_defunciones))
        if solo in (None, "nacimientos"):
            pasos.append(("nacimientos", "numero_planilla ← CERTNACIMIENTO.NROPLANILLA",
                          consulta_nacimientos))

        with connection.cursor() as cur, transaction.atomic():
            for nombre, descripcion, consulta in pasos:
                cur.execute(consulta(contar=True))
                pendientes = cur.fetchone()[0]
                self.stdout.write(f"{nombre}: {pendientes} con número físico recuperable ({descripcion}).")
                if pendientes and ejecutar:
                    cur.execute(consulta(contar=False))
                    self.stdout.write(f"  Actualizados: {cur.rowcount}")
            if solo in (None, "defunciones"):
                cur.execute(_REPETIDOS_DEF)
                repetidos = cur.fetchone()[0]
                cur.execute(_PARECE_FECHA_DEF)
                parecen_fecha = cur.fetchone()[0]
                if repetidos or parecen_fecha:
                    self.stdout.write(
                        f"  Ojo (calidad ya conocida, §27.16.5): {repetidos} NUMEROMSDS "
                        f"repetidos; {parecen_fecha} parecen fecha. Se cargan igual."
                    )
            if not ejecutar:
                transaction.set_rollback(True)

        if not ejecutar:
            self.stdout.write("Dry-run: no se modificó nada. Use --ejecutar para aplicar.")
