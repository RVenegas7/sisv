from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from sisv_backend.api import ok

ENDPOINTS = {
    "catalogos": {
        "list": "/api/catalogos/cie10/",
        "search_cie10": "/api/catalogos/cie10/buscar/?q=<texto|codigo>",
        "list_cie11": "/api/catalogos/cie11/",
        "arbol": "/api/catalogos/cie11/arbol/",
        "ramas": "/api/catalogos/cie11/ramas/?padre=<id>",
        "search_cie11": "/api/catalogos/cie11/buscar/?q=<texto|codigo>",
        "mapeos": "/api/catalogos/mapeos/?cie10=<codigo>&cie11=<id>",
    },
    "registros": {
        "nacimientos": "/api/registros/nacimientos/",
        "nacimientos_detail": "/api/registros/nacimientos/<id>/",
        "nacimientos_stats": "/api/registros/nacimientos/estadisticas/",
        "defunciones": "/api/registros/defunciones/",
        "fichas_vigilancia": "/api/registros/fichas-vigilancia/",
    },
    "vigilancia": {
        "eventos_eno": "/api/vigilancia/eventos-eno/?grupo=&en_epi12=",
        "consolidados": "/api/vigilancia/consolidados/",
        "consolidados_detail": "/api/vigilancia/consolidados/<id>/",
        "consolidados_exportar": "/api/vigilancia/consolidados/exportar/?anio=&semana=&tipo=",
    },
    "territorio": {
        "arbol": "/api/territorio/?nivel=ESTADO|MUNICIPIO|PARROQUIA|COMUNIDAD&padre=<id>",
        "ruta": "/api/territorio/<id>/ruta/",
        "asic": "/api/territorio/asic/?estado=&municipio=&parroquia=&q=",
        "asic_detail": "/api/territorio/asic/<id>/",
    },
    "nota": "Los endpoints de catalogos/registros sirven datos simulados (mock) en memoria; los de vigilancia persisten en PostgreSQL.",
}


class ApiRoot(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return ok(
            ENDPOINTS,
            message="SISV API REST - Sistema Integral de Salud",
            desarrollado_por="Rafael Venegas",
        )