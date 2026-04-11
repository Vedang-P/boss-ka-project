from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from academics.models import Course


DIFFICULTY_WEIGHT = {
    "easy": Decimal("5"),
    "medium": Decimal("10"),
    "hard": Decimal("15"),
}


def calculate_urgency_score(task):
    if getattr(task, "is_completed", False):
        return Decimal("0")

    now = timezone.now()
    due_at = getattr(task, "due_at", now)
    if due_at <= now:
        due_component = Decimal("45")
    else:
        days_remaining = Decimal(str((due_at - now).total_seconds() / 86400))
        due_component = max(Decimal("0"), Decimal("45") - min(days_remaining, Decimal("14")) * Decimal("3"))

    weight = Decimal(task.weight_percent or 0)
    weight_component = min(weight, Decimal("30"))
    time_component = min(Decimal(task.resolved_estimated_hours) * Decimal("2"), Decimal("10"))
    difficulty_component = DIFFICULTY_WEIGHT.get(task.difficulty, Decimal("10"))

    return (due_component + weight_component + time_component + difficulty_component).quantize(Decimal("0.01"))


def build_workload_summary(user, horizon_days=14):
    now = timezone.now()
    end = now + timedelta(days=horizon_days)
    tasks = list(user.tasks.filter(is_completed=False, due_at__range=(now, end)).select_related("course"))

    by_day = []
    for offset in range(horizon_days):
        day = now.date() + timedelta(days=offset)
        day_tasks = [task for task in tasks if task.due_at.date() == day]
        total_hours = sum((task.resolved_estimated_hours for task in day_tasks), Decimal("0"))
        total_weight = sum((Decimal(task.weight_percent or 0) for task in day_tasks), Decimal("0"))
        level = "low"
        if total_hours >= Decimal("6") or total_weight >= Decimal("20"):
            level = "high"
        elif total_hours >= Decimal("3") or total_weight >= Decimal("10"):
            level = "medium"
        by_day.append(
            {
                "date": day,
                "tasks": day_tasks,
                "hours": total_hours,
                "weight": total_weight,
                "level": level,
            }
        )

    week_hours = sum((entry["hours"] for entry in by_day), Decimal("0"))
    week_weight = sum((entry["weight"] for entry in by_day), Decimal("0"))
    return {
        "days": by_day,
        "weekly_hours": week_hours,
        "weekly_weight": week_weight,
        "high_days": [entry for entry in by_day if entry["level"] == "high"],
    }


def _task_score_percent(task, what_if_scores):
    if task.pk in what_if_scores:
        return Decimal(str(what_if_scores[task.pk]))
    if task.earned_score_percent is not None:
        return Decimal(task.earned_score_percent)
    return Decimal("0")


def course_grade_projection(course, what_if_scores=None):
    what_if_scores = what_if_scores or {}
    tasks = course.tasks.select_related("grade_component").all()
    weighted_total = Decimal("0")
    available_weight = Decimal("0")
    for task in tasks:
        weight = Decimal(task.weight_percent or 0)
        if weight <= 0 and task.grade_component_id:
            weight = Decimal(task.grade_component.effective_weight_percent or 0)
        if weight <= 0:
            continue
        available_weight += weight
        weighted_total += weight * (_task_score_percent(task, what_if_scores) / Decimal("100"))

    predicted_percent = Decimal("0")
    if available_weight > 0:
        predicted_percent = (weighted_total / available_weight) * Decimal("100")

    return {
        "course": course,
        "available_weight": available_weight.quantize(Decimal("0.01")),
        "predicted_percent": predicted_percent.quantize(Decimal("0.01")),
        "open_tasks": course.tasks.filter(is_completed=False).order_by("due_at"),
    }


def overall_grade_projection(user, selected_course=None, what_if_scores=None):
    courses = Course.objects.filter(user=user)
    if selected_course:
        courses = courses.filter(pk=selected_course.pk)

    results = [course_grade_projection(course, what_if_scores=what_if_scores) for course in courses]
    overall = Decimal("0")
    if results:
        overall = sum((result["predicted_percent"] for result in results), Decimal("0")) / Decimal(len(results))
    return {
        "courses": results,
        "overall_predicted_percent": overall.quantize(Decimal("0.01")) if results else Decimal("0.00"),
    }
