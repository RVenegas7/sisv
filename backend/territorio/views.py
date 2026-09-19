from rest_framework.views import APIView

from sisv_backend.api import error, ok

from .models import DivisionTerritorial

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