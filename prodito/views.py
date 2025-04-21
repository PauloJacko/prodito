from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib import messages


def bienvenida(request):
    return render(request, "bienvenida.html")


def home(request):
    return render(request, "home.html")


def crear_cuenta(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('crear_cuenta')

        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya existe.")
            return redirect('crear_cuenta')

        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está registrado.")
            return redirect('crear_cuenta')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Cuenta creada exitosamente. Ahora puedes iniciar sesión.")
        return redirect('bienvenida')

    return render(request, 'crear_cuenta.html')

def inicio_sesion(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            username = User.objects.get(email=email).username
        except User.DoesNotExist:
            messages.error(request, "Correo no registrado.")
            return redirect('bienvenida')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Contraseña incorrecta.")
            return redirect('bienvenida')


def google_login(request):
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return redirect(url)


def oauth2callback(request):
    code = request.GET.get("code")

    token_res = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        },
    ).json()

    access_token = token_res.get("access_token")

    # useful when using Google APIs
    id_token = token_res.get("id_token")

    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        params={"access_token": access_token},
    ).json()

    email = user_info["email"]
    name = user_info.get("name", email)

    user, _ = User.objects.get_or_create(username=email, defaults={"first_name": name})
    login(request, user)

    return redirect("home")
