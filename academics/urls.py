from django.urls import path

from .views import manual_task_create, task_delete, task_edit, task_toggle_complete

app_name = "academics"

urlpatterns = [
    path("manual/new/", manual_task_create, name="manual_task_create"),
    path("task/<int:pk>/toggle/", task_toggle_complete, name="task_toggle_complete"),
    path("task/<int:pk>/edit/", task_edit, name="task_edit"),
    path("task/<int:pk>/delete/", task_delete, name="task_delete"),
]
