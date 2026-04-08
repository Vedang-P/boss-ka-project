from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses")
    connection = models.ForeignKey(
        "integrations.LMSConnection",
        on_delete=models.CASCADE,
        related_name="courses",
        null=True,
        blank=True,
    )
    external_id = models.CharField(max_length=128, blank=True)
    code = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    instructor = models.CharField(max_length=255, blank=True)
    color_hex = models.CharField(max_length=7, default="#1f6feb")
    current_grade_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("title",)
        unique_together = ("user", "connection", "external_id")

    def __str__(self):
        return f"{self.code} - {self.title}"


class GradeComponent(models.Model):
    SOURCE_CHOICES = (
        ("lms", "LMS"),
        ("manual", "Manual"),
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="grade_components")
    external_id = models.CharField(max_length=128, blank=True)
    name = models.CharField(max_length=120)
    weight_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    override_weight_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    source = models.CharField(max_length=16, choices=SOURCE_CHOICES, default="lms")

    class Meta:
        ordering = ("course", "name")
        unique_together = ("course", "external_id")

    @property
    def effective_weight_percent(self):
        return self.override_weight_percent if self.override_weight_percent is not None else self.weight_percent

    def __str__(self):
        return f"{self.course.code}: {self.name}"


class Task(models.Model):
    TASK_TYPE_CHOICES = (
        ("assignment", "Assignment"),
        ("exam", "Exam"),
        ("quiz", "Quiz"),
        ("project", "Project"),
        ("manual", "Manual Task"),
    )
    DIFFICULTY_CHOICES = (
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    )
    SOURCE_CHOICES = (
        ("imported", "Imported"),
        ("manual", "Manual"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="tasks", null=True, blank=True)
    connection = models.ForeignKey(
        "integrations.LMSConnection",
        on_delete=models.SET_NULL,
        related_name="tasks",
        null=True,
        blank=True,
    )
    grade_component = models.ForeignKey(
        GradeComponent,
        on_delete=models.SET_NULL,
        related_name="tasks",
        null=True,
        blank=True,
    )
    external_id = models.CharField(max_length=128, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=32, choices=TASK_TYPE_CHOICES, default="assignment")
    due_at = models.DateTimeField()
    weight_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    difficulty = models.CharField(max_length=16, choices=DIFFICULTY_CHOICES, default="medium")
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    max_points = models.DecimalField(max_digits=7, decimal_places=2, default=100)
    earned_score_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    source = models.CharField(max_length=16, choices=SOURCE_CHOICES, default="imported")
    priority_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("due_at", "-priority_score")

    def __str__(self):
        return self.title

    @property
    def days_until_due(self):
        return (self.due_at - timezone.now()).days

    @property
    def resolved_estimated_hours(self):
        if self.estimated_hours and self.estimated_hours > 0:
            return Decimal(self.estimated_hours)

        defaults = {
            ("assignment", "easy"): Decimal("1.5"),
            ("assignment", "medium"): Decimal("2.5"),
            ("assignment", "hard"): Decimal("4.0"),
            ("quiz", "easy"): Decimal("1.0"),
            ("quiz", "medium"): Decimal("1.5"),
            ("quiz", "hard"): Decimal("2.5"),
            ("project", "easy"): Decimal("3.0"),
            ("project", "medium"): Decimal("5.0"),
            ("project", "hard"): Decimal("8.0"),
            ("exam", "easy"): Decimal("3.0"),
            ("exam", "medium"): Decimal("5.0"),
            ("exam", "hard"): Decimal("8.0"),
            ("manual", "easy"): Decimal("1.0"),
            ("manual", "medium"): Decimal("2.0"),
            ("manual", "hard"): Decimal("3.5"),
        }
        return defaults[(self.task_type, self.difficulty)]

    def save(self, *args, **kwargs):
        from analytics_app.services import calculate_urgency_score

        self.priority_score = calculate_urgency_score(self)
        super().save(*args, **kwargs)
