from decimal import Decimal

from django.contrib.auth.models import User
from django.utils import timezone

from academics.models import Course, Task
from integrations.models import LMSConnection
from integrations.services import sync_connection
from planner.models import StudyAvailability
from planner.services import generate_study_sessions


SHOWCASE_USERNAME = "sarvesh"
SHOWCASE_PASSWORD = "StudyAtlas@123"


def _at_local_time(days_ahead, hour, minute=0):
    target_date = timezone.localdate() + timezone.timedelta(days=days_ahead)
    naive = timezone.datetime.combine(target_date, timezone.datetime.min.time()).replace(
        hour=hour,
        minute=minute,
    )
    return timezone.make_aware(naive, timezone.get_current_timezone())


def seed_showcase_user():
    user, _ = User.objects.get_or_create(
        username=SHOWCASE_USERNAME,
        defaults={
            "first_name": "Sarvesh",
            "last_name": "Kumar",
            "email": "sarvesh.kumar@studyatlas.demo",
        },
    )
    user.first_name = "Sarvesh"
    user.last_name = "Kumar"
    user.email = "sarvesh.kumar@studyatlas.demo"
    user.set_password(SHOWCASE_PASSWORD)
    user.save()

    profile = user.student_profile
    profile.timezone = "Asia/Kolkata"
    profile.preferred_daily_study_hours = 4
    profile.course_load_note = "3rd Year B.Tech CSE · MIT Manipal"
    profile.save()

    connections = [
        {
            "display_name": "Canvas CSE Coursework",
            "provider": "canvas",
            "mode": "demo",
            "auth_type": "token",
        },
        {
            "display_name": "Blackboard CSE Coursework",
            "provider": "blackboard",
            "mode": "demo",
            "auth_type": "token",
        },
    ]

    synced_connections = []
    for config in connections:
        connection, _ = LMSConnection.objects.update_or_create(
            user=user,
            display_name=config["display_name"],
            defaults={
                "provider": config["provider"],
                "mode": config["mode"],
                "auth_type": config["auth_type"],
                "base_url": "",
                "client_id": "",
                "client_secret": "",
                "access_token": "",
                "is_active": True,
                "status_message": "Showcase demo connection ready.",
            },
        )
        sync_connection(connection)
        synced_connections.append(connection)

    systems_course, _ = Course.objects.update_or_create(
        user=user,
        connection=None,
        code="OS303",
        title="Operating Systems",
        defaults={
            "external_id": "",
            "instructor": "Prof. Rahul Nair",
            "current_grade_percent": Decimal("89.00"),
        },
    )
    networks_course, _ = Course.objects.update_or_create(
        user=user,
        connection=None,
        code="CN305",
        title="Computer Networks",
        defaults={
            "external_id": "",
            "instructor": "Dr. Kavya Rao",
            "current_grade_percent": Decimal("86.50"),
        },
    )

    manual_tasks = [
        {
            "title": "Kernel Module Reflection",
            "course": systems_course,
            "description": "Write a concise reflection on process scheduling, synchronization, and deadlock handling after the lab.",
            "task_type": "manual",
            "due_at": _at_local_time(2, 21, 0),
            "weight_percent": Decimal("6.00"),
            "difficulty": "medium",
            "estimated_hours": Decimal("2.50"),
            "is_completed": False,
        },
        {
            "title": "Network Security Viva Prep",
            "course": networks_course,
            "description": "Prepare topic-wise viva notes on TLS, symmetric vs public-key crypto, and common packet threats.",
            "task_type": "manual",
            "due_at": _at_local_time(4, 18, 30),
            "weight_percent": Decimal("8.00"),
            "difficulty": "hard",
            "estimated_hours": Decimal("3.50"),
            "is_completed": False,
        },
        {
            "title": "DBMS Mini Project Retrospective",
            "course": None,
            "description": "Summarize lessons learned, architecture decisions, and demo feedback for the project archive.",
            "task_type": "manual",
            "due_at": _at_local_time(6, 17, 0),
            "weight_percent": Decimal("4.00"),
            "difficulty": "easy",
            "estimated_hours": Decimal("1.50"),
            "is_completed": True,
        },
    ]

    for task_data in manual_tasks:
        Task.objects.update_or_create(
            user=user,
            source="manual",
            title=task_data["title"],
            defaults={
                "course": task_data["course"],
                "connection": None,
                "grade_component": None,
                "description": task_data["description"],
                "task_type": task_data["task_type"],
                "due_at": task_data["due_at"],
                "weight_percent": task_data["weight_percent"],
                "difficulty": task_data["difficulty"],
                "estimated_hours": task_data["estimated_hours"],
                "max_points": Decimal("100.00"),
                "earned_score_percent": None,
                "is_completed": task_data["is_completed"],
                "metadata": {"showcase_seed": True},
            },
        )

    StudyAvailability.objects.filter(user=user).delete()
    availability_slots = [
        (0, 18, 0, 20, 0),
        (1, 19, 0, 21, 0),
        (2, 18, 30, 21, 0),
        (4, 17, 30, 20, 30),
        (5, 10, 0, 13, 0),
    ]
    for weekday, start_hour, start_minute, end_hour, end_minute in availability_slots:
        StudyAvailability.objects.create(
            user=user,
            weekday=weekday,
            start_time=timezone.datetime.min.time().replace(hour=start_hour, minute=start_minute),
            end_time=timezone.datetime.min.time().replace(hour=end_hour, minute=end_minute),
        )

    generate_study_sessions(user)

    return {
        "user": user,
        "connections": synced_connections,
        "task_count": user.tasks.count(),
        "course_count": user.courses.count(),
    }
