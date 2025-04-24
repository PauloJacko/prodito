from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.bienvenida, name="bienvenida"),
    path("home/", views.home, name="home"),
    path("login/google/", views.google_login, name="google_login"),
    path("oauth2callback/", views.oauth2callback, name="oauth2callback"),
    path("crear_cuenta/", views.crear_cuenta, name="crear_cuenta"),
    path("inicio_sesion/", views.inicio_sesion, name="inicio_sesion"),
    path(
        "cerrar_sesion/",
        LogoutView.as_view(next_page="bienvenida"),
        name="cerrar_sesion",
    ),
    path("tareas/", include("tareas.urls")),
    path("api/tareas/", views.obtener_tareas, name="api_tareas"),
    path(
        "api/google-calendar/",
        views.eventos_google_calendar,
        name="eventos_google_calendar",
    ),
]
