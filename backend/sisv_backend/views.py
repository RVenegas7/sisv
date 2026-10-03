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
        "defunciones": "/api/registros/defunciones/",
        "defunciones_detail": "/api/registros/defunciones/<id>/",
        "fichas_vigilancia": "/api/registros/fichas-vigilancia/",
        "fichas_vigilancia_detail": "/api/registros/fichas-vigilancia/<id>/",
        "codificacion": "/api/registros/codificacion/?modulo=&pendientes=&anio=",
        "dashboard": "/api/registros/dashboard/",
        "reportes": "/api/registros/reportes/",
        "reportes_comparativo": "/api/registros/reportes/comparativo/?anio1=&anio2=",
        "reportes_residentes": "/api/registros/reportes/residentes/",
        "reportes_semanal_mmi": "/api/registros/reportes/semanal-mmi/?anio=&semana=",
        "reportes_exportar": "/api/registros/reportes/exportar/",
        "configuracion": "/api/registros/configuracion/",
    },
    "vigilancia": {
        "eventos_eno": "/api/vigilancia/eventos-eno/?grupo=&en_epi12=",
        "consolidados": "/api/vigilancia/consolidados/",
        "consolidados_detail": "/api/vigilancia/consolidados/<id>/",
        "consolidados_exportar": "/api/vigilancia/consolidados/exportar/?anio=&semana=&tipo=",
        "epi15": "/api/vigilancia/epi15/",
        "epi15_detail": "/api/vigilancia/epi15/<id>/",
        "epi15_exportar": "/api/vigilancia/epi15/exportar/",
    },
    "seguridad": {
        "organizaciones": "/api/seguridad/organizaciones/",
        "organizaciones_detail": "/api/seguridad/organizaciones/<id>/",
        "usuarios": "/api/seguridad/usuarios/",
        "usuarios_detail": "/api/seguridad/usuarios/<id>/",
        "roles": "/api/seguridad/roles/",
    },
    "despacho": {
        "talonarios": "/api/despacho/talonarios/",
        "talonarios_detail": "/api/despacho/talonarios/<id>/",
        "talonario_certificados": "/api/despacho/talonarios/<id>/certificados/",
        "novedades": "/api/despacho/novedades/",
        "reportes_certificados": "/api/despacho/reportes/certificados/",
        "reportes_pendientes": "/api/despacho/reportes/pendientes/",
    },
    "registradores": {
        "registros_civiles": "/api/registradores/registros-civiles/",
        "registradores": "/api/registradores/registradores/",
        "designaciones": "/api/registradores/designaciones/",
        "quien_firmaba": "/api/registradores/quien-firmaba/?registro_civil=&fecha=",
    },
    "territorio": {
        "arbol": "/api/territorio/?nivel=ESTADO|MUNICIPIO|PARROQUIA|COMUNIDAD&padre=<id>",
        "ruta": "/api/territorio/<id>/ruta/",
        "asic": "/api/territorio/asic/?estado=&municipio=&parroquia=&q=",
        "asic_detail": "/api/territorio/asic/<id>/",
    },
    "nota": "Todos los endpoints sirven datos reales persistidos en PostgreSQL (Django ORM); no hay datos simulados en memoria.",
}


class ApiRoot(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return ok(
            ENDPOINTS,
            message="SISV API REST - Sistema Integral de Salud",
            desarrollado_por="Rafael Venegas",
        )