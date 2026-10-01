from django.urls import path

from . import views

urlpatterns = [
    path("talonarios/", views.TalonariosView.as_view()),
    path("talonarios/<int:pk>/", views.TalonarioDetalleView.as_view()),
    path("talonarios/<int:pk>/certificados/", views.TalonarioCertificadosView.as_view()),
    path("novedades/", views.NovedadesView.as_view()),
    path("novedades/<int:pk>/", views.NovedadDetalleView.as_view()),
    path("reportes/certificados/", views.ReporteCertificadosView.as_view()),
    path("reportes/pendientes/", views.ReportePendientesView.as_view()),
]
