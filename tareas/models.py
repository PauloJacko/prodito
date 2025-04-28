from django.contrib.auth.models import User
from django.db import models


class Etiqueta(models.Model):
    nombre = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#cccccc")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='etiquetas')

    def __str__(self):
        return self.nombre


class Task(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    fecha = models.DateField(null=True, blank=True)
    hora = models.TimeField(null=True, blank=True)
    etiquetas = models.ManyToManyField(Etiqueta, blank=True)
    completada = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)
    meta = models.ForeignKey('Meta', on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas')
    evento_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.titulo} ({self.usuario.username})"
    
class Meta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha_limite = models.DateField(blank=True, null=True)
    completada = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo
