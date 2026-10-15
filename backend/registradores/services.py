"""Consultas del historial de registradores civiles y limpieza del legacy."""

import re
from collections import Counter
from datetime import date, datetime

from django.db.models import Q

from registradores.models import DesignacionRegistrador

_ESPACIOS = re.compile(r"\s+")
_NO_DIGITOS = re.compile(r"\D")
_LETRAS = re.compile(r"[A-ZÁÉÍÓÚÜÑ]")

# Una cédula venezolana tiene al menos 5 dígitos (las más antiguas, 5–6). Por
# debajo de eso es basura del legacy («7», «0») y ensuciaría el catálogo.
MIN_DIGITOS_CEDULA = 5


def normalizar_cedula(valor):
    """Deja solo los dígitos de una cédula («V-12.345.678» → «12345678»)."""
    if not valor:
        return ""
    return _NO_DIGITOS.sub("", str(valor))


def normalizar_nombre(valor):
    """Mayúsculas y espacios colapsados de un nombre del legacy."""
    if not valor:
        return ""
    return _ESPACIOS.sub(" ", str(valor).strip().upper())


def nacionalidad_legacy(valor):
    """El legacy usa 2 = extranjero; cualquier otro valor (o nulo) es venezolano."""
    return "E" if str(valor).strip() in ("2", "2.0") else "V"


def _a_fecha(valor):
    """Normaliza a `date` una fecha del legacy (acepta `datetime`); None si no sirve."""
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    return None


def dividir_nombre(nombre):
    """Separa un nombre del legacy en (nombres, apellidos).

    El formato dominante del legacy es **apellidos primero** («ESPINOZA NELIDA»,
    «VALERA ELVIA ROSA»), así que se asume: 1-3 tokens → el primero es el
    apellido y el resto los nombres; 4 o más → los dos primeros son apellidos.
    Es una heurística: el catálogo se puede corregir a mano.
    """
    tokens = normalizar_nombre(nombre).split()
    if not tokens:
        return "", ""
    if len(tokens) == 1:
        return tokens[0], ""
    if len(tokens) <= 3:
        return " ".join(tokens[1:]), tokens[0]
    return " ".join(tokens[2:]), " ".join(tokens[:2])


def consolidar_registradores(filas):
    """Agrupa registradores del legacy por cédula y elige el nombre canónico.

    `filas` es un iterable de `(nacregistrador, ciregistrador, nomregistrador)`.
    Se admiten filas de 4 elementos, con la **fecha del certificado** al final:
    cuando viene, se anota el periodo observado (`firmo_desde`/`firmo_hasta`),
    que **no** es una designación sino el rango en que ese registrador aparece
    firmando en el legacy.

    Para cada cédula se elige el nombre más frecuente (y, a igualdad, el más
    largo). Devuelve una lista de dicts ordenada por cédula.
    """
    variantes = {}
    certificados = {}
    periodo = {}
    descartados = {"sin_cedula": 0, "sin_nombre": 0, "cedula_corta": 0}
    for fila in filas:
        nac, ci, nom = fila[0], fila[1], fila[2]
        fecha = _a_fecha(fila[3]) if len(fila) > 3 else None
        cedula = normalizar_cedula(ci)
        nombre = normalizar_nombre(nom)
        if not cedula:
            descartados["sin_cedula"] += 1
            continue
        if len(cedula) < MIN_DIGITOS_CEDULA:
            descartados["cedula_corta"] += 1
            continue
        if not nombre or not _LETRAS.search(nombre):
            descartados["sin_nombre"] += 1
            continue
        nacionalidad = nacionalidad_legacy(nac)
        clave = (nacionalidad, cedula)
        variantes.setdefault(clave, Counter())[nombre] += 1
        certificados[clave] = certificados.get(clave, 0) + 1
        if fecha is not None:
            inicio, fin = periodo.get(clave, (fecha, fecha))
            periodo[clave] = (min(inicio, fecha), max(fin, fecha))

    resultado = []
    for (nacionalidad, cedula), contador in sorted(variantes.items()):
        canonico = max(contador.items(), key=lambda par: (par[1], len(par[0])))[0]
        nombres, apellidos = dividir_nombre(canonico)
        desde, hasta = periodo.get((nacionalidad, cedula), (None, None))
        resultado.append({
            "nacionalidad": nacionalidad,
            "cedula": cedula,
            "nombres": nombres,
            "apellidos": apellidos,
            "variantes": len(contador),
            "certificados": certificados[(nacionalidad, cedula)],
            "firmo_desde": desde,
            "firmo_hasta": hasta,
        })
    return resultado, descartados


def vigentes_en(registro_civil_id, fecha, cargo=None):
    """Designaciones vigentes en `fecha` para un registro civil.

    Una designación cubre la fecha si `desde <= fecha` y (`hasta` es nulo o
    `hasta >= fecha`). Varios registradores pueden estar vigentes a la vez
    (titular y suplente), por eso devuelve un queryset ordenado por cargo.
    """
    qs = (
        DesignacionRegistrador.objects.filter(
            registro_civil_id=registro_civil_id,
            desde__lte=fecha,
        )
        .filter(Q(hasta__isnull=True) | Q(hasta__gte=fecha))
        .select_related("registrador", "registro_civil")
        .order_by("cargo", "registrador__apellidos", "registrador__nombres")
    )
    if cargo:
        qs = qs.filter(cargo=cargo)
    return qs
