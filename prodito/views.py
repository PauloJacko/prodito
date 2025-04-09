from django.shortcuts import render

def bienvenida(request):
    return render(request, 'bienvenida.html')

def home(request):
    return render(request, 'home.html')

def crear_cuenta(request):
    return render(request, 'crear_cuenta.html')