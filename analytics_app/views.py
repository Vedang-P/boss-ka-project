from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from academics.models import Task

from .forms import GradePredictionFilterForm
from .services import overall_grade_projection


@login_required
def grade_prediction_view(request):
    filter_form = GradePredictionFilterForm(request.GET or None, user=request.user)
    selected_course = None
    if filter_form.is_valid():
        selected_course = filter_form.cleaned_data.get("course")

    what_if_scores = {}
    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("task_") and value:
                try:
                    task_id = int(key.split("_", 1)[1])
                    parsed = Decimal(value)
                except (ValueError, InvalidOperation):
                    continue
                what_if_scores[task_id] = min(Decimal("100"), max(Decimal("0"), parsed))

    projection = overall_grade_projection(
        request.user,
        selected_course=selected_course,
        what_if_scores=what_if_scores,
    )
    open_tasks = Task.objects.filter(user=request.user, is_completed=False).order_by("due_at")
    if selected_course:
        open_tasks = open_tasks.filter(course=selected_course)

    context = {
        "filter_form": filter_form,
        "projection": projection,
        "open_tasks": open_tasks,
        "what_if_scores": what_if_scores,
    }
    return render(request, "analytics_app/grade_prediction.html", context)
