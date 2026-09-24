from django.urls import path

from . import views

urlpatterns = [
    path("nacimientos/", views.NacimientoView.as_view()),
    path("nacimientos/<int:pk>/", views.NacimientoView.as_view()),
    path("defunciones/", views.DefuncionView.as_view()),
    path("defunciones/<int:pk>/", views.DefuncionView.as_view()),
    path("fichas-vigilancia/", views.FichaVigilanciaView.as_view()),
    path("fichas-vigilancia/<int:pk>/", views.FichaVigilanciaView.as_view()),
    path("dashboard/", views.DashboardView.as_view()),
    path("reportes/", views.ReportesView.as_view()),
    path("reportes/comparativo/", views.ReporteComparativoView.as_view()),
    path("reportes/exportar/", views.ReportesExportView.as_view()),
    path("configuracion/", views.ConfiguracionView.as_view()),
]
