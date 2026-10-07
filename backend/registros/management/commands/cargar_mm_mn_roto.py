"""Carga los CSV de la fase 1 (PENDIENTES §17.17/§17.24) en los modelos de 'registros'.

Los baja `migracion/extraer_mm_mn_roto.sh` del Oracle 10g y este comando los mete en
PostgreSQL. Es el paso que faltaba: sin el, los CSV de la recuperacion se quedan en
disco y no llegan al tablero.

Decisiones que importan:

* **Idempotente** por `registro_numero` (`LEG-CERT-{id}` / `LEG-RN-{id}`). Se puede
  correr tantas veces como haga falta: si el registro ya existe se ACTUALIZA, no se
  duplica ni se borra.
* **No pisa trabajo humano.** Al re-procesar un registro que ya tiene CIE-10, CIE-11,
  sugerido o `codificacion_pendiente` revisados por el codificador, se conservan. La
  carga solo rellena lo que falta.
* **La organizacion se resuelve por nombre de establecimiento**, con el mismo
  criterio que `asignar_organizacion_legacy`: solo establecimientos del arbol Lara
  (raices DES Lara=67754 / DPS Lara=3441583108). Los de domicilio se quedan sin
  organizacion, que es lo correcto: se agrupan por estado de residencia.
* **El encabezado lo pone el propio SQL** (`SELECT 'ID;FECHA_M;...' FROM DUAL` como
  primera fila de cada CSV), asi que el orden de columnas NO esta escrito a mano aca.
  Si falta una columna que el cargador necesita, se dice cual y se aborta.
* **La causa cae al catalogo CIE-10 del legacy** cuando el certificado no tiene
  renglon en `CAUSA_M`. Ojo: en el espejo `CAUSA_M` no tiene NI UNA fila de 2026, por
  eso casi todas las defunciones de 2026 quedaron con `causa_directa` vacia.

Por defecto NO escribe nada (informa). Con `--ejecutar` aplica.

Ejecutar:
    manage.py cargar_mm_mn_roto --directorio salida_mm_mn_20260929_1330
    manage.py cargar_mm_mn_roto --directorio <dir> --ejecutar
    manage.py cargar_mm_mn_roto --directorio <dir> --ejecutar --limite 50
"""
import csv
import os
import re
import unicodedata
from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalogos.models import CIE10, MapeoCIE
from registros.models import Defuncion, Nacimiento
from registros.services import version_cie_por_fecha
from seguridad.models import Organizacion

LOTE_DEF = "LEGACY-CERTIFICADO"
LOTE_NAC = "LEGACY-CERTNACIMIENTO"

SEXO = {1: "F", 2: "M", 3: "I", 0: "I"}
# HPRIMERA/SEGUNDO... en la salida: 1 = AL MOMENTO DE LA MUERTE, 2 = ULTIMOS 12 MESES.
CODIGOS_MM = {1, 2}
FORMAPARTO = {1: "VAGINAL", 2: "CESAREA", 3: "INSTRUMENTAL", 4: "OTRO", 5: "OTRO"}
SITIO_PARTO = {1: "ESTABLECIMIENTO", 2: "ESTABLECIMIENTO", 5: "ESTABLECIMIENTO", 3: "DOMICILIO"}
ESTADO_CIVIL = {
    1: "SOLTERA", 2: "CASADA", 3: "DIVORCIADA", 4: "UNION_LIBRE",
    5: "DIVORCIADA", 6: "SOLTERA", 7: "VIUDA", 8: "SOLTERA",
}
RAICES_LARA = {"67754", "3441583108"}

GEO_RE = re.compile(r"Estado\s+([^,]+),\s*Municipio\s+([^,]+),\s*Parroquia\s*([^,]*)", re.I)


# --------------------------------------------------------------------------- #
# Utilidades de conversion (tolerantes: los CSV del legacy traen basura)          #
# --------------------------------------------------------------------------- #
def vacio(v):
    return (v or "").strip()


def como_entero(v):
    v = vacio(v)
    if not v:
        return None
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return None


def como_id(v):
    """Los ID del legacy vienen como '123' o '123.0'."""
    n = como_entero(v)
    return str(n) if n is not None else ""


def como_fecha(v):
    v = vacio(v)
    if not v:
        return None
    for patron in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(v, patron).date()
        except ValueError:
            continue
    try:
        return date.fromisoformat(v[:10])
    except ValueError:
        return None


def como_fecha_hora(v):
    v = vacio(v)
    if not v:
        return None
    for patron in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(v, patron)
        except ValueError:
            continue
    return None


def como_hora(v):
    """El legacy mezcla '08:30', '8:30 AM' y '08:30:00'."""
    v = vacio(v).upper().replace(".", "")
    if not v:
        return None
    m = re.search(r"(\d{1,2}):(\d{2})(?::(\d{2}))?\s*([AP]M)?", v)
    if not m:
        return None
    h, mi, se, ap = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0), m.group(4)
    if ap == "PM" and h < 12:
        h += 12
    elif ap == "AM" and h == 12:
        h = 0
    if h > 23 or mi > 59:
        return None
    return time(h, mi, se)


def como_decimal(v):
    v = vacio(v).replace(",", ".")
    if not v:
        return None
    try:
        return Decimal(v)
    except (InvalidOperation, ValueError):
        return None


def peso_valido(v):
    """El legacy suele guardar el peso en kg (1.84) y a veces en gramos (1840)."""
    g = como_entero(v)
    if g is None:
        return None
    if g < 20:
        g *= 1000
    return g if 200 <= g <= 8000 else None


def talla_valida(v):
    t = como_decimal(v)
    if t is None:
        return None
    t = t.quantize(Decimal("0.1"))
    return t if 20 <= t <= 100 else None


def rango(v, minimo, maximo):
    n = como_entero(v)
    return n if n is not None and minimo <= n <= maximo else None


def norm_cie10(codigo):
    codigo = vacio(codigo)
    codigo = codigo.replace("\u0086", "").replace("\u2020", "").replace("\u2021", "").replace("*", "")
    return re.sub(r"[^A-Za-z0-9.]", "", codigo).upper()


def normalizar(nombre):
    """Mismo criterio que asignar_organizacion_legacy, para que los nombres casen."""
    nombre = re.sub(r"\([^)]*\)", "", nombre or "")
    nombre = "".join(c for c in unicodedata.normalize("NFD", nombre) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", nombre.lower()).strip()


def parse_geo(texto):
    m = GEO_RE.search(texto or "")
    if not m:
        return "", "", ""
    est, mun, parr = [(x or "").strip() for x in m.groups()]
    return est.title(), mun.title(), parr.title()


class Command(BaseCommand):
    help = "Carga los CSV de la fase 1 (muerte materna/neonatal) desde el Oracle vivo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--directorio", required=True,
            help="Carpeta con los CSV que produjo extraer_mm_mn_roto.sh.",
        )
        parser.add_argument(
            "--ejecutar", action="store_true",
            help="Escribe en la base de datos (sin esto solo informa).",
        )
        parser.add_argument("--limite", type=int, default=0, help="Solo las primeras N (pruebas).")
        parser.add_argument(
            "--ignorar-causa", action="store_true",
            help="No carga la causa de defunción (ni desde CAUSA_M ni desde el catálogo CIE-10).",
        )
        parser.add_argument(
            "--permitir-arbol-completo", action="store_true",
            help="Si establecimiento.csv no trae las raíces Lara, usa TODOS los "
                 "establecimientos. Solo para diagnóstico: puede atribuir registros Lara "
                 "a centros de otros estados.",
        )

    # ---------------------------------------------------------------- helpers
    def leer(self, nombre, requeridas, es_datos=True):
        """Lee un CSV usando la PRIMERA fila como encabezado (la que pone el SQL).

        `es_datos=False` es para los catalogos (establecimientos, CIE-10 legacy,
        geografia): a esos NO se les aplica `--limite`, porque truncarlos dejaria la
        resolucion de organizaciones y de territorio incompleta sin avisar. Limitar los
        datos es util para una prueba rapida; limitar los catalogos solo produce
        resultados falsos.
        """
        ruta = os.path.join(self.directorio, nombre)
        if not os.path.isfile(ruta):
            return None
        with open(ruta, newline="", encoding="utf-8-sig", errors="replace") as fh:
            lector = csv.reader(fh, delimiter=";")
            try:
                encabezado = [c.strip().upper() for c in next(lector)]
            except StopIteration:
                return []
            faltantes = [c for c in requeridas if c not in encabezado]
            if faltantes:
                raise CommandError(
                    f"{nombre}: faltan columnas {faltantes}. El encabezado dice {encabezado}. "
                    "Se extrajo con un SQL distinto al de migracion/extraer_mm_mn_roto.sql."
                )
            filas = []
            for fila in lector:
                if not any(f.strip() for f in fila):
                    continue
                if len(fila) != len(encabezado):
                    continue  # fila cortada: mejor perderla que inventar el orden
                filas.append(dict(zip(encabezado, fila)))
                if es_datos and self.limite and len(filas) >= self.limite:
                    break
            return filas

    def arbol_lara(self, filas_establecimiento):
        """IDs del árbol Lara, walked desde las raíces DES/DPS, igual que el comando de asignación."""
        if not filas_establecimiento:
            return set(), {}
        padres = {}
        nombres = {}
        for f in filas_establecimiento:
            i = como_id(f.get("ID"))
            if not i:
                continue
            padres[i] = como_id(f.get("PADRE"))
            nombres[i] = vacio(f.get("NOMBRE"))
        arbol = set(RAICES_LARA) & set(padres)
        if not arbol:
            # Sin las raices NO se puede saber que establecimientos son de Lara. Adivinar
            # seria peor que no cargar: crearia organizaciones de todo el pais bajo la
            # Direccion Regional Lara y las defunciones de Lara quedarian atribuidas a
            # hospitales de otros estados. Se aborta y se pide reextraer el catalogo.
            raise CommandError(
                "establecimiento.csv no contiene ninguna raiz Lara "
                f"({', '.join(sorted(RAICES_LARA))}): el catalogo vino truncado o de otra "
                "extraccion, y sin el no se puede decidir que centros son de Lara. "
                "Reextraiga establishment.csv con migracion/extraer_mm_mn_roto.sh "
                "(son ~21.000 filas) y vuelva a correr. Para una prueba parcial use "
                "--permitir-arbol-completo solo si sabe lo que hace."
            )
        if self.permitir_arbol_completo and not getattr(self, "_avisado_arbol", False):
            self.stdout.write(self.style.WARNING(
                "AVISO: se esta usando la lista COMPLETA de establecimientos para resolver "
                "organizacion; solo para diagnostico. En la carga real el arbol debe ser Lara."
            ))
            self._avisado_arbol = True
        cambio = True
        while cambio:
            cambio = False
            for i, padre in padres.items():
                if padre in arbol and i not in arbol:
                    arbol.add(i)
                    cambio = True
        return arbol, nombres

    def resolver_organizaciones(self, nombres_lara):
        """mapa nombre normalizado -> Organizacion (crea las de Lara que falten)."""
        padre = (
            Organizacion.objects.filter(nivel="REGIONAL", estado="Lara")
            .exclude(codigo="LEGACY-LARA")
            .order_by("id")
            .first()
        )
        mapa = {normalizar(o.nombre): o for o in Organizacion.objects.filter(padre=padre)}
        if padre is None:
            self.stdout.write(self.style.WARNING(
                "No existe la Direccion de Epidemiologia del Estado Lara: los registros "
                "quedaran sin organizacion (seran visibles para todos, no por centro)."
            ))
            return {}
        # Los codigos que siembro asignar_organizacion_legacy son LEG-CENTRO-001,
        # LEG-CENTRO-002... El prefijo LEGCSV- evita chocar con esa serie, y se sigue
        # contando desde el maximo existente para no repetir ninguno.
        usados = set(Organizacion.objects.filter(codigo__startswith="LEGCSV-")
                     .values_list("codigo", flat=True))
        siguiente = max(
            [int(c.rsplit("-", 1)[1]) for c in usados if c.rsplit("-", 1)[-1].isdigit()] or [0]
        ) + 1
        faltan = sorted(n for n in nombres_lara if normalizar(n) and normalizar(n) not in mapa)
        if faltan:
            self.stdout.write(f"Organizaciones a crear: {len(faltan)}")
            for nombre in faltan:
                while f"LEGCSV-{siguiente:04d}" in usados:
                    siguiente += 1
                codigo = f"LEGCSV-{siguiente:04d}"
                usados.add(codigo)
                siguiente += 1
                org = Organizacion.objects.create(
                    nombre=nombre[:150],
                    codigo=codigo,
                    nivel="CENTRO",
                    estado="Lara",
                    padre=padre,
                    activo=True,
                )
                mapa[normalizar(nombre)] = org
        return mapa

    def cargar_lookups(self, cie10_legacy, org_geografica):
        self.cie10_nuevo = dict(CIE10.objects.values_list("codigo", "id"))
        self.mapeo_exa = {}
        self.mapeo_any = {}
        for c10, c11, tipo in MapeoCIE.objects.values_list("cie10_id", "cie11_id", "tipo"):
            self.mapeo_any.setdefault(c10, c11)
            if tipo == MapeoCIE.TIPO_EXACTO:
                self.mapeo_exa[c10] = c11
        self.cie10_legacy_cod = {}
        self.cie10_legacy_des = {}
        for f in cie10_legacy or []:
            seq = como_id(f.get("SEQ_ID_ACTUAL"))
            if not seq:
                continue
            self.cie10_legacy_cod[seq] = norm_cie10(f.get("COD_CLASIFICACION"))
            self.cie10_legacy_des[seq] = vacio(f.get("DES_CLASIFICACIO1"))
        self.geo = {}
        for f in org_geografica or []:
            num = como_id(f.get("NUM_REGION"))
            if num:
                self.geo[num] = parse_geo(f.get("NOMBRELARGO"))
        self.stdout.write(
            f"Lookups: CIE10={len(self.cie10_nuevo)} EXA={len(self.mapeo_exa)} "
            f"CIE10 legacy={len(self.cie10_legacy_cod)} geo={len(self.geo)}"
        )

    def resolver_cie(self, legacy_fk, fecha, resolver=True):
        """(cie10_id, cie11_id, sugerido_id, pendiente, codigo_legacy)."""
        if not resolver or legacy_fk is None or legacy_fk == "":
            return None, None, None, bool(legacy_fk), ""
        cod = self.cie10_legacy_cod.get(como_id(legacy_fk), "")
        c10_id = self.cie10_nuevo.get(cod)
        if c10_id is None and cod.endswith(".X"):
            c10_id = self.cie10_nuevo.get(cod[:-2])
        # Sin equivalencia EXACTA se usa la primera que exista (PAR/INE) y se deja
        # pendiente de revision. Antes el fallback solo se buscaba cuando no habia
        # CIE-10, de modo que un CIE-10 valido sin equivalencia exacta salia sin
        # CIE-11 y sin sugerencia, que es justo el caso que hay que revisar.
        c11_id = self.mapeo_exa.get(c10_id) if c10_id is not None else None
        sugerido = None
        if c10_id is not None:
            sugerido = c11_id if c11_id is not None else self.mapeo_any.get(c10_id)
        pendiente = c11_id is None
        return c10_id, c11_id, sugerido, pendiente, cod[:20]

    # ------------------------------------------------------------------ handle
    def handle(self, *args, **opts):
        self.directorio = opts["directorio"]
        self.limite = opts["limite"]
        self._ejecutar = opts["ejecutar"]
        self.permitir_arbol_completo = opts["permitir_arbol_completo"]
        ejecutar = opts["ejecutar"]
        resolver_cie = not opts["ignorar_causa"]

        if not os.path.isdir(self.directorio):
            raise CommandError(f"No existe el directorio {self.directorio}")

        self.stdout.write(f"CSV en: {self.directorio}")
        est = self.leer("establecimiento.csv", ["ID", "NOMBRE"], es_datos=False)
        cie10_legacy = self.leer("cie10_legacy.csv", ["SEQ_ID_ACTUAL", "COD_CLASIFICACION"], es_datos=False)
        geo = self.leer("org_geografica.csv", ["NUM_REGION", "NOMBRELARGO"], es_datos=False)
        muertes = self.leer("muerte.csv", ["ID", "FECHA_M"])
        causas = self.leer("causa_m.csv", ["HCERTIFICADO"]) or []
        cert_nac = self.leer("nacimiento.csv", ["ID"]) or []
        rnacidos = self.leer("nac_rnacido.csv", ["ID", "HCERTIFICADO"]) or []
        madres = self.leer("nac_madre.csv", ["ID", "HCERTIFICADO"]) or []
        tardios = self.leer("nacimiento_tardio.csv", ["ID"]) or []
        mmi = self.leer("casosmmi.csv", ["ID"]) or []
        rmm = self.leer("renglon_casosmm.csv", ["ID"]) or []
        rmi = self.leer("renglon_casosmi.csv", ["ID"]) or []

        self.cargar_lookups(cie10_legacy, geo)
        arbol, nombres = self.arbol_lara(est)
        nombres_lara = {nombres[i] for i in arbol if i in nombres and nombres[i]}
        self.stdout.write(f"Arbol Lara: {len(arbol)} establecimientos, {len(nombres_lara)} nombres unicos.")
        orgs = self.resolver_organizaciones(nombres_lara) if ejecutar else {
            normalizar(o.nombre): o
            for o in Organizacion.objects.filter(nivel="CENTRO", estado="Lara")
        }

        # --- defunciones -----------------------------------------------------
        texto_causa = {}
        for f in causas:
            clave = como_id(f.get("HCERTIFICADO"))
            orden = vacio(f.get("ORDENLISTA")) or "z"
            texto = vacio(f.get("DESENFERMEDAD"))
            if clave and texto:
                previo = texto_causa.get(clave)
                if previo is None or orden < previo[0]:
                    texto_causa[clave] = (orden, texto)

        resumen = {"def": self._defunciones(muertes, texto_causa, orgs, nombres, resolver_cie),
                   "nac": self._nacimientos(cert_nac, rnacidos, madres, orgs, nombres)}

        # --- archivos que NO se cargan (quedan como evidencia para el acta) ----
        self.stdout.write("")
        self.stdout.write("NO se cargan (no hay modelo en 'registros'; quedan en los CSV para el acta):")
        self.stdout.write(f"  nacimiento_tardio.csv  {len(tardios):>7} registros  registro tardio de parto")
        self.stdout.write(f"  casosmmi.csv           {len(mmi):>7} casos      muerte materna")
        self.stdout.write(f"  renglon_casosmm.csv    {len(rmm):>7} renglones   muerte materna")
        self.stdout.write(f"  renglon_casosmi.csv    {len(rmi):>7} renglones   muerte neonatal")
        self.stdout.write(
            "  Ojo: el MN del tablero y del acta NO sale de renglon_casosmi sino de Defuncion\n"
            "  (0-27 dias entre FECHA_M y FECHA_N), que es lo que se acaba de cargar."
        )

        for rotulo, r in resumen.items():
            self.stdout.write(
                f"{rotulo}: nuevos={r['nuevos']} actualizados={r['actualizados']} "
                f"sin_cambio={r['sin_cambio']} omitidos={r['omitidos']} "
                f"pendientes_codificacion={r['pendientes']} mm={r['mm']} mn={r['mn']}"
            )
        if not ejecutar:
            self.stdout.write(self.style.WARNING(
                "Dry-run: no se escribio nada. Use --ejecutar para aplicar."
            ))

    # -------------------------------------------------------------- defunciones
    def _defunciones(self, filas, texto_causa, orgs, nombres_establecimiento, resolver_cie):
        r = {"nuevos": 0, "actualizados": 0, "sin_cambio": 0, "omitidos": 0, "pendientes": 0, "mm": 0, "mn": 0}
        buffer = []
        en_visto = set()
        existentes = {
            obj.registro_numero: obj
            for obj in Defuncion.objects.filter(registro_numero__startswith="LEG-CERT-")
        }
        for f in filas:
            legacy_id = como_id(f.get("ID"))
            fecha = como_fecha(f.get("FECHA_M"))
            if not legacy_id or fecha is None or fecha < date(1900, 1, 1):
                r["omitidos"] += 1
                continue
            if legacy_id in en_visto:
                # El mismo certificado dos veces en el mismo archivo: sin esto, el
                # bulk_create revienta con UNIQUE y se pierde TODO el lote, no solo la fila.
                r["omitidos"] += 1
                self.stdout.write(self.style.WARNING(
                    f"muerte.csv: el certificado {legacy_id} aparece mas de una vez; "
                    "se procesa solo la primera."
                ))
                continue
            en_visto.add(legacy_id)
            fecha_nac = como_fecha(f.get("FECHA_N"))
            est_id = como_id(f.get("HESTABLECIMIENTO_OCUR")) or como_id(f.get("HESTABLECIMIENTO"))
            est, mun, parr = self.geo.get(como_id(f.get("HLOCARESIDENCIA")), ("", "", ""))
            nombre_est = nombres_establecimiento.get(est_id, "")
            causa_basica = vacio(f.get("HCAUSABASICA"))
            c10_id, c11_id, sug_id, pend, cod_legacy = self.resolver_cie(
                causa_basica, fecha, resolver_cie and bool(causa_basica)
            )
            # Un certificado SIN causa basica es, para todos los efectos, un
            # certificado que falta codificar. resolver_cie devuelve pendiente=False
            # en ese caso (solo mira si vino la clave), pero
            # importar_legacy_registros._resolver_cie devuelve True, y las 22
            # defunciones del mismo periodo que cargo ese comando estan
            # pendientes (verificado 05/10/2026). Sin esto, las 594 de esta
            # carga entraban con pendiente=False y NO aparecian en la bandeja
            # "Solo pendientes de codificacion" de /defunciones:|work
            # desaparecerian de la cola de trabajo. Solo se fuerza cuando la
            # resolucion esta activa: con --ignorar-causa no se toca el estado.
            if resolver_cie and not causa_basica:
                pend = True
            texto = texto_causa.get(legacy_id, (None, ""))[1]
            if not texto and causa_basica:
                texto = self.cie10_legacy_des.get(como_id(causa_basica), "")
            embarazo = como_entero(f.get("HPRESENCIAEMBARAZO")) in CODIGOS_MM
            numero = f"LEG-CERT-{legacy_id}"
            valores = {
                "fecha_evento": fecha,
                "hora_defuncion": como_hora(f.get("HORAMUERTE")),
                "fallecido_nombres": vacio(f.get("NOMBRE"))[:150] or "SIN NOMBRE",
                "fallecido_apellidos": vacio(f.get("APELLIDO"))[:150],
                "fallecido_cedula": vacio(f.get("CEDULA"))[:20],
                "sexo": SEXO.get(como_entero(f.get("SEXO")), "I"),
                "fecha_nacimiento": fecha_nac,
                "lugar_defuncion": "ESTABLECIMIENTO" if como_entero(f.get("HSITIO_M")) == 1 else "OTRO",
                "establecimiento": (nombre_est or vacio(f.get("HESTABLECIMIENTO")))[:200],
                "estado": est, "municipio": mun, "parroquia": parr,
                "causa_directa": (texto or "")[:300],
                "embarazo_o_puerperio": embarazo,
                "autopsia": como_entero(f.get("AUTOPSIA")) == 1,
                "certificador_nombres": (
                    vacio(f.get("OTROMEDFIRMANTE")) or vacio(f.get("HMEDICOFIRMANTE"))
                )[:150],
                "version_cie": version_cie_por_fecha(fecha),
                "organizacion": orgs.get(normalizar(nombre_est)) if nombre_est else None,
            }
            if embarazo:
                r["mm"] += 1
            if fecha_nac and 0 <= (fecha - fecha_nac).days <= 27:
                r["mn"] += 1

            previo = existentes.get(numero)
            if previo is None:
                valores.update(
                    registro_numero=numero, lote_id=LOTE_DEF, legacy_tabla="CERTIFICADO",
                    legacy_id=legacy_id,
                    cie10_id=c10_id, cie10_legacy=cod_legacy, cie11_id=c11_id,
                    cie11_sugerido_id=sug_id, codificacion_pendiente=pend,
                )
                buffer.append(Defuncion(**valores))
                r["nuevos"] += 1
            else:
                cambios = _aplicar(previo, valores)
                if cambios:
                    previo.save()
                    r["actualizados"] += 1
                else:
                    r["sin_cambio"] += 1
        if buffer and opts_ejecutar(self):
            Defuncion.objects.bulk_create(buffer, batch_size=500)
        r["pendientes"] = sum(1 for o in buffer if o.codificacion_pendiente)
        return r

    # ------------------------------------------------------------- nacimientos
    def _nacimientos(self, certificados, rnacidos, madres, orgs, nombres_establecimiento):
        r = {"nuevos": 0, "actualizados": 0, "sin_cambio": 0, "omitidos": 0, "pendientes": 0, "mm": 0, "mn": 0}
        cert_por_id = {como_id(f.get("ID")): f for f in certificados}
        madre_por_cert = {}
        for f in madres:
            madre_por_cert.setdefault(como_id(f.get("HCERTIFICADO")), f)
        buffer = []
        existentes = {
            obj.registro_numero: obj
            for obj in Nacimiento.objects.filter(registro_numero__startswith="LEG-RN-")
        }
        for f in rnacidos:
            legacy_id = como_id(f.get("ID"))
            cert_id = como_id(f.get("HCERTIFICADO"))
            fecha = como_fecha(f.get("NACIMIENTO")) or como_fecha(f.get("FECHANACIMIENTO"))
            if not legacy_id or fecha is None or fecha < date(1900, 1, 1):
                r["omitidos"] += 1
                continue
            cert = cert_por_id.get(cert_id) or {}
            madre = madre_por_cert.get(cert_id) or {}
            est_id = como_id(cert.get("HESTABLECIMIENTO"))
            est, mun, parr = self.geo.get(como_id(madre.get("HRESIDENCIA")), ("", "", ""))
            nombre_est = nombres_establecimiento.get(est_id, "")
            numero = f"LEG-RN-{legacy_id}"
            peso = peso_valido(f.get("PESO"))
            valores = {
                "fecha_evento": fecha,
                "hora_nacimiento": como_hora(f.get("NACIMIENTO")),
                "sexo": SEXO.get(como_entero(f.get("HSEXO")), "I"),
                "peso_gramos": peso,
                "talla_cm": talla_valida(f.get("TALLA")),
                "edad_gestacional_semanas": rango(f.get("SEMANAGESTACION"), 1, 45),
                "tipo_parto": FORMAPARTO.get(como_entero(f.get("HFORMAPARTO")), "OTRO"),
                "sitio_nacimiento": SITIO_PARTO.get(como_entero(f.get("HTIPOPARTO")), "OTRO"),
                "establecimiento": (nombre_est or vacio(cert.get("HESTABLECIMIENTO")))[:200],
                "estado": est, "municipio": mun, "parroquia": parr,
                "nacido_vivo": como_entero(f.get("VIVO_MUERTO")) != 2,
                "madre_nombres": vacio(madre.get("NOMBRES"))[:150] or "SIN NOMBRE",
                "madre_apellidos": vacio(madre.get("APELLIDOS"))[:150],
                "madre_cedula": vacio(madre.get("CEDULA"))[:20],
                "madre_edad": como_entero(madre.get("EDADM")) or 0,
                "organizacion": orgs.get(normalizar(nombre_est)) if nombre_est else None,
                "version_cie": version_cie_por_fecha(fecha),
            }
            # El estado civil de la madre solo se escribe si el CSV trae un valor
            # reconocible: inventar "SOLTERA" cuando no se sabe es fabricar un dato.
            estado_civil_madre = ESTADO_CIVIL.get(como_entero(madre.get("ESTADOCIVIL")))
            if estado_civil_madre:
                valores["madre_estado_civil"] = estado_civil_madre
            previo = existentes.get(numero)
            if previo is None:
                valores.update(
                    registro_numero=numero, lote_id=LOTE_NAC, legacy_tabla="NAC_RNACIDO",
                    legacy_id=legacy_id,
                )
                buffer.append(Nacimiento(**valores))
                r["nuevos"] += 1
            else:
                if _aplicar(previo, valores):
                    previo.save()
                    r["actualizados"] += 1
                else:
                    r["sin_cambio"] += 1
        if buffer and opts_ejecutar(self):
            Nacimiento.objects.bulk_create(buffer, batch_size=500)
        return r


def opts_ejecutar(cmd):
    return getattr(cmd, "_ejecutar", False)


# Campos que la carga NUNCA debe pisar, porque son trabajo humano del codificador.
PROTEGIDOS = ("cie10_id", "cie11_id", "cie10_legacy", "cie11_sugerido_id", "codificacion_pendiente")


def _aplicar(objeto, valores):
    """Vuelca en el objeto lo que cambio. Devuelve True si toco algo.

    Dos reglas, y las dos importan:

    1. Los campos de PROTEGIDOS no se tocan nunca si el objeto ya tiene un valor: son
       la codificacion que hizo el codificador a mano y recargar el CSV no puede borrarla.
    2. Un valor vacio NUNCA pisa un valor que ya habia. Si el CSV no trae la causa
       (CAUSA_M vacio, que es el caso de 2026) recargar no puede borrar la causa que
       alguien ya corrigio a mano: la ausencia de un dato no es un dato.
    """
    toco = False
    for campo, nuevo in valores.items():
        actual = getattr(objeto, campo, None)
        if actual == nuevo:
            continue
        if campo in PROTEGIDOS and actual not in (None, "", False):
            continue
        if nuevo in (None, "", 0) and actual not in (None, ""):
            continue
        setattr(objeto, campo, nuevo)
        toco = True
    return toco
