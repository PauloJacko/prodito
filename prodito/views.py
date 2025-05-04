import json
import os
import tempfile
from datetime import date, datetime, timedelta
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import JsonResponse
from tareas.models import Notificacion
from django.views.decorators.csrf import csrf_exempt

from tareas.models import Task


def admin(request):
    return render(request, "admin.html")


def bienvenida(request):
    return render(request, "bienvenida.html")


def mi_perfil(request):
    return render(request, "mi_perfil.html")


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
    data = []
    is_google_user = request.session["google_access_token"] is not None

    if is_google_user:
        return JsonResponse(data, safe=False)

    tareas = Task.objects.filter(usuario=request.user)
    for tarea in tareas:
        evento = {
            "id": str(tarea.id),
            "calendarId": "1",
            "title": tarea.titulo,
            "category": "time",
            "dueDateClass": "",
            "start": f"{tarea.fecha}T{tarea.hora or '00:00:00'}",
            "end": f"{tarea.fecha_fin}T{tarea.hora_fin or '00:00:00'}",
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
def eventos_google_calendar(request, anio, mes):
    access_token = request.session.get("google_access_token")
    refresh_token = request.session.get("google_refresh_token")

    if not access_token and refresh_token:
        access_token = refrescar_token(refresh_token)
        request.session["google_access_token"] = access_token

    if not access_token:
        return JsonResponse({"error": "No autorizado"}, status=401)

    try:
        inicio = datetime(anio, mes, 1)
        if mes == 12:
            fin_mes = datetime(anio + 1, 1, 1)
        else:
            fin_mes = datetime(anio, mes + 1, 1)
    except Exception:
        return JsonResponse({"error": "Parámetros año o mes inválidos"}, status=400)

    calendar_id = "primary"
    headers = {"Authorization": f"Bearer {access_token}"}
    base_url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"

    params = {
        "maxResults": 250,
        "orderBy": "startTime",
        "singleEvents": True,
        "timeMin": inicio.isoformat() + "Z",
        "timeMax": fin_mes.isoformat() + "Z",
    }

    eventos = []
    next_page_token = None
    while True:
        if next_page_token:
            params["pageToken"] = next_page_token

        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code != 200:
            return JsonResponse(
                {"error": "Error obteniendo eventos"}, status=response.status_code
            )

        data = response.json()
        eventos.extend(data.get("items", []))

        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    resultado = []
    for e in eventos:
        titulo = e.get("summary", "Sin título")
        inicio_evento = e["start"].get("dateTime") or e["start"].get("date")
        fin_evento = e["end"].get("dateTime") or e["end"].get("date")

        resultado.append(
            {
                "id": e["id"],
                "calendarId": "google",
                "title": titulo,
                "category": "time",
                "start": inicio_evento,
                "end": fin_evento,
                "isReadOnly": True,
            }
        )

    return JsonResponse(resultado, safe=False)


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

    # Si la hora de fin no está especificada, le asignamos una hora por defecto (1 hora después del inicio)
    start_datetime = (
        datetime.combine(tarea.fecha, tarea.hora)
        if tarea.hora
        else datetime.combine(tarea.fecha, datetime.min.time())
    )

    if tarea.hora_fin:
        end_datetime = datetime.combine(tarea.fecha_fin, tarea.hora_fin)
    else:
        # Si no se especifica hora_fin, asignamos 1 hora después de la hora de inicio
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
            descripcion = data.get("descripcion")
            fecha_str = data.get("fecha")
            hora_str = data.get("hora")
            fecha_fin_str = data.get("fecha_fin")
            hora_fin_str = data.get("hora_fin")

            if not titulo or not fecha_str or not hora_str:
                return JsonResponse({"error": "Faltan datos requeridos"}, status=400)

            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                hora = datetime.strptime(hora_str, "%H:%M").time()
                fecha_fin = (
                    datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
                    if fecha_fin_str
                    else None
                )
                hora_fin = (
                    datetime.strptime(hora_fin_str, "%H:%M").time()
                    if hora_fin_str
                    else None
                )
            except ValueError:
                return JsonResponse(
                    {"error": "Formato de fecha u hora inválido."}, status=400
                )

            tarea = Task.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                fecha=fecha,
                hora=hora,
                fecha_fin=fecha_fin,
                hora_fin=hora_fin,
                usuario=request.user,  # asegúrate de que request.user esté disponible
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


@login_required
def generar_reporte(request):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="reporte.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    logo_url = "https://res.cloudinary.com/dtnttrleq/image/upload/v1744407776/prodito_logo_gqeq7n_qhpgv9.png"
    logo_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    logo_file.write(requests.get(logo_url).content)
    logo_file.close()
    p.drawImage(
        logo_file.name,
        50,
        height - 100,
        width=120,
        height=40,
        preserveAspectRatio=True,
        mask="auto",
    )

    # Título
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2, height - 130, "Reporte de Usuario")
    p.line(50, height - 140, width - 50, height - 140)

    # Info de usuario
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 170, f"Usuario: {request.user.username}")
    p.drawString(50, height - 190, f"Email: {request.user.email}")
    p.drawString(
        50, height - 210, f"Fecha de generación: {now().strftime('%d-%m-%Y %H:%M')}"
    )

    # Tareas
    tareas = request.user.task_set.all()
    completadas = tareas.filter(completada=True).count()
    total = tareas.count()
    progreso = (completadas / total * 100) if total > 0 else 0
    p.drawString(
        50,
        height - 240,
        f"Tareas completadas: {completadas} de {total} ({progreso:.0f}%)",
    )

    # Cargar íconos locales
    check_path = os.path.join(settings.BASE_DIR, "static", "img", "check-png.png")
    cross_path = os.path.join(settings.BASE_DIR, "static", "img", "cross-png.png")

    # Lista de tareas
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 270, "Últimas tareas:")
    y = height - 290
    p.setFont("Helvetica", 11)

    for tarea in tareas.order_by("-id")[:10]:
        estado_texto = "Completada:" if tarea.completada else "Pendiente:"
        estado_img = check_path if tarea.completada else cross_path

        try:
            p.drawImage(estado_img, 50, y - 3, width=12, height=12, mask="auto")
        except Exception as e:
            print(f"Error cargando imagen de estado: {e}")

        p.drawString(70, y, f"{estado_texto} {tarea.titulo}")
        y -= 18

        if y < 100:
            p.showPage()
            y = height - 50

    mascota_url = "https://res.cloudinary.com/dtnttrleq/image/upload/v1744407778/prodito_risa_hijnjl_ucgvci.png"
    mascota_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    mascota_file.write(requests.get(mascota_url).content)
    mascota_file.close()
    p.drawImage(
        mascota_file.name,
        width - 180,
        40,
        width=120,
        height=100,
        preserveAspectRatio=True,
        mask="auto",
    )

    p.showPage()
    p.save()

    # Limpiar archivos temporales
    os.unlink(logo_file.name)
    os.unlink(mascota_file.name)

    return response

#Notificaciones

@login_required
def notificaciones_json(request):
    notificaciones = Notificacion.objects.filter(usuario=request.user, leida=False)
    data = [
        {"id": n.id, "mensaje": n.mensaje}
        for n in notificaciones
    ]
    return JsonResponse(data, safe=False)

@require_POST
@login_required
def marcar_notificacion_leida(request, id):
    Notificacion.objects.filter(id=id, usuario=request.user).update(leida=True)
    return JsonResponse({'ok': True})


@require_POST
@login_required
def eliminar_cuenta(request):
    messages.add_message(
        request,
        messages.WARNING,
        "¿Estás seguro de que deseas eliminar tu cuenta? Esta acción es irreversible.",
    )
    usuario = request.user
    logout(request)
    usuario.delete()
    return redirect("bienvenida")

