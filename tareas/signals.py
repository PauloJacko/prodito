from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PerfilUsuario, Task, Meta

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(usuario=instance)

@receiver(post_save, sender=Task)
def gestionar_puntos_tarea(sender, instance, created, **kwargs):
    user_profile = instance.usuario.perfil

    if created:
        user_profile.puntos += 1

    if instance.completada:
        user_profile.puntos += 5

    user_profile.save()

@receiver(post_save, sender=Meta)
def gestionar_puntos_meta(sender, instance, created, **kwargs):
    user_profile = instance.usuario.perfil

    if created:
        user_profile.puntos += 3

    if instance.completada:
        user_profile.puntos += 20

    user_profile.save()