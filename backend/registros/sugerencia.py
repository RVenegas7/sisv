"""Sugerencia de codificación CIE **sin IA** (offline, por catálogo local).

El certificado se consulta por número, se muestra completo y el rol CODIFICADOR solo
confirma el código. Este módulo propone el código más probable a partir del texto de
causa/evento ya registrado, usando **únicamente** los catálogos CIE cargados en la base
(`catalogos.CIE10` / `catalogos.CIE11`) y el cross-walk `MapeoCIE`. No hay llamadas a
servicios externos: el sistema funciona sin internet.

La forma del resultado imita el JSON que describe `codificador.md` (causa básica +
candidatos), pero las reglas nosológicas de la OMS **no** se automatizan aquí: la
persona que codifica es quien decide y confirma.
"""

import re
import unicodedata

from catalogos.models import CIE10, CIE11, MapeoCIE

LIMITE_CANDIDATOS = 8
LONGITUD_MINIMA_TOKEN = 3
MAX_TERMINOS_CONSULTA = 10

_STOPWORDS = {
    "de", "del", "la", "las", "el", "los", "y", "o", "u", "en", "por", "para",
    "con", "sin", "al", "a", "su", "sus", "se", "que", "como", "mas", "más",
    "un", "una", "unos", "unas", "lo", "le", "les", "es", "son", "fue", "era",
    "the", "and", "of", "no", "ni", "si", "sí", "tras", "ante", "bajo", "sobre",
    "entre", "hacia", "hasta", "desde", "durante", "mediante", "según", "segun",
    "causa", "causas", "diagnostico", "diagnóstico", "enfermedad", "paciente",
    "muerte", "fallecido", "fallecida", "tipo", "otros", "otras", "otro", "otra",
}


def _sin_acentos(texto):
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


def _normalizar(texto):
    return _sin_acentos((texto or "").lower())


def _tokens(texto):
    """Tokens clínicos: normaliza, parte por no-alfanumérico, quita stopwords."""
    limpio = re.sub(r"[^0-9a-záéíóúüñ]+", " ", _normalizar(texto))
    return {
        t for t in limpio.split()
        if len(t) >= LONGITUD_MINIMA_TOKEN and t not in _STOPWORDS and not t.isdigit()
    }


def texto_de_causa(registro):
    """Texto libre del que se puede inferir un código, según el módulo."""
    campos = {
        "Defuncion": [
            "causa_primera_parte", "causa_segunda_parte", "causa_antecedentes",
            "causa_directa", "causa_descrita_medico", "otros_estados_patologicos",
        ],
        "FichaVigilancia": ["nombre_evento", "sintomas", "nota"],
        "Nacimiento": [],
    }.get(type(registro).__name__, [])
    partes = []
    for campo in campos:
        valor = getattr(registro, campo, "") or ""
        valor = valor.strip() if isinstance(valor, str) else ""
        if valor:
            partes.append(valor)
    return " . ".join(partes)


def _puntuar(consulta, titulo):
    """Cuánto se solapa el texto consultado con el título del catálogo (no normalizado aparte).

    Se premia cada token coincidente por su longitud: una palabra larga y específica vale
    más que varias cortas, así "insuficiencia renal" no empata con "dolor".
    """
    titulo_tokens = _tokens(titulo)
    comunes = consulta & titulo_tokens
    if not comunes:
        return 0
    return sum(len(t) for t in comunes)


def _candidatos_catalogo(consulta, version, limite_busqueda=250):
    if version == "CIE10":
        base = CIE10.objects.filter(activo=True)
        campos = ("codigo", "descripcion")
    else:
        base = CIE11.objects.filter(activo=True, nivel__in=(CIE11.NIVEL_CATEGORIA, CIE11.NIVEL_SUBGRUPO))
        campos = ("codigo", "titulo")

    terminos = sorted(consulta, key=len, reverse=True)[:MAX_TERMINOS_CONSULTA]
    vistos = {}
    for termino in terminos:
        for obj in base.filter(**{f"{campos[1]}__icontains": termino})[:limite_busqueda]:
            vistos[obj.pk] = obj

    candidatos = []
    for obj in vistos.values():
        titulo = getattr(obj, campos[1])
        puntaje = _puntuar(consulta, titulo)
        if puntaje:
            candidatos.append({
                "codigo": getattr(obj, campos[0]),
                "titulo": titulo,
                "score": puntaje,
                "nivel": getattr(obj, "nivel", None),
                "fuente": version,
            })
    candidatos.sort(key=lambda c: (-c["score"], len(c["titulo"])))
    return candidatos[:LIMITE_CANDIDATOS]


def _desde_crosswalk(registro, version):
    """Apuesta fuerte: el código legacy histórico traducido por el cross-walk CIE-10↔CIE-11."""
    codigo_legacy = (getattr(registro, "cie10_legacy", "") or "").strip()
    if not codigo_legacy:
        return None
    try:
        c10 = CIE10.objects.get(codigo=codigo_legacy)
    except CIE10.DoesNotExist:
        return None
    if version == "CIE10":
        return {"codigo": c10.codigo, "titulo": c10.descripcion, "score": 999,
                "nivel": None, "fuente": "CIE10-LEGACY"}
    mapeo = (MapeoCIE.objects.filter(cie10=c10)
             .select_related("cie11").order_by("tipo").first())
    if not mapeo:
        return None
    return {"codigo": mapeo.cie11.codigo, "titulo": mapeo.cie11.titulo, "score": 999,
            "nivel": mapeo.cie11.nivel, "fuente": "CROSSWALK"}


def sugerir(registro):
    """Devuelve la sugerencia de codificación para un registro, sin efectos secundarios.

    Estructura::

        {"texto": str, "version": "CIE10"|"CIE11", "origen": "CATALOGO",
         "causa_basica": {codigo, titulo, ...}|None, "candidatos": [...]}
    """
    version = getattr(registro, "version_cie", None) or "CIE11"
    texto = texto_de_causa(registro)
    consulta = _tokens(texto)

    candidatos = []
    crosswalk = _desde_crosswalk(registro, version)
    if crosswalk:
        candidatos.append(crosswalk)
    if consulta:
        candidatos.extend(_candidatos_catalogo(consulta, version))

    ya = set()
    unicos = []
    for c in candidatos:
        clave = c["codigo"]
        if clave in ya:
            continue
        ya.add(clave)
        unicos.append(c)
    unicos.sort(key=lambda c: (-c["score"], len(c["titulo"])))
    unicos = unicos[:LIMITE_CANDIDATOS]

    return {
        "texto": texto,
        "version": version,
        "origen": "CATALOGO",
        "causa_basica": unicos[0] if unicos else None,
        "candidatos": unicos,
    }
