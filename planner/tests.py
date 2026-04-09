from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from academics.models import Course, Task

from .forms import StudyAvailabilityForm
from .models import StudyAvailability, StudySession
from .services import generate_study_sessions


class PlannerServiceTests(TestCase):
    def test_availability_form_defaults_weekday_to_monday(self):
        form = StudyAvailabilityForm()

        self.assertEqual(form.fields["weekday"].initial, 0)
        self.assertEqual(list(form.fields["weekday"].choices)[0], (0, "Monday"))

    def test_generate_study_sessions_uses_availability_slots(self):
        user = User.objects.create_user(username="planner", password="pass12345")
        course = Course.objects.create(user=user, code="CS102", title="Data Structures")
        tomorrow = timezone.localdate() + timezone.timedelta(days=1)
        StudyAvailability.objects.create(
            user=user,
            weekday=tomorrow.weekday(),
            start_time=timezone.datetime.strptime("18:00", "%H:%M").time(),
            end_time=timezone.datetime.strptime("20:00", "%H:%M").time(),
        )
        task = Task.objects.create(
            user=user,
            course=course,
            title="Linked List Practice",
            due_at=timezone.make_aware(timezone.datetime.combine(tomorrow + timezone.timedelta(days=1), timezone.datetime.strptime("21:00", "%H:%M").time())),
            weight_percent=Decimal("10"),
            difficulty="medium",
            estimated_hours=Decimal("2"),
        )

        sessions = generate_study_sessions(user, horizon_days=5)

        self.assertGreaterEqual(len(sessions), 1)
        self.assertTrue(all(session.task == task for session in sessions))
        self.assertTrue(all(session.start_at < task.due_at for session in sessions))

    def test_availability_form_rejects_end_before_start(self):
        form = StudyAvailabilityForm(
            data={
                "weekday": 1,
                "start_time": "18:00",
                "end_time": "16:00",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("end_time", form.errors)

    def test_generate_plan_route_requires_post_and_slot_delete_works(self):
        user = User.objects.create_user(username="plannerui", password="pass12345")
        slot = StudyAvailability.objects.create(
            user=user,
            weekday=1,
            start_time=timezone.datetime.strptime("18:00", "%H:%M").time(),
            end_time=timezone.datetime.strptime("20:00", "%H:%M").time(),
        )
        self.client.login(username="plannerui", password="pass12345")

        response = self.client.get(reverse("planner:generate"))
        self.assertEqual(response.status_code, 405)

        response = self.client.post(reverse("planner:slot_delete", args=[slot.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(StudyAvailability.objects.filter(pk=slot.pk).exists())
