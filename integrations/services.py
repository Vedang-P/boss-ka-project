from decimal import Decimal

from django.contrib.auth.signals import user_logged_in
from django.db import transaction
from django.dispatch import receiver
from django.utils import timezone

from academics.models import Course, GradeComponent, Task

from .exceptions import ProviderError
from .models import LMSConnection, SyncLog
from .providers import PROVIDER_REGISTRY


def get_provider(connection):
    provider_class = PROVIDER_REGISTRY[connection.provider]
    return provider_class(connection)


@transaction.atomic
def sync_connection(connection):
    sync_log = SyncLog.objects.create(connection=connection, status="started", message="Sync started.")
    provider = get_provider(connection)

    try:
        payload = provider.fetch_payload()
        course_map = {}
        for course_payload in payload.get("courses", []):
            course, _ = Course.objects.update_or_create(
                user=connection.user,
                connection=connection,
                external_id=str(course_payload["id"]),
                defaults={
                    "code": course_payload.get("code", "COURSE"),
                    "title": course_payload.get("title", "Untitled Course"),
                    "instructor": course_payload.get("instructor", ""),
                    "current_grade_percent": Decimal(str(course_payload.get("current_grade_percent", 0))),
                },
            )
            course_map[str(course_payload["id"])] = course

        component_map = {}
        for course_id, components in payload.get("grade_components", {}).items():
            course = course_map.get(str(course_id))
            if not course:
                continue
            for component_payload in components:
                component, _ = GradeComponent.objects.update_or_create(
                    course=course,
                    external_id=str(component_payload["id"]),
                    defaults={
                        "name": component_payload.get("name", "Assessment"),
                        "weight_percent": Decimal(str(component_payload.get("weight_percent", 0))),
                    },
                )
                component_map[(str(course_id), str(component_payload["id"]))] = component

        imported_count = 0
        for task_payload in payload.get("tasks", []):
            course = course_map.get(str(task_payload["course_id"]))
            task, _ = Task.objects.update_or_create(
                user=connection.user,
                connection=connection,
                external_id=str(task_payload["id"]),
                source="imported",
                defaults={
                    "course": course,
                    "grade_component": component_map.get(
                        (str(task_payload["course_id"]), str(task_payload.get("component_id", "")))
                    ),
                    "title": task_payload.get("title", "Imported Task"),
                    "description": task_payload.get("description", ""),
                    "task_type": task_payload.get("type", "assignment"),
                    "due_at": timezone.datetime.fromisoformat(task_payload["due_at"]),
                    "weight_percent": Decimal(str(task_payload.get("weight_percent", 0))),
                    "difficulty": task_payload.get("difficulty", "medium"),
                    "estimated_hours": Decimal(str(task_payload.get("estimated_hours", 0))),
                    "max_points": Decimal(str(task_payload.get("max_points", 100))),
                    "earned_score_percent": (
                        Decimal(str(task_payload["earned_score_percent"]))
                        if task_payload.get("earned_score_percent") is not None
                        else None
                    ),
                    "is_completed": task_payload.get("is_completed", False),
                    "metadata": task_payload,
                },
            )
            task.save()
            imported_count += 1

        connection.last_synced_at = timezone.now()
        connection.status_message = "Sync completed successfully."
        connection.credential_hint = connection.masked_token
        connection.save(update_fields=["last_synced_at", "status_message", "credential_hint", "updated_at"])
        sync_log.status = "success"
        sync_log.message = connection.status_message
        sync_log.items_imported = imported_count
        sync_log.ended_at = timezone.now()
        sync_log.save(update_fields=["status", "message", "items_imported", "ended_at"])
        return sync_log

    except ProviderError as exc:
        sync_log.status = "failed"
        sync_log.message = str(exc)
        sync_log.ended_at = timezone.now()
        sync_log.save(update_fields=["status", "message", "ended_at"])
        connection.status_message = str(exc)
        connection.save(update_fields=["status_message", "updated_at"])
        raise


def sync_due_connections(user):
    for connection in LMSConnection.objects.filter(user=user, is_active=True):
        if connection.last_synced_at is None:
            try:
                sync_connection(connection)
            except ProviderError:
                continue


@receiver(user_logged_in)
def sync_on_login(sender, request, user, **kwargs):
    sync_due_connections(user)
