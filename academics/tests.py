from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Course, Task


class ManualTaskViewTests(TestCase):
    def test_manual_task_form_page_renders(self):
        user = User.objects.create_user(username="manualpage", password="pass12345")
        self.client.login(username="manualpage", password="pass12345")

        response = self.client.get(reverse("academics:manual_task_create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add Manual Task")

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

    def test_manual_task_toggle_edit_and_delete_flow(self):
        user = User.objects.create_user(username="editor", password="pass12345")
        course = Course.objects.create(user=user, code="SE201", title="Systems Design")
        task = Task.objects.create(
            user=user,
            course=course,
            title="Draft report",
            description="Initial version",
            task_type="manual",
            due_at=timezone.now() + timezone.timedelta(days=2),
            weight_percent=Decimal("10"),
            difficulty="medium",
            estimated_hours=Decimal("2"),
            source="manual",
        )
        self.client.login(username="editor", password="pass12345")

        toggle_response = self.client.post(reverse("academics:task_toggle_complete", args=[task.pk]))
        self.assertEqual(toggle_response.status_code, 200)
        task.refresh_from_db()
        self.assertTrue(task.is_completed)

        edit_response = self.client.post(
            reverse("academics:task_edit", args=[task.pk]),
            {
                "course": course.pk,
                "title": "Draft final report",
                "description": "Revised",
                "task_type": "manual",
                "due_at": (timezone.now() + timezone.timedelta(days=3)).strftime("%Y-%m-%dT%H:%M"),
                "weight_percent": "12",
                "difficulty": "hard",
                "estimated_hours": "4",
            },
        )
        self.assertEqual(edit_response.status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.title, "Draft final report")

        delete_response = self.client.post(reverse("academics:task_delete", args=[task.pk]))
        self.assertEqual(delete_response.status_code, 302)
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())
