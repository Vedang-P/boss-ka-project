from django.contrib import admin

from .models import StudyAvailability, StudySession


@admin.register(StudyAvailability)
class StudyAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("user", "weekday", "start_time", "end_time")


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "start_at", "end_at", "status", "is_generated")
