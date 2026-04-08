from django.urls import path

from .views import manual_task_create

app_name = "academics"

urlpatterns = [
    path("manual/new/", manual_task_create, name="manual_task_create"),
]
