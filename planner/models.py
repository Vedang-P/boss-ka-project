from django.contrib.auth.models import User
from django.db import models


class StudyAvailability(models.Model):
    WEEKDAY_CHOICES = (
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="study_availabilities")
    weekday = models.PositiveSmallIntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ("weekday", "start_time")

    def __str__(self):
        return f"{self.get_weekday_display()} {self.start_time}-{self.end_time}"


class StudySession(models.Model):
    STATUS_CHOICES = (
        ("planned", "Planned"),
        ("completed", "Completed"),
        ("skipped", "Skipped"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="study_sessions")
    task = models.ForeignKey(
        "academics.Task",
        on_delete=models.SET_NULL,
        related_name="study_sessions",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="planned")
    is_generated = models.BooleanField(default=True)

    class Meta:
        ordering = ("start_at",)

    def __str__(self):
        return self.title
