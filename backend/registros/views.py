import csv
import io
from collections import Counter
from datetime import date, timedelta
from statistics import median

from django.db.models import Q, Count, Max
from django.db.models.functions import TruncMonth, ExtractYear, ExtractMonth
from django.db.models.functions import Coalesce
from django.http import HttpResponse, StreamingHttpResponse
from django.utils import timezone
from rest_framework.views import APIView

from sisv_backend.api import error, ok

from .models import ConfiguracionGeneral, Defuncion, FichaVigilancia, Nacimiento
from .presentacion import detalle_certificado
from .serializers import DefuncionSerializer, FichaVigilanciaSerializer, NacimientoSerializer
from .services import (
    muerte_materna_detalle,
    muerte_materna_por_organizacion,
    muerte_materna_por_semana,
    validar_seleccion_cie,
)
from .sugerencia import sugerir
from catalogos.models import CIE10, CIE11, MapeoCIE
from seguridad.models import Organizacion
from vigilancia.models import ConsolidadoSemanal

MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]
from vigilancia.services import (
    rango_anio_epidemiologico,
    rango_semana,
    semana_epidemiologica,
)
from seguridad.services import (
    alcance_registros,
    organizacion_por_defecto,
    permisos_de,
)

NOMBRES_PERMISOS = {
    "puede_escribir": "crear registros",
    "puede_editar": "editar registros",
    "puede_eliminar": "eliminar registros",
    "puede_configurar": "acceder a la configuración general",
    "puede_codificar": "confirmar la codificación CIE",
}

MODELOS = {
    "nacimientos": Nacimiento,
    "defunciones": Defuncion,
    "fichas": FichaVigilancia,
}

SERIALIZADORES = {
    "nacimientos": NacimientoSerializer,
    "defunciones": DefuncionSerializer,
    "fichas": FichaVigilanciaSerializer,
}


def _denegar(permiso):
    return error(f"No tiene permiso para {NOMBRES_PERMISOS[permiso]}.", status=403)


def _por_alcance(qs, request):
    alc = alcance_registros(request.user)
    if not isinstance(alc, dict):
        return qs
    if alc["tipo"] == "CENTRO":
        return qs.filter(organizacion_id=alc["organizacion_id"])
    if alc["tipo"] == "REGIONAL" and alc.get("estado"):
        return qs.filter(estado=alc["estado"])
    return qs


def _consolidados_por_alcance(request):
    """Consolidados semanales de vigilancia según el alcance del usuario."""
    qs = ConsolidadoSemanal.objects.select_related("organizacion", "creado_por").prefetch_related("filas")
    alc = alcance_registros(request.user)
    if isinstance(alc, dict):
        if alc["tipo"] == "CENTRO":
            qs = qs.filter(organizacion_id=alc["organizacion_id"])
        elif alc["tipo"] == "REGIONAL" and alc.get("estado"):
            qs = qs.filter(organizacion__estado=alc["estado"])
    return qs


def _totales_consolidados(qs):
    """Agrega consolidados: total, por tipo/estado/origen y casos acumulados."""
    por_tipo = Counter()
    por_estado = Counter()
    por_origen = Counter()
    casos = 0
    for c in qs:
        por_tipo[c.tipo] += 1
        por_estado[c.estado] += 1
        por_origen[c.origen] += 1
        casos += sum(f.total for f in c.filas.all())
    return {
        "total": len(qs),
        "por_tipo": dict(por_tipo),
        "por_estado": dict(por_estado),
        "por_origen": dict(por_origen),
        "casos": casos,
    }


def _capitulo_cie11(r, mapa):
    if r.cie11_id:
        cap = r.cie11.capitulo
        return cap.titulo if cap else "CIE-11 sin capítulo"
    if r.cie10_id:
        m = mapa.get(r.cie10_id)
        if m is not None and m.cie11_id and m.cie11.capitulo:
            return m.cie11.capitulo.titulo
        return "CIE-10 sin equivalencia"
    return "Sin código"


def _filtros_fecha_estado(qs, desde, hasta, estado):
    if desde:
        qs = qs.filter(fecha_evento__gte=desde)
    if hasta:
        qs = qs.filter(fecha_evento__lte=hasta)
    if estado:
        qs = qs.filter(estado=estado)
    return qs


def _grupo_contar(qs, campo, sin_filtro="Sin dato"):
    """Agrupación {valor: cantidad} hecha en SQL (GROUP BY), no en Python."""
    return {
        (str(v) if v is not None else sin_filtro): n
        for v, n in qs.values(campo).annotate(n=Count("id")).values_list(campo, "n")
    }


def _por_estado_evento(qs):
    """Estado geográfico del registro: el del centro (organización), o el del
    evento cuando la org no está asignada (p. ej. defunciones de domicilio)."""
    return _grupo_contar(
        qs.annotate(estado_evento=Coalesce("organizacion__estado", "estado")), "estado_evento"
    )


def _residentes_otros_estados(qs, estado_evento):
    """Registros ocurridos en ``estado_evento`` con residencia en otro estado,
    agrupados por estado de residencia de mayor a menor."""
    return {
        str(est): n
        for est, n in qs.annotate(estado_evento=Coalesce("organizacion__estado", "estado"))
        .filter(estado_evento=estado_evento)
        .exclude(estado="")
        .exclude(Q(estado=estado_evento))
        .values("estado")
        .annotate(n=Count("id"))
        .order_by("-n")
        .values_list("estado", "n")
    }


def _filtro_anio(anio):
    """Filtro por **año epidemiológico**, no civil.

    El año epidemiológico no coincide con el calendario: la semana 1 de 2026 empieza el
    domingo 04-01-2026 y la 53 de 2025 (28-12-2025 a 03-01-2026) se lleva el 1, 2 y 3 de
    enero. Filtrar por ``fecha_evento__year`` metía en 2025 las ocurridas en la semana 1 de
    2026 y dejaba fuera las de 2026 que pertenecen a la 53 de 2025.
    """
    desde, hasta = rango_anio_epidemiologico(anio)
    return {"fecha_evento__gte": desde, "fecha_evento__lte": hasta}


def _rango_epidemiologico(anio):
    """`(desde, hasta)` del año epidemiológico, para las consultas que no son sobre
    `fecha_evento` sino sobre la fecha del legacy."""
    return rango_anio_epidemiologico(anio)


def _alcance_acotado(user):
    """¿El usuario solo ve parte de los datos (su centro o su estado)?"""
    return isinstance(alcance_registros(user), dict)


def _por_semana(qs):
    """Conteo por semana epidemiológica venezolana {SE: cantidad}.

    Se agrupa por fecha en SQL y la fecha se convierte a semana en Python: la convención
    (``vigilancia.services.semana_epidemiologica``) no es ISO y no se puede expresar con
    ``ExtractWeek``, que es ISO.
    """
    por_fecha = qs.values("fecha_evento").annotate(n=Count("id")).values_list("fecha_evento", "n")
    contador = Counter()
    for fecha_evento, n in por_fecha:
        if fecha_evento:
            contador[semana_epidemiologica(fecha_evento)[1]] += n
    return {int(se): n for se, n in contador.items()}


def _neonatales_por_semana(qs):
    """Muertes neonatales (0-27 días de vida) por semana epidemiológica venezolana."""
    contador = Counter()
    for fecha_evento, fecha_nacimiento in (
        qs.filter(fecha_nacimiento__isnull=False).values_list("fecha_evento", "fecha_nacimiento")
    ):
        if fecha_evento and fecha_nacimiento and 0 <= (fecha_evento - fecha_nacimiento).days <= 27:
            contador[semana_epidemiologica(fecha_evento)[1]] += 1
    return {int(se): n for se, n in contador.items()}


def contar_neonatales(qs):
    """Total de muertes neonatales (0-27 días de vida) en el queryset."""
    total = 0
    for fecha_evento, fecha_nacimiento in (
        qs.filter(fecha_nacimiento__isnull=False).values_list("fecha_evento", "fecha_nacimiento")
    ):
        if fecha_evento and fecha_nacimiento and 0 <= (fecha_evento - fecha_nacimiento).days <= 27:
            total += 1
    return total


def _mortalidad_materno_infantil(request, qs_def, filtro):
    """MM y MN del tablero.

    **MM sale del registro de investigación de la oficina** (`RENGLON_CASOSMM`
    enlazado a `CASOS_MMI`), no de `Defuncion.embarazo_o_puerperio`. Ese campo del
    certificado es un aviso opcional del certificador y lo diligencia en 7 de las
    18 muertes maternas de 2026: contarlo da 7 donde el registro da 18, que es justo
    lo que reportó la responsable de Lara.

    El registro trae establecimiento (`CASOS_MMI."HDOCUMENTO"` → `DOCUMENTO."HORIGEN"`,
    19 centros, todos del árbol Lara), así que **el MM sí se recorta por alcance** igual
    que el MN y que las defunciones.

    El conteo de certificados no se pierde: pasa a `mm_certificadas` con cuántas siguen
    sin CIE, y así la diferencia entre ambos queda a la vista en vez de esconderse
    dentro de un total.
    """
    mm_certificadas = qs_def.filter(embarazo_o_puerperio=True)
    codificadas = mm_certificadas.filter(codificacion_pendiente=False).count()

    por_semana_registro = None
    if filtro:
        por_semana_registro = muerte_materna_por_semana(
            filtro.get("fecha_evento__gte"), filtro.get("fecha_evento__lte"),
            organizaciones=_organizaciones_del_alcance(request),
        )

    # `None` = no se pudo leer el registro legacy.
    # Un dict **vacío** con alcance acotado no es "cero muertes": es que los
    # establecimientos legacy no resolvieron a las organizaciones que el usuario ve
    # (los nombres del legacy, "HOSP. CENTRAL UNIV. DR. ANTONIO MARIA PINEDA", no son
    # los de `Organizacion`, "Hospital Central de Barquisimeto"). Mostrar 0 ahí sería
    # afirmar que el centro no tuvo muertes maternas, que es lo contrario de lo que se
    # sabe, así que en ese caso se cae al certificado, que sí es por centro.
    if por_semana_registro is None or (not por_semana_registro and _alcance_acotado(request.user)):
        mm = mm_certificadas.count()
        fuente = "CERTIFICADO"
    else:
        mm = sum(por_semana_registro.values())
        fuente = "REGISTRO_INVESTIGACION"

    return {
        "mm": mm,
        "mm_fuente": fuente,
        "mm_certificadas": mm_certificadas.count(),
        "mm_codificadas": codificadas,
        "mm_pendientes": mm_certificadas.count() - codificadas,
        "mn": contar_neonatales(qs_def),
    }


def _organizaciones_del_alcance(request):
    """IDs de organización que el usuario puede ver, o `None` si ve todas.

    `None` significa "sin filtro", que es lo que espera
    `muerte_materna_por_organizacion`. Con alcance de centro o regional se traduce el
    alcance a un conjunto de organizaciones para que el MM del registro respete la
    misma frontera que las defunciones.
    """
    alc = alcance_registros(request.user)
    if not isinstance(alc, dict):
        return None
    if alc["tipo"] == "CENTRO":
        return {alc["organizacion_id"]}
    if alc["tipo"] == "REGIONAL" and alc.get("estado"):
        return set(Organizacion.objects.filter(estado=alc["estado"]).values_list("id", flat=True))
    return None


def _fusionar(series):
    """Une series {clave: {modulo: n}} rellenando ceros para todas las claves y módulos."""
    resultado = {}
    claves = set()
    for _m, datos in series:
        claves.update(datos)
        for k, n in datos.items():
            resultado.setdefault(k, {})[_m] = n
    for k in claves:
        for m, _ in series:
            resultado[k].setdefault(m, 0)
    return resultado


def _ordenar_por_clave(series_con_suma):
    return dict(sorted(series_con_suma.items(), key=lambda kv: -sum(kv[1].values())))


def _mensual(qs):
    """Conteo mensual {YYYY-MM: cantidad} con truncamiento de mes en SQL."""
    return {
        f"{mes.year}-{mes.month:02d}": n
        for mes, n in qs.annotate(mes=TruncMonth("fecha_evento"))
        .values("mes")
        .annotate(n=Count("id"))
        .values_list("mes", "n")
        if mes
    }


def _capitulo_por_mapeo(qs):
    """Capítulo CIE-11 unificado (cross-walk) agrupado en SQL.

    - Registros CIE-11: por su capítulo directo.
    - Registros CIE-10: por el capítulo de su equivalencia o «CIE-10 sin equivalencia».
    - Sin código: «Sin código».
    """
    resultado = {}
    for titulo, n in (
        qs.exclude(cie11=None)
        .values("cie11__capitulo__titulo")
        .annotate(n=Count("id"))
        .values_list("cie11__capitulo__titulo", "n")
    ):
        clave = titulo or "CIE-11 sin capítulo"
        resultado[clave] = resultado.get(clave, 0) + n
    ids = list(qs.exclude(cie10=None).values_list("cie10_id", flat=True).distinct())
    mapa = {}
    for m in MapeoCIE.objects.filter(cie10_id__in=ids).select_related("cie11__capitulo"):
        mapa.setdefault(m.cie10_id, m)
    for c10_id, n in (
        qs.exclude(cie10=None).values("cie10_id").annotate(n=Count("id")).values_list("cie10_id", "n")
    ):
        m = mapa.get(c10_id)
        cap = None
        if m is not None and m.cie11_id and m.cie11.capitulo_id:
            cap = m.cie11.capitulo.titulo
        clave = cap or "CIE-10 sin equivalencia"
        resultado[clave] = resultado.get(clave, 0) + n
    sin_codigo = qs.filter(cie10=None, cie11=None).count()
    if sin_codigo:
        resultado["Sin código"] = resultado.get("Sin código", 0) + sin_codigo
    return resultado


class _RegistroAPI(APIView):
    modelo = None
    serializer = None
    etiqueta = "registro"
    buscar = []
    relaciones = ()

    def _qs(self, request):
        qs = self.modelo.objects.all()
        if self.relaciones:
            qs = qs.select_related(*self.relaciones)
        return _por_alcance(qs, request)

    def _obtener(self, request, pk):
        try:
            return self._qs(request).get(pk=pk)
        except self.modelo.DoesNotExist:
            return None

    def get(self, request, pk=None):
        if pk is not None:
            r = self._obtener(request, pk)
            if r is None:
                return error(f"{self.etiqueta.title()} no encontrado", status=404)
            return ok(self.serializer(r).data)

        qs = self._qs(request)
        q = request.query_params.get("q", "").strip()
        if q:
            cond = None
            for campo in self.buscar:
                c = Q(**{f"{campo}__icontains": q})
                cond = c if cond is None else cond | c
            if cond is not None:
                qs = qs.filter(cond)
        lote = request.query_params.get("lote", "").strip()
        if lote:
            qs = qs.filter(lote_id=lote)
        version = request.query_params.get("version", "").strip().upper()
        if version:
            qs = qs.filter(version_cie=version)
        pendientes = request.query_params.get("pendientes", "").strip()
        if pendientes and pendientes.lower() in ("1", "true", "si"):
            qs = qs.filter(codificacion_pendiente=True)
        anio = request.query_params.get("anio", "").strip()
        if anio and anio.lower() != "todos":
            try:
                qs = qs.filter(**_filtro_anio(int(anio)))
            except ValueError:
                pass
        qs = qs.order_by("-fecha_evento", "-creado_en")
        try:
            pagina = max(1, int(request.query_params.get("pagina", 1)))
            por_pagina = min(500, max(1, int(request.query_params.get("por_pagina", 100))))
        except (TypeError, ValueError):
            pagina, por_pagina = 1, 100
        total = qs.count()
        inicio = (pagina - 1) * por_pagina
        lote = list(qs[inicio : inicio + por_pagina])
        return ok(
            self.serializer(lote, many=True).data,
            count=total,
            pagination={
                "pagina": pagina,
                "por_pagina": por_pagina,
                "total": total,
                "paginas": (total + por_pagina - 1) // por_pagina,
            },
        )

    def post(self, request):
        if not permisos_de(request.user)["puede_escribir"]:
            return _denegar("puede_escribir")
        datos = request.data or {}
        s = self.serializer(data=datos)
        if not s.is_valid():
            return error("Datos inválidos", s.errors, 400)
        obj = s.save(organizacion_id=organizacion_por_defecto(request.user, datos))
        return ok(self.serializer(obj).data, message=f"{self.etiqueta.title()} creado", status=201)

    def put(self, request, pk):
        return self._actualizar(request, pk, parcial=False)

    def patch(self, request, pk):
        return self._actualizar(request, pk, parcial=True)

    def _actualizar(self, request, pk, parcial):
        if not permisos_de(request.user)["puede_editar"]:
            return _denegar("puede_editar")
        r = self._obtener(request, pk)
        if r is None:
            return error(f"{self.etiqueta.title()} no encontrado", status=404)
        datos = request.data or {}
        s = self.serializer(r, data=datos, partial=parcial)
        if not s.is_valid():
            return error("Datos inválidos", s.errors, 400)
        alc = alcance_registros(request.user)
        forzar_centro = isinstance(alc, dict) and alc["tipo"] == "CENTRO"
        if "organizacion" in datos or forzar_centro:
            s.save(organizacion_id=organizacion_por_defecto(request.user, datos))
        else:
            s.save()
        return ok(self.serializer(s.instance).data, message=f"{self.etiqueta.title()} actualizado")

    def delete(self, request, pk):
        if not permisos_de(request.user)["puede_eliminar"]:
            return _denegar("puede_eliminar")
        r = self._obtener(request, pk)
        if r is None:
            return error(f"{self.etiqueta.title()} no encontrado", status=404)
        r.delete()
        return ok(None, message=f"{self.etiqueta.title()} eliminado")


class CodificacionView(APIView):
    """Bandeja de codificación: resumen y lista de pendientes por módulo.

    GET /api/registros/codificacion/?modulo=defunciones&q=...&anio=...&pagina=...
    Devuelve {resumen: {defunciones, nacimientos, fichas}, count, items, pagination}.
    La edición del CIE se hace con los PATCH de cada módulo (validan versión por fecha).
    """

    def get(self, request):
        resumen = {}
        for clave, modelo in MODELOS.items():
            qs = _por_alcance(modelo.objects.filter(codificacion_pendiente=True), request)
            resumen[clave] = qs.count()

        modulo = (request.query_params.get("modulo", "defunciones") or "defunciones").strip().lower()
        if modulo not in MODELOS:
            return error(f"Módulo no válido: {modulo}", status=400)
        qs = MODELOS[modulo].objects.select_related("organizacion").filter(codificacion_pendiente=True)
        qs = _por_alcance(qs, request)
        q = request.query_params.get("q", "").strip()
        if q:
            condiciones = []
            if modulo == "defunciones":
                condiciones = [
                    Q(registro_numero__icontains=q),
                    Q(fallecido_nombres__icontains=q),
                    Q(fallecido_apellidos__icontains=q),
                ]
            elif modulo == "nacimientos":
                condiciones = [
                    Q(registro_numero__icontains=q),
                    Q(madre_nombres__icontains=q),
                    Q(madre_apellidos__icontains=q),
                ]
            else:
                condiciones = [
                    Q(codigo_notificacion__icontains=q),
                    Q(paciente_nombres__icontains=q),
                    Q(paciente_apellidos__icontains=q),
                ]
            cond = condiciones[0]
            for cc in condiciones[1:]:
                cond |= cc
            qs = qs.filter(cond)
        anio = request.query_params.get("anio", "").strip()
        if anio and anio.lower() != "todos":
            try:
                qs = qs.filter(**_filtro_anio(int(anio)))
            except ValueError:
                pass
        qs = qs.order_by("-fecha_evento", "-creado_en")
        try:
            pagina = max(1, int(request.query_params.get("pagina", 1)))
            por_pagina = min(200, max(1, int(request.query_params.get("por_pagina", 50))))
        except (TypeError, ValueError):
            pagina, por_pagina = 1, 50
        total = qs.count()
        inicio = (pagina - 1) * por_pagina
        lote = list(qs[inicio : inicio + por_pagina])
        serializer = SERIALIZADORES[modulo]
        return ok(
            serializer(lote, many=True).data,
            count=total,
            resumen=resumen,
            pagination={
                "pagina": pagina,
                "por_pagina": por_pagina,
                "total": total,
                "paginas": (total + por_pagina - 1) // por_pagina,
            },
        )


_CAMPO_NUMERO = {
    "defunciones": "registro_numero",
    "nacimientos": "registro_numero",
    "fichas": "codigo_notificacion",
}


def _resolver_certificado(modulo, numero, request):
    """Busca un certificado por su número exacto respetando el alcance.

    Devuelve ``(registro, None)`` o ``(None, respuesta_de_error)``. El número es el
    `registro_numero` (nacimientos/defunciones) o el `codigo_notificacion` (fichas).
    """
    if modulo not in MODELOS:
        return None, error(f"Módulo no válido: {modulo}", status=400)
    numero = (numero or "").strip()
    if not numero:
        return None, error("Debe indicar el número del certificado.", status=400)
    qs = _por_alcance(
        MODELOS[modulo].objects.select_related("organizacion", "cie10", "cie11", "codificado_por"),
        request,
    )
    campo = _CAMPO_NUMERO[modulo]
    registro = qs.filter(**{f"{campo}__iexact": numero}).order_by("-fecha_evento").first()
    if registro is None:
        return None, error("Certificado no encontrado o fuera de su alcance.", status=404)
    return registro, None


def _cie_por_codigo(version, codigo):
    """Resuelve el objeto CIE de un código del catálogo (subgrupo preferido en CIE-11)."""
    codigo = (codigo or "").strip()
    if not codigo:
        return None
    if version == "CIE10":
        return CIE10.objects.filter(codigo__iexact=codigo).first()
    # Un mismo código CIE-11 puede existir como categoría y como subgrupo; se prefiere
    # el más específico (subgrupo, nivel 4).
    return CIE11.objects.filter(codigo__iexact=codigo).order_by("-nivel").first()


def _guardar_sugerencia(registro, resultado):
    """Persiste la sugerencia para dejar constancia de qué se propuso antes de confirmar."""
    basica = resultado.get("causa_basica") or {}
    registro.sugerencia_codigo = basica.get("codigo", "") or ""
    registro.sugerencia_titulo = (basica.get("titulo", "") or "")[:500]
    registro.sugerencia_origen = resultado.get("origen", "CATALOGO")
    registro.sugerencia_json = resultado
    registro.sugerencia_en = timezone.now()
    registro.save(update_fields=[
        "sugerencia_codigo", "sugerencia_titulo", "sugerencia_origen",
        "sugerencia_json", "sugerencia_en",
    ])


def _sugerencia_actual(registro):
    return {
        "codigo": registro.sugerencia_codigo,
        "titulo": registro.sugerencia_titulo,
        "origen": registro.sugerencia_origen,
        "origen_label": registro.get_sugerencia_origen_display() if registro.sugerencia_origen else "",
        "en": registro.sugerencia_en,
        "detalle": registro.sugerencia_json,
    }


class ConsultaCertificadoView(APIView):
    """Consulta un certificado por número: todo lo registrado + la sugerencia CIE.

    GET /api/registros/consulta/?modulo=defunciones&numero=DEF-2026-000003

    Solo lectura: el detalle agrupado lo arma `presentacion.detalle_certificado`. Si el
    certificado aún no está confirmado, se (re)calcula la sugerencia con el catálogo
    local y se guarda, para que quede la constancia de qué se propuso al confirmar.
    """

    def get(self, request):
        modulo = (request.query_params.get("modulo", "defunciones") or "").strip().lower()
        registro, err = _resolver_certificado(modulo, request.query_params.get("numero"), request)
        if err:
            return err
        if not registro.codificado_en:
            _guardar_sugerencia(registro, sugerir(registro))
        serializer = SERIALIZADORES[modulo]
        return ok({
            "modulo": modulo,
            "numero": getattr(registro, _CAMPO_NUMERO[modulo]),
            "registro": serializer(registro).data,
            "detalle": detalle_certificado(registro),
            "sugerencia": _sugerencia_actual(registro),
            "puede_codificar": permisos_de(request.user)["puede_codificar"],
        })


class ConfirmarCodificacionView(APIView):
    """Confirma la codificación CIE de un certificado (rol CODIFICADOR).

    POST /api/registros/consulta/confirmar/
    body: ``{"modulo": "defunciones", "numero": "...", "codigo": "...", "version_cie": "CIE11"}``

    El código debe existir en el catálogo y ser coherente con la fecha del evento
    (misma validación que la captura). Queda la auditoría de quién y cuándo confirmó.
    """

    def post(self, request):
        if not permisos_de(request.user)["puede_codificar"]:
            return _denegar("puede_codificar")
        datos = request.data or {}
        modulo = (datos.get("modulo", "") or "").strip().lower()
        registro, err = _resolver_certificado(modulo, datos.get("numero"), request)
        if err:
            return err

        version = (datos.get("version_cie") or registro.version_cie or "CIE11").strip().upper()
        if version not in ("CIE10", "CIE11"):
            return error("Versión CIE no válida.", status=400)
        cie_obj = _cie_por_codigo(version, datos.get("codigo"))
        if cie_obj is None:
            return error(f"Código {version} no encontrado en el catálogo: {datos.get('codigo')}", status=400)

        nuevo_cie10 = cie_obj if version == "CIE10" else None
        nuevo_cie11 = cie_obj if version == "CIE11" else None
        errores = validar_seleccion_cie(version, nuevo_cie10, nuevo_cie11, registro.fecha_evento)
        if errores:
            return error("No se puede confirmar esa codificación", errores, 400)

        registro.version_cie = version
        registro.cie10 = nuevo_cie10
        registro.cie11 = nuevo_cie11
        registro.confirmar_codificacion(request.user)
        registro.save()

        serializer = SERIALIZADORES[modulo]
        return ok(serializer(registro).data, message="Codificación confirmada")


class NacimientoView(_RegistroAPI):
    modelo = Nacimiento
    serializer = NacimientoSerializer
    etiqueta = "nacimiento"
    buscar = ["registro_numero", "madre_nombres", "madre_apellidos", "nino_nombres"]
    # La residencia habitual de la madre y del padre son cuatro FKs al árbol territorial
    # (EV-25 §23.3); sin esto el listado hace cuatro consultas más por fila.
    relaciones = (
        "organizacion",
        "madre_residencia_parroquia",
        "madre_residencia_comunidad",
        "padre_residencia_parroquia",
        "padre_residencia_comunidad",
    )


class DefuncionView(_RegistroAPI):
    modelo = Defuncion
    serializer = DefuncionSerializer
    etiqueta = "defunción"
    buscar = ["registro_numero", "fallecido_nombres", "fallecido_apellidos"]


class FichaVigilanciaView(_RegistroAPI):
    modelo = FichaVigilancia
    serializer = FichaVigilanciaSerializer
    etiqueta = "ficha de vigilancia"
    buscar = ["codigo_notificacion", "nombre_evento", "paciente_nombres", "paciente_apellidos"]


class DashboardView(APIView):
    @staticmethod
    def _cobertura(request, series, degradados=None):
        """Dice hasta donde llegan los datos y si falta algun mes.

        El tablero se lee como si la informacion fuera completa. Durante la
        recuperacion de la ventana de septiembre NO lo es: hay meses sin una sola
        fila en medio de la serie. Un grafico asi no avisa de nada, asi que se
        calcula el hueco y se devuelve para que el frontend lo muestre.

        Un mes "vacio" no siempre es un error: antes de que arrancara la captura no
        habia nada, y el mes en curso va atrasado por definicion. Por eso solo se
        marcan los meses YA TERMINADOS que quedan entre el primero y el ultimo mes
        con datos, que es donde un hueco significa de verdad que faltaron registros.
        """
        hoy = date.today()
        etiquetas = {"nacimientos": "Nacimientos", "defunciones": "Defunciones", "fichas": "Vigilancia"}
        por_modulo = {}
        # Un solo conjunto de meses para los tres modulos: un hueco en los tres a la
        # vez es un corte de captura, no que falte un tipo de registro.
        meses_con_datos = set()

        for clave, qs in series:
            ultima = qs.aggregate(m=Max("fecha_evento"))["m"]
            por_modulo[clave] = {
                "etiqueta": etiquetas[clave],
                "ultima_fecha": ultima.isoformat() if ultima else None,
                "atraso_dias": (hoy - ultima).days if ultima else None,
                "total": qs.count(),
            }
            for anio_m, mes_m in (
                qs.annotate(a=ExtractYear("fecha_evento"), m=ExtractMonth("fecha_evento"))
                  .values_list("a", "m").distinct()
            ):
                if anio_m and mes_m:
                    meses_con_datos.add((anio_m, mes_m))

        huecos = []
        if len(meses_con_datos) > 1:
            primero, ultimo = min(meses_con_datos), max(meses_con_datos)
            anio, m = primero
            while (anio, m) <= ultimo:
                # El mes en curso no se marca: a mitad de mes siempre esta a medias.
                if (anio, m) < (hoy.year, hoy.month) and (anio, m) not in meses_con_datos:
                    etiqueta_mes = MESES_ES[m - 1] if 1 <= m <= 12 else str(m)
                    huecos.append(f"{etiqueta_mes} de {anio}")
                m += 1
                if m > 12:
                    m = 1
                    anio += 1

        atrasos = {v["atraso_dias"] for v in por_modulo.values() if v["atraso_dias"] is not None}
        peor = max(atrasos) if atrasos else 0
        degradados = degradados or {"por_modulo": {}}
        return {
            "por_modulo": por_modulo,
            "meses_sin_datos": huecos,
            "meses_degradados": degradados,
            "atraso_dias": peor,
            "completo": not huecos and peor <= 45 and not degradados["por_modulo"],
        }

    @staticmethod
    def _en_rango(anio, mes, rango):
        """¿El mes cae dentro del rango (desde, hasta) que se está mirando?"""
        if not rango:
            return True
        desde, hasta = rango
        inicio = date(anio, mes, 1)
        fin = (date(anio + 1, 1, 1) if mes == 12 else date(anio, mes + 1, 1)) - timedelta(days=1)
        return not (fin < desde or inicio > hasta)

    @staticmethod
    def _meses_degradados(series, cfg, rango=None):
        """Marca los meses terminados que caen muy por debajo de lo normal.

        Compara cada mes contra la mediana de los ultimos ``min_meses_historia``
        meses *normales* (los que no cayeron bajo el umbral). Asi una caida
        sostenida no arrastra la referencia hacia abajo y deja de detectarse: la
        base queda anclada al ultimo nivel sano conocido. Un mes se marca como
        degradado si su total queda por debajo de ``factor`` veces esa mediana.

        La referencia se calcula con **toda** la historia en alcance, pero solo se
        reportan los meses que caen dentro de ``rango`` (el año que se esta
        mirando); igual que ``meses_sin_datos``. Es conservador: exige al menos
        ``min_meses_historia`` meses normales antes de marcar nada, ignora el mes
        en curso (siempre va a medias) y se puede desactivar desde
        ``ConfiguracionGeneral``.
        """
        activo = bool(cfg.detectar_meses_degradados)
        factor = float(cfg.factor_mes_degradado or 0.40)
        min_meses = int(cfg.min_meses_historia or 12)
        salida = {
            "activo": activo,
            "factor": factor,
            "min_meses": min_meses,
            "por_modulo": {},
        }
        if not activo:
            return salida

        hoy = date.today()
        for clave, etiqueta, qs in series:
            filas = (
                qs.annotate(a=ExtractYear("fecha_evento"), m=ExtractMonth("fecha_evento"))
                  .values("a", "m").annotate(c=Count("id"))
            )
            conteos = {(f["a"], f["m"]): f["c"] for f in filas if f["a"] and f["m"]}
            if not conteos:
                continue

            normales = []
            meses = []
            anio, mes = min(conteos)
            ultimo = max(conteos)
            while (anio, mes) <= ultimo:
                # El mes en curso no se marca: a mitad de mes siempre esta a medias.
                if (anio, mes) != (hoy.year, hoy.month):
                    total = conteos.get((anio, mes), 0)
                    if len(normales) >= min_meses and total < factor * median(normales[-min_meses:]):
                        if DashboardView._en_rango(anio, mes, rango):
                            etiqueta_mes = MESES_ES[mes - 1] if 1 <= mes <= 12 else str(mes)
                            meses.append(f"{etiqueta_mes} de {anio}")
                    else:
                        normales.append(total)
                mes += 1
                if mes > 12:
                    mes = 1
                    anio += 1

            if meses:
                salida["por_modulo"][clave] = {
                    "etiqueta": etiqueta,
                    "meses": meses,
                    "desde": meses[0],
                    "hasta": meses[-1],
                    "total": len(meses),
                }
        return salida

    def get(self, request):
        anio_raw = (request.query_params.get("anio") or "").strip()
        hoy = date.today()
        todos = anio_raw.lower() == "todos"
        anio_activo = hoy.year
        filtro = None
        if anio_raw and not todos:
            try:
                anio_activo = int(anio_raw)
            except ValueError:
                anio_activo = hoy.year
            filtro = _filtro_anio(anio_activo)
        elif not todos:
            filtro = _filtro_anio(hoy.year)

        def _qs(modelo):
            qs = _por_alcance(modelo.objects.all(), request)
            if filtro:
                qs = qs.filter(**filtro)
            return qs

        qs_nac = _qs(Nacimiento)
        qs_def = _qs(Defuncion)
        qs_fic = _qs(FichaVigilancia)

        totales = {
            "nacimientos": qs_nac.count(),
            "defunciones": qs_def.count(),
            "fichas": qs_fic.count(),
        }
        totales["total"] = sum(totales.values())

        por_estado = Counter()
        por_version = Counter()
        for qs in (qs_nac, qs_def, qs_fic):
            por_estado.update(_por_estado_evento(qs))
            por_version.update(_grupo_contar(qs, "version_cie"))
        por_estado = dict(sorted(por_estado.items(), key=lambda kv: -kv[1]))

        series = (
            ("nacimientos", qs_nac),
            ("defunciones", qs_def),
            ("fichas", qs_fic),
        )

        por_semana = {k: v for k, v in _fusionar((m, _por_semana(qs)) for m, qs in series).items()}
        por_centro = _fusionar(
            (m, _grupo_contar(qs, "organizacion__nombre", sin_filtro="Sin centro"))
            for m, qs in series
        )
        por_asic = _fusionar(
            (m, _grupo_contar(qs, "organizacion__asic__nombre", sin_filtro="Sin ASIC"))
            for m, qs in series
        )
        por_centro = _ordenar_por_clave(por_centro)
        por_asic = _ordenar_por_clave(por_asic)

        cons = _consolidados_por_alcance(request)
        if filtro:
            cons = cons.filter(anio=anio_activo)
        consolidados = _totales_consolidados(cons)

        anios = set()
        for qs_ref in (Nacimiento.objects.all(), Defuncion.objects.all(), FichaVigilancia.objects.all()):
            anios.update(
                a for a in qs_ref.annotate(y=ExtractYear("fecha_evento")).values_list("y", flat=True).distinct() if a
            )

        cfg = ConfiguracionGeneral.obtener()
        degradados = self._meses_degradados(
            (
                ("nacimientos", "Nacimientos", _por_alcance(Nacimiento.objects.all(), request)),
                ("defunciones", "Defunciones", _por_alcance(Defuncion.objects.all(), request)),
                ("fichas", "Vigilancia", _por_alcance(FichaVigilancia.objects.all(), request)),
            ),
            cfg,
            None if todos else _rango_epidemiologico(anio_activo),
        )
        cobertura = self._cobertura(
            request,
            (("nacimientos", qs_nac), ("defunciones", qs_def), ("fichas", qs_fic)),
            degradados,
        )

        return ok(
            {
                "anio": anio_activo,
                "todos_anios": todos,
                "anios_disponibles": sorted(anios, reverse=True),
                "cobertura": cobertura,
                "totales": totales,
                "por_estado": por_estado,
                "por_version": por_version,
                "mensual": {
                    "nacimientos": _mensual(qs_nac),
                    "defunciones": _mensual(qs_def),
                    "fichas": _mensual(qs_fic),
                },
                "emitidos": {
                    "certificado_vivo": qs_def.count(),
                    "nacimientos_defunciones": 0,
                },
                "mortalidad_materno_infantil": _mortalidad_materno_infantil(request, qs_def, filtro),
                "nacimientos_salud": {
                    "nacidos_vivos": qs_nac.filter(nacido_vivo=True).count(),
                    "por_sexo": _grupo_contar(qs_nac, "sexo"),
                    "por_tipo_parto": _grupo_contar(qs_nac, "tipo_parto"),
                },
                "vigilancia_salud": {
                    "por_clasificacion": _grupo_contar(qs_fic, "clasificacion"),
                },
                "consolidados_semanales": consolidados,
                "por_semana": dict(sorted(por_semana.items())),
                "por_centro": por_centro,
                "por_asic": por_asic,
            }
        )


class ReportesView(APIView):
    def get(self, request):
        modulo = request.query_params.get("modulo", "").strip()
        desde = request.query_params.get("desde", "").strip()
        hasta = request.query_params.get("hasta", "").strip()
        estado = request.query_params.get("estado", "").strip()

        consolidados = {}
        if not modulo or modulo == "consolidados":
            qs = _consolidados_por_alcance(request)
            if estado:
                qs = qs.filter(organizacion__estado=estado)
            consolidados = _totales_consolidados(qs)

        totales = {}
        por_estado = {}
        por_capitulo = {}
        for m, modelo in MODELOS.items():
            if modulo and m != modulo:
                continue
            qs = _filtros_fecha_estado(_por_alcance(modelo.objects.all(), request), desde, hasta, estado)
            totales[m] = qs.count()
            por_estado[m] = _por_estado_evento(qs)
            por_capitulo[m] = _capitulo_por_mapeo(qs)
        return ok(
            {
                "totales": totales,
                "por_estado": por_estado,
                "por_capitulo_cie11": por_capitulo,
                "consolidados_semanales": consolidados,
            }
        )


class ResidentesOtrosEstadosView(APIView):
    """Nacidos/fallecidos en el estado predeterminado con residencia en otro
    estado, agrupados por estado de residencia (mayor a menor)."""

    def get(self, request):
        desde = request.query_params.get("desde", "").strip()
        hasta = request.query_params.get("hasta", "").strip()
        alc = alcance_registros(request.user)
        estado_evento = (alc.get("estado") if isinstance(alc, dict) else "") or "Lara"
        data = {"estado_evento": estado_evento}
        for modulo, modelo in (("nacimientos", Nacimiento), ("defunciones", Defuncion)):
            qs = _filtros_fecha_estado(_por_alcance(modelo.objects.all(), request), desde, hasta, "")
            data[modulo] = _residentes_otros_estados(qs, estado_evento)
        return ok(data)


class ReporteComparativoView(APIView):
    SERIES = [
        ("nacimientos", "Nacimientos"),
        ("muertes", "Muertes"),
        ("muertes_maternas", "Muertes maternas (MM)"),
        ("muertes_neonatales", "Muertes neonatales (MN)"),
        ("mmi", "Vigilancia materno-infantil (MMI)"),
    ]
    LOTES_MMI = ["LEGACY-MMI", "LEGACY-VIOLENTA"]

    def get(self, request):
        anio1 = int(request.query_params.get("anio1", date.today().year))
        anio2 = int(request.query_params.get("anio2", date.today().year - 1))

        def _serie(anio):
            def contar(modelo, **extra):
                # Filtra por año epidemiológico, no civil: así la
                # semana 53 de 2025 (28-12-2025 a 03-01-2026) se queda en 2025 con el 1-3 de
                # enero adentro, y la semana 1 de 2026 arranca el 04-01.
                qs = _por_alcance(modelo.objects.filter(**_filtro_anio(anio), **extra), request)
                return _por_semana(qs)

            def mm_por_semana():
                """MM del registro de investigación, o del certificado si no se pudo leer.

                `None` es "la fuente legacy no está disponible"; un dict vacío es "ese
                año no hay muertes maternas registradas" y sí es una respuesta válida,
                así que no se puede usar `or` para confundir los dos casos.
                """
                desde, hasta = _rango_epidemiologico(anio)
                registro = muerte_materna_por_semana(
                    desde, hasta, organizaciones=_organizaciones_del_alcance(request))
                return registro if registro is not None else \
                    contar(Defuncion, embarazo_o_puerperio=True)

            return {
                "nacimientos": contar(Nacimiento),
                "muertes": contar(Defuncion),
                "muertes_maternas": mm_por_semana(),
                "muertes_neonatales": _neonatales_por_semana(
                    _por_alcance(Defuncion.objects.filter(**_filtro_anio(anio)), request)
                ),
                "mmi": contar(FichaVigilancia, lote_id__in=self.LOTES_MMI),
            }

        serie1 = _serie(anio1)
        serie2 = _serie(anio2)
        semanas = sorted({int(k) for s in (serie1, serie2) for v in s.values() for k in v})
        semanas = list(range(1, 54)) if semanas else []

        totales = {
            mod: {
                anio1: sum(serie1[mod].values()),
                anio2: sum(serie2[mod].values()),
            }
            for mod, _ in self.SERIES
        }

        return ok(
            {
                "anio1": anio1,
                "anio2": anio2,
                "series": [
                    {
                        "clave": mod,
                        "rotulo": rotulo,
                        "anio1": {sem: serie1[mod].get(sem, 0) for sem in semanas},
                        "anio2": {sem: serie2[mod].get(sem, 0) for sem in semanas},
                    }
                    for mod, rotulo in self.SERIES
                ],
                "semanas": semanas,
                "totales": totales,
            }
        )


def _grupo_edad_anexo(fecha_evento, fecha_nacimiento):
    """Grupo del anexo para una defunción, calculado desde las fechas reales.

    `Defuncion` no guarda la edad: se deriva de `fecha_evento - fecha_nacimiento`. Los
    cortes son los del anexo: neonatal 0-27 días, infantil 28-364 días (menor de un año)
    y 1 a 4 años. Fuera de eso devuelve `None` y la muerte no entra al registro.
    """
    if not fecha_evento or not fecha_nacimiento:
        return None
    dias = (fecha_evento - fecha_nacimiento).days
    if dias < 0:
        return None
    if dias <= 27:
        return "neonatal"
    if dias < 365:
        return "infantil"
    if dias < 5 * 365:
        return "1_4"
    return None


def _edad_unidad_anexo(fecha_evento, fecha_nacimiento):
    """`(edad, unidad)` para la columna Edad del anexo: D=días, M=meses, A=años."""
    if not fecha_evento or not fecha_nacimiento:
        return None, ""
    dias = (fecha_evento - fecha_nacimiento).days
    if dias < 0:
        return None, ""
    if dias <= 27:
        return dias, "D"
    if dias < 365:
        return max(dias // 30, 1), "M"
    return dias // 365, "A"


class ReporteSemanalMMIView(APIView):
    """Registro Semanal de Mortalidad Materna e Infantil (anexo del telegrama).

    Es un **reporte generado**, no un formulario: se arma solo con los certificados de
    nacimiento/defunción y con el registro de investigación de muerte materna. ⚠ El SISV
    no captura el número de partos ni de abortos del servicio de obstetricia (el
    certificado de nacimiento es por recién nacido, no por parto): esas casillas del anexo
    quedan vacías en vez de inventarse.
    """

    NOTA_PARTOS_ABORTOS = (
        "El SISV no registra el número de partos ni de abortos del servicio de obstetricia "
        "(el certificado de nacimiento es por recién nacido, no por parto): esas casillas "
        "del anexo van vacías."
    )

    COLUMNAS = [
        "seccion", "establecimiento", "anio", "semana", "grupo",
        "cedula", "nombres", "apellidos", "edad", "unidad_edad", "sexo",
        "fecha", "residencia", "ocurrencia",
        "nacidos_vivos", "nacidos_muertos", "muertes_maternas",
        "muertes_neonatales", "muertes_infantiles", "muertes_1_4",
    ]

    def get(self, request):
        try:
            anio = int(request.query_params.get("anio") or date.today().year)
            semana = int(request.query_params.get("semana") or "")
        except (TypeError, ValueError):
            return error("Indique año y semana epidemiológica válidos.", status=400)
        if semana < 1:
            return error("Falta la semana epidemiológica.", status=400)

        desde, hasta = rango_semana(anio, semana)
        datos = self._construir(request, anio, semana, desde, hasta)
        if request.query_params.get("formato") == "csv":
            return self._csv(datos)
        return ok(datos)

    def _construir(self, request, anio, semana, desde, hasta):
        organizaciones = _organizaciones_del_alcance(request)
        nombres_org = dict(Organizacion.objects.values_list("id", "nombre"))
        filas = {}

        def fila(org_id):
            clave = org_id or 0
            return filas.setdefault(clave, {
                "organizacion_id": org_id or None,
                "organizacion_nombre": nombres_org.get(org_id, "Sin establecimiento identificado"),
                "nacimientos": 0, "nacidos_vivos": 0, "nacidos_muertos": 0,
                "muertes_maternas": 0, "mm_fuente": "REGISTRO_INVESTIGACION",
                "mm_certificadas": 0,
                "muertes_neonatales": 0, "muertes_infantiles": 0, "muertes_1_4": 0,
                "detalle_materna": [], "detalle_infantil": [],
            })

        nac = _por_alcance(
            Nacimiento.objects.filter(fecha_evento__gte=desde, fecha_evento__lte=hasta), request)
        for org_id, total, vivos in (
            nac.values("organizacion_id")
            .annotate(total=Count("id"), vivos=Count("id", filter=Q(nacido_vivo=True)))
            .values_list("organizacion_id", "total", "vivos")
        ):
            f = fila(org_id)
            f["nacimientos"] += total
            f["nacidos_vivos"] += vivos
            f["nacidos_muertos"] += total - vivos

        defs = _por_alcance(
            Defuncion.objects.filter(fecha_evento__gte=desde, fecha_evento__lte=hasta), request)
        for d in defs.values(
            "organizacion_id", "fecha_evento", "fecha_nacimiento",
            "fallecido_nombres", "fallecido_apellidos", "sexo",
            "estado", "municipio", "parroquia",
        ):
            grupo = _grupo_edad_anexo(d["fecha_evento"], d["fecha_nacimiento"])
            if grupo is None:
                continue
            f = fila(d["organizacion_id"])
            if grupo == "neonatal":
                f["muertes_neonatales"] += 1
            if grupo in ("neonatal", "infantil"):
                f["muertes_infantiles"] += 1
            else:
                f["muertes_1_4"] += 1
            edad, unidad = _edad_unidad_anexo(d["fecha_evento"], d["fecha_nacimiento"])
            f["detalle_infantil"].append({
                "grupo": grupo,
                "nombres": (d["fallecido_nombres"] or "").strip(),
                "apellidos": (d["fallecido_apellidos"] or "").strip(),
                "fecha": d["fecha_evento"].isoformat() if d["fecha_evento"] else "",
                "sexo": d["sexo"],
                "edad": edad,
                "unidad_edad": unidad,
                "residencia": ", ".join(
                    x for x in [d["parroquia"], d["municipio"], d["estado"]] if x),
                "ocurrencia": f["organizacion_nombre"],
            })

        # MM del certificado, siempre: sirve para conciliar aunque el indicador salga del
        # registro de investigación.
        for org_id, n in (
            defs.filter(embarazo_o_puerperio=True)
            .values("organizacion_id").annotate(n=Count("id"))
            .values_list("organizacion_id", "n")
        ):
            fila(org_id)["mm_certificadas"] = n

        registro = muerte_materna_por_organizacion(desde, hasta, organizaciones)
        if registro is None:
            for f in filas.values():
                f["mm_fuente"] = "CERTIFICADO"
                f["muertes_maternas"] = f["mm_certificadas"]
        else:
            for org_id, por_semana in registro.items():
                cantidad = por_semana.get(semana, 0)
                if cantidad:
                    fila(org_id)["muertes_maternas"] = cantidad
            for caso in muerte_materna_detalle(desde, hasta, organizaciones) or []:
                f = fila(caso["organizacion_id"])
                f["detalle_materna"].append({
                    "nacionalidad": caso["nacionalidad"],
                    "cedula": caso["cedula"],
                    "nombres": caso["nombres"],
                    "apellidos": caso["apellidos"],
                    "edad": caso["edad"],
                    "unidad_edad": caso["unidad_edad"] or "A",
                    "fecha": caso["fecha"],
                    "residencia": caso["residencia"],
                    "residencia_ubicacion": caso["residencia_ubicacion"],
                    "residencia_pais": caso["residencia_pais"] or 0,
                    "ocurrencia": f["organizacion_nombre"],
                })

        alc = alcance_registros(request.user)
        if isinstance(alc, dict) and alc["tipo"] == "CENTRO":
            fila(alc["organizacion_id"])

        centros = sorted(
            filas.values(),
            key=lambda f: (f["organizacion_id"] is None, f["organizacion_nombre"]),
        )
        campos = ["nacimientos", "nacidos_vivos", "nacidos_muertos", "muertes_maternas",
                  "muertes_neonatales", "muertes_infantiles", "muertes_1_4"]
        totales = {campo: sum(c[campo] for c in centros) for campo in campos}
        totales["mm_certificadas"] = sum(c["mm_certificadas"] for c in centros)

        return {
            "anio": anio,
            "semana": semana,
            "desde": desde.isoformat(),
            "hasta": hasta.isoformat(),
            "nota_partos_abortos": self.NOTA_PARTOS_ABORTOS,
            "centros": centros,
            "totales": totales,
        }

    def _csv(self, datos):
        def generar():
            buffer = io.StringIO()
            escritor = csv.DictWriter(buffer, fieldnames=self.COLUMNAS)
            escritor.writeheader()
            yield "\ufeff" + buffer.getvalue()
            buffer.seek(0)
            buffer.truncate(0)
            resumen = {
                "seccion": "RESUMEN",
                "anio": datos["anio"], "semana": datos["semana"],
            }
            for c in datos["centros"]:
                escritor.writerow({
                    **resumen,
                    "establecimiento": c["organizacion_nombre"],
                    "nacidos_vivos": c["nacidos_vivos"],
                    "nacidos_muertos": c["nacidos_muertos"],
                    "muertes_maternas": c["muertes_maternas"],
                    "muertes_neonatales": c["muertes_neonatales"],
                    "muertes_infantiles": c["muertes_infantiles"],
                    "muertes_1_4": c["muertes_1_4"],
                })
            for c in datos["centros"]:
                for d in c["detalle_materna"]:
                    escritor.writerow({
                        **resumen, "seccion": "MATERNA",
                        "establecimiento": c["organizacion_nombre"],
                        "cedula": d["cedula"], "nombres": d["nombres"],
                        "apellidos": d["apellidos"], "edad": d["edad"],
                        "unidad_edad": d["unidad_edad"], "fecha": d["fecha"],
                        "residencia": d["residencia"], "ocurrencia": d["ocurrencia"],
                    })
            for c in datos["centros"]:
                for d in c["detalle_infantil"]:
                    escritor.writerow({
                        **resumen, "seccion": "INFANTIL",
                        "establecimiento": c["organizacion_nombre"],
                        "grupo": d["grupo"], "nombres": d["nombres"],
                        "apellidos": d["apellidos"], "edad": d["edad"],
                        "unidad_edad": d["unidad_edad"], "sexo": d["sexo"],
                        "fecha": d["fecha"], "residencia": d["residencia"],
                        "ocurrencia": d["ocurrencia"],
                    })
            if buffer.tell():
                yield buffer.getvalue()

        nombre = f"anexo_mmi_{datos['anio']}_{datos['semana']}.csv"
        respuesta = StreamingHttpResponse(generar(), content_type="text/csv; charset=utf-8")
        respuesta["Content-Disposition"] = f'attachment; filename="{nombre}"'
        return respuesta


class ReportesExportView(APIView):
    COLUMNAS = [
        "modulo", "numero", "fecha_evento", "version_cie", "codigo_cie", "capitulo_cie11", "sexo",
        "estado", "municipio", "parroquia", "establecimiento", "organizacion",
    ]

    def get(self, request):
        modulo = request.query_params.get("modulo", "").strip()
        desde = request.query_params.get("desde", "").strip()
        hasta = request.query_params.get("hasta", "").strip()
        estado = request.query_params.get("estado", "").strip()

        def generar():
            buffer = io.StringIO()
            escritor = csv.DictWriter(buffer, fieldnames=self.COLUMNAS)
            escritor.writeheader()
            yield "\ufeff" + buffer.getvalue()
            buffer.seek(0)
            buffer.truncate(0)
            filas_desde = 0
            for m, modelo in MODELOS.items():
                if modulo and m != modulo:
                    continue
                qs = _filtros_fecha_estado(_por_alcance(modelo.objects.all(), request), desde, hasta, estado)
                qs = qs.select_related("cie10", "cie11__capitulo", "organizacion")
                ids = list(qs.exclude(cie10=None).values_list("cie10_id", flat=True).distinct())
                mapa = {}
                for mm in MapeoCIE.objects.filter(cie10_id__in=ids).select_related("cie11__capitulo"):
                    mapa.setdefault(mm.cie10_id, mm)
                for r in qs.iterator():
                    codigo = r.cie10.codigo if r.cie10 else (r.cie11.codigo if r.cie11 else "")
                    numero = getattr(r, "registro_numero", "") or getattr(r, "codigo_notificacion", "") or ""
                    escritor.writerow({
                        "modulo": m,
                        "numero": numero,
                        "fecha_evento": r.fecha_evento.isoformat() if r.fecha_evento else "",
                        "version_cie": r.version_cie,
                        "codigo_cie": codigo,
                        "capitulo_cie11": _capitulo_cie11(r, mapa),
                        "sexo": r.sexo,
                        "estado": r.estado,
                        "municipio": r.municipio,
                        "parroquia": r.parroquia,
                        "establecimiento": r.establecimiento,
                        "organizacion": r.organizacion.nombre if r.organizacion else "",
                    })
                    filas_desde += 1
                    if filas_desde % 5000 == 0:
                        yield buffer.getvalue()
                        buffer.seek(0)
                        buffer.truncate(0)
            if buffer.tell():
                yield buffer.getvalue()

        nombre = f"reporte_sisv_{date.today().isoformat()}.csv"
        respuesta = StreamingHttpResponse(generar(), content_type="text/csv; charset=utf-8")
        respuesta["Content-Disposition"] = f'attachment; filename="{nombre}"'
        return respuesta


class ConfiguracionView(APIView):
    def get(self, request):
        cfg = ConfiguracionGeneral.obtener()
        return ok(
            {
                "estado": cfg.estado,
                "municipio": cfg.municipio,
                "parroquia": cfg.parroquia,
                "establecimiento": cfg.establecimiento,
                "fecha_corte_cie11": cfg.fecha_corte_cie11.isoformat(),
                "organizacion_activa": cfg.organizacion_activa_id,
                "detectar_meses_degradados": cfg.detectar_meses_degradados,
                "factor_mes_degradado": cfg.factor_mes_degradado,
                "min_meses_historia": cfg.min_meses_historia,
                "actualizado_en": cfg.actualizado_en.isoformat() if cfg.actualizado_en else None,
            }
        )

    def put(self, request):
        if not permisos_de(request.user)["puede_configurar"]:
            return _denegar("puede_configurar")
        cfg = ConfiguracionGeneral.obtener()
        datos = request.data or {}
        for campo in ["estado", "municipio", "parroquia", "establecimiento"]:
            if campo in datos and datos[campo] is not None and str(datos[campo]).strip() != "":
                setattr(cfg, campo, datos[campo])
        if datos.get("fecha_corte_cie11") not in (None, ""):
            cfg.fecha_corte_cie11 = date.fromisoformat(str(datos["fecha_corte_cie11"])[:10])
        if datos.get("organizacion_activa") not in (None, ""):
            cfg.organizacion_activa_id = int(datos["organizacion_activa"])
        if "detectar_meses_degradados" in datos and datos["detectar_meses_degradados"] is not None:
            cfg.detectar_meses_degradados = bool(datos["detectar_meses_degradados"])
        if datos.get("factor_mes_degradado") not in (None, ""):
            try:
                factor = float(datos["factor_mes_degradado"])
            except (TypeError, ValueError):
                return error("factor_mes_degradado debe ser un número", status=400)
            if not 0 < factor <= 1:
                return error("factor_mes_degradado debe estar entre 0 y 1", status=400)
            cfg.factor_mes_degradado = factor
        if datos.get("min_meses_historia") not in (None, ""):
            try:
                min_meses = int(datos["min_meses_historia"])
            except (TypeError, ValueError):
                return error("min_meses_historia debe ser un número entero", status=400)
            if min_meses < 3:
                return error("min_meses_historia debe ser al menos 3", status=400)
            cfg.min_meses_historia = min_meses
        cfg.save()
        return ok(
            {
                "estado": cfg.estado,
                "municipio": cfg.municipio,
                "parroquia": cfg.parroquia,
                "establecimiento": cfg.establecimiento,
                "fecha_corte_cie11": cfg.fecha_corte_cie11.isoformat(),
                "organizacion_activa": cfg.organizacion_activa_id,
                "detectar_meses_degradados": cfg.detectar_meses_degradados,
                "factor_mes_degradado": cfg.factor_mes_degradado,
                "min_meses_historia": cfg.min_meses_historia,
            },
            message="Configuración actualizada",
        )
