"""Detección de datos sospechosos en certificados (§35).

El legacy capturó a mano, sin validación, el número físico del certificado y algunos
nombres. La auditoría del 14/10/2026 encontró números que no son numéricos
(``.141409``, ``C85.9``, ``ABRAHAM JESUS``) y nombres con dígitos incrustados
(``0CTAVIA``, ``SANCHEZ ADRIANA JOSEFINA15776495``), casi todos de 2009-2011.

Estas funciones detectan esos casos para dos consumidores:

- ``manage.py auditar_certificados`` (informe con CSV), y
- el filtro «solo con datos sospechosos» de las listas (``?sospechosos=1``).

La detección es **no destructiva**: describe, no corrige.
"""

import re

from django.db.models import Q

# Un número «sano» es solo dígitos; cualquier otra cosa se reporta.
_RE_NUMERO = re.compile(r"^\d+$")
# Un nombre con un dígito incrustado es sospechoso de tecleo/OCR.
_RE_DIGITO = re.compile(r"\d")
# Números que son en realidad la fecha del evento (p. ej. 16032021), el caso más claro
# de confusión; el resto de los «parecen fecha» son planillas largas (falso positivo).
_RE_OCHO_DIGITOS = re.compile(r"^\d{8}$")


def numero_sospechoso(numero):
    """True si el número no es puramente numérico (el campo vacío no es sospechoso)."""
    texto = (numero or "").strip()
    return bool(texto) and not _RE_NUMERO.match(texto)


def nombre_sospechoso(*valores):
    """True si alguno de los nombres trae dígitos incrustados."""
    return any(_RE_DIGITO.search(v or "") for v in valores)


def numero_es_fecha(numero, fecha_evento):
    """True si el número de 8 dígitos coincide con la fecha del evento (DDMMAAAA)."""
    texto = (numero or "").strip()
    if not fecha_evento or not _RE_OCHO_DIGITOS.match(texto):
        return False
    return texto == fecha_evento.strftime("%d%m%Y")


def q_sospechosos(campo_numero, campos_nombre=()):
    """``Q`` para el filtro de la lista: número no numérico o nombre con dígitos.

    Portable (PostgreSQL y SQLite): usa el ``REGEXP`` que Django registra en ambos
    motores. El campo numérico vacío **no** cuenta como sospechoso.
    """
    q = ~Q(**{f"{campo_numero}__regex": r"^\d+$"}) & ~Q(**{campo_numero: ""})
    for campo in campos_nombre:
        q |= Q(**{f"{campo}__regex": r"\d"})
    return q
