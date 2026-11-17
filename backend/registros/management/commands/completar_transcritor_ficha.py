"""Completa el transcriptor y el subtipo de las fichas legacy: MM, MI y violentas (§46).

Las fichas importadas del legacy vienen de dos tablas y **ambas guardan quién las transcribió**
(el análisis inicial solo había revisado ``HISTDOC``, que sí está vacío):

- ``sismai."CASOS_MMI"`` (10.798 fichas de morbilidad materno-infantil): ``USUARIO`` lleno en el
  100 %, 38 logins. Dentro de esa tabla, el **formulario** distingue MM de MI:
  ``RENGLON_CASOSMM."HCASOSMMI"`` (749 casos de muerte materna) y
  ``RENGLON_CASOSMI."HCASOSMMI"`` (10.047 de muerte infantil). Los 2 restantes no están en
  ningún renglón: quedan sin subtipo y el reporte los informa.
- ``sismai."M_VIOLENTA"`` (12.409 muertes violentas): ``LOGIN`` lleno en el 100 %, 115 logins.

Se copian a ``FichaVigilancia.transcrito_legacy`` (el login no es cuenta de SISV),
``transcrito_en`` (``FECHAOPERACION``, la fecha de trabajo) y ``subtipo_legacy``
(``MM``/``MI``/``VIOLENTA``). No pisa valores ya escritos y es idempotente: una segunda corrida
no encuentra nada que cambiar (los 2 casos sin renglón se quedan sin subtipo a propósito).
Sin ``--ejecutar`` solo informa. Requiere el esquema espejo ``sismai`` en PostgreSQL.
"""

from django.core.management.base import BaseCommand
from django.db import connection, transaction

# MM/MI se derivan de los renglones del formulario; la ficha en sí no lo dice.
_EXISTE_MM = (
    'EXISTS (SELECT 1 FROM sismai."RENGLON_CASOSMM" r '
    'WHERE r."HCASOSMMI" = k."ID")'
)
_EXISTE_MI = (
    'EXISTS (SELECT 1 FROM sismai."RENGLON_CASOSMI" r '
    'WHERE r."HCASOSMMI" = k."ID")'
)

_PENDIENTE_MMI = (
    "btrim(COALESCE(f.transcrito_legacy, '')) = '' "
    "OR (btrim(COALESCE(f.subtipo_legacy, '')) = '' AND (" + _EXISTE_MM + " OR " + _EXISTE_MI + "))"
)

_SQL_MMI = (
    "UPDATE registros_fichavigilancia f SET "
    'transcrito_legacy = CASE WHEN btrim(COALESCE(f.transcrito_legacy, \'\')) = \'\' '
    'THEN btrim(k."USUARIO") ELSE f.transcrito_legacy END, '
    'transcrito_en = COALESCE(f.transcrito_en, k."FECHAOPERACION", f.creado_en), '
    "subtipo_legacy = CASE WHEN btrim(COALESCE(f.subtipo_legacy, '')) = '' THEN "
    "CASE WHEN " + _EXISTE_MM + " THEN 'MM' WHEN " + _EXISTE_MI + " THEN 'MI' "
    "ELSE '' END ELSE f.subtipo_legacy END "
    'FROM sismai."CASOS_MMI" k '
    'WHERE k."ID"::bigint::text = f.legacy_id '
    "AND f.legacy_tabla = 'CASOS_MMI' "
    'AND btrim(COALESCE(k."USUARIO", \'\')) <> \'\' '
    "AND (" + _PENDIENTE_MMI + ")"
)

_SQL_VIOLENTA = (
    "UPDATE registros_fichavigilancia f SET "
    'transcrito_legacy = CASE WHEN btrim(COALESCE(f.transcrito_legacy, \'\')) = \'\' '
    'THEN btrim(m."LOGIN") ELSE f.transcrito_legacy END, '
    'transcrito_en = COALESCE(f.transcrito_en, m."FECHAOPERACION", f.creado_en), '
    "subtipo_legacy = CASE WHEN btrim(COALESCE(f.subtipo_legacy, '')) = '' "
    "THEN 'VIOLENTA' ELSE f.subtipo_legacy END "
    'FROM sismai."M_VIOLENTA" m '
    'WHERE m."ID"::bigint::text = f.legacy_id '
    "AND f.legacy_tabla = 'M_VIOLENTA' "
    'AND btrim(COALESCE(m."LOGIN", \'\')) <> \'\' '
    "AND (btrim(COALESCE(f.transcrito_legacy, '')) = '' "
    "OR btrim(COALESCE(f.subtipo_legacy, '')) = '')"
)

_CONTAR_MMI = (
    "SELECT count(*) FROM registros_fichavigilancia f "
    'JOIN sismai."CASOS_MMI" k ON k."ID"::bigint::text = f.legacy_id '
    "AND f.legacy_tabla = 'CASOS_MMI' "
    'WHERE btrim(COALESCE(k."USUARIO", \'\')) <> \'\' AND (' + _PENDIENTE_MMI + ")"
)

_CONTAR_VIOLENTA = (
    "SELECT count(*) FROM registros_fichavigilancia f "
    'JOIN sismai."M_VIOLENTA" m ON m."ID"::bigint::text = f.legacy_id '
    "AND f.legacy_tabla = 'M_VIOLENTA' "
    'WHERE btrim(COALESCE(m."LOGIN", \'\')) <> \'\' '
    "AND (btrim(COALESCE(f.transcrito_legacy, '')) = '' "
    "OR btrim(COALESCE(f.subtipo_legacy, '')) = '')"
)

_YA_COMPLETOS = (
    "SELECT count(*) FROM registros_fichavigilancia "
    "WHERE TRIM(COALESCE(transcrito_legacy, '')) <> ''"
)

_RESUMEN = (
    "SELECT COALESCE(NULLIF(subtipo_legacy, ''), 'SIN_CLASIFICAR'), count(*) "
    "FROM registros_fichavigilancia WHERE transcrito_legacy <> '' GROUP BY 1 ORDER BY 2 DESC"
)

# El UNION ALL se envuelve en una subconsulta: un GROUP BY suelto al final se aplicaría a
# todo el UNION y PostgreSQL lo rechaza («column must appear in the GROUP BY clause»), que
# además abortaba la transacción y hacía fallar el UPDATE posterior.
_TOP_LOGINS = (
    "SELECT login, sum(n) AS n FROM ("
    'SELECT btrim(k."USUARIO") AS login, count(*) AS n '
    'FROM registros_fichavigilancia f '
    'JOIN sismai."CASOS_MMI" k ON k."ID"::bigint::text = f.legacy_id '
    "AND f.legacy_tabla = 'CASOS_MMI' "
    "GROUP BY 1 "
    "UNION ALL "
    'SELECT btrim(m."LOGIN"), count(*) FROM registros_fichavigilancia f '
    'JOIN sismai."M_VIOLENTA" m ON m."ID"::bigint::text = f.legacy_id '
    "AND f.legacy_tabla = 'M_VIOLENTA' "
    "GROUP BY 1"
    ") t GROUP BY 1 ORDER BY 2 DESC LIMIT 12"
)


class Command(BaseCommand):
    help = (
        "Copia el transcriptor legacy de las fichas (CASOS_MMI.USUARIO y M_VIOLENTA.LOGIN) y "
        "clasifica MM/MI/VIOLENTA. Dry-run por defecto; --ejecutar aplica."
    )

    def add_arguments(self, parser):
        parser.add_argument("--ejecutar", action="store_true", help="Aplica los UPDATE.")
        parser.add_argument(
            "--limite", type=int, default=None,
            help="Máximo de fichas por tabla a actualizar (solo con --ejecutar).",
        )

    def _contar(self, cur, sql):
        try:
            cur.execute(sql)
            return cur.fetchone()[0]
        except Exception:  # noqa: BLE001 - sin espejo no se puede informar
            return None

    def handle(self, *args, **opts):
        ejecutar = opts["ejecutar"]
        limite = opts["limite"]

        # Lecturas fuera del bloque atómico de escritura: en PostgreSQL un error de lectura
        # dentro de una transacción deja el resto inutilizable y el UPDATE fallaría con
        # «current transaction is aborted» en vez de con el error real (pasó con _TOP_LOGINS).
        with connection.cursor() as cur:
            cur.execute(_YA_COMPLETOS)
            self.stdout.write(f"Ya tienen transcriptor legacy: {cur.fetchone()[0]} fichas.")

            mmi = self._contar(cur, _CONTAR_MMI)
            violenta = self._contar(cur, _CONTAR_VIOLENTA)
            if mmi is None and violenta is None:
                self.stderr.write(
                    "No se pudo leer el espejo sismai (¿no está montado?)."
                )
                return
            self.stdout.write(
                f"Fichas con transcriptor recuperable: {mmi or 0} de CASOS_MMI (MM/MI) "
                f"+ {violenta or 0} de M_VIOLENTA (violentas)."
            )

            if (mmi or 0) + (violenta or 0):
                try:
                    cur.execute(_TOP_LOGINS)
                    self.stdout.write("  Logins con más fichas en ese cruce:")
                    for login, n in cur.fetchall()[:12]:
                        self.stdout.write(f"    {login:<12} {n}")
                except Exception as exc:  # noqa: BLE001 - informativo, no impide el backfill
                    self.stderr.write(f"  (no se pudo listar los logins: {exc})")

            if not ejecutar:
                self.stdout.write(
                    self.style.WARNING("Dry-run: no se escribió nada. Use --ejecutar para aplicar.")
                )
                return

        total = 0
        with connection.cursor() as cur, transaction.atomic():
            if mmi:
                cur.execute(_SQL_MMI)
                total += cur.rowcount
                self.stdout.write(f"  CASOS_MMI (MM/MI): {cur.rowcount} fichas.")
            if violenta:
                cur.execute(_SQL_VIOLENTA)
                total += cur.rowcount
                self.stdout.write(f"  M_VIOLENTA: {cur.rowcount} fichas.")
        self.stdout.write(self.style.SUCCESS(f"Actualizadas: {total} fichas."))

        with connection.cursor() as cur:
            cur.execute(_RESUMEN)
            self.stdout.write("  Reparto por subtipo (fichas atribuidas):")
            for subtipo, n in cur.fetchall():
                self.stdout.write(f"    {subtipo:<14} {n}")
