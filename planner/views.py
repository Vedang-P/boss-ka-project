from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import StudyAvailabilityForm
from .models import StudyAvailability
from .services import generate_study_sessions


@login_required
def availability_view(request):
    form = StudyAvailabilityForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        availability = form.save(commit=False)
        availability.user = request.user
        availability.save()
        messages.success(request, "Availability slot saved.")
        return redirect("planner:availability")

    slots = StudyAvailability.objects.filter(user=request.user)
    return render(request, "planner/availability.html", {"form": form, "slots": slots})


@login_required
@require_POST
def generate_plan_view(request):
    created = generate_study_sessions(request.user)
    if created:
        messages.success(request, f"Generated {len(created)} study sessions.")
    else:
        messages.warning(
            request,
            "No study sessions were generated. Add availability or upcoming tasks first.",
        )
    return redirect("dashboard:home")


@login_required
@require_POST
def slot_delete(request, pk):
    """Delete an availability slot."""
    slot = get_object_or_404(StudyAvailability, pk=pk, user=request.user)
    slot.delete()
    messages.success(request, "Availability slot removed.")
    return redirect("planner:availability")


@login_required
@require_POST
def session_update_status(request, pk):
    """Update a study session status."""
    from .models import StudySession

    session = get_object_or_404(StudySession, pk=pk, user=request.user)
    new_status = request.POST.get("status", "")
    if new_status in ("completed", "skipped", "planned"):
        session.status = new_status
        session.save(update_fields=["status"])
        return JsonResponse({"ok": True, "status": session.status})
    return JsonResponse({"ok": False, "error": "Invalid status"}, status=400)
