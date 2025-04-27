import json

import requests
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from prodito.views import (
    crear_evento_google_calendar,
    eliminar_evento_google_calendar,
    refrescar_token,
)

from .forms import TaskForm
from .models import Task


# @login_required
def tareas(request):
    if not request.user.is_authenticated:
        try:
            user = User.objects.get(username="admin")
        except User.DoesNotExist:
            user = User.objects.create_user(
                username="admin", password="admin123", first_name="Admin"
            )
        login(request, user)

    tareas_usuario = Task.objects.filter(usuario=request.user).order_by("fecha", "hora")
    return render(request, "tareas/tareas.html", {"tareas": tareas_usuario})


def crear_tarea(request):
    if not request.user.is_authenticated:
        user = User.objects.get(username="admin")
        login(request, user)

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.usuario = request.user
            tarea.save()
            form.save_m2m()

            crear_evento_google_calendar(request, tarea)

            return redirect("tareas")
    else:
        form = TaskForm()

    return render(request, "tareas/crear_tarea.html", {"form": form})


def editar_tarea(request, tarea_id):
    if not request.user.is_authenticated:
        user = User.objects.get(username="admin")
        login(request, user)

    tarea = get_object_or_404(Task, id=tarea_id, usuario=request.user)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=tarea)
        if form.is_valid():
            tarea = form.save()

            if tarea.evento_id:
                access_token = request.session.get("google_access_token")
                refresh_token = request.session.get("google_refresh_token")

                if not access_token and refresh_token:
                    access_token = refrescar_token(refresh_token)
                    request.session["google_access_token"] = access_token

                if access_token:
                    url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events/{tarea.evento_id}"
                    headers = {
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    }

                    event_data = {
                        "summary": tarea.titulo,
                        "description": tarea.descripcion,
                        "start": {
                            "dateTime": f"{tarea.fecha}T{tarea.hora or '00:00:00'}",
                            "timeZone": "America/Santiago",
                        },
                        "end": {
                            "dateTime": f"{tarea.fecha}T{tarea.hora or '00:00:00'}",
                            "timeZone": "America/Santiago",
                        },
                    }

                    response = requests.patch(
                        url, headers=headers, data=json.dumps(event_data)
                    )

                    if response.status_code not in [200, 201]:
                        print(
                            "Error actualizando evento en Google Calendar:",
                            response.json(),
                        )

            return redirect("tareas")
    else:
        form = TaskForm(instance=tarea)

    return render(request, "tareas/editar_tarea.html", {"form": form, "tarea": tarea})


def eliminar_tarea(request, tarea_id):
    if not request.user.is_authenticated:
        user = User.objects.get(username="admin")
        login(request, user)

    tarea = get_object_or_404(Task, id=tarea_id, usuario=request.user)

    if request.method == "POST":
        if tarea.evento_id:
            eliminar_evento_google_calendar(request, tarea.evento_id)

        tarea.delete()
        return redirect("tareas")

    return render(request, "tareas/eliminar_tarea.html", {"tarea": tarea})


@require_POST
def toggle_completada(request, tarea_id):
    if not request.user.is_authenticated:
        user = User.objects.get(username="admin")
        login(request, user)

    tarea = get_object_or_404(Task, id=tarea_id, usuario=request.user)
    tarea.completada = not tarea.completada
    tarea.save()
    return redirect("tareas")
