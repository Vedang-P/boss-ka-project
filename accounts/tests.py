from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from accounts.showcase import SHOWCASE_PASSWORD, SHOWCASE_USERNAME


class AccountFlowTests(TestCase):
    def test_login_page_uses_public_layout(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "main-area--public")

    def test_signup_creates_profile_and_redirects(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "newstudent",
                "email": "student@example.com",
                "password1": "BetterPass123!",
                "password2": "BetterPass123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="newstudent")
        self.assertEqual(user.student_profile.timezone, "Asia/Kolkata")

    def test_profile_update_uses_validated_form(self):
        user = User.objects.create_user(
            username="profileuser",
            password="pass12345",
            email="profile@example.com",
        )
        self.client.login(username="profileuser", password="pass12345")

        response = self.client.post(
            reverse("accounts:profile"),
            {
                "timezone": "Europe/London",
                "preferred_daily_study_hours": 5,
                "course_load_note": "Capstone semester",
            },
        )

        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        self.assertEqual(user.student_profile.timezone, "Europe/London")
        self.assertEqual(user.student_profile.preferred_daily_study_hours, 5)

    def test_showcase_seed_command_creates_demo_user(self):
        call_command("seed_showcase_user")

        user = User.objects.get(username=SHOWCASE_USERNAME)
        self.assertTrue(user.check_password(SHOWCASE_PASSWORD))
        self.assertEqual(user.first_name, "Sarvesh")
        self.assertGreaterEqual(user.courses.count(), 2)
        self.assertGreaterEqual(user.tasks.count(), 3)
