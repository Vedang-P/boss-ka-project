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

    tasks = request.user.tasks.select_related("course", "connection").order_by("-priority_score", "due_at")
    upcoming_tasks = tasks.filter(is_completed=False, due_at__gte=timezone.now())[:8]
    connections = request.user.lms_connections.prefetch_related("sync_logs")
    workload = build_workload_summary(request.user)
    grade_projection = overall_grade_projection(request.user)
    sessions = StudySession.objects.filter(user=request.user, start_at__gte=timezone.now())[:8]
    task_counts = request.user.tasks.values("task_type").annotate(total=Count("id")).order_by("-total")

    context = {
        "upcoming_tasks": upcoming_tasks,
        "all_tasks": tasks[:20],
        "connections": connections,
        "workload": workload,
        "grade_projection": grade_projection,
        "sessions": sessions,
        "task_counts": task_counts,
    }
    return render(request, "dashboard/home.html", context)
