"""Completa el transcriptor de los certificados de defunción del legacy (§46).

A diferencia de lo que decía el análisis inicial (§45), `sismai."CERTIFICADO"` **sí** guarda
quién transcribió: la columna se llama ``LOGIN`` y está llena en 175.259 de 175.260 filas
(172 logins distintos; el primero es YOLISIMORT / YOLIMAR SIRA, 21.358 certificados).

Ese login **no es una cuenta de SISV** (p. ej. ``YOLISIMORT``), así que se copia a
``Defuncion.transcrito_legacy`` — no a ``transcrito_por``, que es una FK a ``auth.User`` — junto
con ``transcrito_en``, que se rellena con ``CERTIFICADO."FECHAOPERACION"`` (la fecha de la
transcripción, no la de la muerte: difieren en casi todas las filas porque el registro es tardío
y la productividad se mide por mes de trabajo). ``FECHAOPERACION`` está en el 100 % de las filas;
``FECHAELABORACION`` tiene un 26 % nulas y no sirve como respaldo.

Cruce (comprobado el 16/11/2026: las 175.260 defunciones importadas de ``CERTIFICADO`` unen):

    registros_defuncion.legacy_tabla = 'CERTIFICADO'
    registros_defuncion.legacy_id  → sismai."CERTIFICADO"."ID"
    sismai."CERTIFICADO"."LOGIN"   → transcrito_legacy

No pisa un valor ya escrito y es idempotente. Las 17.371 defunciones de ``lara_2019_2020`` no
tienen certificado en el espejo y se informan aparte (no es un error del comando). Sin
``--ejecutar`` solo informa. Requiere el esquema espejo ``sismai`` en PostgreSQL.
"""

from django.core.management.base import BaseCommand
from django.db import connection, transaction


def _where(alias="d", c="c"):
    return (
        f'WHERE {c}."ID"::bigint::text = {alias}.legacy_id '
        f"AND {alias}.legacy_tabla = 'CERTIFICADO' "
        f"AND btrim(COALESCE({alias}.transcrito_legacy, '')) = '' "
        f"AND btrim(COALESCE({c}.\"LOGIN\", '')) <> ''"
    )


def _base(alias="d", c="c"):
    return (
        f'FROM registros_defuncion {alias} '
        f'JOIN sismai."CERTIFICADO" {c} ON {c}."ID"::bigint::text = {alias}.legacy_id '
        f"AND {alias}.legacy_tabla = 'CERTIFICADO' "
        + _where(alias, c)
    )


def consulta_defunciones(contar=False, limite=None):
    if contar:
        return "SELECT count(*) " + _base()
    sql = (
        "UPDATE registros_defuncion d SET "
        'transcrito_legacy = btrim(c."LOGIN"), '
        'transcrito_en = COALESCE(d.transcrito_en, c."FECHAOPERACION", d.creado_en) '
        'FROM sismai."CERTIFICADO" c '
        + _where()
    )
    if limite:
        sql += (
            " AND d.id IN (SELECT id FROM (SELECT d2.id "
            + _base("d2", "c2")
            + f" ORDER BY d2.id LIMIT {int(limite)}) t)"
        )
    return sql


_SIN_CERTIFICADO = (
    "SELECT count(*) FROM registros_defuncion d "
    "WHERE btrim(COALESCE(d.transcrito_legacy, '')) = '' "
    "AND NOT EXISTS (SELECT 1 FROM sismai.\"CERTIFICADO\" c "
    'WHERE c."ID"::bigint::text = d.legacy_id)'
)

_YA_COMPLETOS = (
    "SELECT count(*) FROM registros_defuncion "
    "WHERE TRIM(COALESCE(transcrito_legacy, '')) <> ''"
)

_TOP_LOGINS = (
    'SELECT btrim(c."LOGIN") AS login, count(*) AS n ' + _base()
    + " GROUP BY 1 ORDER BY 2 DESC LIMIT 12"
)


class Command(BaseCommand):
    help = (
        "Copia el login del transcriptor legacy (CERTIFICADO.LOGIN) a "
        "Defuncion.transcrito_legacy y la fecha de operación a transcrito_en. "
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

        # Las lecturas van fuera del bloque atómico de escritura: en PostgreSQL un error de
        # lectura dentro de una transacción deja el resto de la transacción inutilizable y el
        # UPDATE fallaría con «current transaction is aborted» en vez de con el error real.
        pendientes = None
        with connection.cursor() as cur:
            cur.execute(_YA_COMPLETOS)
            self.stdout.write(f"Ya tienen transcriptor legacy: {cur.fetchone()[0]} defunciones.")

            try:
                cur.execute(consulta_defunciones(contar=True))
                pendientes = cur.fetchone()[0]
            except Exception as exc:  # noqa: BLE001 - sin espejo (sqlite) no hay nada que hacer
                self.stderr.write(
                    f"No se pudo leer el espejo sismai (¿no está montado?): {exc}"
                )

            if pendientes is None:
                return
            self.stdout.write(
                f"Defunciones con transcriptor recuperable: {pendientes} "
                '(registros_defuncion.legacy_id → sismai."CERTIFICADO"."LOGIN").'
            )

            if pendientes:
                try:
                    cur.execute(_TOP_LOGINS)
                    self.stdout.write("  Logins con más certificados en ese cruce:")
                    for login, n in cur.fetchall()[:12]:
                        self.stdout.write(f"    {login:<12} {n}")
                except Exception as exc:  # noqa: BLE001 - informativo, no impide el backfill
                    self.stderr.write(f"  (no se pudo listar los logins: {exc})")

            try:
                cur.execute(_SIN_CERTIFICADO)
                self.stdout.write(
                    f"  sin certificado en el espejo (p. ej. lara_2019_2020): "
                    f"{cur.fetchone()[0]}"
                )
            except Exception:  # noqa: BLE001
                pass

            if not ejecutar:
                self.stdout.write(
                    self.style.WARNING("Dry-run: no se escribió nada. Use --ejecutar para aplicar.")
                )
                return
            if not pendientes:
                return

        total = 0
        with connection.cursor() as cur, transaction.atomic():
            cur.execute(consulta_defunciones(contar=False, limite=limite))
            total = cur.rowcount
        self.stdout.write(self.style.SUCCESS(f"Actualizados: {total} defunciones."))
