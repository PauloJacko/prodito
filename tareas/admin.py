from django.contrib import admin
from .models import Task, Etiqueta, Meta, Skin, PerfilUsuario, SkinUsuario, ReportePuntos, Notificacion

admin.site.register(Task)
admin.site.register(Etiqueta)
admin.site.register(Meta)
admin.site.register(Skin)
admin.site.register(PerfilUsuario)
admin.site.register(SkinUsuario)
admin.site.register(ReportePuntos)
admin.site.register(Notificacion)
