"""Completa los nacimientos importados del legacy con datos que el ETL descartó.

``importar_legacy_registros`` leía ``NAC_RNACIDO."NOMBRES"`` (nombre del recién nacido)
y ``NAC_MADRE."HRESIDENCIA"`` (residencia de la madre), pero no había dónde guardarlos:
el modelo ``Nacimiento`` no tenía esos campos hasta el EV-25 (migración ``0006``). Ahora
que existen, este comando los rellena.

- ``nino_nombres`` ← ``NAC_RNACIDO."NOMBRES"``.
- ``madre_residencia_parroquia`` ← ``NAC_MADRE."HRESIDENCIA"`` → ``ORG_GEOGRAFICA`` →
  parroquia del árbol ``DivisionTerritorial`` (por nombre, dentro del municipio y estado
  correctos). Solo se marca ``madre_residencia='V'`` si estaba vacía.

**Nunca pisa un valor ya escrito** (solo toca campos vacíos) y es idempotente. El nombre
del padre ya lo importaba el ETL (``padre_nombres``), así que no se toca.

Es un ``UPDATE`` por bloque (no fila por fila), dentro de una transacción. Sin
``--ejecutar`` solo informa. La resolución territorial usa ``regexp_match``/``initcap``,
así que requiere PostgreSQL.
"""

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from registros.models import Nacimiento

MARCA = "registros_nacimiento"

NOMBRES = (
    "UPDATE registros_nacimiento n "
    'SET nino_nombres = btrim(r."NOMBRES") '
    'FROM sismai."NAC_RNACIDO" r '
    'WHERE r."ID"::bigint::text = n.legacy_id '
    "AND n.legacy_tabla = 'NAC_RNACIDO' "
    "AND btrim(COALESCE(n.nino_nombres, '')) = '' "
    'AND btrim(COALESCE(r."NOMBRES", \'\')) <> \'\''
)

# Resuelve "Estado X, Municipio Y, Parroquia Z" y enlaza la parroquia del árbol.
_RESUELTO = (
    "WITH madre AS ("
    ' SELECT DISTINCT ON ("HCERTIFICADO") "HCERTIFICADO", "HRESIDENCIA"'
    ' FROM sismai."NAC_MADRE" WHERE "HRESIDENCIA" IS NOT NULL'
    "), resuelto AS ("
    ' SELECT r."ID" AS rn_id,'
    " regexp_match(g.\"NOMBRELARGO\","
    " 'Estado\\s+([^,]+),\\s*Municipio\\s+([^,]+),\\s*Parroquia\\s*([^,]+)') AS rr"
    ' FROM sismai."NAC_RNACIDO" r'
    ' JOIN madre m ON m."HCERTIFICADO" = r."HCERTIFICADO"'
    ' JOIN sismai."ORG_GEOGRAFICA" g ON g."NUM_REGION" = m."HRESIDENCIA"'
    ") "
)

_JOIN_TERRITORIO = (
    " JOIN territorio_divisionterritorial p"
    " ON p.nivel='PARROQUIA' AND lower(p.nombre)=lower(initcap(btrim(x.rr[3])))"
    " JOIN territorio_divisionterritorial mu"
    " ON mu.id=p.padre_id AND mu.nivel='MUNICIPIO'"
    " AND lower(mu.nombre)=lower(initcap(btrim(x.rr[2])))"
    " JOIN territorio_divisionterritorial es"
    " ON es.id=mu.padre_id AND es.nivel='ESTADO'"
    " AND lower(es.nombre)=lower(initcap(btrim(x.rr[1])))"
)

_FILTRO_RESIDENCIA = (
    " x.rn_id::bigint::text = n.legacy_id"
    " AND n.legacy_tabla = 'NAC_RNACIDO'"
    " AND n.madre_residencia_parroquia_id IS NULL"
)


def consulta_nombres(contar):
    if contar:
        return (
            "SELECT count(*) FROM registros_nacimiento n "
            'JOIN sismai."NAC_RNACIDO" r ON r."ID"::bigint::text = n.legacy_id '
            "WHERE n.legacy_tabla = 'NAC_RNACIDO' "
            "AND btrim(COALESCE(n.nino_nombres, '')) = '' "
            'AND btrim(COALESCE(r."NOMBRES", \'\')) <> \'\''
        )
    return NOMBRES


def consulta_residencia(contar):
    if contar:
        return (
            _RESUELTO
            + "SELECT count(*) FROM registros_nacimiento n"
            " CROSS JOIN resuelto x" + _JOIN_TERRITORIO
            + " WHERE" + _FILTRO_RESIDENCIA
        )
    return (
        _RESUELTO
        + "UPDATE registros_nacimiento n"
        " SET madre_residencia_parroquia_id = p.id,"
        " madre_residencia = CASE"
        " WHEN btrim(COALESCE(n.madre_residencia, '')) = '' THEN 'V'"
        " ELSE n.madre_residencia END"
        " FROM resuelto x" + _JOIN_TERRITORIO
        + " WHERE" + _FILTRO_RESIDENCIA
    )


class Command(BaseCommand):
    help = "Rellena nombre del recién nacido y residencia materna en nacimientos del legacy."

    def add_arguments(self, parser):
        parser.add_argument("--ejecutar", action="store_true",
                            help="Aplica los cambios (sin esto solo informa).")
        parser.add_argument("--solo", choices=["nombres", "residencia"],
                            help="Limita el trabajo a una sola parte.")

    def handle(self, *args, **options):
        hacer_nombres = options["solo"] in (None, "nombres")
        hacer_residencia = options["solo"] in (None, "residencia")

        with connection.cursor() as cur:
            nombres_rec = residencia_rec = 0
            if hacer_nombres:
                cur.execute(consulta_nombres(contar=True))
                nombres_rec = cur.fetchone()[0]
            if hacer_residencia:
                cur.execute(consulta_residencia(contar=True))
                residencia_rec = cur.fetchone()[0]

        total = Nacimiento.objects.filter(legacy_tabla="NAC_RNACIDO").count()
        self.stdout.write(
            f"Nacimientos del legacy: {total:,} · recuperables nombre={nombres_rec:,} "
            f"residencia madre={residencia_rec:,}."
        )
        if not (nombres_rec or residencia_rec):
            self.stdout.write(self.style.SUCCESS("No hay nada que recuperar."))
            return
        if not options["ejecutar"]:
            self.stdout.write(self.style.WARNING(
                "Dry-run: no se modificó nada. Use --ejecutar para aplicar."))
            return

        with transaction.atomic():
            with connection.cursor() as cur:
                aplicados_n = aplicados_r = 0
                if hacer_nombres:
                    cur.execute(consulta_nombres(contar=False))
                    aplicados_n = cur.rowcount
                if hacer_residencia:
                    cur.execute(consulta_residencia(contar=False))
                    aplicados_r = cur.rowcount

        self.stdout.write(self.style.SUCCESS(
            f"Actualizados: nombre del recién nacido={aplicados_n:,} · "
            f"residencia materna={aplicados_r:,}."))
