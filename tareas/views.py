from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Task, Meta, Etiqueta
from .forms import TaskForm, MetaForm, EtiquetaForm
from django.views.decorators.http import require_POST

@login_required
def tareas(request):
    tareas_usuario = Task.objects.filter(usuario=request.user).order_by('fecha', 'hora')
    return render(request, 'tareas/tareas.html', {'tareas': tareas_usuario})

@login_required
def crear_tarea(request):
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

@login_required
def editar_tarea(request, tarea_id):
    tarea = get_object_or_404(Task, id=tarea_id, usuario=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=tarea)
        if form.is_valid():
            form.save()
            return redirect('tareas')
    else:
        form = TaskForm(instance=tarea)

    return render(request, 'tareas/editar_tarea.html', {'form': form, 'tarea': tarea})

@login_required
def eliminar_tarea(request, tarea_id):
    tarea = get_object_or_404(Task, id=tarea_id, usuario=request.user)

    if request.method == 'POST':
        tarea.delete()
        return redirect('tareas')

    return render(request, 'tareas/eliminar_tarea.html', {'tarea': tarea})

@login_required
@require_POST
def toggle_completada(request, tarea_id):
    tarea = get_object_or_404(Task, id=tarea_id, usuario=request.user)
    tarea.completada = not tarea.completada
    tarea.save()
    return redirect('tareas')

@login_required
def metas(request):
    metas_usuario = Meta.objects.filter(usuario=request.user).order_by('fecha_limite')
    return render(request, 'tareas/metas.html', {'metas': metas_usuario})

@login_required
def crear_meta(request):
    if request.method == 'POST':
        form = MetaForm(request.POST)
        if form.is_valid():
            meta = form.save(commit=False)
            meta.usuario = request.user
            meta.save()
            return redirect('metas')
    else:
        form = MetaForm()
    return render(request, 'tareas/crear_meta.html', {'form': form})

@login_required
def editar_meta(request, meta_id):
    meta = get_object_or_404(Meta, id=meta_id, usuario=request.user)

    if request.method == 'POST':
        form = MetaForm(request.POST, instance=meta)
        if form.is_valid():
            form.save()
            return redirect('metas')
    else:
        form = MetaForm(instance=meta)

    return render(request, 'tareas/editar_meta.html', {'form': form, 'meta': meta})


@login_required
def eliminar_meta(request, meta_id):
    meta = get_object_or_404(Meta, id=meta_id, usuario=request.user)

    if request.method == 'POST':
        meta.delete()
        return redirect('metas')

    return render(request, 'tareas/eliminar_meta.html', {'meta': meta})

@login_required
def etiquetas(request):
    etiquetas = Etiqueta.objects.filter(usuario=request.user)
    return render(request, 'tareas/etiquetas.html', {'etiquetas': etiquetas})

@login_required
def crear_etiqueta(request):
    if request.method == 'POST':
        form = EtiquetaForm(request.POST)
        if form.is_valid():
            etiqueta = form.save(commit=False)
            etiqueta.usuario = request.user
            etiqueta.save()
            return redirect('etiquetas')
    else:
        form = EtiquetaForm()
    return render(request, 'tareas/crear_etiqueta.html', {'form': form})

@login_required
def editar_etiqueta(request, etiqueta_id):
    etiqueta = get_object_or_404(Etiqueta, id=etiqueta_id, usuario=request.user)
    if request.method == 'POST':
        form = EtiquetaForm(request.POST, instance=etiqueta)
        if form.is_valid():
            form.save()
            return redirect('etiquetas')
    else:
        form = EtiquetaForm(instance=etiqueta)
    return render(request, 'tareas/editar_etiqueta.html', {'form': form, 'etiqueta': etiqueta})

@login_required
def eliminar_etiqueta(request, etiqueta_id):
    etiqueta = get_object_or_404(Etiqueta, id=etiqueta_id, usuario=request.user)
    if request.method == 'POST':
        etiqueta.delete()
        return redirect('etiquetas')
    return render(request, 'tareas/eliminar_etiqueta.html', {'etiqueta': etiqueta})