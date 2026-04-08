from decimal import Decimal

from django.utils import timezone

from academics.models import Task

from .models import StudyAvailability, StudySession


def generate_study_sessions(user, horizon_days=14):
    StudySession.objects.filter(
        user=user,
        is_generated=True,
        status="planned",
        start_at__gte=timezone.now(),
    ).delete()

    availabilities = list(StudyAvailability.objects.filter(user=user).order_by("weekday", "start_time"))
    if not availabilities:
        return []

    tasks = list(
        Task.objects.filter(user=user, is_completed=False, due_at__gte=timezone.now())
        .select_related("course")
        .order_by("-priority_score", "due_at")
    )

    created_sessions = []
    current_date = timezone.localdate()
    slot_cursor = {}
    for offset in range(horizon_days):
        target_date = current_date + timezone.timedelta(days=offset)
        weekday_slots = [slot for slot in availabilities if slot.weekday == target_date.weekday()]
        for slot in weekday_slots:
            slot_cursor.setdefault(target_date, []).append(
                {
                    "start_time": slot.start_time,
                    "end_time": slot.end_time,
                }
            )

    for task in tasks:
        remaining_hours = Decimal(task.resolved_estimated_hours)
        if remaining_hours <= 0:
            continue
        due_date = timezone.localtime(task.due_at).date()
        for day, slots in slot_cursor.items():
            if day > due_date or remaining_hours <= 0:
                continue
            for slot in slots:
                if remaining_hours <= 0:
                    break
                start_at = timezone.make_aware(timezone.datetime.combine(day, slot["start_time"]))
                end_limit = timezone.make_aware(timezone.datetime.combine(day, slot["end_time"]))
                existing_sessions = StudySession.objects.filter(user=user, start_at__date=day)
                occupied_hours = sum(
                    (
                        Decimal(str((session.end_at - session.start_at).total_seconds() / 3600))
                        for session in existing_sessions
                    ),
                    Decimal("0"),
                )
                if occupied_hours >= Decimal("4"):
                    continue

                block_hours = min(Decimal("1"), remaining_hours)
                end_at = start_at + timezone.timedelta(hours=float(block_hours))
                if end_at > end_limit:
                    continue

                session = StudySession.objects.create(
                    user=user,
                    task=task,
                    title=f"Study: {task.title}",
                    start_at=start_at,
                    end_at=end_at,
                    notes=f"Generated from {task.get_task_type_display()} due on {timezone.localtime(task.due_at).strftime('%d %b %Y %H:%M')}.",
                    is_generated=True,
                )
                created_sessions.append(session)
                remaining_hours -= block_hours
                slot["start_time"] = end_at.timetz().replace(tzinfo=None)

    return created_sessions
