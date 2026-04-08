from django.urls import path

from .views import availability_view, generate_plan_view

app_name = "planner"

urlpatterns = [
    path("availability/", availability_view, name="availability"),
    path("generate/", generate_plan_view, name="generate"),
]
