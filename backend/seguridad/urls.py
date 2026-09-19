from django.urls import path

from . import views

urlpatterns = [
    path("organizaciones/", views.OrganizacionesView.as_view()),
    path("organizaciones/<int:pk>/", views.OrganizacionDetalleView.as_view()),
    path("usuarios/", views.UsuariosView.as_view()),
    path("usuarios/<int:pk>/", views.UsuarioDetalleView.as_view()),
    path("roles/", views.RolesView.as_view()),
    path("auth/login/", views.LoginView.as_view()),
    path("auth/logout/", views.LogoutView.as_view()),
    path("auth/me/", views.MeView.as_view()),
    path("auth/csrf/", views.CsrfView.as_view()),
]