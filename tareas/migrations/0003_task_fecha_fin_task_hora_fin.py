# Generated by Django 5.2 on 2025-05-01 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tareas', '0002_task_evento_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='fecha_fin',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='hora_fin',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
