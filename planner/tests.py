from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from academics.models import Course, Task

from .models import StudyAvailability
from .services import generate_study_sessions


class PlannerServiceTests(TestCase):
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
