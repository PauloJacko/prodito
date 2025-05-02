from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PerfilUsuario, Task, Meta

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(usuario=instance)

@receiver(post_save, sender=Task)
def sumar_puntos_crear_tarea(sender, instance, created, **kwargs):
    if created:
        user_profile = instance.usuario.perfil
        user_profile.puntos += 1
        user_profile.save()

@receiver(post_save, sender=Meta)
def sumar_puntos_crear_meta(sender, instance, created, **kwargs):
    if created:
        user_profile = instance.usuario.perfil
        user_profile.puntos += 3
        user_profile.save()

@receiver(post_save, sender=Task)
def sumar_puntos_completar_tarea(sender, instance, **kwargs):
    if instance.completada:
        user_profile = instance.usuario.perfil
        user_profile.puntos += 5
        user_profile.save()

@receiver(post_save, sender=Meta)
def sumar_puntos_completar_meta(sender, instance, **kwargs):
    if instance.completada:
        user_profile = instance.usuario.perfil
        user_profile.puntos += 20
        user_profile.save()