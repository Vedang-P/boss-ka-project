from django.urls import path

from .views import (
    connection_create,
    connection_delete,
    connection_sync,
    connection_sync_all,
    connection_toggle_mode,
    manage_connections,
)

app_name = "integrations"

urlpatterns = [
    path("connect/", connection_create, name="connection_create"),
    path("sync-all/", connection_sync_all, name="connection_sync_all"),
    path("manage/", manage_connections, name="manage"),
    path("<int:pk>/sync/", connection_sync, name="connection_sync"),
    path(
        "<int:pk>/toggle-mode/", connection_toggle_mode, name="connection_toggle_mode"
    ),
    path("<int:pk>/delete/", connection_delete, name="connection_delete"),
]
