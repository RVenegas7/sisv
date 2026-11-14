"""Completa el transcriptor de los certificados de nacimiento del legacy (§45).

El sistema anterior **sí** guarda quién transcribió la natalidad:
``sismai."CERTNACIMIENTO"."USUARIO"`` está lleno en las 439.596 filas del espejo
(311 logins distintos). Ese login **no es una cuenta de SISV** (p. ej. ``JUANANAT``), así
que se copia a ``Nacimiento.transcrito_legacy`` — no a ``transcrito_por``, que es una FK a
``auth.User`` y quedaría vacía— junto con ``transcrito_en``, que se rellena con la **fecha
del certificado** (``FECHACERTIFICADO``): es la que usa el reporte de productividad de la
oficina, porque el mes de productividad es el de la certificación y no el del nacimiento.

Cruce (comprobado el 11/11/2026: 439.282 de 439.476 nacimientos unen):

    registros_nacimiento.legacy_id → sismai."NAC_RNACIDO"."ID"
    NAC_RNACIDO."HCERTIFICADO"     → sismai."CERTNACIMIENTO"."ID"
    CERTNACIMIENTO."USUARIO"       → transcrito_legacy

**Nunca pisa un valor ya escrito** (solo toca ``transcrito_legacy`` vacío y solo rellena
``transcrito_en`` si es nulo) y es idempotente. Sin ``--ejecutar`` solo informa. Requiere
el esquema espejo ``sismai`` en PostgreSQL; en la oficina va sobre el espejo refrescado y
está en la lista compartida de ``migracion/etl_comandos.sh``.

Los nacimientos que no unen se informan (madre/recién nacido sin certificado, o sin
``NAC_RNACIDO``): son 50 y ~144 en el espejo de casa, no un error del comando.
"""

from django.core.management.base import BaseCommand
from django.db import connection, transaction


def _where(alias="n", r="r", cn="cn"):
    return (
        f'WHERE {r}."ID"::bigint::text = {alias}.legacy_id '
        f"AND {alias}.legacy_tabla = 'NAC_RNACIDO' "
        f"AND btrim(COALESCE({alias}.transcrito_legacy, '')) = '' "
        f'AND btrim(COALESCE({cn}."USUARIO", \'\')) <> \'\''
    )


def _base(alias="n", r="r", cn="cn"):
    """FROM/WHERE del cruce, parametrizado por alias para poder anidar el LIMIT."""
    return (
        f'FROM registros_nacimiento {alias} '
        f'JOIN sismai."NAC_RNACIDO" {r} '
        f'ON {r}."ID"::bigint::text = {alias}.legacy_id '
        f'AND {alias}.legacy_tabla = \'NAC_RNACIDO\' '
        f'JOIN sismai."CERTNACIMIENTO" {cn} ON {cn}."ID" = {r}."HCERTIFICADO" '
        + _where(alias, r, cn)
    )


def consulta_nacimientos(contar=False, limite=None):
    if contar:
        return "SELECT count(*) " + _base()
    # El UPDATE no puede repetir la tabla destino en el FROM: se arma sin el
    # `FROM registros_nacimiento` que sí usan los SELECT.
    sql = (
        "UPDATE registros_nacimiento n SET "
        'transcrito_legacy = btrim(cn."USUARIO"), '
        'transcrito_en = COALESCE(n.transcrito_en, cn."FECHACERTIFICADO", n.creado_en) '
        'FROM sismai."NAC_RNACIDO" r '
        'JOIN sismai."CERTNACIMIENTO" cn ON cn."ID" = r."HCERTIFICADO" '
        + _where()
    )
    if limite:
        sql += (
            " AND n.id IN (SELECT id FROM (SELECT n2.id "
            + _base("n2", "r2", "cn2")
            + f" ORDER BY n2.id LIMIT {int(limite)}) t)"
        )
    return sql


_SIN_NAC_RNACIDO = (
    "SELECT count(*) FROM registros_nacimiento n "
    "WHERE n.legacy_tabla = 'NAC_RNACIDO' "
    "AND btrim(COALESCE(n.transcrito_legacy, '')) = '' "
    'AND NOT EXISTS (SELECT 1 FROM sismai."NAC_RNACIDO" r '
    'WHERE r."ID"::bigint::text = n.legacy_id)'
)

_SIN_CERTIFICADO = (
    "SELECT count(*) FROM registros_nacimiento n "
    "WHERE n.legacy_tabla = 'NAC_RNACIDO' "
    "AND btrim(COALESCE(n.transcrito_legacy, '')) = '' "
    'AND EXISTS (SELECT 1 FROM sismai."NAC_RNACIDO" r '
    'WHERE r."ID"::bigint::text = n.legacy_id) '
    'AND NOT EXISTS (SELECT 1 FROM sismai."NAC_RNACIDO" r '
    'JOIN sismai."CERTNACIMIENTO" cn ON cn."ID" = r."HCERTIFICADO" '
    'WHERE r."ID"::bigint::text = n.legacy_id)'
)

_YA_COMPLETOS = (
    "SELECT count(*) FROM registros_nacimiento "
    "WHERE TRIM(COALESCE(transcrito_legacy, '')) <> ''"
)

_TOP_LOGINS = (
    'SELECT btrim(cn."USUARIO") AS login, count(*) AS n ' + _base() +
    " GROUP BY 1 ORDER BY 2 DESC LIMIT 12"
)


class Command(BaseCommand):
    help = (
        "Copia el login del transcriptor legacy (CERTNACIMIENTO.USUARIO) a "
        "Nacimiento.transcrito_legacy y la fecha del certificado a transcrito_en. "
        "Dry-run por defecto; --ejecutar aplica."
    )

    def add_arguments(self, parser):
        parser.add_argument("--ejecutar", action="store_true", help="Aplica el UPDATE.")
        parser.add_argument(
            "--limite", type=int, default=None,
            help="Máximo de registros a actualizar (solo con --ejecutar).",
        )

    def handle(self, *args, **opts):
        ejecutar = opts["ejecutar"]
        limite = opts["limite"]

        with connection.cursor() as cur, transaction.atomic():
            cur.execute(_YA_COMPLETOS)
            ya = cur.fetchone()[0]
            self.stdout.write(f"Ya tienen transcriptor legacy: {ya} nacimientos.")

            pendientes = None
            try:
                cur.execute(consulta_nacimientos(contar=True))
                pendientes = cur.fetchone()[0]
            except Exception as exc:  # noqa: BLE001 - sin espejo (sqlite) no hay nada que hacer
                self.stderr.write(
                    f"No se pudo leer el espejo sismai (¿no está montado?): {exc}"
                )

            if pendientes is None:
                return
            self.stdout.write(
                f"Nacimientos con transcriptor recuperable: {pendientes} "
                "(NAC_RNACIDO → CERTNACIMIENTO.USUARIO)."
            )

            if pendientes:
                cur.execute(_TOP_LOGINS)
                self.stdout.write("  Logins con más certificados en ese cruce:")
                for login, n in cur.fetchall()[:12]:
                    self.stdout.write(f"    {login:<12} {n}")

            for etiqueta, sql in (
                ("sin NAC_RNACIDO (no unen)", _SIN_NAC_RNACIDO),
                ("sin certificado enlazado", _SIN_CERTIFICADO),
            ):
                try:
                    cur.execute(sql)
                    self.stdout.write(f"  {etiqueta}: {cur.fetchone()[0]}")
                except Exception:  # noqa: BLE001
                    pass

            if not ejecutar:
                self.stdout.write(
                    self.style.WARNING("Dry-run: no se escribió nada. Use --ejecutar para aplicar.")
                )
                return
            if not pendientes:
                return
            cur.execute(consulta_nacimientos(contar=False, limite=limite))
            self.stdout.write(self.style.SUCCESS(f"Actualizados: {cur.rowcount} nacimientos."))
