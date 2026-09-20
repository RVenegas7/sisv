from rest_framework.views import APIView

from seguridad.services import permisos_de
from sisv_backend.api import error, ok

from .models import ASIC, DivisionTerritorial

NIVELES_VALIDOS = [v for v, _ in DivisionTerritorial.NIVEL_CHOICES]


class TerritorioView(APIView):
    def get(self, request):
        nivel = request.query_params.get("nivel", "").strip().upper()
        padre = int(request.query_params.get("padre", "0") or 0)
        if nivel and nivel not in NIVELES_VALIDOS:
            return error(f"Nivel inválido. Use: {', '.join(NIVELES_VALIDOS)}")
        qs = DivisionTerritorial.objects.filter(activo=True)
        if nivel:
            qs = qs.filter(nivel=nivel)
        if padre:
            qs = qs.filter(padre_id=padre)
        qs = qs.select_related("padre").order_by("nombre")
        return ok(
            [
                {
                    "id": t.id,
                    "nombre": t.nombre,
                    "codigo": t.codigo,
                    "nivel": t.nivel,
                    "nivel_label": t.get_nivel_display(),
                    "padre_id": t.padre_id,
                    "padre_nombre": t.padre.nombre if t.padre else None,
                }
                for t in qs
            ],
            count=len(qs),
        )


class RutaTerritorialView(APIView):
    def get(self, request, pk):
        t = DivisionTerritorial.objects.filter(pk=pk).first()
        if t is None:
            return error("División territorial no encontrada", status=404)
        return ok(t.ruta)


def _serializar_asic(a):
    ub = a.ubicacion()
    return {
        "id": a.id,
        "codigo": a.codigo,
        "nombre": a.nombre,
        "parroquia_id": a.parroquia_id,
        "parroquia": ub["parroquia"],
        "municipio": ub["municipio"],
        "estado": ub["estado"],
        "direccion": a.direccion,
        "responsable": a.responsable,
        "telefono": a.telefono,
        "email": a.email,
        "establecimientos_adscritos": a.establecimientos_adscritos,
        "observaciones": a.observaciones,
        "activo": a.activo,
        "centros": a.organizaciones.filter(activo=True).count(),
    }


class AsicView(APIView):
    def get(self, request):
        qs = ASIC.objects.filter(activo=True).select_related("parroquia__padre__padre").order_by("nombre")
        estado = request.query_params.get("estado", "").strip().lower()
        municipio = request.query_params.get("municipio", "").strip().lower()
        parroquia = request.query_params.get("parroquia", "").strip().lower()
        q = request.query_params.get("q", "").strip()
        if parroquia:
            qs = qs.filter(parroquia__nombre__iexact=parroquia)
        if municipio:
            qs = qs.filter(parroquia__padre__nombre__iexact=municipio)
        if estado:
            qs = qs.filter(parroquia__padre__padre__nombre__iexact=estado)
        ser = [_serializar_asic(a) for a in qs]
        if q:
            ql = q.lower()
            ser = [s for s in ser if ql in s["nombre"].lower() or ql in s["codigo"].lower()]
        return ok(ser, count=len(ser))

    def post(self, request):
        if not permisos_de(request.user)["puede_configurar"]:
            return error("No tiene permiso para administrar los ASIC.", status=403)
        datos = request.data or {}
        codigo = str(datos.get("codigo", "")).strip()
        nombre = str(datos.get("nombre", "")).strip()
        if not codigo or not nombre:
            return error("Código y nombre del ASIC son obligatorios.", status=400)
        if ASIC.objects.filter(codigo=codigo).exists():
            return error("El código ya existe.", {"codigo": "Ya existe un ASIC con este código."}, 400)
        parroquia_id = datos.get("parroquia") or None
        if parroquia_id:
            p = DivisionTerritorial.objects.filter(pk=parroquia_id).first()
            if p is None or p.nivel != DivisionTerritorial.NIVEL_PARROQUIA:
                return error("La sede debe ser una parroquia válida.", status=400)
        asic = ASIC.objects.create(
            codigo=codigo,
            nombre=nombre,
            parroquia_id=parroquia_id,
            direccion=str(datos.get("direccion", "")).strip(),
            responsable=str(datos.get("responsable", "")).strip(),
            telefono=str(datos.get("telefono", "")).strip(),
            email=str(datos.get("email", "")).strip(),
            establecimientos_adscritos=int(datos.get("establecimientos_adscritos", 0) or 0),
            observaciones=str(datos.get("observaciones", "")).strip(),
            activo=bool(datos.get("activo", True)),
        )
        return ok(_serializar_asic(asic), message="ASIC creado", status=201)


class AsicDetalleView(APIView):
    def _obtener(self, pk):
        return ASIC.objects.filter(pk=pk).select_related("parroquia__padre__padre").first()

    def get(self, request, pk):
        a = self._obtener(pk)
        if a is None:
            return error("ASIC no encontrado", status=404)
        return ok(_serializar_asic(a))

    def patch(self, request, pk):
        if not permisos_de(request.user)["puede_configurar"]:
            return error("No tiene permiso para administrar los ASIC.", status=403)
        a = self._obtener(pk)
        if a is None:
            return error("ASIC no encontrado", status=404)
        datos = request.data or {}
        if "parroquia" in datos:
            parroquia_id = datos.get("parroquia") or None
            if parroquia_id:
                p = DivisionTerritorial.objects.filter(pk=parroquia_id).first()
                if p is None or p.nivel != DivisionTerritorial.NIVEL_PARROQUIA:
                    return error("La sede debe ser una parroquia válida.", status=400)
            a.parroquia_id = parroquia_id
        for campo in ["codigo", "nombre", "direccion", "responsable", "telefono", "email", "observaciones"]:
            if campo in datos and datos[campo] is not None:
                setattr(a, campo, str(datos[campo]).strip())
        if "establecimientos_adscritos" in datos and datos["establecimientos_adscritos"] is not None:
            a.establecimientos_adscritos = int(datos["establecimientos_adscritos"])
        if "activo" in datos:
            a.activo = bool(datos["activo"])
        if "codigo" in datos and ASIC.objects.filter(codigo=a.codigo).exclude(pk=a.pk).exists():
            return error("El código ya existe.", {"codigo": "Ya existe un ASIC con este código."}, 400)
        a.save()
        return ok(_serializar_asic(a), message="ASIC actualizado")

    def delete(self, request, pk):
        if not permisos_de(request.user)["puede_configurar"]:
            return error("No tiene permiso para administrar los ASIC.", status=403)
        a = self._obtener(pk)
        if a is None:
            return error("ASIC no encontrado", status=404)
        if a.organizaciones.filter(activo=True).exists():
            return error("No se puede eliminar: tiene centros de salud asociados.", status=400)
        a.delete()
        return ok(None, message="ASIC eliminado")