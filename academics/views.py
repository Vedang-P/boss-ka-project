from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ManualTaskForm


@login_required
def manual_task_create(request):
    form = ManualTaskForm(request.POST or None)
    form.fields["course"].queryset = request.user.courses.order_by("title")
    if request.method == "POST" and form.is_valid():
        task = form.save(commit=False)
        task.user = request.user
        task.source = "manual"
        task.task_type = task.task_type or "manual"
        task.save()
        messages.success(request, "Manual task added to your dashboard.")
        return redirect("dashboard:home")

    return render(request, "academics/manual_task_form.html", {"form": form})
