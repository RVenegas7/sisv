"""API de registradores civiles y sus vigencias (§24.2).

Escribe quien `puede_despachar` (Jefe de Unidad / Director / superusuario); leer,
cualquier usuario autenticado. El alcance de los registros civiles sigue el
mismo criterio que el despacho: el centro ve el suyo, la regional los de su
estado, los niveles superiores ven todo.
"""

from datetime import datetime

from django.db.models import ProtectedError, Q
from rest_framework.views import APIView

from registradores.models import DesignacionRegistrador, RegistradorCivil, RegistroCivil
from registradores.serializers import (
    DesignacionRegistradorSerializer,
    RegistradorCivilSerializer,
    RegistroCivilSerializer,
)
from registradores.services import vigentes_en
from seguridad.services import alcance_registros, permisos_de
from sisv_backend.api import error, ok


def _denegar():
    return error("No tiene permiso para administrar los registradores civiles.", status=403)


def _puede(request):
    return permisos_de(request.user)["puede_despachar"]


def _por_alcance_registros_civiles(qs, request):
    alc = alcance_registros(request.user)
    if not isinstance(alc, dict):
        return qs
    if alc["tipo"] == "CENTRO":
        return qs.filter(organizacion_id=alc["organizacion_id"])
    if alc["tipo"] == "REGIONAL" and alc.get("estado"):
        estado = alc["estado"]
        return qs.filter(Q(estado=estado) | Q(organizacion__estado=estado))
    return qs


def _por_alcance_designaciones(qs, request):
    alc = alcance_registros(request.user)
    if not isinstance(alc, dict):
        return qs
    if alc["tipo"] == "CENTRO":
        return qs.filter(registro_civil__organizacion_id=alc["organizacion_id"])
    if alc["tipo"] == "REGIONAL" and alc.get("estado"):
        estado = alc["estado"]
        return qs.filter(
            Q(registro_civil__estado=estado) | Q(registro_civil__organizacion__estado=estado)
        )
    return qs


# --------------------------------------------------------------------------
# Registros civiles
# --------------------------------------------------------------------------

class RegistrosCivilesView(APIView):
    def get(self, request):
        qs = RegistroCivil.objects.select_related("organizacion")
        qs = _por_alcance_registros_civiles(qs, request)
        q = request.query_params.get("q", "").strip()
        if q:
            qs = qs.filter(nombre__icontains=q)
        activo = request.query_params.get("activo", "").strip()
        if activo in ("1", "true", "si"):
            qs = qs.filter(activo=True)
        return ok(RegistroCivilSerializer(qs, many=True).data, count=qs.count())

    def post(self, request):
        if not _puede(request):
            return _denegar()
        s = RegistroCivilSerializer(data=request.data or {})
        if not s.is_valid():
            return error("Datos inválidos", s.errors, 400)
        obj = s.save()
        return ok(RegistroCivilSerializer(obj).data, message="Registro civil creado", status=201)


class RegistroCivilDetalleView(APIView):
    def _get(self, pk):
        try:
            return RegistroCivil.objects.select_related("organizacion").get(pk=pk)
        except RegistroCivil.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self._get(pk)
        if obj is None:
            return error("Registro civil no encontrado", status=404)
        return ok(RegistroCivilSerializer(obj).data)

    def patch(self, request, pk):
        return self._actualizar(request, pk, parcial=True)

    def put(self, request, pk):
        return self._actualizar(request, pk, parcial=False)

    def _actualizar(self, request, pk, parcial):
        if not _puede(request):
            return _denegar()
        obj = self._get(pk)
        if obj is None:
            return error("Registro civil no encontrado", status=404)
        s = RegistroCivilSerializer(obj, data=request.data or {}, partial=parcial)
        if not s.is_valid():
            return error("Datos inválidos", s.errors, 400)
        return ok(RegistroCivilSerializer(s.save()).data, message="Registro civil actualizado")

    def delete(self, request, pk):
        if not _puede(request):
            return _denegar()
        obj = self._get(pk)
        if obj is None:
            return error("Registro civil no encontrado", status=404)
        try:
            obj.delete()
        except ProtectedError:
            return error(
                "No se puede eliminar: tiene designaciones registradas.", status=400
            )
        return ok(message="Registro civil eliminado")


# --------------------------------------------------------------------------
# Registradores (personas)
# --------------------------------------------------------------------------

class RegistradoresView(APIView):
    def get(self, request):
        qs = RegistradorCivil.objects.all()
        q = request.query_params.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(nombres__icontains=q) | Q(apellidos__icontains=q) | Q(cedula__icontains=q)
            )
        activo = request.query_params.get("activo", "").strip()
        if activo in ("1", "true", "si"):
            qs = qs.filter(activo=True)
        return ok(RegistradorCivilSerializer(qs, many=True).data, count=qs.count())

    def post(self, request):
        if not _puede(request):
            return _denegar()
        s = RegistradorCivilSerializer(data=request.data or {})
        if not s.is_valid():
            return error("Datos inválidos", s.errors, 400)
        obj = s.save()
        return ok(RegistradorCivilSerializer(obj).data, message="Registrador creado", status=201)


class RegistradorDetalleView(APIView):
    def _get(self, pk):
        try:
            return RegistradorCivil.objects.get(pk=pk)
        except RegistradorCivil.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self._get(pk)
        if obj is None:
            return error("Registrador no encontrado", status=404)
        return ok(RegistradorCivilSerializer(obj).data)

    def patch(self, request, pk):
        return self._actualizar(request, pk, parcial=True)

    def put(self, request, pk):
        return self._actualizar(request, pk, parcial=False)

    def _actualizar(self, request, pk, parcial):
        if not _puede(request):
            return _denegar()
        obj = self._get(pk)
        if obj is None:
            return error("Registrador no encontrado", status=404)
        s = RegistradorCivilSerializer(obj, data=request.data or {}, partial=parcial)
        if not s.is_valid():
            return error("Datos inválidos", s.errors, 400)
        return ok(RegistradorCivilSerializer(s.save()).data, message="Registrador actualizado")

    def delete(self, request, pk):
        if not _puede(request):
            return _denegar()
        obj = self._get(pk)
        if obj is None:
            return error("Registrador no encontrado", status=404)
        try:
            obj.delete()
        except ProtectedError:
            return error(
                "No se puede eliminar: tiene designaciones registradas. "
                "Desactive al registrador o cierre sus vigencias.",
                status=400,
            )
        return ok(message="Registrador eliminado")


# --------------------------------------------------------------------------
# Designaciones (vigencias)
# --------------------------------------------------------------------------

class DesignacionesView(APIView):
    def get(self, request):
        qs = DesignacionRegistrador.objects.select_related("registro_civil", "registrador")
        qs = _por_alcance_designaciones(qs, request)
        registro_civil = request.query_params.get("registro_civil", "").strip()
        if registro_civil.isdigit():
            qs = qs.filter(registro_civil_id=registro_civil)
        registrador = request.query_params.get("registrador", "").strip()
        if registrador.isdigit():
            qs = qs.filter(registrador_id=registrador)
        cargo = request.query_params.get("cargo", "").strip()
        if cargo:
            qs = qs.filter(cargo=cargo)
        if request.query_params.get("vigente", "").strip() in ("1", "true", "si"):
            qs = qs.filter(hasta__isnull=True)
        return ok(DesignacionRegistradorSerializer(qs, many=True).data, count=qs.count())

    def post(self, request):
        if not _puede(request):
            return _denegar()
        s = DesignacionRegistradorSerializer(data=request.data or {})
        if not s.is_valid():
            return error("Datos inválidos", s.errors, 400)
        obj = s.save(creado_por=request.user)
        return ok(DesignacionRegistradorSerializer(obj).data, message="Designación registrada", status=201)


class DesignacionDetalleView(APIView):
    def _get(self, pk):
        try:
            return DesignacionRegistrador.objects.select_related(
                "registro_civil", "registrador"
            ).get(pk=pk)
        except DesignacionRegistrador.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self._get(pk)
        if obj is None:
            return error("Designación no encontrada", status=404)
        return ok(DesignacionRegistradorSerializer(obj).data)

    def patch(self, request, pk):
        return self._actualizar(request, pk, parcial=True)

    def put(self, request, pk):
        return self._actualizar(request, pk, parcial=False)

    def _actualizar(self, request, pk, parcial):
        if not _puede(request):
            return _denegar()
        obj = self._get(pk)
        if obj is None:
            return error("Designación no encontrada", status=404)
        s = DesignacionRegistradorSerializer(obj, data=request.data or {}, partial=parcial)
        if not s.is_valid():
            return error("Datos inválidos", s.errors, 400)
        return ok(DesignacionRegistradorSerializer(s.save()).data, message="Designación actualizada")

    def delete(self, request, pk):
        if not _puede(request):
            return _denegar()
        obj = self._get(pk)
        if obj is None:
            return error("Designación no encontrada", status=404)
        obj.delete()
        return ok(message="Designación eliminada")


class QuienFirmabaView(APIView):
    """¿Qué registrador(es) estaban vigentes en un registro civil en una fecha?"""

    def get(self, request):
        registro_civil = request.query_params.get("registro_civil", "").strip()
        fecha_txt = request.query_params.get("fecha", "").strip()
        if not registro_civil or not fecha_txt:
            return error("Indique registro_civil y fecha (AAAA-MM-DD).", status=400)
        if not registro_civil.isdigit():
            return error("Registro civil no encontrado", status=404)
        if not RegistroCivil.objects.filter(pk=registro_civil).exists():
            return error("Registro civil no encontrado", status=404)
        try:
            fecha = datetime.strptime(fecha_txt, "%Y-%m-%d").date()
        except ValueError:
            return error("La fecha debe tener el formato AAAA-MM-DD.", status=400)
        vigentes = vigentes_en(registro_civil, fecha)
        return ok({
            "registro_civil": int(registro_civil),
            "fecha": fecha.isoformat(),
            "vigentes": DesignacionRegistradorSerializer(vigentes, many=True).data,
        })
