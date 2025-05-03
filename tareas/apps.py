from django.apps import AppConfig


class TareasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tareas"

    def ready(self) -> None:
        from tareas.notificaciones.scheduler import iniciar_scheduler

        iniciar_scheduler()
        return super().ready()
