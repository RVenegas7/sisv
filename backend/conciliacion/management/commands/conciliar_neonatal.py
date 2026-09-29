"""Concilia la muerte neonatal del registro MMI de la oficina contra SISV.

Lado legacy: `sismai."CASOS_MMI"` (registro materno-infantil), tomando solo los
neonatos —edad en horas, o en días de 0 a 27— y atribuyendo cada caso al
establecimiento que reportó el sobre ENO (`HDOCUMENTO` → `DOCUMENTO.HORIGEN`).

Lado SISV: `registros.Defuncion` con fecha de nacimiento conocida y 0 a 27 días
de vida. Es la misma definición que usa el tablero.

⚠ **La semana se calcula en los dos lados desde la fecha real del evento**, nunca
desde `DOCUMENTO."PERIODO"`: en el legacy ese campo no es una semana, es un número
de formulario del centro y sus rangos se solapan (en 2019 el periodo 29 va del 2
de enero al 12 de septiembre). Usar `PERIODO` produciría diferencias de un
número de formulario, no de captura.

⚠ Esto **no** concilia la muerte materna: `CASOS_MMI` mezcla materna, infantil y
otras sin marcarlas, y usa `HSEXO` con la convención inversa a `RENGLONTELE`. El
indicador de MM sale de `Defuncion.embarazo_o_puerperio`. Ver PENDIENTES.md §20.
"""
import csv
import os
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from conciliacion.models import ConciliacionNeonatal
from conciliacion.services import normalizar_centro
from seguridad.models import Organizacion
from vigilancia.services import semana_epidemiologica

LARA_ROOT = [67754, 3441583108]
CODIGO_FALLBACK = "LEGACY-LARA"

# `DOCUMENTO."TIPO"` distingue el tipo de formulario semanal. El 1 es el ENO de
# mortalidad (RENGLONTELE) y el 23 es el formulario MMI individual: los 10.754
# documentos de `CASOS_MMI` son tipo 23, sin excepción entre 2009 y 2026. Filtrar
# por 1 (como hace `conciliar_eno`) deja el lado legacy vacío.
TIPO_MMI = 23

# 27 días en horas: un caso registrado en horas sigue siendo neonatal hasta acá.
HORAS_NEONATAL = 27 * 24


class Command(BaseCommand):
    help = "Compara los neonatos del registro MMI de la oficina contra SISV, por semana y centro."

    def add_arguments(self, parser):
        parser.add_argument("--desde", type=int, default=2009, help="Año mínimo (default 2009).")
        parser.add_argument("--anio", type=int, default=0, help="Limita a un solo año.")
        parser.add_argument("--ejecutar", action="store_true",
                            help="Escribe el resultado. Sin esta opción solo informa.")
        parser.add_argument("--csv", default="", help="Exporta el diff a un CSV (UTF-8 BOM).")
        parser.add_argument("--todo-pais", action="store_true",
                            help="Ignora el filtro Lara (solo depuración).")
        parser.add_argument("--alerta", type=int, default=5,
                            help="Diferencia absoluta que dispara el aviso de hueco de captura "
                                 "(default 5).")

    def handle(self, *args, **opts):
        desde = opts["anio"] or opts["desde"]
        self.stdout.write(
            f"Conciliando mortalidad neonatal (0-27 días) desde {desde}"
            + (f" — solo {opts['anio']}" if opts["anio"] else "")
        )
        nombres = self._nombres_establecimiento()
        org_por_nombre = self._organizaciones()
        fallback_id = self._fallback_id()
        area = None if opts["todo_pais"] else self._area()

        legacy = self._legacy(desde, area)
        sisv = self._sisv(desde)

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
            registros.append(ConciliacionNeonatal(
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
        self._informe(registros, tot_l, tot_s, por_estado, opts["alerta"])

        if opts["ejecutar"]:
            with transaction.atomic():
                ConciliacionNeonatal.objects.all().delete()
                ConciliacionNeonatal.objects.bulk_create(registros, batch_size=2000)
            self.stdout.write(self.style.SUCCESS(
                f"Escritos {len(registros):,} filas en ConciliacionNeonatal"))
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
        """[(establecimiento, anio, semana, neonatos)] del registro MMI."""
        sql = """
            SELECT d."HORIGEN"::bigint, c."FECHAOCURRENCIA"::date, count(*)
            FROM sismai."CASOS_MMI" c
            JOIN sismai."DOCUMENTO" d ON d."ID" = c."HDOCUMENTO"
            WHERE d."TIPO" = %s AND c."FECHAOCURRENCIA" >= %s
              AND (   (c."UNIDAD_EDAD" IN ('H', 'h') AND c."EDAD" <= %s)
                   OR (c."UNIDAD_EDAD" IN ('D', 'd') AND c."EDAD" <= 27) )
        """
        params = [TIPO_MMI, f"{desde}-01-01", HORAS_NEONATAL]
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

    def _sisv(self, desde):
        """[(organizacion, anio, semana, neonatos)] de `registros.Defuncion`."""
        sql = """
            SELECT d."organizacion_id", d."fecha_evento"::date, count(*)
            FROM registros_defuncion d
            WHERE d."fecha_evento" >= %s AND d."fecha_nacimiento" IS NOT NULL
              AND (d."fecha_evento"::date - d."fecha_nacimiento"::date) BETWEEN 0 AND 27
              AND d."organizacion_id" IS NOT NULL
            GROUP BY 1, 2
        """
        salida = defaultdict(int)
        with connection.cursor() as cur:
            cur.execute(sql, [f"{desde}-01-01"])
            for org_id, fecha, n in cur.fetchall():
                if not fecha:
                    continue
                anio, semana = semana_epidemiologica(fecha)
                salida[(int(org_id), anio, semana)] += int(n or 0)
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

    def _informe(self, registros, tot_l, tot_s, por_estado, alerta):
        self.stdout.write(
            f"Filas: {len(registros):,} · legacy {tot_l:,} · SISV {tot_s:,} · "
            f"diferencia {tot_l - tot_s:,}"
        )
        self.stdout.write("  " + " · ".join(f"{k}={v:,}" for k, v in sorted(por_estado.items())))
        if tot_s:
            self.stdout.write(
                f"Desviación global: {(tot_l - tot_s) / tot_s * 100:+.1f} % (legacy sobre SISV)")
        elif tot_l:
            self.stdout.write(self.style.ERROR(
                "SISV no tiene ni un neonato en el periodo: el lado de certificados esta vacio."))

        # El año es la unidad que decide: una semana de un centro con 18 casos
        # contra 0 es ruido, pero un año con 165 contra 5 es el sistema caído.
        por_anio = defaultdict(lambda: [0, 0])
        for r in registros:
            por_anio[r.anio][0] += r.legado
            por_anio[r.anio][1] += r.sisv
        self.stdout.write("\n  Año   Legacy    SISV    Dif.     %")
        for anio in sorted(por_anio):
            leg, sis = por_anio[anio]
            dif = leg - sis
            p = f"{dif / sis * 100:+.0f} %" if sis else "—"
            self.stdout.write(f"  {anio}  {leg:7,}  {sis:6,}  {dif:+6,}  {p:>6}")

        # Un gap sostenido del legacy sobre SISV significa que el certificado no
        # entró, no que SISV contara mal: en 2019-2021 el sistema estuvo caído.
        # El agregado regional se excluye del aviso: por construcción junta
        #establecimientos que SISV imputa a organizaciones concretas, así que
        # siempre saldría como "todo el legacy y nada de SISV".
        guiones = [(r.anio, r.semana, r) for r in registros
                   if r.estado in ("SOLO_CRUDO", "DIFERENCIA")
                   and r.diferencia >= alerta and not r.es_agregado_sin_org]
        agregado = [r for r in registros if r.es_agregado_sin_org]
        if agregado:
            self.stdout.write(
                f"Agregado regional: {sum(r.legado for r in agregado):,} neonatos legacy de "
                f"{sum(r.cantidad_centros_legacy for r in agregado):,} establecimientos sin "
                f"organización propia (van a LEGACY-LARA, no se pierden)."
            )
        if not guiones:
            return
        self.stdout.write(self.style.WARNING(
            f"\n! {len(guiones)} semana(s) con el registro de la oficina por encima de SISV:"))
        for anio, semana, r in sorted(guiones, key=lambda x: -x[2].diferencia)[:15]:
            self.stdout.write(f"   {anio} S{semana:02d} legacy={r.legado} sisv={r.sisv} "
                              f"(+{r.diferencia})")

    def _csv(self, ruta):
        with open(ruta, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh, delimiter=";")
            w.writerow(["anio", "semana", "organizacion_id", "organizacion", "centros_legacy",
                        "agregado_sin_org", "legacy", "sisv", "diferencia", "estado", "resolucion"])
            for r in ConciliacionNeonatal.objects.select_related("organizacion").iterator():
                w.writerow([r.anio, r.semana, r.organizacion_id, r.organizacion.nombre,
                            r.cantidad_centros_legacy, "si" if r.es_agregado_sin_org else "no",
                            r.legado, r.sisv, r.diferencia, r.estado, r.resolucion])
        self.stdout.write(f"CSV: {ruta}")
