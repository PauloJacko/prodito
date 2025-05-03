from django.contrib.auth.models import User
from django.db import models


class Etiqueta(models.Model):
    nombre = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#cccccc")
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="etiquetas"
    )

    def __str__(self):
        return self.nombre


class Task(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    fecha = models.DateField(null=True, blank=True)
    hora = models.TimeField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    etiquetas = models.ManyToManyField(Etiqueta, blank=True)
    completada = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)
    meta = models.ForeignKey(
        "Meta", on_delete=models.SET_NULL, null=True, blank=True, related_name="tareas"
    )
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

# Extiende al usuario con sus puntos
class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    puntos = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.usuario.username} - {self.puntos} PP"

# Define los cosméticos (skins) disponibles
class Skin(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.IntegerField()
    imagen = models.URLField(blank=True)  # opcional: puedes guardar URL de la imagen

    def __str__(self):
        return f"{self.nombre} ({self.precio} PP)"

# Relación entre usuario y skins que ya canjeó
class SkinUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skins_obtenidas')
    skin = models.ForeignKey(Skin, on_delete=models.CASCADE)
    fecha_canje = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'skin')  # evita que canjee dos veces la misma skin

    def __str__(self):
        return f"{self.usuario.username} - {self.skin.nombre}"

# Historial de obtención/gasto de puntos
class ReportePuntos(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reportes_puntos')
    descripcion = models.TextField()
    puntos_cambiados = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.puntos_cambiados} puntos el {self.fecha}"

class Notificacion(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="notificaciones"
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    mensaje = models.CharField(max_length=255)
    programada_para = models.DateTimeField()
    leida = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notif: {self.task.titulo} → {self.usuario.username}"
