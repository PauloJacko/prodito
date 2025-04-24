from datetime import date, datetime, timedelta
from urllib.parse import urlencode
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from tareas.models import Task


def admin(request):
    return render(request, "admin.html")


def bienvenida(request):
    return render(request, "bienvenida.html")


def home(request):
    tareas_hoy = []
    if request.user.is_authenticated:
        tareas_hoy = Task.objects.filter(
            usuario=request.user, fecha=date.today()
        ).order_by("hora")
    return render(request, "home.html", {"tareas_hoy": tareas_hoy})


def crear_cuenta(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect("crear_cuenta")

        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya existe.")
            return redirect("crear_cuenta")

        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está registrado.")
            return redirect("crear_cuenta")

        user = User.objects.create_user(
            username=username, email=email, password=password1
        )
        user.save()
        messages.success(
            request, "Cuenta creada exitosamente. Ahora puedes iniciar sesión."
        )
        return redirect("bienvenida")

    return render(request, "crear_cuenta.html")


def inicio_sesion(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        try:
            username = User.objects.get(email=email).username
        except User.DoesNotExist:
            messages.error(request, "Correo no registrado.")
            return redirect("bienvenida")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Contraseña incorrecta.")
            return redirect("bienvenida")


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

    # Solicita el token de acceso y el refresh token
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
    refresh_token = token_res.get("refresh_token")

    request.session["google_access_token"] = access_token
    if refresh_token:
        request.session["google_refresh_token"] = refresh_token

    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        params={"access_token": access_token},
    ).json()

    email = user_info["email"]
    name = user_info.get("name", email)

    user, _ = User.objects.get_or_create(username=email, defaults={"first_name": name})
    login(request, user)

    return redirect("home")


def obtener_tareas(request):
    tareas = Task.objects.filter(usuario=request.user)
    data = []

    for tarea in tareas:
        if tarea.fecha:
            evento = {
                "id": str(tarea.id),
                "calendarId": "1",
                "title": tarea.titulo,
                "category": "time",
                "dueDateClass": "",
                "start": f"{tarea.fecha}T{tarea.hora or '00:00:00'}",
                "end": f"{tarea.fecha}T{tarea.hora or '00:00:00'}",
                "isReadOnly": True,
            }
            data.append(evento)

    return JsonResponse(data, safe=False)


SCOPES = ["https://www.googleapis.com/auth/calendar"]


def refrescar_token(refresh_token):
    token_res = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
    ).json()
    return token_res.get("access_token")


@login_required
def eventos_google_calendar(request):
    access_token = request.session.get("google_access_token")
    refresh_token = request.session.get("google_refresh_token")

    if not access_token and refresh_token:
        access_token = refrescar_token(refresh_token)
        request.session["google_access_token"] = access_token

    if not access_token:
        return JsonResponse({"error": "No autorizado"}, status=401)

    calendar_id = "primary"
    time_min = (datetime.now() - timedelta(days=60)).isoformat() + "Z"
    time_max = (datetime.now() + timedelta(days=30)).isoformat() + "Z"

    url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "maxResults": 250,
        "orderBy": "startTime",
        "singleEvents": True,
        "timeMin": time_min,
        "timeMax": time_max,
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 403:
        return JsonResponse(
            {"error": "Acceso denegado. Verifica los permisos de OAuth."}, status=403
        )

    if response.status_code != 200:
        return JsonResponse(
            {"error": "No se pudieron obtener los eventos"}, status=response.status_code
        )

    eventos = response.json().get("items", [])
    data = []
    for e in eventos:
        titulo = e.get("summary", "Sin título")
        inicio = e["start"].get("dateTime") or e["start"].get("date")
        fin = e["end"].get("dateTime") or e["end"].get("date")

        data.append(
            {
                "id": e["id"],
                "calendarId": "google",
                "title": titulo,
                "category": "time",
                "start": inicio,
                "end": fin,
                "isReadOnly": True,
            }
        )

    return JsonResponse(data, safe=False)
