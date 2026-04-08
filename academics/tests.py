from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Course, Task


class ManualTaskViewTests(TestCase):
    def test_manual_task_creation_flow(self):
        user = User.objects.create_user(username="writer", password="pass12345")
        course = Course.objects.create(user=user, code="SE200", title="Software Design")
        self.client.login(username="writer", password="pass12345")

        response = self.client.post(
            reverse("academics:manual_task_create"),
            {
                "course": course.pk,
                "title": "Prepare viva notes",
                "description": "Summarize key architecture trade-offs.",
                "task_type": "manual",
                "due_at": (timezone.now() + timezone.timedelta(days=3)).strftime("%Y-%m-%dT%H:%M"),
                "weight_percent": "5",
                "difficulty": "medium",
                "estimated_hours": "2",
            },
        )

        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(title="Prepare viva notes")
        self.assertEqual(task.source, "manual")
