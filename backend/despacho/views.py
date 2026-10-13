import csv
import io

from django.http import HttpResponse
from rest_framework.views import APIView

from despacho.models import NovedadCertificado, Talonario
from despacho.serializers import NovedadCertificadoSerializer, TalonarioSerializer
from despacho.services import detalle_certificados, persona_registro, resumen_talonario
from registros.models import Defuncion, Nacimiento
from seguridad.models import Organizacion
from seguridad.services import alcance_registros, organizacion_destino_valida, permisos_de
from sisv_backend.api import error, ok

MODELO_POR_TIPO = {
    Talonario.TIPO_NACIMIENTO: Nacimiento,
    Talonario.TIPO_DEFUNCION: Defuncion,
}


def _denegar(permiso="despachar"):
    return error("No tiene permiso para administrar el despacho de certificados.", status=403)


def _por_alcance(qs, request, campo="centro"):
    """Restringe por el alcance del usuario (centro / regional / todos)."""
    alc = alcance_registros(request.user)
    if not isinstance(alc, dict):
        return qs
    if alc["tipo"] == "CENTRO":
        return qs.filter(**{f"{campo}_id": alc["organizacion_id"]})
    if alc["tipo"] == "REGIONAL" and alc.get("estado"):
        return qs.filter(**{f"{campo}__estado": alc["estado"]})
    return qs


def _en_alcance(request, centro_id):
    """Lectura: el centro del talonario está dentro del alcance del usuario.

    Además del caso directo (su centro / su estado), un usuario de centro puede
    leer un talonario entregado a un ancestro (p. ej. la regional), porque el
    cruce de certificados usa el subárbol del centro del talonario.
    """
    if organizacion_destino_valida(request.user, centro_id):
        return True
    alc = alcance_registros(request.user)
    if isinstance(alc, dict) and alc["tipo"] == "CENTRO":
        org = Organizacion.objects.filter(pk=alc["organizacion_id"]).first()
        while org is not None:
            if org.pk == centro_id:
                return True
            org = org.padre
    return False


class TalonariosView(APIView):
    def get(self, request):
        qs = Talonario.objects.select_related("centro").prefetch_related("novedades")
        qs = _por_alcance(qs, request)
        tipo = request.query_params.get("tipo", "").strip()
        if tipo:
            qs = qs.filter(tipo=tipo)
        centro = request.query_params.get("centro", "").strip()
        if centro:
            qs = qs.filter(centro_id=centro)
        anio = request.query_params.get("anio", "").strip()
        if anio and anio.lower() != "todos":
            try:
                qs = qs.filter(fecha_entrega__year=int(anio))
            except ValueError:
                pass
        return ok(TalonarioSerializer(qs, many=True).data, count=qs.count())

    def post(self, request):
        if not permisos_de(request.user)["puede_despachar"]:
            return _denegar()
        datos = dict(request.data or {})
        alc = alcance_registros(request.user)
        if isinstance(alc, dict) and alc["tipo"] == "CENTRO":
            # El centro se fuerza al del usuario.
            datos["centro"] = alc["organizacion_id"]
        if not datos.get("centro"):
            return error(
                "Debe indicar el centro de salud al que se asigna el talonario.",
                {"centro": "Obligatorio."},
                400,
            )
        if not organizacion_destino_valida(request.user, datos["centro"]):
            return error("El centro de salud elegido está fuera de su alcance geográfico.", status=403)
        s = TalonarioSerializer(data=datos)
        if not s.is_valid():
            return error("Datos inválidos", s.errors, 400)
        obj = s.save(creado_por=request.user)
        return ok(TalonarioSerializer(obj).data, message="Talonario registrado", status=201)


class TalonarioDetalleView(APIView):
    def _get(self, pk):
        try:
            return Talonario.objects.select_related("centro").get(pk=pk)
        except Talonario.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self._get(pk)
        if obj is None or not _en_alcance(request, obj.centro_id):
            return error("Talonario no encontrado", status=404)
        return ok(TalonarioSerializer(obj).data)

    def patch(self, request, pk):
        return self._actualizar(request, pk, parcial=True)

    def put(self, request, pk):
        return self._actualizar(request, pk, parcial=False)

    def _actualizar(self, request, pk, parcial):
        if not permisos_de(request.user)["puede_despachar"]:
            return _denegar()
        obj = self._get(pk)
        if obj is None or not _en_alcance(request, obj.centro_id):
            return error("Talonario no encontrado", status=404)
        # La escritura es estricta: solo se modifica el talonario propio (o,
        # en regional, uno de su estado), no el entregado a un ancestro.
        if not organizacion_destino_valida(request.user, obj.centro_id):
            return _denegar()
        datos = dict(request.data or {})
        if "centro" in datos and not organizacion_destino_valida(request.user, datos["centro"]):
            return error("El centro de salud elegido está fuera de su alcance geográfico.", status=403)
        s = TalonarioSerializer(obj, data=datos, partial=parcial)
        if not s.is_valid():
            return error("Datos inválidos", s.errors, 400)
        obj = s.save()
        return ok(TalonarioSerializer(obj).data, message="Talonario actualizado")

    def delete(self, request, pk):
        if not permisos_de(request.user)["puede_despachar"]:
            return _denegar()
        obj = self._get(pk)
        if obj is None or not _en_alcance(request, obj.centro_id):
            return error("Talonario no encontrado", status=404)
        if not organizacion_destino_valida(request.user, obj.centro_id):
            return _denegar()
        obj.delete()
        return ok(message="Talonario eliminado")


class TalonarioCertificadosView(APIView):
    """Detalle certificado por certificado con su estatus (calculado + novedades)."""

    def get(self, request, pk):
        try:
            talonario = Talonario.objects.select_related("centro").get(pk=pk)
        except Talonario.DoesNotExist:
            return error("Talonario no encontrado", status=404)
        if not _en_alcance(request, talonario.centro_id):
            return error("Talonario no encontrado", status=404)
        filas = detalle_certificados(talonario)
        return ok({
            "talonario": TalonarioSerializer(talonario).data,
            "resumen": resumen_talonario(talonario),
            "certificados": filas,
        })


class NovedadesView(APIView):
    def get(self, request):
        qs = NovedadCertificado.objects.select_related("talonario", "talonario__centro")
        qs = _por_alcance(qs, request, campo="talonario__centro")
        talonario = request.query_params.get("talonario", "").strip()
        if talonario:
            qs = qs.filter(talonario_id=talonario)
        estado = request.query_params.get("estado", "").strip()
        if estado:
            qs = qs.filter(estado=estado)
        return ok(NovedadCertificadoSerializer(qs, many=True).data, count=qs.count())

    def post(self, request):
        if not permisos_de(request.user)["puede_despachar"]:
            return _denegar()
        s = NovedadCertificadoSerializer(data=request.data or {})
        if not s.is_valid():
            return error("Datos inválidos", s.errors, 400)
        talonario = s.validated_data.get("talonario")
        if talonario is not None and not organizacion_destino_valida(request.user, talonario.centro_id):
            return error("El talonario está fuera de su alcance geográfico.", status=403)
        obj = s.save()
        return ok(NovedadCertificadoSerializer(obj).data, message="Novedad registrada", status=201)


class NovedadDetalleView(APIView):
    def _get(self, pk):
        try:
            return NovedadCertificado.objects.get(pk=pk)
        except NovedadCertificado.DoesNotExist:
            return None

    def _autorizar(self, request, obj):
        """La novedad solo toca talonarios dentro del alcance del usuario.

        La escritura es estricta (`organizacion_destino_valida`): un centro no
        modifica novedades de un talonario entregado a un ancestro.
        """
        if obj is None or not _en_alcance(request, obj.talonario.centro_id):
            return error("Novedad no encontrada", status=404)
        if not permisos_de(request.user)["puede_despachar"]:
            return _denegar()
        if not organizacion_destino_valida(request.user, obj.talonario.centro_id):
            return _denegar()
        return None

    def patch(self, request, pk):
        obj = self._get(pk)
        denia = self._autorizar(request, obj)
        if denia is not None:
            return denia
        s = NovedadCertificadoSerializer(obj, data=request.data or {}, partial=True)
        if not s.is_valid():
            return error("Datos inválidos", s.errors, 400)
        return ok(NovedadCertificadoSerializer(s.save()).data, message="Novedad actualizada")

    def delete(self, request, pk):
        obj = self._get(pk)
        denia = self._autorizar(request, obj)
        if denia is not None:
            return denia
        obj.delete()
        return ok(message="Novedad eliminada")


def _filas_certificados_cargados(request):
    """Reporte 1: certificados usados, por centro y tipo, con persona y fecha."""
    tipo = request.query_params.get("tipo", "").strip() or Talonario.TIPO_DEFUNCION
    modelo = MODELO_POR_TIPO.get(tipo)
    if modelo is None:
        return None, None, []
    qs = modelo.objects.select_related("organizacion")
    alc = alcance_registros(request.user)
    if isinstance(alc, dict):
        if alc["tipo"] == "CENTRO":
            qs = qs.filter(organizacion_id=alc["organizacion_id"])
        elif alc["tipo"] == "REGIONAL" and alc.get("estado"):
            qs = qs.filter(estado=alc["estado"])
    centro = request.query_params.get("centro", "").strip()
    if centro:
        qs = qs.filter(organizacion_id=centro)
    desde = request.query_params.get("desde", "").strip()
    hasta = request.query_params.get("hasta", "").strip()
    if desde:
        qs = qs.filter(fecha_evento__gte=desde)
    if hasta:
        qs = qs.filter(fecha_evento__lte=hasta)
    qs = qs.order_by("organizacion__nombre", "fecha_evento")

    filas = []
    for r in qs.iterator():
        nombres, apellidos, persona = persona_registro(modelo, r)
        filas.append({
            "numero": r.registro_numero,
            "nombres": nombres,
            "apellidos": apellidos,
            "fecha": str(r.fecha_evento),
            "centro": r.organizacion.nombre if r.organizacion_id else "",
            "persona": persona,
        })
    return tipo, modelo, filas


class ReporteCertificadosView(APIView):
    def get(self, request):
        tipo, _modelo, filas = _filas_certificados_cargados(request)
        if tipo is None:
            return error("Tipo inválido. Use NACIMIENTO o DEFUNCION.", status=400)
        if request.query_params.get("formato", "").lower() == "csv":
            return _csv_certificados(tipo, filas)
        return ok({
            "tipo": tipo,
            "total": len(filas),
            "items": filas,
        })


class ReporteCentrosView(APIView):
    """Reporte por centro: certificados entregados vs regresados (procesados).

    Agrega los talonarios de cada centro (y tipo) dentro del alcance del
    usuario: entregados = suma de `cantidad`; regresados = certificados de la
    serie ya cargados en la BD; el resto (dañado/devuelto/transito/faltante)
    explica lo todavía no procesado.
    """

    def get(self, request):
        qs = Talonario.objects.select_related("centro").prefetch_related("novedades")
        qs = _por_alcance(qs, request)
        tipo = request.query_params.get("tipo", "").strip()
        if tipo:
            qs = qs.filter(tipo=tipo)
        centro = request.query_params.get("centro", "").strip()
        if centro:
            qs = qs.filter(centro_id=centro)
        anio = request.query_params.get("anio", "").strip()
        if anio:
            try:
                qs = qs.filter(fecha_entrega__year=int(anio))
            except ValueError:
                pass

        agregados = {}
        for talonario in qs:
            clave = (talonario.centro_id, talonario.tipo)
            fila = agregados.setdefault(clave, {
                "centro_id": talonario.centro_id,
                "centro": talonario.centro.nombre,
                "tipo": talonario.tipo,
                "tipo_label": talonario.get_tipo_display(),
                "talonarios": 0,
                "entregados": 0,
                "regresados": 0,
                "danados": 0,
                "devueltos": 0,
                "en_transito": 0,
                "faltantes": 0,
            })
            resumen = resumen_talonario(talonario)
            fila["talonarios"] += 1
            fila["entregados"] += resumen["cantidad"]
            fila["regresados"] += resumen["usados"]
            fila["danados"] += resumen["danados"]
            fila["devueltos"] += resumen["devueltos"]
            fila["en_transito"] += resumen["en_transito"]
            fila["faltantes"] += resumen["faltantes_total"]

        filas = sorted(agregados.values(), key=lambda f: (f["centro"], f["tipo"]))
        if request.query_params.get("formato", "").lower() == "csv":
            return _csv_response(
                "despacho_por_centro.csv",
                ["Centro", "Tipo", "Talonarios", "Entregados", "Regresados (procesados)",
                 "Danados", "Devueltos", "En transito", "Faltantes"],
                [[f["centro"], f["tipo_label"], f["talonarios"], f["entregados"], f["regresados"],
                  f["danados"], f["devueltos"], f["en_transito"], f["faltantes"]] for f in filas],
            )
        return ok({"total": len(filas), "items": filas})


class ReportePendientesView(APIView):
    """Reporte 2: certificados entregados y todavía no retornados ni justificados."""

    def get(self, request):
        qs = Talonario.objects.select_related("centro").prefetch_related("novedades")
        qs = _por_alcance(qs, request)
        tipo = request.query_params.get("tipo", "").strip()
        if tipo:
            qs = qs.filter(tipo=tipo)
        centro = request.query_params.get("centro", "").strip()
        if centro:
            qs = qs.filter(centro_id=centro)

        # "Pendiente" = sin asignar (nunca usado) o en tránsito. Dañado y devuelto
        # están justificados; cargado está usado.
        solo_pendientes = request.query_params.get("solo_pendientes", "1").lower() in ("1", "true", "si")

        filas = []
        for talonario in qs:
            detalle = detalle_certificados(talonario)
            for fila in detalle:
                if solo_pendientes and fila["estatus"] not in ("SIN_ASIGNAR", "EN_TRANSITO"):
                    continue
                filas.append({
                    **fila,
                    "tipo": talonario.tipo,
                    "talonario_id": talonario.id,
                    "serie": f"{talonario.serie_desde}-{talonario.serie_hasta}",
                    "centro": talonario.centro.nombre,
                    "centro_id": talonario.centro_id,
                    "fecha_entrega": str(talonario.fecha_entrega),
                    "responsable_recibe": talonario.responsable_recibe,
                })

        if request.query_params.get("formato", "").lower() == "csv":
            return _csv_pendientes(filas)
        return ok({"total": len(filas), "items": filas})


def _csv_response(nombre, cabecera, filas):
    buffer = io.StringIO()
    buffer.write("\ufeff")  # BOM para Excel
    escritor = csv.writer(buffer)
    escritor.writerow(cabecera)
    escritor.writerows(filas)
    respuesta = HttpResponse(buffer.getvalue(), content_type="text/csv; charset=utf-8")
    respuesta["Content-Disposition"] = f'attachment; filename="{nombre}"'
    return respuesta


def _csv_certificados(tipo, filas):
    return _csv_response(
        f"certificados_{tipo.lower()}.csv",
        ["No Certificado", "Persona", "Nombres", "Apellidos", "Fecha", "Centro"],
        [
            [f["numero"], f.get("persona", ""), f["nombres"], f["apellidos"], f["fecha"], f["centro"]]
            for f in filas
        ],
    )


def _csv_pendientes(filas):
    return _csv_response(
        "certificados_pendientes.csv",
        ["Tipo", "No Certificado", "Serie", "Centro", "Fecha entrega", "Estatus",
         "Nombres", "Apellidos", "Fecha", "Justificación"],
        [[f["tipo"], f["numero"], f["serie"], f["centro"], f["fecha_entrega"],
          f["estatus"], f["nombres"], f["apellidos"], f["fecha"],
          f.get("justificacion_numero", "")] for f in filas],
    )
