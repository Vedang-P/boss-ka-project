from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from academics.models import Course, Task

from .services import build_workload_summary, calculate_urgency_score, overall_grade_projection


class AnalyticsServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="student", password="pass12345")
        self.course = Course.objects.create(user=self.user, code="CS101", title="Computer Science")

    def test_urgency_score_prioritizes_near_term_heavier_work(self):
        soon_task = Task(
            user=self.user,
            course=self.course,
            title="Soon Task",
            due_at=timezone.now() + timezone.timedelta(days=1),
            weight_percent=Decimal("15"),
            difficulty="hard",
            estimated_hours=Decimal("4"),
        )
        later_task = Task(
            user=self.user,
            course=self.course,
            title="Later Task",
            due_at=timezone.now() + timezone.timedelta(days=10),
            weight_percent=Decimal("5"),
            difficulty="easy",
            estimated_hours=Decimal("1"),
        )

        self.assertGreater(calculate_urgency_score(soon_task), calculate_urgency_score(later_task))

    def test_workload_summary_flags_high_load_day(self):
        Task.objects.create(
            user=self.user,
            course=self.course,
            title="Heavy Project",
            due_at=timezone.now() + timezone.timedelta(days=2),
            weight_percent=Decimal("22"),
            difficulty="hard",
            estimated_hours=Decimal("7"),
        )

        summary = build_workload_summary(self.user, horizon_days=7)
        self.assertTrue(summary["high_days"])

    def test_overall_grade_projection_uses_what_if_scores(self):
        task = Task.objects.create(
            user=self.user,
            course=self.course,
            title="Future Exam",
            due_at=timezone.now() + timezone.timedelta(days=4),
            weight_percent=Decimal("30"),
            difficulty="medium",
            estimated_hours=Decimal("3"),
        )

        projection = overall_grade_projection(self.user, what_if_scores={task.pk: Decimal("80")})
        self.assertEqual(projection["overall_predicted_percent"], Decimal("80.00"))

    def test_grade_prediction_view_handles_posted_what_if_scores(self):
        task = Task.objects.create(
            user=self.user,
            course=self.course,
            title="Scenario Quiz",
            due_at=timezone.now() + timezone.timedelta(days=1),
            weight_percent=Decimal("20"),
            difficulty="medium",
            estimated_hours=Decimal("2"),
        )
        self.client.login(username="student", password="pass12345")

        response = self.client.post(
            reverse("analytics_app:grade_prediction"),
            {f"task_{task.pk}": "75"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "75.00%")

    def test_grade_prediction_view_does_not_render_broken_template_tokens(self):
        Task.objects.create(
            user=self.user,
            course=self.course,
            title="Rendering Quiz",
            due_at=timezone.now() + timezone.timedelta(days=1),
            weight_percent=Decimal("10"),
            difficulty="medium",
            estimated_hours=Decimal("1"),
        )
        self.client.login(username="student", password="pass12345")

        response = self.client.get(reverse("analytics_app:grade_prediction"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "{{ result.course.title }}", html=False)
        self.assertNotContains(response, "{{ task.weight_percent }}", html=False)
