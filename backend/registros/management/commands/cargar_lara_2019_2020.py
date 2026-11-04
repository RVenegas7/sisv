"""Carga ADITIVA de las defunciones de ``lara_2019_2020.xlsx`` en la app.

El archivo son las defunciones de Lara de 2019-2020 persona a persona (estructura
EV-14 «modelo 2012», 220 columnas y hoja ``Diccionario``), una fuente **paralela**
al legacy: no es una tabla de Oracle. La carga cruda vive en
``espejo_extra.lara_2019_2020`` (ver ``migracion/cargar_lara_2019_2020_pg.py``);
este comando la lleva a ``registros.Defuncion`` leyendo el Excel directamente.

Reglas de la carga (03/11/2026):

- **Aditiva**: nunca borra ni pisa un registro existente. Los certificados que ya
  están en la app (mismo ``numero_certificado`` = ``NUMEROMSDS``) se omiten.
- **Idempotente**: cada fila tiene una clave estable ``LARA-<hoja>-<fila>`` en
  ``legacy_id`` y un ``registro_numero`` único; una segunda corrida no duplica.
- **Dedup dentro del archivo**: la ``PLANILLA`` se repite; se conserva la primera
  aparición. Las filas sin número utilizable se descartan solo si ya hay un
  registro con el mismo nombre y la misma fecha.
- **Sin organización**: el xlsx **no trae el establecimiento** (``14b`` y
  ``14. ESTABLECIMIENTO`` vienen vacíos), así que la fila queda con
  ``organizacion`` nula. Atribuir por municipio sería inventar.
- **CIE**: la causa viene como ``O622 Otra inercia uterina``; se separa el código
  (``O62.2``) y se enlaza al catálogo CIE-10. Los eventos son anteriores al corte
  CIE-11 → ``version_cie`` CIE10. Solo quedan ``codificacion_pendiente`` las filas
  sin causa o con un código fuera del catálogo. **No** se confirma nada.

Notas del diccionario que el archivo no respeta al pie de la letra:

- ``39. tipo EDAD`` trae la **edad** del fallecido (los tipos están en ``C39V``);
  ``18 TIPO EDAD CUANTOS`` trae la **cantidad** de la unidad de ``C18A``.
- ``30. EDAD`` es la edad de la **madre** del feto/menor, no del fallecido.
- La **hora** de defunción viene en reloj de 12 horas y el marcador ``C9c``
  (a.m./p.m.) es aleatorio (50/50 en todas las horas), así que **no se carga**:
  guardarla sería inventar la mitad de las horas.
- La residencia es ``37*`` para feto/menor de un año (la de la familia) y
  ``46*``/``47`` para el fallecido de un año o más.

Uso::

    manage.py cargar_lara_2019_2020 [--archivo RUTA] [--ejecutar]
        [--limite N] [--csv informe.csv]

Sin ``--ejecutar`` solo informa (dry-run).
"""

import csv
import datetime
import re
from pathlib import Path

import openpyxl
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalogos.models import CIE10
from registros.models import Defuncion
from registros.services import dividir_nombre_compuesto, version_cie_por_fecha

LOTE_ID = "LARA-2019-2020"
HOJAS = ("2019", "2020")
LOTE = 2000

# Fecha de defunción y de nacimiento: ISO casi siempre; unas pocas de nacimiento
# vienen como D/M/A.
_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})")
_DMA = re.compile(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})")

# «478 - BARQUISIMETO En IRIBARREN, LARA» (con o sin el código delante).
_LUGAR = re.compile(r"^\s*(?:\d+\s*-\s*)?(.*?)\s+En\s+([^,]+),\s*([^,]+)\s*$", re.I)

# Código al inicio de la causa: C61+ , O622 , A09.0 , I500 …
_CIE = re.compile(r"^\s*([A-Za-z]\d{2}(?:\.\d)?)(?=[\s+*]|$)")
_CIE4 = re.compile(r"^\s*([A-Za-z]\d{3})(?=[\s+*]|$)")

# Código numérico CIUO delante de la descripción («904 OFICIOS DEL HOGAR…»).
_CODIGO_TEXTO = re.compile(r"^\s*[Xx]?\d{2,6}\s+(.*)$")

_PRIMER_NUMERO = re.compile(r"(\d+)")

SEXO = {"1": "M", "2": "F", "0": "I"}
NACIONALIDAD = {"1": "V", "2": "E", "3": "P", "4": "O", "9": "I"}

ESTADO_CIVIL = {
    "01": "SOLTERO", "02": "CASADO", "03": "DIVORCIADO", "04": "UNIDO",
    "05": "SEPARADO", "07": "VIUDO",
}

# 13 = sitio donde ocurrió la muerte (1 hospital, 2 clínica, 3 casa particular,
# 4 vía pública, 5 sitio de trabajo, 6 ignorado, 7 otro, 9 vía fluvial,
# 10 otros establecimientos de salud).
LUGAR_DEFUNCION = {
    "1": "ESTABLECIMIENTO", "2": "ESTABLECIMIENTO", "10": "ESTABLECIMIENTO",
    "3": "DOMICILIO", "4": "VIA_PUBLICA", "9": "VIA_PUBLICA",
    "5": "OTRO", "7": "OTRO",
}

MANERA_MORIR = {
    "1": "ACCIDENTE", "2": "AUTOINFLIGIDA", "3": "AGRESION",
    "4": "ESTUDIO_FORENSE", "5": "NO_DETERMINADA", "6": "NO_DETERMINADA",
}

TIPO_PARTO = {"1": "VAGINAL", "2": "CESAREA", "3": "INSTRUMENTAL"}
TIPO_EMBARAZO = {"1": "UNICO", "2": "MULTIPLE"}
ASISTENCIA_PARTO = {"1": "Médico", "2": "Comadrona", "3": "Otro"}
DESTINO = {"1": "INHUMACION", "2": "CREMACION"}
TIPO_CERTIFICACION = {"1": "MEDICA", "2": "NO_MEDICA"}
EMBARAZADA = {"1": "SI", "3": "NO", "4": "IGNORADO"}
SI_NO = {"1": "SI", "2": "NO"}


def _texto(valor):
    """Celda → texto recortado, o `None` si está vacía."""
    if valor is None:
        return None
    if isinstance(valor, datetime.datetime):
        return valor.isoformat(sep=" ")
    if isinstance(valor, datetime.date):
        return valor.isoformat()
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    valor = str(valor).strip()
    return valor or None


def _nombre_columna(crudo, usados):
    """Mismo normalizador que el cargador crudo del espejo (debe coincidir)."""
    base = re.sub(r"[^0-9a-zA-Z]+", "_", str(crudo).strip()).strip("_").lower()
    if not base:
        base = "col"
    if base[0].isdigit():
        base = "c_" + base
    if len(base) > 60:
        base = base[:60]
    nombre, n = base, 2
    while nombre in usados:
        nombre = f"{base}_{n}"
        n += 1
    usados.add(nombre)
    return nombre


def _fecha(valor):
    """Fecha ISO o D/M/A; `None` si no se puede leer."""
    if not valor:
        return None
    texto = str(valor).strip()
    m = _ISO.match(texto)
    if m:
        try:
            return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    m = _DMA.match(texto)
    if m:
        dia, mes, anio = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if anio < 100:
            anio += 1900 if anio > 30 else 2000
        try:
            return datetime.date(anio, mes, dia)
        except ValueError:
            return None
    return None


def _entero(valor, minimo=None, maximo=None):
    if valor is None:
        return None
    try:
        n = int(round(float(str(valor).strip())))
    except (TypeError, ValueError):
        return None
    if minimo is not None and n < minimo:
        return None
    if maximo is not None and n > maximo:
        return None
    return n


def _primer_entero(valor):
    """«38 SEMANAS» → 38."""
    if not valor:
        return None
    m = _PRIMER_NUMERO.search(str(valor))
    return int(m.group(1)) if m else None


def _codigo(valor):
    """Primer token de un valor con código delante («3 casa particular» → 3)."""
    if not valor:
        return ""
    return str(valor).strip().split(" ", 1)[0]


def _sin_codigo(valor, largo=200):
    """«904 OFICIOS DEL HOGAR, AMA DE CASA» → «OFICIOS DEL HOGAR, AMA DE CASA»."""
    if not valor:
        return ""
    m = _CODIGO_TEXTO.match(str(valor).strip())
    return (m.group(1) if m else str(valor).strip())[:largo]


def _si_no_codigo(valor):
    """Valor tipo «-1»/«0» de las casillas de confirmación → booleano."""
    return str(valor or "").strip() in ("-1", "1")


def _planilla(valor):
    """Número del certificado utilizable (dígitos y distinto de 0), o ''."""
    texto = (valor or "").strip()
    if re.fullmatch(r"\d+", texto) and int(texto) != 0:
        return texto
    return ""


def _clave_numero(valor):
    """Forma canónica del número para comparar contra la base."""
    valor = (valor or "").strip()
    if re.fullmatch(r"\d+", valor):
        return str(int(valor))
    return valor


def _causa(texto):
    """Separa la causa en (código CIE-10 normalizado, descripción)."""
    texto = (texto or "").strip()
    if not texto:
        return "", ""
    codigo, fin = "", 0
    m = _CIE.match(texto)
    if m:
        codigo, fin = m.group(1).upper(), m.end()
    else:
        m4 = _CIE4.match(texto)
        if m4:
            crudo = m4.group(1).upper()
            codigo, fin = f"{crudo[:3]}.{crudo[3]}", m4.end()
    if not codigo:
        return "", texto
    return codigo, texto[fin:].strip(" +*") or texto


def _resolver_cie10(codigo, mapa):
    """Código legacy → id de CIE10, con los mismos fallbacks que el ETL."""
    if not codigo:
        return None
    candidatos = [codigo]
    if codigo.endswith(".X"):
        candidatos.append(codigo[:-2])
    if "." in codigo:
        candidatos.append(codigo.split(".")[0])
    for candidato in candidatos:
        if candidato in mapa:
            return mapa[candidato]
    return None


def _lugar(texto):
    """«478 - BARQUISIMETO En IRIBARREN, LARA» → (parroquia, municipio, estado)."""
    if not texto:
        return "", "", ""
    m = _LUGAR.match(str(texto).strip())
    if not m:
        return "", "", ""
    return (
        m.group(1).strip().title(),
        m.group(2).strip().title(),
        m.group(3).strip().title(),
    )


def _clave_nombre(a1, a2, n1, n2):
    """Clave tolerante al orden de los campos para el dedup por nombre.

    Los nombres de relleno («XXX», «DESCONOCIDO», «SIN NOMBRE»…) no identifican
    a nadie y se descartan: un feto sin nombre no se puede deduplicar por nombre.
    """
    palabras = [
        x for x in " ".join(v for v in (a1, a2, n1, n2) if v).upper().split()
        if x not in _PLACEHOLDERS
    ]
    return " ".join(sorted(palabras))


_PLACEHOLDERS = {
    "XXX", "XX", "X", "DESCONOCIDO", "DESCONOCIDA", "SIN", "NOMBRE", "NOMBRES",
    "FETO", "NN", "N", "NO", "DECLARA",
}


def _parecido(clave_a, clave_b):
    """¿Dos claves de nombre comparten alguna palabra de 4+ letras?

    Los nombres del certificado se repiten con erratas de tecleo muy frecuentes
    (el nombre o un apellido mal escrito, un segundo nombre que falta), así que
    se comparan los tokens: con **una palabra exacta de 4+ letras** en común
    basta para considerarlos la misma persona a efectos de no duplicar. Las
    palabras cortas («ANA», «LUZ») y los rellenos se descartan porque no
    identifican a nadie.
    """
    largo = lambda clave: {p for p in clave.split() if len(p) >= 4}  # noqa: E731
    return bool(largo(clave_a) & largo(clave_b))


def _misma_persona(clave_a, fecha_a, cedula_a, clave_b, fecha_b, cedula_b):
    """¿Las dos filas son la misma persona? El número impreso, por sí solo, no lo dice.

    Se considera la misma si coincide la cédula, o el nombre (por tokens) o la
    fecha **con nombre parecido**: dos personas distintas pueden morir el mismo
    día con el mismo serial reutilizado (se comprobaron 3 casos en el archivo),
    así que la fecha sola no basta.

    La cédula **no** se usa como prueba en contra: un certificado repetido suele
    traer la cédula tecleada distinto (mismo número, mismo día, mismo apellido),
    y cargarlo otra vez crearía un duplicado. Relajar esto a «cédula distinta ⇒
    persona distinta» haría entrar 109 filas más, imposibles de distinguir sin
    el certificado en la mano.
    """
    if cedula_a and cedula_b and cedula_a == cedula_b:
        return True
    if clave_a and clave_b and clave_a == clave_b:
        return True
    if fecha_a != fecha_b:
        return False
    # Misma fecha y alguno sin nombre utilizable: no hay con qué distinguirlos.
    if not clave_a or not clave_b:
        return True
    return _parecido(clave_a, clave_b)


class Command(BaseCommand):
    help = (
        "Carga ADITIVA de las defunciones de lara_2019_2020.xlsx en "
        "'registros.Defuncion': omite lo ya existente, no toca la organización "
        "y deja el CIE-10 legacy enlazado. Dry-run por defecto."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--archivo",
            default=str(Path(settings.BASE_DIR).parent / "lara_2019_2020.xlsx"),
            help="Ruta del xlsx (por defecto, la raíz del repositorio).",
        )
        parser.add_argument(
            "--ejecutar", action="store_true",
            help="Aplica la carga (sin esto solo informa).",
        )
        parser.add_argument(
            "--limite", type=int, default=None,
            help="Procesa como máximo N filas del archivo (para probar).",
        )
        parser.add_argument(
            "--csv", default=None,
            help="Escribe el resultado fila por fila en este CSV (UTF-8 con BOM).",
        )

    # ------------------------------------------------------------------ main
    def handle(self, *args, **opts):
        archivo = Path(opts["archivo"])
        if not archivo.is_file():
            raise CommandError(f"No existe el archivo {archivo}")

        antes = {
            anio: Defuncion.objects.filter(fecha_evento__year=anio).count()
            for anio in (2019, 2020)
        }
        existentes_num, existentes_nombre, cargadas = self._existentes()
        mapa_cie = dict(CIE10.objects.values_list("codigo", "id"))

        self.stdout.write(f"Leyendo {archivo} ...")
        wb = openpyxl.load_workbook(archivo, read_only=True, data_only=True)
        faltan = [h for h in HOJAS if h not in wb.sheetnames]
        if faltan:
            raise CommandError(f"Faltan hojas en el archivo: {', '.join(faltan)}")

        contadores = {
            "leidas": 0, "sin_fecha": 0, "ya_cargadas": 0, "ya_existen": 0,
            "duplicadas": 0, "sin_numero_ya_existe": 0, "insertadas": 0,
            "pendientes_cie": 0, "sin_numero": 0, "numero_repetido": 0,
        }
        # El archivo es «lara 2019-2020», pero trae unas pocas inscripciones
        # tardías con fecha real de 2018 (y una de 2000, que parece un error de
        # tecleo). Se cargan igual: son defunciones reales que faltan.
        por_anio = {}
        vistos = {}  # número canónico → [(clave de nombre, fecha, cédula), …]
        buffer = []
        filas_csv = []

        for hoja in HOJAS:
            ws = wb[hoja]
            iterador = ws.iter_rows(min_row=2, values_only=True)
            cabecera = list(next(iterador, ()))
            indices, usados = {}, set()
            for i, celda in enumerate(cabecera):
                indices[_nombre_columna(celda, usados)] = i
            if "c_8_defuncion" not in indices:
                raise CommandError(f"La hoja {hoja} no trae la columna de defunción")

            def lector(fila, indices=indices):
                """Lector de una fila: `g("columna")` → texto o None."""
                def g(clave, indices=indices):
                    i = indices.get(clave)
                    if i is None or i >= len(fila):
                        return None
                    return _texto(fila[i])

                return g

            for numero, fila in enumerate(iterador, start=3):
                if opts["limite"] and contadores["leidas"] >= opts["limite"]:
                    break
                contadores["leidas"] += 1
                legado = f"{hoja}-{numero}"
                g = lector(fila)
                resultado, obj = self._fila(
                    hoja, numero, g, g("planilla"), legado,
                    mapa_cie=mapa_cie, existentes_num=existentes_num,
                    existentes_nombre=existentes_nombre, cargadas=cargadas,
                    vistos=vistos, contadores=contadores,
                )
                if obj is not None:
                    buffer.append(obj)
                    anio = obj.fecha_evento.year
                    por_anio[anio] = por_anio.get(anio, 0) + 1
                if resultado:
                    filas_csv.append([
                        hoja, numero, g("planilla") or "",
                        obj.registro_numero if obj else "", resultado,
                    ])
                if len(buffer) >= LOTE:
                    self._guardar(buffer, opts["ejecutar"])
                    buffer = []
        if buffer:
            self._guardar(buffer, opts["ejecutar"])

        self._resumen(contadores, por_anio, antes, opts["ejecutar"])
        if opts["csv"]:
            self._csv(opts["csv"], filas_csv)
            self.stdout.write(f"CSV del informe: {opts['csv']}")

    # -------------------------------------------------------------- helpers
    def _existentes(self):
        """Certificados ya presentes, nombres del histórico y filas del lote.

        El **número impreso se reutiliza**. De los 4.866 números del archivo que ya
        existen en la base, en 4.781 es la misma persona (se omite) y en **85 es
        otra** (el serial se asigna por libro/año): esos se cargan como certificado
        distinto y se marcan en el informe. Lo mismo vale dentro del archivo.
        """
        por_numero = {}
        for numero, ap1, ap2, nom1, nom2, cedula, fecha in Defuncion.objects.exclude(
            numero_certificado=""
        ).values_list(
            "numero_certificado", "fallecido_apellidos", "segundo_apellido",
            "fallecido_nombres", "segundo_nombre", "fallecido_cedula", "fecha_evento",
        ):
            datos = (
                _clave_nombre(ap1, ap2, nom1, nom2),
                fecha,
                _clave_numero(cedula),
            )
            for clave in {(numero or "").strip(), _clave_numero(numero)}:
                if clave:
                    por_numero.setdefault(clave, []).append(datos)

        nombres = set()
        for ap1, ap2, nom1, nom2, fecha in Defuncion.objects.filter(
            fecha_evento__year__in=(2018, 2019, 2020)
        ).values_list(
            "fallecido_apellidos", "segundo_apellido",
            "fallecido_nombres", "segundo_nombre", "fecha_evento",
        ):
            clave = _clave_nombre(ap1, ap2, nom1, nom2)
            if fecha and clave:
                nombres.add((clave, fecha))

        cargadas = set(
            Defuncion.objects.filter(lote_id=LOTE_ID).values_list("legacy_id", flat=True)
        )
        return por_numero, nombres, cargadas

    @staticmethod
    def _ya_existe(por_numero, planilla, canonica, clave, fecha_evento, cedula):
        """¿El número existente es *esta* persona y no otra con el serial reusado?"""
        datos = por_numero.get(planilla) or por_numero.get(canonica) or []
        cedula = _clave_numero(cedula)
        return any(
            _misma_persona(
                clave, fecha_evento, cedula, clave_existente, fecha_existente, cedula_existente
            )
            for clave_existente, fecha_existente, cedula_existente in datos
        )

    def _fila(self, hoja, numero, g, planilla_cruda, legado, *,
              mapa_cie, existentes_num, existentes_nombre, cargadas, vistos,
              contadores):
        """Devuelve (resultado, Defuncion|None) para una fila del xlsx."""
        if legado in cargadas:
            contadores["ya_cargadas"] += 1
            return "ya_cargada", None

        fecha_evento = _fecha(g("c_8_defuncion"))
        if not fecha_evento:
            contadores["sin_fecha"] += 1
            return "sin_fecha", None

        planilla = _planilla(planilla_cruda)
        canonica = _clave_numero(planilla)
        a1 = g("c_1_primer_apellido")
        a2 = g("c_2_segundo_apellido")
        n1 = g("c_3_primer_nombre")
        n2 = g("c_4_segundo_nombre")

        clave_nombre = _clave_nombre(a1, a2, n1, n2)
        cedula = g("c_5_cedula_de_identidad")
        repetido = False

        if planilla:
            if self._ya_existe(
                existentes_num, planilla, canonica, clave_nombre, fecha_evento, cedula
            ):
                contadores["ya_existen"] += 1
                return "ya_existe", None
            if self._ya_existe(
                vistos, planilla, canonica, clave_nombre, fecha_evento, cedula
            ):
                contadores["duplicadas"] += 1
                return "duplicada_en_archivo", None
            ya_en_archivo = bool(vistos.get(planilla) or vistos.get(canonica))
            # El número ya está usado (en la base o en el archivo) por *otra*
            # persona: se carga igual y se marca; el serial se reutiliza.
            repetido = bool(
                existentes_num.get(planilla) or existentes_num.get(canonica)
                or ya_en_archivo
            )
            vistos.setdefault(canonica, []).append(
                (clave_nombre, fecha_evento, _clave_numero(cedula))
            )
        else:
            contadores["sin_numero"] += 1
            if clave_nombre and (clave_nombre, fecha_evento) in existentes_nombre:
                contadores["sin_numero_ya_existe"] += 1
                return "ya_existe_por_nombre", None

        tipo = _codigo(g("tipo_de_defuncion"))          # 1 fetal · 2 <1 año · 3 ≥1 año
        es_menor = tipo in ("1", "2")

        # --- causa -------------------------------------------------------
        causa_texto = g("c_54_causa_de_muerte")
        cie10_legacy, descripcion = _causa(causa_texto)
        cie10_id = _resolver_cie10(cie10_legacy, mapa_cie)
        pendiente = cie10_id is None

        # --- residencia --------------------------------------------------
        residencia = g("c_37_lugar_de_residencia_h") if es_menor else g(
            "c_46_lugar_de_residencia_h"
        )
        parroquia, municipio, estado = _lugar(residencia)
        if not estado:
            parroquia, municipio, estado = _lugar(g("c_15_lugar_donde_ocurrio"))
        direccion = g("c_38_direccion") if es_menor else g("c_47_direccion")

        # --- edad --------------------------------------------------------
        edad, edad_unidad, edad_ignorada = self._edad(tipo, g)

        # --- madre y padre (sección del menor / registro civil) ----------
        madre_a1, madre_a2 = g("c_25_primer_apellido"), g("c_26_segundo_apellido")
        madre_n1, madre_n2 = g("c_27_primer_nombre"), g("c_28_segundo_nombre")
        madre_apellidos = " ".join(x for x in (madre_a1, madre_a2) if x)
        madre_nombres = " ".join(x for x in (madre_n1, madre_n2) if x)
        madre_cedula = g("c_29_cedula_de_identidad")
        if not madre_nombres and not madre_apellidos:
            nombre = g("c_74_apellido_y_nombre_de_la_madre_del_fallecido")
            if nombre and nombre.upper() not in ("XXX", "0"):
                madre_nombres, madre_apellidos = dividir_nombre_compuesto(nombre)
                madre_cedula = madre_cedula or g("c_75_cedula_de_identidad")

        nombre_padre = g("c_76_apellido_y_nombre_del_padre_del_fallecido_a")
        padre_nombres = ""
        if nombre_padre and nombre_padre.upper() not in ("XXX", "0"):
            nombres_p, apellidos_p = dividir_nombre_compuesto(nombre_padre)
            padre_nombres = f"{apellidos_p} {nombres_p}".strip()

        # --- embarazo / historia obstétrica (solo mujeres) ---------------
        sexo = SEXO.get(_codigo(g("c_6_sexo")), "I")
        embarazo = _codigo(g("c_48_presencia_de_embarazo"))
        es_mujer = sexo == "F"

        # --- causas asociadas --------------------------------------------
        asociadas = []
        for clave in ("asociada_a", "asociada_b", "asociada_c", "asociada_d"):
            valor = g(clave)
            if valor:
                asociadas.append(_causa(valor)[0] or valor)

        # --- lugar de nacimiento -----------------------------------------
        nacimiento = g("c_10_lugar_de_nacimiento") or ""
        if nacimiento.lower().startswith(("0 ", "no declara")):
            nacimiento = ""
        nacimiento = _sin_codigo(nacimiento, 80)
        exterior = (g("c10a") or "").strip().lower().startswith("exterior")

        def t(valor, largo):
            return (valor or "")[:largo]

        def sin_cero(clave, largo):
            """Número con ``0`` como «sin dato»."""
            valor = g(clave)
            if not valor or valor.strip() == "0":
                return ""
            return t(valor.strip(), largo)

        obj = Defuncion(
            registro_numero=f"LARA-{hoja}-{numero:05d}",
            lote_id=LOTE_ID,
            legacy_tabla="lara_2019_2020",
            legacy_id=legado,
            numero_certificado=t(planilla, 30),
            fecha_evento=fecha_evento,
            fallecido_nombres=t(n1 or "SIN NOMBRE", 150),
            fallecido_apellidos=t(a1, 150),
            segundo_nombre=t(n2, 150),
            segundo_apellido=t(a2, 150),
            fallecido_cedula=sin_cero("c_5_cedula_de_identidad", 20),
            nacionalidad=NACIONALIDAD.get(_codigo(g("c5a")), ""),
            sexo=sexo,
            fecha_nacimiento=_fecha(g("c_7_nacimiento")),
            edad=edad,
            edad_unidad=edad_unidad,
            edad_ignorada=edad_ignorada,
            lugar_nacimiento=t(nacimiento, 200),
            nacimiento_entidad=t(nacimiento if exterior is False else "", 80),
            nacimiento_exterior=exterior,
            nacimiento_pais=t(nacimiento if exterior else "", 80),
            lugar_defuncion=LUGAR_DEFUNCION.get(_codigo(g("c_13_sitio_donde_ocurrio_la_muerte")), "OTRO"),
            sitio_ocurrencia=t(g("c_13_sitio_donde_ocurrio_la_muerte"), 200),
            ubicacion_geografica=t(g("c_15_lugar_donde_ocurrio"), 150),
            establecimiento="",  # el xlsx no trae el nombre del establecimiento
            estado=t(estado, 60),
            municipio=t(municipio, 100),
            parroquia=t(parroquia, 100),
            residencia_habitual=t(direccion, 300),
            causa_directa=t(descripcion, 300),
            causa_descrita_medico=causa_texto or "",
            causa_antecedentes=t(", ".join(asociadas), 300),
            embarazo_o_puerperio=embarazo in ("1", "2"),
            fertil_estaba_embarazada=EMBARAZADA.get(embarazo, "") if es_mujer else "",
            fertil_puerperio="DENTRO12M" if embarazo == "2" and es_mujer else "",
            fertil_nacidos_vivos=_entero(g("c_40_nac_vivos"), 0) if es_mujer else None,
            fertil_nacidos_fallecidos=_entero(g("c_40_fallecidos"), 0) if es_mujer else None,
            fertil_muertes_fetales=_entero(g("c_40_muertes_f"), 0) if es_mujer else None,
            autopsia=(_codigo(g("c57a")) == "1"),
            diagnostico_examen_cadaver=_si_no_codigo(g("examen_del_cad_ver")),
            diagnostico_examen_laboratorio=_si_no_codigo(g("examen_lab")),
            diagnostico_historia_clinica=_si_no_codigo(g("historia_clinica")),
            diagnostico_interrogatorio_familiar=_si_no_codigo(
                g("interrogatorio_fam_o_testigo")
            ),
            matricula_mpps=sin_cero("c_60_b_matricula_mpps", 30),
            tipo_certificacion=TIPO_CERTIFICACION.get(
                _codigo(g("c_59_firma_60_certificacion")), ""
            ),
            certificador_nombres=t(g("c_66_certificacion_no_medica"), 150),
            manera_de_morir=MANERA_MORIR.get(
                _codigo(g("c_49_tipo_de_muerte_violenta_presuntiva")), ""
            ),
            fecha_hecho_violento=_fecha(g("c_50_fecha")),
            descripcion_hecho_violento=t(g("c_53_breve_descripcion_del_suceso"), 300),
            es_muerte_fetal=tipo == "1",
            peso_nacer_gramos=_entero(g("c_24_peso_del_feto_gramos"), 200, 8000),
            edad_gestacional_semanas=_entero(
                _primer_entero(g("c_19_duracion_del_embarazo_semanas")), 1, 45
            ),
            tipo_embarazo=TIPO_EMBARAZO.get(_codigo(g("c20a")), ""),
            tipo_parto=TIPO_PARTO.get(_codigo(g("c_21_tipo_de_parto")), ""),
            asistencia_parto=ASISTENCIA_PARTO.get(_codigo(g("c22a")), ""),
            madre_apellidos=t(madre_apellidos, 150),
            madre_nombres=t(madre_nombres, 150),
            madre_cedula=t(madre_cedula if madre_cedula and madre_cedula.strip() != "0" else "", 20),
            padre_fallecido_nombres=t(padre_nombres, 200),
            padre_fallecido_cedula=sin_cero("c_77_cedula_de_identidad", 20),
            estado_civil=ESTADO_CIVIL.get((g("c_41_situacion_conyugal") or "")[:2], ""),
            profesion=_sin_codigo(g("c_44_profesion"), 100),
            ocupacion_lugar_trabajo=_sin_codigo(g("c_45_ocupacion"), 200),
            sabe_leer_escribir=SI_NO.get(_codigo(g("c_42_leer")), ""),
            asistencia_medica=(
                SI_NO.get(_codigo(g("c_12_asist_medica")), "IGNORADO")
                if g("c_12_asist_medica") else ""
            ),
            fecha_registro=_fecha(g("c_73_fecha_registro")),
            numero_acta_defuncion=sin_cero("c_72_numero_de_acta", 30),
            folio_defuncion=sin_cero("c_72_numero_de_folio", 20),
            partida_tomo=sin_cero("c_17_numero_de_tomo", 20),
            partida_folio=sin_cero("c_17_numero_de_folio", 20),
            partida_libro=sin_cero("c_17_numero_de_libro", 20),
            partida_acta=sin_cero("numero_de_acta", 30),
            registrador_civil_nombres=sin_cero("c_78_apellido_y_nombre_del_registrador", 200),
            registrador_civil_cedula=sin_cero("c_79_cedula_de_identidad", 20),
            registrador_civil_nacionalidad=NACIONALIDAD.get(_codigo(g("c79a")), ""),
            destino_cadaver=DESTINO.get(_codigo(g("c_68_destino_del_cadaver")), ""),
            numero_permiso=sin_cero("c_69_no_de_permiso", 30),
            version_cie=version_cie_por_fecha(fecha_evento),
            cie10_id=cie10_id,
            cie10_legacy=t(cie10_legacy, 20),
            codificacion_pendiente=pendiente,
        )
        contadores["insertadas"] += 1
        if pendiente:
            contadores["pendientes_cie"] += 1
        if repetido:
            contadores["numero_repetido"] += 1
            return "insertada_numero_repetido", obj
        return "insertada", obj

    @staticmethod
    def _edad(tipo, g):
        """(edad, unidad, ignorada) — el archivo rotula mal las columnas.

        - feto / menor de 1 año: unidad en ``C18A`` (Horas, Días, Meses, Fetal)
          y cantidad en ``18 TIPO EDAD CUANTOS``;
        - 1 año o más: unidad en ``C39V`` (Años, 100 y, Ignorado) y valor en
          ``39. tipo EDAD``. ``30. EDAD`` es la edad de la madre: no se usa.
        """
        if tipo in ("1", "2"):
            unidad = (g("c18a") or "").strip().lower()
            valor = _entero(g("c_18_tipo_edad_cuantos"), 0, 99)
            if unidad.startswith("d"):
                return valor, "DIAS", False
            if unidad.startswith("mes"):
                return valor, "MESES", False
            if unidad.startswith("hora"):
                # Murió en las primeras horas de vida: menos de un día.
                return 0, "DIAS", False
            return None, "", False  # fetal: no tiene edad

        unidad = (g("c39v") or "").strip().lower()
        valor = _entero(g("c_39_tipo_edad"), 0, 120)
        if unidad.startswith("ignor"):
            return None, "", True
        if unidad.startswith("100"):
            return 100, "ANIOS", False
        if unidad.startswith("a"):
            return valor, "ANIOS", False
        return None, "", False

    def _guardar(self, buffer, ejecutar):
        if not ejecutar or not buffer:
            return
        with transaction.atomic():
            Defuncion.objects.bulk_create(buffer, batch_size=LOTE)

    def _resumen(self, c, por_anio, antes, ejecutar):
        self.stdout.write("")
        self.stdout.write(f"Filas leídas:                {c['leidas']}")
        self.stdout.write(f"  ya cargadas (idempotencia): {c['ya_cargadas']}")
        self.stdout.write(f"  certificado ya existe:      {c['ya_existen']}")
        self.stdout.write(f"  duplicadas en el archivo:   {c['duplicadas']}")
        self.stdout.write(f"  sin fecha de defunción:     {c['sin_fecha']}")
        self.stdout.write(f"  sin número:                 {c['sin_numero']}")
        self.stdout.write(
            f"    de esas, ya por nombre:   {c['sin_numero_ya_existe']}"
        )
        self.stdout.write(f"A insertar:                  {c['insertadas']}")
        self.stdout.write(
            f"  con número ya usado por otra persona (serial reusado): "
            f"{c['numero_repetido']}"
        )
        if por_anio:
            detalle = " · ".join(f"{a}={por_anio[a]}" for a in sorted(por_anio))
            self.stdout.write(f"  por año de la defunción: {detalle}")
        self.stdout.write(
            f"  CIE-10 enlazado: {c['insertadas'] - c['pendientes_cie']} · "
            f"codificación pendiente: {c['pendientes_cie']}"
        )
        if not ejecutar:
            self.stdout.write("\ndry-run: usa --ejecutar para cargar")
            return

        for anio in sorted(antes):
            self.stdout.write(
                f"Defunciones {anio} en la base: {antes[anio]} → "
                f"{Defuncion.objects.filter(fecha_evento__year=anio).count()}"
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"Cargadas {c['insertadas']} defunciones con lote {LOTE_ID} "
                "(sin organización: el xlsx no trae establecimiento)."
            )
        )

    def _csv(self, ruta, filas):
        with open(ruta, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["Hoja", "Fila", "Planilla", "Registro en SISV", "Resultado"])
            w.writerows(filas)
