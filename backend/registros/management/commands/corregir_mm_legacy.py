"""Corrige la marca de muerte materna en las defunciones ya importadas del legacy.

El ETL original mapeaba solo ``HPRESENCIAEMBARAZO = 1`` (embarazo al momento de la
muerte) y descartaba el ``2`` (puerperio, últimos 12 meses). El catálogo
``sismai.PRESENCIAEMBARAZO`` define 01=AL MOMENTO DE LA MUERTE, 02=EN LOS ULTIMOS 12
MESES, 03=NO, 04=IGNORADO, 05=SIN INFORMACION: **ambas 1 y 2 son muerte materna**.

Como el ETL es idempotente por ``legacy_id`` (no vuelve a tocar filas existentes),
corregir el comando de importación no repara lo ya cargado: este comando lo hace.

Ejecutar: ``manage.py corregir_mm_legacy --ejecutar`` (por defecto solo informa).
Requiere el espejo PostgreSQL (``sismai."CERTIFICADO"``).
"""
from django.core.management.base import BaseCommand
from django.db import connection, transaction

from registros.management.commands.importar_legacy_registros import CODIGOS_MM, LOTE_DEF
from registros.models import Defuncion

CODIGOS = ", ".join(str(c) for c in sorted(CODIGOS_MM))

# El enlace con el espejo: 'registros_defuncion' se une por el ID del CERTIFICADO legacy
# (el ETL guarda str(int(ID)) en legacy_id).
VINCULO = 'd.legacy_id = trunc(c."ID")::bigint::text'
LOTE = f"d.lote_id = '{LOTE_DEF}'"


def union():
    """FROM ... para los SELECT de conteo."""
    return f"""
    FROM registros_defuncion d
    JOIN sismai."CERTIFICADO" c ON {VINCULO}
    WHERE {LOTE}
    """


def desde():
    """FROM ... para los UPDATE (la tabla a actualizar ya está en la sentencia)."""
    return f"""
    FROM sismai."CERTIFICADO" c
    WHERE {VINCULO} AND {LOTE}
    """


class Command(BaseCommand):
    help = (
        "Reasigna embarazo_o_puerperio según sismai.PRESENCIAEMBARAZO (1=embarazo, "
        "2=puerperio). Dry-run por defecto."
    )

    def add_arguments(self, parser):
        parser.add_argument("--ejecutar", action="store_true", help="Aplica la corrección (sin esto solo informa).")

    def _conteo(self, con):
        """(año, n) de las MM ya marcadas (con=True) o por marcar (con=False)."""
        with connection.cursor() as cur:
            cur.execute(
                f"""
                SELECT extract(year from d.fecha_evento) AS anio, count(*) AS n
                {union()}
                  AND d.embarazo_o_puerperio {'IS TRUE' if con else 'IS NOT TRUE'}
                  AND c."HPRESENCIAEMBARAZO" IN ({CODIGOS})
                GROUP BY 1 ORDER BY 1
                """
            )
            return cur.fetchall()

    def _por_codigo(self):
        with connection.cursor() as cur:
            cur.execute(
                f"""
                SELECT c."HPRESENCIAEMBARAZO" AS codigo, count(*)
                {union()}
                  AND c."HPRESENCIAEMBARAZO" IS NOT NULL
                GROUP BY 1 ORDER BY 1
                """
            )
            return cur.fetchall()

    def handle(self, *args, **opts):
        try:
            with connection.cursor() as cur:
                cur.execute('SELECT count(*) FROM sismai."CERTIFICADO"')
        except Exception as exc:  # pragma: no cover - sin espejo legacy
            raise SystemExit(
                "No se encuentra el espejo legacy sismai.\"CERTIFICADO\". "
                "Este comando solo corre contra PostgreSQL con el espejo cargado."
            ) from exc

        base = Defuncion.objects.filter(lote_id=LOTE_DEF)
        self.stdout.write(f"Defunciones del lote {LOTE_DEF}: {base.count()}")

        self.stdout.write("\nDistribución de HPRESENCIAEMBARAZO en la fuente (MM = 1 y 2):")
        catalogo = dict(self._por_codigo())
        for codigo, n in sorted(catalogo.items(), key=lambda x: (x[0] is None, x[0])):
            marca = "  <- cuenta como MM" if int(codigo) in CODIGOS_MM else ""
            self.stdout.write(f"  {int(codigo)}: {n:>6}{marca}")

        ya, faltan = self._conteo(True), self._conteo(False)
        total_ya = sum(n for _a, n in ya)
        total_faltan = sum(n for _a, n in faltan)
        self.stdout.write("\nMM ya marcadas / a marcar, por año de ocurrencia:")
        self.stdout.write(f"  {'año':<6}{'marcadas':>10}{'a marcar':>10}{'total año':>12}")
        por_anio = dict(ya)
        faltan_por_anio = dict(faltan)
        for anio in sorted(set(por_anio) | set(faltan_por_anio)):
            ya_n, falta_n = por_anio.get(anio, 0), faltan_por_anio.get(anio, 0)
            self.stdout.write(f"  {anio or '?':<6}{ya_n:>10}{falta_n:>10}{ya_n + falta_n:>12}")
        self.stdout.write(f"  {'TOTAL':<6}{total_ya:>10}{total_faltan:>10}{total_ya + total_faltan:>12}")

        if total_faltan == 0:
            self.stdout.write(self.style.SUCCESS("No hay nada que corregir."))
            return

        if not opts["ejecutar"]:
            self.stdout.write(
                self.style.WARNING(
                    f"Dry-run: {total_faltan} defunciones pasarían a muerte materna. "
                    "Use --ejecutar para aplicar."
                )
            )
            return

        with transaction.atomic(), connection.cursor() as cur:
            cur.execute(
                f"""
                UPDATE registros_defuncion d
                SET embarazo_o_puerperio = TRUE
                {desde()}
                  AND d.embarazo_o_puerperio IS NOT TRUE
                  AND c."HPRESENCIAEMBARAZO" IN ({CODIGOS})
                """
            )
            marcadas = cur.rowcount
            # Las que el legacy marca 3/4/5 (o NULL) NO son muerte materna: se limpian.
            cur.execute(
                f"""
                UPDATE registros_defuncion d
                SET embarazo_o_puerperio = FALSE
                {desde()}
                  AND d.embarazo_o_puerperio IS TRUE
                  AND (c."HPRESENCIAEMBARAZO" IS NULL OR c."HPRESENCIAEMBARAZO" NOT IN ({CODIGOS}))
                """
            )
            limpiadas = cur.rowcount

        self.stdout.write(
            self.style.SUCCESS(
                f"Marcadas {marcadas} como muerte materna; {limpiadas} desmarcadas. "
                f"MM totales del lote: {Defuncion.objects.filter(lote_id=LOTE_DEF, embarazo_o_puerperio=True).count()}"
            )
        )
