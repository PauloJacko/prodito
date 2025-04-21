from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.bienvenida, name="bienvenida"),
    path("home/", views.home, name="home"),
    path("login/google/", views.google_login, name="google_login"),
    path("oauth2callback/", views.oauth2callback, name="oauth2callback"),
    path("crear_cuenta/", views.crear_cuenta, name="crear_cuenta"),
    path('inicio_sesion', views.inicio_sesion, name='inicio_sesion'),
    
]
