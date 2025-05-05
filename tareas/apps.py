from django.apps import AppConfig

class TareasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tareas'

    def ready(self):
        # Importa los signals para que se registren al arrancar
        import tareas.signals
        
        # Inicia el scheduler (notificaciones)
        from tareas.notificaciones.scheduler import iniciar_scheduler
        iniciar_scheduler()