import csv
import io
from datetime import date

from django.http import HttpResponse
from django.utils import timezone
from rest_framework.views import APIView

from sisv_backend.api import error, ok

from seguridad.services import alcance_registros, organizacion_por_defecto, permisos_de
from seguridad.models import Organizacion

from .models import (
    CAMPOS_COLUMNA,
    AlertaEpidemia,
    ConsolidadoEpi15,
    ConsolidadoSemanal,
    EventoENO,
    FilaConsolidado,
    SituacionEspecial,
    columna,
)
from .serializers import (
    AlertaEpidemiaSerializer,
    ConsolidadoEpi15Serializer,
    ConsolidadoSemanalEscribeSerializer,
    ConsolidadoSemanalSerializer,
    EventoENOSerializer,
    FilaConsolidadoSerializer,
    SituacionEspecialSerializer,
)
from .services import sembrar_filas, semana_epidemiologica


NOMBRES_PERMISOS = {
    "puede_escribir": "crear consolidados de vigilancia",
    "puede_editar": "editar consolidados de vigilancia",
    "puede_eliminar": "eliminar consolidados de vigilancia",
}


def _denegar(permiso):
    return error(f"No tiene permiso para {NOMBRES_PERMISOS[permiso]}.", status=403)


def _por_alcance_qs(qs, request):
    alc = alcance_registros(request.user)
    if not isinstance(alc, dict):
        return qs
    if alc["tipo"] == "CENTRO":
        return qs.filter(organizacion_id=alc["organizacion_id"])
    if alc["tipo"] == "REGIONAL" and alc.get("estado"):
        return qs.filter(organizacion__estado=alc["estado"])
    return qs


class EventoENOListView(APIView):
    def get(self, request):
        qs = EventoENO.objects.filter(activo=True)
        grupo = request.query_params.get("grupo", "").strip().upper()
        if grupo:
            qs = qs.filter(grupo=grupo)
        en_epi12 = request.query_params.get("en_epi12", "").strip()
        if en_epi12.lower() in ("1", "true"):
            qs = qs.filter(en_epi12=True)
        en_epi14 = request.query_params.get("en_epi14", "").strip()
        if en_epi14.lower() in ("1", "true"):
            qs = qs.filter(en_epi14=True)
        q = request.query_params.get("q", "").strip()
        if q:
            qs = qs.filter(nombre__icontains=q)
        qs = qs.order_by("orden_epi12", "orden_epi14")
        data = EventoENOSerializer(qs, many=True).data
        return ok(data, count=len(data))


class ConsolidadoSemanalListView(APIView):
    """GET: lista consolidados del usuario; POST: crea cabecera + filas."""

    def get(self, request):
        qs = ConsolidadoSemanal.objects.select_related("organizacion", "creado_por").prefetch_related(
            "filas__evento", "situaciones_especiales", "alertas_epidemias__evento"
        )
        qs = _por_alcance_qs(qs, request)
        anio = request.query_params.get("anio", "").strip()
        semana = request.query_params.get("semana", "").strip()
        tipo = request.query_params.get("tipo", "").strip().upper()
        if anio:
            qs = qs.filter(anio=int(anio))
        if semana:
            qs = qs.filter(semana=int(semana))
        if tipo in ("MORBILIDAD", "MORTALIDAD"):
            qs = qs.filter(tipo=tipo)
        qs = qs.order_by("-anio", "-semana", "tipo")
        data = ConsolidadoSemanalSerializer(qs, many=True).data
        return ok(data, count=qs.count())

    def post(self, request):
        if not permisos_de(request.user)["puede_escribir"]:
            return _denegar("puede_escribir")
        datos = dict(request.data or {})
        org_id = organizacion_por_defecto(request.user, datos)
        if not datos.get("organizacion"):
            if not org_id:
                return error("Debe indicar la organización/establecimiento destino para el consolidado.", status=400)
            datos["organizacion"] = org_id
        org = Organizacion.objects.filter(id=datos["organizacion"]).first()
        if org is not None:
            tiene_dependientes = org.hijos.filter(activo=True).exists()
            datos["origen"] = (
                ConsolidadoSemanal.ORIGEN_PROPIO
                if not tiene_dependientes
                else ConsolidadoSemanal.ORIGEN_CONSOLIDADO
            )
        s = ConsolidadoSemanalEscribeSerializer(data=datos)
        if not s.is_valid():
            return error("Datos inválidos", s.errors, 400)
        filas_enviadas = s.validated_data.pop("filas", None)
        situaciones_enviadas = s.validated_data.pop("situaciones_especiales", None)
        alertas_enviadas = s.validated_data.pop("alertas_epidemias", None)
        consolidado = s.save(
            organizacion_id=org_id,
            creado_por=request.user if request.user.is_authenticated else None,
        )
        if filas_enviadas is not None:
            _reemplazar_filas(consolidado, filas_enviadas)
        elif consolidado.filas.count() == 0:
            sembrar_filas(consolidado)
        if situaciones_enviadas is not None:
            _reemplazar_situaciones(consolidado, situaciones_enviadas)
        if alertas_enviadas is not None:
            _reemplazar_alertas(consolidado, alertas_enviadas)
        consolidado.refresh_from_db()
        return ok(
            ConsolidadoSemanalSerializer(consolidado).data,
            message=f"Consolidado {consolidado.get_tipo_display()} {consolidado.anio}-S{consolidado.semana:02d} creado",
            status=201,
        )


class ConsolidadoSemanalDetailView(APIView):
    def _obtener(self, request, pk):
        qs = ConsolidadoSemanal.objects.select_related("organizacion", "creado_por").prefetch_related(
            "filas__evento", "situaciones_especiales", "alertas_epidemias__evento"
        )
        qs = _por_alcance_qs(qs, request)
        try:
            return qs.get(pk=pk)
        except ConsolidadoSemanal.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self._obtener(request, pk)
        if obj is None:
            return error("Consolidado no encontrado", status=404)
        return ok(ConsolidadoSemanalSerializer(obj).data)

    def patch(self, request, pk):
        if not permisos_de(request.user)["puede_editar"]:
            return _denegar("puede_editar")
        obj = self._obtener(request, pk)
        if obj is None:
            return error("Consolidado no encontrado", status=404)
        nuevo_estado = (request.data or {}).get("estado")
        if obj.estado == ConsolidadoSemanal.ESTADO_CERRADO:
            return error("Un consolidado CERRADO no puede modificarse.")
        if nuevo_estado and nuevo_estado == ConsolidadoSemanal.ESTADO_ENVIADO:
            obj.enviado_en = timezone.now()
        filas = (request.data or {}).pop("filas", None)
        situaciones = (request.data or {}).pop("situaciones_especiales", None)
        alertas = (request.data or {}).pop("alertas_epidemias", None)
        s = ConsolidadoSemanalEscribeSerializer(obj, data=request.data, partial=True)
        if not s.is_valid():
            return error("Datos inválidos", s.errors, 400)
        obj = s.save()
        if filas is not None:
            _reemplazar_filas(obj, filas)
        if situaciones is not None:
            _reemplazar_situaciones(obj, situaciones)
        if alertas is not None:
            _reemplazar_alertas(obj, alertas)
        obj.refresh_from_db()
        return ok(ConsolidadoSemanalSerializer(obj).data, message="Consolidado actualizado")

    def delete(self, request, pk):
        if not permisos_de(request.user)["puede_eliminar"]:
            return _denegar("puede_eliminar")
        obj = self._obtener(request, pk)
        if obj is None:
            return error("Consolidado no encontrado", status=404)
        obj.delete()
        return ok(None, message="Consolidado eliminado")


def _reemplazar_filas(consolidado, filas_payload):
    """Borra las filas actuales y crea las del payload.

    Cada elemento puede tener la forma:
    {'evento': id, 'columnas': {'menor_1_h': 5, …}}
    """
    consolidado.filas.all().delete()
    mapa_campos = {columna(g, s) for g, s in CAMPOS_COLUMNA}
    for item in (filas_payload or []):
        evento_id = item.get("evento")
        columnas = dict(item.get("columnas", {}) or {})
        if columnas.get("edad_ignorada_m"):
            columnas["edad_ignorada_h"] = int(columnas.get("edad_ignorada_h") or 0) + int(columnas.pop("edad_ignorada_m"))
            columnas["edad_ignorada_m"] = 0
        valores = {}
        for nombre in mapa_campos:
            valores[nombre] = max(0, int(columnas.get(nombre, 0) or 0))
        FilaConsolidado.objects.create(
            consolidado=consolidado,
            evento_id=evento_id,
            **valores,
        )


def _reemplazar_situaciones(consolidado, payload):
    consolidado.situaciones_especiales.all().delete()
    for item in (payload or []):
        SituacionEspecial.objects.create(consolidado=consolidado, **{
            k: v for k, v in item.items() if k != "id"
        })


def _reemplazar_alertas(consolidado, payload):
    consolidado.alertas_epidemias.all().delete()
    for item in (payload or []):
        valores = {k: v for k, v in item.items() if k not in ("id", "evento")}
        evento_id = item.get("evento")
        if evento_id:
            valores["evento_id"] = evento_id
        AlertaEpidemia.objects.create(consolidado=consolidado, **valores)


class ConsolidadoSemanalExportView(APIView):
    """Exporta a CSV los consolidados semanales filtrados (respeta alcance)."""

    def get(self, request):
        qs = ConsolidadoSemanal.objects.select_related("organizacion").prefetch_related("filas__evento")
        qs = _por_alcance_qs(qs, request)
        anio = request.query_params.get("anio", "").strip()
        semana = request.query_params.get("semana", "").strip()
        tipo = request.query_params.get("tipo", "").strip().upper()
        if anio:
            qs = qs.filter(anio=int(anio))
        if semana:
            qs = qs.filter(semana=int(semana))
        if tipo in ("MORBILIDAD", "MORTALIDAD"):
            qs = qs.filter(tipo=tipo)

        cabeceras = [
            "organizacion", "anio", "semana", "tipo", "evento", "orden",
            *(columna(g, s) for g, s in CAMPOS_COLUMNA),
            "total_h", "total_m", "total",
        ]
        buffer = io.StringIO()
        escritor = csv.DictWriter(buffer, fieldnames=cabeceras)
        escritor.writeheader()
        for cons in qs.order_by("organizacion__nombre", "anio", "semana", "tipo"):
            for fila in cons.filas.select_related("evento").order_by(
                "evento__orden_epi12", "evento__orden_epi14"
            ):
                registro = {
                    "organizacion": cons.organizacion.nombre if cons.organizacion_id else "",
                    "anio": cons.anio,
                    "semana": cons.semana,
                    "tipo": cons.tipo,
                    "evento": fila.evento.nombre,
                    "orden": fila.evento.orden_epi12 or fila.evento.orden_epi14,
                }
                for g, s in CAMPOS_COLUMNA:
                    registro[columna(g, s)] = getattr(fila, columna(g, s)) or 0
                registro["total_h"] = fila.total_hombres()
                registro["total_m"] = fila.total_mujeres()
                registro["total"] = fila.total
                escritor.writerow(registro)
        contenido = "\ufeff" + buffer.getvalue()
        nombre = f"consolidado_vigilancia_{date.today().isoformat()}.csv"
        respuesta = HttpResponse(contenido, content_type="text/csv; charset=utf-8")
        respuesta["Content-Disposition"] = f'attachment; filename="{nombre}"'
        return respuesta


class Epi15ListView(APIView):
    """GET: lista de consolidados EPI-15 (SIS-04) visibles según alcance."""

    def get(self, request):
        qs = ConsolidadoEpi15.objects.select_related("organizacion").prefetch_related(
            "filas__evento"
        )
        qs = _por_alcance_qs(qs, request)
        anio = request.query_params.get("anio", "").strip()
        semana = request.query_params.get("semana", "").strip()
        if anio:
            qs = qs.filter(anio=int(anio))
        if semana:
            qs = qs.filter(semana=int(semana))
        qs = qs.order_by("-anio", "-semana", "organizacion__nombre")
        data = ConsolidadoEpi15Serializer(qs, many=True).data
        return ok(data, count=qs.count())


class Epi15DetailView(APIView):
    """GET: detalle de un consolidado EPI-15 (cabecera + filas)."""

    def _obtener(self, request, pk):
        qs = ConsolidadoEpi15.objects.select_related("organizacion").prefetch_related(
            "filas__evento"
        )
        qs = _por_alcance_qs(qs, request)
        try:
            return qs.get(pk=pk)
        except ConsolidadoEpi15.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self._obtener(request, pk)
        if obj is None:
            return error("Consolidado EPI-15 no encontrado", status=404)
        return ok(ConsolidadoEpi15Serializer(obj).data)


class Epi15ExportView(APIView):
    """Exporta a CSV los consolidados EPI-15 (respeta alcance)."""

    def get(self, request):
        qs = ConsolidadoEpi15.objects.select_related("organizacion").prefetch_related(
            "filas__evento"
        )
        qs = _por_alcance_qs(qs, request)
        anio = request.query_params.get("anio", "").strip()
        semana = request.query_params.get("semana", "").strip()
        if anio:
            qs = qs.filter(anio=int(anio))
        if semana:
            qs = qs.filter(semana=int(semana))

        cabeceras = ["organizacion", "anio", "semana", "codigo", "evento", "casosp", "casoss", "casosx", "total"]
        buffer = io.StringIO()
        escritor = csv.DictWriter(buffer, fieldnames=cabeceras)
        escritor.writeheader()
        for cons in qs.order_by("organizacion__nombre", "anio", "semana"):
            for fila in cons.filas.select_related("evento").order_by(
                "evento__orden_epi12", "evento__orden_epi14", "nombre_legacy"
            ):
                escritor.writerow({
                    "organizacion": cons.organizacion.nombre if cons.organizacion_id else "",
                    "anio": cons.anio,
                    "semana": cons.semana,
                    "codigo": fila.codigo_legacy,
                    "evento": fila.evento.nombre if fila.evento_id else (fila.nombre_legacy or ""),
                    "casosp": fila.casosp,
                    "casoss": fila.casoss,
                    "casosx": fila.casosx,
                    "total": fila.total,
                })
        contenido = "\ufeff" + buffer.getvalue()
        nombre = f"consolidado_epi15_{date.today().isoformat()}.csv"
        respuesta = HttpResponse(contenido, content_type="text/csv; charset=utf-8")
        respuesta["Content-Disposition"] = f'attachment; filename="{nombre}"'
        return respuesta