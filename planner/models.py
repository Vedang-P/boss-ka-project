from django.contrib.auth.models import User
from django.db import models
from django.db.models import F


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
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=F("start_time")),
                name="study_availability_end_after_start",
            ),
            models.UniqueConstraint(
                fields=("user", "weekday", "start_time", "end_time"),
                name="uniq_user_availability_slot",
            ),
        ]
        indexes = [
            models.Index(fields=("user", "weekday"), name="availability_user_weekday_idx"),
        ]

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
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_at__gt=F("start_at")),
                name="study_session_end_after_start",
            ),
        ]
        indexes = [
            models.Index(fields=("user", "start_at"), name="session_user_start_idx"),
            models.Index(fields=("user", "status", "start_at"), name="session_user_status_start_idx"),
        ]

    def __str__(self):
        return self.title
