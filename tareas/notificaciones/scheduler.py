from apscheduler.schedulers.background import BackgroundScheduler
from django.db import connection


def ejecutar_sp():
    with connection.cursor() as cursor:
        cursor.execute("SELECT generar_notificaciones();")
    print("Stored procedure ejecutado correctamente.")


def iniciar_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(ejecutar_sp, "interval", minutes=1)
    scheduler.start()
