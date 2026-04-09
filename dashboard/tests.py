from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from integrations.models import LMSConnection
from integrations.services import sync_connection
from config import settings as project_settings


class DashboardViewTests(TestCase):
    def test_dashboard_renders_synced_tasks(self):
        user = User.objects.create_user(username="viewer", password="pass12345")
        connection = LMSConnection.objects.create(
            user=user,
            display_name="Blackboard Demo",
            provider="blackboard",
            mode="demo",
            auth_type="token",
        )
        sync_connection(connection)
        self.client.login(username="viewer", password="pass12345")

        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mini Project Checkpoint")

    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    @patch.dict("os.environ", {"DATABASE_URL": "postgres://user:pass@localhost:5432/studyatlas"}, clear=False)
    def test_database_config_uses_database_url_when_present(self):
        config = project_settings.get_database_config(debug=False)

        self.assertEqual(config["ENGINE"], "django.db.backends.postgresql")
