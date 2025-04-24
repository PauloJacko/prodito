from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import TaskForm
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST

# @login_required
def tareas(request):
    # Usuario de prueba para poder visualizar los cambios
    if not request.user.is_authenticated:
        try:
            user = User.objects.get(username="admin")
        except User.DoesNotExist:
            user = User.objects.create_user(username="admin", password="admin123", first_name="Admin")
        login(request, user)
    
    tareas_usuario = Task.objects.filter(usuario=request.user).order_by('fecha', 'hora')
    return render(request, 'tareas/tareas.html', {'tareas': tareas_usuario})

def crear_tarea(request):
    if not request.user.is_authenticated:
        user = User.objects.get(username="admin")
        login(request, user)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.usuario = request.user
            tarea.save()
            form.save_m2m()  # para guardar etiquetas
            return redirect('tareas')
    else:
        form = TaskForm()

    return render(request, 'tareas/crear_tarea.html', {'form': form})

def editar_tarea(request, tarea_id):
    if not request.user.is_authenticated:
        user = User.objects.get(username="admin")
        login(request, user)

    tarea = get_object_or_404(Task, id=tarea_id, usuario=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=tarea)
        if form.is_valid():
            form.save()
            return redirect('tareas')
    else:
        form = TaskForm(instance=tarea)

    return render(request, 'tareas/editar_tarea.html', {'form': form, 'tarea': tarea})

def eliminar_tarea(request, tarea_id):
    if not request.user.is_authenticated:
        user = User.objects.get(username="admin")
        login(request, user)

    tarea = get_object_or_404(Task, id=tarea_id, usuario=request.user)

    if request.method == 'POST':
        tarea.delete()
        return redirect('tareas')

    return render(request, 'tareas/eliminar_tarea.html', {'tarea': tarea})

@require_POST
def toggle_completada(request, tarea_id):
    if not request.user.is_authenticated:
        user = User.objects.get(username="admin")
        login(request, user)

    tarea = get_object_or_404(Task, id=tarea_id, usuario=request.user)
    tarea.completada = not tarea.completada
    tarea.save()
    return redirect('tareas')