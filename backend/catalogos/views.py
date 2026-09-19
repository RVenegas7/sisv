from rest_framework.views import APIView

from catalogos.models import CIE10, CIE11, MapeoCIE
from catalogos.serializers import CIE10Serializer, CIE11SlimSerializer
from sisv_backend.api import error, ok


NIVEL_LABEL = {1: "Capítulo", 2: "Bloque", 3: "Categoría", 4: "Subgrupo"}


def _slim(dato):
    item = {
        "id": dato.id,
        "codigo": dato.codigo,
        "titulo": dato.titulo,
        "nivel": dato.nivel,
        "nivel_label": dato.get_nivel_display(),
        "requiere_subgrupo": dato.requiere_subgrupo,
    }
    ruta = []
    x = dato.padre
    while x is not None:
        ruta.append(
            {
                "codigo": x.codigo,
                "titulo": x.titulo,
                "nivel": x.nivel,
                "nivel_label": x.get_nivel_display(),
            }
        )
        x = x.padre
    ruta.reverse()
    item["ruta"] = ruta
    return item


class CIE10ListView(APIView):
    def get(self, request):
        q = request.query_params.get("q", "").strip()
        qs = CIE10.objects.filter(activo=True)
        if q:
            qs = qs.filter(codigo__istartswith=q)
        capitulo = request.query_params.get("capitulo", "").strip()
        if capitulo:
            qs = qs.filter(capitulo__icontains=capitulo)
        data = CIE10Serializer(qs[:200], many=True).data
        return ok(data, count=len(data))


class CIE10SearchView(APIView):
    def get(self, request):
        q = request.query_params.get("q", "").strip()
        if not q:
            return ok([])
        qs = (
            CIE10.objects.filter(activo=True)
            .filter(codigo__istartswith=q)
            .order_by("codigo")[:15]
        )
        if not qs.exists():
            qs = CIE10.objects.filter(activo=True, descripcion__icontains=q).order_by("codigo")[:15]
        return ok(CIE10Serializer(qs, many=True).data)


class CIE10DetailView(APIView):
    def get(self, request, pk):
        obj = CIE10.objects.filter(pk=pk, activo=True).first()
        if obj is None:
            return error("Código CIE-10 no encontrado", status=404)
        return ok(CIE10Serializer(obj).data)


class CIE11ListView(APIView):
    def get(self, request):
        nivel = int(request.query_params.get("nivel", 0) or 0)
        padre = int(request.query_params.get("padre", 0) or 0)
        qs = CIE11.objects.filter(activo=True)
        if nivel:
            qs = qs.filter(nivel=nivel)
        if padre:
            qs = qs.filter(padre_id=padre)
        if nivel == 1:
            return ok([_slim(n) for n in qs.order_by("id")], count=qs.count())
        return ok([_slim(n) for n in qs.order_by("codigo")[:200]], count=qs.count())


class CIE11ArbolView(APIView):
    def get(self, request):
        capitulos = CIE11.objects.filter(activo=True, nivel=1).order_by("id")
        return ok([_slim(n) for n in capitulos], message="Capítulos CIE-11 (hijos se cargan bajo demanda)")


class CIE11SearchView(APIView):
    def get(self, request):
        q = request.query_params.get("q", "").strip()
        if not q:
            return ok([])
        qs = CIE11.objects.filter(activo=True, codigo__istartswith=q).order_by("codigo")[:15]
        if not qs.exists():
            qs = CIE11.objects.filter(activo=True, titulo__icontains=q).order_by("codigo")[:15]
        return ok([_slim(n) for n in qs])


class CIE11DetailView(APIView):
    def get(self, request, pk):
        obj = CIE11.objects.filter(pk=pk, activo=True).first()
        if obj is None:
            return error("Código CIE-11 no encontrado", status=404)
        return ok(_slim(obj))


class MapeoListView(APIView):
    def get(self, request):
        qs = MapeoCIE.objects.select_related("cie10", "cie11").all()
        cie10 = request.query_params.get("cie10", "").strip().upper()
        cie11 = request.query_params.get("cie11", "").strip().upper()
        if cie10:
            qs = qs.filter(cie10__codigo=cie10)
        if cie11:
            qs = qs.filter(cie11__codigo=cie11)
        return ok(
            [
                {
                    "cie10": {"codigo": m.cie10.codigo, "descripcion": m.cie10.descripcion},
                    "cie11": _slim_mapeo(m.cie11),
                    "tipo": m.tipo,
                    "tipo_label": m.get_tipo_display(),
                }
                for m in qs[:200]
            ]
        )


def _slim_mapeo(n):
    return {
        "id": n.id,
        "codigo": n.codigo,
        "titulo": n.titulo,
        "nivel": n.nivel,
        "nivel_label": n.get_nivel_display(),
        "requiere_subgrupo": n.requiere_subgrupo,
    }