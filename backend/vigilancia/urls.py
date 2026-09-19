from django.urls import path

from . import views

urlpatterns = [
    path("eventos-eno/", views.EventoENOListView.as_view()),
    path("consolidados/", views.ConsolidadoSemanalListView.as_view()),
    path("consolidados/exportar/", views.ConsolidadoSemanalExportView.as_view()),
    path("consolidados/<int:pk>/", views.ConsolidadoSemanalDetailView.as_view()),
]