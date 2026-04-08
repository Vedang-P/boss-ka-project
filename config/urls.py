from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("dashboard.urls")),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("integrations/", include("integrations.urls")),
    path("academics/", include("academics.urls")),
    path("planner/", include("planner.urls")),
    path("analytics/", include("analytics_app.urls")),
]
