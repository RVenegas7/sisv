from django.contrib import admin
from django.urls import include, path, re_path

from sisv_backend.views import ApiRoot, spa

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", ApiRoot.as_view()),
    path("api/catalogos/", include("catalogos.urls")),
    path("api/registros/", include("registros.urls")),
    path("api/seguridad/", include("seguridad.urls")),
    path("api/auth/", include("seguridad.auth_urls")),
    path("api/territorio/", include("territorio.urls")),
    path("api/vigilancia/", include("vigilancia.urls")),
    path("api/despacho/", include("despacho.urls")),
    path("api/registradores/", include("registradores.urls")),
]

# Frontend compilado: el resto de rutas son del React Router (SPA). Se excluye /api, /admin
# y los archivos estáticos para no taparlos con el index.html. WhiteNoise ya sirve
# /assets/... antes de llegar aquí, pero se excluye también por claridad.
urlpatterns += [
    re_path(r"^(?!api/|admin/|static/|assets/).*$", spa, name="spa"),
]

# Errores en español (Django los sirve en inglés por defecto).
handler404 = "sisv_backend.views.handler404"
handler500 = "sisv_backend.views.handler500"
