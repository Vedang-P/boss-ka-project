from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from academics.models import Course, Task

from .exceptions import ProviderError
from .forms import LMSConnectionForm
from .models import LMSConnection
from .services import sync_connection


class IntegrationSyncTests(TestCase):
    def test_demo_canvas_sync_imports_fixture_data(self):
        user = User.objects.create_user(username="student", password="pass12345")
        connection = LMSConnection.objects.create(
            user=user,
            display_name="Canvas Demo",
            provider="canvas",
            mode="demo",
            auth_type="token",
        )

        sync_log = sync_connection(connection)

        self.assertEqual(sync_log.status, "success")
        self.assertEqual(Course.objects.filter(user=user, connection=connection).count(), 2)
        self.assertEqual(Task.objects.filter(user=user, connection=connection).count(), 4)
        connection.refresh_from_db()
        self.assertIsNotNone(connection.last_synced_at)

    def test_live_connection_form_requires_live_credentials(self):
        form = LMSConnectionForm(
            data={
                "display_name": "Live Canvas",
                "provider": "canvas",
                "mode": "live",
                "auth_type": "token",
                "base_url": "",
                "access_token": "",
                "client_id": "",
                "client_secret": "",
                "is_active": True,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("base_url", form.errors)
        self.assertIn("access_token", form.errors)

    def test_sync_failure_on_invalid_due_datetime_marks_sync_log(self):
        user = User.objects.create_user(username="student2", password="pass12345")
        connection = LMSConnection.objects.create(
            user=user,
            display_name="Broken Demo",
            provider="canvas",
            mode="demo",
            auth_type="token",
        )
        payload = {
            "courses": [
                {
                    "id": "course-1",
                    "code": "CS100",
                    "title": "Course 1",
                    "instructor": "",
                    "current_grade_percent": 0,
                }
            ],
            "grade_components": {},
            "tasks": [
                {
                    "id": "task-1",
                    "course_id": "course-1",
                    "component_id": "",
                    "title": "Broken due date",
                    "type": "assignment",
                    "description": "",
                    "due_at": "not-a-date",
                    "weight_percent": 10,
                    "difficulty": "medium",
                    "estimated_hours": 2,
                    "max_points": 100,
                    "earned_score_percent": None,
                    "is_completed": False,
                }
            ],
        }

        fake_provider = Mock()
        fake_provider.fetch_payload.return_value = payload

        with patch("integrations.services.get_provider", return_value=fake_provider):
            with self.assertRaises(ProviderError):
                sync_connection(connection)

        log = connection.sync_logs.first()
        self.assertIsNotNone(log)
        self.assertEqual(log.status, "failed")

    def test_sync_all_route_handles_no_connections(self):
        user = User.objects.create_user(username="syncuser", password="pass12345")
        self.client.login(username="syncuser", password="pass12345")
        response = self.client.get(reverse("integrations:connection_sync_all"))
        self.assertEqual(response.status_code, 302)
