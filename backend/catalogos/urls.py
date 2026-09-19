from django.urls import path

from . import views

urlpatterns = [
    path("cie10/", views.CIE10ListView.as_view()),
    path("cie10/buscar/", views.CIE10SearchView.as_view()),
    path("cie10/<int:pk>/", views.CIE10DetailView.as_view()),
    path("cie11/", views.CIE11ListView.as_view()),
    path("cie11/arbol/", views.CIE11ArbolView.as_view()),
    path("cie11/buscar/", views.CIE11SearchView.as_view()),
    path("cie11/<int:pk>/", views.CIE11DetailView.as_view()),
    path("mapeos/", views.MapeoListView.as_view()),
]