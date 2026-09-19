import re
from datetime import date, time

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from catalogos.models import CIE10, CIE11, MapeoCIE
from registros.models import Defuncion, Nacimiento
from registros.services import version_cie_por_fecha

LOTE_NAC = "LEGACY-CERTNACIMIENTO"
LOTE_DEF = "LEGACY-CERTIFICADO"

# OJO: en los datos legacy el código de sexo está invertido respecto al catálogo
# 'sismai.SEXO' (que rotula 01=MASCULINO/02=FEMENINO). Verificado sobre los nombres
# reales de CERTIFICADO y NAC_RNACIDO: 1 → femenino, 2 → masculino.
SEXO = {1: "F", 2: "M", 3: "I", 0: "I"}
FORMAPARTO = {1: "VAGINAL", 2: "CESAREA", 3: "INSTRUMENTAL", 4: "OTRO", 5: "OTRO"}
SITIO_PARTO = {1: "ESTABLECIMIENTO", 2: "ESTABLECIMIENTO", 5: "ESTABLECIMIENTO", 3: "DOMICILIO"}
ESTADO_CIVIL = {
    1: "SOLTERA", 2: "CASADA", 3: "DIVORCIADA", 4: "UNION_LIBRE",
    5: "DIVORCIADA", 6: "SOLTERA", 7: "VIUDA", 8: "SOLTERA",
}
GEO_RE = re.compile(r"Estado\s+([^,]+),\s*Municipio\s+([^,]+),\s*Parroquia\s+([^,]+)", re.I)


def norm_cie10(codigo):
    codigo = (codigo or "").strip()
    codigo = codigo.replace("\u0086", "").replace("\u2020", "").replace("\u2021", "").replace("*", "")
    return re.sub(r"[^A-Za-z0-9.]", "", codigo).upper()


def parse_hora(valor):
    if not valor:
        return None
    s = str(valor).strip().upper().replace(".", "")
    m = re.match(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?\s*([AP]M)?$", s)
    if not m:
        return None
    h, mi, se = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
    ap = m.group(4)
    if ap == "PM" and h < 12:
        h += 12
    elif ap == "AM" and h == 12:
        h = 0
    if h > 23 or mi > 59:
        return None
    return time(h, mi, se)


def parse_geo(nombre_largo):
    if not nombre_largo:
        return "", "", ""
    m = GEO_RE.search(nombre_largo)
    if not m:
        return "", "", ""
    return m.group(1).strip().title(), m.group(2).strip().title(), m.group(3).strip().title()


def como_entero(v):
    if v is None:
        return None
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return None


def talla_valida(v):
    """Talla en cm razonable (20-100); descarta valores basura del legacy (p. ej. 5000)."""
    try:
        t = round(float(v), 1)
    except (TypeError, ValueError):
        return None
    return t if 20 <= t <= 100 else None


def peso_valido(v):
    """Peso del RN en gramos; el legacy suele guardarlo en kg (ej. 1.84 → 1840)."""
    g = como_entero(v)
    if g is None:
        return None
    if g < 20:
        g *= 1000
    return g if 200 <= g <= 8000 else None


def rango(v, minimo, maximo, defecto=None):
    n = como_entero(v)
    return n if n is not None and minimo <= n <= maximo else defecto


class Command(BaseCommand):
    help = (
        "ETL del sistema legacy (espejo sismai.*) hacia los modelos de 'registros'. "
        "Preserva el código CIE-10 original en 'cie10_legacy', resuelve el catálogo nuevo "
        "y deja 'codificacion_pendiente' cuando el evento requiere CIE-11 y no hay equivalencia."
    )

    def add_arguments(self, parser):
        parser.add_argument("--modelo", choices=["nacimientos", "defunciones", "todos"], default="todos")
        parser.add_argument("--limite", type=int, default=0, help="Procesa solo N filas (pruebas).")
        parser.add_argument("--borrar", action="store_true", help="Elimina los lotes LEGACY-* antes de cargar.")

    def handle(self, *args, **opts):
        self.pendientes = 0
        self._cargar_lookups()
        if opts["borrar"]:
            n = Nacimiento.objects.filter(lote_id=LOTE_NAC).delete()[0]
            d = Defuncion.objects.filter(lote_id=LOTE_DEF).delete()[0]
            self.stdout.write(f"Borrados lotes previos: nacimientos={n} defunciones={d}")
        if opts["modelo"] in ("nacimientos", "todos"):
            self._nacimientos(opts["limite"])
        if opts["modelo"] in ("defunciones", "todos"):
            self._defunciones(opts["limite"])

    # ---------- catálogos de apoyo ----------
    def _cargar_lookups(self):
        self.cie10_nuevo = dict(CIE10.objects.values_list("codigo", "id"))
        self.mapeo_exa = {}
        self.mapeo_any = {}
        for c10, c11, tipo in MapeoCIE.objects.values_list("cie10_id", "cie11_id", "tipo"):
            self.mapeo_any.setdefault(c10, c11)
            if tipo == MapeoCIE.TIPO_EXACTO:
                self.mapeo_exa[c10] = c11
        with connection.cursor() as cur:
            cur.execute('SELECT "SEQ_ID_ACTUAL","COD_CLASIFICACION","DES_CLASIFICACIO1" FROM sismai."CIE10";')
            self.cie10_legacy_cod = {}
            self.cie10_legacy_des = {}
            for pk, cod, des in cur.fetchall():
                cod_n = norm_cie10(cod)
                self.cie10_legacy_cod[float(pk)] = cod_n
                self.cie10_legacy_des[float(pk)] = (des or "").strip()
            cur.execute('SELECT "NUM_REGION","NOMBRELARGO" FROM sismai."ORG_GEOGRAFICA";')
            self.geo = {}
            for num, largo in cur.fetchall():
                self.geo[float(num)] = parse_geo(largo)
            cur.execute('SELECT "ID","NOMBRE" FROM sismai."ESTABLECIMIENTO";')
            self.estable = {float(i): (n or "").strip() for i, n in cur.fetchall()}
        self.stdout.write(
            f"Lookups: CIE10 nuevo={len(self.cie10_nuevo)} mapeos EXA={len(self.mapeo_exa)} "
            f"geo={len(self.geo)} establecimientos={len(self.estable)}"
        )

    def _resolver_cie(self, legacy_id_fk, fecha):
        """Devuelve (cie10_id, cie11_id, sugerido_id, pendiente, codigo_legacy)."""
        if legacy_id_fk is None:
            return None, None, None, True, ""
        cod = self.cie10_legacy_cod.get(float(legacy_id_fk), "")
        c10_id = self.cie10_nuevo.get(cod)
        if c10_id is None and cod.endswith(".X"):
            c10_id = self.cie10_nuevo.get(cod[:-2])
        if c10_id is None and "." in cod:
            c10_id = self.cie10_nuevo.get(cod.split(".")[0])
        exa = self.mapeo_exa.get(c10_id) if c10_id else None
        any_ = self.mapeo_any.get(c10_id) if c10_id else None
        espera_cie11 = version_cie_por_fecha(fecha) == "CIE11"
        if espera_cie11:
            cie11 = exa
            sugerido = None if exa else any_
            pendiente = cie11 is None
        else:
            cie11 = None
            sugerido = None
            pendiente = c10_id is None
        return c10_id, cie11, sugerido, pendiente, cod

    # ---------- Nacimientos ----------
    def _nacimientos(self, limite):
        sql = """
            SELECT r."ID", r."HCERTIFICADO", r."NOMBRES", r."FECHANACIMIENTO", r."HORA",
                   r."PESO", r."TALLA", r."HSEXO", r."HFORMAPARTO", r."HSITIOPARTO",
                   r."VIVO_MUERTO", r."SEMANAGESTACION",
                   c."FECHACERTIFICADO", c."HESTABLECIMIENTO", c."HLOCALIDADOC",
                   c."TOMO", c."FOLIO", c."LIBRO",
                   m."CEDULA", m."NOMBRES", m."APELLIDOS", m."EDADM", m."ESTADOCIVIL",
                   m."HRESIDENCIA", m."PNOMBRES", m."PCEDULA"
            FROM sismai."NAC_RNACIDO" r
            JOIN sismai."CERTNACIMIENTO" c ON c."ID" = r."HCERTIFICADO"
            LEFT JOIN (
                SELECT DISTINCT ON ("HCERTIFICADO")
                       "HCERTIFICADO", "CEDULA", "NOMBRES", "APELLIDOS", "EDADM",
                       "ESTADOCIVIL", "HRESIDENCIA", "PNOMBRES", "PCEDULA"
                FROM sismai."NAC_MADRE"
            ) m ON m."HCERTIFICADO" = r."HCERTIFICADO"
            ORDER BY r."ID"
        """
        if limite:
            sql += f" LIMIT {int(limite)}"
        with connection.cursor() as cur:
            cur.execute(sql)
            filas = cur.fetchall()

        existentes = set(Nacimiento.objects.filter(lote_id=LOTE_NAC).values_list("legacy_id", flat=True))
        gemelos = self._contar_gemelos()
        self.pendientes = 0
        buffer, total, sin_fecha = [], 0, 0
        procesados = set()
        for f in filas:
            (rn_id, cert_id, nombres, fecha_nac, hora, peso, talla, sexo, fparto, sitio,
             vivo, sem_gest, fecha_cert, estable_id, geo_id, tomo, folio, libro,
             madre_ci, madre_nom, madre_ape, madre_edad, madre_ec, madre_geo,
             padre_nom, padre_ci) = f
            fecha = fecha_nac or fecha_cert
            if fecha is None:
                sin_fecha += 1
                continue
            fecha = fecha.date() if hasattr(fecha, "date") else fecha
            if fecha < date(1900, 1, 1):
                sin_fecha += 1
                continue
            legacy_id = str(int(rn_id))
            if legacy_id in existentes or legacy_id in procesados:
                continue
            procesados.add(legacy_id)
            est, mun, parr = self.geo.get(float(geo_id) if geo_id is not None else -1, ("", "", ""))
            if not est and madre_geo is not None:
                est, mun, parr = self.geo.get(float(madre_geo), ("", "", ""))
            peso_g = peso_valido(peso)
            num_gem = gemelos.get(float(cert_id), 1)
            tipo_emb = {1: "UNICO", 2: "GEMELAR", 3: "TRIPLE"}.get(num_gem, "MULTIPLE")
            buffer.append(
                Nacimiento(
                    registro_numero=f"LEG-RN-{legacy_id}",
                    lote_id=LOTE_NAC,
                    legacy_tabla="NAC_RNACIDO",
                    legacy_id=legacy_id,
                    fecha_evento=fecha,
                    hora_nacimiento=parse_hora(hora),
                    sexo=SEXO.get(como_entero(sexo), "I"),
                    peso_gramos=peso_g,
                    talla_cm=talla_valida(talla),
                    edad_gestacional_semanas=rango(sem_gest, 1, 45),
                    tipo_parto=FORMAPARTO.get(como_entero(fparto), "OTRO"),
                    tipo_embarazo=tipo_emb,
                    numero_gemelar=num_gem if num_gem > 1 else None,
                    sitio_nacimiento=SITIO_PARTO.get(como_entero(sitio), "OTRO"),
                    establecimiento=self.estable.get(float(estable_id) if estable_id is not None else -1, ""),
                    estado=est, municipio=mun, parroquia=parr,
                    nacido_vivo=como_entero(vivo) == 1,
                    madre_nombres=(madre_nom or "").strip()[:150] or "SIN NOMBRE",
                    madre_apellidos=(madre_ape or "").strip()[:150],
                    madre_cedula=(madre_ci or "").strip()[:20],
                    madre_edad=rango(madre_edad, 0, 120, 0),
                    madre_estado_civil=ESTADO_CIVIL.get(como_entero(madre_ec), "SOLTERA"),
                    padre_nombres=(padre_nom or "").strip()[:150],
                    padre_cedula=(padre_ci or "").strip()[:20],
                    libro=(str(tomo) if tomo else "")[:20],
                    folio=rango(folio, 0, 2000000000),
                    version_cie=version_cie_por_fecha(fecha),
                    codificacion_pendiente=False,
                )
            )
            if len(buffer) >= self.LOTE:
                total += self._flush(Nacimiento, buffer)
                buffer = []
        total += self._flush(Nacimiento, buffer)
        self._resumen("nacimientos", total, sin_fecha)

    def _contar_gemelos(self):
        with connection.cursor() as cur:
            cur.execute('SELECT "HCERTIFICADO", count(*) FROM sismai."NAC_RNACIDO" GROUP BY 1;')
            return {float(k): int(v) for k, v in cur.fetchall()}

    # ---------- Defunciones ----------
    def _defunciones(self, limite):
        sql = """
            SELECT c."ID", c."NOMBRE", c."APELLIDO", c."CEDULA", c."SEXO", c."FECHA_M",
                   c."FECHA_N", c."HORAMUERTE", c."HSITIO_M", c."HESTABLECIMIENTO_OCUR",
                   c."HLOCARESIDENCIA", c."HPRESENCIAEMBARAZO", c."AUTOPSIA",
                   c."OTROMEDFIRMANTE", c."HCAUSABASICA"
            FROM sismai."CERTIFICADO" c
            WHERE c."FECHA_M" IS NOT NULL AND c."FECHA_M" >= DATE '1900-01-01'
            ORDER BY c."ID"
        """
        if limite:
            sql += f" LIMIT {int(limite)}"
        with connection.cursor() as cur:
            cur.execute(sql)
            filas = cur.fetchall()
            cur.execute('SELECT "HCERTIFICADO","HCIE10","DESENFERMEDAD","ORDENLISTA" FROM sismai."CAUSA_M";')
            causas = {}
            for hc, hcie, des, orden in cur.fetchall():
                causas.setdefault(float(hc), []).append((orden or "z", hcie, (des or "").strip()))

        existentes = set(Defuncion.objects.filter(lote_id=LOTE_DEF).values_list("legacy_id", flat=True))
        self.pendientes = 0
        buffer, total, sin_fecha = [], 0, 0
        procesados = set()
        for f in filas:
            (cid, nombre, apellido, cedula, sexo, fecha_m, fecha_n, hora, sitio,
             est_ocur, geo_id, embarazo, autopsia, otro_med, causa_bas) = f
            fecha = fecha_m.date() if hasattr(fecha_m, "date") else fecha_m
            legacy_id = str(int(cid))
            if legacy_id in existentes or legacy_id in procesados:
                continue
            procesados.add(legacy_id)
            est, mun, parr = self.geo.get(float(geo_id) if geo_id is not None else -1, ("", "", ""))
            c10_id, c11_id, sug_id, pend, cod_legacy = self._resolver_cie(causa_bas, fecha)
            lista = sorted(causas.get(float(cid), []), key=lambda x: (x[0] or "z"))
            if lista and lista[0][2]:
                texto = lista[0][2]
            elif causa_bas is not None:
                texto = self.cie10_legacy_des.get(float(causa_bas), "")
            else:
                texto = ""
            buffer.append(
                Defuncion(
                    registro_numero=f"LEG-CERT-{legacy_id}",
                    lote_id=LOTE_DEF,
                    legacy_tabla="CERTIFICADO",
                    legacy_id=legacy_id,
                    fecha_evento=fecha,
                    hora_defuncion=parse_hora(hora),
                    fallecido_nombres=(nombre or "").strip()[:150] or "SIN NOMBRE",
                    fallecido_apellidos=(apellido or "").strip()[:150],
                    fallecido_cedula=(cedula or "").strip()[:20],
                    sexo=SEXO.get(como_entero(sexo), "I"),
                    fecha_nacimiento=(fecha_n.date() if hasattr(fecha_n, "date") else fecha_n) if fecha_n else None,
                    lugar_defuncion="ESTABLECIMIENTO" if como_entero(sitio) == 1 else "OTRO",
                    establecimiento=self.estable.get(float(est_ocur) if est_ocur is not None else -1, ""),
                    estado=est, municipio=mun, parroquia=parr,
                    causa_directa=(texto or "")[:300],
                    embarazo_o_puerperio=como_entero(embarazo) == 1,
                    autopsia=como_entero(autopsia) == 1,
                    certificador_nombres=(otro_med or "").strip()[:150],
                    cie10_id=c10_id,
                    cie10_legacy=cod_legacy[:20],
                    cie11_id=c11_id,
                    cie11_sugerido_id=sug_id,
                    codificacion_pendiente=pend,
                    version_cie=version_cie_por_fecha(fecha),
                )
            )
            if len(buffer) >= self.LOTE:
                total += self._flush(Defuncion, buffer)
                buffer = []
        total += self._flush(Defuncion, buffer)
        self._resumen("defunciones", total, sin_fecha)

    LOTE = 5000

    def _flush(self, modelo, buffer):
        if not buffer:
            return 0
        with transaction.atomic():
            modelo.objects.bulk_create(buffer, batch_size=2000)
        n = len(buffer)
        self.pendientes += sum(1 for o in buffer if o.codificacion_pendiente)
        return n

    def _resumen(self, nombre, total, sin_fecha):
        self.stdout.write(
            self.style.SUCCESS(
                f"{nombre}: creados={total} pendientes_codificacion={self.pendientes} "
                f"sin_fecha_omitidos={sin_fecha}"
            )
        )

