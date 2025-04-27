import json
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
from django.views.decorators.csrf import csrf_exempt

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


SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.app.created",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
    "email",
    "profile",
]


def google_login(request):
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
        "scope": " ".join(SCOPES),
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


def crear_evento_google_calendar(request, tarea):
    access_token = request.session.get("google_access_token")
    refresh_token = request.session.get("google_refresh_token")

    if not access_token and refresh_token:
        access_token = refrescar_token(refresh_token)
        request.session["google_access_token"] = access_token

    if not access_token:
        print("No autorizado para crear evento en Google Calendar")
        return

    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    start_datetime = (
        datetime.combine(tarea.fecha, tarea.hora)
        if tarea.hora
        else datetime.combine(tarea.fecha, datetime.min.time())
    )
    end_datetime = start_datetime + timedelta(hours=1)

    event_data = {
        "summary": tarea.titulo,
        "description": tarea.descripcion,
        "start": {
            "dateTime": start_datetime.isoformat(),
            "timeZone": "America/Santiago",
        },
        "end": {
            "dateTime": end_datetime.isoformat(),
            "timeZone": "America/Santiago",
        },
    }

    response = requests.post(url, headers=headers, json=event_data)

    if response.status_code == 200:
        event = response.json()
        tarea.evento_id = event["id"]
        tarea.save(update_fields=["evento_id"])
        print("Evento creado en Google Calendar")
    else:
        print(f"Error al crear evento: {response.text}")


def eliminar_evento_google_calendar(request, evento_id):
    access_token = request.session.get("google_access_token")
    refresh_token = request.session.get("google_refresh_token")

    if not access_token and refresh_token:
        access_token = refrescar_token(refresh_token)
        request.session["google_access_token"] = access_token

    if not access_token:
        print("No autorizado para eliminar evento en Google Calendar")
        return

    url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events/{evento_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        print("Evento eliminado de Google Calendar")
    else:
        print(f"Error al eliminar evento: {response.text}")


@csrf_exempt
def crear_tarea_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            titulo = data.get("titulo")
            fecha = data.get("fecha")
            descripcion = data.get("descripcion")

            if not titulo or not fecha:
                return JsonResponse({"error": "Faltan datos requeridos"}, status=400)

            try:
                fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse(
                    {"error": "Formato de fecha inválido. Debe ser 'YYYY-MM-DD'"},
                    status=400,
                )

            tarea = Task.objects.create(
                titulo=titulo,
                fecha=fecha_obj,
                descripcion=descripcion,
                usuario=request.user,
            )

            crear_evento_google_calendar(request, tarea)

            return JsonResponse(
                {"message": "Tarea creada con éxito", "tarea_id": tarea.id}, status=201
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Datos JSON inválidos"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)
