from django.contrib.auth.models import User
from django.db import models


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    timezone = models.CharField(max_length=64, default="Asia/Kolkata")
    preferred_daily_study_hours = models.PositiveSmallIntegerField(default=2)
    course_load_note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
