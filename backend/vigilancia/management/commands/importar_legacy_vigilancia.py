"""ETL de la vigilancia legacy (espejo sismai.*) hacia los modelos de 'vigilancia'
y 'registros'. Alcance establecido el 23/09/2026: solo el árbol de establecimientos
de Lara (raíces DES LARA=67754 y DPS LARA=3441583108).

Qué importa y hacia dónde:
  - sismai.RENGLONTELE  (SIS-04/EPI-12 semanal, casos y muertes 13×2)
      → vigilancia.ConsolidadoSemanal tipo MORBILIDAD y MORTALIDAD
        con sus FilaConsolidado (matriz de 13 grupos etarios × 2 sexos).
  - sismai.RENGLON_EPI15 (SIS-04/EPI-15 semanal) → nuevo vigilancia.ConsolidadoEpi15
        + FilaEpi15 (sin matriz de edad; desglose en el nombre del evento).
  - sismai.CASOS_MMI / M_VIOLENTA (casos individuales) → registros.FichaVigilancia
        con lote LEGACY-MMI / LEGACY-VIOLENTA.

Las enfermedades legacy se cruzan con el catálogo EventoENO vía el mapeo curado
de vigilancia/legacy_mapeo.py; lo no mapeado se reporta como "no importado".

Idempotencia: crea (o reusa) los ConsolidadoSemanal por (org, anio, semana, tipo),
las filas se acumulan dentro de cada consolidado y se insertan en bulks.
"""

import re
import unicodedata
from datetime import date

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from registros.models import FichaVigilancia
from vigilancia.legacy_mapeo import (
    GRUPO_EDAD_LEGACY,
    LEGACY_ENFERMEDAD_NOMBRE,
    por_evento_id,
)
from vigilancia.models import (
    ConsolidadoEpi15,
    ConsolidadoSemanal,
    EventoENO,
    FilaConsolidado,
    FilaEpi15,
    columna,
)

LOTE_MMI = "LEGACY-MMI"
LOTE_VIOLENTA = "LEGACY-VIOLENTA"

LARA_ROOT = [67754, 3441583108]

SEXO_MMI = {1: "M", 2: "F", 0: "I", 3: "I"}
SEXO_CERTIFICADO = {1: "F", 2: "M", 0: "I", 3: "I"}

UNIDAD_EDAD = {"D": "Días", "M": "Meses", "A": "Años"}


def normalizar(texto):
    """Clave de unión: sin paréntesis, minúsculas, sin tildes, espacios colapsados."""
    sin_parentesis = re.sub(r"\([^)]*\)", "", texto or "")
    sin_acentos = unicodedata.normalize("NFD", sin_parentesis)
    sin_acentos = "".join(c for c in sin_acentos if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", (sin_acentos or "").lower()).strip()


def como_entero(v):
    if v is None:
        return None
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return None


class Command(BaseCommand):
    help = "ETL de la vigilancia legacy (sismai.*) hacia ConsolidadoSemanal, EPI-15 y FichaVigilancia."

    def add_arguments(self, parser):
        parser.add_argument(
            "--modelo",
            choices=["todos", "epi12", "epi15", "mmi", "violenta"],
            default="todos",
        )
        parser.add_argument("--borrar", action="store_true", help="Borra los lotes LEGACY-* antes de cargar.")
        parser.add_argument("--limite", type=int, default=0, help="Procesa solo N filas (pruebas).")
        parser.add_argument("--desde", type=int, default=2000, help="Año mínimo de los documentos.")
        parser.add_argument("--todo-pais", action="store_true", help="Ignora el filtro Lara (solo depuración).")

    def handle(self, *args, **opts):
        self.desde = opts["desde"]
        self.todo_pais = opts["todo_pais"]
        self.no_importados = {}  # legacy_id -> nombre
        self.sin_edad = 0
        self._cargar_lookups()
        if opts["borrar"]:
            self._borrar()
        if opts["modelo"] in ("todos", "epi12"):
            self._epi12(opts["limite"])
        if opts["modelo"] in ("todos", "epi15"):
            self._epi15(opts["limite"])
        if opts["modelo"] in ("todos", "mmi"):
            self._mmi(opts["limite"])
        if opts["modelo"] in ("todos", "violenta"):
            self._violenta(opts["limite"])
        if self.no_importados:
            self.stdout.write(
                "Enfermedades legacy sin equivalente ENO (no importadas):\n  "
                + "\n  ".join(f"[{k}] {n}" for k, n in sorted(self.no_importados.items()))
            )

    # ------------------------------------------------------------------
    # Catálogos y árboles de apoyo
    # ------------------------------------------------------------------
    def _cargar_lookups(self):
        from seguridad.models import Organizacion

        self.evento_por_codigo = dict(EventoENO.objects.values_list("codigo_evento", "id"))
        self.evento_por_legacy = por_evento_id(self.evento_por_codigo)
        self.org_por_nombre = {
            normalizar(nombre): org_id
            for nombre, org_id in Organizacion.objects.filter(activo=True).values_list("nombre", "id")
        }
        self._fallback_org_id = None
        with connection.cursor() as cur:
            cur.execute('SELECT "ID", "NOMBRE" FROM sismai."ESTABLECIMIENTO";')
            self.establecimientos = {float(i): (n or "").strip() for i, n in cur.fetchall()}
            cur.execute('SELECT "NUM_REGION", "NOMBRELARGO" FROM sismai."ORG_GEOGRAFICA";')
            re_geo = re.compile(
                r"Estado\s+([^,]+),\s*Municipio\s+([^,]+),\s*Parroquia\s+([^,]+)", re.I
            )

            def parse_geo(largo):
                m = re_geo.search(largo or "")
                return (m.group(1).strip().title(), m.group(2).strip().title(), m.group(3).strip().title()) if m else ("", "", "")

            self.geo = {float(n): parse_geo(v) for n, v in cur.fetchall()}
        if not self.todo_pais:
            self.lara = self._lara_ids()
            self.stdout.write(f"Árbol Lara: {len(self.lara)} establecimientos")
        self.stdout.write(
            f"Eventos ENO: {len(self.evento_por_codigo)} · mapeo legacy→ENO: {len(self.evento_por_legacy)}"
        )

    def _lara_ids(self):
        with connection.cursor() as cur:
            ids = set()
            for root in LARA_ROOT:
                cur.execute(
                    """
                    WITH RECURSIVE t AS (
                        SELECT %s::double precision AS id
                        UNION ALL
                        SELECT e."ID" FROM sismai."ESTABLECIMIENTO" e
                        JOIN t ON e."PADRE" = t.id
                    )
                    SELECT id FROM t;
                    """,
                    [root],
                )
                ids.update(float(fila[0]) for fila in cur.fetchall())
        return ids

    def _borrar(self):
        c = ConsolidadoSemanal.objects.filter(legacy_tabla="RENGLONTELE").delete()[0]
        e = ConsolidadoEpi15.objects.filter(legacy_tabla="RENGLON_EPI15").delete()[0]
        m = FichaVigilancia.objects.filter(lote_id=LOTE_MMI).delete()[0]
        v = FichaVigilancia.objects.filter(lote_id=LOTE_VIOLENTA).delete()[0]
        self.stdout.write(f"Borrados lotes previos: EPI-12={c} EPI-15={e} MMI={m} violenta={v}")

    # ------------------------------------------------------------------
    # Organizaciones destino
    # ------------------------------------------------------------------
    def _org_id(self, establecimiento_id):
        """Org destino según el nombre del establecimiento legacy; si no existe se
        consolida en la organización regional 'Legacy regional (histórico)'."""
        nombre = self.establecimientos.get(float(establecimiento_id), "")
        return self.org_por_nombre.get(normalizar(nombre)) if nombre else None

    def _org_id_o_fallback(self, establecimiento_id):
        return self._org_id(establecimiento_id) or self._fallback_org()

    def _fallback_org(self):
        if self._fallback_org_id is None:
            from seguridad.models import Organizacion

            obj, _ = Organizacion.objects.get_or_create(
                codigo="LEGACY-LARA",
                defaults={
                    "nombre": "Legacy regional (histórico)",
                    "nivel": "REGIONAL",
                    "estado": "Lara",
                },
            )
            self._fallback_org_id = obj.id
        return self._fallback_org_id

    def _mapear_evento(self, legacy_id):
        """Devuelve id de EventoENO o None (reportando el evento no mapeado)."""
        if legacy_id is None:
            return None
        key = int(float(legacy_id))
        evento_id = self.evento_por_legacy.get(key)
        if evento_id is None and key not in self.no_importados:
            self.no_importados[key] = LEGACY_ENFERMEDAD_NOMBRE.get(key, f"código legacy {key}")
        return evento_id

    # ------------------------------------------------------------------
    # SIS-04/EPI-12 → ConsolidadoSemanal
    # ------------------------------------------------------------------
    def _sql_epi12(self, limite):
        filtro_doc = 'd."TIPO" = 1 AND d."ANNO" >= %(desde)s'
        parametros = {"desde": self.desde}
        if not self.todo_pais:
            filtro_doc += ' AND d."HORIGEN" = ANY(%(lara)s)'
            parametros["lara"] = list(self.lara)
        sql = f"""
            SELECT d."ID", d."HORIGEN", d."ANNO", d."PERIODO",
                   r."ENFERMEDAD", r."EDAD",
                   COALESCE(SUM(r."CASOSHOM"),0), COALESCE(SUM(r."CASOSMUJ"),0),
                   COALESCE(SUM(r."MUERTESHOM"),0), COALESCE(SUM(r."MUERTESMUJ"),0)
            FROM sismai."RENGLONTELE" r
            JOIN sismai."DOCUMENTO" d ON d."ID" = r."DOCUMENTO"
            WHERE {filtro_doc}
            GROUP BY d."ID", d."HORIGEN", d."ANNO", d."PERIODO", r."ENFERMEDAD", r."EDAD"
            ORDER BY d."ID"
        """
        if limite:
            sql += f" LIMIT {int(limite)}"
        return sql, parametros

    def _epi12(self, limite):
        sql, parametros = self._sql_epi12(limite)
        claves = self._claves_consolidado(sql, parametros)
        mapa = self._crear_consolidados_semanal("RENGLONTELE", claves)
        creadas = self._filas_epi12(sql, parametros, mapa)
        total = ConsolidadoSemanal.objects.filter(legacy_tabla="RENGLONTELE").count()
        self.stdout.write(
            self.style.SUCCESS(f"EPI-12: consolidados={total} filas_creadas={creadas}")
        )

    def _claves_consolidado(self, sql, parametros):
        """Re-lee la consulta agregada y extrae las claves (org, anio, semana, tipo)."""
        claves = set()
        with connection.cursor() as cur:
            cur.execute(sql, parametros)
            while True:
                filas = cur.fetchmany(2000)
                if not filas:
                    break
                for _, horigen, anno, periodo, _, _, ch, cm, mh, mm in filas:
                    semana = como_entero(periodo)
                    if not anno or int(anno) < self.desde or not semana or not (1 <= semana <= 53):
                        continue
                    org = self._org_id_o_fallback(horigen)
                    if ch or cm:
                        claves.add((org, int(anno), semana, "MORBILIDAD"))
                    if mh or mm:
                        claves.add((org, int(anno), semana, "MORTALIDAD"))
        return claves

    def _crear_consolidados_semanal(self, tabla, claves):
        existentes = set(
            ConsolidadoSemanal.objects.filter(
                organizacion_id__in={k[0] for k in claves},
                anio__in={k[1] for k in claves},
                legacy_tabla=tabla,
            ).values_list("organizacion_id", "anio", "semana", "tipo")
        )
        faltantes = sorted(claves - existentes)
        mapa = {}
        for i in range(0, len(faltantes), 3000):
            lote = [
                ConsolidadoSemanal(
                    organizacion_id=org, anio=anno, semana=semana, tipo=tipo,
                    estado="CERRADO", origen="PROPIO", legacy_tabla=tabla,
                )
                for org, anno, semana, tipo in faltantes[i : i + 3000]
            ]
            if not lote:
                continue
            with transaction.atomic():
                creados = ConsolidadoSemanal.objects.bulk_create(lote, batch_size=1000)
            for obj in creados:
                mapa[(obj.organizacion_id, obj.anio, obj.semana, obj.tipo)] = obj.id
        self.stdout.write(f"{tabla}: consolidados creados={len(faltantes)}")
        return mapa

    def _filas_epi12(self, sql, parametros, mapa):
        acum = {}  # (consolidado_id, evento) -> {columna: valor}

        with connection.cursor() as cur:
            cur.arraysize = 2000
            cur.execute(sql, parametros)
            while True:
                filas = cur.fetchmany(cur.arraysize)
                if not filas:
                    break
                for doc_id, horigen, anno, periodo, enfermedad, edad, ch, cm, mh, mm in filas:
                    semana = como_entero(periodo)
                    if not anno or int(anno) < self.desde or not semana or not (1 <= semana <= 53):
                        continue
                    org = self._org_id_o_fallback(horigen)
                    if ch or cm:
                        cid = mapa.get((org, int(anno), semana, "MORBILIDAD"))
                        if cid is not None:
                            self._acum_fila(acum, cid, enfermedad, edad, "h", "m", ch, cm)
                    if mh or mm:
                        cid = mapa.get((org, int(anno), semana, "MORTALIDAD"))
                        if cid is not None:
                            self._acum_fila(acum, cid, enfermedad, edad, "h", "m", mh, mm)

        lote = [FilaConsolidado(consolidado_id=c, evento_id=e, **v) for (c, e), v in acum.items()]
        creadas = len(lote)
        for i in range(0, len(lote), 2000):
            with transaction.atomic():
                FilaConsolidado.objects.bulk_create(lote[i : i + 2000], batch_size=2000)
        return creadas

    def _acum_fila(self, acum, consolidado_id, enfermedad, edad, sexo_h, sexo_m, vh, vm):
        """Acumula un conteo por (consolidado, evento, grupo/sexo) dentro de la matriz."""
        evento = self._mapear_evento(enfermedad)
        if evento is None:
            return
        grupo = GRUPO_EDAD_LEGACY.get(como_entero(edad))
        if grupo is None:
            self.sin_edad += 1
            return
        v = acum.setdefault((consolidado_id, evento), {})
        if int(vh or 0):
            c = columna(grupo, sexo_h)
            v[c] = v.get(c, 0) + int(vh)
        if int(vm or 0):
            c = columna(grupo, sexo_m)
            v[c] = v.get(c, 0) + int(vm)

    # ------------------------------------------------------------------
    # SIS-04/EPI-15 → ConsolidadoEpi15
    # ------------------------------------------------------------------
    def _sql_epi15(self, limite):
        filtro_doc = 'd."TIPO" = 2 AND d."ANNO" >= %(desde)s'
        parametros = {"desde": self.desde}
        if not self.todo_pais:
            filtro_doc += ' AND d."HORIGEN" = ANY(%(lara)s)'
            parametros["lara"] = list(self.lara)
        sql = f"""
            SELECT d."ID", d."HORIGEN", d."ANNO", d."PERIODO",
                   r."ENFERMEDAD", r."CASOSP", r."CASOSS", r."CASOSX"
            FROM sismai."RENGLON_EPI15" r
            JOIN sismai."DOCUMENTO" d ON d."ID" = r."DOCUMENTO"
            WHERE {filtro_doc}
            ORDER BY d."ID"
        """
        if limite:
            sql += f" LIMIT {int(limite)}"
        return sql, parametros

    def _epi15(self, limite):
        sql, parametros = self._sql_epi15(limite)
        mapa = self._crear_epi15(sql, parametros)
        if mapa:
            con_ids = set(mapa.values())
            ya_filadas = set(
                FilaEpi15.objects.filter(consolidado_id__in=con_ids)
                .values_list("consolidado_id", flat=True)
                .distinct()
            )
            mapa = {k: v for k, v in mapa.items() if v not in ya_filadas}
        creadas = self._filas_epi15(sql, parametros, mapa)
        total = ConsolidadoEpi15.objects.filter(legacy_tabla="RENGLON_EPI15").count()
        self.stdout.write(
            self.style.SUCCESS(f"EPI-15: consolidados={total} filas_creadas={creadas}")
        )

    def _claves_epi15(self, sql, parametros):
        claves = set()
        with connection.cursor() as cur:
            cur.execute(sql, parametros)
            while True:
                filas = cur.fetchmany(2000)
                if not filas:
                    break
                for _, horigen, anno, periodo, _, cp, cs, cx in filas:
                    semana = como_entero(periodo)
                    if not anno or int(anno) < self.desde or not semana or not (1 <= semana <= 53):
                        continue
                    if cp or cs or cx:
                        claves.add((self._org_id_o_fallback(horigen), int(anno), semana))
        return claves

    def _crear_epi15(self, sql, parametros):
        claves = self._claves_epi15(sql, parametros)
        existentes = set(
            ConsolidadoEpi15.objects.filter(
                organizacion_id__in={k[0] for k in claves},
                anio__in={k[1] for k in claves},
                legacy_tabla="RENGLON_EPI15",
            ).values_list("organizacion_id", "anio", "semana")
        )
        faltantes = sorted(claves - existentes)
        mapa = {}
        for i in range(0, len(faltantes), 3000):
            lote = [
                ConsolidadoEpi15(
                    organizacion_id=org, anio=anno, semana=semana,
                    estado="CERRADO", origen="PROPIO", legacy_tabla="RENGLON_EPI15",
                )
                for org, anno, semana in faltantes[i : i + 3000]
            ]
            if not lote:
                continue
            with transaction.atomic():
                creados = ConsolidadoEpi15.objects.bulk_create(lote, batch_size=1000)
            for obj in creados:
                mapa[(obj.organizacion_id, obj.anio, obj.semana)] = obj.id
        self.stdout.write(f"RENGLON_EPI15: consolidados creados={len(faltantes)}")
        return mapa

    def _filas_epi15(self, sql, parametros, mapa):
        acum = {}  # (consolidado_id, legacy_id) -> (evento_id, cp, cs, cx)

        with connection.cursor() as cur:
            cur.arraysize = 2000
            cur.execute(sql, parametros)
            while True:
                filas = cur.fetchmany(cur.arraysize)
                if not filas:
                    break
                for doc_id, horigen, anno, periodo, enfermedad, cp, cs, cx in filas:
                    semana = como_entero(periodo)
                    if not anno or int(anno) < self.desde or not semana or not (1 <= semana <= 53):
                        continue
                    cons_id = mapa.get((self._org_id_o_fallback(horigen), int(anno), semana))
                    if cons_id is None:
                        continue
                    leg = como_entero(enfermedad)
                    if leg is None:
                        continue
                    evento = self._mapear_evento(leg)
                    cp = int(cp or 0)
                    cs = int(cs or 0)
                    cx = int(cx or 0)
                    if (cons_id, leg) in acum:
                        _, ap, aq, ax = acum[(cons_id, leg)]
                        acum[(cons_id, leg)] = (evento, ap + cp, aq + cs, ax + cx)
                    else:
                        acum[(cons_id, leg)] = (evento, cp, cs, cx)

        lote = []
        creadas = 0
        for (cons_id, leg), (evento, cp, cs, cx) in acum.items():
            lote.append(
                FilaEpi15(
                    consolidado_id=cons_id,
                    legacy_id=leg,
                    codigo_legacy="",
                    nombre_legacy=LEGACY_ENFERMEDAD_NOMBRE.get(leg, ""),
                    evento_id=evento,
                    casosp=cp,
                    casoss=cs,
                    casosx=cx,
                )
            )
            if len(lote) >= 2000:
                with transaction.atomic():
                    FilaEpi15.objects.bulk_create(lote, batch_size=2000)
                creadas += len(lote)
                lote = []
        if lote:
            with transaction.atomic():
                FilaEpi15.objects.bulk_create(lote, batch_size=2000)
            creadas += len(lote)
        return creadas

    # ------------------------------------------------------------------
    # CASOS_MMI → FichaVigilancia
    # ------------------------------------------------------------------
    def _mmi(self, limite):
        sql = """
            SELECT c."ID", c."NOMBRE", c."APELLIDO", c."EDAD", c."UNIDAD_EDAD", c."HSEXO",
                   c."CEDULA", c."FECHAOCURRENCIA", c."FECHAOPERACION", c."NACIONALIDAD",
                   c."NUMEROMSDS", c."HRESIDENCIA", e."NOMBRE", c."USUARIO"
            FROM sismai."CASOS_MMI" c
            LEFT JOIN sismai."DOCUMENTO" d ON d."ID" = c."HDOCUMENTO"
            LEFT JOIN sismai."ESTABLECIMIENTO" e ON e."ID" = d."HORIGEN"
            ORDER BY c."ID"
        """
        if limite:
            sql += f" LIMIT {int(limite)}"
        creadas = self._cargar_fichas_masivas(sql, LOTE_MMI, "CASOS_MMI",
                                              lambda f: self._mmi_ficha(f))
        self.stdout.write(self.style.SUCCESS(f"MMI: fichas creadas={creadas}"))

    def _mmi_ficha(self, fila):
        (cid, nombre, apellido, edad, unidad, sexo, cedula, fec_ocurr, fec_op,
         nac, msds, hres, estable, usuario) = fila
        fecha = self._fecha(fec_ocurr) or self._fecha(fec_op)
        if not fecha:
            return None
        est, mun, parr = self.geo.get(float(hres) if hres is not None else -1, ("", "", ""))
        bits = []
        if edad is not None:
            bits.append(f"Edad: {int(edad)} {UNIDAD_EDAD.get(unidad, '')}".rstrip())
        if msds:
            bits.append(f"MSDS: {msds}")
        if usuario:
            bits.append(f"Usuario legacy: {usuario}")
        return FichaVigilancia(
            codigo_notificacion=f"LEG-MMI-{int(cid)}",
            lote_id=LOTE_MMI,
            legacy_tabla="CASOS_MMI",
            legacy_id=str(int(cid)),
            fecha_evento=fecha,
            fecha_notificacion=fecha,
            nombre_evento="Caso de mortalidad materno-infantil (legacy)",
            clasificacion="SOSPECHOSO",
            establecimiento=(estable or "").strip()[:200],
            estado=est,
            municipio=mun,
            parroquia=parr,
            paciente_nombres=(nombre or "SIN NOMBRE").strip()[:150],
            paciente_apellidos=(apellido or "").strip()[:150],
            paciente_cedula=(cedula or "").strip()[:20],
            sexo=SEXO_MMI.get(como_entero(sexo), "I") or "I",
            nota=" | ".join(bits)[:3000],
        )

    # ------------------------------------------------------------------
    # M_VIOLENTA → FichaVigilancia
    # ------------------------------------------------------------------
    def _violenta(self, limite):
        sql = """
            SELECT v."ID", v."FECHA_MV", v."HTIPO_M", t."NOMBRE", v."DESCRIPCIONSUCESO",
                   v."LOGIN", v."FECHAOPERACION", c."NOMBRE", c."APELLIDO", c."SEXO",
                   c."CEDULA", e."NOMBRE"
            FROM sismai."M_VIOLENTA" v
            LEFT JOIN sismai."TIPO_M" t ON t."ID" = v."HTIPO_M"
            LEFT JOIN sismai."CERTIFICADO" c ON c."ID" = v."HCERTIFICADO"
            LEFT JOIN sismai."ESTABLECIMIENTO" e ON e."ID" = c."HESTABLECIMIENTO_OCUR"
            ORDER BY v."ID"
        """
        if limite:
            sql += f" LIMIT {int(limite)}"
        creadas = self._cargar_fichas_masivas(sql, LOTE_VIOLENTA, "M_VIOLENTA",
                                              lambda f: self._violenta_ficha(f))
        self.stdout.write(self.style.SUCCESS(f"Violenta: fichas creadas={creadas}"))

    def _violenta_ficha(self, fila):
        (vid, fec_mv, _htp, tipo, descrip, login, fec_op,
         nombre, apellido, sexo, cedula, estable) = fila
        fecha = self._fecha(fec_mv) or self._fecha(fec_op)
        if not fecha:
            return None
        bits = [b for b in [descrip or "", login and f"Operador legacy: {login}" or ""] if b]
        return FichaVigilancia(
            codigo_notificacion=f"LEG-VIOL-{int(vid)}",
            lote_id=LOTE_VIOLENTA,
            legacy_tabla="M_VIOLENTA",
            legacy_id=str(int(vid)),
            fecha_evento=fecha,
            fecha_notificacion=fecha,
            nombre_evento=f"Muerte violenta — {tipo or 'sin clasificar'} (legacy)"[:200],
            clasificacion="SOSPECHOSO",
            establecimiento=(estable or "").strip()[:200],
            paciente_nombres=(nombre or "SIN NOMBRE").strip()[:150],
            paciente_apellidos=(apellido or "").strip()[:150],
            paciente_cedula=(cedula or "").strip()[:20],
            sexo=SEXO_CERTIFICADO.get(como_entero(sexo), "I") or "I",
            nota=" | ".join(bits)[:3000],
        )

    # ------------------------------------------------------------------
    # Helpers compartidos
    # ------------------------------------------------------------------
    def _fecha(self, valor):
        if not valor:
            return None
        fecha = valor.date() if hasattr(valor, "date") else valor
        if isinstance(fecha, str):
            from django.utils.dateparse import parse_date

            fecha = parse_date(fecha)
        return fecha if isinstance(fecha, date) and fecha >= date(1900, 1, 1) else None

    def _cargar_fichas_masivas(self, sql, lote, tabla, maker):
        total = 0
        buffer = []
        with connection.cursor() as cur:
            cur.execute(sql)
            while True:
                filas = cur.fetchmany(5000)
                if not filas:
                    break
                for fila in filas:
                    obj = maker(fila)
                    if obj is None:
                        continue
                    buffer.append(obj)
                    if len(buffer) >= 5000:
                        with transaction.atomic():
                            FichaVigilancia.objects.bulk_create(buffer, batch_size=2000)
                        total += len(buffer)
                        buffer = []
        if buffer:
            with transaction.atomic():
                FichaVigilancia.objects.bulk_create(buffer, batch_size=2000)
            total += len(buffer)
        return total