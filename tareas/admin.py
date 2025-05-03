from django.contrib import admin

from .models import Etiqueta, Meta, Notificacion, Task

admin.site.register(Task)
admin.site.register(Etiqueta)
admin.site.register(Meta)
admin.site.register(Notificacion)
