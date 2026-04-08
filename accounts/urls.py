from django.urls import path

from .views import signup_view

app_name = "accounts"

urlpatterns = [
    path("signup/", signup_view, name="signup"),
]
