from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from analytics_app.services import build_workload_summary, overall_grade_projection
from integrations.services import sync_due_connections
from planner.models import StudySession


@login_required
def dashboard_home(request):
    sync_due_connections(request.user)

    now = timezone.now()
    tasks = request.user.tasks.select_related("course", "connection").order_by("-priority_score", "due_at")
    open_tasks = tasks.filter(is_completed=False)
    upcoming_tasks = open_tasks.filter(due_at__gte=now)[:8]
    connections = request.user.lms_connections.prefetch_related("sync_logs")
    workload = build_workload_summary(request.user)
    grade_projection = overall_grade_projection(request.user)
    sessions = StudySession.objects.filter(user=request.user, start_at__gte=now)[:8]
    task_counts = request.user.tasks.values("task_type").annotate(total=Count("id")).order_by("-total")
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(is_completed=True).count()
    completion_percent = round((completed_tasks / total_tasks) * 100, 1) if total_tasks else 0
    high_priority_open = open_tasks.filter(priority_score__gte=70).count()
    overdue_open = open_tasks.filter(due_at__lt=now).count()
    due_today_open = open_tasks.filter(due_at__date=timezone.localdate()).count()

    context = {
        "upcoming_tasks": upcoming_tasks,
        "all_tasks": tasks[:30],
        "connections": connections,
        "workload": workload,
        "grade_projection": grade_projection,
        "sessions": sessions,
        "task_counts": task_counts,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_percent": completion_percent,
        "high_priority_open": high_priority_open,
        "overdue_open": overdue_open,
        "due_today_open": due_today_open,
    }
    return render(request, "dashboard/home.html", context)
