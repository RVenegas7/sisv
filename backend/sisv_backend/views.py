from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template import loader
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from sisv_backend.api import ok

ENDPOINTS = {
    "catalogos": {
        "list": "/api/catalogos/cie10/",
        "search_cie10": "/api/catalogos/cie10/buscar/?q=<texto|codigo>",
        "list_cie11": "/api/catalogos/cie11/",
        "arbol": "/api/catalogos/cie11/arbol/",
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
        "consolidados_resumen": "/api/vigilancia/consolidados/resumen/?anio=",
        "epi15_resumen": "/api/vigilancia/epi15/resumen/?anio=",
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


# ---------------------------------------------------------------------------
# Errores en español
#
# Django responde sus páginas de error en inglés («Not Found», <html lang="en">), y en
# producción el 404/500 se ve tal cual. Aquí se devuelve JSON en español para /api y una
# página corta en español para el resto (el frontend es una SPA, así que el usuario casi
# nunca llega a ellas).
# ---------------------------------------------------------------------------
MENSAJE_404 = "No se encontró lo solicitado."
MENSAJE_500 = "El servidor tuvo un problema al procesar la solicitud. Intente de nuevo en unos minutos."


def _es_api(request):
    return request.path.startswith("/api/")


def handler404(request, exception=None):
    if _es_api(request):
        return JsonResponse({"success": False, "message": MENSAJE_404, "errors": None}, status=404)
    return _pagina(request, "404.html", MENSAJE_404, 404)


def handler500(request):
    if _es_api(request):
        return JsonResponse({"success": False, "message": MENSAJE_500, "errors": None}, status=500)
    return _pagina(request, "500.html", MENSAJE_500, 500)


def _pagina(request, plantilla, mensaje, status):
    try:
        html = loader.get_template(plantilla).render({"mensaje": mensaje}, request)
    except Exception:  # noqa: BLE001 - si falta la plantilla, JSON igual en español
        return JsonResponse({"success": False, "message": mensaje, "errors": None}, status=status)
    return HttpResponse(html, status=status, content_type="text/html; charset=utf-8")


def spa(request):
    """Devuelve el `index.html` del frontend compilado para las rutas del React Router.

    Sin esto, recargar `/productividad` en el contenedor daría 404 (Django no conoce las
    rutas del cliente). En desarrollo esta carpeta no existe y se usa Vite.
    """
    index = getattr(settings, "FRONTEND_DIST", None)
    index = index / "index.html" if index else None
    if index is None or not index.is_file():
        return JsonResponse(
            {
                "success": False,
                "message": (
                    "El frontend no está compilado en el servidor. En desarrollo use Vite "
                    "(npm run dev); en el contenedor, la imagen lo compila al construirla."
                ),
            },
            status=404,
        )
    respuesta = HttpResponse(
        index.read_text(encoding="utf-8"), content_type="text/html; charset=utf-8"
    )
    respuesta["Cache-Control"] = "no-cache"
    return respuesta