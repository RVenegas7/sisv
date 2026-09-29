"""Concilia la transcripción legacy (RENGLONTELE) contra los consolidados de SISV.

Ambos lados se agregan con los **mismos filtros** que aplicó
`importar_legacy_vigilancia` (árbol Lara, `DOCUMENTO."TIPO"=1`, enfermedad con
equivalente ENO), porque si difieren la diferencia mediría un filtro y no un
error de captura.

El grano de la conciliación es (organización, semana, tipo, evento). `FilaConsolidado`
no guarda el ID legacy de la enfermedad, así que el lado SISV solo se puede
indexar por `evento_id`; las enfermedades legacy **sin** equivalente se aíslan con
una clave negativa propia para que la pérdida quede a la vista en vez de mezclarse.
"""
import csv
import os
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from conciliacion.models import ConciliacionENO, ConciliacionENOCentro
from conciliacion.services import clasificar, es_pseudo_total, normalizar_centro
from seguridad.models import Organizacion
from vigilancia.legacy_mapeo import por_evento_id
from vigilancia.models import EventoENO

LARA_ROOT = [67754, 3441583108]
CODIGO_FALLBACK = "LEGACY-LARA"
NOMBRE_FALLBACK = "Legacy regional (histórico)"

COLUMNAS_H = ("menor_1_h", "de_1_4_h", "de_5_6_h", "de_7_9_h", "de_10_11_h", "de_12_14_h",
              "de_15_19_h", "de_20_24_h", "de_25_44_h", "de_45_59_h", "de_60_64_h", "de_65_h",
              "edad_ignorada_h")
COLUMNAS_M = tuple(c[:-1] + "m" for c in COLUMNAS_H)
SUMA_H = "+".join(f"f.{c}" for c in COLUMNAS_H)
SUMA_M = "+".join(f"f.{c}" for c in COLUMNAS_M)


class Command(BaseCommand):
    help = "Compara la transcripción legacy con los consolidados de SISV, por centro y evento."

    def add_arguments(self, parser):
        parser.add_argument("--desde", type=int, default=2009, help="Año mínimo (default 2009).")
        parser.add_argument("--anio", type=int, default=0, help="Limita a un solo año.")
        parser.add_argument("--ejecutar", action="store_true",
                            help="Escribe el resultado. Sin esta opción solo informa.")
        parser.add_argument("--csv", default="", help="Exporta el diff a un CSV (UTF-8 BOM).")
        parser.add_argument("--todo-pais", action="store_true",
                            help="Ignora el filtro Lara (solo depuración).")
        parser.add_argument("--limite", type=int, default=0,
                            help="Máximo de documentos leídos por año (pruebas).")

    def handle(self, *args, **opts):
        desde = opts["anio"] or opts["desde"]
        self.stdout.write(
            f"Conciliando SIS-04/EPI-12 desde {desde}"
            + (f" — solo {opts['anio']}" if opts["anio"] else "")
        )
        catalogo, nombres = self._catalogo_legacy()
        mapa_evento = por_evento_id(dict(EventoENO.objects.values_list("codigo_evento", "id")))
        org_por_nombre = self._organizaciones()
        fallback_id = self._fallback_id()
        self.stdout.write(
            f"Eventos ENO mapeados: {len(mapa_evento)} · organizaciones activas: "
            f"{len(org_por_nombre)} · fallback #{fallback_id}"
        )
        area = self._area(opts["todo_pais"])
        if area is None and not opts["todo_pais"]:
            self.stderr.write("El árbol Lara no arrojó establecimientos: no se puede conciliar.")
            return

        anios = [opts["anio"]] if opts["anio"] else self._anios(desde)
        transcriptores = self._transcriptores()
        for anio in anios:
            self._anio(anio, area, mapa_evento, org_por_nombre, fallback_id, catalogo,
                       nombres, transcriptores, opts)
        if opts["csv"]:
            self._csv(opts["csv"], desde, opts["anio"])

    # ------------------------------------------------------------------  catálogos
    def _catalogo_legacy(self):
        with connection.cursor() as cur:
            cur.execute('SELECT "ID"::bigint, "CODIGO", "NOMBRE" FROM sismai."CODIFICADOR";')
            catalogo = {int(a): (b or "", c or "") for a, b, c in cur.fetchall()}
            cur.execute('SELECT "ID"::bigint, "NOMBRE" FROM sismai."ESTABLECIMIENTO";')
            nombres = {int(a): (b or "").strip() for a, b in cur.fetchall()}
        return catalogo, nombres

    def _organizaciones(self):
        mapa = {}
        for nombre, org_id in Organizacion.objects.filter(activo=True).values_list("nombre", "id"):
            mapa[normalizar_centro(nombre)] = org_id
        return mapa

    def _fallback_id(self):
        org = Organizacion.objects.filter(codigo=CODIGO_FALLBACK).first()
        return org.id if org else None

    def _area(self, todo_pais):
        if todo_pais:
            return None
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

    def _anios(self, desde):
        with connection.cursor() as cur:
            cur.execute('SELECT DISTINCT "ANNO"::int FROM sismai."DOCUMENTO"'
                        ' WHERE "ANNO" >= %s ORDER BY 1;', [desde])
            return [a for (a,) in cur.fetchall() if a]

    # ------------------------------------------------------------------  lectura
    def _transcriptores(self):
        """{documento: instancia} desde `HISTDOC`, para atribuir quién transcribió.

        `HISTDOC` sólo registra la creación del documento (su `EVENTO` siempre es
        'Creado'), no cada edición, y empieza en agosto de 2019: antes de esa fecha
        no hay rastro y la atribución queda vacía a propósito, no inventada. La
        columna `USUARIO` está vacía en todo el histórico, así que `INSTANCIA` es
        el nombre de la estación de trabajo, no una cuenta verificada de persona.
        """
        with connection.cursor() as cur:
            cur.execute('SELECT "DOCUMENTO"::bigint, "INSTANCIA" FROM sismai."HISTDOC"')
            return {int(a): (b or "").strip() for a, b in cur.fetchall()}

    def _crudo(self, anio, area, limite, transcriptores):
        """[(establecimiento, semana, enfermedad, casos_h, casos_m, muertes_h, muertes_m,
             documento, instancia)]"""
        sql = """
            SELECT d."HORIGEN"::bigint, d."PERIODO"::int, r."ENFERMEDAD"::bigint,
                   sum(COALESCE(r."CASOSHOM",0)), sum(COALESCE(r."CASOSMUJ",0)),
                   sum(COALESCE(r."MUERTESHOM",0)), sum(COALESCE(r."MUERTESMUJ",0)),
                   min(d."ID"::bigint)
            FROM sismai."RENGLONTELE" r
            JOIN sismai."DOCUMENTO" d ON d."ID" = r."DOCUMENTO"
            WHERE d."TIPO" = 1 AND d."ANNO" = %s
        """
        params = [anio]
        if area is not None:
            sql += ' AND d."HORIGEN" = ANY(%s)'
            params.append(sorted(area))
        if limite:
            sql += (' AND d."ID" IN (SELECT "ID" FROM sismai."DOCUMENTO"'
                    ' WHERE "TIPO"=1 AND "ANNO"=%s LIMIT %s)')
            params += [anio, limite]
        sql += " GROUP BY 1,2,3"
        with connection.cursor() as cur:
            cur.execute(sql, params)
            return [(a, b, c, int(h or 0), int(m or 0), int(mh or 0), int(mm or 0),
                     int(doc), transcriptores.get(int(doc), ""))
                    for a, b, c, h, m, mh, mm, doc in cur.fetchall()]

    def _sisv(self, anio):
        """{(organizacion, semana, tipo, evento_id): (hombres, mujeres)}"""
        sql = f"""
            SELECT c.organizacion_id, c.semana, c.tipo, f.evento_id, sum({SUMA_H}), sum({SUMA_M})
            FROM vigilancia_consolidadosemanal c
            JOIN vigilancia_filaconsolidado f ON f.consolidado_id = c.id
            WHERE c.anio = %s AND c.legacy_tabla = 'RENGLONTELE'
            GROUP BY 1,2,3,4
        """
        with connection.cursor() as cur:
            cur.execute(sql, [anio])
            return {(o, s, t, e): (int(h or 0), int(m or 0)) for o, s, t, e, h, m in cur.fetchall()}

    # ------------------------------------------------------------------  conciliación
    def _anio(self, anio, area, mapa_evento, org_por_nombre, fallback_id,
              catalogo, nombres, transcriptores, opts):
        crudo = self._crudo(anio, area, opts["limite"], transcriptores)
        sisv = self._sisv(anio)

        org_de_establecimiento = {}
        for est_id, _sem, _enf, *_ in crudo:
            if est_id not in org_de_establecimiento:
                org_de_establecimiento[est_id] = org_por_nombre.get(
                    normalizar_centro(nombres.get(est_id, "")))
        legacy_por_org = defaultdict(set)
        for est_id, org_id in org_de_establecimiento.items():
            legacy_por_org[org_id if org_id is not None else fallback_id].add(est_id)

        agregado = {}
        por_establecimiento = defaultdict(lambda: defaultdict(lambda: [0, 0]))
        atribucion = {}
        for est_id, semana, enf, ch, cm, mh, mm, doc, instancia in crudo:
            if not (ch or cm or mh or mm) or not semana or not (1 <= semana <= 53):
                continue
            org_real = org_de_establecimiento[est_id]
            org_id = org_real if org_real is not None else fallback_id
            if org_id is None:
                continue
            evento_id = mapa_evento.get(int(enf))
            #clave positiva si hay equivalente ENO, negativa si no lo hay
            clave_ev = evento_id if evento_id is not None else -int(enf)
            for tipo, h, m in (("MORBILIDAD", ch, cm), ("MORTALIDAD", mh, mm)):
                if not (h or m):
                    continue
                clave = (org_id, semana, tipo, clave_ev)
                celda = agregado.get(clave)
                if celda is None:
                    codigo, nombre_enf = catalogo.get(int(enf), ("", ""))
                    celda = agregado[clave] = {
                        "evento_id": evento_id, "enf": int(enf), "codigo": codigo,
                        "nombre": nombre_enf, "sin_org": org_real is None, "h": 0, "m": 0,
                    }
                celda["h"] += int(h or 0)
                celda["m"] += int(m or 0)
                por_establecimiento[clave][est_id][0] += int(h or 0)
                por_establecimiento[clave][est_id][1] += int(m or 0)
                # un DOCUMENTO es único por centro+semana+tipo: la estación es de esa fila
                atribucion[(org_id, semana, tipo, est_id)] = (doc, instancia)

        for (org_id, semana, tipo, evento_id), (h, m) in sisv.items():
            clave = (org_id, semana, tipo, evento_id)
            if clave not in agregado:
                agregado[clave] = {"evento_id": evento_id, "enf": None, "codigo": "",
                                   "nombre": "(solo en SISV)", "sin_org": False, "h": 0, "m": 0}

        registros, detalles = [], []
        for (org_id, semana, tipo, clave_ev), celda in agregado.items():
            evento_id = celda["evento_id"]
            sisv_h, sisv_m = sisv.get((org_id, semana, tipo, evento_id), (0, 0)) \
                if evento_id is not None else (0, 0)
            dif_h = celda["h"] - sisv_h
            dif_m = celda["m"] - sisv_m
            pseudo = es_pseudo_total(celda["nombre"])
            estado, resolucion = clasificar(
                celda["h"], celda["m"], sisv_h, sisv_m,
                celda["sin_org"], evento_id is not None, pseudo)
            colision = len(legacy_por_org.get(org_id, set())) > 1
            obj = ConciliacionENO(
                anio=anio, semana=semana, tipo=tipo, organizacion_id=org_id, evento_id=evento_id,
                legado_enfermedad_id=celda["enf"] if celda["enf"] is not None else 0,
                legado_enfermedad_codigo=celda["codigo"] or "",
                legado_enfermedad_nombre=celda["nombre"] or "",
                es_pseudo_total=pseudo, cantidad_centros=len(por_establecimiento.get(
                    (org_id, semana, tipo, clave_ev), {})) or 1, colision=colision,
                crudo_h=celda["h"], crudo_m=celda["m"], sisv_h=sisv_h, sisv_m=sisv_m,
                diferencia_h=dif_h, diferencia_m=dif_m, estado=estado, resolucion=resolucion,
            )
            registros.append(obj)
            por_est = por_establecimiento.get((org_id, semana, tipo, clave_ev), {})
            if por_est:
                for est_id, (h, m) in por_est.items():
                    doc, instancia = atribucion.get((org_id, semana, tipo, est_id), (None, ""))
                    detalles.append(ConciliacionENOCentro(
                        conciliacion=obj, legado_establecimiento_id=est_id,
                        legado_establecimiento_nombre=nombres.get(est_id, "")[:200],
                        legado_documento=doc, transcrito_por=instancia[:30],
                        crudo_h=h, crudo_m=m,
                        sisv_h=None if colision else sisv_h,
                        sisv_m=None if colision else sisv_m, colision=colision))
            else:
                detalles.append(ConciliacionENOCentro(
                    conciliacion=obj, legado_establecimiento_id=0,
                    legado_establecimiento_nombre="(sin fuente en el crudo)",
                    crudo_h=0, crudo_m=0, sisv_h=sisv_h, sisv_m=sisv_m, colision=colision))

        sin_org = sum(1 for r in registros if r.resolucion == "CENTRO_SIN_ORG")
        real_perdida = sum(r.diferencia_h + r.diferencia_m for r in registros
                           if r.estado in ("DIFERENCIA", "SOLO_CRUDO"))
        self.stdout.write(
            f"{anio}: filas={len(registros):,} centros={len(org_de_establecimiento):,} "
            f"cuadran={sum(1 for r in registros if r.estado == 'CUADRA'):,} "
            f"diferencia={sum(1 for r in registros if r.estado == 'DIFERENCIA'):,} "
            f"solo_crudo={sum(1 for r in registros if r.estado == 'SOLO_CRUDO'):,} "
            f"excluidos={sum(1 for r in registros if r.estado == 'EXCLUIDO_EN_ETL'):,} "
            f"sin_org={sin_org:,} casos_no_conciliados={real_perdida:,}"
        )
        if opts["ejecutar"]:
            self._escribir(anio, registros, detalles)

    def _escribir(self, anio, registros, detalles):
        with transaction.atomic():
            ConciliacionENOCentro.objects.filter(conciliacion__anio=anio).delete()
            ConciliacionENO.objects.filter(anio=anio).delete()
            for i in range(0, len(registros), 2000):
                ConciliacionENO.objects.bulk_create(registros[i:i + 2000], batch_size=2000)
            for i in range(0, len(detalles), 2000):
                ConciliacionENOCentro.objects.bulk_create(detalles[i:i + 2000], batch_size=2000)
        self.stdout.write(self.style.SUCCESS(f"{anio}: escritura hecha "
                                             f"({len(registros):,} filas, {len(detalles):,} centros)"))

    def _csv(self, ruta, desde=0, anio=0):
        """Exporta la conciliación **respetando los filtros del comando**.

        Exportar la tabla entera bajo un nombre de año concreto sería peor que no
        exportar: el acta leería como 2026 cifras de 2009.
        """
        if anio:
            filas = ConciliacionENO.objects.filter(anio=anio)
        else:
            filas = ConciliacionENO.objects.filter(anio__gte=desde)
        campos = ["anio", "semana", "tipo", "organizacion", "evento", "codigo_legacy",
                  "enfermedad_legacy", "pseudo_total", "centros", "colision", "crudo_h",
                  "crudo_m", "sisv_h", "sisv_m", "diferencia_h", "diferencia_m", "estado",
                  "resolucion"]
        total = 0
        with open(ruta, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh, delimiter=";")
            w.writerow(campos)
            for r in filas.select_related("organizacion", "evento").iterator():
                w.writerow([r.anio, r.semana, r.tipo, r.organizacion.nombre,
                            r.evento.nombre if r.evento else "", r.legado_enfermedad_codigo,
                            r.legado_enfermedad_nombre, "si" if r.es_pseudo_total else "no",
                            r.cantidad_centros, "si" if r.colision else "no",
                            r.crudo_h, r.crudo_m, r.sisv_h, r.sisv_m,
                            r.diferencia_h, r.diferencia_m, r.estado, r.resolucion])
                total += 1
        self.stdout.write(self.style.SUCCESS(f"CSV: {ruta} ({total:,} filas)"))
        self._csv_centros(f"{os.path.splitext(ruta)[0]}_centros.csv", desde, anio)

    def _csv_centros(self, ruta, desde=0, anio=0):
        """Detalle por centro: incluye la estación que transcribió cada hoja."""
        if anio:
            centros = ConciliacionENOCentro.objects.filter(conciliacion__anio=anio)
        else:
            centros = ConciliacionENOCentro.objects.filter(conciliacion__anio__gte=desde)
        campos = ["anio", "semana", "tipo", "organizacion", "evento", "enfermedad_legacy",
                  "codigo_legacy", "estado", "resolucion", "establecimiento_id",
                  "establecimiento", "documento", "transcrito_por", "crudo_h", "crudo_m",
                  "sisv_h", "sisv_m", "colision"]
        total = 0
        with open(ruta, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh, delimiter=";")
            w.writerow(campos)
            for d in centros.select_related("conciliacion", "conciliacion__organizacion",
                                            "conciliacion__evento").iterator():
                c = d.conciliacion
                w.writerow([c.anio, c.semana, c.tipo, c.organizacion.nombre,
                            c.evento.nombre if c.evento else "", c.legado_enfermedad_nombre,
                            c.legado_enfermedad_codigo, c.estado, c.resolucion,
                            d.legado_establecimiento_id, d.legado_establecimiento_nombre,
                            d.legado_documento or "", d.transcrito_por,
                            d.crudo_h, d.crudo_m,
                            "" if d.sisv_h is None else d.sisv_h,
                            "" if d.sisv_m is None else d.sisv_m,
                            "si" if d.colision else "no"])
                total += 1
        self.stdout.write(self.style.SUCCESS(f"CSV centros: {ruta} ({total:,} filas)"))
