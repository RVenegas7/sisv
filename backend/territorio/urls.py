from django.urls import path

from . import views

urlpatterns = [
    path("", views.TerritorioView.as_view()),
    path("<int:pk>/ruta/", views.RutaTerritorialView.as_view()),
]