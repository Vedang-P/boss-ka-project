from django.urls import path

from .views import grade_prediction_view

app_name = "analytics_app"

urlpatterns = [
    path("grade-prediction/", grade_prediction_view, name="grade_prediction"),
]
