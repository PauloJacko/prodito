from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Crea o reemplaza el stored procedure generar_notificaciones en PostgreSQL."

    def handle(self, *args, **options):
        sql = """
        CREATE OR REPLACE FUNCTION generar_notificaciones()
        RETURNS void AS $$
        BEGIN
            INSERT INTO tareas_notificacion (
                task_id, 
                usuario_id, 
                mensaje,  
                programada_para, 
                creada_en,
                leida
            )
            SELECT 
                t.id,
                t.usuario_id,
                '¡Recordatorio de tarea: ' || t.titulo || '!',
                NOW() + interval '30 minutes',
                NOW(),
                FALSE
            FROM tareas_task t
            WHERE 
                t.fecha = CURRENT_DATE
                AND t.completada = FALSE
                AND NOT EXISTS (
                    SELECT 1 
                    FROM tareas_notificacion n 
                    WHERE n.task_id = t.id
                      AND DATE(n.programada_para) = CURRENT_DATE
                );
        END;
        $$ LANGUAGE plpgsql;
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            self.stdout.write(
                self.style.SUCCESS(
                    "Stored procedure 'generar_notificaciones' actualizado exitosamente."
                )
            )
