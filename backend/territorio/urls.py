from django.urls import path

from . import views

urlpatterns = [
    path("", views.TerritorioView.as_view()),
    path("<int:pk>/ruta/", views.RutaTerritorialView.as_view()),
    path("asic/", views.AsicView.as_view()),
    path("asic/<int:pk>/", views.AsicDetalleView.as_view()),
]