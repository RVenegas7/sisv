from django.contrib import admin
from django.urls import include, path

from sisv_backend.views import ApiRoot

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", ApiRoot.as_view()),
    path("api/catalogos/", include("catalogos.urls")),
    path("api/registros/", include("registros.urls")),
    path("api/seguridad/", include("seguridad.urls")),
    path("api/auth/", include("seguridad.auth_urls")),
    path("api/territorio/", include("territorio.urls")),
    path("api/vigilancia/", include("vigilancia.urls")),
]