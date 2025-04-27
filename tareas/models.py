from django.contrib.auth.models import User
from django.db import models


class Etiqueta(models.Model):
    nombre = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#cccccc")  # color HEX opcional

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
    evento_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.titulo} ({self.usuario.username})"
