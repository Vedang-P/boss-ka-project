from django.urls import path

from .views import (
    availability_view,
    generate_plan_view,
    session_update_status,
    slot_delete,
)

app_name = "planner"

urlpatterns = [
    path("availability/", availability_view, name="availability"),
    path("generate/", generate_plan_view, name="generate"),
    path("slot/<int:pk>/delete/", slot_delete, name="slot_delete"),
    path(
        "session/<int:pk>/status/", session_update_status, name="session_update_status"
    ),
]
