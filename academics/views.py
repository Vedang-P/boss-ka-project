from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ManualTaskForm
from .models import Task


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


@login_required
def task_toggle_complete(request, pk):
    """Toggle the is_completed flag on a task. Accepts POST. Returns JSON."""
    import json

    from django.http import JsonResponse

    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == "POST":
        task.is_completed = not task.is_completed
        task.save()
        return JsonResponse(
            {"ok": True, "is_completed": task.is_completed, "pk": task.pk}
        )
    return JsonResponse({"ok": False, "error": "POST required"}, status=405)


@login_required
def task_edit(request, pk):
    """Edit a manually created task."""
    task = get_object_or_404(Task, pk=pk, user=request.user, source="manual")
    form = ManualTaskForm(request.POST or None, instance=task)
    form.fields["course"].queryset = request.user.courses.order_by("title")
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Task updated.")
        return redirect("dashboard:home")
    return render(
        request,
        "academics/manual_task_form.html",
        {"form": form, "editing": True, "task": task},
    )


@login_required
def task_delete(request, pk):
    """Delete a manually created task. Accepts POST only."""
    task = get_object_or_404(Task, pk=pk, user=request.user, source="manual")
    if request.method == "POST":
        task.delete()
        messages.success(request, "Task deleted.")
        return redirect("dashboard:home")
    return render(request, "academics/task_confirm_delete.html", {"task": task})
