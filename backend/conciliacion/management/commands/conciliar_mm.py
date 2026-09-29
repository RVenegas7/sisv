"""Concilia la muerte materna del registro de investigación de la oficina contra SISV.

Lado legacy: `sismai."RENGLON_CASOSMM"` enlazado a `sismai."CASOS_MMI"` por
`HCASOSMMI` → `CASOS_MMI."ID"`, atribuyendo cada caso al establecimiento que reportó
el formulario MMI (`CASOS_MMI."HDOCUMENTO"` → `DOCUMENTO.HORIGEN`). Son 748 muertes
maternas de 2009 a 2026 en 19 establecimientos, todas dentro del árbol Lara.

Lado SISV: `registros.Defuncion` con `embarazo_o_puerperio` (`CERTIFICADO.HPRESENCIAEMBARAZO`
en 1 o 2, embarazo o puerperio).

⚠ **Los dos lados no son la misma definición y esa es la conciliación.** El campo del
certificado es un aviso opcional del certificador: en 2026 lo diligencia en 7 de las 18
muertes maternas. Por eso `difere` casi siempre, y esa diferencia **no es una pérdida de
datos**: es que el certificado rarely declara el embarazo y el registro de investigación
sí. El registro es el indicador; el certificado, el dato que se puede recortar por centro
y por el cual además se sabe si la muerte fue notificada.

⚠ `DOCUMENTO."TIPO"` es **23** en los 10.742 documentos MMI, no 1 (1 es el ENO de
mortalidad, `RENGLONTELE`). Filtrar por 1 deja el lado legacy vacío en silencio.

⚠ La semana se calcula en los dos lados desde la fecha real del evento
(`CASOS_MMI."FECHAOCURRENCIA"`), nunca desde `RENGLON_CASOSMM."PERIODOOCURRENCIA"`, que
viene nula en las 749 filas, ni desde `DOCUMENTO."PERIODO"`, que es un número de
formulario del centro con rangos solapados.
"""
import csv
import os
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from conciliacion.models import ConciliacionMaterna
from conciliacion.services import normalizar_centro
from seguridad.models import Organizacion
from vigilancia.services import semana_epidemiologica

LARA_ROOT = [67754, 3441583108]
CODIGO_FALLBACK = "LEGACY-LARA"

# Ver la nota del módulo: los formularios MMI son tipo 23, no 1.
TIPO_MMI = 23


class Command(BaseCommand):
    help = "Compara las muertes maternas del registro de la oficina contra SISV, por semana y centro."

    def add_arguments(self, parser):
        parser.add_argument("--desde", type=int, default=2009, help="Año mínimo (default 2009).")
        parser.add_argument("--anio", type=int, default=0, help="Limita a un solo año.")
        parser.add_argument("--ejecutar", action="store_true",
                            help="Escribe el resultado. Sin esta opción solo informa.")
        parser.add_argument("--csv", default="", help="Exporta el diff a un CSV (UTF-8 BOM).")
        parser.add_argument("--todo-pais", action="store_true",
                            help="Ignora el filtro Lara (solo depuración).")
        parser.add_argument("--alerta", type=int, default=5,
                            help="Diferencia absoluta que dispara el aviso (default 5).")

    def handle(self, *args, **opts):
        desde = opts["anio"] or opts["desde"]
        self.stdout.write(
            f"Conciliando muerte materna (registro de investigación) desde {desde}"
            + (f" — solo {opts['anio']}" if opts["anio"] else "")
        )
        nombres = self._nombres_establecimiento()
        org_por_nombre = self._organizaciones()
        fallback_id = self._fallback_id()
        area = None if opts["todo_pais"] else self._area()

        legacy = self._legacy(desde, area)
        sisv = self._sisv(desde, fallback_id)

        # {(anio, semana, org_id): [legacy, sisv, sin_org, {establecimientos}]}
        celdas = defaultdict(lambda: [0, 0, False, set()])

        org_de_establecimiento = {}
        for est_id, _anio, _semana, _n in legacy:
            if est_id not in org_de_establecimiento:
                org_de_establecimiento[est_id] = org_por_nombre.get(
                    normalizar_centro(nombres.get(est_id, "")))

        for est_id, anio, semana, n in legacy:
            org_real = org_de_establecimiento.get(est_id)
            org_id = org_real if org_real is not None else fallback_id
            if org_id is None:
                continue
            celda = celdas[(anio, semana, org_id)]
            celda[0] += n
            if org_real is None:
                celda[2] = True
            celda[3].add(est_id)

        for org_id, anio, semana, n in sisv:
            celda = celdas[(anio, semana, org_id)]
            celda[1] += n

        registros = []
        for (anio, semana, org_id), (leg, sis, sin_org, ests) in sorted(
                celdas.items(), key=lambda k: (k[0][0], k[0][1], k[0][2])):
            registros.append(ConciliacionMaterna(
                anio=anio, semana=semana, organizacion_id=org_id,
                es_agregado_sin_org=sin_org, cantidad_centros_legacy=len(ests),
                legado=leg, sisv=sis, diferencia=leg - sis,
                estado=self._estado(leg, sis), resolucion="CENTRO_SIN_ORG" if sin_org else "CONCILIADO",
            ))

        tot_l = sum(r.legado for r in registros)
        tot_s = sum(r.sisv for r in registros)
        por_estado = defaultdict(int)
        for r in registros:
            por_estado[r.estado] += 1
        # Distintos reales, no la suma de los `cantidad_centros_legacy` de cada celda:
        # un mismo establecimiento aparece en muchas semanas y sumarlas contaría un
        # centro por semana.
        centros_agregado = set()
        for est_id, org_real in org_de_establecimiento.items():
            if org_real is None and any(est_id in c[3] for c in celdas.values()):
                centros_agregado.add(est_id)
        self._informe(registros, tot_l, tot_s, por_estado, opts["alerta"], centros_agregado)

        if opts["ejecutar"]:
            with transaction.atomic():
                ConciliacionMaterna.objects.all().delete()
                ConciliacionMaterna.objects.bulk_create(registros, batch_size=2000)
            self.stdout.write(self.style.SUCCESS(
                f"Escritos {len(registros):,} filas en ConciliacionMaterna"))
        else:
            self.stdout.write("Sin --ejecutar: no se escribió nada.")

        if opts["csv"]:
            self._csv(opts["csv"])

    # ------------------------------------------------------------------  lectura
    def _nombres_establecimiento(self):
        with connection.cursor() as cur:
            cur.execute('SELECT "ID"::bigint, "NOMBRE" FROM sismai."ESTABLECIMIENTO";')
            return {int(a): (b or "").strip() for a, b in cur.fetchall()}

    def _organizaciones(self):
        return {normalizar_centro(n): i for n, i in
                Organizacion.objects.filter(activo=True).values_list("nombre", "id")}

    def _fallback_id(self):
        org = Organizacion.objects.filter(codigo=CODIGO_FALLBACK).first()
        return org.id if org else None

    def _area(self):
        with connection.cursor() as cur:
            ids = set()
            for root in LARA_ROOT:
                cur.execute(
                    """WITH RECURSIVE t AS (
                           SELECT %s::double precision AS id
                           UNION ALL
                           SELECT e."ID" FROM sismai."ESTABLECIMIENTO" e
                           JOIN t ON e."PADRE" = t.id
                       ) SELECT id FROM t;""", [root])
                ids.update(float(f[0]) for f in cur.fetchall())
        return ids or None

    def _legacy(self, desde, area):
        """[(establecimiento, anio, semana, muertes maternas)] del registro de la oficina.

        `count(DISTINCT "HCASOSMMI")` porque el grano del renglón es (persona, causa):
        una misma persona puede tener más de una causa registrada, y lo que se cuenta
        son muertes, no renglones.
        """
        sql = """
            SELECT d."HORIGEN"::bigint, c."FECHAOCURRENCIA"::date, count(DISTINCT r."HCASOSMMI")
            FROM sismai."RENGLON_CASOSMM" r
            JOIN sismai."CASOS_MMI" c ON c."ID" = r."HCASOSMMI"
            JOIN sismai."DOCUMENTO" d ON d."ID" = c."HDOCUMENTO"
            WHERE d."TIPO" = %s AND c."FECHAOCURRENCIA" >= %s
        """
        params = [TIPO_MMI, f"{desde}-01-01"]
        if area is not None:
            sql += ' AND d."HORIGEN" = ANY(%s)'
            params.append(sorted(area))
        sql += ' GROUP BY 1, 2'
        salida = defaultdict(int)
        with connection.cursor() as cur:
            cur.execute(sql, params)
            for est_id, fecha, n in cur.fetchall():
                if not fecha:
                    continue
                anio, semana = semana_epidemiologica(fecha)
                salida[(int(est_id), anio, semana)] += int(n or 0)
        return [(e, a, s, n) for (e, a, s), n in salida.items()]

    def _sisv(self, desde, fallback_id):
        """[(organizacion, anio, semana, muertes maternas)] de `registros.Defuncion`.

        Los certificados sin organización **no se filtran**: van al mismo agregado
        regional que el lado legacy. Filtrarlos por `organizacion_id IS NOT NULL` los
        borraría en silencio y haría creer que el certificado no registró ninguna muerte
        materna, que es un falso negativo: la muerte está, lo que falta es el centro.
        """
        sql = """
            SELECT d."organizacion_id", d."fecha_evento"::date, count(*)
            FROM registros_defuncion d
            WHERE d."fecha_evento" >= %s AND d."embarazo_o_puerperio" IS TRUE
            GROUP BY 1, 2
        """
        salida = defaultdict(int)
        sin_org = defaultdict(int)
        with connection.cursor() as cur:
            cur.execute(sql, [f"{desde}-01-01"])
            for org_id, fecha, n in cur.fetchall():
                if not fecha:
                    continue
                anio, semana = semana_epidemiologica(fecha)
                if org_id is None:
                    sin_org[(anio, semana)] += int(n or 0)
                else:
                    salida[(int(org_id), anio, semana)] += int(n or 0)
        if fallback_id is not None:
            for (anio, semana), n in sin_org.items():
                salida[(fallback_id, anio, semana)] += n
        return [(o, a, s, n) for (o, a, s), n in salida.items()]

    # ------------------------------------------------------------------  salida
    @staticmethod
    def _estado(legado, sisv):
        if not legado and not sisv:
            return "CUADRA"
        if not sisv:
            return "SOLO_CRUDO"
        if not legado:
            return "SOLO_SISV"
        return "CUADRA" if legado == sisv else "DIFERENCIA"

    def _informe(self, registros, tot_l, tot_s, por_estado, alerta, centros_agregado):
        self.stdout.write(
            f"Filas: {len(registros):,} · registro de la oficina {tot_l:,} · "
            f"certificados {tot_s:,} · diferencia {tot_l - tot_s:,}"
        )
        self.stdout.write("  " + " · ".join(f"{k}={v:,}" for k, v in sorted(por_estado.items())))
        if tot_l:
            pct = (tot_l - tot_s) / tot_l * 100
            self.stdout.write(
                f"El certificado marca el embarazo o puerperio en el {tot_s / tot_l * 100:.1f} % "
                f"de las muertes maternas del registro (faltan {tot_l - tot_s:,}, {pct:.0f} %).")

        por_anio = defaultdict(lambda: [0, 0])
        for r in registros:
            por_anio[r.anio][0] += r.legado
            por_anio[r.anio][1] += r.sisv
        self.stdout.write("\n  Año   Registro  Certif.   Dif.   Marcado")
        for anio in sorted(por_anio):
            leg, sis = por_anio[anio]
            marcado = f"{sis / leg * 100:.0f} %" if leg else "—"
            self.stdout.write(f"  {anio}  {leg:8,}  {sis:7,}  {leg - sis:+6,}  {marcado:>8}")

        agregado = [r for r in registros if r.es_agregado_sin_org]
        if agregado:
            self.stdout.write(
                f"Agregado regional: {sum(r.legado for r in agregado):,} muertes del registro de "
                f"{len(centros_agregado):,} establecimientos sin organización propia (van a "
                f"LEGACY-LARA, no se pierden)."
            )

        if por_estado.get("SOLO_SISV"):
            self.stdout.write(self.style.WARNING(
                f"\n! {por_estado['SOLO_SISV']} semana(s) con muerte materna en el certificado y "
                "no en el registro de investigación: hay muertes que el registro no llegó a "
                "registrar.\n  Ninguna de las dos fuentes es completa. El indicador de MM es el "
                "del registro de investigación y el certificado se reporta aparte."))

    def _csv(self, ruta):
        with open(ruta, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh, delimiter=";")
            w.writerow(["anio", "semana", "organizacion_id", "organizacion", "centros_legacy",
                        "agregado_sin_org", "registro_oficina", "certificados", "diferencia",
                        "estado", "resolucion"])
            for r in ConciliacionMaterna.objects.select_related("organizacion").iterator():
                w.writerow([r.anio, r.semana, r.organizacion_id, r.organizacion.nombre,
                            r.cantidad_centros_legacy, "si" if r.es_agregado_sin_org else "no",
                            r.legado, r.sisv, r.diferencia, r.estado, r.resolucion])
        self.stdout.write(f"CSV: {ruta}")
