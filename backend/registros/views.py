import csv
import io
from collections import Counter
from datetime import date

from django.db.models import Q
from django.http import HttpResponse
from rest_framework.views import APIView

from sisv_backend.api import error, ok

from .models import ConfiguracionGeneral, Defuncion, FichaVigilancia, Nacimiento
from .serializers import DefuncionSerializer, FichaVigilanciaSerializer, NacimientoSerializer
from catalogos.models import MapeoCIE
from vigilancia.models import ConsolidadoSemanal
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


def _qs_con_detalle(modelo, request):
    return _por_alcance(modelo.objects.all(), request).select_related("cie10", "cie11__capitulo")


def _mapa_mapeos(registros):
    ids = {r.cie10_id for r in registros if r.cie10_id}
    if not ids:
        return {}
    return {
        x.cie10_id: x
        for x in MapeoCIE.objects.filter(cie10_id__in=ids).select_related("cie11__capitulo")
    }


def _capitulo_cie11(r, mapa):
    if r.cie11_id:
        cap = r.cie11.capitulo
        return cap.titulo if cap else "CIE-11 sin capítulo"
    if r.cie10_id:
        m = mapa.get(r.cie10_id)
        if m is not None and m.cie11.capitulo:
            return m.cie11.capitulo.titulo
        return "CIE-10 sin equivalencia"
    return "Sin código"


class _RegistroAPI(APIView):
    modelo = None
    serializer = None
    etiqueta = "registro"
    buscar = []

    def _qs(self, request):
        return _por_alcance(self.modelo.objects.all(), request)

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
        qs = qs.order_by("-fecha_evento", "-creado_en")
        return ok(self.serializer(qs, many=True).data, count=qs.count())

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


class NacimientoView(_RegistroAPI):
    modelo = Nacimiento
    serializer = NacimientoSerializer
    etiqueta = "nacimiento"
    buscar = ["registro_numero", "madre_nombres", "madre_apellidos"]


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
    def get(self, request):
        datos = {
            m: _por_alcance(modelo.objects.all(), request)
            for m, modelo in MODELOS.items()
        }
        mensual = {m: Counter() for m in datos}
        por_estado = Counter()
        por_version = Counter()
        for m, qs in datos.items():
            for r in qs.iterator():
                if r.fecha_evento:
                    mensual[m][r.fecha_evento.strftime("%Y-%m")] += 1
                por_estado[r.estado or "Sin estado"] += 1
                por_version[r.version_cie or "CIE11"] += 1
        por_estado = dict(sorted(por_estado.items(), key=lambda kv: -kv[1]))
        totales = {k: qs.count() for k, qs in datos.items()}
        nac = datos["nacimientos"]
        defs = datos["defunciones"]
        fichas = datos["fichas"]
        return ok(
            {
                "totales": {
                    "total": sum(totales.values()),
                    "nacimientos": totales["nacimientos"],
                    "defunciones": totales["defunciones"],
                    "fichas": totales["fichas"],
                },
                "por_estado": por_estado,
                "por_version": por_version,
                "mensual": mensual,
                "emitidos": {
                    "certificado_vivo": sum(1 for r in defs if getattr(r, "certificado_vivo", True)),
                    "nacimientos_defunciones": sum(1 for r in defs if getattr(r, "feto_muerto", False)),
                },
                "nacimientos_salud": {
                    "nacidos_vivos": sum(1 for r in nac if r.nacido_vivo),
                    "por_sexo": dict(Counter(r.sexo for r in nac)),
                    "por_tipo_parto": dict(Counter(r.tipo_parto for r in nac)),
                },
                "vigilancia_salud": {
                    "por_clasificacion": dict(Counter(r.clasificacion for r in fichas)),
                },
                "consolidados_semanales": _totales_consolidados(_consolidados_por_alcance(request)),
            }
        )


class ReportesView(APIView):
    def get(self, request):
        modulo = request.query_params.get("modulo", "").strip()
        desde = request.query_params.get("desde", "").strip()
        hasta = request.query_params.get("hasta", "").strip()
        estado = request.query_params.get("estado", "").strip()

        provincias = {}
        for m, modelo in MODELOS.items():
            if modulo and m != modulo:
                continue
            for r in _qs_con_detalle(modelo, request).iterator():
                f = r.fecha_evento.isoformat() if r.fecha_evento else ""
                if desde and f < desde:
                    continue
                if hasta and f > hasta:
                    continue
                if estado and (r.estado or "") != estado:
                    continue
                provincias.setdefault(m, []).append(r)
        registros = [r for rs in provincias.values() for r in rs]
        mapa = _mapa_mapeos(registros)
        por_estado = {m: dict(Counter(r.estado or "Sin estado" for r in rs)) for m, rs in provincias.items()}
        por_capitulo = {
            m: dict(Counter(_capitulo_cie11(r, mapa) for r in rs))
            for m, rs in provincias.items()
        }
        consolidados = {}
        if not modulo or modulo == "consolidados":
            qs = _consolidados_por_alcance(request)
            if estado:
                qs = qs.filter(organizacion__estado=estado)
            consolidados = _totales_consolidados(qs)
        return ok(
            {
                "provincias": {
                    m: SERIALIZADORES[m](rs, many=True).data for m, rs in provincias.items()
                },
                "por_estado": por_estado,
                "por_capitulo_cie11": por_capitulo,
                "totales": {m: len(rs) for m, rs in provincias.items()},
                "consolidados_semanales": consolidados,
            }
        )

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

        filas = []
        for m, modelo in MODELOS.items():
            if modulo and m != modulo:
                continue
            for r in _qs_con_detalle(modelo, request).iterator():
                f = r.fecha_evento.isoformat() if r.fecha_evento else ""
                if desde and f < desde:
                    continue
                if hasta and f > hasta:
                    continue
                if estado and (r.estado or "") != estado:
                    continue
                filas.append((m, r))
        mapa = _mapa_mapeos([r for _, r in filas])
        buffer = io.StringIO()
        escritor = csv.DictWriter(buffer, fieldnames=self.COLUMNAS)
        escritor.writeheader()
        for m, r in filas:
            codigo = r.cie10.codigo if r.cie10 else (r.cie11.codigo if r.cie11 else "")
            numero = getattr(r, "registro_numero", "") or getattr(r, "codigo_notificacion", "") or ""
            escritor.writerow({
                "modulo": m,
                "numero": numero,
                "fecha_evento": f,
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
        contenido = "\ufeff" + buffer.getvalue()
        nombre = f"reporte_sisv_{date.today().isoformat()}.csv"
        respuesta = HttpResponse(contenido, content_type="text/csv; charset=utf-8")
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
        cfg.save()
        return ok(
            {
                "estado": cfg.estado,
                "municipio": cfg.municipio,
                "parroquia": cfg.parroquia,
                "establecimiento": cfg.establecimiento,
                "fecha_corte_cie11": cfg.fecha_corte_cie11.isoformat(),
                "organizacion_activa": cfg.organizacion_activa_id,
            },
            message="Configuración actualizada",
        )
