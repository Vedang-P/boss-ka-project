from django.urls import path

from .views import connection_create, connection_sync

app_name = "integrations"

urlpatterns = [
    path("connect/", connection_create, name="connection_create"),
    path("<int:pk>/sync/", connection_sync, name="connection_sync"),
]
