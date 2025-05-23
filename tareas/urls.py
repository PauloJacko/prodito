from django.urls import path

from . import views

urlpatterns = [
    path("", views.tareas, name="tareas"),
    path("crear/", views.crear_tarea, name="crear_tarea"),
    path("editar/<int:tarea_id>/", views.editar_tarea, name="editar_tarea"),
    path("eliminar/<int:tarea_id>/", views.eliminar_tarea, name="eliminar_tarea"),
    path("toggle/<int:tarea_id>/", views.toggle_completada, name="toggle_completada"),

    # Metas
    path("metas/", views.metas, name="metas"),
    path("metas/crear/", views.crear_meta, name="crear_meta"),
    path("metas/editar/<int:meta_id>/", views.editar_meta, name="editar_meta"),
    path("metas/eliminar/<int:meta_id>/", views.eliminar_meta, name="eliminar_meta"),

    # Etiquetas
    path("etiquetas/", views.etiquetas, name="etiquetas"),
    path("etiquetas/crear/", views.crear_etiqueta, name="crear_etiqueta"),
    path("etiquetas/editar/<int:etiqueta_id>/", views.editar_etiqueta, name="editar_etiqueta"),
    path("etiquetas/eliminar/<int:etiqueta_id>/", views.eliminar_etiqueta, name="eliminar_etiqueta"),

    # Recompensas
    path('tienda/', views.tienda, name='tienda'),
    path('tienda/canjear/<int:skin_id>/', views.canjear_skin, name='canjear_skin'),
    path('activar_skin/<int:skin_id>/', views.activar_skin, name='activar_skin'),
]