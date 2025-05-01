from django.contrib import admin
from django.contrib.auth import views as auth_views
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
    path("mi_perfil/", views.mi_perfil, name="mi_perfil"),
    path("generar_reporte/", views.generar_reporte, name="generar_reporte"),
    path(
        "cambiar_contrasena/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/password_change_form.html"
        ),
        name="password_change",
    ),
    path(
        "cambiar_contrasena/hecho/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html"
        ),
        name="password_change_done",
    ),
    path("eliminar_cuenta/", views.eliminar_cuenta, name="eliminar_cuenta"),
    path("api/tareas/", views.obtener_tareas, name="api_tareas"),
    path(
        "api/google-calendar/<int:anio>/<int:mes>/",
        views.eventos_google_calendar,
        name="eventos_google_calendar",
    ),
    path("api/crear-tarea/", views.crear_tarea_api, name="crear_tarea_api"),
]
