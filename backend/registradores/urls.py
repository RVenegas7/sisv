from django.urls import path

from . import views

urlpatterns = [
    path("registros-civiles/", views.RegistrosCivilesView.as_view()),
    path("registros-civiles/<int:pk>/", views.RegistroCivilDetalleView.as_view()),
    path("registradores/", views.RegistradoresView.as_view()),
    path("registradores/<int:pk>/", views.RegistradorDetalleView.as_view()),
    path("designaciones/", views.DesignacionesView.as_view()),
    path("designaciones/<int:pk>/", views.DesignacionDetalleView.as_view()),
    path("quien-firmaba/", views.QuienFirmabaView.as_view()),
]
