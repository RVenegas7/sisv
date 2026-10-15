"""Cruce entre los talonarios despachados y los certificados cargados en la BD.

La serie del talonario es el consecutivo que va dentro del «Nº de certificado»
(`registro_numero`). Se extrae el bloque de dígitos finales para poder comparar:
`NC-2026-000123` → `123`, `DEF-2026-000045` → `45`, `LEG-CERT-12345` → `12345`.

El centro se resuelve por el árbol de organizaciones: un talonario entregado a una
organización cubre también sus descendientes (una regional entrega a sus centros).
"""

import re

from despacho.models import NovedadCertificado, Talonario
from registros.models import Defuncion, Nacimiento
from seguridad.models import Organizacion
from vigilancia.services import organizaciones_descendientes

_RE_DIGITOS_FINALES = re.compile(r"(\d+)\s*$")

MODELO_POR_TIPO = {
    Talonario.TIPO_NACIMIENTO: Nacimiento,
    Talonario.TIPO_DEFUNCION: Defuncion,
}


def numero_de_registro(registro_numero):
    """Consecutivo final del Nº de certificado, o None si no tiene dígitos."""
    if not registro_numero:
        return None
    coincidencia = _RE_DIGITOS_FINALES.search(str(registro_numero).strip())
    return int(coincidencia.group(1)) if coincidencia else None


def _ids_organizaciones(centro):
    return [o.id for o in organizaciones_descendientes(centro)]


def persona_registro(modelo, registro):
    """Nombre y apellidos para identificar el certificado, y de quién son.

    En defunción son del fallecido. En nacimiento es del recién nacido; mientras el
    certificado cargado no traiga su nombre (los que importationó el legacy, anteriores
    al EV-25) se recurre al de la madre y así se dice en la etiqueta, porque un
    certificado identificado por el nombre de la madre parece de otra persona.
    """
    if modelo is Defuncion:
        return registro.fallecido_nombres or "", registro.fallecido_apellidos or "", "Fallecido"
    nombres = registro.nino_nombres or registro.madre_nombres or ""
    apellidos = registro.nino_apellidos or registro.madre_apellidos or ""
    etiqueta = "Recién nacido" if registro.nino_nombres else "Madre"
    return nombres, apellidos, etiqueta


def numero_en_serie(modelo, registro):
    """Consecutivo físico del certificado para ubicarlo en la serie del talonario.

    Prioriza el número impreso real (``numero_certificado`` en defunción,
    ``numero_planilla`` en nacimiento — §27.16); si no está cargado, cae a los
    dígitos finales del ``registro_numero`` (certificados capturados a mano).
    """
    real = registro.numero_certificado if modelo is Defuncion else registro.numero_planilla
    if real is not None:
        real = str(real).strip()
        if real.isdigit():
            return int(real)
    return numero_de_registro(registro.registro_numero)


def certificados_usados(talonario):
    """Certificados de la serie que ya están cargados, indexados por consecutivo.

    Devuelve `{numero: registro}`. Solo mira dentro del subárbol del centro y dentro
    del rango de la serie; el certificado cuyo número no se puede ubicar en la serie
    se ignora (no se cuenta como usado ni como faltante — queda fuera del cálculo y
    el reporte lo advierte).
    """
    modelo = MODELO_POR_TIPO[talonario.tipo]
    ids = _ids_organizaciones(talonario.centro)
    qs = modelo.objects.filter(organizacion_id__in=ids).only(
        "id", "registro_numero", "organizacion_id", "numero_certificado"
        if modelo is Defuncion else "numero_planilla"
    )
    usados = {}
    for registro in qs.iterator():
        numero = numero_en_serie(modelo, registro)
        if numero is not None and talonario.serie_desde <= numero <= talonario.serie_hasta:
            usados[numero] = registro
    return usados


def resumen_talonario(talonario, usados=None):
    """Estado del talonario: cuántos usados, dañados, devueltos, en tránsito y faltantes."""
    if usados is None:
        usados = certificados_usados(talonario)

    novedades = list(talonario.novedades.all())
    por_estado = {"DANADO": set(), "EN_TRANSITO": set(), "DEVUELTO": set()}
    for novedad in novedades:
        if novedad.estado in por_estado:
            por_estado[novedad.estado].add(novedad.numero)

    usados_numeros = set(usados)
    danados = por_estado["DANADO"]
    devueltos = por_estado["DEVUELTO"]
    en_transito = por_estado["EN_TRANSITO"]

    # Un certificado en tránsito no está ni usado ni disponible. El faltante
    # (entregado y sin justificar) es lo que queda tras descontar todo lo explicado.
    justificados_o_en_curso = usados_numeros | danados | devueltos | en_transito
    faltantes = sorted(set(range(talonario.serie_desde, talonario.serie_hasta + 1)) - justificados_o_en_curso)

    return {
        "cantidad": talonario.cantidad,
        "usados": len(usados_numeros),
        "danados": len(danados),
        "devueltos": len(devueltos),
        "en_transito": len(en_transito),
        "faltantes": faltantes,
        "faltantes_total": len(faltantes),
    }


def _a_entero(valor):
    """Número impreso como entero, o None si no es puramente numérico."""
    if valor is None:
        return None
    texto = str(valor).strip()
    return int(texto) if texto.isdigit() else None


def numero_fisico(modelo, registro):
    """Solo el número impreso del certificado, o None si no lo trae.

    La deducción de series usa **exclusivamente** el número impreso
    (``numero_certificado`` en defunción, ``numero_planilla`` en nacimiento):
    el ``registro_numero`` legacy es la PK de Oracle y en los certificados
    capturados a mano su sufijo no es la serie física, así que ensuciaría la
    deducción. Los certificados sin número impreso simplemente no participan.
    """
    valor = registro.numero_certificado if modelo is Defuncion else registro.numero_planilla
    return _a_entero(valor)


def _partir_en_series(pares, tolerancia):
    """Parte una lista de ``(numero, fecha)`` en corridas donde el hueco <= tolerancia.

    Devuelve listas consecutivas (la serie no tiene que ser estrictamente
    consecutiva: un certificado usado en otro centro o aún no cargado deja un
    hueco pequeño que la tolerancia puentea).
    """
    series = []
    actual = []
    anterior = None
    for numero, fecha in pares:
        if anterior is not None and numero - anterior > tolerancia:
            series.append(actual)
            actual = []
        actual.append((numero, fecha))
        anterior = numero
    if actual:
        series.append(actual)
    return series


def _redondear_extremos(desde, hasta, usados_referencia, margen):
    """Estira los extremos de una serie hacia el corte de decena más cercano.

    Las asignaciones de libro se reparten en **decenas** (los sub-rangos van de
    «múltiplo de 10 + 1» a «múltiplo de 10»: 601–650, 81–100, 101–500…), pero
    un centro puede no haber agotado su talonario, así que el rango *observado*
    suele quedarse corto por arriba. Aquí cada extremo se estira como mucho
    ``margen`` números hacia ese corte, y **nunca** sobre un número que ya
    sabemos usado (por otro centro o por otra corrida del mismo centro): si el
    corte pertenece al vecino, el estirón se cancela.
    """
    if margen <= 0:
        return desde, hasta
    inicio = (desde - 1) // 10 * 10 + 1
    if desde - inicio <= margen and all(
        n not in usados_referencia for n in range(inicio, desde)
    ):
        desde = inicio
    fin = (hasta + 9) // 10 * 10
    if fin - hasta <= margen and all(
        n not in usados_referencia for n in range(hasta + 1, fin + 1)
    ):
        hasta = fin
    return desde, hasta


def series_deducidas(modelo, tolerancia=10, min_usados=3, densidad_minima=0.5,
                     organizaciones=None, anio=None, margen_redondeo=0):
    """Deduce los talonarios (rango de serie) a partir de los certificados cargados.

    El SISMAI legacy nunca guardó la entrega de talonarios, así que la serie
    entregada se **infiere** de los certificados que la BD sí tiene, por centro:

    - se toman los números **impresos** de cada centro (``numero_fisico``);
    - se ordenan y se parten en corridas donde el hueco entre consecutivos no
      supera ``tolerancia`` (los huecos nacen de certificados usados en otro
      centro del mismo libro o todavía no cargados);
    - cada corrida es una serie candidata ``[min, max]`` con sus certificados
      usados, su extensión y sus fechas.

    Se descartan las series con menos de ``min_usados`` certificados o cuya
    densidad (usados / extensión) quede por debajo de ``densidad_minima``: un
    rango salpicado no es un talonario, es ruido de captura histórica.

    ``organizaciones`` limita a un subconjunto de centros (el alcance del
    usuario); ``anio`` filtra por año del evento. **Es una inferencia**, no un
    dato del legacy: el operario revisa y confirma antes de dar el talonario por
    bueno.

    ``margen_redondeo`` (0 = apagado) estira cada extremo hacia el corte de
    decena más cercano, como mucho ``margen_redondeo`` números, para acercar el
    rango observado a la serie realmente entregada (ver ``_redondear_extremos``).
    El filtro de densidad sigue midiéndose sobre el rango **observado** (para que
    redondear no descarte series); por eso se informan las dos: ``densidad`` es la
    del rango ya redondeado y ``densidad_observada`` la que pasó el filtro.
    """
    campo = "numero_certificado" if modelo is Defuncion else "numero_planilla"
    qs = modelo.objects.filter(organizacion__isnull=False)
    if organizaciones is not None:
        ids = list(organizaciones)
        if not ids:
            return []
        qs = qs.filter(organizacion_id__in=ids)
    if anio:
        qs = qs.filter(fecha_evento__year=anio)

    por_centro = {}
    # Solo hace falta el censo de números usados (de todos los centros) cuando
    # se redondea, porque es lo que impide estirar una serie sobre el vecino.
    usados_referencia = set() if margen_redondeo > 0 else None
    # values_list evita instanciar 600 000 modelos: la deducción recorre la tabla
    # completa y con objetos tardaba ~50 s (aquí baja a unos pocos segundos).
    filas = qs.values_list("organizacion_id", campo, "fecha_evento")
    for centro_id, numero, fecha in filas.iterator():
        entero = _a_entero(numero)
        if entero is None:
            continue
        por_centro.setdefault(centro_id, []).append((entero, fecha))
        if usados_referencia is not None:
            usados_referencia.add(entero)

    nombres = dict(
        Organizacion.objects.filter(id__in=list(por_centro)).values_list("id", "nombre")
    )

    candidatas = []
    for centro_id, pares in por_centro.items():
        pares.sort(key=lambda p: p[0])
        for corrida in _partir_en_series(pares, tolerancia):
            usados = len(corrida)
            if usados < min_usados:
                continue
            numeros = [n for n, _ in corrida]
            desde_obs, hasta_obs = numeros[0], numeros[-1]
            extension_obs = hasta_obs - desde_obs + 1
            densidad_obs = round(usados / extension_obs, 2)
            if densidad_obs < densidad_minima:
                continue
            desde, hasta = _redondear_extremos(
                desde_obs, hasta_obs, usados_referencia, margen_redondeo
            )
            redondeado = (desde, hasta) != (desde_obs, hasta_obs)
            extension = hasta - desde + 1
            fechas = [f for _, f in corrida]
            candidatas.append({
                "centro_id": centro_id,
                "centro": nombres.get(centro_id, ""),
                "serie_desde": desde,
                "serie_hasta": hasta,
                "usados": usados,
                "extension": extension,
                "densidad": round(usados / extension, 2),
                "densidad_observada": densidad_obs,
                "serie_desde_observada": desde_obs,
                "serie_hasta_observada": hasta_obs,
                "redondeado": redondeado,
                "fecha_desde": str(min(fechas)),
                "fecha_hasta": str(max(fechas)),
            })

    candidatas.sort(key=lambda c: (c["centro"], c["serie_desde"]))
    return candidatas


def detalle_certificados(talonario, usados=None):
    """Una fila por certificado de la serie, con su estatus y su persona si está usado."""
    if usados is None:
        usados = certificados_usados(talonario)
    modelo = MODELO_POR_TIPO[talonario.tipo]
    novedades = {n.numero: n for n in talonario.novedades.all()}

    filas = []
    for numero in range(talonario.serie_desde, talonario.serie_hasta + 1):
        registro = usados.get(numero)
        novedad = novedades.get(numero)
        if registro is not None:
            nombres, apellidos, persona = persona_registro(modelo, registro)
            filas.append({
                "numero": numero,
                "estatus": "CARGADO",
                "nombres": nombres,
                "apellidos": apellidos,
                "persona": persona,
                "fecha": str(registro.fecha_evento),
                "registro_id": registro.id,
                "registro_numero": registro.registro_numero,
            })
        elif novedad is not None:
            filas.append({
                "numero": numero,
                "estatus": novedad.estado,
                "nombres": novedad.transitado_nombres,
                "apellidos": novedad.transitado_apellidos,
                "fecha": str(novedad.fecha_salio_centro or novedad.justificacion_fecha or ""),
                "justificacion_numero": novedad.justificacion_numero,
                "observaciones": novedad.observaciones,
            })
        else:
            filas.append({
                "numero": numero,
                "estatus": "SIN_ASIGNAR",
                "nombres": "",
                "apellidos": "",
                "fecha": "",
            })
    return filas
