from django.contrib.auth.models import User
from django.test import TestCase

from academics.models import Course, Task

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
